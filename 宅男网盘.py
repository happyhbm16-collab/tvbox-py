# -*- coding: utf-8 -*-
"""宅男网盘 (time1080.xyz) TVBox py 爬虫 —— 单文件自包含

站点结构：
- 栏目页：/c/<栏目>.html，过滤器为栏目作用域：类型 /c/<栏目>/<类型>.html，榜单 /c/<栏目>.html?rank=<榜单>
- 详情页：/v/<片名>.html，按网盘平台（夸克/百度/阿里/迅雷/115/UC/移动/123/guangya）分 tab，
  每条资源是 /go.php?k=xxx 中转链接
- 搜索页：/s.php?wd=<关键词>，直接返回该关键词的全部网盘资源（跳过详情页）
- /go.php?k=xxx 是 302 中转，最终落点是 pan.quark.cn/s/xxx、pan.baidu.com/s/xxx 等真实网盘分享页

播放策略：网盘播放统一走 push 模式。playerContent 解析 /go.php 的 302 得到真实网盘链接，
包成 push://<真实链接> 交给 TVBox 的 push 能力。

网络层（与 huangguo_spider / bt115 同一套约定）：
- 优先 fongmi/OK影视 的 OkHttp Java 桥（com.github.catvod.net.OkHttp）——Chaquopy 下唯一稳定出站方式；
- 本地/无桥环境回退 urllib（懒建 SSL 上下文，绝不在 import 阶段做）。

TVBox 兼容要点（踩坑后总结，勿删）：
- init() / homeContent() 内零网络请求，否则爬虫加载阶段卡死 -> 整源“无任何输出”；
- homeContent 只返回 {"class", "filters"}（与 bt115 / huangguo 完全一致，不带 list）；
- 过滤器从模块级常量构建，不依赖 __init__ 里的实例状态；
- categoryContent 同时从 filter 和 extend 两个参数读选中项（不同 loader 放的位置不同）；
- 所有接口 try/except 兜底，失败返回合法空结构 + msg，绝不抛异常。

配置示例（sites 数组）：
{
  "key": "time1080", "name": "宅男网盘", "type": 3,
  "api": "./time1080.py", "searchable": 1, "quickSearch": 1, "filterable": 1
}
extend 可选 JSON：{"host":"...","cookie":"...","proxy":"http://127.0.0.1:7890","ua":"..."}
"""

import re
import sys
import json
import base64
import urllib.parse
import urllib.request
import urllib.error

try:
    from base.spider import Spider as BaseSpider
except Exception:  # 独立运行（CLI）时没有 TVBox 的 base 包
    BaseSpider = object


# ---------------------------------------------------------------- 常量

HOST = "https://v.time1080.xyz"

UA = ("Mozilla/5.0 (Linux; Android 10; TVBox) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

# 5 个大栏目（一级分类）
COLUMNS = [
    {"type_id": "电视剧", "type_name": "电视剧"},
    {"type_id": "电影", "type_name": "电影"},
    {"type_id": "综艺", "type_name": "综艺"},
    {"type_id": "动漫", "type_name": "动漫"},
    {"type_id": "短剧", "type_name": "短剧"},
]

FILTER_KEY_GENRE = "genre"   # 第一个过滤器：类型（全部/喜剧/爱情/...）
FILTER_KEY_RANK = "rank"     # 第二个过滤器：榜单（热搜榜/新片榜/好评榜）

# 站点真实过滤器名（按各栏目页实测；href 由 build_filters_static 按栏目作用域化）
GENRE_FILTERS = ["喜剧", "爱情", "悬疑", "古装", "家庭", "犯罪", "科幻", "恐怖",
                 "历史", "战争", "动作", "冒险", "传记", "剧情", "奇幻", "惊悚", "短片"]
# 榜单组：首项「全部」rk 为空 -> 生成 /c/<栏目>.html（不带 ?rank=，即取消榜单筛选）；
# 其余三项带上真实 rank 值 -> /c/<栏目>.html?rank=<榜单>（栏目作用域才真筛选）。
RANK_FILTERS = [("全部", ""), ("热搜榜", "热搜榜"), ("新片榜", "新片榜"), ("好评榜", "好评榜")]

# 真实网盘落点域名（200 页面兜底捞链接用）
PAN_RE = (r'(https?://(?:pan\.(?:quark|baidu|xunlei|115|uc)\.[a-z.]+'
          r'|www\.aliyundrive\.com|www\.123pan\.com|pan\.123pan\.com'
          r'|drive\.guangya\.com|pan\.guangya\.com)[^\s"\'<>]+)')

DEFAULT_HEADERS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
}


