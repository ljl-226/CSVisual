"""安全审计日志。

记录登录成功 / 失败、改密码、找回密码、删除数据这类「出事后要能回溯是谁干的」的动作。
业务日志（知识点浏览、答题）不写这里 —— 量太大，会淹没真正需要关注的事件。

落盘到 server-py/logs/security-YYYY-MM-DD.log，按天切分，
不依赖任何日志框架，避免为一条日志引入配置负担。
"""

import json
import os
import threading
from datetime import datetime
from pathlib import Path

from app.core import config as C

BASE_DIR = Path(__file__).resolve().parents[2]
LOG_DIR = BASE_DIR / 'logs'

_lock = threading.Lock()


def _path() -> Path:
    return LOG_DIR / ('security-%s.log' % datetime.now().strftime('%Y-%m-%d'))


def log(event: str, **fields):
    """写一条审计记录。任何异常都不能影响业务请求，所以整段吞掉异常。"""
    if not C.AUDIT_LOG:
        return
    record = {
        'time': datetime.now().isoformat(timespec='seconds'),
        'event': event,
    }
    record.update({k: v for k, v in fields.items() if v is not None})
    line = json.dumps(record, ensure_ascii=False)
    print('[AUDIT] ' + line)
    try:
        with _lock:
            LOG_DIR.mkdir(parents=True, exist_ok=True)
            with open(_path(), 'a', encoding='utf-8') as f:
                f.write(line + '\n')
    except Exception:
        # 磁盘满 / 权限问题不该让登录接口挂掉
        pass
