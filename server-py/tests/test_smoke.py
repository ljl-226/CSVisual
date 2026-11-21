"""冒烟测试：确认 Python 版后端的核心链路与原 Node 版行为一致。"""

from conftest import assert_fail, assert_ok


def test_health(client):
    body = client.get('/api/health').json()
    assert body['code'] == 200
    assert body['data']['db'] == 'connected'
    assert body['data']['runtime'] == 'python-fastapi'


def test_login_ok(client):
    body = client.post('/api/auth/login', json={'username': 'student', 'password': '123456'}).json()
    assert body['code'] == 200
    assert body['data']['token']
    assert body['data']['user']['username'] == 'student'


def test_login_wrong_password(client):
    r = client.post('/api/auth/login', json={'username': 'student', 'password': 'bad-password'})
    assert_fail(r.json(), 400)


def test_me(client, auth):
    data = assert_ok(client.get('/api/auth/me', headers=auth).json())
    assert data['username'] == 'student'


def test_me_without_token(client):
    r = client.get('/api/auth/me')
    assert r.status_code == 401
    assert r.json()['code'] == 401


def test_course_list(client):
    data = assert_ok(client.get('/api/course').json())
    assert len(data) >= 13  # 四大专业 + 数理 + 四门编程语言
    assert 'knowledge_count' in data[0]


def test_course_detail(client):
    first = assert_ok(client.get('/api/course').json())[0]
    data = assert_ok(client.get(f"/api/course/{first['id']}").json())
    assert data['course']['id'] == first['id']
    assert isinstance(data['knowledge'], list)


def test_course_detail_invalid(client):
    for bad in ['abc', '-1', '0', '1.5', '999999999999']:
        assert_fail(client.get(f'/api/course/{bad}').json(), 400)


def test_knowledge_detail_and_view(client, auth):
    from app.db import query_one

    k = query_one('SELECT id FROM knowledge ORDER BY id LIMIT 1')
    data = assert_ok(client.get(f"/api/course/knowledge/{k['id']}").json())
    assert data['knowledge']['id'] == k['id']
    assert isinstance(data['visualizations'], list)
    assert_ok(client.post(f"/api/course/knowledge/{k['id']}/view", headers=auth).json())


def test_question_by_knowledge(client):
    from app.db import query_one

    row = query_one('SELECT knowledge_id, COUNT(*) c FROM question GROUP BY knowledge_id ORDER BY c DESC LIMIT 1')
    data = assert_ok(client.get(f"/api/question/by-knowledge/{row['knowledge_id']}").json())
    assert len(data) > 0
    assert isinstance(data[0]['options'], list)
    assert data[0]['source']
    assert 1 <= data[0]['difficulty'] <= 5


def test_random_paper(client):
    data = assert_ok(client.get('/api/question/paper/random?limit=5').json())
    assert len(data) == 5


def test_random_paper_limit_clamped(client):
    data = assert_ok(client.get('/api/question/paper/random?limit=9999').json())
    assert len(data) == 100  # 上限收敛


def test_submit_and_wrong_book(client, auth):
    from app.db import query_one

    q = query_one("SELECT * FROM question WHERE type = 'single' ORDER BY id LIMIT 1")
    wrong = 'B' if str(q['answer']).upper() != 'B' else 'A'
    data = assert_ok(client.post('/api/question/submit', headers=auth,
                                 json={'questionId': q['id'], 'answer': wrong}).json())
    assert data['correct'] is False
    wrongs = assert_ok(client.get('/api/learn/wrong', headers=auth).json())
    assert any(int(w['question_id']) == int(q['id']) for w in wrongs)

    right_data = assert_ok(client.post('/api/question/submit', headers=auth,
                                       json={'questionId': q['id'], 'answer': q['answer']}).json())
    assert right_data['correct'] is True
    wrongs = assert_ok(client.get('/api/learn/wrong', headers=auth).json())
    assert not any(int(w['question_id']) == int(q['id']) for w in wrongs)


def test_submit_judge_alias(client, auth):
    """判断题 A/B 与 T/F 跨写法互认"""
    from app.db import query_one

    q = query_one("SELECT * FROM question WHERE type = 'judge' ORDER BY id LIMIT 1")
    if not q:
        return
    target = q['answer']
    alias = {'A': 'T', 'B': 'F'}.get(str(target).upper())
    data = assert_ok(client.post('/api/question/submit', headers=auth,
                                 json={'questionId': q['id'], 'answer': alias}).json())
    assert data['correct'] is True


def test_submit_paper(client, auth):
    from app.db import query

    rows = query("SELECT id, answer FROM question WHERE type = 'single' ORDER BY id LIMIT 3").rows
    payload = [{'questionId': r['id'], 'answer': r['answer']} for r in rows]
    data = assert_ok(client.post('/api/question/submit-paper', headers=auth, json={'answers': payload}).json())
    assert data['total'] == 3
    assert data['correctCount'] == 3
    assert data['score'] == 100


def test_overview_and_favorite(client, auth):
    data = assert_ok(client.get('/api/learn/overview', headers=auth).json())
    for key in ['knowledgeTotal', 'knowledgeStudied', 'favoriteCount', 'wrongCount',
                'answerTotal', 'courseProgress']:
        assert key in data

    from app.db import query_one

    k = query_one('SELECT id FROM knowledge ORDER BY id LIMIT 1')
    body = client.post(f"/api/learn/favorite/{k['id']}", headers=auth).json()
    assert_ok(body)
    status = assert_ok(client.get(f"/api/learn/favorite/{k['id']}/status", headers=auth).json())
    assert status['favorited'] is True
    body = client.post(f"/api/learn/favorite/{k['id']}", headers=auth).json()
    assert body['data']['favorited'] is False
