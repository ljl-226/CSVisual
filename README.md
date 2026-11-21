# CSVisual · 计算机专业多学科可视化智能学习平台

面向计算机专业本科生的 Web 学习平台。用可交互的 SVG 动画把数据结构、计算机网络、操作系统、计算机组成原理等课程的底层机制「跑起来」，再配上一套能检索知识库、调用工具、跳转动画的智能学习助手。

当前版本：**18 门课程 · 117 个知识点 · 72 个可视化案例 · 35 个代码实验室 · 2263 道习题 · 200 道算法题**。

---

## 一、核心设计

1. **动画是状态机，不是录屏。** 全部动画用原生 SVG + CSS 实现，每个案例先生成帧序列，再由播放控制器渲染「帧序列 + 下标」。因此可以播放、暂停、单步、回退、拖拽进度、切换 0.5x~4x 倍速，停在任何一步都能讲清楚当前状态。
2. **单一 Python 后端。** 后端只有 `server-py/`（FastAPI，默认 3000 端口），接口统一返回 `{code, data}` / `{code, message}`；生产模式下由后端直接托管前端构建产物，一个端口交付整套系统。
3. **三级代码执行通道。** 在线运行按「项目内置 `runtime/` → 系统已装编译器 → 云端沙箱（Wandbox / 可配置自建 Piston）」依次探测，本机没有编译环境也能拿到真实执行结果，且不会伪造成功。
4. **智能助手可离线降级。** 配置了 OpenAI 兼容接口就调用大模型；未配置 Key 时自动退回本地知识库（TF-IDF 检索 + 别名表）回答，断网也能完成完整演示。

---

## 二、项目速览

| 项目 | 数量 | 说明 |
|---|---|---|
| 课程 | 18 门 | 核心四门 + 数理五门 + 编程语言四门 + Web 前端三门 + 教材两门 |
| 知识点 | 117 个 | 每个知识点包含 Markdown 正文、可视化演示或代码实验室、配套习题 |
| 可视化案例 | 72 个 | 按 `ds/net/os/co/math/linalg/prob/phys/dm` 九类分组，共 71 个组件 |
| 代码实验室 | 35 个 | C / C++ / Java / Python / HTML / CSS / JavaScript 等语言的可运行示例 |
| 习题 | 2263 道 | 单选 / 判断 / 多选，按知识点组织，标注考研 408 / 软考 / NCRE / 期末 |
| 算法题 | 200 道 | 洛谷风格，五种语言作答，内置测试用例、提交判分与排行榜 |
| 页面 | 27 个 | 14 个学习页 + 4 个认证页 + 9 个管理后台页 |
| 数据库 | 21 张表 | MySQL 5.7+ / 8.0，`utf8mb4` |
| 后端接口 | 9 组路由 | auth / course / question / learn / agent / admin / feedback / code / algorithm |
| 测试 | 17 个文件 | pytest 338 个用例，进程内调用 ASGI 应用 |

---

## 三、功能模块

| 模块 | 主要能力 |
|---|---|
| **课程与可视化** | 课程中心、知识点详情、动画播放器；统一支持播放 / 暂停 / 单步 / 回退 / 重置 / 倍速 / 进度拖拽，多数案例可自定义初始数据 |
| **习题与练习** | 按来源、难度、掌握状态筛选；客观题即时判分，答错自动进错题本，答对自动移出；支持保留上次答案、重做此题、重做整套 |
| **错题重做** | 单题 / 本页 / 全部三档粒度，另有跨知识点错题集 `/wrong-practice`，答对标记「本次已攻克」 |
| **代码实验室** | 零依赖代码编辑器（高亮 / 补全 / 参数提示 / 自动缩进 / 草稿记忆）；宽屏下编辑器吸顶、结果面板吸底；Web 三语实时预览 |
| **算法题** | 题目列表、题面、在线自测、提交判分、通过率与排行榜、题解发布与点赞；控制台支持自定义输入 |
| **智能学习助手** | 意图识别 → Planner 拆解 → 工具按依赖分层并发 → 长期记忆召回 → 大模型或本地知识库作答；SSE 流式输出、任务面板、工具时间线与来源脚注 |
| **用户与个人中心** | 注册 / 登录 / 找回密码 / 临时密码申请；学习进度、收藏、错题本、对话记录、反馈进度；头像上传与恢复默认 |
| **管理后台** | 数据统计、知识点 / 可视化 / 题库 / 算法题 / 用户管理、临时密码工单审批、安全日志、反馈处理 |
| **反馈建议** | 任意页面悬浮入口，自动附带当前路由；个人中心查看处理进度，后台可回状态并写回复 |

