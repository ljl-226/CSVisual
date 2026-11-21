#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""大模型配置自检。

填完 API Key 之后跑一下，确认到底通没通 —— 因为「配了却没生效」是最难排查的：
后端不会报错，只会静默降级到本地知识库，界面上看起来只是「回答有点模板化」。

    python tools/llm_check.py

只用标准库（urllib），不依赖 httpx，在哪套 Python 下都能跑。
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(errors='replace')
    except Exception:
        pass

ROOT = Path(__file__).resolve().parents[1]


def load_env():
    """和 app/core/config.py 保持一致的查找位置：server-py/.env"""
    for p in (ROOT / 'server-py' / '.env',):
        if not p.exists():
            continue
        for line in p.read_text(encoding='utf-8', errors='replace').splitlines():
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            os.environ.setdefault(k.strip(), v.strip())
        return p
    return None


def mask(key):
    if not key:
        return '(空)'
    return key[:6] + '*' * max(0, len(key) - 10) + key[-4:] if len(key) > 10 else '*' * len(key)


def main():
    print('=' * 58)
    print('  CSVisual 大模型配置自检')
    print('=' * 58)

    src = load_env()
    if src:
        print('  配置文件: %s' % src)
    else:
        print('  [错误] 没找到 server-py/.env，先复制一份 server-py/.env.example')
        return 1

    key = os.environ.get('LLM_API_KEY', '')
    base = (os.environ.get('LLM_BASE_URL') or 'https://api.deepseek.com/v1').rstrip('/')
    model = os.environ.get('LLM_MODEL') or 'deepseek-flash'
    thinking = os.environ.get('LLM_THINKING') == '1'

    print('  API Key : %s' % mask(key))
    print('  接口地址: %s' % base)
    print('  模型    : %s' % model)
    print('  思考模式: %s' % ('开启（超时 120s）' if thinking else '关闭（超时 30s）'))
    print('')

    if not key:
        print('  [未配置] LLM_API_KEY 是空的。')
        print('  → 去 https://platform.deepseek.com/api_keys 申请后填进 server-py/.env')
        print('  → 留空也属于正常用法：Agent 会用本地知识库回答，无外网也能演示。')
        return 0

    payload = {
        'model': model,
        'messages': [
            {'role': 'system', 'content': '你是一个简洁的助手。'},
            {'role': 'user', 'content': '用一句话说明什么是 TCP 三次握手。'}
        ],
        'temperature': 0.6,
        'stream': False,
        'thinking': {'type': 'enabled' if thinking else 'disabled'},
    }
    req = urllib.request.Request(
        base + '/chat/completions',
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + key},
        method='POST',
    )

    print('  正在发一次真实测试请求...')
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=120.0 if thinking else 30.0) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', 'replace')[:400]
        cost = time.time() - t0
        print('')
        print('  [失败] HTTP %d（耗时 %.1fs）' % (e.code, cost))
        print('  响应: %s' % body)
        print('')
        hint = {
            401: 'API Key 无效或已过期 —— 回 platform.deepseek.com 检查 Key 是否正确复制完整。',
            402: '余额不足 —— DeepSeek 账户需要充值或有可用的赠送额度。',
            404: '接口或模型名不存在 —— 检查 LLM_BASE_URL 是否正确、LLM_MODEL 拼写是否有误。',
            422: '请求参数不被接受 —— 检查 LLM_MODEL 是否是当前可用的模型名。',
            429: '触发限流 —— 稍等再试，或降低调用频率。',
        }.get(e.code, '看上面的响应体判断原因。')
        print('  可能原因: %s' % hint)
        return 1
    except urllib.error.URLError as e:
        print('')
        print('  [失败] 网络不通（耗时 %.1fs）: %s' % (time.time() - t0, e.reason))
        print('  可能原因: 没有外网 / 需要代理 / 公司网络屏蔽了 api.deepseek.com')
        return 1
    except Exception as e:
        print('')
        print('  [失败] 超时或未知错误（耗时 %.1fs）: %s' % (time.time() - t0, e))
        if thinking:
            print('  提示: 思考模式开着，模型要先输出思维链，容易超时。')
            print('       试试在 server-py/.env 里设 LLM_THINKING=0 再跑一次。')
        return 1

    cost = time.time() - t0
    content = ((data.get('choices') or [{}])[0].get('message') or {}).get('content') or ''
    usage = data.get('usage') or {}

    print('')
    print('  [成功] HTTP 200（耗时 %.1fs）' % cost)
    print('  模型实际返回: %s' % (data.get('model') or model))
    if usage:
        print('  Token 用量: 输入 %s / 输出 %s' % (usage.get('prompt_tokens'), usage.get('completion_tokens')))
    print('  回答: %s' % (content[:200].replace('\n', ' ') or '(空)'))
    print('')
    print('  配置没问题，重启后端即可生效：')
    print('    cd server-py && python run.py')
    print('  启动日志里应看到「大模型: 已配置(%s)」' % model)
    return 0


if __name__ == '__main__':
    sys.exit(main())
