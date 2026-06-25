# 阶段 8：文档交付 — vibe-tech-writer

**角色**：vibe-tech-writer
**任务**：输出 API 文档和开发者指南

---

## 文档清单

| 文档 | 文件 | 受众 |
|------|------|------|
| API 参考 | `API.md` | 前端开发者、第三方集成者 |
| 开发者指南 | 本文档 | 新加入的开发者 |
| 部署指南 | `07-deployment/README.md` | 运维工程师 |

---

## API 文档 — `API.md`

包含：
- 基础 URL 和认证说明
- 所有端点的请求/响应格式
- 错误代码表
- 代码示例（curl、Python）
- 变更日志

---

## 开发者快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/TonyAtNet/autopilot-code-team.git
cd examples/ai-note-assistant
```

### 2. 环境配置

```bash
# 后端
cd 05-development/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="sk-your-key"

# 前端
cd ../frontend
npm install
```

### 3. 启动服务

```bash
# 方式一：Docker Compose（推荐）
cd 07-deployment
docker-compose up -d

# 方式二：本地开发
# 终端 1：后端
cd 05-development/backend
uvicorn main:app --reload

# 终端 2：前端
cd 05-development/frontend
npm run dev
```

### 4. 访问应用

- 前端：http://localhost:3000
- 后端 API：http://localhost:8000
- Swagger UI：http://localhost:8000/docs

---

## 文档质量标准

- 所有示例代码可运行（已测试）
- 所有 API 端点有请求/响应示例
- 错误场景有处理说明
- 变更日志及时更新

---

## 角色使用提示

> "请为 AI Note Assistant 编写完整的 API 文档和开发者指南，确保所有示例代码可运行。"

**项目交付完成！**