智能助手内置 7 类工具：`kb_search`（知识库检索）、`code_run`（在线运行）、`render_formula`（公式渲染）、`draw_diagram`（流程图）、`quiz_generate`（出题）、`wrong_record`（错题整理）、`study_plan`（学习计划），并按 `TOOL_DEPENDS` 声明分层并发执行。

---

## 四、技术选型

| 层次 | 技术 |
|---|---|
| 前端 | Vue 3 + Vite + Vue Router + Pinia + Element Plus；动画全部原生 SVG / CSS；Markdown（markdown-it / marked）+ DOMPurify 净化，KaTeX 公式、Mermaid 图表按需异步加载 |
| 后端 | Python 3 + FastAPI + Uvicorn；PyMySQL + DBUtils 连接池；PyJWT + bcrypt；httpx |
| 数据库 | MySQL 5.7+ / 8.0，`utf8mb4` |
| 智能助手 | OpenAI 兼容接口（DeepSeek / 通义 / 智谱 / 本地 Ollama 均可）+ 本地知识库 RAG（TF-IDF，可选远程 embedding） |
| 代码运行 | 项目内置 `runtime/` 工具链（w64devkit + jlink 裁剪 JDK）/ 本机编译器 / Wandbox 云端沙箱 |
| 测试 | pytest（后端）；`web/scripts/` 下的 Node 自检脚本（SSR、可视化、XSS、主题、编辑器、Web 沙箱） |

---

## 五、项目结构

```
CSVisual/
├── server-py/                    # 唯一后端（Python / FastAPI，:3000）
│   ├── run.py                    # 启动入口
│   ├── app/
│   │   ├── main.py               # 应用装配、启动迁移、静态资源与 SPA 兜底
│   │   ├── db.py                 # PyMySQL 连接池
│   │   ├── core/                 # 配置、JWT、安全中间件、审计、统一响应与异常
│   │   ├── routers/              # 9 组业务路由
│   │   ├── agent/                # 意图、规划、工具、RAG、大模型、记忆、校验
│   │   ├── utils/                # 参数校验、数值处理、云端沙箱
│   │   └── scripts/              # initdb / migrate / repair
│   ├── sql/                      # schema.sql + 14 个种子与题库脚本
│   ├── tests/                    # pytest（17 个文件）
│   ├── .env.example              # 配置样例
│   └── requirements.txt
├── web/                          # 前端（Vue 3 + Vite，开发端口 5173）
│   ├── src/
│   │   ├── api/                  # axios 封装
│   │   ├── components/           # 编辑器、控制台、预览、分页等公共组件
│   │   │   └── vis/              # 可视化组件，按学科分九类
│   │   ├── data/                 # visMap.js（动画注册表）、codeLabs.js（实验室定义）
│   │   ├── layout/ router/ stores/ styles/ utils/
│   │   └── views/                # 14 个学习页 + 4 个认证页 + admin/ 9 个后台页
│   ├── scripts/                  # 6 个前端自检脚本
│   └── vite.config.js            # /api、/uploads 代理到 3000
├── tools/                        # 打包、运行时部署、数据生成与自检脚本
├── start.bat / start-python.bat / stop.bat     # Windows 一键启动 / 停止
├── start.sh / stop.sh                          # Linux / macOS
├── pack.bat                      # 打源码包
└── README.md
```

完整的逐目录职责、数据库表清单与文件数量统计见 [项目结构与源码清单.md](项目结构与源码清单.md)。

---

## 六、快速开始

### 方式一：安装包（普通用户）

双击 `CSVisual-Setup.exe` 安装，启动后自动打开浏览器。

### 方式二：一键脚本（开发者）

Windows 双击 `start.bat`，Linux / macOS 执行 `./start.sh`。脚本会依次检查 Python、Node.js、MySQL，创建虚拟环境、安装依赖、初始化数据库，然后启动前后端。

### 方式三：手工启动

