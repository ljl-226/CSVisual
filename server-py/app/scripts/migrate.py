"""
数据库增量迁移（幂等，可重复执行）
用于给已有库补上新模块所需的表/字段，不影响已有数据。启动服务时自动执行一次。

从 Node 版 scripts/migrate.js 平移，split_sql 的状态机逻辑保持一致 ——
它是整个数据库初始化的命门，一旦改错会导致种子数据导入失败。
"""

import os
import re
from pathlib import Path

from app.db import connection, query, query_one

# server-py/ （migrate.py → scripts → app → server-py）
_BASE_DIR = Path(__file__).resolve().parents[2]
# 项目已收敛为只有 Python 后端，种子 SQL 统一放在 server-py/sql/
SQL_DIR = _BASE_DIR / 'sql'


def _sql_dir():
    return SQL_DIR


def split_sql(sql: str):
    """按「不在字符串字面量内」的分号切分 SQL。

    execute 一次只支持一条语句，故需拆分后逐条执行。
    注释必须在扫描时处理：若先用正则剥离，正文里的 |---|---| 会被误判为注释而截断字符串。
    """
    out = []
    buf = []
    quote = None
    i = 0
    n = len(sql)
    while i < n:
        c = sql[i]
        if quote:
            buf.append(c)
            if c == '\\':
                if i + 1 < n:
                    buf.append(sql[i + 1])
                    i += 1
            elif c == quote:
                # SQL 中两个连续引号表示一个字面量引号，需整体跳过，否则状态机会错位
                if sql[i + 1:i + 2] == quote:
                    buf.append(quote)
                    i += 1
                else:
                    quote = None
            i += 1
            continue

        if c == '-' and sql[i + 1:i + 2] == '-' and (sql[i + 2:i + 3] in (' ', '\n', '') ):
            while i < n and sql[i] != '\n':
                i += 1
            buf.append('\n')
            continue

        if c in ("'", '"', '`'):
            quote = c
            buf.append(c)
            i += 1
            continue

        if c == ';':
            out.append(''.join(buf))
            buf = []
            i += 1
            continue

        buf.append(c)
        i += 1

    tail = ''.join(buf).strip()
    if tail:
        out.append(tail)
    return [s.strip() for s in out if len(s.strip()) > 0]


def seed_module(file_name, guard_sql, guard_min, done_text):
    """导入模块种子数据。仅在 guard 不满足时执行，保证幂等、不清空已有数据。"""
    full = os.path.join(_sql_dir(), file_name)
    if not os.path.exists(full):
        return None
    row = query_one(guard_sql)
    if row and int(row['c'] or 0) >= guard_min:
        return None

    with open(full, 'r', encoding='utf-8') as f:
        raw = f.read()
    raw = re.sub(r'CREATE\s+DATABASE[^;]*;', '', raw, flags=re.I)
    raw = re.sub(r'^\s*USE\s+[`\w]+;', '', raw, flags=re.I | re.M)
    statements = split_sql(raw)

    # 全程单连接 + 事务，原因有二：
    #  1) 依赖会话变量（SET @aid = LAST_INSERT_ID() 再用 @aid 关联子表）的脚本，
    #     连接池每次取到的连接可能不同，会话变量会丢失；
    #  2) 中途失败必须整体回滚，否则留下的「部分导入」会让 guard 被满足，
    #     后续迁移永远跳过，缺失内容再也不会被补上。
    conn = connection()
    try:
        conn.begin()
        with conn.cursor() as cur:
            for stmt in statements:
                cur.execute(stmt)
        conn.commit()
        return done_text
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        raise
    finally:
        conn.close()


def has_column(table, column):
    row = query_one(
        'SELECT COUNT(*) AS c FROM information_schema.columns '
        'WHERE table_schema = DATABASE() AND table_name = ? AND column_name = ?',
        [table, column],
    )
    return bool(row and int(row['c'] or 0) > 0)


def has_index(table, index):
    row = query_one(
        'SELECT COUNT(*) AS c FROM information_schema.statistics '
        'WHERE table_schema = DATABASE() AND table_name = ? AND index_name = ?',
        [table, index],
    )
    return bool(row and int(row['c'] or 0) > 0)


