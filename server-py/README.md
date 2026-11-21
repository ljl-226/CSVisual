# CSVisual 后端（Python / FastAPI 版）

这是 CSVisual 平台后端从 Node.js/Express 到 **Python / FastAPI** 的完整迁移版本。

**前端零改动**：所有接口路径、请求体、响应结构与原 Express 版逐字一致
（`{code:200, data:...}` / `{code:400, message:...}`），前端只通过 HTTP 调 `/api/*`，
把后端换成 Python 后 `web/` 目录一行代码都不用动。

---

## 一、目录结构

```
server-py/
├── app/
│   ├── main.py                 # 应用装配 + 启动迁移 + 数据体检
│   ├── db.py                   # PyMySQL 连接池，? 占位符（与 mysql2 写法一致）
│   ├── core/
│   │   ├── config.py           # .env 加载（优先 server-py/.env，回落 server/.env）
│   │   ├── security.py         # JWT 签发校验 + bcrypt 密码散列
│   │   ├── deps.py             # current_user / admin_user / optional_user 依赖
│   │   ├── body.py             # JSON body 解析中间件
│   │   ├── errors.py           # 401/403 异常 → 统一响应
│   │   └── response.py         # ok() / fail() 统一包体
│   ├── agent/
│   │   ├── guard.py            # 意图识别 + 安全护栏 + 反提示注入
│   │   ├── reasoning.py        # 思考链生成（先思考再回答）
│   │   ├── grading.py          # 主观题要点判分 + 反作弊
│   │   ├── vector.py           # TF-IDF 向量检索
│   │   ├── llm.py              # 大模型调用 + 本地降级
│   │   ├── rag.py              # 检索增强
│   │   └── report.py           # 学情报告
│   ├── routers/                # 8 个业务模块，共 60+ 接口
│   ├── utils/validate.py       # 参数校验（含 to_js_string）
│   └── scripts/
│       ├── migrate.py          # 增量迁移（幂等）
│       ├── initdb.py           # 一键初始化
│       └── repair.py           # 数据体检与修复
├── tests/                      # pytest 测试套件
├── run.py                      # 启动入口
├── start.bat / start.sh        # 一键启动（建 venv → 装依赖 → 初始化 → 起服务）
└── requirements.txt
```

## 二、快速开始

### 方式一：双击 `start.bat`（Windows）

脚本会自动完成：检查 Python → 创建 `.venv` → 安装依赖 → 初始化数据库 → 启动服务。

### 方式二：命令行

```bash
cd server-py

python -m venv .venv
.venv\Scripts\activate          # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt

# 初始化数据库（建库建表 + 导入课程与题库）
set PYTHONPATH=.                # Linux/Mac: export PYTHONPATH=.
python -m app.scripts.initdb

# 启动
python run.py                   # 或 uvicorn app.main:app --port 3000
```

服务起来后：

- 接口地址 `http://localhost:3000/api`
- 健康检查 `http://localhost:3000/api/health`
- **自动接口文档** `http://localhost:3000/docs`（Node 版没有的额外收益）

前端照常 `cd ../web && npm run dev`，Vite 已把 `/api` 代理到 3000 端口。

## 三、运行测试

```bash
cd server-py
python -m pytest tests/ -q
```

测试通过 FastAPI `TestClient` 在进程内调用 ASGI 应用，**不需要起端口、不需要起数据库以外的任何服务**。

## 四、技术映射对照

| Node/Express | Python/FastAPI | 说明 |
|---|---|---|
| `express` + `cors` | `FastAPI` + `CORSMiddleware` | |
| `mysql2/promise` | `PyMySQL` + `dbutils` 连接池 | **保留了 `?` 占位符写法**，SQL 语句原样迁移 |
| `jsonwebtoken` | `PyJWT` | payload 一致，两边签发的 token 可互认 |
| `bcryptjs` | `bcrypt` | `$2a$`/`$2b$` 前缀互通，**老用户密码无需重置** |
| `middleware/auth.js` | `Depends(current_user)` | |
| `child_process.exec` | `subprocess.run` | 编译器探测与判题 |
| — | `app/scripts/repair.py` | 新增：数据体检与自愈 |

## 五、迁移中修掉的两个真实 Bug

这两个 bug 只有在真实跑起来时才会暴露，都是「不报错、只是结果不对」的类型。

### 1. 数组转字符串语义不一致（多选题判分会恒错）

Node 里到处用 `String(x)` 收口，而 Python 的 `str()` 与它在数组上行为不同：

```js
String(['A','B'])   // 'A,B'
```

```python
str(['A','B'])      # "['A', 'B']"
```

多选题的作答是数组，照搬 `str()` 会让答案跟库里的 `'A,B'` 永远对不上。
解决方式是在 `app/utils/validate.py` 里写了 `to_js_string()`，逐类型对齐 JS 的 `String()`
语义（数组摊平、布尔转 `true/false`、对象转 `[object Object]`、`1.0` 转 `'1'`）。

### 2. `subprocess.run(input=...)` 传了字符串（判题 100% 超时）

`subprocess.run` 的管道默认是二进制模式，`input` 必须是 `bytes`。传 `str` 会让内部
的写入线程抛 `TypeError` 后**静默死掉**，导致子进程的 stdin 永远不关闭 —— 凡是读输入
的程序（`sys.stdin.read()`，而判题必读）都会卡到超时。

这个 bug 特别隐蔽：接口照样返回 200，只是判题结果永远是 `runtime_error`。
修复在 `app/routers/code.py` 的 `run()`，并配了专门的回归测试。
注意这里**刻意不用 `text=True`**：文本模式在 Windows 上会把 `\n` 翻译成 `\r\n`，
判题是逐字符比对输出，任何换行转换都会造成误判。