# ---------------------------------------------------------------- 工具

def _b64(s):
    """代理图床 key 字段是标准 base64，解出原图 URL（带容错补 padding）。"""
    s = str(s or "").strip()
    if not s:
        return ""
    try:
        s += "=" * (-len(s) % 4)
        return base64.b64decode(s).decode("utf-8", "ignore")
    except Exception:
        return ""


def real_pic(src):
    """卡片海报走 s2.zimgs.cn 代理，key 参数里是真实图片 URL 的 base64，解出原图更稳。

    页面 img src 带 &amp; HTML 实体，先 unescape 再提 key，否则正则会漏掉 key 参数。"""
    if not src:
        return ""
    try:
        import html as _html
        src = _html.unescape(str(src))
    except Exception:
        pass
    m = re.search(r"[?&]key=([^&]+)", src)
    if m:
        dec = _b64(m.group(1))
        if dec:
            return dec
    return src


def clean(s):
    return re.sub(r"\s+", " ", str(s or "")).strip()


def sanitize_ep_name(name):
    """剧集显示名里不能有 $（名字$链接分隔）和 #（集数分隔）。"""
    return re.sub(r"[\$\#]", " ", str(name or "")).strip()


def build_filters_static(tid):
    """按已验证的站点过滤结构生成该栏目过滤器（零网络、零实例状态）。

    类型组：/c/<栏目>/<类型>.html；榜单组：/c/<栏目>.html?rank=<榜单>（栏目作用域才真筛选）。"""
    base = "/c/" + urllib.parse.quote(str(tid))
    genre_vals = [{"n": "全部", "v": base + ".html"}]
    for g in GENRE_FILTERS:
        genre_vals.append({"n": g, "v": base + "/" + urllib.parse.quote(g) + ".html"})
    rank_vals = []
    for name, rk in RANK_FILTERS:
        if rk:
            rank_vals.append({"n": name, "v": base + ".html?rank=" + urllib.parse.quote(rk)})
        else:
            rank_vals.append({"n": name, "v": base + ".html"})
    return [
        {"key": FILTER_KEY_GENRE, "name": "类型", "value": genre_vals},
        {"key": FILTER_KEY_RANK, "name": "榜单", "value": rank_vals},
    ]


# ---------------------------------------------------------------- HTTP（OkHttp 桥优先，urllib 兜底）

def _okhttp_call(url, headers, timeout):
    """fongmi/OK影视 Chaquopy 环境的 OkHttp Java 桥。返回 (final_url, body_text) 或抛异常。"""
    from com.github.catvod.net import OkHttp  # noqa
    from java.util import HashMap
    from java.util.concurrent import TimeUnit

    hm = HashMap()
    for k, v in (headers or {}).items():
        hm.put(k, v)
    call = OkHttp.newCall(url, hm)
    try:
        call.timeout().timeout(int(timeout), TimeUnit.SECONDS)
    except Exception:
        pass
    resp = call.execute()
    try:
        body = resp.body()
        text = str(body.string()) if body is not None else ""
        try:
            final_url = str(resp.request().url().toString())
        except Exception:
            final_url = url
        return final_url, text
    finally:
        try:
            resp.close()
        except Exception:
            pass


_SSL_CTX = [None]


def _ssl_ctx():
    """懒建不校验证书的 SSL 上下文（绝不在 import 阶段执行）。"""
    if _SSL_CTX[0] is None:
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        _SSL_CTX[0] = ctx
    return _SSL_CTX[0]


def _urllib_get(url, headers, timeout):
    """urllib 兜底。返回 (final_url, body_text)。"""
    req = urllib.request.Request(url, headers=headers or {})
    r = urllib.request.urlopen(req, timeout=timeout, context=_ssl_ctx())
    return r.geturl(), r.read().decode("utf-8", "ignore")


def http_get(url, headers=None, timeout=15):
    """统一 GET：OkHttp 桥优先，失败回退 urllib；再失败返回空串（绝不抛）。"""
    hs = headers or DEFAULT_HEADERS
    try:
        return _okhttp_call(url, hs, timeout)[1]
    except Exception:
        pass
    try:
        return _urllib_get(url, hs, timeout)[1]
    except Exception as e:
        sys.stdout.write("[http] %s -> %s\n" % (url, e))
        return ""


