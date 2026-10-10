# -*- coding: utf-8 -*-
"""
ss.py - TVBox配置生成器
强制生成到固定路径 /storage/emulated/0/cai/ss.json
"""

import os
import json
import sys
import base64
import re

try:
    from base.spider import Spider as BaseSpider
except Exception:
    class BaseSpider(object):
        pass
# ==================== 用户可修改配置 ====================
# 主目录：扫描目录、生成配置和设置文件通常统一放在此目录下。
OUTPUT_PATH = "/storage/emulated/0/cai/cc.json"
DEFAULT_OUTPUT_PATH = OUTPUT_PATH
SETTINGS_PATH = "/storage/emulated/0/cai/cc_settings.json"

# 存储根目录：用于将扫描到的绝对路径转换为宿主可读取的 file:// 地址。
STORAGE_ROOT = '/storage/emulated/0'
# PHP 服务默认端口：自动检测失败时使用该端口。
DEFAULT_PHP_PORT = 8901
# 最大扫描深度：0 表示仅扫描当前目录，5 表示最多进入五层子目录。
MAX_SCAN_DEPTH = 5
# 默认扫描文件类型：可在“扫描目录”弹窗中独立开关。
SCAN_FILE_TYPES = {'py': 'PY', 'js': 'JS', 'wv.js': 'WV.JS', 'php': 'PHP', 'html': 'HTML', 'json': 'JSON', 'txt': 'TXT', 'm3u': 'M3U', 'zip': 'ZIP', 'pkg': 'PKG'}
DEFAULT_SCAN_EXTENSIONS = list(SCAN_FILE_TYPES)
# 18+ 默认开关和标签：关闭时不扫描路径链中命中任一标签的文件夹。
DEFAULT_ADULT_ENABLED = False
DEFAULT_ADULT_TAGS = ['[密]', '[18]']
# 直播目录名：该目录及其子目录的支持文件会生成 lives，而不是 sites。
LIVE_DIR_NAME = '直播文件'

# 置顶站点：始终排在自动扫描站点之前。
PINNED_SITES = [
    {'key': '本地加载', 'name': '⭐本地加载[设置]', 'type': 3, 'api': './cc.py', 'searchable': 1, 'quickSearch': 1, 'filterable': 1},
    {'key': '⚙️Nostrʷᵖ|配置', 'name': '⚙️Nostrʷᵖ|配置', 'type': 3, 'api': 'csp_Config', 'jar': './jar/vox.jar', 'searchable': 0, 'changeable': 0}
]

# 扫描根目录：按列表顺序扫描，支持绝对路径和相对主目录路径。
SCAN_DIRS = ['/storage/emulated/0/cai/']
# 屏蔽文件夹：命中名称的目录及其全部子目录不会扫描。
NO_SCAN_DIRS = {'webview', '直播转点播辅助文件', '全能王', '道长', 'lib', 'labeditor', 'pycache', '.git', '.idea'}
# 不显示的源文件：命中名称的文件不会生成 site。
EXCLUDE_FILES = {'index.php', 'test_runner.php', 'config.php', 'start.py', 'start.php', 'T4Proxy.php', 'FileExplorer.php', 'ss.json'}
# 特殊目录关键词：目录名命中后，其所有子目录都继承对应解析类型。
XBPQ_DIR_KEYWORDS = ['PQ类']
XYQ_DIR_KEYWORDS = ['YQ类']
DRPY2_DIR_KEYWORDS = ['JS[Drpy]']
LOCAL_PACKAGE_DIR_KEYWORDS = ['本地包', 'package', 'pkg', '包']

# 首页卡片图标：替换链接即可修改对应功能图标。
LOCAL_UI_ICONS = {
    # 本地加载：扫描本地目录并生成 TVBox 配置。
    'scan': 'https://cdn.jsdelivr.net/gh/tabler/tabler-icons/icons/outline/refresh.svg',
    # 扫描目录：查看或修改本地源文件扫描路径。
    'folder': 'https://cdn.jsdelivr.net/gh/tabler/tabler-icons/icons/outline/folder.svg',
    # 状态提示：显示操作结果、说明和错误信息。
    'status': 'https://cdn.jsdelivr.net/gh/tabler/tabler-icons/icons/outline/info-circle.svg',
    # 生成文件：查看或修改 JSON 输出文件及其保存位置。
    'download': 'https://cdn.jsdelivr.net/gh/tabler/tabler-icons/icons/outline/file-download.svg',
    # 屏蔽设置：管理屏蔽文件夹、不显示源文件和18+标签。
    'block': 'https://cdn.jsdelivr.net/gh/tabler/tabler-icons/icons/outline/eye-off.svg',
    # 解析设置：管理解析名称、解析URL及启用状态。
    'parse': 'https://cdn.jsdelivr.net/gh/tabler/tabler-icons/icons/outline/link.svg',
    # 自检设置：管理自检测开关、最小字节数、JAR检测、远程检测等。
    'selfcheck': 'https://cdn.jsdelivr.net/gh/tabler/tabler-icons/icons/outline/shield-check.svg'
}

# 手动站点：始终排在自动扫描站点之后。
MANUAL_SITES = [{'key': '熊猫视频', 'name': '🔞熊猫视频[采集]', 'type': 3, 'api': 'csp_XMVideo', 'jar': './jar/custom_spider.jar', 'searchable': 1, 'filterable': 1}]
# 内置直播：始终排在扫描到的直播源之前。
DEFAULT_LIVES = [{'name': '十八摸', 'type': 0, 'url': 'https://down.nigx.cn/mpimg.cn/down.php/25da10b0cb7b90d422ae22852bd7d414.txt', 'playerType': 1, 'ua': 'okhttp/3.12.13', 'epg': 'https://epg.imxd.top/?ch={name}&date={date}', 'logo': 'https://live.imxd.top/logo/{name}.png'}]
# 配置外观和 Spider JAR。
CONFIG_SPIDER = ''
CONFIG_LOGO = 'https://gss0.baidu.com/-vo3dSag_xI4khGko9WTAnF6hhy/zhidao/pic/item/a2cc7cd98d1001e99498eddaba0e7bec55e797bb.jpg'
CONFIG_WALLPAPER = 'https://p0.itc.cn/q_70/images03/20200828/8a58426e820e4c3ea4da42a3948f6f06.gif'

# ==================== 自检测配置 ====================
# 自检测总开关：开启后，生成配置时会自动检测扫描到的每个站点源是否有效，
# 无效的站源（源文件缺失/为空/内容损坏/过小疑似模板/依赖缺失/远程不可达）
# 会被自动屏蔽，不写入 sites。
# 手动置顶(PINNED_SITES)与手动站点(MANUAL_SITES)不受自检影响，始终保留。
SELF_CHECK_ENABLED = True
# 自检测要求源文件的最小字节数：小于该值的文件视为空壳/占位/模板，判定无效。
SELF_CHECK_MIN_SIZE = 8
# 自检测要求源文件的最小有效代码行数（去除注释和空行后）。
# JS/PY/PHP 源文件有效行数不足该值时，视为无实际内容的空壳站源，判定无效。
SELF_CHECK_MIN_EFFECTIVE_LINES = 1
# 是否校验 JAR 依赖文件存在性：开启后会检查站点引用的 jar 文件是否存在于本地。
SELF_CHECK_JAR_ENABLED = True
# 是否校验 drpy 引擎文件存在性：开启后会检查 drpy 站点引用的 drpy2.min.js 是否存在。
SELF_CHECK_DRPY_ENABLED = True
# 是否校验远程 API 可达性：开启后会对 http/https API 发起轻量请求检测。
# 注意：网络不佳时可能拖慢生成速度，部分服务器不支持 HEAD 请求可能误判。
SELF_CHECK_REMOTE_ENABLED = False
# 远程检测超时秒数：超过该时间未响应视为不可达。
SELF_CHECK_REMOTE_TIMEOUT = 5
# 远程检测允许的重试次数（每次超时后重试）。
SELF_CHECK_REMOTE_RETRIES = 1
# 屏蔽结果统计：记录本次生成中被自检屏蔽的无效站源，便于排查。
BLOCKED_SITE_RECORDS = {}


# ==================== 工具函数 ====================

