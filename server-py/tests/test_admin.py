"""管理端接口测试：权限隔离、五题型题库、算法题与用例 CRUD、统计。"""

from conftest import assert_fail, assert_ok

from app.db import query
from app.utils.validate import normalize_judge_answer

# ============ 权限隔离 ============
def test_admin_requires_admin_role(client, auth):
    r = client.get('/api/admin/stats', headers=auth)
    assert r.status_code == 403
    assert r.json()['code'] == 403


def test_admin_requires_login(client):
    r = client.get('/api/admin/stats')
    assert r.status_code == 401


def test_admin_stats(client, admin_auth):
    data = assert_ok(client.get('/api/admin/stats', headers=admin_auth).json())
    for key in ['userCount', 'knowledgeCount', 'questionCount', 'answerTotal', 'chatCount', 'byCourse']:
        assert key in data
    # 与库里真实条数对齐，而不是写死数字：种子数据会随版本增长
    assert data['knowledgeCount'] == query('SELECT COUNT(*) AS c FROM knowledge').rows[0]['c']
    assert data['questionCount'] == query('SELECT COUNT(*) AS c FROM question').rows[0]['c']
    assert data['knowledgeCount'] >= 80
    assert data['questionCount'] >= 400


def test_admin_stats_course_breakdown(client, admin_auth):
    """按课程统计的题目数之和，应等于题目总数（不能有孤儿题漏在外面）。"""
    data = assert_ok(client.get('/api/admin/stats', headers=admin_auth).json())
    total = sum(int(x.get('count') or x.get('question_count') or 0) for x in data['byCourse'])
    assert total == data['questionCount'], f'分课程统计 {total} != 总数 {data["questionCount"]}'


def test_admin_users(client, admin_auth):
    data = assert_ok(client.get('/api/admin/users', headers=admin_auth).json())
    assert len(data) >= 2
    assert 'answer_count' in data[0]


# ============ 知识点 CRUD ============
def test_admin_knowledge_crud(client, admin_auth):
    from app.db import query_one

    course = query_one('SELECT id FROM course ORDER BY id LIMIT 1')
    created = assert_ok(client.post('/api/admin/knowledge', headers=admin_auth, json={
        'courseId': course['id'], 'name': '测试知识点PY', 'summary': '用于自动化测试',
        'content': '正文内容', 'route': '/vis/test', 'sortNo': 999,
    }).json())
    kid = created['id']

    lst = assert_ok(client.get('/api/admin/knowledge?keyword=测试知识点PY', headers=admin_auth).json())
    assert any(int(k['id']) == int(kid) for k in lst)

    assert_ok(client.put(f'/api/admin/knowledge/{kid}', headers=admin_auth,
                         json={'summary': '已更新的摘要'}).json())
    assert query_one('SELECT summary FROM knowledge WHERE id = ?', [kid])['summary'] == '已更新的摘要'

    assert_ok(client.delete(f'/api/admin/knowledge/{kid}', headers=admin_auth).json())
    assert query_one('SELECT id FROM knowledge WHERE id = ?', [kid]) is None


def test_admin_knowledge_rejects_missing_course(client, admin_auth):
    assert_fail(client.post('/api/admin/knowledge', headers=admin_auth,
                            json={'courseId': 999999, 'name': 'x'}).json(), 404)


def test_admin_knowledge_invalid_id(client, admin_auth):
    assert_fail(client.put('/api/admin/knowledge/abc', headers=admin_auth, json={'name': 'x'}).json(), 400)


# ============ 可视化 CRUD ============
def test_admin_visualization_crud(client, admin_auth):
    from app.db import query_one

    k = query_one('SELECT id FROM knowledge ORDER BY id LIMIT 1')
    created = assert_ok(client.post('/api/admin/visualization', headers=admin_auth, json={
        'knowledgeId': k['id'], 'title': '测试案例PY', 'description': '自动化', 'config': {'steps': [1, 2]},
    }).json())
    vid = created['id']
    assert_ok(client.put(f'/api/admin/visualization/{vid}', headers=admin_auth,
                         json={'description': '已更新'}).json())
    assert_ok(client.delete(f'/api/admin/visualization/{vid}', headers=admin_auth).json())


# ============ 题库：五种题型 ============
def test_admin_question_create_judge(client, admin_auth):
    """判断题自动归一化为 A/B 并补齐选项，避免出现「判断题没有选项可点」"""
    from app.db import query_one

    k = query_one('SELECT id FROM knowledge ORDER BY id LIMIT 1')
    created = assert_ok(client.post('/api/admin/question', headers=admin_auth, json={
        'knowledgeId': k['id'], 'type': '判断题', 'title': '测试判断题PY', 'answer': '正确',
    }).json())
    row = query_one('SELECT type, answer, options FROM question WHERE id = ?', [created['id']])
    assert row['type'] == 'judge'
    assert row['answer'] == 'A'
    assert '正确' in str(row['options'])
    assert_ok(client.delete(f"/api/admin/question/{created['id']}", headers=admin_auth).json())


