# 阶段 5：开发实现 — 工程团队

**角色**：vibe-frontend-engineer + vibe-backend-engineer + vibe-ai-llm-engineer
**任务**：按架构 Spec 开发前端、后端和 AI 集成

---

## 开发分工

| 子任务 | 负责角色 | 文件 |
|--------|---------|------|
| 前端开发 | vibe-frontend-engineer | `frontend/` |
| 后端开发 | vibe-backend-engineer | `backend/main.py` |
| AI 集成 | vibe-ai-llm-engineer | `backend/main.py` (AI 部分) |

---

## 前端开发 — vibe-frontend-engineer

使用 Next.js 15 + Tailwind CSS + shadcn/ui 构建：

- `package.json`：项目依赖配置
- `tailwind.config.ts`：设计 Token（slate 配色系统）
- `Dockerfile`：前端容器化配置

核心组件（实际开发中会创建）：
- `NoteInput.tsx`：笔记输入框，支持自然语言输入
- `NoteCard.tsx`：笔记卡片，展示摘要和标签
- `SearchBar.tsx`：语义搜索框，带自然语言提示
- `LoadingSpinner.tsx`：AI 处理状态动画

> **角色使用提示**："请按架构 Spec，用 Next.js 15 + Tailwind 开发 AI Note Assistant 的前端。需要包含笔记输入、列表展示、搜索功能。"

---

## 后端开发 — vibe-backend-engineer

使用 FastAPI + Python 3.11 构建：

- `main.py`：核心 API 服务
  - `POST /api/notes`：创建笔记（调用 AI 生成摘要和标签）
  - `GET /api/notes`：列出笔记
  - `POST /api/notes/search`：语义搜索
  - `GET /health`：健康检查
- `requirements.txt`：Python 依赖
- `Dockerfile`：后端容器化配置

> **角色使用提示**："请用 FastAPI 开发 AI Note Assistant 的后端 API，包含笔记 CRUD 和语义搜索接口。"

---

## AI 集成 — vibe-ai-llm-engineer

在 `main.py` 中集成 OpenAI：

- **摘要生成**：使用 GPT-4，system prompt 要求返回 JSON 格式
- **标签提取**：与摘要一起生成，3-5 个标签
- **语义搜索**：使用 text-embedding-3-small 生成向量（demo 中使用关键词匹配）
- **响应格式**：所有 AI 输出要求结构化 JSON

> **角色使用提示**："请为笔记应用集成 OpenAI API，实现自动摘要、标签提取和语义搜索功能。"

---

## 关键实现决策

1. **数据存储**：demo 使用内存数组，生产环境使用 PostgreSQL + pgvector
2. **AI 调用**：同步调用（demo），生产环境改为异步 + 队列
3. **错误处理**：AI 失败返回 500，前端显示重试按钮
4. **流式响应**：V2 支持 SSE 流式返回 AI 处理结果

---

## 角色协作边界

- **vibe-frontend-engineer** 负责 UI 组件和页面，调用后端 API
- **vibe-backend-engineer** 负责 API 路由、数据库、错误处理
- **vibe-ai-llm-engineer** 负责 AI prompt 设计、模型选择、输出验证

移交至 vibe-qa-automation-engineer 进行质量保障。