def decode_base64_file(filepath):
    """
    尝试将文件内容作为 Base64 编码的 JSON 进行解码。
    如果解码成功且结果为合法 JSON，则覆盖原文件。
    否则静默跳过（非 Base64 或非 JSON）。
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        # 检查是否已是JSON，如果是则跳过
        try:
            json.loads(content)
            return
        except:
            pass
        
        # 尝试 Base64 解码（自动处理填充）
        decoded_bytes = base64.b64decode(content, validate=True)
        decoded_str = decoded_bytes.decode('utf-8')
        # 验证是否为合法 JSON
        json.loads(decoded_str)
        # 解码成功且为 JSON，覆盖写入原文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(decoded_str)
        print(f"✅ Base64 解码成功: {filepath}", file=sys.stderr)
    except Exception:
        # 不是 Base64 或解码后不是有效 JSON，不做任何操作
        pass

def fix_types(obj):
    """递归修正所有 type 为整数"""
    if isinstance(obj, dict):
        for k, v in list(obj.items()):
            if k == 'type' and isinstance(v, str) and v.isdigit():
                obj[k] = int(v)
            else:
                fix_types(v)
    elif isinstance(obj, list):
        for item in obj:
            fix_types(item)

# ==================== 构建站点 ====================

# ==================== 扫描状态 ====================

ROOT_DIR = os.path.dirname(OUTPUT_PATH)
SELF_FILE = os.path.basename(__file__)
_SCAN_CACHE = None
# 站点 key -> 源文件绝对路径 的映射：由扫描阶段记录，供自检测使用。
# 这样即使是 api 为 http 地址的 PHP 站点也能定位到源文件进行有效性检查。
_SITE_SOURCE_PATHS = {}
# 直播源 name -> 源文件绝对路径 的映射：由扫描阶段记录，供自检测使用。
_LIVE_SOURCE_PATHS = {}
# 被屏蔽的无效直播源记录：name -> {name, reason, source_path}
BLOCKED_LIVE_RECORDS = {}


# ==================== 扫描工具函数 ====================

def detect_php_port():
    for cmd in ('ps aux', 'pgrep -lf php', 'ps aux | grep php | grep -v grep'):
        try:
            output = os.popen(cmd + ' 2>/dev/null').read()
            for line in output.splitlines():
                if 'php' not in line.lower() or 'grep' in line.lower():
                    continue
                match = re.search(r':(\d{4,5})', line)
                if match:
                    port = int(match.group(1))
                    if 1024 <= port <= 65535:
                        return port
        except Exception:
            pass
    return DEFAULT_PHP_PORT

def get_file_extension_info(filename):
    lower = filename.lower()
    if lower.endswith('.wv.js'):
        return {'full': 'wv.js', 'simple': 'js', 'name': filename[:-6]}
    name, ext = os.path.splitext(filename)
    ext = ext[1:].lower()
    return {'full': ext, 'simple': ext, 'name': name}

def remove_all_tags(text):
    return re.sub(r'\[[^\]]*\]', '', text or '')

def extract_all_tags(text):
    return re.findall(r'\[[^\]]+\]', text or '')

def output_base_dir():
    try:
        return os.path.realpath(os.path.abspath(os.path.dirname(current_output_path())))
    except Exception:
        return os.path.realpath(os.path.abspath(ROOT_DIR))

def file_url(path):
    # 参考本地影仓 v7.0 的 _file_url：不复制源文件，转换为宿主可解析的 file:// 引用。
    absolute = os.path.realpath(os.path.abspath(os.path.expanduser(str(path))))
    storage_root = os.path.realpath(os.path.abspath(STORAGE_ROOT))
    try:
        relative = os.path.relpath(absolute, storage_root).replace(os.sep, '/')
    except Exception:
        relative = ''
    if relative and relative != '..' and not relative.startswith('../'):
        return 'file://' + relative.lstrip('/')
    return 'file://' + absolute

def rel_path(path):
    abs_path = os.path.realpath(os.path.abspath(path))
    base_dir = output_base_dir()
    try:
        # 输出文件同目录/子目录内的源，继续用 ./ 相对路径。
        # 输出目录外的源，不能用 ../ 或裸 /storage/...，否则部分壳能扫到但加载不可用；改用 file://。
        if os.path.commonpath([abs_path, base_dir]) == base_dir:
            rel = './' + os.path.relpath(abs_path, base_dir).replace(os.sep, '/')
            return './' if rel == './.' else rel
    except Exception:
        pass
    return file_url(abs_path)

def abs_scan_path(path):
    path = os.path.expanduser(str(path or '').strip())
    return os.path.abspath(path if os.path.isabs(path) else os.path.join(ROOT_DIR, path))

def split_scan_dirs(value):
    raw = str(value or '').strip()
    for sep in ('｜', '，', '；', ';', '、', ','):
        raw = raw.replace(sep, '|')
    raw = raw.replace('\r', '\n').replace('\n', '|')
    result = []
    for item in raw.split('|'):
        item = item.strip().strip('\"').strip("'")
        if item and item not in result:
            result.append(item)
    return result

def is_supported_file(ext_info):
    return ext_info['full'] in current_scan_extensions()

def is_runtime_generated_file(path):
    try:
        ap = os.path.abspath(path)
        protected = {
            os.path.abspath(DEFAULT_OUTPUT_PATH),
            os.path.abspath(current_output_path()) if 'current_output_path' in globals() else os.path.abspath(DEFAULT_OUTPUT_PATH),
            os.path.abspath(SETTINGS_PATH)
        }
        return ap in protected
    except Exception:
        return False


def _read_utf8(path, limit=4096):
    """读取源文件前 limit 字节用于自检；失败返回 None。"""
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read(limit)
    except Exception:
        return None


def _strip_comments_and_blank(text):
    """去除 Python/JS/PHP/CSS 注释和空白行后的有效内容。"""
    if not text:
        return ''
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        # 跳过空行
        if not stripped:
            continue
        # 跳过 Python/JS 注释行
        if stripped.startswith('#') or stripped.startswith('//'):
            continue
        # 去掉行内注释后保留代码部分
        for marker in ('#', '//'):
            idx = stripped.find(marker)
            if idx > 0:
                stripped = stripped[:idx].strip()
        if stripped:
            lines.append(stripped)
    return '\n'.join(lines)


def _looks_like_template(content):
    """启发式判断是否为占位模板内容（过短/纯注释/纯空白/TODO 占位）。"""
    if content is None:
        return True
    stripped = content.strip()
    if not stripped:
        return True
    if len(stripped) < SELF_CHECK_MIN_SIZE:
        return True
    # 纯注释/空白内容
    effective = _strip_comments_and_blank(content)
    if not effective:
        return True
    # 常见占位标记
    placeholders = ('todo', 'placeholder', 'fixme', '待补充', '待完善', '暂无', 'xxx', 'lorem ipsum')
    lower = stripped.lower()
    if lower in placeholders:
        return True
    # 整个文件仅由占位标记组成
    if all(word in placeholders for word in lower.split()):
        return True
    # 去掉注释后内容极少（<16字符），视为无意义占位
    effective = _strip_comments_and_blank(content)
    if len(effective.strip()) < 16:
        return True
    return False


def _is_content_valid(path, ext_info):
    """针对不同源类型做基础有效性检测，返回 (bool, 原因)。"""
    ext = ext_info['full']
    abs_path = os.path.realpath(os.path.abspath(path))

    # 路径存在性
    if not os.path.exists(abs_path):
        return False, '文件不存在'
    if not os.path.isfile(abs_path):
        return False, '不是普通文件'
    try:
        size = os.path.getsize(abs_path)
    except Exception:
        size = 0

    # 基础大小校验：过小视为空壳/占位
    if size < SELF_CHECK_MIN_SIZE:
        return False, f'文件过小({size}B)疑似模板'

    # 读取采样内容
    content = _read_utf8(abs_path)
    if _looks_like_template(content):
        return False, '内容为空或过短'

    # 按类型做专项校验
    lower_ext = ext.lower()
    if lower_ext == 'json':
        try:
            with open(abs_path, 'r', encoding='utf-8', errors='replace') as f:
                raw = f.read()
            data = json.loads(raw)
            if isinstance(data, dict):
                if not data:
                    return False, 'JSON 对象为空'
                # 检查是否包含至少一个 TVBox 站源关键字段
                # 避免 {}、{"foo":"bar"} 等无意义对象通过检测
                tvbox_keys = ('url', 'api', 'key', 'name', 'sites', 'ext', 'jar', 'homePage',
                              'type', 'searchable', 'quickSearch', 'filterable', 'changeable',
                              'group', 'header', 'playerType', 'ua')
                if not any(k in data for k in tvbox_keys):
                    return False, 'JSON 缺少站源关键字段'
                # 检查 sites 列表是否为空
                sites_val = data.get('sites')
                if isinstance(sites_val, list) and not sites_val:
                    return False, 'JSON sites 列表为空'
                # 检查关键字段是否存在但值为空/None
                def _is_empty_val(v):
                    return v is None or (isinstance(v, str) and not v.strip())
                if 'url' in data and _is_empty_val(data.get('url')):
                    return False, 'JSON url 字段为空'
                if 'api' in data and _is_empty_val(data.get('api')):
                    return False, 'JSON api 字段为空'
                if 'name' in data and _is_empty_val(data.get('name')):
                    return False, 'JSON name 字段为空'
                if 'key' in data and _is_empty_val(data.get('key')):
                    return False, 'JSON key 字段为空'
                if 'ext' in data and _is_empty_val(data.get('ext')):
                    return False, 'JSON ext 字段为空'
                if 'jar' in data and _is_empty_val(data.get('jar')):
                    return False, 'JSON jar 字段为空'
            elif isinstance(data, list):
                if not data:
                    return False, 'JSON 列表为空'
            elif isinstance(data, str):
                if not data.strip():
                    return False, 'JSON 字符串为空'
        except Exception as e:
            return False, f'JSON 解析失败: {e}'

    elif lower_ext in ('py', 'js', 'wv.js'):
        # 有效代码行数检测：去除注释和空行后不足阈值 → 空壳
        effective = _strip_comments_and_blank(content)
        effective_lines = [l for l in effective.splitlines() if l.strip()]
        if len(effective_lines) < SELF_CHECK_MIN_EFFECTIVE_LINES:
            return False, f'有效代码仅{len(effective_lines)}行，疑似空壳'
        # JS/PY 源应有可运行的定义，检测是否有 class/function/export/var 等
        # 放宽检测：只要包含基本 JS/PY 语法标记即可（函数、变量、赋值、对象等）
        # 严格检测：JS 站源必须包含 TVBox/Drpy 特有的结构标记
        # 旧版 Drpy 用 var rule = {...}，新版用 class + homeContent/categoryContent 等方法
        js_tvbox_kws = ('var rule', 'rule =', 'rule:', 'class ', 'homeContent',
                        'categoryContent', 'detailContent', 'searchContent', 'playContent',
                        'searchable', 'filterable', 'quickSearch', 'changeable',
                        'function', '=>', 'var ', 'const ', 'let ', 'export', 'module.exports')
        if not any(kw in content for kw in js_tvbox_kws):
            return False, 'JS 缺少 TVBox 站源结构（rule/class/homeContent 等）'
        # 有效代码行数检测
        effective = _strip_comments_and_blank(content)
        effective_lines = [l for l in effective.splitlines() if l.strip()]
        if len(effective_lines) < SELF_CHECK_MIN_EFFECTIVE_LINES:
            return False, f'有效代码仅{len(effective_lines)}行，疑似空壳'

    elif lower_ext == 'html':
        # HTML 源需包含基本标签结构
        if not any(tag in content.lower() for tag in ('<html', '<body', '<div', '<script', '<meta', '<link', '<head', '<!doctype', '<iframe', '<video', '<source', '<ul', '<table', '<form', '<span', '<p', '<a ')):
            return False, 'HTML 缺少标签结构'

    elif lower_ext == 'm3u':
        # M3U 直播源需包含 #EXTM3U 头或至少一条 #EXTINF
        if '#EXTM3U' not in content and '#EXTINF' not in content:
            return False, 'M3U 缺少 #EXTM3U/#EXTINF'

    elif lower_ext in ('zip', 'pkg'):
        # 本地包为二进制文件，仅校验存在性和大小
        return True, ''
    elif lower_ext == 'txt':
        # TXT 直播源需至少包含一行非空内容
        if not any(line.strip() for line in content.splitlines()):
            return False, 'TXT 内容为空'

    return True, 'ok'


def _check_remote_url(url):
    """对远程 URL 发起轻量请求检测可达性，返回 (bool, 原因)。"""
    if not SELF_CHECK_REMOTE_ENABLED:
        return True, ''
    try:
        import urllib.request
        import urllib.error
        req = urllib.request.Request(url, method='HEAD', headers={'User-Agent': 'okhttp/3.12.13'})
        for attempt in range(SELF_CHECK_REMOTE_RETRIES + 1):
            try:
                resp = urllib.request.urlopen(req, timeout=SELF_CHECK_REMOTE_TIMEOUT)
                resp.close()
                return True, ''
            except urllib.error.HTTPError as e:
                # 405 Method Not Allowed：服务器不支持 HEAD，尝试 GET
                if e.code == 405 and attempt == 0:
                    req = urllib.request.Request(url, headers={'User-Agent': 'okhttp/3.12.13'})
                    continue
                # 4xx/5xx 也可能是正常的（需要参数），不判定为不可达
                if e.code in (400, 401, 403, 404, 429):
                    return False, f'HTTP {e.code}'
                return True, ''
            except Exception:
                if attempt < SELF_CHECK_REMOTE_RETRIES:
                    continue
                return False, '远程不可达'
        return True, ''
    except Exception as e:
        return False, f'远程检测异常: {e}'


def _resolve_local_ref(ref):
    """将站点字段中的本地引用（./xxx 或 file://xxx）解析为绝对路径。"""
    p = str(ref)
    if p.startswith('./'):
        p = os.path.join(ROOT_DIR, p[2:])
    elif p.startswith('file://'):
        p = p[len('file://'):]
        # file://storage/emulated/0/... → /storage/emulated/0/...
        if p.startswith('storage/'):
            p = '/' + p
        elif not p.startswith('/'):
            p = '/' + p
    else:
        return None  # 非本地引用
    return os.path.realpath(os.path.abspath(os.path.expanduser(p)))


def is_site_valid(site):
    """检查构建出的站点是否指向一个真实有效的源文件。

    返回 (bool, 原因)。site 中可能携带 ext / api / homePage / jar 等字段。
    检测维度：
      1) 扫描阶段记录的源文件绝对路径（覆盖 PHP 的 http api 等场景）
      2) ext / api / homePage 字段中的本地文件引用（./xxx 或 file://xxx）
      3) jar 依赖文件存在性
      4) drpy 引擎文件存在性
      5) 远程 API 可达性（可选，默认关闭）
    """
    checked_paths = set()

    # 1) 优先使用扫描阶段记录的源文件绝对路径
    site_key = site.get('key')
    if site_key and site_key in _SITE_SOURCE_PATHS:
        src = _SITE_SOURCE_PATHS[site_key]
        ext_info = get_file_extension_info(os.path.basename(src))
        ok, reason = _is_content_valid(src, ext_info)
        if not ok:
            return False, reason
        checked_paths.add(os.path.realpath(src))

    # 2) 从 ext / api / homePage 字段中解析本地文件引用（不跳过 file://）
    remote_urls = []
    candidates = []
    for field in ('ext', 'api', 'homePage'):
        val = site.get(field)
        if not val:
            continue
        val = str(val)
        if val.startswith('csp_'):
            continue
        if val.startswith('http://') or val.startswith('https://'):
            remote_urls.append(val)
            continue
        # ./xxx 和 file://xxx 都是本地引用，需要检查
        candidates.append(val)

    for ref in candidates:
        resolved = _resolve_local_ref(ref)
        if resolved is None:
            continue
        if not os.path.exists(resolved):
            # 引用文件不存在时跳过该项检测，不判为无效
            continue
        if resolved in checked_paths:
            continue  # 已在第 1 步校验过
        ext_info = get_file_extension_info(os.path.basename(resolved))
        ok, reason = _is_content_valid(resolved, ext_info)
        if not ok:
            return False, reason
        checked_paths.add(resolved)

    # 3) JAR 依赖文件存在性检测
    if SELF_CHECK_JAR_ENABLED:
        jar = site.get('jar')
        if jar:
            jar_resolved = _resolve_local_ref(jar)
            if jar_resolved is not None and not os.path.exists(jar_resolved):
                return False, f'JAR 不存在: {jar}'

    # 4) drpy 引擎文件存在性检测
    if SELF_CHECK_DRPY_ENABLED:
        api_val = str(site.get('api', ''))
        if 'drpy2' in api_val:
            drpy_resolved = _resolve_local_ref(api_val)
            if drpy_resolved is not None and not os.path.exists(drpy_resolved):
                return False, f'drpy 引擎不存在: {api_val}'

    # 5) 远程 API 可达性检测（可选）
    if SELF_CHECK_REMOTE_ENABLED and remote_urls:
        for url in remote_urls:
            ok, reason = _check_remote_url(url)
            if not ok:
                return False, f'远程不可达: {url} ({reason})'

    return True, ''


def self_check_and_filter(sites):
    """对扫描得到的站点列表进行自检，屏蔽无效站源。

    返回 (保留站点, 被屏蔽列表)。为了幂等，会重置屏蔽统计，并在最终汇总时去重。
    重要：必须在 deduplicate_sites 之前调用，否则 key 可能被修改导致
    _SITE_SOURCE_PATHS 查找失败。
    """
    global BLOCKED_SITE_RECORDS
    # 优先从设置文件读取自检测开关，实现运行时可切换
    sc_settings = current_self_check_settings()
    if not sc_settings.get('enabled', SELF_CHECK_ENABLED):
        BLOCKED_SITE_RECORDS = {}
        return sites, []
    kept = []
    blocked = []
    for site in sites:
        ok, reason = is_site_valid(site)
        if ok:
            kept.append(site)
        else:
            name = site.get('name', site.get('key', ''))
            blocked.append({'name': name, 'key': site.get('key', ''), 'reason': reason,
                            'source_path': _SITE_SOURCE_PATHS.get(site.get('key', ''), '')})
    # 按 key 去重统计
    BLOCKED_SITE_RECORDS = {}
    for b in blocked:
        BLOCKED_SITE_RECORDS[b['key']] = b
    return kept, blocked


def is_live_valid(live):
    """检查直播源是否指向一个真实有效的源文件或 URL。

    返回 (bool, 原因)。live 中 url 字段可能为本地路径（./xxx、file://xxx）或远程 URL。
    """
    live_name = live.get('name', '')
    url = str(live.get('url', ''))

    # 1) 优先使用扫描阶段记录的源文件绝对路径
    if live_name and live_name in _LIVE_SOURCE_PATHS:
        src = _LIVE_SOURCE_PATHS[live_name]
        ext_info = get_file_extension_info(os.path.basename(src))
        ok, reason = _is_content_valid(src, ext_info)
        if not ok:
            return False, reason
        return True, ''

    # 2) 从 url 字段解析本地文件引用
    if url.startswith('http://') or url.startswith('https://'):
        # 远程直播源：仅在开启远程检测时检查
        if SELF_CHECK_REMOTE_ENABLED:
            ok, reason = _check_remote_url(url)
            if not ok:
                return False, f'远程不可达: {url} ({reason})'
        return True, ''

    if url.startswith('csp_'):
        return True, ''  # CSP 爬虫源，不做本地检测

    # 本地引用（./xxx 或 file://xxx）
    resolved = _resolve_local_ref(url)
    if resolved is None:
        return True, ''  # 无法识别的格式，默认不屏蔽

    if not os.path.exists(resolved):
        return False, f'直播源文件不存在: {url}'

    ext_info = get_file_extension_info(os.path.basename(resolved))
    ok, reason = _is_content_valid(resolved, ext_info)
    if not ok:
        return False, reason

    return True, ''


def self_check_and_filter_lives(lives):
    """对扫描得到的直播源列表进行自检，屏蔽无效直播源。

    返回 (保留直播源, 被屏蔽列表)。
    DEFAULT_LIVES（内置直播）不受自检影响，始终保留。
    """
    global BLOCKED_LIVE_RECORDS
    sc_settings = current_self_check_settings()
    if not sc_settings.get('enabled', SELF_CHECK_ENABLED):
        BLOCKED_LIVE_RECORDS = {}
        return lives, []
    kept = []
    blocked = []
    for live in lives:
        ok, reason = is_live_valid(live)
        if ok:
            kept.append(live)
        else:
            name = live.get('name', '')
            blocked.append({'name': name, 'reason': reason,
                            'source_path': _LIVE_SOURCE_PATHS.get(name, '')})
    BLOCKED_LIVE_RECORDS = {}
    for b in blocked:
        BLOCKED_LIVE_RECORDS[b['name']] = b
    return kept, blocked


def get_nearest_tag(tags):
    return tags[-1] if tags else ''
def scan_sort_key(name):
    try:
        return str(name or '').casefold().encode('gbk', 'replace')
    except Exception:
        return str(name or '').casefold()
def keyword_hit(dirname, keywords):
    return any(keyword in dirname for keyword in keywords)

def check_special_directory(dirname, parent_xbpq=False, parent_xyq=False, parent_drpy=False, parent_pkg=False):
    is_xbpq = parent_xbpq or keyword_hit(dirname, XBPQ_DIR_KEYWORDS)
    is_xyq = parent_xyq or keyword_hit(dirname, XYQ_DIR_KEYWORDS)
    is_drpy = parent_drpy or keyword_hit(dirname, DRPY2_DIR_KEYWORDS)
    is_pkg = parent_pkg or keyword_hit(dirname, LOCAL_PACKAGE_DIR_KEYWORDS)
    return is_xbpq, is_xyq, is_drpy, is_pkg

def drpy_api_path():
    fast = os.path.join(ROOT_DIR, 'lib/lib/drpy2-fast.min.js')
    normal = os.path.join(ROOT_DIR, 'lib/drpy2.min.js')
    if os.path.exists(fast):
        return './lib/lib/drpy2-fast.min.js'
    if os.path.exists(normal):
        return './lib/drpy2.min.js'
    return './lib/drpy2.min.js'

