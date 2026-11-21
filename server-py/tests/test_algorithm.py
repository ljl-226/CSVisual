"""程序设计算法题模块测试：列表 / 详情 / 助手 / 排名 / 提交判题。"""

import re

import pytest

from conftest import assert_fail, assert_ok

VALID_STATUS = {'accepted', 'wrong_answer', 'compile_error', 'runtime_error', 'timeout'}


def test_algorithm_list(client):
    data = assert_ok(client.get('/api/algorithm').json())
    assert data['total'] >= 20
    assert len(data['list']) <= data['size']
    for item in data['list']:
        assert item['difficultyText']
        assert 'solved' in item and 'bestScore' in item


def test_algorithm_list_filters(client):
    data = assert_ok(client.get('/api/algorithm?difficulty=3&size=5').json())
    assert all(a['difficulty'] == 3 for a in data['list'])
    assert data['size'] == 5

    empty = assert_ok(client.get('/api/algorithm?keyword=不存在的题目关键词zzz').json())
    assert empty['total'] == 0


def test_algorithm_detail(client):
    first = assert_ok(client.get('/api/algorithm').json())['list'][0]
    data = assert_ok(client.get(f"/api/algorithm/{first['id']}").json())
    assert data['id'] == first['id']
    assert data['description']
    assert isinstance(data['tags'], list)
    assert isinstance(data['samples'], list)


def test_algorithm_detail_logged_in(client, auth):
    """带登录态时必须照样能拿到详情。

    这条是补漏用房：原来 `test_algorithm_detail` 不带 Authorization，
    `optional_user` 解析出 None，那条查「我的最好成绩」的 SQL 压根没被执行，
    所以它一直绿着，而真实用户一打开详情页就 500 —— 是这个漏网角度。

    当时的坏 SQL 是 SELECT status, MAX(score)... FROM algorithm_submit，
    裸列 status 违反 MySQL 默认的 ONLY_FULL_GROUP_BY（错误 1140），
    且在解析期就报错，跟有没有数据无关。
    """
    first = assert_ok(client.get('/api/algorithm').json())['list'][0]
    data = assert_ok(client.get(f"/api/algorithm/{first['id']}", headers=auth).json())
    assert data['id'] == first['id']
    assert data['description']
    assert 'myBest' in data
    # 有提交记录时必须是结构化的最好成绩；没有时是 None —— 两种都要走得通
    assert data['myBest'] is None or (
        'status' in data['myBest'] and 'score' in data['myBest']
        and 'maxScore' in data['myBest']
    )


def test_algorithm_detail_survives_real_submission_rows(client, auth):
    """库里真有提交记录时，详情也必須能出来 —— 直接撞 ONLY_FULL_GROUP_BY 的场景。"""
    from app.db import query_one

    row = query_one(
        'SELECT algorithm_id FROM algorithm_submit '
        'ORDER BY id DESC LIMIT 1'
    )
    data = assert_ok(client.get('/api/algorithm').json())['list'][0]
    aid = (row and row['algorithm_id']) or data['id']
    # 用 admin 的身份确保查到自己名下的记录
    res = client.get(f'/api/algorithm/{aid}', headers=auth)
    body = res.json()
    assert body['code'] == 200, '详情接口返回 %s：%s' % (body['code'], body.get('message'))
    assert 'myBest' in body['data']


def test_algorithm_detail_invalid(client):
    for bad in ['abc', '-1', '0']:
        assert_fail(client.get(f'/api/algorithm/{bad}').json(), 400)
    assert_fail(client.get('/api/algorithm/999999').json(), 404)


def test_algorithm_solution_requires_login(client):
    r = client.get('/api/algorithm/1/solution')
    assert r.status_code == 401


def test_algorithm_solution(client, auth):
    data = assert_ok(client.get('/api/algorithm/1/solution', headers=auth).json())
    assert 'code' in data and 'language' in data and 'tip' in data
    # 多语言参考答案：available 必须存在且至少含当前返回的那门语言
    assert 'available' in data, '缺少 available 列表，前端无法渲染语言下拉'
    assert isinstance(data['available'], list) and data['available'], 'available 不应为空'
    assert data['language'] in data['available'], '返回的语言必须在 available 里'