## 六、数据体检（新增）

原 Node 版的边界测试会往库里插入伪造 ID（如 `knowledge_id=99999999`）的行，
部分用例还直接改了已有可视化的外键，跑完没清理。这会造成：

- 知识点详情页返回 404、前端出现空白卡片；
- 某个知识点下的可视化凭空消失（内容还在，只是外键被改坏了）。

`app/scripts/repair.py` 负责扫描并修复，**服务启动时会自动跑一遍**（只在真有问题时打印）：

```bash
python -m app.scripts.repair --dry-run   # 只报告不改动
python -m app.scripts.repair             # 执行修复（自动备份到 backups/）
```

修复逻辑：先还原已知被改坏的外键，再从叶子表往父表清孤儿行，
全程备份为 JSON 便于回滚。

## 七、环境变量

沿用 `server/.env`（不存在时自动回落读取），无需重新配置：

| 变量 | 说明 | 默认 |
|---|---|---|
| `DB_HOST` / `DB_PORT` / `DB_USER` / `DB_PASSWORD` / `DB_NAME` | 数据库连接 | `127.0.0.1:3306` / `root` / `cs_visual` |
| `PORT` | 服务端口 | `3000` |
| `JWT_SECRET` / `JWT_EXPIRES` | 令牌密钥与有效期 | `csvisual_secret_key_change_me` / `7d` |
| `LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL` | 大模型（不配则走本地知识库降级） | 空 |
| `CODE_RUN` | 设为 `0` 可关闭在线运行 | 默认开启 |

> 提示：`JWT_SECRET` 当前默认值长度 29 字节，低于 RFC 7518 建议的 32 字节，
> PyJWT 会打印 `InsecureKeyLengthWarning`。HMAC 本身并未被削弱，
> 但部署到公网前建议在 `.env` 里换成 32 位以上的随机串
> （改了会让已登录用户重新登录一次）。

## 八、在线运行与内置工具链

判题和执行由 `app/routers/code.py` 负责。核心契约是**永远如实告知**：
有编译器就真实编译运行并返回输出，没有就明确说「未检测到 XX 环境」并给出安装指引，
绝不伪造成功。

### 探测优先级

`runtime\` 是否存在决定了这个功能是「开箱可用」还是「碰运气」：

```
1. 项目内置 runtime\        最优先 —— 它由 tools\setup_runtime.py 部署，跟着项目走
2. 环境变量                 CSVISUAL_GCC / CPP_COMPILER / JAVA_HOME 等显式指定
3. PATH                     系统上正常安装的 gcc / javac / python
4. 常见安装目录             WinGet、Program Files 下的已知布局（有界深度扫描）
5. 实在找不到               返回降级提示 + 安装指引
```

内置排在第一位，是为了让「程序里能做出来但看不到结果」这种现象不再发生：
只要 `runtime\` 在，无论这台机器装没装过编译器，行为都一致。

### 目录约定

```
runtime/
├── c-cpp/bin/gcc.exe       C 编译（w64devkit，已裁掉 Fortran / cmake / vim / 32 位库）
├── c-cpp/bin/g++.exe       C++ 编译
├── java/bin/javac.exe      Java 编译（由 JDK 经 jlink 裁出的私有运行时）
├── python/python.exe       可选：服务本身是 Python，通常不必部署
├── node/node.exe           可选：前端本来就要 Node，通常不必部署
└── .manifest.json          部署清单（来源、版本、体积、验证结果）
```

部署与维护都用项目根目录的 `tools\setup_runtime.py`：

```bash
python tools/setup_runtime.py            # 自动：优先下载官方便携包
python tools/setup_runtime.py --info     # 查看当前状态
python tools/setup_runtime.py --verify   # 逐语言真实编译运行验证
python tools/setup_runtime.py --clean    # 删除已部署的工具链
```

### `source` 字段

`GET /api/code/env` 每一项都带 `source`：

| 值 | 含义 | 前端展示 |
|---|---|---|
| `bundled` | 命中项目内置 `runtime\` | 「内置编译器」绿色标签 |
| `system` | 命中本机 PATH / 环境变量里装的工具链 | 「本机环境」灰色标签 |
| `null` | 没找到 | 降级提示 + 安装指引 |

> 迁移时修过一个真 bug：`detect_env()` 里 java / python 原先是先扫 PATH 再调探测函数，
> 导致 `runtime\java` 明明存在却永远轮不上，标签退化成「本机环境」。
> 已改为探测函数前置，并由回归测试 `test_java_source_not_degraded_to_system` 锁住。

## 九、已知限制

- 未部署内置工具链、本机也没装编译器时，接口会明确返回「未检测到 XX 编译器」并给出
  安装指引，不会伪造成功 —— 这是设计，不是缺陷。
- 判题为单机串行执行，未做沙箱隔离（仅 5 秒超时强杀 + 临时目录隔离 + 每分钟限流）。
  公网部署需要额外加容器 / 资源限制。
- Windows 上有宿主环境禁止 Node 创建子进程的情况（表现为 `spawnSync` 返回
  `EBUSY`）：同样的可靠子进程能力 Python 侧不受影响，这也是推荐 Python 后端的原因之一。

## 九、两个后端如何切换

两个后端监听同一个端口（3000），同时只能起一个：

- 用 Python 版：双击 `server-py/start.bat`，或 `cd server-py && python run.py`
- 用回 Node 版：双击根目录 `start.bat`，或 `cd server && npm start`

前端无需任何改动。
