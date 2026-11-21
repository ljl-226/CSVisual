# CSVisual · 计算机专业多学科可视化智能学习平台

面向计算机专业大学生的 Web 端可视化学习平台：用交互动画把数据结构与算法、计算机网络、操作系统、计算机组成原理的底层原理"动起来"，并搭载智能学习助手——自然语言提问 → 检索知识库 → 跳转对应动画 → 结合错题数据诊断薄弱点。

**四个关键设计**

1. **动画全部原生 SVG + CSS**，零图形依赖，可单步、可回退、可调速——不是录屏，是能停在任何一步上讲的状态机。
2. **单后端（Python / FastAPI）**：自 2026-10-10 起项目收敛为纯 Python 后端，原来同构的 Node/Express 实现已归档到 `build/_trash/server-node-*`，接口契约保持不变。
3. **运行环境随项目走**：C/C++/Java 工具链打进 `runtime/`，任何人拿到源码都能点「运行」出结果，不依赖访客机器上装过什么。
4. **离线也能完整演示**：未配置大模型 Key 时自动降级为本地知识库回答，比赛现场断网不影响主流程。

---

## 一、项目速览

| 项目 | 数量 | 说明 |
|---|---|---|
| 课程 | 18 门 | 核心四门 + 数理三门 + 物理/离散 + 编程语言四门 + Web 前端三门 + 教材两门 |
| 知识点 | 117 | 每个配正文（Markdown）+ 可视化动画或代码实验室 + 20 道配套习题 |
| 可视化动画 | 71 | 按 `ds/net/os/co/math/linalg/prob/phys/dm` 九类分组 |
| 代码实验室 | 35 | C / C++ / Java / Python / HTML / CSS / JavaScript 各 5 个 |
| 配套习题 | 2340 | 117 知识点 × 每节 20 道，打标考研 408 / 软考 / NCRE / 期末 |
| 算法题 | 200 | 洛谷风格，1180 个测试用例，参考代码全部实测过 |
| 后端 | 1 套 | `server-py`（Python/FastAPI），端口 3000 |
| 前端 | 1 套 | Vue 3 + Vite，端口 5173 |

---

## 二、技术选型

| 层次 | 技术 |
|---|---|
| 前端 | Vue 3 + Vite + Vue Router + Pinia + Element Plus；可视化全部原生 SVG/CSS；Markdown 走 marked + DOMPurify，公式 KaTeX、图 Mermaid（按需异步加载） |
| 后端 | Python 3 + FastAPI（PyMySQL + PyJWT + bcrypt） |
| 数据库 | MySQL 5.7+ / 8.0（utf8mb4） |
| 智能助手 | 大模型（OpenAI 兼容接口，可配 DeepSeek / 通义 / 本地 Ollama）+ 本地知识库 RAG（TF-IDF 向量 + 别名表）；**未配置 Key 时自动降级** |
| 代码运行 | 内置 `runtime/` 工具链（w64devkit + jlink 裁剪 JDK）；JS 走进程内沙箱 |

---

## 三、目录结构

```
CSVisual/
├── server-py/           # 后端：Python + FastAPI（唯一后端）
│   ├── run.py           # 入口（:3000）
│   ├── .env             # 数据库 / JWT / 大模型配置（由 .env.example 复制而来）
│   ├── sql/             # schema.sql + 各阶段 seed（建库与迁移的数据源）
│   ├── app/
│   │   ├── core/        # config / security / shield / audit / deps / response / errors
│   │   ├── routers/     # auth course question learn code algorithm agent admin feedback
│   │   ├── agent/       # rag / llm / tools / planner / verifier / memory / trace / report
│   │   ├── utils/       # validate / num / remote_run（Wandbox 云端沙箱兜底）
│   │   └── scripts/     # initdb / migrate / repair
│   └── tests/           # pytest（17 个文件）
├── web/                 # 前端
│   ├── vite.config.js   # /api → 3000，/uploads → 3000
│   └── src/
│       ├── api/         # axios 封装（统一带 X-Timestamp）
│       ├── components/  # RunConsole（统一控制台：会话流水 + 常驻输入行 + 历史）、CodeEditor（自研零依赖编辑器）、VisFrame、WebPreview、AlgoAssistant、AuthShell、PaginationBar…
│       │   └── vis/     # 71 个可视化组件，按学科分 ds/net/co/os/math/prob/phys/linalg/dm
│       ├── utils/       # indent / draftStore / codeTemplates / markdown / avatar / phone / theme / sse / webSandbox
│       ├── views/       # 17 个页面 + views/admin/ 9 个后台页
│       └── data/        # codeLabs.js（35 个实验室）、visMap.js（71 个动画登记）
├── runtime/             # 内置工具链（C/C++ 约 411MB + Java 约 45MB，不进源码包）
├── tools/               # pack.py（源码包）、build_portable.py（绿色包）、build_setup.py（安装包）、ensure-runtime.bat（部署工具链）、llm_check.py（大模型自检）、algo/（算法题生成器）
├── start.bat / start.sh         # 一键启动（Python 后端 + 前端）
├── start-python.bat             # 同上（start.bat 直接转发到这里）
└── stop.bat / stop.sh           # 停止
```