def http_follow(url, headers=None, timeout=15):
    """解析 302 中转：返回最终落点 URL（如 pan.quark.cn/s/xxx）。

    OkHttp 会自动跟随重定向，response.request().url() 即最终 URL；
    urllib 路径用 HTTPRedirectHandler 截获第一跳。都失败再从 200 正文捞 pan 链接。"""
    hs = headers or DEFAULT_HEADERS
    final_url, body = "", ""
    try:
        final_url, body = _okhttp_call(url, hs, timeout)
    except Exception:
        try:
            final_url, body = _urllib_get(url, hs, timeout)
        except Exception:
            final_url, body = "", ""
    fu = str(final_url or "")
    if fu.startswith("http") and "/go.php" not in fu:
        return fu
    m = re.search(PAN_RE, body or "")
    if m:
        return m.group(1)
    return ""


# ---------------------------------------------------------------- Spider

class Spider(BaseSpider):
    SITE_NAME = "宅男网盘"
    SITE_ID = "time1080"

    def init(self, extend=""):
        """只做配置，绝不发网络请求（TVBox 加载爬虫会先调 init，网络卡住=整源无输出）。"""
        cfg = {}
        if isinstance(extend, dict):
            cfg = extend
        elif extend:
            try:
                cfg = json.loads(extend)
                if not isinstance(cfg, dict):
                    cfg = {}
            except Exception:
                cfg = {}
        self.host = str(cfg.get("host") or HOST).rstrip("/")
        self.headers = dict(DEFAULT_HEADERS)
        if cfg.get("cookie"):
            self.headers["Cookie"] = str(cfg["cookie"]).strip()
        if cfg.get("ua"):
            self.headers["User-Agent"] = str(cfg["ua"])
        self.headers["Referer"] = self.host + "/"
        self.proxy = str(cfg.get("proxy", "") or "").strip()

    def getName(self):
        return self.SITE_NAME

    def isVideoFormat(self, url):
        return False

    def manualVideoCheck(self):
        return False

    def destroy(self):
        pass

    # -------------------------------------------------- HTTP（带实例配置）

    def _headers(self):
        return getattr(self, "headers", None) or dict(DEFAULT_HEADERS)

    def _host(self):
        return getattr(self, "host", None) or HOST

    def fetch(self, url, timeout=15):
        try:
            return http_get(url, self._headers(), timeout)
        except Exception:
            return ""

    def _follow(self, url, timeout=15):
        try:
            return http_follow(url, self._headers(), timeout)
        except Exception:
            return ""

    # -------------------------------------------------- HTML 解析

    @staticmethod
    def parse_cards(text, base):
        """栏目/主页 <a class="card"> 卡片 -> [{vod_id,vod_name,vod_pic,vod_remarks}]。"""
        out = []
        for href, inner in re.findall(r'<a class="card"[^>]*href="(/v/[^"]+)"[^>]*>(.*?)</a>', text, re.S):
            name = ""
            m = re.search(r'class="card-tt">([^<]+)<', inner)
            if not m:
                m = re.search(r'title="([^"]+)"', inner)
            if m:
                name = clean(m.group(1))
            pic = ""
            m = re.search(r'<img[^>]*src="([^"]+)"', inner)
            if m:
                pic = real_pic(m.group(1))
            remarks = ""
            m = re.search(r"<em>([^<]+)</em>", inner)
            if m:
                remarks = clean(m.group(1))
            if not name:
                continue
            out.append({
                "vod_id": base + href,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": remarks,
            })
        return out

    @staticmethod
    def parse_panes(text, base):
        """资源区按平台 tab 拆分，返回 {平台名: [(资源名, go链接, 提取码), ...]}。"""
        tabs = dict(re.findall(r'data-pane="([^"]+)"\s+data-plat-name="([^"]+)"', text))
        parts = re.split(r'<div class="res-pane[^"]*"\s+id="(pane-[^"]+)"', text)
        panes = {}
        i = 1
        while i + 1 < len(parts):
            pid, content = parts[i], parts[i + 1]
            i += 2
            plat = tabs.get(pid, pid)
            for tag in re.findall(r'<a class="weui-cell weui-cell_access res-it"[^>]*>', content):
                href = re.search(r'href="([^"]+)"', tag)
                if not href:
                    continue
                nm = re.search(r'data-name="([^"]*)"', tag)
                pw = re.search(r'data-pwd="([^"]*)"', tag)
                u = href.group(1)
                if u.startswith("/"):
                    u = base + u
                panes.setdefault(plat, []).append(
                    (clean(nm.group(1)) if nm else "", u, pw.group(1) if pw else "")
                )
        return panes

    @staticmethod
    def parse_detail_pic(text):
        """详情页海报：<div class="dt-pic"> 内第一张 <img> 的 src（代理 key 解出原图）。"""
        m = re.search(r'<div class="dt-pic">.*?<img[^>]*src="([^"]+)"', text, re.S)
        if m:
            return real_pic(m.group(1))
        m = re.search(r'<img[^>]*src="([^"]*key=[^"]+)"', text)
        if m:
            return real_pic(m.group(1))
        return ""

    # -------------------------------------------------- TVBox 标准接口

    def homeContent(self, filter):
        """【必须零网络】栏目 + 静态过滤器，结构与 bt115/huangguo 完全一致（不带 list）。"""
        classes = [dict(c) for c in COLUMNS]
        filters = {}
        for c in COLUMNS:
            filters[c["type_id"]] = build_filters_static(c["type_id"])
        return {"class": classes, "filters": filters}

    def homeVideoContent(self):
        return self.categoryContent(COLUMNS[0]["type_id"], 1, {}, {})

    def categoryContent(self, tid, pg, filter, extend):
        try:
            pg = int(pg or 1)
        except Exception:
            pg = 1
        try:
            root = "/c/" + urllib.parse.quote(str(tid or "")) + ".html"
            # 不同 loader 把选中项放 filter 或 extend，两个都读（bt115/huangguo 同款写法）
            f = {}
            for src in (filter, extend):
                if isinstance(src, dict) and src:
                    f = src
                    break
            genre_v = str(f.get(FILTER_KEY_GENRE, "") or "")
            rank_v = str(f.get(FILTER_KEY_RANK, "") or "")
            path = root
            if genre_v and genre_v != root and not genre_v.endswith(root):
                path = genre_v
            if rank_v and "?rank=" in rank_v:
                q = rank_v.split("?", 1)[1]
                path = path + ("?" + q if "?" not in path else "&" + q)
            text = self.fetch(self._host() + path)
            items = self.parse_cards(text, self._host())
        except Exception as e:
            sys.stdout.write("[category] %s\n" % e)
            items = []
        return {
            "list": items,
            "page": pg,
            "pagecount": 1,
            "limit": 90,
            "total": len(items),
        }

    def searchContent(self, key, quick):
        """搜索：返回干净的结果卡片（vod_id 指向 /s.php 搜索页，detailContent 再解析）。"""
        kw = clean(key)
        if not kw:
            return {"list": []}
        try:
            url = self._host() + "/s.php?wd=" + urllib.parse.quote(kw)
            text = self.fetch(url)
            if not text:
                return {"list": [], "msg": "搜索请求失败"}
            title_m = re.search(r'data-title="([^"]+)"', text)
            title = clean(title_m.group(1)) if title_m else kw
            if not re.search(r'class="weui-cell weui-cell_access res-it"', text):
                return {"list": []}
            return {"list": [{
                "vod_id": url,
                "vod_name": title,
                "vod_pic": "",
            }]}
        except Exception as e:
            return {"list": [], "msg": "搜索失败：" + type(e).__name__}

    def detailContent(self, ids):
        try:
            vid = ids[0]
        except Exception:
            return {"list": [], "msg": "空的详情参数"}
        try:
            url = vid if str(vid).startswith("http") else self._host() + vid
            text = self.fetch(url)
            if not text:
                return {"list": [], "msg": "详情加载失败"}
            # 搜索页详情没有海报，用影片名对应 /v/<名>.html 补一张
            pic = ""
            if "/s.php" in url:
                tm = re.search(r'data-title="([^"]+)"', text)
                if tm:
                    dv = self.fetch(self._host() + "/v/" + urllib.parse.quote(clean(tm.group(1))) + ".html")
                    if dv:
                        pic = self.parse_detail_pic(dv)
            return self.build_detail(text, url, pic_override=pic)
        except Exception as e:
            return {"list": [], "msg": "详情失败：" + type(e).__name__}

    def build_detail(self, text, vid, pic_override=None):
        """把一个资源页（详情页或搜索页）拼成 TVBox 需要的 vod dict。"""
        title_m = re.search(r'data-title="([^"]+)"', text)
        title = clean(title_m.group(1)) if title_m else str(vid)
        pic = pic_override or self.parse_detail_pic(text)
        panes = self.parse_panes(text, self._host())

        if not panes:
            return {"list": [{
                "vod_id": vid,
                "vod_name": title,
                "vod_pic": pic,
                "vod_play_from": "提示",
                "vod_play_url": "暂无网盘资源$__NONE__",
            }]}

        play_from, play_url = [], []
        total = 0
        for plat, items in panes.items():
            play_from.append(plat)
            eps = []
            for nm, u, pw in items:
                disp = sanitize_ep_name(nm) or "资源"
                if pw:
                    disp += " 提取码:" + pw
                eps.append(disp + "$" + u)
                total += 1
            play_url.append("#".join(eps))

        vod = {
            "vod_id": vid,
            "vod_name": title,
            "vod_pic": pic,
            "vod_content": "%s · 共 %d 个网盘源" % (title, total),
            "vod_play_from": "$$$".join(play_from),
            "vod_play_url": "$$$".join(play_url),
        }
        return {"list": [vod]}

    def playerContent(self, flag, id, vipFlags):
        try:
            id = str(id or "").strip()
            if id in ("__ACK__", "__NONE__", ""):
                return self._ack()
            # /go.php 中转 -> 真实网盘链接 -> push 模式
            real = self._follow(id)
            if not real:
                sys.stdout.write("[player] 未解析到网盘链接: %s\n" % id)
                return self._ack()
            return {"parse": 0, "playUrl": "", "url": "push://" + real}
        except Exception as e:
            return {"parse": 0, "playUrl": "", "url": "", "msg": "播放失败：" + type(e).__name__}

    def _ack(self):
        return {
            "parse": 0,
            "playUrl": "",
            "url": "https://vd2.bdstatic.com/mda-nj5kxa8kr7wgq6ie/sc/"
                   "cae_h264_nowatermark/1653272065989267185/mda-nj5kxa8kr7wgq6ie.mp4",
            "header": {"User-Agent": self._headers().get("User-Agent", UA)},
        }


