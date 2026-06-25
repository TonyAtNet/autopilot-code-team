# 阶段 4：技术架构 — vibe-architect

**角色**：vibe-architect
**任务**：设计系统架构、MCP 接口、基础设施配置

---

## 系统架构 Spec：AI Note Assistant

Status: Approved
Last Updated: 2026-06-21  Version: 1.0

---

### 1. 架构概述

```
[用户] -> [Next.js Frontend] -> [FastAPI Backend] -> [OpenAI API]
                                      |
                                      v
                              [PostgreSQL + pgvector]
```

- **前端**：Next.js 15 (App Router) + Tailwind CSS + shadcn/ui
- **后端**：FastAPI + Python 3.11
- **AI**：OpenAI GPT-4 + text-embedding-3-small
- **数据库**：PostgreSQL 15 + pgvector 扩展
- **部署**：Docker + Docker Compose

---

### 2. 组件设计

| 组件 | 技术 | 职责 | 模型风险 | 月成本 |
|------|------|------|----------|--------|
| Web 前端 | Next.js 15 | 用户界面 | 低 | $0 (Vercel Hobby) |
| API 网关 | FastAPI | 路由、鉴权、限流 | 低 | $0 |
| 笔记服务 | FastAPI | CRUD、标签、摘要 | 低 | $0 |
| AI 服务 | FastAPI | 调用 OpenAI API | 中 | ~$50/月 |
| 向量服务 | FastAPI | 嵌入生成、语义搜索 | 中 | ~$20/月 |
| 数据库 | PostgreSQL + pgvector | 数据存储、向量索引 | 低 | $0 (本地) |

---

### 3. 数据模型

```sql
-- 笔记表
CREATE TABLE notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    content TEXT NOT NULL,
    summary TEXT,
    tags TEXT[],
    embedding VECTOR(1536),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 向量索引
CREATE INDEX idx_notes_embedding ON notes USING hnsw (embedding vector_cosine_ops);

-- 用户表
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

### 4. MCP 设计

```typescript
// MCP Server: note-assistant
interface NoteAssistantMCP {
  name: "note-assistant";
  tools: [
    {
      name: "create_note",
      description: "创建一条新笔记",
      parameters: {
        content: string;
        user_id: string;
      }
    },
    {
      name: "search_notes",
      description: "语义搜索笔记",
      parameters: {
        query: string;
        user_id: string;
        limit?: number;
      }
    },
    {
      name: "get_note_summary",
      description: "获取笔记摘要",
      parameters: {
        note_id: string;
      }
    }
  ];
}
```

---

### 5. 模型依赖风险

| 模型 | 用途 | 可替代性 | 回退方案 | 移除影响 |
|------|------|----------|----------|----------|
| GPT-4 | 摘要生成、标签提取 | 中 | Claude 3.5 | 质量下降 10% |
| text-embedding-3-small | 语义搜索 | 高 | 本地模型 | 成本上升但可用 |

---

### 6. 基础设施配置

```terraform
# 生产环境：暂用 Docker Compose，后续迁移至 Kubernetes
# terraform/main.tf

# 本地开发：Docker Compose
# docker-compose.yml 见 07-deployment/
```

---

## ADR-001：技术栈选择

**问题**：选择什么技术栈？

**选项**：
- A: Next.js + FastAPI + PostgreSQL（选择）
- B: React + Express + MongoDB
- C: Vue + Django + MySQL

**决策**：选择 A，因为：
1. Next.js 支持 AI 流式响应（Server-Sent Events）
2. FastAPI 原生支持异步 OpenAI API 调用
3. PostgreSQL + pgvector 是最成熟的向量数据库方案

---

## 角色使用提示

> "请为 AI Note Assistant 设计系统架构，包括组件选择、数据模型、MCP 接口和模型依赖风险评估。"

vibe-architect 输出此 Spec 后，移交至开发团队（vibe-frontend-engineer + vibe-backend-engineer + vibe-ai-llm-engineer）。
