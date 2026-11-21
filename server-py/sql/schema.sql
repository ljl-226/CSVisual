-- ============================================================
--  基于Agent的计算机专业多学科可视化智能学习平台 - 数据库结构
--  MySQL 5.7+ / 8.0   字符集 utf8mb4
-- ============================================================
SET NAMES utf8mb4;

CREATE DATABASE IF NOT EXISTS cs_visual
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_general_ci;
USE cs_visual;

-- 1. 用户表
DROP TABLE IF EXISTS user;
CREATE TABLE user (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  username     VARCHAR(64)  NOT NULL UNIQUE COMMENT '账号',
  password     VARCHAR(255) NOT NULL COMMENT '密码(bcrypt加密)',
  real_name    VARCHAR(64)  DEFAULT '' COMMENT '姓名',
  role         ENUM('student','admin') DEFAULT 'student' COMMENT '角色',
  avatar       VARCHAR(255) DEFAULT '' COMMENT '头像',
  created_at   DATETIME     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 2. 课程表
DROP TABLE IF EXISTS course;
CREATE TABLE course (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  name       VARCHAR(64) NOT NULL COMMENT '课程名称',
  category   VARCHAR(32) NOT NULL COMMENT '分类标识 ds/net/os/co',
  intro      TEXT COMMENT '课程简介',
  icon       VARCHAR(64) DEFAULT '' COMMENT '图标',
  sort_no    INT DEFAULT 0 COMMENT '排序',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='课程表';

-- 3. 知识点表
DROP TABLE IF EXISTS knowledge;
CREATE TABLE knowledge (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  course_id   INT NOT NULL COMMENT '所属课程id',
  name        VARCHAR(128) NOT NULL COMMENT '知识点名称',
  summary     VARCHAR(500) DEFAULT '' COMMENT '一句话摘要(RAG检索用)',
  content     TEXT COMMENT '知识点正文(Markdown)',
  route       VARCHAR(255) DEFAULT '' COMMENT '可视化页面路由地址',
  sort_no     INT DEFAULT 0 COMMENT '排序',
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_course (course_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='知识点表';

-- 4. 可视化案例表
DROP TABLE IF EXISTS visualization;
CREATE TABLE visualization (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  knowledge_id INT NOT NULL COMMENT '关联知识点id',
  title        VARCHAR(128) NOT NULL COMMENT '案例标题',
  description  TEXT COMMENT '案例描述',
  config       TEXT COMMENT '动画配置参数(JSON)',
  created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_k (knowledge_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='可视化案例表';

-- 5. 习题表
DROP TABLE IF EXISTS question;
CREATE TABLE question (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  knowledge_id INT NOT NULL COMMENT '关联知识点id',
  type         ENUM('single','judge','multi') DEFAULT 'single' COMMENT '题型',
  title        TEXT NOT NULL COMMENT '题干',
  options      TEXT COMMENT '选项JSON: [{key:"A",text:"..."}]',
  answer       VARCHAR(64) NOT NULL COMMENT '正确答案 A/B/C/D 或 对/错',
  analysis     TEXT COMMENT '解析',
  score        INT DEFAULT 5 COMMENT '分值',
  created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_k (knowledge_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='习题表';

-- 6. 错题表
DROP TABLE IF EXISTS wrong_question;
CREATE TABLE wrong_question (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  user_id         INT NOT NULL,
  question_id     INT NOT NULL,
  wrong_count     INT DEFAULT 1 COMMENT '错误次数',
  last_wrong_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '最近错误时间',
  UNIQUE KEY uk_user_question (user_id, question_id),
  INDEX idx_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='错题表';

-- 7. Agent 对话记录表
DROP TABLE IF EXISTS chat_record;
CREATE TABLE chat_record (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  user_id       INT NOT NULL,
  question      TEXT NOT NULL COMMENT '用户提问',
  answer        TEXT COMMENT 'Agent回答',
  knowledge_id  INT DEFAULT NULL COMMENT '关联知识点id',
  mode          VARCHAR(16) DEFAULT 'llm' COMMENT 'llm/fallback',
  created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Agent对话记录表';

-- 8. 学习记录表（辅助）
DROP TABLE IF EXISTS study_record;
CREATE TABLE study_record (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  user_id       INT NOT NULL,
  knowledge_id  INT NOT NULL,
  event_type    VARCHAR(16) DEFAULT 'view' COMMENT 'view/quiz/vis',
  visit_count   INT DEFAULT 1,
  duration      INT DEFAULT 0 COMMENT '停留秒数',
  last_time     DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_user_knowledge (user_id, knowledge_id),
  INDEX idx_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学习记录表';

-- 9. 收藏表（辅助）
DROP TABLE IF EXISTS favorite;
CREATE TABLE favorite (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  user_id      INT NOT NULL,
  knowledge_id INT NOT NULL,
  created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_user_knowledge (user_id, knowledge_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='知识点收藏表';

-- 10. 答题记录表（辅助，支撑正确率统计）
DROP TABLE IF EXISTS answer_record;
CREATE TABLE answer_record (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  user_id      INT NOT NULL,
  question_id  INT NOT NULL,
  user_answer  VARCHAR(128) DEFAULT '',
  is_correct   TINYINT DEFAULT 0,
  created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='答题记录表';

-- 11. Agent 语义记忆笔记（长期记忆向量化的载体）
DROP TABLE IF EXISTS memory_note;
CREATE TABLE memory_note (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  user_id      INT NOT NULL COMMENT '所属用户',
  kind         VARCHAR(16) DEFAULT 'wrong' COMMENT 'wrong错题 / chat问答',
  ref_id       INT DEFAULT NULL COMMENT '关联的题目或对话记录',
  knowledge_id INT DEFAULT NULL COMMENT '关联知识点',
  title        VARCHAR(200) DEFAULT '' COMMENT '知识点名或问题标题',
  content      TEXT NOT NULL COMMENT '被向量化的正文（题干+错因 / 问答摘要）',
  weight       INT DEFAULT 1 COMMENT '权重：同一题重复犯错累加',
  created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_user (user_id),
  INDEX idx_user_kind (user_id, kind)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Agent 语义记忆笔记';

-- 12. 语义记忆向量缓存（仅在配置了远程 embedding 时使用）
DROP TABLE IF EXISTS memory_vector;
CREATE TABLE memory_vector (
  note_id    INT PRIMARY KEY COMMENT '对应 memory_note.id',
  model      VARCHAR(64) DEFAULT '' COMMENT '生成该向量的模型名',
  dim        INT DEFAULT 0 COMMENT '维度',
  vec        MEDIUMTEXT COMMENT '向量 JSON',
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='语义记忆向量缓存';

-- 内置管理员账号（密码: admin123）
INSERT INTO user (username, password, real_name, role)
VALUES ('admin', '$2a$10$cxtegmXY0oQ6b1kpmOMS3.n5.XSqqJBd4PSfYjASi77a8EIZRTF.m', '系统管理员', 'admin');
-- 内置演示学生账号（密码: 123456）
INSERT INTO user (username, password, real_name, role)
VALUES ('student', '$2a$10$hSbryF4n2ECYlVwhzFERRODG83kdGSWTKVtJGrgYXP4s76kwPNDDy', '演示同学', 'student');