```bash
# 1) 后端
cd server-py
copy .env.example .env          # Linux/macOS: cp .env.example .env
# 按本机情况修改 DB_HOST / DB_USER / DB_PASSWORD / DB_NAME

python -m venv .venv
.venv\Scripts\activate          # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt

set PYTHONPATH=.                # Linux/macOS: export PYTHONPATH=.
python -m app.scripts.initdb    # 建库建表并导入种子数据（幂等）
python run.py                   # http://localhost:3000

# 2) 前端（另开终端）
cd web
npm install
npm run dev                     # http://localhost:5173，/api 已代理到 3000
```

后端接口文档：`http://localhost:3000/docs`；健康检查：`http://localhost:3000/api/health`。

### 内置账号

| 角色 | 账号 | 密码 |
|---|---|---|
| 管理员 | `admin` | `admin123` |
| 学生 | `student` | `123456` |

---

## 七、配置

配置从 `server-py/.env` 读取（不存在时回落到项目根目录 `.env`，再不存在则全部使用默认值）。

| 变量 | 说明 |
|---|---|
| `PORT` | 服务端口，默认 `3000` |
| `CSVISUAL_ENV` | `development` / `production`；生产环境强制要求自定义 `JWT_SECRET` |
| `DB_HOST / DB_PORT / DB_USER / DB_PASSWORD / DB_NAME` | MySQL 连接，默认 `127.0.0.1:3306` / `root` / `cs_visual` |
| `JWT_SECRET / JWT_EXPIRES` | 令牌密钥与有效期（默认 7 天） |
| `ALLOWED_ORIGINS` | 跨域白名单，逗号分隔；留空时开发态放通本机端口、生产态只允许同源 |
| `RATE_MAX / RATE_AUTH_MAX / RATE_HEAVY_MAX` | 限流：全局 600 次/分钟、认证 20 次/15 分钟、重资源 30 次/分钟 |
| `LOGIN_MAX_FAIL / LOGIN_LOCK_MINUTES` | 连续失败 5 次锁定 15 分钟 |
| `COOKIE_SECURE / COOKIE_NAME` | HttpOnly Cookie 通道 |
| `TS_TOLERANCE` | 敏感写接口 `X-Timestamp` 容差，默认 300 秒 |
| `AUDIT_LOG` | 是否记录审计日志 |
| `LLM_API_KEY / LLM_BASE_URL / LLM_MODEL / LLM_THINKING` | 大模型配置，`LLM_API_KEY` 留空则走本地知识库降级 |
| `EMBEDDING_API_KEY / EMBEDDING_BASE_URL / EMBEDDING_MODEL` | 可选的语义向量检索，留空使用本地 TF-IDF |

---

## 八、测试

```bash
cd server-py
python -m pytest tests/ -q        # 17 个文件 / 338 个用例
```

测试通过 FastAPI `TestClient` 在进程内调用 ASGI 应用，无需额外起端口；涉及数据库的用例需要本地 MySQL 可用。

前端自检：

```bash
cd web
npm run check:ssr     # 服务端渲染一致性
npm run check:vis     # 可视化注册表与组件一致性
npm run check:xss     # Markdown 渲染的 XSS 防护
```

---

## 九、打包与交付

| 产物 | 命令 | 说明 |
|---|---|---|
| 源码包 | `python tools/pack.py --no-runtime` | 剔除 `node_modules`、`dist`、`runtime`、`.env`、`uploads`、`__pycache__` 等 |
| 绿色运行包 | `python tools/build_portable.py` | 便携目录，解压即用、删目录即卸载 |
| Windows 安装包 | `python tools/build_setup.py` | 内置 Python 便携运行时 + MySQL 精简版，安装后自动初始化数据库 |
| 内置工具链 | `python tools/setup_runtime.py` | 部署 / 校验 / 清理 `runtime/` 下的 C/C++、Java 工具链 |

`runtime/`、`node_modules/`、`web/dist/`、`server-py/.env`、`server-py/uploads/` 都是构建或运行期产物，不属于源码，也不进入版本库（见 `.gitignore`）。

---

## 十、相关文档

- [项目结构与源码清单.md](项目结构与源码清单.md)：逐目录职责、数据表清单、阅读顺序与文件统计
- [server-py/README.md](server-py/README.md)：后端实现细节、迁移说明、在线运行与工具链
- `web/src/data/visMap.js`：全部可视化案例的唯一注册表
- `web/src/data/codeLabs.js`：全部代码实验室的语言定义与示例
