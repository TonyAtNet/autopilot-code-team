# 阶段 6：质量保障 — vibe-qa-automation-engineer

**角色**：vibe-qa-automation-engineer
**任务**：构建自动化测试套件，确保代码质量

---

## 测试策略

| 测试层 | 覆盖率目标 | 工具 | 频率 |
|--------|-----------|------|------|
| 单元测试 | > 80% | Pytest | 每次提交 |
| 集成测试 | > 70% | Pytest + TestClient | 每次 PR |
| E2E 测试 | > 50% | Playwright | 每次发布 |
| 安全扫描 | 100% | Snyk | 每次 PR |
| AI 测试 | 100% | 自定义测试 | 每次 PR |

---

## 测试文件：`test_main.py`

使用 Pytest + FastAPI TestClient 构建：

### 测试覆盖

1. **NoteCreation**：
   - `test_create_note_success`：验证 AI 摘要和标签生成
   - `test_create_note_empty_content`：验证空内容拒绝
   - `test_create_note_missing_user_id`：验证缺少用户 ID 拒绝

2. **NoteListing**：
   - `test_list_notes_empty`：空列表返回
   - `test_list_notes_returns_user_notes`：用户数据隔离

3. **NoteSearch**：
   - `test_search_by_keyword`：关键词搜索

4. **Health**：
   - `test_health_check`：健康检查

---

## AI 专项测试

| 测试 | 方法 | 阈值 | 状态 |
|------|------|------|------|
| 摘要质量 | 人工标注 50 条笔记 | 准确率 > 80% | 待执行 |
| 标签相关性 | 用户确认 | 准确率 > 85% | 待执行 |
| 幻觉检测 | 事实检查 | 幻觉率 < 5% | 待执行 |
| 提示注入 | 50 个已知模式 | 拦截率 100% | 待执行 |

---

## 运行测试

```bash
cd examples/ai-note-assistant/05-development/backend
pip install pytest
pytest ../../06-testing/test_main.py -v
```

---

## 角色使用提示

> "请为 AI Note Assistant 构建完整的自动化测试套件，覆盖单元测试、集成测试、AI 专项测试和安全扫描。"

移交至 vibe-devops-engineer 进行部署配置。
