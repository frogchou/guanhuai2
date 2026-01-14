# guanhuai2

一个支持“克隆联系人声音”的情感语音聊天系统：  
通过 Index TTS 克隆联系人声音，让 AI 以对方的语气和称呼方式和你进行语音对话，前端界面整体风格参考微信聊天界面。

---

## 1. 项目简介

本项目是一个端到端的 AI 语音聊天系统，主要能力包括：
- 录制或上传联系人语音样本，调用 Index TTS 服务完成“声音克隆”
- 基于克隆后的声音，让 LLM 扮演该联系人，与用户进行情感化对话
- 使用微信风格的对话界面，以“按住说话”的方式进行语音聊天
- 后端负责语音转文字（STT）→ 大模型回复（LLM）→ 文字转语音（TTS）完整流水线

典型使用场景：
- 和家人/重要联系人进行“情感陪伴式”语音聊天
- 用熟悉的声音做心理安抚、日常关怀或简单闲聊
- 为特定角色（如“奶奶”“导师”“好朋友”）定制语气和称呼方式

> 重要提示：项目内已加入“法律权利确认”逻辑，只允许在用户确认具有合法权利的前提下进行声音克隆，实际部署时仍需遵守所在地法律法规及平台政策。

---

## 2. 核心功能

- 联系人 / 角色（Persona）管理  
  - 新增联系人时，可配置：
    - 姓名（例如：Grandma）
    - 与用户的关系（例如：Grandmother）
    - 对方怎么称呼你（persona_called_by）
    - 你怎么称呼对方（user_called_by）
  - 上传联系人头像
  - 为每个联系人单独上传语音样本并创建对应的“克隆声音模型”

- 声音克隆（Index TTS 集成）  
  - 上传联系人语音样本到后端 `/api/v1/personas/{id}/voice`
  - 后端调用 Index TTS 服务：
    - `upload_audio`：上传语音样本，获取服务器上的音频绝对路径
    - `tts`：根据文本和样本音色生成回复语音
  - 支持 mock 模式：在配置中使用 mock 地址时，后端会生成静音 wav 文件，方便在无真实 TTS 服务时调试前端流程

- 语音对话流水线  
  1. 前端在聊天页按住录音，使用 `MediaRecorder` 采集音频
  2. 将音频以 multipart/form-data 的形式发送到 `/api/v1/conversations/{persona_id}/send`
  3. 后端保存用户语音文件并创建一条用户消息记录
  4. 通过后台任务执行完整链路：
     - STT：调用 OpenAI Whisper（或 Mock）将语音转文字
     - LLM：根据 Persona 的设定和用户内容，构造 system prompt，调用 OpenAI Chat Completion（或 Mock），得到情感标注和回复内容（JSON 格式，含 tone 和 content）
     - TTS：调用 Index TTS，将 LLM 文本回复合成为语音文件
  5. 将生成好的语音文件路径更新到消息记录中，前端轮询 `/messages` 接口获取新消息与语音 URL

- 微信风格聊天界面（前端）  
  - 使用 Vue 3 + Vant 实现移动端友好的聊天 UI：
    - 顶部导航条样式类似微信
    - 左右气泡区分用户和“联系人”（AI）
    - 头像区域、绿色气泡、尾巴样式等贴近微信视觉
  - 支持：
    - “按住说话”录音发送
    - 消息列表自动滚动到底部
    - 显示情绪分析标签（tone）
    - 在消息生成中展示 Loading 状态

- 账号与权限  
  - 后端使用 JWT 做登录态管理（FastAPI + 自定义安全模块）
  - 只有登录用户才能管理自己的 Persona、上传语音样本和发起聊天

---

## 3. 技术栈

- 前端（`frontend/`）
  - 框架：Vue 3 + TypeScript
  - 构建工具：Vite
  - 路由：vue-router
  - 状态管理：Pinia（`src/stores/auth.ts` 用于登录态与 Token 管理）
  - UI 组件：Vant（适配移动端、微信风格 UI）
  - HTTP 客户端：axios

- 后端（`backend/`）
  - Web 框架：FastAPI
  - 配置管理：pydantic-settings，读取根目录 `.env`
  - 数据库：SQLAlchemy + Alembic 迁移（见 `backend/alembic/`）
  - 鉴权：JWT 登录认证（`app/core/security.py`）
  - 日志：统一日志配置（`app/core/logging.py`）
  - 语音转文字（STT）：OpenAI Whisper（或 Mock）
  - 文本生成（LLM）：OpenAI Chat Completions（或 Mock）
  - 文字转语音（TTS）：Index TTS 服务（或 Mock）
  - 静态资源：通过 FastAPI `StaticFiles` 挂载 `/static`，用于提供音频与图片访问

- 运行与部署
  - Docker：前后端均提供 Dockerfile
  - `docker-compose.yml`：用于编排前端、后端及依赖服务
  - Makefile：封装了一些常用开发命令（可自行扩展）

---