---

## 四、快速开始

> 双击 CSVisual-Setup.exe

**内置账号**：管理员 `admin / admin123`；学生演示 `student / 123456`。

**常用环境变量**（`server-py/.env`）：

| 变量 | 说明 |
|---|---|
| `DB_HOST/DB_USER/DB_PASSWORD/DB_NAME` | 数据库连接 |
| `JWT_SECRET` | 令牌密钥；生产为占位值时拒绝启动 |
| `ALLOWED_ORIGINS` | 跨域白名单，逗号分隔 |
| `LLM_API_KEY/LLM_BASE_URL/LLM_MODEL/LLM_THINKING` | 大模型配置，留空则离线降级 |
| `RATE_MAX / RATE_AUTH_MAX / RATE_HEAVY_MAX` | 限流：全局 600/min、认证 20/15min、重资源 30/min |
| `LOGIN_MAX_FAIL / LOGIN_LOCK_MINUTES` | 5 次失败锁 15 分钟 |
| `TS_TOLERANCE / COOKIE_SECURE / AUDIT_LOG / TRUST_PROXY` | 防重放容差（默认 300s）／Cookie 仅 HTTPS／审计日志／信任反向代理头 |

---

## 五、功能模块

| 模块 | 要点 |
|---|---|
| **用户与个人中心** | 注册（bcrypt 加盐）、登录（JWT + HttpOnly Cookie）、空闲 30 分钟自动登出；个人中心含学习进度 / 收藏 / 错题本 / 对话记录 / 我的反馈，统一分页；头像本地 canvas 压缩后上传，支持查看与恢复默认 |
| **课程与可视化** | 18 门课 117 知识点 71 个动画，统一支持播放 / 暂停 / 单步 / 回退 / 重置 / 0.5x~4x 倍速 / 进度拖拽，多数可自定义初始数据 |
| **习题与做题** | 2340 道题按来源与难度三维筛选；客观题即时判分、答错进错题本、答对自动移出；支持保留上次答案、重新做此题/此套题、只看未掌握 |
| **错题重做** | 三档粒度：重做此题 / 本页 / 全部（上限 200），跨知识点题集 `/wrong-practice`，答对标记「本次已攻克」 |
| **代码实验室** | 35 个可交互实验室；自研零依赖编辑器（高亮 / 补全 / 参数提示 / 自动缩进 / 缩进整理 / 草稿记忆）；宽屏编辑器吸顶 + 结果面板吸底；Web 三语实时预览 |
| **算法题** | 200 道洛谷风格题目，五种语言作答，在线运行自测 + 提交判分 + 通过率 + 排行榜，支持提交题解与点赞 |
| **智能助手** | 13 类意图 → Planner 拆解 → 7 个工具按依赖分层并发 → 长期记忆（语义笔记向量化召回）→ LLM 作答；SSE 流式、任务拆解面板、工具时间线、来源脚注；命中知识点时下发 `navigate` 直达动画或练习页 |
| **管理后台** | 数据统计、知识点 / 可视化 / 题库 / 算法题 / 用户 CRUD、临时密码工单审批、安全日志、反馈处理 |
| **反馈建议** | 右下角悬浮钮任意页面唤起，自动带当前路由；个人中心看处理进度，后台可回状态 + 写回复 |
| **找回密码** | 账号 + 姓名自助重置；不记得姓名可取脱敏提示；都不记得则走「申请临时密码」，管理员电话核身后人工放行 |

---