def has_table(table):
    row = query_one(
        'SELECT COUNT(*) AS c FROM information_schema.tables '
        'WHERE table_schema = DATABASE() AND table_name = ?',
        [table],
    )
    return bool(row and int(row['c'] or 0) > 0)


def run():
    done = []

    # 1) 多轮会话表
    if not has_table('chat_session'):
        query(
            """CREATE TABLE chat_session (
                 id          INT AUTO_INCREMENT PRIMARY KEY,
                 user_id     INT NOT NULL COMMENT '所属用户',
                 title       VARCHAR(200) DEFAULT '新对话' COMMENT '会话标题',
                 created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
                 updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                 KEY idx_user (user_id)
               ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Agent 多轮会话'"""
        )
        done.append('新建表 chat_session')

    # 2) chat_record 增加 session_id
    if not has_column('chat_record', 'session_id'):
        query('ALTER TABLE chat_record ADD COLUMN session_id INT NULL COMMENT "所属会话" AFTER user_id')
        query('ALTER TABLE chat_record ADD KEY idx_session (session_id)')
        done.append('chat_record 增加 session_id')

    # 3) chat_record 增加意图类型，便于统计与安全审计
    if not has_column('chat_record', 'intent'):
        query('ALTER TABLE chat_record ADD COLUMN intent VARCHAR(32) NULL COMMENT "意图类型" AFTER mode')
        done.append('chat_record 增加 intent')

    # 4) knowledge 增加难度与标签
    if not has_column('knowledge', 'difficulty'):
        query("ALTER TABLE knowledge ADD COLUMN difficulty TINYINT DEFAULT 3 COMMENT '难度 1-5' AFTER sort_no")
        done.append('knowledge 增加 difficulty')
    if not has_column('knowledge', 'tags'):
        query('ALTER TABLE knowledge ADD COLUMN tags VARCHAR(200) DEFAULT "" COMMENT "标签，逗号分隔" AFTER difficulty')
        done.append('knowledge 增加 tags')

    # 5) course 增加分组
    if not has_column('course', 'group_name'):
        query("ALTER TABLE course ADD COLUMN group_name VARCHAR(32) DEFAULT 'core' COMMENT '分组: core 计算机核心 / math 数理基础' AFTER category")
        done.append('course 增加 group_name')

    # 6) user 增加「免管理员找回密码」所需字段
    #    email / 密保问题 / 重置码：找回密码必须能自证身份，
    #    不能像现在这样只能找管理员改库 —— 那等于把账号回收权交给了运维。
    for col, ddl, desc in (
        ('email', 'email VARCHAR(120) DEFAULT "" COMMENT "找回密码用的邮箱"', '邮箱'),
        ('sec_question', 'sec_question VARCHAR(255) DEFAULT "" COMMENT "密保问题"', '密保问题'),
        ('sec_answer_hash', 'sec_answer_hash VARCHAR(255) DEFAULT "" COMMENT "密保答案(bcrypt)"', '密保答案'),
        ('reset_code_hash', 'reset_code_hash VARCHAR(255) DEFAULT "" COMMENT "邮箱验证码(bcrypt)"', '重置码'),
        ('reset_code_expire', 'reset_code_expire DATETIME NULL COMMENT "重置码过期时间"', '重置码过期时间'),
    ):
        if not has_column('user', col):
            query('ALTER TABLE user ADD COLUMN ' + ddl)
            done.append('user 增加 ' + desc)

    # 6) 二期模块：数学物理
    try:
        r = seed_module(
            'seed-math.sql',
            'SELECT COUNT(*) AS c FROM knowledge WHERE id BETWEEN 22 AND 32',
            11,
            '导入数学物理模块（5 门课 / 11 个知识点 / 33 道题）',
        )
        if r:
            done.append(r)
    except Exception as e:
        print('[migrate] 数学物理模块数据导入失败:', e)

    # 7) 核心课补充知识点
    try:
        r = seed_module(
            'seed-plus.sql',
            'SELECT COUNT(*) AS c FROM knowledge WHERE id IN (33, 34)',
            2,
            '导入核心课补充知识点（哈希表 / Cache 映射，共 2 个点 6 道题）',
        )
        if r:
            done.append(r)
    except Exception as e:
        print('[migrate] 核心课补充知识点导入失败:', e)

    # 8) 题库升级：来源与难度
    if not has_column('question', 'source'):
        query("ALTER TABLE question ADD COLUMN source VARCHAR(32) DEFAULT '基础' COMMENT '题目来源: 考研408/软考/NCRE/期末/基础' AFTER knowledge_id")
        done.append('question 增加 source')
    if not has_column('question', 'difficulty'):
        query("ALTER TABLE question ADD COLUMN difficulty TINYINT DEFAULT 3 COMMENT '难度 1-5' AFTER source")
        done.append('question 增加 difficulty')
    if not has_index('question', 'idx_source'):
        try:
            query('ALTER TABLE question ADD KEY idx_source (source)')
        except Exception:
            pass

    # 9) 知识点升级：对照教材补充 31 个知识点
    try:
        r = seed_module(
            'seed-core3.sql',
            'SELECT COUNT(*) AS c FROM knowledge WHERE id BETWEEN 35 AND 65',
            31,
            '导入教材对照新增知识点（31 个知识点 + 31 个可视化 + 93 道题）',
        )
        if r:
            done.append(r)
    except Exception as e:
        print('[migrate] 新增知识点导入失败:', e)

    # 10) 编程语言模块
    try:
        r = seed_module(
            'seed-lang.sql',
            'SELECT COUNT(*) AS c FROM knowledge WHERE id BETWEEN 66 AND 85',
            20,
            '导入编程语言模块（4 门课 / 20 个知识点 + 配套代码实验室）',
        )
        if r:
            done.append(r)
    except Exception as e:
        print('[migrate] 编程语言模块导入失败:', e)

    # 11) 判断题答案规范化
    try:
        row = query_one(
            "SELECT COUNT(*) AS c FROM question WHERE type = 'judge' "
            "AND (answer IN ('T','F','t','f') OR options IS NULL OR options = '' OR options = '[]')"
        )
        if row and int(row['c'] or 0) > 0:
            query(
                "UPDATE question SET "
                "  answer = CASE WHEN UPPER(TRIM(answer)) IN ('T','TRUE','对','正确','√','A') THEN 'A' ELSE 'B' END, "
                "  options = '[{\"key\":\"A\",\"text\":\"正确\"},{\"key\":\"B\",\"text\":\"错误\"}]' "
                "WHERE type = 'judge' AND (UPPER(TRIM(answer)) IN "
                "('T','F','TRUE','FALSE','对','错','正确','错误','√','×','A','B') "
                "OR options IS NULL OR options = '' OR options = '[]')"
            )
            done.append(f'规范化 {int(row["c"])} 道判断题的答案与选项')
    except Exception as e:
        print('[migrate] 判断题规范化失败:', e)

    # 12) 考试真题库
    try:
        r = seed_module(
            'seed-exam.sql',
            "SELECT COUNT(*) AS c FROM question WHERE source IN ('考研408','软考','NCRE')",
            60,
            '导入考试真题库（考研408 / 软考 / NCRE）',
        )
        if r:
            done.append(r)
    except Exception as e:
        print('[migrate] 考试真题库导入失败:', e)

    # 13) 题型扩展
    try:
        col = query_one(
            "SELECT COLUMN_TYPE AS t FROM information_schema.columns "
            "WHERE table_schema = DATABASE() AND table_name = 'question' AND column_name = 'type'"
        )
        if col and 'case' not in str(col['t']):
            query(
                "ALTER TABLE question MODIFY COLUMN type "
                "ENUM('single','judge','multi','case','programming') DEFAULT 'single' "
                "COMMENT '题型: 单选/判断/多选/案例分析/编程'"
            )
            done.append('question 题型扩展为 5 种（新增 case / programming）')
        if not has_column('question', 'reference_answer'):
            query('ALTER TABLE question ADD COLUMN reference_answer TEXT COMMENT "参考答案（案例题/编程题）" AFTER analysis')
            done.append('question 增加 reference_answer')
        if not has_column('question', 'grading_points'):
            query('ALTER TABLE question ADD COLUMN grading_points TEXT COMMENT "评分要点JSON（Agent判分依据）" AFTER reference_answer')
            done.append('question 增加 grading_points')
    except Exception as e:
        print('[migrate] 题型扩展失败:', e)

    # 13b) 主观题作答变长
    try:
        col = query_one(
            "SELECT DATA_TYPE AS t FROM information_schema.columns "
            "WHERE table_schema = DATABASE() AND table_name = 'answer_record' AND column_name = 'user_answer'"
        )
        if col and str(col['t']).lower() != 'text':
            query('ALTER TABLE answer_record MODIFY COLUMN user_answer TEXT COMMENT "用户作答（主观题可能较长）"')
            done.append('answer_record.user_answer 扩展为 TEXT（支持主观题长作答）')
    except Exception as e:
        print('[migrate] user_answer 扩展失败:', e)

    # 14) 程序设计算法题模块
    try:
        if not has_table('algorithm'):
            query(
                """CREATE TABLE algorithm (
                     id                 INT AUTO_INCREMENT PRIMARY KEY,
                     title              VARCHAR(200) NOT NULL COMMENT '题目标题',
                     difficulty         TINYINT DEFAULT 3 COMMENT '难度 1-5',
                     weight             INT DEFAULT 10 COMMENT '权值，用于排名计分',
                     description        TEXT NOT NULL COMMENT '题面(Markdown)',
                     input_desc         TEXT COMMENT '输入格式说明',
                     output_desc        TEXT COMMENT '输出格式说明',
                     sample_input       TEXT COMMENT '样例输入',
                     sample_output      TEXT COMMENT '样例输出',
                     hints              TEXT COMMENT '解题思路提示',
                     reference_code     TEXT COMMENT '参考答案代码',
                     reference_language VARCHAR(16) DEFAULT 'python' COMMENT '参考答案语言',
                     tags               VARCHAR(200) DEFAULT '' COMMENT '标签，逗号分隔',
                     source             VARCHAR(32) DEFAULT '基础' COMMENT '来源: 考研408/软考/NCRE/期末/基础',
                     knowledge_id       INT DEFAULT NULL COMMENT '关联知识点id',
                     submit_count       INT DEFAULT 0 COMMENT '提交次数',
                     accepted_count     INT DEFAULT 0 COMMENT '通过次数',
                     status             TINYINT DEFAULT 1 COMMENT '1启用 0停用',
                     created_at         DATETIME DEFAULT CURRENT_TIMESTAMP,
                     INDEX idx_diff (difficulty),
                     INDEX idx_k (knowledge_id)
                   ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='程序设计算法题'"""
            )
            done.append('新建表 algorithm（算法题）')
        if not has_table('algorithm_case'):
            query(
                """CREATE TABLE algorithm_case (
                     id           INT AUTO_INCREMENT PRIMARY KEY,
                     algorithm_id INT NOT NULL COMMENT '所属题目',
                     stdin        TEXT COMMENT '标准输入',
                     expected     TEXT COMMENT '期望输出',
                     is_sample    TINYINT DEFAULT 0 COMMENT '1=样例(展示给用户) 0=隐藏用例',
                     sort_no      INT DEFAULT 0,
                     INDEX idx_a (algorithm_id)
                   ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='算法题测试用例'"""
            )
            done.append('新建表 algorithm_case（测试用例）')
        if not has_table('algorithm_submit'):
            query(
                """CREATE TABLE algorithm_submit (
                     id           INT AUTO_INCREMENT PRIMARY KEY,
                     user_id      INT NOT NULL,
                     algorithm_id INT NOT NULL,
                     language     VARCHAR(16) DEFAULT 'python' COMMENT '提交语言',
                     code         TEXT NOT NULL COMMENT '提交代码',
                     status       VARCHAR(24) DEFAULT 'pending' COMMENT 'accepted/wrong_answer/compile_error/runtime_error/timeout',
                     passed       INT DEFAULT 0 COMMENT '通过用例数',
                     total        INT DEFAULT 0 COMMENT '用例总数',
                     score        INT DEFAULT 0 COMMENT '本次得分',
                     max_score    INT DEFAULT 0 COMMENT '该题满分(权值)',
                     runtime      INT DEFAULT 0 COMMENT '总耗时ms',
                     message      TEXT COMMENT '判题信息',
                     created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
                     INDEX idx_user (user_id),
                     INDEX idx_a (algorithm_id),
                     INDEX idx_status (status)
                   ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='算法题提交记录'"""
            )
            done.append('新建表 algorithm_submit（提交记录）')
        if not has_table('algorithm_solution'):
            query(
                """CREATE TABLE algorithm_solution (
                     id           INT AUTO_INCREMENT PRIMARY KEY,
                     algorithm_id INT NOT NULL COMMENT '所属题目',
                     user_id      INT NOT NULL COMMENT '作者',
                     title        VARCHAR(200) DEFAULT '' COMMENT '题解标题',
                     content      TEXT NOT NULL COMMENT '题解正文(Markdown，可含代码块)',
                     language     VARCHAR(16) DEFAULT 'python' COMMENT '题解使用的语言',
                     likes        INT DEFAULT 0 COMMENT '点赞数',
                     created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
                     updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
                     INDEX idx_a (algorithm_id),
                     INDEX idx_user (user_id)
                   ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='算法题题解（用户投稿）"""
            )
            done.append('新建表 algorithm_solution（题解）')
        if not has_table('algorithm_solution_like'):
            query(
                """CREATE TABLE algorithm_solution_like (
                     id          INT AUTO_INCREMENT PRIMARY KEY,
                     solution_id INT NOT NULL,
                     user_id     INT NOT NULL,
                     created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
                     UNIQUE KEY uk_sol_user (solution_id, user_id)
                   ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='题解点赞'"""
            )
            done.append('新建表 algorithm_solution_like（题解点赞）')
        if not has_table('algorithm_reference_lang'):
            # 多语言参考答案。原先只有 algorithm.reference_code 一个字段 + reference_language，
            # 一题只能存一种语言的答案（实际 200 道题全是 Python），
            # 学生想看 C/C++/Java/JS 的写法只能自己翻。拆成独立表按 (题, 语言) 存。
            query(
                """CREATE TABLE algorithm_reference_lang (
                     id           INT AUTO_INCREMENT PRIMARY KEY,
                     algorithm_id INT NOT NULL COMMENT '所属题目',
                     language     VARCHAR(16) NOT NULL COMMENT 'c/cpp/java/javascript',
                     code         TEXT NOT NULL COMMENT '该语言的参考答案代码',
                     verified     TINYINT DEFAULT 0 COMMENT '1=已用测试用例真实跑通 0=未验证',
                     created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
                     UNIQUE KEY uk_algo_lang (algorithm_id, language)
                   ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='算法题多语言参考答案'"""
            )
            done.append('新建表 algorithm_reference_lang（多语言参考答案）')
    except Exception as e:
        print('[migrate] 算法题建表失败:', e)

    # 15) 案例分析题与编程题
    try:
        r = seed_module(
            'seed-case-prog.sql',
            "SELECT COUNT(*) AS c FROM question WHERE type IN ('case','programming')",
            60,
            '导入案例分析题与编程题',
        )
        if r:
            done.append(r)
    except Exception as e:
        print('[migrate] 案例/编程题导入失败:', e)

    # 16) 程序设计算法题库（依赖会话变量 @aid，必须单连接执行）
    try:
        r = seed_module(
            'seed-algo.sql',
            'SELECT COUNT(*) AS c FROM algorithm',
            20,
            '导入程序设计算法题库（含测试用例）',
        )
        if r:
            done.append(r)
    except Exception as e:
        print('[migrate] 算法题库导入失败:', e)

    # 17) Web 前端模块（HTML / CSS / JavaScript）
    try:
        r = seed_module(
            'seed-web.sql',
            'SELECT COUNT(*) AS c FROM knowledge WHERE id BETWEEN 86 AND 100',
            15,
            '导入 Web 前端模块（3 门课 / 15 个知识点 + 45 道题）',
        )
        if r:
            done.append(r)
    except Exception as e:
        print('[migrate] Web 前端模块导入失败:', e)

    # 18) 教材对照知识点：数学物理补充 + 机械工业出版社教材体系（数据库 / 编译原理）
    try:
        r = seed_module(
            'seed-textbook.sql',
            'SELECT COUNT(*) AS c FROM knowledge WHERE id BETWEEN 101 AND 117',
            17,
            '导入教材对照知识点（数学物理 7 点 + 数据库/编译原理 2 门课 10 点，共 51 道题）',
        )
        if r:
            done.append(r)
    except Exception as e:
        print('[migrate] 教材对照知识点导入失败:', e)

    # 19) 核心课程习题扩充：课程 1-4 每节补齐到 20 题（43 个知识点 × 20 = 860）
    try:
        r = seed_module(
            'seed-core20.sql',
            'SELECT COUNT(*) AS c FROM question WHERE knowledge_id IN '
            '(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,'
            '33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54)',
            860,
            '导入核心课程习题扩充（课程 1-4 每节补齐到 20 题，共新增 574 道）',
        )
        if r:
            done.append(r)
    except Exception as e:
        print('[migrate] 核心课程习题扩充导入失败:', e)

    # 20) 算法题库扩充：洛谷风格程序设计题 30 -> 200（依赖会话变量 @aid，必须单连接执行）
    try:
        r = seed_module(
            'seed-algo200.sql',
            'SELECT COUNT(*) AS c FROM algorithm',
            200,
            '导入算法题库扩充（洛谷风格 170 道 + 1020 个测试用例）',
        )
        if r:
            done.append(r)
    except Exception as e:
        print('[migrate] 算法题库扩充导入失败:', e)

    # 21) 习题补齐：课程 5-18 的知识点从 3~9 题补齐到 20 题
    #     判据用「题目总数」而不是单表 count：前面模块已把总量推到 1140，
    #     再 +1200 = 2340。用总量可以天然避免两个模块互相踩门槛。
    try:
        r = seed_module(
            'seed-rest20.sql',
            'SELECT COUNT(*) AS c FROM question',
            2340,
            '导入习题补齐（课程 5-18 每节补足到 20 题，共新增 1200 道）',
        )
        if r:
            done.append(r)
    except Exception as e:
        print('[migrate] 习题补齐导入失败:', e)

    # 22) 判断题答案规范化（对「最后导入」的习题补齐再做一次）
    #     步骤 11 的规范化跑在 seed-exam 之前，之后进来的题目（尤其第 21 步的 1200 道）
    #     根本没被它扫到。这批题按 T/F 写答案、options 留空，
    #     前端 Practice 页拿不到任何选项，整道题一个按钮都渲染不出来 ——
    #     学生看着题干却没法作答。所以规范化必须放在所有出题之后再兜一次底。
    try:
        row = query_one(
            "SELECT COUNT(*) AS c FROM question WHERE type = 'judge' "
            "AND (UPPER(TRIM(answer)) IN ('T','F','TRUE','FALSE','对','错','正确','错误') "
            "OR options IS NULL OR options = '' OR options = '[]')"
        )
        if row and int(row['c'] or 0) > 0:
            query(
                "UPDATE question SET "
                "  answer = CASE WHEN UPPER(TRIM(answer)) IN "
                "    ('T','TRUE','对','正确','√','A') THEN 'A' ELSE 'B' END, "
                "  options = '[{\"key\":\"A\",\"text\":\"正确\"},{\"key\":\"B\",\"text\":\"错误\"}]' "
                "WHERE type = 'judge'"
            )
            done.append(f'规范化 {int(row["c"])} 道判断题的答案与选项')
    except Exception as e:
        print('[migrate] 判断题二次规范化失败:', e)

    # 23) 用户反馈建议表：学生提 bug / 建议，管理员在后台处理并回复
    if not has_table('feedback'):
        query(
            'CREATE TABLE feedback ('
            '  id          INT AUTO_INCREMENT PRIMARY KEY,'
            '  user_id     INT NOT NULL COMMENT "提交人",'
            '  username    VARCHAR(64) DEFAULT "" COMMENT "提交人账号（冗余，账号注销后列表仍可读）",'
            '  type        VARCHAR(16) DEFAULT "bug" COMMENT "类型: bug功能异常/feature功能建议/experience体验问题/other其他",'
            '  content     TEXT NOT NULL COMMENT "反馈正文",'
            '  contact     VARCHAR(120) DEFAULT "" COMMENT "联系方式（选填）",'
            '  page        VARCHAR(200) DEFAULT "" COMMENT "提交时所处页面",'
            '  ua          VARCHAR(255) DEFAULT "" COMMENT "浏览器标识（排障用，截短存储）",'
            '  status      VARCHAR(16) DEFAULT "pending" COMMENT "pending待处理/processing处理中/resolved已解决/closed已关闭",'
            '  admin_reply TEXT COMMENT "管理员回复",'
            '  admin_id    INT DEFAULT NULL COMMENT "处理人",'
            '  replied_at  DATETIME NULL COMMENT "回复时间",'
            '  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,'
            '  updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,'
            '  INDEX idx_user (user_id),'
            '  INDEX idx_status (status),'
            '  INDEX idx_created (created_at)'
            ') ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT="用户反馈建议"'
        )
        done.append('新建表 feedback（用户反馈建议）')

    # ---- 临时密码申请：学生忘了姓名（自助找回走不通）时的兜底工单 ----
    if not has_table('password_request'):
        query(
            'CREATE TABLE password_request ('
            '  id            INT AUTO_INCREMENT PRIMARY KEY,'
            '  ticket        VARCHAR(20) NOT NULL COMMENT "申请单号：用户凭它查询结果",'
            '  user_id       INT NOT NULL COMMENT "申请人",'
            '  username      VARCHAR(64) DEFAULT "" COMMENT "账号冗余（管理员看的不是用户表的当前值）",'
            '  real_name     VARCHAR(64) DEFAULT "" COMMENT "申请时的姓名快照：管理员据此核对是不是本人",'
            '  phone         VARCHAR(32) DEFAULT "" COMMENT "联系电话：管理员线下核身 / 告知临时密码",'
            '  reason        VARCHAR(500) DEFAULT "" COMMENT "申请理由（选填）",'
            '  status        VARCHAR(16) DEFAULT "pending" COMMENT "pending待处理/approved已通过/rejected已驳回/used已使用",'
            '  temp_password VARCHAR(64) DEFAULT "" COMMENT "临时密码明文：没有邮件短信通道，只能留给用户凭单号自取；用它登录成功即刻清空",'
            '  admin_id      INT DEFAULT NULL COMMENT "处理人",'
            '  admin_name    VARCHAR(64) DEFAULT "" COMMENT "处理人账号（冗余）",'
            '  reject_reason VARCHAR(200) DEFAULT "" COMMENT "驳回理由",'
            '  handled_at    DATETIME NULL COMMENT "处理时间",'
            '  created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,'
            '  updated_at    DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,'
            '  UNIQUE KEY uk_ticket (ticket),'
            '  INDEX idx_user (user_id),'
            '  INDEX idx_status (status),'
            '  INDEX idx_created (created_at)'
            ') ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT="临时密码申请"'
        )
        done.append('新建表 password_request（临时密码申请）')

    # ---- Agent 长期记忆向量化：语义笔记 + 向量缓存 ----
    if not has_table('memory_note'):
        query(
            'CREATE TABLE memory_note ('
            '  id           INT AUTO_INCREMENT PRIMARY KEY,'
            '  user_id      INT NOT NULL COMMENT "所属用户",'
            '  kind         VARCHAR(16) DEFAULT "wrong" COMMENT "wrong错题 / chat问答",'
            '  ref_id       INT DEFAULT NULL COMMENT "关联的题目或对话记录",'
            '  knowledge_id INT DEFAULT NULL COMMENT "关联知识点",'
            '  title        VARCHAR(200) DEFAULT "" COMMENT "知识点名或问题标题",'
            '  content      TEXT NOT NULL COMMENT "被向量化的正文（题干+错因 / 问答摘要）",'
            '  weight       INT DEFAULT 1 COMMENT "权重：同一题重复犯错累加",'
            '  created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,'
            '  updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,'
            '  INDEX idx_user (user_id),'
            '  INDEX idx_user_kind (user_id, kind)'
            ') ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT="Agent 语义记忆笔记"'
        )
        done.append('新建表 memory_note（Agent 语义记忆笔记）')

    if not has_table('memory_vector'):
        query(
            'CREATE TABLE memory_vector ('
            '  note_id    INT PRIMARY KEY COMMENT "对应 memory_note.id",'
            '  model      VARCHAR(64) DEFAULT "" COMMENT "生成该向量的模型名",'
            '  dim        INT DEFAULT 0 COMMENT "维度",'
            '  vec        MEDIUMTEXT COMMENT "向量 JSON",'
            '  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'
            ') ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT="语义记忆向量缓存"'
        )
        done.append('新建表 memory_vector（语义记忆向量缓存）')

    return done


if __name__ == '__main__':
    result = run()
    print('迁移完成:\n  - ' + '\n  - '.join(result) if result else '无需迁移，结构已是最新')