def test_admin_question_create_subjective_needs_reference(client, admin_auth):
    from app.db import query_one

    k = query_one('SELECT id FROM knowledge ORDER BY id LIMIT 1')
    assert_fail(client.post('/api/admin/question', headers=admin_auth, json={
        'knowledgeId': k['id'], 'type': 'case', 'title': '缺少参考答案的案例题',
    }).json(), 400)


def test_admin_question_subjective_accepts_points(client, admin_auth):
    from app.db import query_one

    k = query_one('SELECT id FROM knowledge ORDER BY id LIMIT 1')
    created = assert_ok(client.post('/api/admin/question', headers=admin_auth, json={
        'knowledgeId': k['id'], 'type': 'programming', 'title': '测试编程题PY',
        'gradingPoints': [{'point': '使用双指针', 'score': 5}, {'point': '复杂度 O(n)', 'score': 5}],
    }).json())
    row = query_one('SELECT type, answer, options, grading_points FROM question WHERE id = ?', [created['id']])
    assert row['type'] == 'programming'
    assert row['answer'] == ''          # 主观题不设标准答案
    assert row['options'] == '[]'       # 主观题不给选项
    assert '双指针' in str(row['grading_points'])
    assert_ok(client.delete(f"/api/admin/question/{created['id']}", headers=admin_auth).json())


def test_admin_question_rejects_bad_points(client, admin_auth):
    from app.db import query_one

    k = query_one('SELECT id FROM knowledge ORDER BY id LIMIT 1')
    for bad in [[{'point': '没有分值'}], 'not-json', [{'score': 3}]]:
        assert_fail(client.post('/api/admin/question', headers=admin_auth, json={
            'knowledgeId': k['id'], 'type': 'case', 'title': '要点非法的案例题', 'gradingPoints': bad,
        }).json(), 400)


def test_admin_question_rejects_unknown_type(client, admin_auth):
    from app.db import query_one

    k = query_one('SELECT id FROM knowledge ORDER BY id LIMIT 1')
    assert_fail(client.post('/api/admin/question', headers=admin_auth, json={
        'knowledgeId': k['id'], 'type': '填空题', 'title': '未知题型', 'answer': 'A',
    }).json(), 400)


def test_admin_question_update_normalizes_judge(client, admin_auth):
    from app.db import query_one

    row = query_one("SELECT id FROM question WHERE type='judge' ORDER BY id LIMIT 1")
    assert_ok(client.put(f"/api/admin/question/{row['id']}", headers=admin_auth,
                         json={'answer': 'T'}).json())
    updated = query_one('SELECT answer, options FROM question WHERE id = ?', [row['id']])
    assert updated['answer'] == 'A'
    assert '正确' in str(updated['options'])


# ============ 算法题与用例 ============
def test_admin_algorithm_crud(client, admin_auth):
    created = assert_ok(client.post('/api/admin/algorithm', headers=admin_auth, json={
        'title': '测试算法题PY', 'description': '求两数之和', 'difficulty': 3, 'tags': '哈希表',
    }).json())
    aid = created['id']
    assert created['weight'] == 20  # 难度 3 → 默认权值 20

    detail = assert_ok(client.get(f'/api/admin/algorithm/{aid}', headers=admin_auth).json())
    assert detail['cases'] == []

    case = assert_ok(client.post('/api/admin/algorithm-cases', headers=admin_auth, json={
        'algorithmId': aid, 'stdin': '1 2', 'expected': '3', 'isSample': 1, 'sortNo': 0,
    }).json())
    cases = assert_ok(client.get(f'/api/admin/algorithm-cases?algorithmId={aid}', headers=admin_auth).json())
    assert any(int(c['id']) == int(case['id']) for c in cases)

    assert_fail(client.post('/api/admin/algorithm-cases', headers=admin_auth,
                            json={'algorithmId': aid, 'stdin': '', 'expected': '   '}).json(), 400)
    assert_fail(client.post('/api/admin/algorithm-cases', headers=admin_auth,
                            json={'algorithmId': 999999, 'stdin': '1', 'expected': '2'}).json(), 404)

    assert_ok(client.delete(f"/api/admin/algorithm-cases/{case['id']}", headers=admin_auth).json())
    assert_ok(client.delete(f'/api/admin/algorithm/{aid}', headers=admin_auth).json())


def test_admin_algorithm_requires_description(client, admin_auth):
    assert_fail(client.post('/api/admin/algorithm', headers=admin_auth, json={'title': '只有标题'}).json(), 400)


def test_admin_algorithm_case_rejects_invalid_id(client, admin_auth):
    assert_fail(client.get('/api/admin/algorithm-cases?algorithmId=abc', headers=admin_auth).json(), 400)


def test_normalize_judge_answer_aliases():
    for v in ['T', 'TRUE', 'A', '对', '正确', '√', '1']:
        assert normalize_judge_answer(v) == 'A'
    for v in ['F', 'FALSE', 'B', '错', '错误', '×', '0']:
        assert normalize_judge_answer(v) == 'B'
    assert normalize_judge_answer('随便写') is None
