"""Agent 可观测：调用轨迹落盘 + 效果评估统计。

为什么单独落一份 agent-*.log：
  安全日志只记"进出"，业务日志混在 stdout 里没法统计。
  Agent 的效果评估需要「每次提问用了哪些工具、耗时多少、最终走了大模型还是降级」，
  这些字段结构化之后才能回答"助手到底好不好用"，所以按 JSONL 单独存一份。
"""

import datetime
import json
import re
from collections import defaultdict

from app.core.audit import LOG_DIR

NAME_RE = re.compile(r'^agent-\d{4}-\d{2}-\d{2}\.log$')


def _today_file():
    return LOG_DIR / ('agent-%s.log' % datetime.datetime.now().strftime('%Y-%m-%d'))


def write(rec: dict):
    """写一条轨迹。日志失败绝不能影响正常对话。"""
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        rec = dict(rec or {})
        rec.setdefault('ts', datetime.datetime.now().isoformat(timespec='seconds'))
        with open(_today_file(), 'a', encoding='utf-8') as f:
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')
    except Exception:
        pass


def log_turn(user_id, session_id, question, intent, mode, elapsed_ms,
             tool_calls=None, chars=0, plan_count=0, blocked=False, issues=None):
    write({
        'type': 'turn',
        'userId': user_id,
        'sessionId': session_id,
        'question': str(question or '')[:120],
        'intent': intent,
        'mode': mode,
        'elapsedMs': int(elapsed_ms or 0),
        'chars': int(chars or 0),
        'planCount': int(plan_count or 0),
        'blocked': bool(blocked),
        'issues': issues or [],
        'tools': [{
            'name': t.get('name'),
            'ok': bool(t.get('ok')),
            'ms': int(t.get('ms') or 0),
        } for t in (tool_calls or [])],
    })


def log_tool(user_id, name, ok, ms, summary=''):
    write({'type': 'tool', 'userId': user_id, 'name': name, 'ok': bool(ok), 'ms': int(ms or 0),
           'summary': str(summary or '')[:120]})


def _files(days: int = 7):
    if not LOG_DIR.is_dir():
        return []
    out = []
    for p in sorted(LOG_DIR.glob('agent-*.log'), reverse=True):
        # 文件名白名单：与 glob 结果交叉验证，避免把别的文件当日志读进来
        if NAME_RE.match(p.name):
            out.append(p)
        if len(out) >= max(1, days):
            break
    return out


def _read(days: int = 7, limit: int = 5000):
    rows = []
    for p in _files(days):
        try:
            with open(p, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rows.append(json.loads(line))
                    except Exception:
                        continue  # 坏行跳过，不让它毁掉整份统计
        except Exception:
            continue
    return rows[-limit:]


def recent(limit: int = 50, days: int = 3):
    rows = [r for r in _read(days) if r.get('type') == 'turn']
    rows.sort(key=lambda x: str(x.get('ts') or ''), reverse=True)
    return rows[:limit]


def stats(days: int = 7, rows: list = None) -> dict:
    # rows 可外部传入：管理员看全站统计，学生只看自己的那几条，
    # 统计逻辑共用一份，避免出现"两处算法、两个数字"。
    if rows is None:
        rows = [r for r in _read(days) if r.get('type') == 'turn']
    if not rows:
        return {
            'days': days, 'turns': 0, 'avgElapsedMs': 0, 'toolRuns': 0, 'toolSuccessRate': None,
            'fallbackRate': 0, 'blocked': 0, 'byIntent': [], 'byMode': [], 'byTool': [],
            'recent': [], 'updatedAt': datetime.datetime.now().isoformat(timespec='seconds'),
        }

    total = len(rows)
    elapsed = [int(r.get('elapsedMs') or 0) for r in rows]
    by_intent = defaultdict(int)
    by_mode = defaultdict(int)
    tool_stat = {}
    tool_runs = 0
    tool_ok = 0

    for r in rows:
        by_intent[str(r.get('intent') or 'unknown')] += 1
        by_mode[str(r.get('mode') or 'unknown')] += 1
        for t in (r.get('tools') or []):
            name = str(t.get('name') or 'unknown')
            st = tool_stat.setdefault(name, {'name': name, 'runs': 0, 'ok': 0, 'ms': 0})
            st['runs'] += 1
            st['ms'] += int(t.get('ms') or 0)
            tool_runs += 1
            if t.get('ok'):
                st['ok'] += 1
                tool_ok += 1

    def top(d, n=8):
        return sorted([{'name': k, 'count': v} for k, v in d.items()],
                      key=lambda x: x['count'], reverse=True)[:n]

    return {
        'days': days,
        'turns': total,
        'avgElapsedMs': int(sum(elapsed) / total),
        'maxElapsedMs': max(elapsed),
        'toolRuns': tool_runs,
        'toolSuccessRate': round(tool_ok / tool_runs * 100, 1) if tool_runs else None,
        'fallbackRate': round(by_mode.get('fallback', 0) / total * 100, 1),
        'blocked': sum(1 for r in rows if r.get('blocked')),
        'avgChars': int(sum(int(r.get('chars') or 0) for r in rows) / total),
        'byIntent': top(by_intent),
        'byMode': top(by_mode),
        'byTool': sorted([{
            'name': v['name'],
            'runs': v['runs'],
            'ok': v['ok'],
            'successRate': round(v['ok'] / v['runs'] * 100, 1),
            'avgMs': int(v['ms'] / v['runs']),
        } for v in tool_stat.values()], key=lambda x: x['runs'], reverse=True),
        'recent': recent(20, days),
        'updatedAt': datetime.datetime.now().isoformat(timespec='seconds'),
    }
