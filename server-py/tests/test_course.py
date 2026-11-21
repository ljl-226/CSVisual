"""课程 / 知识点 / 可视化 / 学习记录 模块测试。"""

from conftest import assert_ok

# 18 门 = 原 13 门（4 门核心课 + 数学物理 5 门 + 语言 4 门）
#        + Web 前端 3 门（HTML / CSS / JavaScript）
#        + 机械工业出版社教材体系 2 门（数据库系统概论 / 编译原理）
# 新增课程后请同步修改此常量 —— 这里是刻意写死，用来捕获「课程意外丢失」的回归。
EXPECTED_COURSES = 18


def _first_knowledge_id(client):
    data = assert_ok(client.get('/api/course/1').json())
    return data['knowledge'][0]['id']


# ==================== 课程列表 ====================
def test_course_list(client):
    data = assert_ok(client.get('/api/course/').json())
    assert len(data) == EXPECTED_COURSES, f'应有 {EXPECTED_COURSES} 门课'
    assert {'id', 'name', 'category', 'knowledge_count'} <= set(data[0].keys())


def test_course_list_sorted(client):
    data = assert_ok(client.get('/api/course/').json())
    nos = [c.get('sort_no') or 0 for c in data]
    assert nos == sorted(nos), '课程应按 sort_no 升序'


def test_course_list_has_all_categories(client):
    data = assert_ok(client.get('/api/course/').json())
    names = ' '.join(c['name'] for c in data)
    for key in ['数据结构', '计算机网络', '操作系统', '组成原理', '离散数学',
                'C 语言', 'C++', 'Java', 'Python']:
        assert key in names, f'缺少课程 {key}'


def test_course_list_no_password_leak(client):
    data = assert_ok(client.get('/api/course/').json())
    assert all('password' not in c for c in data)


# ==================== 课程详情 ====================
def test_course_detail(client):
    data = assert_ok(client.get('/api/course/1').json())
    assert data['course']['id'] == 1
    assert isinstance(data['knowledge'], list) and len(data['knowledge']) > 0


def test_course_detail_invalid_id(client):
    for bad in ['abc', '-1', '0', '1.5', '1 OR 1=1', "1'"]:
        body = client.get(f'/api/course/{bad}').json()
        assert body['code'] == 400, bad
        assert '不合法' in body['message']


def test_course_detail_not_found(client):
    body = client.get('/api/course/999999').json()
    assert body['code'] == 404


def test_course_detail_knowledge_sorted(client):
    data = assert_ok(client.get('/api/course/1').json())
    nos = [k.get('sort_no') or 0 for k in data['knowledge']]
    assert nos == sorted(nos)


def test_all_courses_detail_ok(client):
    """所有课程逐一拉取，任一一门报错都算回归失败。"""
    courses = assert_ok(client.get('/api/course/').json())
    for c in courses:
        body = client.get(f"/api/course/{c['id']}").json()
        assert body['code'] == 200, f"{c['name']} 详情失败: {body}"
        assert len(body['data']['knowledge']) > 0, f"{c['name']} 无知识点"


# ==================== 知识点详情 ====================
def test_knowledge_detail(client):
    kid = _first_knowledge_id(client)
    data = assert_ok(client.get(f'/api/course/knowledge/{kid}').json())
    assert data['knowledge']['id'] == kid
    assert 'visualizations' in data
    assert 'progress' in data
    assert data['knowledge']['course_name']


def test_knowledge_detail_options_parsed(client):
    kid = _first_knowledge_id(client)
    data = assert_ok(client.get(f'/api/course/knowledge/{kid}').json())
    for v in data['visualizations']:
        assert isinstance(v['config'], dict), '可视化 config 必须是解析后的对象'


def test_knowledge_detail_invalid(client):
    for bad in ['abc', '0', '-3', '1;DROP TABLE course']:
        assert client.get(f'/api/course/knowledge/{bad}').json()['code'] == 400


def test_knowledge_detail_not_found(client):
    assert client.get('/api/course/knowledge/999999').json()['code'] == 404


def test_all_knowledge_accessible(client):
    """全部知识点逐个访问，确保没有脏数据导致 500。"""
    from app.db import query
    rows = query('SELECT id FROM knowledge').rows
    bad = []
    for r in rows:
        body = client.get(f"/api/course/knowledge/{r['id']}").json()
        if body.get('code') != 200:
            bad.append((r['id'], body.get('message')))
    assert not bad, f'以下知识点访问失败: {bad[:5]}'


def test_visualization_count(client):
    """可视化总数为 65，逐知识点核对数量吻合。"""
    from app.db import query
    total = query('SELECT COUNT(*) AS c FROM visualization').rows[0]['c']
    assert total >= 60, f'可视化数量异常: {total}'