def make_full_name(name, tag, label):
    clean_name = remove_all_tags(name).strip() or name
    return f'{clean_name}{tag}({label.upper()})'

def deduplicate_sites(sites):
    seen = {}
    result = []
    for site in sites:
        key = site.get('key')
        if not key:
            result.append(site)
            continue
        if key in seen:
            seen[key] += 1
            new_key = f'{key}_{seen[key]}'
            while new_key in seen:
                seen[key] += 1
                new_key = f'{key}_{seen[key]}'
            site = dict(site)
            site['key'] = new_key
            site['name'] = f"{site.get('name', key)} ({seen[key]})"
            seen[new_key] = 0
        else:
            seen[key] = 0
        result.append(site)
    return result


# ==================== 站点构建规则 ====================

def build_site_config(name, top_tag, ext_info, local_path, php_api_prefix, is_xbpq=False, is_xyq=False, is_drpy=False, is_pkg=False):
    ext = ext_info['full']
    simple_ext = ext_info['simple']

    if is_xbpq and ext == 'json':
        full = make_full_name(name, top_tag, 'xbpq')
        return {'key': full, 'name': full, 'type': 3, 'api': 'csp_XBPQ', 'searchable': 1, 'quickSearch': 1, 'filterable': 1, 'changeable': 1, 'ext': local_path}

    if is_xyq and ext == 'json':
        full = make_full_name(name, top_tag, 'XYQ')
        return {'key': full, 'name': full, 'type': 3, 'api': 'csp_XYQHiker', 'searchable': 1, 'quickSearch': 1, 'filterable': 1, 'changeable': 1, 'ext': local_path}

    if is_drpy and ext == 'js':
        full = make_full_name(name, top_tag, 'js')
        return {'key': full, 'name': full, 'type': 3, 'api': drpy_api_path(), 'searchable': 1, 'quickSearch': 1, 'filterable': 1, 'changeable': 1, 'order_num': 0, 'ext': local_path}


    if ext == 'php':
        full = make_full_name(name, top_tag, 'php')
        clean_path = local_path[2:] if local_path.startswith('./') else local_path
        return {'key': full, 'name': full, 'type': 4, 'api': php_api_prefix + '/' + clean_path, 'searchable': 1, 'quickSearch': 1, 'filterable': 1, 'changeable': 1}

    if ext == 'wv.js':
        full = make_full_name(name, top_tag, 'wv.js')
        return {'key': full, 'name': full, 'type': 3, 'api': 'csp_WvSpider', 'jar': './jar/WvSpider.jar', 'searchable': 1, 'quickSearch': 1, 'filterable': 1, 'switchable': 1, 'ext': local_path}

    if ext == 'py':
        full = make_full_name(name, top_tag, 'py')
        return {'key': full, 'name': full, 'type': 3, 'api': local_path, 'searchable': 1, 'quickSearch': 1, 'filterable': 1, 'switchable': 1}

    if ext == 'js':
        full = make_full_name(name, top_tag, 'js')
        return {'key': full, 'name': full, 'type': 3, 'api': local_path, 'searchable': 1, 'quickSearch': 1, 'filterable': 1, 'switchable': 1}

    if ext == 'html':
        full = make_full_name(name, top_tag, 'html')
        return {'key': full, 'name': full, 'type': 3, 'api': 'csp_Nostr', 'searchable': 1, 'quickSearch': 1, 'filterable': 1, 'switchable': 1, 'homePage': local_path}

    if ext in ('txt', 'm3u', 'json', 'zip', 'pkg') or simple_ext in ('txt', 'm3u', 'json', 'zip', 'pkg'):
        full = make_full_name(name, top_tag, ext)
        return {'key': full, 'name': full, 'type': 3, 'api': 'csp_FileSpider', 'jar': './jar/WvSpider.jar', 'searchable': 0, 'quickSearch': 0, 'filterable': 0, 'switchable': 0, 'changeable': 0, 'ext': local_path}

    full = make_full_name(name, top_tag, ext or 'file')
    return {'key': full, 'name': full, 'type': 3, 'api': local_path, 'searchable': 1, 'quickSearch': 1, 'filterable': 1, 'switchable': 1}


# ==================== 递归扫描引擎 ====================

def scan_directory_recursive(path, scanned_sites, scanned_lives, php_api_prefix, current_depth=0, nearest_tag='', parent_xbpq=False, parent_xyq=False, parent_drpy=False, parent_live=False, parent_pkg=False):
    global BLOCKED_SITE_RECORDS, _SITE_SOURCE_PATHS
    if current_depth > MAX_SCAN_DEPTH or not os.path.isdir(path):
        return

    current_dir_name = os.path.basename(path)
    if not current_adult_enabled() and any(tag in current_dir_name for tag in current_adult_tags()):
        return
    current_tags = extract_all_tags(current_dir_name)
    current_nearest_tag = get_nearest_tag(current_tags) or nearest_tag
    top_tag = current_nearest_tag

    is_live = parent_live or (current_dir_name == LIVE_DIR_NAME)
    is_xbpq, is_xyq, is_drpy, is_pkg = check_special_directory(current_dir_name, parent_xbpq, parent_xyq, parent_drpy, parent_pkg)

    try:
        items = sorted(os.listdir(path), key=scan_sort_key)
    except Exception as e:
        print(f'⚠️ 扫描目录失败 {path}: {e}', file=sys.stderr)
        return

    for item in items:
        if item in current_blocked_dirs():
            continue

        full_path = os.path.join(path, item)

        if os.path.isdir(full_path):
            scan_directory_recursive(full_path, scanned_sites, scanned_lives, php_api_prefix, current_depth + 1, current_nearest_tag, is_xbpq, is_xyq, is_drpy, is_live, is_pkg)
            continue

        if item in current_excluded_files() or is_runtime_generated_file(full_path):
            continue

        ext_info = get_file_extension_info(item)
        ext = ext_info['full']

        if not is_supported_file(ext_info):
            continue

        if ext == 'json' and (is_xbpq or is_xyq):
            decode_base64_file(full_path)

        local_path = rel_path(full_path)
        name = remove_all_tags(ext_info['name']).strip() or ext_info['name']

        if is_live:
            live_name = name + top_tag
            scanned_lives.append({'name': live_name, 'type': 0, 'url': local_path, 'playerType': 2, 'epg': 'http://epg.51zmt.top:8000/api/diyp/?ch={name}&date={date}', 'logo': f'https://11.112114.xyz/logo/{name}.png', 'ua': ''})
            # 记录直播源 -> 源文件绝对路径，供自检测定位本地文件
            _LIVE_SOURCE_PATHS[live_name] = full_path
            continue

        site = build_site_config(name, top_tag, ext_info, local_path, php_api_prefix, is_xbpq, is_xyq, is_drpy, is_pkg)
        scanned_sites.append(site)
        # 记录站点 -> 源文件绝对路径，供自检测定位本地文件（尤其 PHP 的 api 是 http 地址）
        site_key = site.get('key')
        if site_key:
            _SITE_SOURCE_PATHS[site_key] = full_path


# ==================== 设置读写与生成动作 ====================

def default_settings():
    return {
        'output_path': DEFAULT_OUTPUT_PATH,
        'scan_dirs': list(SCAN_DIRS),
        'scan_enabled_dirs': list(SCAN_DIRS),
        'scan_extensions': list(DEFAULT_SCAN_EXTENSIONS),
        'adult_enabled': DEFAULT_ADULT_ENABLED,
        'blocked_dirs': sorted(NO_SCAN_DIRS, key=scan_sort_key),
        'excluded_files': sorted(EXCLUDE_FILES, key=scan_sort_key),
        'adult_tags': list(DEFAULT_ADULT_TAGS),
        'parse_entries': default_parse_entries(),
        'self_check': default_self_check_settings()
    }

def default_self_check_settings():
    return {
        'enabled': SELF_CHECK_ENABLED,
        'min_size': SELF_CHECK_MIN_SIZE,
        'min_effective_lines': SELF_CHECK_MIN_EFFECTIVE_LINES,
        'jar_enabled': SELF_CHECK_JAR_ENABLED,
        'drpy_enabled': SELF_CHECK_DRPY_ENABLED,
        'remote_enabled': SELF_CHECK_REMOTE_ENABLED,
        'remote_timeout': SELF_CHECK_REMOTE_TIMEOUT
    }

def current_self_check_settings():
    saved = load_settings().get('self_check')
    if not isinstance(saved, dict):
        return default_self_check_settings()
    defaults = default_self_check_settings()
    result = dict(defaults)
    result['enabled'] = bool(saved.get('enabled', defaults['enabled']))
    try:
        result['min_size'] = int(saved.get('min_size', defaults['min_size']))
    except Exception:
        result['min_size'] = defaults['min_size']
    try:
        result['min_effective_lines'] = int(saved.get('min_effective_lines', defaults['min_effective_lines']))
    except Exception:
        result['min_effective_lines'] = defaults['min_effective_lines']
    result['jar_enabled'] = bool(saved.get('jar_enabled', defaults['jar_enabled']))
    result['drpy_enabled'] = bool(saved.get('drpy_enabled', defaults['drpy_enabled']))
    result['remote_enabled'] = bool(saved.get('remote_enabled', defaults['remote_enabled']))
    try:
        result['remote_timeout'] = int(saved.get('remote_timeout', defaults['remote_timeout']))
    except Exception:
        result['remote_timeout'] = defaults['remote_timeout']
    return result

def save_self_check_settings(sc_data):
    data = load_settings()
    data['self_check'] = sc_data
    save_settings(data)
    reset_scan_cache()
    return sc_data

def _apply_self_check_settings():
    """将设置文件中的自检测参数同步到全局变量，供模块级函数使用。"""
    global SELF_CHECK_ENABLED, SELF_CHECK_MIN_SIZE, SELF_CHECK_MIN_EFFECTIVE_LINES
    global SELF_CHECK_JAR_ENABLED, SELF_CHECK_DRPY_ENABLED, SELF_CHECK_REMOTE_ENABLED, SELF_CHECK_REMOTE_TIMEOUT
    sc = current_self_check_settings()
    SELF_CHECK_ENABLED = sc.get('enabled', SELF_CHECK_ENABLED)
    SELF_CHECK_MIN_SIZE = sc.get('min_size', SELF_CHECK_MIN_SIZE)
    SELF_CHECK_MIN_EFFECTIVE_LINES = sc.get('min_effective_lines', SELF_CHECK_MIN_EFFECTIVE_LINES)
    SELF_CHECK_JAR_ENABLED = sc.get('jar_enabled', SELF_CHECK_JAR_ENABLED)
    SELF_CHECK_DRPY_ENABLED = sc.get('drpy_enabled', SELF_CHECK_DRPY_ENABLED)
    SELF_CHECK_REMOTE_ENABLED = sc.get('remote_enabled', SELF_CHECK_REMOTE_ENABLED)
    SELF_CHECK_REMOTE_TIMEOUT = sc.get('remote_timeout', SELF_CHECK_REMOTE_TIMEOUT)

def load_settings():
    data = default_settings()
    try:
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
                saved = json.load(f)
            if isinstance(saved, dict):
                output_path = str(saved.get('output_path') or '').strip()
                if output_path:
                    data['output_path'] = output_path
                if isinstance(saved.get('scan_dirs'), list):
                    dirs = [str(x).strip() for x in saved['scan_dirs'] if str(x).strip()]
                    data['scan_dirs'] = dirs
                    if 'scan_enabled_dirs' not in saved:
                        data['scan_enabled_dirs'] = list(dirs)
                if isinstance(saved.get('scan_enabled_dirs'), list):
                    data['scan_enabled_dirs'] = [str(x).strip() for x in saved['scan_enabled_dirs'] if str(x).strip()]
                if isinstance(saved.get('scan_extensions'), list):
                    data['scan_extensions'] = [x for x in saved['scan_extensions'] if x in SCAN_FILE_TYPES]
                if 'adult_enabled' in saved:
                    data['adult_enabled'] = bool(saved['adult_enabled'])
                for key in ('blocked_dirs', 'excluded_files', 'adult_tags'):
                    if isinstance(saved.get(key), list):
                        data[key] = [str(x).strip() for x in saved[key] if str(x).strip()]
                if isinstance(saved.get('parse_entries'), list):
                    data['parse_entries'] = [dict(x) for x in saved['parse_entries'] if isinstance(x, dict)]
                if isinstance(saved.get('self_check'), dict):
                    data['self_check'] = dict(default_self_check_settings(), **saved['self_check'])
    except Exception as e:
        print(f'⚠️ 读取设置失败: {e}', file=sys.stderr)
    return data

def save_settings(data):
    os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
    with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return data

def current_output_path():
    return load_settings().get('output_path') or DEFAULT_OUTPUT_PATH

def current_scan_dirs():
    saved = load_settings().get('scan_dirs')
    return saved if isinstance(saved, list) else list(SCAN_DIRS)

def current_enabled_scan_dirs():
    data = load_settings()
    dirs = data.get('scan_dirs', [])
    enabled = set(data.get('scan_enabled_dirs', dirs))
    return [path for path in dirs if path in enabled]

def set_scan_dir_enabled(path, enabled):
    data = load_settings()
    active = set(data.get('scan_enabled_dirs', data.get('scan_dirs', [])))
    active.add(path) if enabled else active.discard(path)
    data['scan_enabled_dirs'] = [x for x in data.get('scan_dirs', []) if x in active]
    save_settings(data)
    reset_scan_cache()
    return enabled

def current_scan_extensions():
    saved = load_settings().get('scan_extensions')
    return [x for x in saved if x in SCAN_FILE_TYPES] if isinstance(saved, list) else list(DEFAULT_SCAN_EXTENSIONS)

def current_adult_enabled():
    value = load_settings().get('adult_enabled')
    return DEFAULT_ADULT_ENABLED if value is None else bool(value)

def current_blocked_dirs():
    return set(load_settings().get('blocked_dirs', NO_SCAN_DIRS))

def current_excluded_files():
    return set(load_settings().get('excluded_files', EXCLUDE_FILES))

def current_adult_tags():
    return load_settings().get('adult_tags', DEFAULT_ADULT_TAGS)

def split_csv(value):
    raw = str(value or '').replace('，', ',').replace('、', ',').replace('\n', ',')
    return list(dict.fromkeys(x.strip() for x in raw.split(',') if x.strip()))

def save_block_settings(blocked_dirs, excluded_files, adult_tags):
    data = load_settings()
    data['blocked_dirs'] = split_csv(blocked_dirs)
    data['excluded_files'] = split_csv(excluded_files)
    data['adult_tags'] = split_csv(adult_tags)
    save_settings(data)
    reset_scan_cache()
    return data

def save_scan_options(extensions, adult_enabled):
    data = load_settings()
    data['scan_extensions'] = [x for x in extensions if x in SCAN_FILE_TYPES]
    data['adult_enabled'] = bool(adult_enabled)
    save_settings(data)
    reset_scan_cache()
    return data

def reset_scan_cache():
    global _SCAN_CACHE
    _SCAN_CACHE = None

