# MyQAsystem

基于 RAG 的私有化部署知识库系统，所有文档、向量数据、对话数据均保留本地，模型可以api调用，
可管理知识库、文档上传与分块、混合检索。项目采用前后端分离架构，前端基于 Vue 3，后端基于 FastAPI，使用 SQLite 轻量化数据库在本机运行。

## 功能简介

- 知识库管理：创建、编辑、删除知识库，配置 Embedding 模型、分块大小和重叠参数。
- 支持多格式文档自动入库：`pdf`、`csv`、`txt`、`md`、`docx`、`doc`。
- 文档管理：支持增量更新、文档删除、智能解析查看状态和错误信息。
- 文档分块：多种分块方式，普通分块、父子分块等。
- 混合检索：基于 `BAAI/bge-m3` 的向量检索。
- RAG 对话：基于知识库的自然语言单轮/多轮对话，回答来源标注，会话管理。
- LLM 配置管理：支持 OpenAI、DeepSeek、Ollama 及 OpenAI 兼容接口。
- MCP 接口：配置 `/mcp` 路由，方便扩展。

## 技术栈

- 前端：Vue 3、Vite、Vue Router
- 后端：FastAPI、SQLAlchemy、Uvicorn、Pydantic
- 数据库：SQLite
- 向量库：Milvus Lite
- Embedding：`BAAI/bge-m3`
- LLM 网关：LiteLLM

## 项目结构

```text
RAG-Pro/
├─ backend/                # FastAPI 后端
│  ├─ app/                 # API、核心逻辑、数据模型
│  ├─ data/                # SQLite 本地数据
│  ├─ models/              # 本地模型目录
│  ├─ uploads/             # 上传文件目录
│  ├─ requirements.txt
│  └─ start_backend.py
├─ frontend/               # Vue 3 前端
│  ├─ src/
│  ├─ package.json
│  └─ vite.config.js
├─ docs/                   # 使用文档
├─ sample-data/            # 测试数据
├─ install.bat             # 安装必要环境和依赖
├─ start.bat               # 启动前后端
└─ docker-compose.yml      # Docker
```

## 运行环境

- Python 3.10 及以上
- Node.js 18 及以上
- npm 9 及以上


## 系统部署

#### 1. 启动后端

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt -i https://pypi.org/simple
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

后端数据库默认使用：

- SQLite：`backend/data/ragapp.db`

#### 2. 启动前端

```powershell
cd frontend
npm install
npm run dev
```

前端 Vite 默认运行在 `3000` 端口，并将 `/api` 请求代理到 `http://localhost:8000`。

启动后默认地址：

- 前端：`http://localhost:3000`
- 后端：`http://localhost:8000`
- Swagger 文档：`http://localhost:8000/docs`



## 初始配置

### 1. 配置 LLM

进入前端 `设置` 页面，添加一个可用模型配置。

如：

- OpenAI
  - `provider`: `openai`
  - `model_name`: `gpt-4o`
  - `api_key`: 你的 API Key
- Ollama
  - `provider`: `ollama`
  - `model_name`: `qwen2.5:7b`
  - `base_url`: `http://localhost:11434`

后端接口：

- `POST /api/v1/llm/configs`
- `POST /api/v1/llm/configs/test`

### 2. 创建知识库

进入 `知识库` 页面，创建知识库并设置：

- 名称与描述
- Embedding 模型
- `chunk_size`
- `chunk_overlap`

后端接口：

- `POST /api/v1/kb`
- `GET /api/v1/kb`

### 3. 上传文档

进入某个知识库的文档页，上传文档。系统会先完成解析，再进入分块阶段。

后端接口：

- `POST /api/v1/kb/{kb_id}/documents`
- `GET /api/v1/kb/{kb_id}/documents`
- `GET /api/v1/kb/{kb_id}/documents/{doc_id}/status`

### 4. 执行分块

文档解析成功后，可对单个文档或批量文档执行分块。

后端接口：

- `POST /api/v1/kb/{kb_id}/documents/{doc_id}/chunk`
- `POST /api/v1/kb/{kb_id}/documents/chunk-batch`

### 5. 开始问答

进入 `聊天` 页面进行知识库问答，支持流式 SSE 返回和多轮会话。

后端接口：

- `POST /api/v1/chat`
- `GET /api/v1/conversations`
- `GET /api/v1/conversations/{conversation_id}`


## 关键配置

后端配置位于 `backend/app/config.py`，也支持通过 `backend/.env` 覆盖。

常用配置项：

```env
APP_NAME=RAG Knowledge Base
APP_VERSION=1.0.0
API_PREFIX=/api/v1

HOST=0.0.0.0
PORT=8000

DATABASE_URL=sqlite+aiosqlite:///backend/data/ragapp.db
REDIS_URL=redis://localhost:6379/0

MILVUS_URI=backend/data/milvus.db
MILVUS_HOST=localhost
MILVUS_PORT=19530

UPLOAD_DIR=backend/uploads
MAX_UPLOAD_SIZE_MB=100

DEFAULT_EMBEDDING_MODEL=BAAI/bge-m3
DEFAULT_RERANKER_MODEL=BAAI/bge-reranker-v2-m3
EMBEDDING_DEVICE=cpu

RETRIEVAL_TOP_K=20
RERANK_TOP_N=5
CONFIDENCE_THRESHOLD=0.3

DEFAULT_CHUNK_SIZE=512
DEFAULT_CHUNK_OVERLAP=64
PARENT_CHUNK_SIZE=1536

SECRET_KEY=change-this-to-a-secure-random-string
DEBUG=false
```

说明：

- 本地开发默认使用 SQLite，无需额外搭建数据库。
- `EMBEDDING_DEVICE=cpu` 适合默认本地运行；如有 CUDA 环境，可改为 `cuda`。
- 项目会将 Hugging Face 模型缓存目录指向 `backend/models`。

## 常用接口

### 健康检查

- `GET /health`

### 知识库

- `GET /api/v1/kb`
- `POST /api/v1/kb`
- `GET /api/v1/kb/{kb_id}`
- `PUT /api/v1/kb/{kb_id}`
- `DELETE /api/v1/kb/{kb_id}`

### 文档

- `GET /api/v1/kb/{kb_id}/documents`
- `POST /api/v1/kb/{kb_id}/documents`
- `POST /api/v1/kb/{kb_id}/documents/{doc_id}/chunk`
- `POST /api/v1/kb/{kb_id}/documents/chunk-batch`
- `GET /api/v1/kb/{kb_id}/documents/{doc_id}/chunks`
- `DELETE /api/v1/kb/{kb_id}/documents/{doc_id}`

### 问答与会话

- `POST /api/v1/chat`
- `GET /api/v1/conversations`
- `GET /api/v1/conversations/{conversation_id}`
- `PUT /api/v1/conversations/{conversation_id}`
- `DELETE /api/v1/conversations/{conversation_id}`

### 模型配置

- `GET /api/v1/llm/configs`
- `POST /api/v1/llm/configs`
- `PUT /api/v1/llm/configs/{config_id}`
- `DELETE /api/v1/llm/configs/{config_id}`
- `POST /api/v1/llm/configs/test`