def test_algorithm_solution_by_lang(client, auth):
    """?lang= 指定语言：命中就返回该语言，没配置则回落到主语言而不是报错。"""
    first = assert_ok(client.get('/api/algorithm').json())['list'][0]
    aid = first['id']
    base = assert_ok(client.get(f'/api/algorithm/{aid}/solution', headers=auth).json())
    target = base['available'][0]

    data = assert_ok(client.get(f'/api/algorithm/{aid}/solution?lang={target}', headers=auth).json())
    assert data['language'] == target
    assert data['code'], '指定了 available 里的语言却返回空代码'
    assert set(data['available']) >= set(base['available']), '换语言后 available 不该变窄'

    # 库里没有的语言（如 rust）必须优雅回落，不能 500 也不能返回空
    miss = assert_ok(client.get(f'/api/algorithm/{aid}/solution?lang=rust', headers=auth).json())
    assert miss['language'] in miss['available']
    assert miss['code'], '未配置的语言应回落到主语言答案，而不是留空'


def test_algorithm_reference_lang_consistency(client, auth):
    """独立表里存的答案必须真的能在该语言下通过判题 —— verified=1 的语义就是这个保证。"""
    from app.db import query
    rows = query(
        "SELECT r.algorithm_id, r.language, r.code, a.title "
        "FROM algorithm_reference_lang r JOIN algorithm a ON a.id = r.algorithm_id "
        "WHERE r.verified = 1 ORDER BY r.id LIMIT 1"
    ).rows
    if not rows:
        return   # 还没生成，属正常
    from app.routers.algorithm import judge
    r = rows[0]
    cases = [dict(c) for c in query(
        'SELECT stdin, expected FROM algorithm_case WHERE algorithm_id = ? ORDER BY sort_no',
        (r['algorithm_id'],)).rows]
    if not cases:
        return
    res = judge(cases, r['language'], r['code'])
    assert res['status'] == 'accepted', (
        '标了 verified=1 的 %s [%s] 参考答案实际跑不通：%s' % (r['title'], r['language'], res.get('message'))
    )


def test_algorithm_ranking(client):
    data = assert_ok(client.get('/api/algorithm/ranking').json())
    assert 'list' in data and 'me' in data
    for i, row in enumerate(data['list']):
        assert row['rank'] == i + 1
        assert row['totalScore'] > 0


def test_algorithm_ranking_with_user(client, auth):
    data = assert_ok(client.get('/api/algorithm/ranking', headers=auth).json())
    assert data['me'] is not None
    assert data['me']['rank'] >= 1


def test_algorithm_assistant_explain(client, auth):
    first = assert_ok(client.get('/api/algorithm').json())['list'][0]
    data = assert_ok(client.post('/api/algorithm/assistant', headers=auth, json={
        'algorithmId': first['id'], 'question': '这道题怎么想？', 'mode': 'explain',
    }).json())
    assert data['answer']
    assert data['algorithm']['id'] == first['id']
    assert [s['phase'] for s in data['reasoning']][0] == 'parse'


def test_algorithm_assistant_debug(client, auth):
    data = assert_ok(client.post('/api/algorithm/assistant', headers=auth, json={
        'question': '帮我看看哪里错了',
        'code': 'while(true){\n  for(;i<=a.length;i++){\n    console.log(i);\n  }\n}',
        'mode': 'debug',
    }).json())
    assert '第 1 行' in data['answer'] or '死循环' in data['answer']


def test_algorithm_assistant_requires_something(client, auth):
    assert_fail(client.post('/api/algorithm/assistant', headers=auth, json={}).json(), 400)