def set_output_name(name):
    name = str(name or '').strip().replace('\\', '/').split('/')[-1]
    if not name:
        raise ValueError('文件名不能为空')
    if not name.lower().endswith('.json'):
        name += '.json'
    data = load_settings()
    output_dir = os.path.dirname(data.get('output_path') or DEFAULT_OUTPUT_PATH) or ROOT_DIR
    data['output_path'] = os.path.join(output_dir, name)
    save_settings(data)
    return data['output_path']

def set_output_dir(path):
    path = str(path or '').strip()
    if not path:
        raise ValueError('保存路径不能为空')
    data = load_settings()
    name = os.path.basename(data.get('output_path') or DEFAULT_OUTPUT_PATH) or 'ss.json'
    data['output_path'] = os.path.join(path, name)
    save_settings(data)
    return data['output_path']

def set_output_full_path(path):
    path = str(path or '').strip()
    if not path:
        raise ValueError('输出路径不能为空')
    if path.endswith('/'):
        path = os.path.join(path, os.path.basename(DEFAULT_OUTPUT_PATH))
    if not path.lower().endswith('.json'):
        path += '.json'
    data = load_settings()
    data['output_path'] = path
    save_settings(data)
    return data['output_path']

def set_scan_dirs(value):
    raw = str(value or '').strip()
    if not raw:
        raise ValueError('扫描路径不能为空')
    dirs = split_scan_dirs(raw)
    if not dirs:
        raise ValueError('扫描路径不能为空')
    data = load_settings()
    data['scan_dirs'] = dirs
    data['scan_enabled_dirs'] = list(dirs)
    save_settings(data)
    reset_scan_cache()
    return dirs

def add_scan_dir(path):
    path = os.path.abspath(os.path.expanduser(str(path or '').strip()))
    if not path or not os.path.isdir(path):
        raise ValueError('目录不存在')
    data = load_settings()
    dirs = data.get('scan_dirs') or []
    if path not in dirs:
        dirs.append(path)
    data['scan_dirs'] = dirs
    enabled = data.get('scan_enabled_dirs', [])
    if path not in enabled:
        enabled.append(path)
    data['scan_enabled_dirs'] = enabled
    save_settings(data)
    reset_scan_cache()
    return path

def remove_scan_dir(path):
    data = load_settings()
    data['scan_dirs'] = [x for x in data.get('scan_dirs', []) if x != path]
    data['scan_enabled_dirs'] = [x for x in data.get('scan_enabled_dirs', []) if x != path]
    save_settings(data)
    reset_scan_cache()
    return path

def generate_and_write_config():
    """扫描本地目录 → 自检过滤无效源 → 写入配置文件。

    无效站源和无效直播源在写入前已被过滤，不会出现在最终输出 JSON 中。
    返回生成统计信息，包含被屏蔽的站点和直播源数量。
    """
    reset_scan_cache()
    output_path = current_output_path()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    config_data = get_config()
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)
    sc = current_self_check_settings()
    sc_enabled = sc.get('enabled', SELF_CHECK_ENABLED)
    return {
        'output_path': output_path,
        'sites': len(config_data.get('sites', [])),
        'lives': len(config_data.get('lives', [])),
        'scan_dirs': current_scan_dirs(),
        'blocked_sites': len(BLOCKED_SITE_RECORDS) if sc_enabled else 0,
        'blocked_lives': len(BLOCKED_LIVE_RECORDS) if sc_enabled else 0
    }

# ==================== 输出构建 ====================

def scan_local_entries():
    global _SCAN_CACHE, _SITE_SOURCE_PATHS, _LIVE_SOURCE_PATHS
    if _SCAN_CACHE is not None:
        return _SCAN_CACHE
    # 仅在全新扫描时重置路径映射（缓存命中时不能清空，否则自检会丢失源文件定位）
    _SITE_SOURCE_PATHS = {}
    _LIVE_SOURCE_PATHS = {}

    sites, lives = [], []
    php_port = detect_php_port()
    php_api_prefix = f'http://0.0.0.0:{php_port}'

    for scan_dir in current_enabled_scan_dirs():
        scan_path = abs_scan_path(scan_dir)
        if not os.path.isdir(scan_path):
            continue
        if os.path.basename(os.path.normpath(scan_path)) in current_blocked_dirs():
            continue
        scan_directory_recursive(scan_path, sites, lives, php_api_prefix)

    # 注意：此处不进行 deduplicate_sites，因为自检依赖 _SITE_SOURCE_PATHS
    # 中的原始 key 进行源文件定位。deduplicate 会修改 key（如 foo→foo_1），
    # 导致自检时 key 不匹配而跳过检测。
    # 自检和 deduplicate 均在 build_sites() 中按正确顺序执行。
    _SCAN_CACHE = (sites, lives)
    return _SCAN_CACHE

def build_lives():
    """构建直播源列表：内置直播 + 扫描到的直播源，扫描到的直播源经自检过滤。"""
    global BLOCKED_LIVE_RECORDS
    # 内置直播始终保留，不做自检
    lives = [dict(live) for live in DEFAULT_LIVES]
    scanned_lives = scan_local_entries()[1]

    # 自检测：过滤扫描到的无效直播源（内置 DEFAULT_LIVES 不受影响）
    kept_lives, blocked_lives = self_check_and_filter_lives(scanned_lives)
    BLOCKED_LIVE_RECORDS = {b['name']: b for b in blocked_lives}

    lives.extend(kept_lives)
    return lives

def build_sites():
    """构建站点列表：置顶站点 + 自检后的扫描站点 + 手动站点。"""
    global BLOCKED_SITE_RECORDS, _SITE_SOURCE_PATHS
    # 同步自检测设置到全局变量
    _apply_self_check_settings()

    # 置顶站点始终保留，不做自检
    sites = [dict(site) for site in PINNED_SITES]
    scanned_sites, _ = scan_local_entries()

    # 自检测：在 deduplicate 之前执行，确保 _SITE_SOURCE_PATHS 的 key 与站点 key 一致。
    # 仅扫描到的站点参与自检；置顶(PINNED_SITES)与手动(MANUAL_SITES)始终保留。
    kept_sites, blocked = self_check_and_filter(scanned_sites)
    BLOCKED_SITE_RECORDS = {b['key']: b for b in blocked}

    sites.extend(kept_sites)

    # 手动站点始终保留，不做自检
    sites.extend(dict(site) for site in MANUAL_SITES)
    return deduplicate_sites(sites)


def blocked_site_summary():
    """返回被自检屏蔽的无效站源和直播源的统计信息。"""
    sc = current_self_check_settings()
    if not sc.get('enabled', SELF_CHECK_ENABLED):
        return '自检测已关闭'
    site_count = len(BLOCKED_SITE_RECORDS)
    live_count = len(BLOCKED_LIVE_RECORDS)
    if site_count == 0 and live_count == 0:
        return '全部站源有效，无屏蔽'
    lines = []
    if site_count > 0:
        lines.append(f'已屏蔽 {site_count} 个无效站源：')
        for b in BLOCKED_SITE_RECORDS.values():
            lines.append('- {name}：{reason}'.format(name=b.get('name', ''), reason=b.get('reason', '')))
    if live_count > 0:
        lines.append(f'已屏蔽 {live_count} 个无效直播源：')
        for b in BLOCKED_LIVE_RECORDS.values():
            lines.append('- {name}：{reason}'.format(name=b.get('name', ''), reason=b.get('reason', '')))
    return '\n'.join(lines)

def blocked_site_details():
    """返回被屏蔽站源的详细列表，供 UI 弹窗展示。"""
    if not BLOCKED_SITE_RECORDS:
        return []
    return [
        {'name': b.get('name', ''), 'key': b.get('key', ''), 'reason': b.get('reason', ''),
         'source_path': b.get('source_path', ''), 'type': 'site'}
        for b in BLOCKED_SITE_RECORDS.values()
    ]

def blocked_live_details():
    """返回被屏蔽直播源的详细列表，供 UI 弹窗展示。"""
    if not BLOCKED_LIVE_RECORDS:
        return []
    return [
        {'name': b.get('name', ''), 'reason': b.get('reason', ''),
         'source_path': b.get('source_path', ''), 'type': 'live'}
        for b in BLOCKED_LIVE_RECORDS.values()
    ]

# ==================== 额外配置（完整版） ====================

EXTRA_JSON = r'''{
    "parses": [
        {"name":"♻️龙26","type":0,"url":"https://www.mtosz.com/m3u8.php?url=","ext":{"flag":["qq","腾讯","qiyi","iqiyi","爱奇艺","奇艺","youku","优酷","mgtv","芒果","letv","乐视","pptv","PPTV","sohu","bilibili","哔哩哔哩","哔哩"]}},
        {"name":"-BBKDJ-","type":0,"url":"https://jx.yparse.com/index.php?url="},
        {"name":"-777-","type":0,"url":"https://jx.bozrc.com:4433/player/?url="},
        {"name":"-全看-","type":0,"url":"https://jx.quankan.app/?url="}
    ],
    "rules": [
        {"name":"proxy","hosts":["stream-link.org"]},
        {"name":"量子广告","hosts":["vip.lz","hd.lz",".cdnlz"],"regex":["#EXT-X-DISCONTINUITY\\r*\\n*#EXTINF:6\\.666667,[\\s\\S]*?#EXT-X-DISCONTINUITY","#EXTINF.*?\\s+.*?1o.*?\\.ts\\s+"]},
        {"name":"非凡广告","hosts":["vip.ffzy","hd.ffzy"],"regex":["20.52","#EXT-X-DISCONTINUITY\\r*\\n*#EXTINF:7\\.400000,[\\s\\S]*?#EXT-X-DISCONTINUITY","#EXTINF.*?\\s+.*?1170(20|32).*?\\.ts\\s+","#EXTINF.*?\\s+.*?116977.*?\\.ts\\s+"]},
        {"name":"索尼广告","hosts":["suonizy"],"regex":["#EXT-X-DISCONTINUITY\\r*\\n*#EXTINF:1\\.000000,[\\s\\S]*?#EXT-X-DISCONTINUITY","#EXTINF.*?\\s+.*?p1ayer.*?\\.ts\\s+","#EXTINF.*?\\s+.*?\\/video\\/original.*?\\.ts\\s+"]},
        {"name":"暴风广告","hosts":["bfzy","bfbfvip"],"regex":["#EXTINF.*?\\s+.*?adjump.*?\\.ts\\s+"]},
        {"name":"星星广告","hosts":["aws.ulivetv.net"],"regex":["#EXT-X-DISCONTINUITY\\r*\\n*#EXTINF:8,[\\s\\S]*?#EXT-X-DISCONTINUITY"]},
        {"name":"快看广告","hosts":["kuaikan"],"regex":["#EXT-X-KEY:METHOD=NONE\\r*\\n*#EXTINF:5,[\\s\\S]*?#EXT-X-DISCONTINUITY","#EXT-X-KEY:METHOD=NONE\\r*\\n*#EXTINF:2\\.4,[\\s\\S]*?#EXT-X-DISCONTINUITY"]},
        {"name":"夜市","hosts":["yeslivetv.com"],"script":["document.getElementsByClassName('vjs-big-play-button')[0].click()"]},
        {"name":"毛驢","hosts":["www.maolvys.com"],"script":["document.getElementsByClassName('swal-button swal-button--confirm')[0].click()"]},
        {"name":"磁力广告","hosts":["magnet"],"regex":["更多","请访问","example","社 區","x u u","直 播","更 新","社 区","有趣","有 趣","英皇体育","全中文AV在线","澳门皇冠赌场","哥哥快来","美女荷官","裸聊","新片首发","UUE29"]},
        {"name":"一起看广告","hosts":["yqk88"],"regex":["18.4","15.1666","16.5333","#EXT-X-DISCONTINUITY\\r*\\n*[\\s\\S]*?#EXT-X-CUE-IN"]},
        {"name":"火山嗅探","hosts":["huoshan.com"],"regex":["item_id="]},
        {"name":"抖音嗅探","hosts":["douyin.com"],"regex":["is_play_url="]},
        {"name":"proxy","hosts":["raw.githubusercontent.com","googlevideo.com","cdn.v82u1l.com","cdn.iz8qkg.com","cdn.kin6c1.com","c.biggggg.com","c.olddddd.com","haiwaikan.com","www.histar.tv","youtube.com","uhibo.com",".*boku.*",".*nivod.*","*.t4tv.hz.cz",".*ulivetv.*"]},
        {"name":"农民嗅探","hosts":["toutiaovod.com"],"regex":["video/tos/cn"]}
    ],
    "doh": [
        {"name":"Google","url":"https://dns.google/dns-query","ips":["8.8.4.4","8.8.8.8"]},
        {"name":"Cloudflare","url":"https://cloudflare-dns.com/dns-query","ips":["1.1.1.1","1.0.0.1","2606:4700:4700::1111","2606:4700:4700::1001"]},
        {"name":"AdGuard","url":"https://dns.adguard.com/dns-query","ips":["94.140.14.140","94.140.14.141"]},
        {"name":"DNSWatch","url":"https://resolver2.dns.watch/dns-query","ips":["84.200.69.80","84.200.70.40"]},
        {"name":"Quad9","url":"https://dns.quad9.net/dns-quer","ips":["9.9.9.9","149.112.112.112"]},
        {"host":"www.djuu.com","rule":["mp4.djuu.com","m4a"]},
        {"host":"www.sharenice.net","rule":["huoshan.com","/item/video/"],"filter":[]},
        {"host":"www.sharenice.net","rule":["sovv.qianpailive.com","vid="],"filter":[]},
        {"host":"www.sharenice.net","rule":["douyin.com","/play/"]},
        {"host":"m.ysxs8.vip","rule":["ysting.ysxs8.vip:81","xmcdn.com"],"filter":[]},
        {"host":"hdmoli.com","rule":[".m3u8"]},
        {"host":"https://api.live.bilibili.com","rule":["bilivideo.com","/index.m3u8"],"filter":["data.bilibili.com/log/web","i0.hdslb.com/bfs/live/"]},
        {"host":"www.agemys.cc","rule":["cdn-tos","obj/tos-cn"]},
        {"host":"www.fun4k.com","rule":["https://hd.ijycnd.com/play","index.m3u8"]},
        {"host":"zjmiao.com","rule":["play.videomiao.vip/API.php","time=","key=","path="]}
    ],
    "flags": ["youku","优酷","优 酷","优酷视频","qq","腾讯","腾 讯","腾讯视频","iqiyi","qiyi","奇艺","爱奇艺","爱 奇 艺","m1905","xigua","letv","leshi","乐视","乐 视","sohu","搜狐","搜 狐","搜狐视频","tudou","pptv","mgtv","芒果","imgo","芒果TV","芒 果 T V","bilibili","哔 哩","哔 哩 哔 哩"],
    "ijk": [
        {"group":"软解码","options":[{"category":4,"name":"opensles","value":"0"},{"category":4,"name":"overlay-format","value":"842225234"},{"category":4,"name":"framedrop","value":"1"},{"category":4,"name":"soundtouch","value":"1"},{"category":4,"name":"start-on-prepared","value":"1"},{"category":1,"name":"http-detect-range-support","value":"0"},{"category":1,"name":"fflags","value":"fastseek"},{"category":2,"name":"skip_loop_filter","value":"48"},{"category":4,"name":"reconnect","value":"1"},{"category":4,"name":"max-buffer-size","value":"5242880"},{"category":4,"name":"enable-accurate-seek","value":"0"},{"category":4,"name":"mediacodec","value":"0"},{"category":4,"name":"mediacodec-auto-rotate","value":"0"},{"category":4,"name":"mediacodec-handle-resolution-change","value":"0"},{"category":4,"name":"mediacodec-hevc","value":"0"},{"category":1,"name":"dns_cache_timeout","value":"600000000"}]},
        {"group":"硬解码","options":[{"category":4,"name":"opensles","value":"0"},{"category":4,"name":"overlay-format","value":"842225234"},{"category":4,"name":"framedrop","value":"1"},{"category":4,"name":"soundtouch","value":"1"},{"category":4,"name":"start-on-prepared","value":"1"},{"category":1,"name":"http-detect-range-support","value":"0"},{"category":1,"name":"fflags","value":"fastseek"},{"category":2,"name":"skip_loop_filter","value":"48"},{"category":4,"name":"reconnect","value":"1"},{"category":4,"name":"max-buffer-size","value":"5242880"},{"category":4,"name":"enable-accurate-seek","value":"0"},{"category":4,"name":"mediacodec","value":"1"},{"category":4,"name":"mediacodec-auto-rotate","value":"1"},{"category":4,"name":"mediacodec-handle-resolution-change","value":"1"},{"category":4,"name":"mediacodec-hevc","value":"1"},{"category":1,"name":"dns_cache_timeout","value":"600000000"}]}
    ],
    "ads": ["https://img.mjviku.com","wan.51img1.com","iqiyi.hbuioo.com","vip.ffzyad.com","https://lf1-cdn-tos.bytegoofy.com/obj/tos-cn-i-dy/455ccf9e8ae744378118e4bd289288dd","mimg.0c1q0l.cn","www.googletagmanager.com","www.google-analytics.com","mc.usihnbcq.cn","mg.g1mm3d.cn","mscs.svaeuzh.cn","cnzz.hhttm.top","tp.vinuxhome.com","cnzz.mmstat.com","www.baihuillq.com","s23.cnzz.com","z3.cnzz.com","c.cnzz.com","stj.v1vo.top","z12.cnzz.com","img.mosflower.cn","tips.gamevvip.com","ehwe.yhdtns.com","xdn.cqqc3.com","www.jixunkyy.cn","sp.chemacid.cn","hm.baidu.com","s9.cnzz.com","z6.cnzz.com","um.cavuc.com","mav.mavuz.com","wofwk.aoidf3.com","z5.cnzz.com","xc.hubeijieshikj.cn","tj.tianwenhu.com","xg.gars57.cn","k.jinxiuzhilv.com","cdn.bootcss.com","ppl.xunzhuo123.com","xomk.jiangjunmh.top","img.xunzhuo123.com","z1.cnzz.com","s13.cnzz.com","xg.huataisangao.cn","z7.cnzz.com","xg.huataisangao.cn","z2.cnzz.com","s96.cnzz.com","q11.cnzz.com","thy.dacedsfa.cn","xg.whsbpw.cn","s19.cnzz.com","z8.cnzz.com","s4.cnzz.com","f5w.as12df.top","ae01.alicdn.com","www.92424.cn","k.wudejia.com","vivovip.mmszxc.top","qiu.xixiqiu.com","cdnjs.hnfenxun.com","cms.qdwght.com"]
}'''