# ---------------------------------------------------------------- CLI 自检

def run_cli(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)

    def arg(name, default=""):
        return argv[argv.index("--" + name) + 1] if ("--" + name) in argv else default

    conf = {}
    conf_path = arg("conf", "")
    if conf_path:
        try:
            conf = json.load(open(conf_path, encoding="utf-8"))
        except Exception as e:
            print("读取配置失败: %s" % e)
    spider = Spider()
    spider.init(json.dumps(conf, ensure_ascii=False))

    print("=" * 64)
    print(" %s  |  域名: %s" % (spider.getName(), spider._host()))
    print("=" * 64)

    print("\n[1] 大栏目 + 过滤器（homeContent，应即时返回）：")
    hc = spider.homeContent(True)
    for c in hc["class"]:
        fg = hc["filters"].get(c["type_id"], [])
        desc = "  |  ".join(
            "%s[%s]" % (g["name"], "/".join(v["n"] for v in g["value"])) for g in fg)
        print("   %s : %s" % (c["type_name"], desc or "(无)"))

    print("\n[2] 拉取「电视剧」分类列表...")
    cat = spider.categoryContent("电视剧", 1, {}, {})
    items = cat.get("list", [])
    if not items:
        print("   没有结果（域名可能变了 / 被墙，可加 proxy 配置）。")
        return
    for i, it in enumerate(items[:8], 1):
        print("   %2d) %s  %s" % (i, it["vod_name"][:40], it.get("vod_remarks", "")))

    fv = [v["v"] for g in hc["filters"]["电视剧"] if g["key"] == FILTER_KEY_GENRE
          for v in g["value"] if v["n"] == "喜剧"][0]
    fc = spider.categoryContent("电视剧", 1, {FILTER_KEY_GENRE: fv}, {})
    fitems = fc.get("list", [])
    print("\n[2.1] 应用过滤器 电视剧/喜剧 -> 前3: %s" % (
        " / ".join(x["vod_name"] for x in fitems[:3]) if fitems else "(空)"))

    vid = items[0]["vod_id"]
    print("\n[3] 详情：%s" % items[0]["vod_name"])
    det = spider.detailContent([vid])["list"][0]
    plats = det.get("vod_play_from", "").split("$$$")
    urls = det.get("vod_play_url", "").split("$$$")
    for p, u in zip(plats, urls):
        print("   %s : %d 条" % (p, len(u.split("#")) if u else 0))

    print("\n[4] 验证 push 链接（取第一条资源）...")
    first_url = urls[0].split("#")[0].split("$")[-1] if urls and urls[0] else ""
    if first_url:
        pc = spider.playerContent(plats[0] if plats else "", first_url, "")
        print("   %s" % pc.get("url", ""))


if __name__ == "__main__":
    run_cli()
