# AI 智能笔记助手 — 示例项目

这是一个端到端的 Vibe Coding 示例项目，展示 21 个 AI-Native 智能体如何协作，从趋势研究到产品部署的完整链路。

## 项目简介

**AI Note Assistant** 是一个 AI 驱动的智能笔记应用，用户可以用自然语言记录笔记，AI 自动提取关键信息、打标签、生成摘要，并支持语义搜索。

## 协作流程

本项目展示了 8 个阶段的完整协作：

| 阶段 | 角色 | 产出 |
|------|------|------|
| 1 趋势研究 | vibe-trend-researcher | 趋势分析报告 |
| 2 产品定义 | product-manager | 产品 Spec + RICE-V 评分 |
| 3 原型验证 | vibe-prototyper | 交互原型 + 验证报告 |
| 4 技术架构 | vibe-architect | 架构 Spec + 基础设施配置 |
| 5 开发实现 | vibe-frontend-engineer / vibe-backend-engineer / vibe-ai-llm-engineer | 前端 + 后端 + AI 代码 |
| 6 质量保障 | vibe-qa-automation-engineer | 自动化测试套件 |
| 7 部署运维 | vibe-devops-engineer | Dockerfile + CI/CD + 部署 |
| 8 文档交付 | vibe-tech-writer | API 文档 + 开发者指南 |

## 如何使用本示例

1. 按阶段顺序阅读每个目录的 README.md
2. 查看每个角色的实际产出文件（Spec、代码、配置）
3. 理解多角色协作的边界和交接方式
4. 将流程复用到你自己的项目中

## 技术栈

- 前端：Next.js 15 + Tailwind CSS + shadcn/ui
- 后端：FastAPI + Python 3.11
- AI：OpenAI GPT-4 + text-embedding-3-small
- 数据库：PostgreSQL + pgvector
- 部署：Docker + Docker Compose
- 测试：Playwright + Pytest

## 快速启动

```bash
cd examples/ai-note-assistant
# 使用 Docker Compose 一键启动
docker-compose up -d
# 访问 http://localhost:3000
```