# ==================== 解析设置 ====================

def default_parse_entries():
    try:
        return [dict(item, enabled=True) for item in json.loads(EXTRA_JSON).get('parses', []) if isinstance(item, dict)]
    except Exception:
        return []

def current_parse_entries():
    entries = load_settings().get('parse_entries')
    return [dict(item) for item in entries] if isinstance(entries, list) else default_parse_entries()

def save_parse_entries(entries):
    data = load_settings()
    data['parse_entries'] = [dict(item) for item in entries if isinstance(item, dict)]
    save_settings(data)
    return data['parse_entries']

def enabled_parses():
    result = []
    for item in current_parse_entries():
        if item.get('enabled', True):
            clean = dict(item)
            clean.pop('enabled', None)
            result.append(clean)
    return result

# ==================== 生成配置 ====================

def get_config():
    """获取完整配置。

    执行流程：扫描 → 自检过滤（站点+直播源）→ 组装配置。
    无效站源和无效直播源在写入前已被过滤，不会出现在最终输出中。
    """
    # 同步自检测设置
    _apply_self_check_settings()

    # 构建站点列表（内部触发扫描并执行自检过滤，无效站源不写入）
    sites = build_sites()

    # 构建直播源列表（使用扫描缓存并执行自检过滤，无效直播源不写入）
    lives = build_lives()

    config = {
        "spider": CONFIG_SPIDER,
        "logo": CONFIG_LOGO,
        "wallpaper": CONFIG_WALLPAPER,
        "lives": lives,
        "sites": sites
    }

    # 加载额外配置
    try:
        extra = json.loads(EXTRA_JSON)
        fix_types(extra)
        extra['parses'] = enabled_parses()
        config.update(extra)
    except Exception as e:
        print(f"⚠️ EXTRA_JSON 解析失败: {e}", file=sys.stderr)

    return config


# ==================== 卡片交互 Spider ====================