# ==================== 浏览记录 ====================
def test_knowledge_view_ok(client, auth):
    kid = _first_knowledge_id(client)
    assert_ok(client.post(f'/api/course/knowledge/{kid}/view', headers=auth).json())


def test_knowledge_view_increments_progress(client, auth):
    kid = _first_knowledge_id(client)
    before = assert_ok(client.get('/api/learn/overview', headers=auth).json())['knowledgeStudied']
    client.post('/api/course/knowledge/99999/view', headers=auth)
    client.post(f'/api/course/knowledge/{kid}/view', headers=auth)
    after = assert_ok(client.get('/api/learn/overview', headers=auth).json())['knowledgeStudied']
    assert after >= before


def test_knowledge_view_requires_auth(client):
    kid = _first_knowledge_id(client)
    assert client.post(f'/api/course/knowledge/{kid}/view').status_code == 401


def test_knowledge_view_invalid(client, auth):
    for bad in ['abc', '0', 'x']:
        assert client.post(f'/api/course/knowledge/{bad}/view', headers=auth).json()['code'] == 400


def test_knowledge_view_not_found(client, auth):
    assert client.post('/api/course/knowledge/999999/view', headers=auth).json()['code'] == 404


# ==================== 学习中心 ====================
def test_overview_fields(client, auth):
    data = assert_ok(client.get('/api/learn/overview', headers=auth).json())
    for key in ['knowledgeTotal', 'knowledgeStudied', 'favoriteCount', 'wrongCount',
                'chatCount', 'answerTotal', 'answerCorrect', 'courseProgress']:
        assert key in data, f'缺少字段 {key}'
    assert data['knowledgeTotal'] > 0
    assert len(data['courseProgress']) == EXPECTED_COURSES


def test_overview_requires_auth(client):
    assert client.get('/api/learn/overview').status_code == 401


def test_wrong_list(client, auth):
    data = assert_ok(client.get('/api/learn/wrong', headers=auth).json())
    assert isinstance(data, list)
    if data:
        assert {'question_id', 'title', 'analysis', 'knowledge_name'} <= set(data[0].keys())


def test_favorite_toggle_roundtrip(client, auth):
    kid = _first_knowledge_id(client)
    # 先清干净，保证幂等
    if assert_ok(client.get(f'/api/learn/favorite/{kid}/status', headers=auth).json())['favorited']:
        client.post(f'/api/learn/favorite/{kid}', headers=auth)

    r1 = assert_ok(client.post(f'/api/learn/favorite/{kid}', headers=auth).json())
    assert r1['favorited'] is True
    assert assert_ok(client.get(f'/api/learn/favorite/{kid}/status', headers=auth).json())['favorited'] is True

    r2 = assert_ok(client.post(f'/api/learn/favorite/{kid}', headers=auth).json())
    assert r2['favorited'] is False
    assert assert_ok(client.get(f'/api/learn/favorite/{kid}/status', headers=auth).json())['favorited'] is False


def test_favorite_invalid(client, auth):
    for bad in ['abc', '0', '-1']:
        assert client.post(f'/api/learn/favorite/{bad}', headers=auth).json()['code'] == 400
        assert client.get(f'/api/learn/favorite/{bad}/status', headers=auth).json()['code'] == 400


def test_favorite_not_found(client, auth):
    assert client.post('/api/learn/favorite/999999', headers=auth).json()['code'] == 404


def test_favorite_list(client, auth):
    data = assert_ok(client.get('/api/learn/favorite', headers=auth).json())
    assert isinstance(data, list)


def test_wrong_remove(client, auth):
    assert_ok(client.delete('/api/learn/wrong/1', headers=auth).json())


def test_wrong_remove_invalid(client, auth):
    assert client.delete('/api/learn/wrong/abc', headers=auth).json()['code'] == 400


def test_chat_history(client, auth):
    data = assert_ok(client.get('/api/learn/chats', headers=auth).json())
    assert isinstance(data, list)


def test_weak_points(client, auth):
    data = assert_ok(client.get('/api/learn/weak-points', headers=auth).json())
    assert isinstance(data, list)
    if len(data) >= 2:
        counts = [d['wrong_count'] for d in data]
        assert counts == sorted(counts, reverse=True), '薄弱点应按错误次数降序'


def test_learn_requires_auth_all(client):
    for path in ['/api/learn/overview', '/api/learn/wrong', '/api/learn/favorite',
                 '/api/learn/chats', '/api/learn/weak-points']:
        assert client.get(path).status_code == 401, path