## 4. 快速开始

以下步骤默认在项目根目录 `guanhuai2/` 中执行。

### 4.1 环境准备

- 必需软件：
  - Node.js（建议 18+）
  - Python（建议 3.10+）
  - Docker 与 docker-compose（可选，用于一键启动）
  - 一个可用的数据库（根据 `DATABASE_URL` 配置，通常为 PostgreSQL）
- 必需账号：
  - OpenAI API Key（如需使用真实 STT/LLM）
  - Index TTS 服务地址与权限（如需使用真实声音克隆）

### 4.2 配置环境变量

1. 在项目根目录复制环境变量模板：

   ```bash
   cp .env.example .env
   ```

2. 根据实际情况修改 `.env` 中的配置，主要包括：
   - `SECRET_KEY`：JWT 用的密钥
   - `DATABASE_URL`：数据库连接串
   - `REDIS_URL`：如有使用 Redis 的连接串
   - `OPENAI_API_KEY`：OpenAI 的 API Key  
   - `INDEXTTS_BASE_URL`：Index TTS 服务的基础 URL  
     - 使用包含 `mock` 的地址（默认）时，系统会使用 MockTTS，生成静音 wav 方便调试

后端会自动尝试从：
- 当前工作目录 `.env`
- 按路径推导的项目根目录 `.env`

中加载配置。

### 4.3 启动后端（FastAPI）

1. 安装依赖：

   ```bash
   cd backend
   pip install -r requirements.txt
   # 或使用 Poetry：根据 pyproject.toml 自行配置
   ```

2. 初始化数据库（以 Alembic 为例）：

   ```bash
   alembic upgrade head
   ```

3. 运行后端服务：

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   默认将暴露：
   - API 根路径：`/api/v1`
   - OpenAPI 文档：`/api/v1/openapi.json`

### 4.4 启动前端（Vue + Vite）

1. 安装依赖：

   ```bash
   cd frontend
   npm install
   # 或 pnpm install / yarn install
   ```

2. 启动开发服务器：

   ```bash
   npm run dev
   ```

3. 默认访问地址（视 Vite 配置而定）：
   - 前端：`http://localhost:5173`（或控制台输出端口）
   - 后端 API：`http://localhost:8000`

前端通过 `/api` 代理访问后端（具体代理配置见 `vite.config.ts` 或 nginx 配置）。

### 4.5 使用方式概览

1. 注册 / 登录账号（前端 Login 页面）  
2. 前往联系人页面，创建新的 Persona：
   - 填写姓名、关系、称呼方式
   - 上传头像（可选）
   - 上传语音样本文件，并勾选“我确认拥有合法权利克隆该声音”
3. 等待后端调用 Index TTS 完成声音克隆（状态从 `processing` 变为 `ready`）  
4. 进入对应 Persona 的聊天界面：
   - 按住底部“Hold to Speak”按钮说话
   - 松开后发送语音，等待 AI 以该声音生成语音回复
   - 在对话中可看到情绪标签（tone）和文字内容

---

## 5. 目录结构概览

```text
guanhuai2/
├── backend/                 # FastAPI 后端服务
│   ├── app/
│   │   ├── api/v1/          # 认证、Persona、聊天相关 API
│   │   ├── core/            # 配置、日志、数据库、安全相关
│   │   ├── models/          # SQLAlchemy 模型（User / Persona / Conversation / Message 等）
│   │   ├── schemas/         # Pydantic 模型
│   │   └── services/        # STT / TTS / LLM 服务封装
│   ├── alembic/             # 数据库迁移
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── requirements.txt
│
├── frontend/                # Vue 3 前端应用
│   ├── src/
│   │   ├── views/           # 页面组件（Chat, Contacts, PersonaCreate, Login 等）
│   │   ├── router/          # 路由配置
│   │   ├── stores/          # Pinia 状态（auth）
│   │   ├── App.vue
│   │   └── main.ts
│   ├── Dockerfile
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
│
├── .env.example             # 环境变量示例
├── docker-compose.yml       # 前后端及依赖编排
├── Makefile                 # 常用命令脚手架
└── README.md
```

---

## 6. 后续规划

可以根据实际产品需求，继续在以下方向演进：
- 聊天体验
  - 增加文本输入模式（文字 + 语音混合聊天）
  - 支持长对话上下文记忆与多轮情绪追踪
  - 聊天记录存档、搜索与回放
- 声音与隐私
  - 更细粒度的同意与授权管理
  - 更完善的风控与滥用检测机制
- 多端支持
  - PWA / 移动端原生封装
  - 桌面端客户端
- 部署与运维
  - 完善 CI/CD 流程与监控报警
  - 支持多环境配置（开发 / 测试 / 生产）

如果你有更具体的产品设想（例如：主打“亲情陪伴”、面向心理咨询、或企业关怀场景），可以告诉我，我可以再帮你把 README 的“项目简介”和“核心功能”部分写得更贴近目标用户与应用场景。