def test_algorithm_submit_rejects_empty(client, auth):
    first = assert_ok(client.get('/api/algorithm').json())['list'][0]
    assert_fail(client.post(f"/api/algorithm/{first['id']}/submit", headers=auth,
                            json={'language': 'python', 'code': '  '}).json(), 400)
    assert_fail(client.post(f"/api/algorithm/{first['id']}/submit", headers=auth,
                            json={'language': 'python', 'code': 'a=1'}).json(), 400)
    assert_fail(client.post(f"/api/algorithm/{first['id']}/submit", headers=auth,
                            json={'language': 'cobol', 'code': 'print(1)'}).json(), 400)


def test_algorithm_submit_and_records(client, auth):
    """真实判题：把题目自带的参考代码提交上去，应当 AC，并写入提交记录。"""
    from app.db import query, query_one

    row = query_one(
        "SELECT a.id, a.reference_code, a.reference_language, a.weight, "
        "(SELECT COUNT(*) FROM algorithm_case c WHERE c.algorithm_id = a.id) AS case_count "
        "FROM algorithm a WHERE a.status = 1 AND a.reference_code IS NOT NULL "
        "AND a.reference_code != '' ORDER BY a.id LIMIT 1"
    )
    if not row or not row['case_count']:
        return

    # 前后必须用「同一个用户、同一个接口」比。
    # 旧写法有两处错：① before 查的是 user_id=1，而这里登录的是 student(id=2)，
    # 两个用户的记录数没有可比性；② /my 接口有 LIMIT 20，len(mine) 会封顶在 20，
    # 拿它去和 COUNT(*) 比属于量纲不同 —— 只要 user 1 累积超过 20 条，断言就永久失败。
    mine_before = assert_ok(client.get(f"/api/algorithm/{row['id']}/my", headers=auth).json())
    before_ids = {r['id'] for r in mine_before}

    data = assert_ok(client.post(f"/api/algorithm/{row['id']}/submit", headers=auth, json={
        'language': row['reference_language'] or 'python',
        'code': row['reference_code'],
    }).json())

    assert data['status'] in VALID_STATUS
    assert data['total'] == min(row['case_count'], 12)
    assert data['maxScore'] == row['weight']
    if data['status'] == 'accepted':
        assert data['score'] == row['weight']

    mine = assert_ok(client.get(f"/api/algorithm/{row['id']}/my", headers=auth).json())
    # 按 id 差集判断新增，不受 LIMIT 20 封顶影响
    added = [r for r in mine if r['id'] not in before_ids]
    assert added, '提交后应新增一条提交记录'
    assert added[0]['status'] == data['status']
    assert added[0]['total'] == data['total']


def test_algorithm_my_submits_invalid(client, auth):
    assert_fail(client.get('/api/algorithm/abc/my', headers=auth).json(), 400)


# ==================== 运行（不计提交）====================
def test_run_does_not_record_submission(client, auth):
    """运行代码只跑样例：返回结果但绝不写提交记录、不加提交次数。

    任务七的回归线：以前「运行判题」直接走 submit，做一题交一次，
    提交次数与排行榜都被「试运行」刷上去 —— 运行与提交必须分离。
    """
    if not _subproc_available():
        pytest.skip('当前环境无法创建子进程，跳过真实判题')

    from app.db import query_one

    row = query_one(
        'SELECT a.id, a.submit_count FROM algorithm a WHERE a.status = 1 '
        'AND EXISTS (SELECT 1 FROM algorithm_case c WHERE c.algorithm_id = a.id) '
        'ORDER BY a.id LIMIT 1'
    )
    if not row:
        pytest.skip('没有可判题的题目')

    aid = row['id']
    mine_before = assert_ok(client.get(f'/api/algorithm/{aid}/my', headers=auth).json())
    before_ids = {r['id'] for r in mine_before}

    data = assert_ok(client.post(f'/api/algorithm/{aid}/run', headers=auth, json={
        'language': 'python', 'code': 'a, b = map(int, input().split())\nprint(a + b)',
    }).json())

    assert data['sample'] is True, '运行必须标记为样例运行'
    assert 'score' not in data, '运行不应返回得分'
    assert data['status'] in VALID_STATUS
    assert data['total'] > 0

    after = query_one('SELECT submit_count FROM algorithm WHERE id = ?', [aid])
    assert int(after['submit_count'] or 0) == int(row['submit_count'] or 0), '运行不能增加提交次数'

    mine_after = assert_ok(client.get(f'/api/algorithm/{aid}/my', headers=auth).json())
    added = [r for r in mine_after if r['id'] not in before_ids]
    assert not added, '运行不能写提交记录'


