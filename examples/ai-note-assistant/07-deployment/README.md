# 阶段 7：部署运维 — vibe-devops-engineer

**角色**：vibe-devops-engineer
**任务**：Docker 容器化、CI/CD 配置、部署脚本

---

## 部署架构

```
[Docker Compose]
├── frontend (Next.js, port 3000)
├── backend (FastAPI, port 8000)
└── db (PostgreSQL + pgvector, port 5432)
```

---

## 配置文件

### `docker-compose.yml`

定义三个服务：
- **frontend**：Next.js 应用，端口 3000
- **backend**：FastAPI 应用，端口 8000，依赖 db
- **db**：PostgreSQL + pgvector，端口 5432，数据持久化

### `frontend/Dockerfile`

基于 `node:20-alpine`，构建并运行 Next.js 应用。

### `backend/Dockerfile`

基于 `python:3.11-slim`，安装依赖并运行 uvicorn。

---

## 快速启动

```bash
# 设置 OpenAI API Key
export OPENAI_API_KEY="sk-your-key"

# 启动所有服务
cd examples/ai-note-assistant/07-deployment
docker-compose up -d

# 访问应用
# 前端: http://localhost:3000
# 后端 API: http://localhost:8000
# API 文档: http://localhost:8000/docs
```

---

## 监控配置

| 指标 | 目标 | 告警 |
|------|------|------|
| 后端 P95 延迟 | < 500ms | > 1s |
| 错误率 | < 0.1% | > 1% |
| AI 成本/请求 | <$0.05 | > $0.10 |
| 数据库连接池 | < 80% | > 90% |

---

## 角色使用提示

> "请为 AI Note Assistant 配置 Docker 容器化部署，包含前端、后端、数据库的完整编排。"

移交至 vibe-tech-writer 进行文档交付。