class Spider(BaseSpider):
    LOAD_ID = '__cc_local_load__'
    OUTPUT_ID = '__cc_output_file__'
    OUTPUT_NAME_ID = '__cc_output_name__'
    OUTPUT_PATH_ID = '__cc_output_path__'
    OUTPUT_FULL_ID = '__cc_output_full__'
    SCAN_ID = '__cc_scan_dirs__'
    SCAN_SET_ID = '__cc_scan_set__'
    BLOCK_ID = '__cc_block_settings__'
    PARSE_ID = '__cc_parse_settings__'
    SELFCHECK_ID = '__cc_selfcheck_settings__'
    BLOCKED_ID = '__cc_blocked_sites__'

    def getName(self):
        return '本地配置工具'

    def init(self, extend=''):
        pass

    def destroy(self):
        pass

    def isVideoFormat(self, url):
        return False

    def manualVideoCheck(self):
        return True

    def _icon(self, key):
        return LOCAL_UI_ICONS.get(key, '')

    def _card(self, vod_id, name, pic_key='status', remarks='', **extra):
        item = {
            'vod_id': vod_id,
            'vod_name': name,
            'vod_pic': self._icon(pic_key),
            'vod_remarks': remarks
        }
        item.update(extra)
        return item

    def _settings_summary(self):
        data = load_settings()
        return data.get('output_path', DEFAULT_OUTPUT_PATH), data.get('scan_dirs', list(SCAN_DIRS))

    def _home_items(self):
        output_path, scan_dirs = self._settings_summary()
        sc = current_self_check_settings()
        sc_status = '已开启' if sc.get('enabled') else '已关闭'
        blocked_sites = len(BLOCKED_SITE_RECORDS) if sc.get('enabled') else 0
        blocked_lives = len(BLOCKED_LIVE_RECORDS) if sc.get('enabled') else 0
        blocked_total = blocked_sites + blocked_lives
        sc_remarks = sc_status + (f'，已屏蔽 {blocked_total} 个' if blocked_total else '')
        items = [
            self._card(self.LOAD_ID, '本地加载', 'scan', '点击后扫描本地目录并生成配置', action='local_load'),
            self._card(self.OUTPUT_ID, '生成文件', 'download', '当前输出：' + output_path, settings=True, output_settings=True, action='edit_output_full'),
            self._card(self.SCAN_ID, '扫描设置', 'folder', '{} 个目录：{}'.format(len(scan_dirs), ' | '.join(scan_dirs)[:90]), settings=True, scan_settings=True, action='edit_scan_dirs'),
            self._card(self.BLOCK_ID, '屏蔽设置', 'block', '目录、源文件和18+标签', settings=True, action='edit_block_settings'),
            self._card(self.SELFCHECK_ID, '自检测设置', 'selfcheck', sc_remarks, settings=True, action='edit_selfcheck_settings'),
            self._card(self.PARSE_ID, '解析设置', 'parse', '{} 个解析'.format(len(current_parse_entries())), settings=True, action='edit_parse_settings')
        ]
        if blocked_total > 0:
            detail = []
            if blocked_sites:
                detail.append(f'{blocked_sites} 个站源')
            if blocked_lives:
                detail.append(f'{blocked_lives} 个直播源')
            items.append(self._card(self.BLOCKED_ID, '屏蔽详情', 'selfcheck', '查看被屏蔽的{}'.format(' + '.join(detail)), settings=True, action='view_blocked_sites'))
        return items

    def homeContent(self, filter=False):
        return {'class': [{'type_id': 'setting', 'type_name': '设置'}], 'list': self._home_items()}

    def homeVideoContent(self):
        return {'list': self._home_items()}

    def categoryContent(self, tid, pg, filter, extend):
        return {'list': self._home_items(), 'page': 1, 'pagecount': 1, 'limit': 20, 'total': len(self._home_items())}

    def _detail(self, vod_id, title, content, pic_key='status'):
        return {'list': [{
            'vod_id': vod_id,
            'vod_name': title,
            'vod_pic': self._icon(pic_key),
            'vod_content': content,
            'vod_play_from': '提示',
            'vod_play_url': '返回$cc://noop'
        }]}

    def _output_setting_items(self):
        output_path, _ = self._settings_summary()
        output_dir = os.path.dirname(output_path) or ROOT_DIR
        output_name = os.path.basename(output_path) or 'ss.json'
        return [
            self._card(self.OUTPUT_NAME_ID, '修改名字', 'download', '当前：' + output_name, settings=True, input=True, input_type='text', input_key='文件名', input_value=output_name, input_hint='输入文件名，例如 cc.json', action='edit_output_name'),
            self._card(self.OUTPUT_PATH_ID, '修改路径', 'folder', '当前：' + output_dir, settings=True, input=True, input_type='path', input_key='路径', input_value=output_dir, input_hint='输入保存目录，例如 /storage/emulated/0/cai/', action='edit_output_path'),
            self._card(self.OUTPUT_FULL_ID, '完整输出', 'status', output_path, settings=True, input=True, input_type='file', input_key='输出', input_value=output_path, input_hint='输入完整输出文件，例如 /storage/emulated/0/cai/ss.json', action='edit_output_full')
        ]

    def _scan_setting_items(self):
        _, scan_dirs = self._settings_summary()
        value = '|'.join(scan_dirs)
        types = '、'.join(SCAN_FILE_TYPES[x] for x in current_scan_extensions()) or '未选择'
        status = '18+开启' if current_adult_enabled() else '18+关闭'
        return [
            self._card(self.SCAN_SET_ID, '扫描设置', 'folder', '{}；{}；{}'.format(types, status, value), settings=True, action='edit_scan_dirs'),
            self._card(self.LOAD_ID, '本地加载', 'scan', '按当前扫描目录生成配置', action='local_load')
        ]

    def detailContent(self, ids):
        vod_id = str(ids[0] if isinstance(ids, (list, tuple)) and ids else ids or '')
        output_path, scan_dirs = self._settings_summary()
        if vod_id == self.LOAD_ID:
            try:
                info = generate_and_write_config()
                content = '加载中...\n加载完成！\n站点数量：{}\n直播数量：{}\n生成文件：{}\n扫描目录：{}'.format(info['sites'], info['lives'], info['output_path'], ' | '.join(info['scan_dirs']))
                blocked_total = info.get('blocked_sites', 0) + info.get('blocked_lives', 0)
                if blocked_total > 0:
                    parts = []
                    if info.get('blocked_sites', 0):
                        parts.append('{} 个站源'.format(info['blocked_sites']))
                    if info.get('blocked_lives', 0):
                        parts.append('{} 个直播源'.format(info['blocked_lives']))
                    content += '\n已屏蔽 {}'.format(' + '.join(parts))
                    summary = blocked_site_summary()
                    if summary and summary != '全部站源有效，无屏蔽':
                        content += '\n' + summary
                return self._detail(vod_id, '本地加载完成', content, 'scan')
            except Exception as e:
                return self._detail(vod_id, '本地加载失败', str(e), 'status')
        if vod_id == self.OUTPUT_ID:
            return {'list': self._output_setting_items()}
        if vod_id in (self.OUTPUT_NAME_ID, self.OUTPUT_PATH_ID, self.OUTPUT_FULL_ID):
            return self._detail(vod_id, '生成文件', '如果没有弹窗，请用搜索修改：\n文件名=cc.json\n路径=/storage/emulated/0/cai/\n输出=/storage/emulated/0/cai/ss.json\n\n当前输出：{}'.format(output_path), 'download')
        if vod_id == self.SCAN_ID:
            return {'list': self._scan_setting_items()}
        if vod_id == self.BLOCK_ID:
            return self._detail(vod_id, '屏蔽设置', '请点击卡片操作按钮打开设置弹窗。', 'status')
        if vod_id == self.SELFCHECK_ID:
            sc = current_self_check_settings()
            lines = [
                '自检测：{}'.format('已开启' if sc.get('enabled') else '已关闭'),
                '最小字节数：{}'.format(sc.get('min_size', 8)),
                '最小有效代码行数：{}'.format(sc.get('min_effective_lines', 3)),
                'JAR 检测：{}'.format('已开启' if sc.get('jar_enabled') else '已关闭'),
                'drpy 引擎检测：{}'.format('已开启' if sc.get('drpy_enabled') else '已关闭'),
                '远程 API 检测：{}'.format('已开启' if sc.get('remote_enabled') else '已关闭'),
                '',
                '请点击卡片操作按钮打开设置弹窗。'
            ]
            site_blocked = len(BLOCKED_SITE_RECORDS)
            live_blocked = len(BLOCKED_LIVE_RECORDS)
            if site_blocked or live_blocked:
                parts = []
                if site_blocked:
                    parts.append('{} 个站源'.format(site_blocked))
                if live_blocked:
                    parts.append('{} 个直播源'.format(live_blocked))
                lines.insert(0, '已屏蔽 {}\n'.format(' + '.join(parts)))
            return self._detail(vod_id, '自检测设置', '\n'.join(lines), 'selfcheck')
        if vod_id == self.BLOCKED_ID:
            site_details = blocked_site_details()
            live_details = blocked_live_details()
            if not site_details and not live_details:
                return self._detail(vod_id, '屏蔽详情', '暂无被屏蔽的站源或直播源。', 'selfcheck')
            lines = []
            idx = 1
            if site_details:
                lines.append('【无效站源】共 {} 个：\n'.format(len(site_details)))
                for d in site_details:
                    lines.append('{}. {}'.format(idx, d.get('name', '')))
                    lines.append('   原因：{}'.format(d.get('reason', '')))
                    if d.get('source_path'):
                        lines.append('   源文件：{}'.format(d['source_path']))
                    lines.append('')
                    idx += 1
            if live_details:
                lines.append('【无效直播源】共 {} 个：\n'.format(len(live_details)))
                for d in live_details:
                    lines.append('{}. {}'.format(idx, d.get('name', '')))
                    lines.append('   原因：{}'.format(d.get('reason', '')))
                    if d.get('source_path'):
                        lines.append('   源文件：{}'.format(d['source_path']))
                    lines.append('')
                    idx += 1
            return self._detail(vod_id, '屏蔽详情', '\n'.join(lines), 'selfcheck')
        if vod_id == self.PARSE_ID:
            text = '\n'.join('{}：{}'.format(x.get('name', ''), x.get('url', '')) for x in current_parse_entries())
            return self._detail(vod_id, '解析设置', text or '暂无解析', 'status')
        if vod_id == self.SCAN_SET_ID:
            return self._detail(vod_id, '扫描设置', '如果没有弹窗，请用搜索修改：\n扫描=/路径1/|/路径2/\n\n当前扫描目录：\n{}'.format('\n'.join(scan_dirs)), 'folder')
        return self._detail(vod_id, '本地配置工具', '请选择首页卡片操作。', 'status')


    def _current_android_activity(self, jclass):
        app_class = jclass('com.fongmi.android.tv.App')
        activity_class = jclass('android.app.Activity')
        modifier_class = jclass('java.lang.reflect.Modifier')
        app_info = app_class.getClass()
        activity_info = activity_class.getClass()
        for method in app_info.getDeclaredMethods():
            try:
                if not modifier_class.isStatic(method.getModifiers()):
                    continue
                if len(method.getParameterTypes()) != 0:
                    continue
                if not activity_info.isAssignableFrom(method.getReturnType()):
                    continue
                method.setAccessible(True)
                try:
                    activity = method.invoke(None, [])
                except Exception:
                    activity = method.invoke(None)
                if activity is not None:
                    return activity
            except Exception:
                continue
        app = None
        for field in app_info.getDeclaredFields():
            try:
                if not modifier_class.isStatic(field.getModifiers()):
                    continue
                if not app_info.isAssignableFrom(field.getType()):
                    continue
                field.setAccessible(True)
                app = field.get(None)
                if app is not None:
                    break
            except Exception:
                continue
        if app is not None:
            for field in app.getClass().getDeclaredFields():
                try:
                    if modifier_class.isStatic(field.getModifiers()):
                        continue
                    if not activity_info.isAssignableFrom(field.getType()):
                        continue
                    field.setAccessible(True)
                    activity = field.get(app)
                    if activity is not None:
                        return activity
                except Exception:
                    continue
        raise ValueError('未找到当前 Android 页面')

    def _open_text_dialog(self, title, label, value, save_func):
        try:
            from java import dynamic_proxy, jclass
            toast_class = jclass('android.widget.Toast')
            edit_text_class = jclass('android.widget.EditText')
            linear_layout_class = jclass('android.widget.LinearLayout')
            text_view_class = jclass('android.widget.TextView')
            input_type = jclass('android.text.InputType')
            click_listener = jclass('android.content.DialogInterface$OnClickListener')
            show_listener = jclass('android.content.DialogInterface$OnShowListener')
            view_click_listener = jclass('android.view.View$OnClickListener')
            runnable_class = jclass('java.lang.Runnable')
            try:
                builder_class = jclass('com.google.android.material.dialog.MaterialAlertDialogBuilder')
            except Exception:
                builder_class = jclass('android.app.AlertDialog$Builder')
            activity = self._current_android_activity(jclass)
            owner = self
            class NoopClickListener(dynamic_proxy(click_listener)):
                def onClick(self, dialog, which):
                    return None
            class NoopShowListener(dynamic_proxy(show_listener)):
                def onShow(self, dialog):
                    return None
            class SaveButtonListener(dynamic_proxy(view_click_listener)):
                def __init__(self, edit, dialog):
                    super().__init__()
                    self.edit = edit
                    self.dialog = dialog
                def onClick(self, view):
                    try:
                        result = save_func(str(self.edit.getText().toString()))
                        toast_class.makeText(activity, '已保存：{}'.format(result), toast_class.LENGTH_LONG).show()
                        self.dialog.dismiss()
                    except Exception as exc:
                        toast_class.makeText(activity, '保存失败：{}'.format(exc), toast_class.LENGTH_LONG).show()
            class ShowDialog(dynamic_proxy(runnable_class)):
                def run(self):
                    density = float(activity.getResources().getDisplayMetrics().density)
                    padding = int(16 * density + 0.5)
                    spacing = int(8 * density + 0.5)
                    container = linear_layout_class(activity)
                    container.setOrientation(linear_layout_class.VERTICAL)
                    container.setPadding(padding, spacing, padding, 0)
                    label_view = text_view_class(activity)
                    label_view.setText(label)
                    edit = edit_text_class(activity)
                    edit.setSingleLine(False)
                    edit.setMinLines(1)
                    edit.setInputType(input_type.TYPE_CLASS_TEXT | input_type.TYPE_TEXT_FLAG_MULTI_LINE)
                    edit.setText(str(value or ''))
                    edit.setSelectAllOnFocus(True)
                    owner._style_input(activity, jclass, edit)
                    try:
                        color = jclass('android.graphics.Color')
                        label_view.setTextColor(color.parseColor('#64748B'))
                        label_view.setTextSize(11)
                        label_view.setPadding(0, 0, 0, owner._dp(activity, 8))
                    except Exception:
                        pass
                    container.addView(label_view)
                    container.addView(edit)
                    builder = builder_class(activity)
                    builder.setTitle(title)
                    builder.setView(container)
                    builder.setNegativeButton('取消', NoopClickListener())
                    builder.setPositiveButton('保存', NoopClickListener())
                    dialog = builder.create()
                    dialog.setOnShowListener(NoopShowListener())
                    dialog.show()
                    owner._style_dialog_buttons(activity, jclass, dialog, -1)
                    dialog.getButton(-1).setOnClickListener(SaveButtonListener(edit, dialog))
            activity.runOnUiThread(ShowDialog())
            return True, ''
        except Exception as exc:
            return False, '{}打开失败：{}'.format(title, exc)

    def _open_output_name_dialog(self):
        output_path, _ = self._settings_summary()
        return self._open_text_dialog('修改名字', '生成文件名', os.path.basename(output_path) or 'ss.json', set_output_name)

    def _open_output_path_dialog(self):
        output_path, _ = self._settings_summary()
        return self._open_text_dialog('修改路径', '保存目录', os.path.dirname(output_path) or ROOT_DIR, set_output_dir)

    def _open_output_full_dialog(self):
        output_path, _ = self._settings_summary()
        return self._open_text_dialog('完整输出', '完整输出文件', output_path, set_output_full_path)

    def _dp(self, activity, value):
        return int(float(value) * float(activity.getResources().getDisplayMetrics().density) + .5)

    def _rounded_bg(self, jclass, color, radius=8, stroke=None):
        drawable = jclass('android.graphics.drawable.GradientDrawable')()
        drawable.setShape(drawable.RECTANGLE)
        drawable.setCornerRadius(float(radius))
        drawable.setColor(jclass('android.graphics.Color').parseColor(color))
        if stroke:
            drawable.setStroke(1, jclass('android.graphics.Color').parseColor(stroke))
        return drawable

    def _style_input(self, activity, jclass, view):
        color = jclass('android.graphics.Color')
        view.setTextColor(color.parseColor('#1E293B'))
        view.setHintTextColor(color.parseColor('#94A3B8'))
        view.setTextSize(12)
        view.setPadding(self._dp(activity, 12), self._dp(activity, 9), self._dp(activity, 12), self._dp(activity, 9))
        view.setBackgroundDrawable(self._rounded_bg(jclass, '#F8FAFC', self._dp(activity, 8), '#E2E8F0'))

    def _style_dialog_buttons(self, activity, jclass, dialog, primary=-1):
        color = jclass('android.graphics.Color')
        for which in (-1, -2, -3):
            try:
                button = dialog.getButton(which)
                if button is None:
                    continue
                button.setAllCaps(False)
                button.setTextSize(12)
                button.setTextColor(color.parseColor('#6C63FF') if which == primary else color.parseColor('#475569'))
            except Exception:
                pass

    def _open_add_scan_dir_dialog(self):
        owner = self
        def save(path):
            result = add_scan_dir(path)
            owner._open_scan_dirs_dialog()
            return result
        return self._open_text_dialog('添加目录', '扫描目录路径', '', save)

    def _open_block_settings_dialog(self):
        try:
            from java import dynamic_proxy, jclass
            activity = self._current_android_activity(jclass)
            linear = jclass('android.widget.LinearLayout')
            text_view = jclass('android.widget.TextView')
            edit_text = jclass('android.widget.EditText')
            scroll = jclass('android.widget.ScrollView')
            runnable = jclass('java.lang.Runnable')
            dialog_click = jclass('android.content.DialogInterface$OnClickListener')
            click = jclass('android.view.View$OnClickListener')
            color = jclass('android.graphics.Color')
            typeface = jclass('android.graphics.Typeface')
            try:
                builder_class = jclass('com.google.android.material.dialog.MaterialAlertDialogBuilder')
            except Exception:
                builder_class = jclass('android.app.AlertDialog$Builder')
            owner = self
            class Noop(dynamic_proxy(dialog_click)):
                def onClick(self, dialog, which):
                    return None
            class Click(dynamic_proxy(click)):
                def __init__(self, fn):
                    super().__init__()
                    self.fn = fn
                def onClick(self, view):
                    self.fn()
            class Show(dynamic_proxy(runnable)):
                def run(self):
                    root = linear(activity)
                    root.setOrientation(linear.VERTICAL)
                    root.setPadding(owner._dp(activity, 16), owner._dp(activity, 8), owner._dp(activity, 16), owner._dp(activity, 4))
                    intro = text_view(activity)
                    intro.setText('使用逗号分隔，可直接增删内容')
                    intro.setTextColor(color.parseColor('#64748B'))
                    intro.setTextSize(11)
                    root.addView(intro)
                    fields = []
                    sections = [
                        ('屏蔽扫描文件夹', '命中名称的目录及其子目录不会扫描', sorted(current_blocked_dirs(), key=scan_sort_key)),
                        ('不显示的源文件', '命中文件名时不写入 sites', sorted(current_excluded_files(), key=scan_sort_key)),
                        ('18+ 标签', '关闭18+扫描时跳过带有这些标签的目录', current_adult_tags())
                    ]
                    for title, hint, values in sections:
                        label = text_view(activity)
                        label.setText('\n' + title)
                        label.setTextColor(color.parseColor('#1E293B'))
                        label.setTextSize(12)
                        label.setTypeface(typeface.DEFAULT_BOLD)
                        root.addView(label)
                        desc = text_view(activity)
                        desc.setText(hint)
                        desc.setTextColor(color.parseColor('#64748B'))
                        desc.setTextSize(10)
                        root.addView(desc)
                        edit = edit_text(activity)
                        edit.setText(','.join(values))
                        edit.setMinLines(2)
                        edit.setMaxLines(4)
                        owner._style_input(activity, jclass, edit)
                        root.addView(edit)
                        fields.append(edit)
                    wrapper = scroll(activity)
                    wrapper.addView(root)
                    builder = builder_class(activity)
                    builder.setTitle('屏蔽设置')
                    builder.setView(wrapper)
                    builder.setNegativeButton('取消', Noop())
                    builder.setPositiveButton('保存', Noop())
                    dialog = builder.create()
                    dialog.show()
                    owner._style_dialog_buttons(activity, jclass, dialog, -1)
                    def save():
                        save_block_settings(str(fields[0].getText()), str(fields[1].getText()), str(fields[2].getText()))
                        owner._toast('屏蔽设置已保存')
                        dialog.dismiss()
                    dialog.getButton(-1).setOnClickListener(Click(save))
            activity.runOnUiThread(Show())
            return True, ''
        except Exception as exc:
            return False, '屏蔽设置弹窗打开失败：{}'.format(exc)

    def _open_add_parse_dialog(self):
        try:
            from java import dynamic_proxy, jclass
            activity = self._current_android_activity(jclass)
            linear = jclass('android.widget.LinearLayout')
            text_view = jclass('android.widget.TextView')
            edit_text = jclass('android.widget.EditText')
            runnable = jclass('java.lang.Runnable')
            dialog_click = jclass('android.content.DialogInterface$OnClickListener')
            click = jclass('android.view.View$OnClickListener')
            color = jclass('android.graphics.Color')
            try:
                builder_class = jclass('com.google.android.material.dialog.MaterialAlertDialogBuilder')
            except Exception:
                builder_class = jclass('android.app.AlertDialog$Builder')
            owner = self
            class Noop(dynamic_proxy(dialog_click)):
                def onClick(self, dialog, which):
                    return None
            class Click(dynamic_proxy(click)):
                def __init__(self, fn):
                    super().__init__()
                    self.fn = fn
                def onClick(self, view):
                    self.fn()
            class Show(dynamic_proxy(runnable)):
                def run(self):
                    root = linear(activity)
                    root.setOrientation(linear.VERTICAL)
                    root.setPadding(owner._dp(activity, 16), owner._dp(activity, 8), owner._dp(activity, 16), 0)
                    fields = []
                    for label_text, hint in (('解析名字', '例如：线路一'), ('解析 URL', '例如：https://example.com/?url=')):
                        label = text_view(activity)
                        label.setText(label_text)
                        label.setTextColor(color.parseColor('#1E293B'))
                        label.setTextSize(12)
                        label.setPadding(0, owner._dp(activity, 8), 0, owner._dp(activity, 5))
                        root.addView(label)
                        edit = edit_text(activity)
                        edit.setHint(hint)
                        edit.setSingleLine(True)
                        owner._style_input(activity, jclass, edit)
                        root.addView(edit)
                        fields.append(edit)
                    builder = builder_class(activity)
                    builder.setTitle('增加解析')
                    builder.setView(root)
                    builder.setNegativeButton('取消', Noop())
                    builder.setPositiveButton('增加', Noop())
                    dialog = builder.create()
                    dialog.show()
                    owner._style_dialog_buttons(activity, jclass, dialog, -1)
                    def add():
                        name, url = str(fields[0].getText()).strip(), str(fields[1].getText()).strip()
                        if not name or not url:
                            owner._toast('解析名字和 URL 不能为空')
                            return
                        entries = current_parse_entries()
                        entries.append({'name': name, 'type': 0, 'url': url, 'enabled': True})
                        save_parse_entries(entries)
                        dialog.dismiss()
                        owner._open_parse_settings_dialog()
                    dialog.getButton(-1).setOnClickListener(Click(add))
            activity.runOnUiThread(Show())
            return True, ''
        except Exception as exc:
            return False, '增加解析弹窗打开失败：{}'.format(exc)

    def _open_parse_settings_dialog(self):
        try:
            from java import dynamic_proxy, jclass
            activity = self._current_android_activity(jclass)
            linear = jclass('android.widget.LinearLayout')
            text_view = jclass('android.widget.TextView')
            switch = jclass('android.widget.Switch')
            button = jclass('android.widget.Button')
            layout_params = jclass('android.widget.LinearLayout$LayoutParams')
            scroll = jclass('android.widget.ScrollView')
            runnable = jclass('java.lang.Runnable')
            click = jclass('android.view.View$OnClickListener')
            dialog_click = jclass('android.content.DialogInterface$OnClickListener')
            color = jclass('android.graphics.Color')
            try:
                builder_class = jclass('com.google.android.material.dialog.MaterialAlertDialogBuilder')
            except Exception:
                builder_class = jclass('android.app.AlertDialog$Builder')
            owner = self
            entries = current_parse_entries()
            class Noop(dynamic_proxy(dialog_click)):
                def onClick(self, dialog, which):
                    return None
            class Click(dynamic_proxy(click)):
                def __init__(self, fn):
                    super().__init__()
                    self.fn = fn
                def onClick(self, view):
                    self.fn()
            class Show(dynamic_proxy(runnable)):
                def run(self):
                    root = linear(activity)
                    root.setOrientation(linear.VERTICAL)
                    root.setPadding(owner._dp(activity, 16), owner._dp(activity, 6), owner._dp(activity, 16), 0)
                    intro = text_view(activity)
                    intro.setText('当前解析列表')
                    intro.setTextColor(color.parseColor('#64748B'))
                    intro.setTextSize(11)
                    root.addView(intro)
                    switches = []
                    for index, entry in enumerate(entries):
                        row = linear(activity)
                        row.setOrientation(linear.HORIZONTAL)
                        row.setGravity(16)
                        row.setPadding(0, owner._dp(activity, 8), 0, owner._dp(activity, 8))
                        enabled = switch(activity)
                        enabled.setText('{}\n{}'.format(entry.get('name', ''), entry.get('url', '')))
                        enabled.setTextColor(color.parseColor('#334155'))
                        enabled.setTextSize(11)
                        enabled.setLineSpacing(owner._dp(activity, 3), 1.15)
                        enabled.setPadding(0, owner._dp(activity, 4), owner._dp(activity, 8), owner._dp(activity, 4))
                        enabled.setChecked(entry.get('enabled', True))
                        row.addView(enabled, layout_params(0, -2, 1.0))
                        switches.append(enabled)
                        delete = button(activity)
                        delete.setText('删除')
                        delete.setAllCaps(False)
                        delete.setTextColor(color.WHITE)
                        delete.setTextSize(11)
                        delete.setMinWidth(owner._dp(activity, 52))
                        delete.setMinimumWidth(owner._dp(activity, 52))
                        delete.setMinHeight(owner._dp(activity, 32))
                        delete.setMinimumHeight(owner._dp(activity, 32))
                        delete.setPadding(owner._dp(activity, 12), owner._dp(activity, 5), owner._dp(activity, 12), owner._dp(activity, 5))
                        delete.setBackgroundDrawable(owner._rounded_bg(jclass, '#EF4444', owner._dp(activity, 7)))
                        def remove(i=index):
                            fresh = current_parse_entries()
                            if 0 <= i < len(fresh):
                                fresh.pop(i)
                                save_parse_entries(fresh)
                            dialog.dismiss()
                            owner._open_parse_settings_dialog()
                        delete.setOnClickListener(Click(remove))
                        row.addView(delete)
                        root.addView(row)
                        if index < len(entries) - 1:
                            divider = text_view(activity)
                            divider.setBackgroundColor(color.parseColor('#E2E8F0'))
                            root.addView(divider, layout_params(-1, owner._dp(activity, 1)))
                    wrapper = scroll(activity)
                    wrapper.addView(root)
                    builder = builder_class(activity)
                    builder.setTitle('解析设置')
                    builder.setView(wrapper)
                    builder.setNegativeButton('增加解析', Noop())
                    builder.setPositiveButton('确认', Noop())
                    dialog = builder.create()
                    dialog.show()
                    owner._style_dialog_buttons(activity, jclass, dialog, -1)
                    def confirm():
                        for i, view in enumerate(switches):
                            if i < len(entries):
                                entries[i]['enabled'] = view.isChecked()
                        save_parse_entries(entries)
                        owner._toast('解析设置已保存')
                        dialog.dismiss()
                    def add():
                        for i, view in enumerate(switches):
                            if i < len(entries):
                                entries[i]['enabled'] = view.isChecked()
                        save_parse_entries(entries)
                        dialog.dismiss()
                        owner._open_add_parse_dialog()
                    dialog.getButton(-1).setOnClickListener(Click(confirm))
                    dialog.getButton(-2).setOnClickListener(Click(add))
            activity.runOnUiThread(Show())
            return True, ''
        except Exception as exc:
            return False, '解析设置弹窗打开失败：{}'.format(exc)

    def _open_scan_dirs_dialog(self):
        try:
            from java import dynamic_proxy, jclass
            activity = self._current_android_activity(jclass)
            linear = jclass('android.widget.LinearLayout')
            text_view = jclass('android.widget.TextView')
            switch = jclass('android.widget.Switch')
            button = jclass('android.widget.Button')
            layout_params = jclass('android.widget.LinearLayout$LayoutParams')
            scroll = jclass('android.widget.ScrollView')
            runnable = jclass('java.lang.Runnable')
            click = jclass('android.view.View$OnClickListener')
            dialog_click = jclass('android.content.DialogInterface$OnClickListener')
            try:
                builder_class = jclass('com.google.android.material.dialog.MaterialAlertDialogBuilder')
            except Exception:
                builder_class = jclass('android.app.AlertDialog$Builder')
            owner = self
            class Noop(dynamic_proxy(dialog_click)):
                def onClick(self, dialog, which):
                    return None
            class Click(dynamic_proxy(click)):
                def __init__(self, fn):
                    super().__init__()
                    self.fn = fn
                def onClick(self, view):
                    self.fn()
            class Show(dynamic_proxy(runnable)):
                def run(self):
                    density = float(activity.getResources().getDisplayMetrics().density)
                    pad = int(16 * density + .5)
                    root = linear(activity)
                    root.setOrientation(linear.VERTICAL)
                    root.setPadding(pad, pad // 2, pad, owner._dp(activity, 4))
                    color = jclass('android.graphics.Color')
                    typeface = jclass('android.graphics.Typeface')
                    title = text_view(activity)
                    title.setText('扫描文件类型（可多选）')
                    title.setTextColor(color.parseColor('#1E293B'))
                    title.setTextSize(12)
                    title.setTypeface(typeface.DEFAULT_BOLD)
                    root.addView(title)
                    checks = {}
                    type_grid = linear(activity)
                    type_grid.setOrientation(linear.VERTICAL)
                    row = None
                    adult = None
                    grid_items = list(SCAN_FILE_TYPES.items()) + [('__adult__', '18+')]
                    for index, (ext, label) in enumerate(grid_items):
                        if index % 2 == 0:
                            row = linear(activity)
                            row.setOrientation(linear.HORIZONTAL)
                            row.setGravity(16)
                            row.setPadding(0, 0, 0, 0)
                            type_row_lp = layout_params(-1, -2)
                            type_row_lp.setMargins(0, 0, 0, -owner._dp(activity, 2))
                            type_grid.addView(row, type_row_lp)
                        item = switch(activity)
                        item.setText(label)
                        item.setTextColor(color.parseColor('#334155'))
                        item.setTextSize(12)
                        item.setGravity(16)
                        item.setPadding(0, 0, 0, 0)
                        if ext == '__adult__':
                            item.setChecked(current_adult_enabled())
                            adult = item
                        else:
                            item.setChecked(ext in current_scan_extensions())
                            checks[ext] = item
                        item_lp = layout_params(0, -2, 1.0)
                        gap = owner._dp(activity, 8)
                        item_lp.setMargins(0 if index % 2 == 0 else gap, 0, gap if index % 2 == 0 else 0, 0)
                        row.addView(item, item_lp)
                    if len(grid_items) % 2:
                        blank_lp = layout_params(0, -2, 1.0)
                        blank_lp.setMargins(owner._dp(activity, 8), 0, 0, 0)
                        row.addView(text_view(activity), blank_lp)
                    root.addView(type_grid)
                    dirs_title = text_view(activity)
                    dirs_title.setText('\n设置目录列表')
                    dirs_title.setTextColor(color.parseColor('#1E293B'))
                    dirs_title.setTextSize(12)
                    dirs_title.setTypeface(typeface.DEFAULT_BOLD)
                    root.addView(dirs_title)
                    scan_dirs = current_scan_dirs()
                    for index, path in enumerate(scan_dirs, 1):
                        row = linear(activity)
                        row.setOrientation(linear.HORIZONTAL)
                        row.setGravity(16)
                        row.setPadding(0, owner._dp(activity, 8), 0, owner._dp(activity, 8))
                        enabled = switch(activity)
                        enabled.setText('{}. {}'.format(index, path))
                        enabled.setTextColor(color.parseColor('#334155'))
                        enabled.setTextSize(11)
                        enabled.setPadding(0, owner._dp(activity, 3), owner._dp(activity, 4), owner._dp(activity, 3))
                        enabled.setChecked(path in current_enabled_scan_dirs())
                        def toggle(p=path, view=enabled):
                            set_scan_dir_enabled(p, view.isChecked())
                        enabled.setOnClickListener(Click(toggle))
                        row.addView(enabled, layout_params(0, -2, 1.0))
                        delete = button(activity)
                        delete.setText('删除')
                        delete.setAllCaps(False)
                        delete.setTextColor(color.WHITE)
                        delete.setTextSize(11)
                        delete.setMinWidth(owner._dp(activity, 52))
                        delete.setMinimumWidth(owner._dp(activity, 52))
                        delete.setMinHeight(owner._dp(activity, 32))
                        delete.setMinimumHeight(owner._dp(activity, 32))
                        delete.setPadding(owner._dp(activity, 12), owner._dp(activity, 5), owner._dp(activity, 12), owner._dp(activity, 5))
                        delete.setBackgroundDrawable(owner._rounded_bg(jclass, '#EF4444', owner._dp(activity, 7)))
                        def remove(p=path):
                            remove_scan_dir(p)
                            owner._toast('已删除：' + p)
                            try:
                                dialog.dismiss()
                            except Exception:
                                pass
                            owner._open_scan_dirs_dialog()
                        delete.setOnClickListener(Click(remove))
                        row.addView(delete)
                        root.addView(row)
                        if index < len(scan_dirs):
                            divider = text_view(activity)
                            divider.setBackgroundColor(color.parseColor('#E2E8F0'))
                            root.addView(divider, layout_params(-1, owner._dp(activity, 1)))
                    def persist():
                        selected = [ext for ext, view in checks.items() if view.isChecked()]
                        save_scan_options(selected, adult.isChecked())
                    for view in checks.values():
                        view.setOnClickListener(Click(persist))
                    adult.setOnClickListener(Click(persist))
                    wrapper = scroll(activity)
                    wrapper.addView(root)
                    builder = builder_class(activity)
                    builder.setTitle('扫描设置')
                    builder.setView(wrapper)
                    def add():
                        persist()
                        dialog.dismiss()
                        owner._open_add_scan_dir_dialog()
                    builder.setNegativeButton('添加目录', Noop())
                    builder.setPositiveButton('关闭', Noop())
                    dialog = builder.create()
                    dialog.show()
                    owner._style_dialog_buttons(activity, jclass, dialog, -1)
                    dialog.getButton(-2).setOnClickListener(Click(add))
            activity.runOnUiThread(Show())
            return True, ''
        except Exception as exc:
            return False, '扫描设置弹窗打开失败：{}'.format(exc)


    def _open_selfcheck_settings_dialog(self):
        try:
            from java import dynamic_proxy, jclass
            activity = self._current_android_activity(jclass)
            linear = jclass('android.widget.LinearLayout')
            text_view = jclass('android.widget.TextView')
            switch = jclass('android.widget.Switch')
            edit_text = jclass('android.widget.EditText')
            layout_params = jclass('android.widget.LinearLayout$LayoutParams')
            scroll = jclass('android.widget.ScrollView')
            runnable = jclass('java.lang.Runnable')
            click = jclass('android.view.View$OnClickListener')
            dialog_click = jclass('android.content.DialogInterface$OnClickListener')
            color = jclass('android.graphics.Color')
            typeface = jclass('android.graphics.Typeface')
            try:
                builder_class = jclass('com.google.android.material.dialog.MaterialAlertDialogBuilder')
            except Exception:
                builder_class = jclass('android.app.AlertDialog$Builder')
            owner = self
            sc = current_self_check_settings()
            class Noop(dynamic_proxy(dialog_click)):
                def onClick(self, dialog, which):
                    return None
            class Click(dynamic_proxy(click)):
                def __init__(self, fn):
                    super().__init__()
                    self.fn = fn
                def onClick(self, view):
                    self.fn()
            class Show(dynamic_proxy(runnable)):
                def run(self):
                    root = linear(activity)
                    root.setOrientation(linear.VERTICAL)
                    root.setPadding(owner._dp(activity, 16), owner._dp(activity, 8), owner._dp(activity, 16), owner._dp(activity, 4))

                    intro = text_view(activity)
                    intro.setText('自动检测扫描到的站源是否有效，无效站源将被屏蔽')
                    intro.setTextColor(color.parseColor('#64748B'))
                    intro.setTextSize(11)
                    intro.setLineSpacing(owner._dp(activity, 3), 1.15)
                    root.addView(intro)

                    toggles = {}

                    def add_toggle(key, label, hint, checked):
                        row = linear(activity)
                        row.setOrientation(linear.VERTICAL)
                        row.setPadding(0, owner._dp(activity, 8), 0, owner._dp(activity, 4))
                        sw = switch(activity)
                        sw.setText(label)
                        sw.setTextColor(color.parseColor('#334155'))
                        sw.setTextSize(12)
                        sw.setChecked(checked)
                        sw.setPadding(0, owner._dp(activity, 2), 0, 0)
                        row.addView(sw)
                        if hint:
                            desc = text_view(activity)
                            desc.setText(hint)
                            desc.setTextColor(color.parseColor('#94A3B8'))
                            desc.setTextSize(10)
                            desc.setPadding(owner._dp(activity, 4), 0, 0, owner._dp(activity, 2))
                            row.addView(desc)
                        root.addView(row)
                        toggles[key] = sw

                    add_toggle('enabled', '启用自检测', '关闭后所有站源均不做有效性检测', sc.get('enabled', True))
                    add_toggle('jar_enabled', '检测 JAR 依赖', '检查站点引用的 jar 文件是否存在', sc.get('jar_enabled', True))
                    add_toggle('drpy_enabled', '检测 drpy 引擎', '检查 drpy 站点引用的 drpy2.min.js 是否存在', sc.get('drpy_enabled', True))
                    add_toggle('remote_enabled', '检测远程 API 可达性', '对 http/https API 发起轻量请求（可能拖慢速度）', sc.get('remote_enabled', False))

                    # 最小字节数输入
                    size_label = text_view(activity)
                    size_label.setText('\n最小字节数')
                    size_label.setTextColor(color.parseColor('#1E293B'))
                    size_label.setTextSize(12)
                    size_label.setTypeface(typeface.DEFAULT_BOLD)
                    root.addView(size_label)
                    size_hint = text_view(activity)
                    size_hint.setText('小于该值的源文件视为空壳/占位/模板，判定无效')
                    size_hint.setTextColor(color.parseColor('#94A3B8'))
                    size_hint.setTextSize(10)
                    root.addView(size_hint)
                    size_edit = edit_text(activity)
                    size_edit.setText(str(sc.get('min_size', 8)))
                    size_edit.setSingleLine(True)
                    owner._style_input(activity, jclass, size_edit)
                    root.addView(size_edit)

                    # 最小有效行数输入
                    lines_label = text_view(activity)
                    lines_label.setText('\n最小有效代码行数')
                    lines_label.setTextColor(color.parseColor('#1E293B'))
                    lines_label.setTextSize(12)
                    lines_label.setTypeface(typeface.DEFAULT_BOLD)
                    root.addView(lines_label)
                    lines_hint = text_view(activity)
                    lines_hint.setText('JS/PY/PHP 去除注释和空行后不足该值视为空壳，判定无效')
                    lines_hint.setTextColor(color.parseColor('#94A3B8'))
                    lines_hint.setTextSize(10)
                    root.addView(lines_hint)
                    lines_edit = edit_text(activity)
                    lines_edit.setText(str(sc.get('min_effective_lines', 3)))
                    lines_edit.setSingleLine(True)
                    owner._style_input(activity, jclass, lines_edit)
                    root.addView(lines_edit)

                    # 远程超时输入
                    timeout_label = text_view(activity)
                    timeout_label.setText('\n远程检测超时（秒）')
                    timeout_label.setTextColor(color.parseColor('#1E293B'))
                    timeout_label.setTextSize(12)
                    timeout_label.setTypeface(typeface.DEFAULT_BOLD)
                    root.addView(timeout_label)
                    timeout_edit = edit_text(activity)
                    timeout_edit.setText(str(sc.get('remote_timeout', 5)))
                    timeout_edit.setSingleLine(True)
                    owner._style_input(activity, jclass, timeout_edit)
                    root.addView(timeout_edit)

                    # 当前屏蔽统计
                    site_blocked = len(BLOCKED_SITE_RECORDS)
                    live_blocked = len(BLOCKED_LIVE_RECORDS)
                    if site_blocked or live_blocked:
                        parts = []
                        if site_blocked:
                            parts.append('{} 个站源'.format(site_blocked))
                        if live_blocked:
                            parts.append('{} 个直播源'.format(live_blocked))
                        stat = text_view(activity)
                        stat.setText('\n当前已屏蔽 {}'.format(' + '.join(parts)))
                        stat.setTextColor(color.parseColor('#EF4444'))
                        stat.setTextSize(11)
                        root.addView(stat)

                    wrapper = scroll(activity)
                    wrapper.addView(root)
                    builder = builder_class(activity)
                    builder.setTitle('自检测设置')
                    builder.setView(wrapper)
                    builder.setNegativeButton('取消', Noop())
                    builder.setPositiveButton('保存', Noop())
                    dialog = builder.create()
                    dialog.show()
                    owner._style_dialog_buttons(activity, jclass, dialog, -1)

                    def save():
                        try:
                            min_size = int(str(size_edit.getText()).strip() or '8')
                        except Exception:
                            min_size = 8
                        try:
                            min_effective_lines = int(str(lines_edit.getText()).strip() or '3')
                        except Exception:
                            min_effective_lines = 3
                        try:
                            remote_timeout = int(str(timeout_edit.getText()).strip() or '5')
                        except Exception:
                            remote_timeout = 5
                        new_sc = {
                            'enabled': toggles['enabled'].isChecked(),
                            'min_size': min_size,
                            'min_effective_lines': min_effective_lines,
                            'jar_enabled': toggles['jar_enabled'].isChecked(),
                            'drpy_enabled': toggles['drpy_enabled'].isChecked(),
                            'remote_enabled': toggles['remote_enabled'].isChecked(),
                            'remote_timeout': remote_timeout
                        }
                        save_self_check_settings(new_sc)
                        owner._toast('自检测设置已保存')
                        dialog.dismiss()
                    dialog.getButton(-1).setOnClickListener(Click(save))
            activity.runOnUiThread(Show())
            return True, ''
        except Exception as exc:
            return False, '自检测设置弹窗打开失败：{}'.format(exc)


    def _open_blocked_sites_dialog(self):
        try:
            from java import dynamic_proxy, jclass
            activity = self._current_android_activity(jclass)
            linear = jclass('android.widget.LinearLayout')
            text_view = jclass('android.widget.TextView')
            layout_params = jclass('android.widget.LinearLayout$LayoutParams')
            scroll = jclass('android.widget.ScrollView')
            runnable = jclass('java.lang.Runnable')
            click = jclass('android.view.View$OnClickListener')
            dialog_click = jclass('android.content.DialogInterface$OnClickListener')
            color = jclass('android.graphics.Color')
            try:
                builder_class = jclass('com.google.android.material.dialog.MaterialAlertDialogBuilder')
            except Exception:
                builder_class = jclass('android.app.AlertDialog$Builder')
            owner = self
            site_details = blocked_site_details()
            live_details = blocked_live_details()
            all_details = site_details + live_details
            class Noop(dynamic_proxy(dialog_click)):
                def onClick(self, dialog, which):
                    return None
            class Click(dynamic_proxy(click)):
                def __init__(self, fn):
                    super().__init__()
                    self.fn = fn
                def onClick(self, view):
                    self.fn()
            class Show(dynamic_proxy(runnable)):
                def run(self):
                    root = linear(activity)
                    root.setOrientation(linear.VERTICAL)
                    root.setPadding(owner._dp(activity, 16), owner._dp(activity, 8), owner._dp(activity, 16), owner._dp(activity, 4))

                    if not all_details:
                        empty = text_view(activity)
                        empty.setText('暂无被屏蔽的站源或直播源\n\n可能原因：\n• 自检测已关闭\n• 全部源有效\n• 尚未执行本地加载')
                        empty.setTextColor(color.parseColor('#64748B'))
                        empty.setTextSize(12)
                        empty.setLineSpacing(owner._dp(activity, 3), 1.2)
                        root.addView(empty)
                    else:
                        idx = 1
                        typeface = jclass('android.graphics.Typeface')
                        def add_section(title, items):
                            nonlocal idx
                            if not items:
                                return
                            header = text_view(activity)
                            header.setText(title)
                            header.setTextColor(color.parseColor('#1E293B'))
                            header.setTextSize(13)
                            header.setTypeface(typeface.DEFAULT_BOLD)
                            root.addView(header)
                            for d in items:
                                item_layout = linear(activity)
                                item_layout.setOrientation(linear.VERTICAL)
                                item_layout.setPadding(0, owner._dp(activity, 6), 0, owner._dp(activity, 6))
                                name_view = text_view(activity)
                                name_view.setText('{}. {}'.format(idx, d.get('name', '')))
                                name_view.setTextColor(color.parseColor('#DC2626'))
                                name_view.setTextSize(12)
                                item_layout.addView(name_view)
                                reason_view = text_view(activity)
                                reason_view.setText('   原因：{}'.format(d.get('reason', '')))
                                reason_view.setTextColor(color.parseColor('#64748B'))
                                reason_view.setTextSize(10)
                                item_layout.addView(reason_view)
                                if d.get('source_path'):
                                    path_view = text_view(activity)
                                    path_view.setText('   源文件：{}'.format(d['source_path']))
                                    path_view.setTextColor(color.parseColor('#94A3B8'))
                                    path_view.setTextSize(10)
                                    item_layout.addView(path_view)
                                root.addView(item_layout)
                                divider = text_view(activity)
                                divider.setBackgroundColor(color.parseColor('#E2E8F0'))
                                root.addView(divider, layout_params(-1, owner._dp(activity, 1)))
                                idx += 1

                        add_section('【无效站源】共 {} 个：'.format(len(site_details)), site_details)
                        add_section('【无效直播源】共 {} 个：'.format(len(live_details)), live_details)

                    wrapper = scroll(activity)
                    wrapper.addView(root)
                    builder = builder_class(activity)
                    builder.setTitle('屏蔽详情')
                    builder.setView(wrapper)
                    builder.setNegativeButton('关闭', Noop())
                    if all_details:
                        builder.setPositiveButton('重新加载', Noop())
                    dialog = builder.create()
                    dialog.show()
                    owner._style_dialog_buttons(activity, jclass, dialog, -1)
                    if all_details:
                        def reload():
                            dialog.dismiss()
                            owner.action('local_load')
                        dialog.getButton(-1).setOnClickListener(Click(reload))
            activity.runOnUiThread(Show())
            return True, ''
        except Exception as exc:
            return False, '屏蔽详情弹窗打开失败：{}'.format(exc)


    def _toast(self, message):
        try:
            from java import jclass
            toast_class = jclass('android.widget.Toast')
            activity = self._current_android_activity(jclass)
            toast_class.makeText(activity, str(message), toast_class.LENGTH_SHORT).show()
            return True
        except Exception:
            return False

    def _show_message_dialog(self, title, message):
        try:
            from java import dynamic_proxy, jclass
            click_listener = jclass('android.content.DialogInterface$OnClickListener')
            runnable_class = jclass('java.lang.Runnable')
            try:
                builder_class = jclass('com.google.android.material.dialog.MaterialAlertDialogBuilder')
            except Exception:
                builder_class = jclass('android.app.AlertDialog$Builder')
            activity = self._current_android_activity(jclass)
            owner = self
            class NoopClickListener(dynamic_proxy(click_listener)):
                def onClick(self, dialog, which):
                    return None
            class ShowDialog(dynamic_proxy(runnable_class)):
                def run(self):
                    builder = builder_class(activity)
                    builder.setTitle(str(title))
                    builder.setMessage(str(message))
                    builder.setPositiveButton('确定', NoopClickListener())
                    dialog = builder.create()
                    dialog.show()
                    owner._style_dialog_buttons(activity, jclass, dialog, -1)
            activity.runOnUiThread(ShowDialog())
            return True, ''
        except Exception as exc:
            return False, '{}弹窗失败：{}'.format(title, exc)


    def _show_loading_dialog(self, title='本地加载', message='加载中，请稍候...'):
        holder = {'dialog': None}
        try:
            from java import dynamic_proxy, jclass
            runnable_class = jclass('java.lang.Runnable')
            try:
                builder_class = jclass('com.google.android.material.dialog.MaterialAlertDialogBuilder')
            except Exception:
                builder_class = jclass('android.app.AlertDialog$Builder')
            activity = self._current_android_activity(jclass)
            class ShowDialog(dynamic_proxy(runnable_class)):
                def run(self):
                    builder = builder_class(activity)
                    builder.setTitle(str(title))
                    builder.setMessage(str(message))
                    try:
                        builder.setCancelable(False)
                    except Exception:
                        pass
                    dialog = builder.create()
                    holder['dialog'] = dialog
                    dialog.show()
            activity.runOnUiThread(ShowDialog())
            return holder
        except Exception:
            self._toast(message)
            return holder

    def _dismiss_dialog_holder(self, holder):
        try:
            dialog = holder.get('dialog') if isinstance(holder, dict) else None
            if dialog is not None:
                dialog.dismiss()
        except Exception:
            pass

    def action(self, action):
        action = str(action or '')
        if action == 'local_load':
            loading = self._show_loading_dialog('本地加载', '加载中，请稍候...')
            try:
                info = generate_and_write_config()
                self._dismiss_dialog_holder(loading)
                message = '加载完成！\n站点数量：{}\n直播数量：{}\n生成文件：{}\n扫描目录：{}'.format(info['sites'], info['lives'], info['output_path'], ' | '.join(info['scan_dirs']))
                blocked_total = info.get('blocked_sites', 0) + info.get('blocked_lives', 0)
                if blocked_total > 0:
                    parts = []
                    if info.get('blocked_sites', 0):
                        parts.append('{} 个站源'.format(info['blocked_sites']))
                    if info.get('blocked_lives', 0):
                        parts.append('{} 个直播源'.format(info['blocked_lives']))
                    message += '\n已屏蔽 {}'.format(' + '.join(parts))
                    summary = blocked_site_summary()
                    if summary and summary != '全部站源有效，无屏蔽':
                        message += '\n' + summary
                opened, err = self._show_message_dialog('本地加载', message)
                return {'code': 0, 'msg': '' if opened else message}
            except Exception as e:
                self._dismiss_dialog_holder(loading)
                message = '加载失败：{}'.format(e)
                opened, err = self._show_message_dialog('本地加载', message)
                return {'code': 0, 'msg': '' if opened else message}
        if action == 'edit_output_name':
            opened, message = self._open_output_name_dialog()
            return {'code': 0, 'msg': '' if opened else message}
        if action == 'edit_output_path':
            opened, message = self._open_output_path_dialog()
            return {'code': 0, 'msg': '' if opened else message}
        if action == 'edit_output_full':
            opened, message = self._open_output_full_dialog()
            return {'code': 0, 'msg': '' if opened else message}
        if action == 'edit_scan_dirs':
            opened, message = self._open_scan_dirs_dialog()
            return {'code': 0, 'msg': '' if opened else message}
        if action == 'edit_block_settings':
            opened, message = self._open_block_settings_dialog()
            return {'code': 0, 'msg': '' if opened else message}
        if action == 'edit_parse_settings':
            opened, message = self._open_parse_settings_dialog()
            return {'code': 0, 'msg': '' if opened else message}
        if action == 'edit_selfcheck_settings':
            opened, message = self._open_selfcheck_settings_dialog()
            return {'code': 0, 'msg': '' if opened else message}
        if action == 'view_blocked_sites':
            opened, message = self._open_blocked_sites_dialog()
            return {'code': 0, 'msg': '' if opened else message}
        return {'code': 0, 'msg': ''}

    def searchContent(self, key, quick=False, pg='1'):
        text = str(key or '').strip()
        try:
            if text.startswith(('文件名=', 'name=')):
                value = text.split('=', 1)[1]
                path = set_output_name(value)
                return {'list': [self._card(self.OUTPUT_ID, '文件名已更新', 'download', path)]}
            if text.startswith(('路径=', 'path=')):
                value = text.split('=', 1)[1]
                path = set_output_dir(value)
                return {'list': [self._card(self.OUTPUT_ID, '保存路径已更新', 'folder', path)]}
            if text.startswith(('输出=', 'output=')):
                value = text.split('=', 1)[1]
                path = set_output_full_path(value)
                return {'list': [self._card(self.OUTPUT_ID, '输出文件已更新', 'download', path)]}
            if text.startswith(('扫描=', 'scan=')):
                value = text.split('=', 1)[1]
                dirs = set_scan_dirs(value)
                return {'list': [self._card(self.SCAN_ID, '扫描目录已更新', 'folder', ' | '.join(dirs))]}
        except Exception as e:
            return {'list': [self._card('__cc_error__', '设置失败', 'status', str(e))]}
        return {'list': self._output_setting_items() + self._scan_setting_items()}

    def playerContent(self, flag, id, vipFlags):
        return {'parse': 0, 'playUrl': '', 'url': str(id or ''), 'header': {}}

    def localProxy(self, param):
        return None

# ==================== 命令行入口 ====================

if __name__ == "__main__":
    try:
        if len(sys.argv) > 1 and sys.argv[1] in ('load', 'refresh', '生成', '刷新'):
            info = generate_and_write_config()
            summary = blocked_site_summary()
            if summary and summary != '全部站源有效，无屏蔽':
                print(summary, file=sys.stderr)
            json.dump(info, sys.stdout, indent=2, ensure_ascii=False)
        else:
            json.dump(Spider().homeVideoContent(), sys.stdout, indent=2, ensure_ascii=False)
    except Exception as e:
        fallback = {
            "spider": "",
            "logo": "",
            "sites": [{"key": "error", "name": f"配置加载失败: {e}", "type": 1, "api": ""}]
        }
        json.dump(fallback, sys.stdout, indent=2, ensure_ascii=False)