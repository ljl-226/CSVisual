"""
云端沙箱兜底执行（与 Node 版 utils/remoteRun.js 同构）

为什么要有这一层：本机执行链路依赖两件事 —— 机器上装了编译器、后端进程
有权创建子进程。任何一条不满足（没装 gcc/JDK、后端被开发工具拉起继承受限
环境 EBUSY/EPERM、杀软锁死编译器），"运行/判分"就整个瘫痪。

方案：把代码 POST 到公共云沙箱编译执行。语义与本地一致：
stdin 进、stdout/stderr 出、退出码比对，判分逻辑无需改动。

服务商链（按顺序尝试，任一成功即返回）：
    1. 自建 Piston（设置 PISTON_URL 环境变量时启用）；
    2. Wandbox 公共实例（wandbox.org，免密钥）。
    注：Piston 官方公共实例 2026/2/15 起改为白名单制（401），只能自建。

urllib 原生尊重系统代理环境变量（HTTPS_PROXY 等，Windows 下连注册表
代理设置都会读），无需像 Node 版那样手动建 CONNECT 隧道。

返回值约定（调用方据此决定是否兜底成功）：
    {'ok': True,  'stdout': ..., 'stderr': ..., 'exitCode': 0}      执行成功（程序本身可能报错）
    {'ok': False, 'compileError': True, 'stderr': ...}              云端编译失败（代码问题）
    {'ok': False, 'reason': ...}                                    云端不可达/被关闭
"""

import json
import os
import re
import time
import urllib.error
import urllib.request

# 云端回显给用户的前缀：说明这条结果不是本机跑出来的
NOTICE = '『云端沙箱』本机没有可用的编译环境，本次结果由内置云端沙箱执行返回。\n'

# ==================== Wandbox ====================

_WANDBOX_API = 'https://wandbox.org/api/compile.json'
WANDBOX_COMPILER = {
    'c': 'gcc-13.2.0-c',
    'cpp': 'gcc-13.2.0',
    'java': 'openjdk-jdk-21+35',
    'python': 'cpython-3.12.7',
    'javascript': 'nodejs-20.17.0',
}


def _java_class_rename(code, cls_name):
    """Wandbox 把 Java 代码写成 prog.java（Piston 用 Main.java）：
    public 类名必须与文件名一致才能编译"""
    m = re.search(r'public\s+class\s+([A-Za-z_]\w*)', code)
    cls = m.group(1) if m else None
    if cls and cls != cls_name:
        return re.sub(r'\b' + cls + r'\b', cls_name, code)
    return code


def _post_json(url, body_obj, timeout):
    """POST JSON 并解析响应；429 等一拍重试一次"""
    payload = json.dumps(body_obj).encode('utf-8')

    def _once():
        req = urllib.request.Request(
            url, data=payload,
            # Wandbox（Cloudflare）会 403 掉 Python-urllib 默认 UA
            headers={'Content-Type': 'application/json',
                     'User-Agent': 'CSVisual/1.0 (+https://github.com/csvisual)'},
            method='POST')
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8'))

    try:
        return _once()
    except urllib.error.HTTPError as e:
        if e.code == 429:
            time.sleep(0.9)
            return _once()
        raise


def _run_wandbox(lang, code, stdin, run_timeout):
    body = {
        'code': _java_class_rename(code, 'prog') if lang == 'java' else code,
        'compiler': WANDBOX_COMPILER[lang],
        'stdin': str(stdin or ''),
        'save': False,
    }
    status, data = _post_json(_WANDBOX_API, body, 50)
    if status != 200:
        return {'ok': False, 'reason': 'Wandbox 返回 HTTP %s' % status}
    compile_err = str(data.get('compiler_error') or '')
    if compile_err.strip() and not str(data.get('program_output') or '') \
            and not str(data.get('program_error') or ''):
        return {'ok': False, 'compileError': True, 'stderr': compile_err}
    return {
        'ok': True,
        'stdout': str(data.get('program_output') or ''),
        'stderr': str(data.get('program_error') or ''),
        # status 是进程退出码（字符串）；编译失败分支上面已经拦住了
        'exitCode': 0 if str(data.get('status')) == '0' else 1,
    }


# ==================== 自建 Piston（可选） ====================

_PISTON_LANG = {'c': 'c', 'cpp': 'c++', 'java': 'java',
                'python': 'python', 'javascript': 'javascript'}
_PISTON_FILE = {'c': 'main.c', 'cpp': 'main.cpp', 'java': 'Main.java',
                'python': 'main.py', 'javascript': 'main.js'}


def _run_piston(lang, code, stdin, run_timeout):
    body = {
        'language': _PISTON_LANG[lang],
        'version': '*',
        'files': [{'name': _PISTON_FILE[lang],
                   'content': _java_class_rename(code, 'Main') if lang == 'java' else code}],
        'stdin': str(stdin or ''),
        'compile_timeout': 15000,
        'run_timeout': run_timeout,
    }
    status, data = _post_json(
        os.getenv('PISTON_URL').rstrip('/') + '/api/v2/execute', body, 50)
    if status != 200:
        return {'ok': False, 'reason': 'Piston 返回 HTTP %s' % status}
    compile_res = data.get('compile')
    if compile_res and compile_res.get('code') not in (None, 0):
        return {'ok': False, 'compileError': True,
                'stderr': str(compile_res.get('stderr') or '编译失败')}
    run_res = data.get('run') or {}
    return {
        'ok': True,
        'stdout': str(run_res.get('stdout') or ''),
        'stderr': str(run_res.get('stderr') or ''),
        'exitCode': 0 if run_res.get('code') in (None, 0) else 1,
    }


# ==================== 对外入口 ====================

def remote_run(lang, code, stdin='', run_timeout=5000):
    """在云端沙箱执行一段代码，返回值约定见模块 docstring"""
    if lang not in WANDBOX_COMPILER:
        return {'ok': False, 'reason': '云端沙箱不支持该语言：' + str(lang)}
    if os.getenv('REMOTE_RUN') == '0':
        return {'ok': False, 'reason': '云端运行已由管理员关闭（REMOTE_RUN=0）'}

    chain = []
    if os.getenv('PISTON_URL'):
        chain.append(('自建 Piston', _run_piston))
    chain.append(('Wandbox', _run_wandbox))

    errors = []
    for name, fn in chain:
        try:
            r = fn(lang, code, stdin, run_timeout)
            if r['ok'] or r.get('compileError'):
                return r        # 编译错误是代码问题，无需换服务商重试
            errors.append(name + '：' + r.get('reason', ''))
        except Exception as e:
            errors.append(name + '：' + str(e))
    return {'ok': False, 'reason': '；'.join(errors)}


def is_env_error(err_text):
    """判断一次本地执行的报错是否属于「环境问题」（值得云端兜底）。
    真正的编译错误/运行时报错是代码问题，云端跑结果也一样，不兜底。"""
    text = str(err_text or '')
    return any(k in text for k in
               ('无法启动运行环境', '无法启动编译器', '可执行文件无法启动', '本机未检测到'))