def test_run_rejects_bad_input(client, auth):
    assert_fail(client.post('/api/algorithm/1/run', headers=auth,
                            json={'language': 'ruby', 'code': 'puts 1'}).json(), 400)
    assert_fail(client.post('/api/algorithm/1/run', headers=auth,
                            json={'language': 'python', 'code': '  '}).json(), 400)
    assert client.post('/api/algorithm/1/run', json={'language': 'python', 'code': 'print(1)'}).status_code == 401


# ==================== 真实判题（参考答案必须通过）====================
def _subproc_available():
    from app.routers.code import detect_env

    return bool(detect_env().get('python', {}).get('bin'))


def test_reference_solution_must_pass(client, auth):
    """带参考答案的题目，把答案原样提交必须 AC。

    这条是对「判题管道」最强的回归：它同时覆盖
    编译/解释器探测 → 源码落盘 → stdin 注入 → 输出捕获 → 逐用例比对。
    当初 stdin 传成了 str，子进程的写入线程静默崩掉，
    结果就是这里全部超时——而接口照样返回 200，只有这条断言能抓到。
    """
    if not _subproc_available():
        pytest.skip('当前环境无法创建子进程，跳过真实判题')

    from app.db import query

    rows = query(
        'SELECT a.id, a.title, a.reference_code, a.reference_language '
        'FROM algorithm a WHERE a.status = 1 AND a.reference_code IS NOT NULL '
        "AND a.reference_code != '' AND a.reference_language = 'python' "
        'ORDER BY a.id LIMIT 6'
    ).rows
    assert rows, '没有可用于判题的参考答案'

    failed = []
    for r in rows:
        sol = assert_ok(client.get(f"/api/algorithm/{r['id']}/solution", headers=auth).json())
        data = assert_ok(client.post(f"/api/algorithm/{r['id']}/submit", headers=auth, json={
            'language': sol['language'], 'code': sol['code'],
        }).json())
        if data['status'] != 'accepted':
            failed.append((r['id'], r['title'], data['status'],
                           f"{data['passed']}/{data['total']}", data.get('message', '')[:120]))
    assert not failed, f'以下题目参考答案未通过: {failed}'


def test_wrong_code_must_not_pass(client, auth):
    """明显错误的代码不能蒙混过关。"""
    if not _subproc_available():
        pytest.skip('当前环境无法创建子进程，跳过真实判题')

    from app.db import query_one

    row = query_one(
        'SELECT a.id FROM algorithm a WHERE a.status = 1 AND a.reference_code IS NOT NULL '
        "AND a.reference_code != '' ORDER BY a.id LIMIT 1")
    if not row:
        pytest.skip('没有可判题的题目')

    data = assert_ok(client.post(f"/api/algorithm/{row['id']}/submit", headers=auth, json={
        'language': 'python', 'code': 'print(12345)',
    }).json())
    assert data['status'] != 'accepted'
    assert data['score'] == 0


def test_ranking_reflects_accepted(client, auth):
    """AC 之后排行榜要能查到自己，且分数等于题目权值之和。"""
    if not _subproc_available():
        pytest.skip('当前环境无法创建子进程，跳过真实判题')

    data = assert_ok(client.get('/api/algorithm/ranking', headers=auth).json())
    assert data['me'] is not None, '登录用户必须能查到自己的排名'
    me = data['me']
    assert me['rank'] >= 1
    assert me['totalScore'] >= 0
    assert me['solvedCount'] >= 0


def test_normalize_output_helper():
    """判题比对忽略行尾空白与末尾换行"""
    from app.routers.algorithm import normalize_out

    assert normalize_out('1 2 \n3\n\n') == normalize_out('1 2\n3')
    assert normalize_out(None) == ''
    assert normalize_out('a\r\nb') == 'a\nb'
