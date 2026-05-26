# Phase 2 手动操作指南

Phase 2（Tag Indexing）的所有代码已自动完成。本文档列出需要你**手动完成**的操作步骤。

---

## 1. 确认 API Key 配置

索引命令需要调用 LLM（通过 OpenRouter）进行标签提取和主题分类。

**检查现有配置：**

```bash
cat config.local.yml
```

确认 `provider.openrouter_api_key` 已填入有效的 OpenRouter API key。如果需要更换：

```yaml
# config.local.yml
provider:
  openrouter_api_key: "sk-or-v1-你的key"
```

或通过环境变量：

```bash
export OPENROUTER_API_KEY="sk-or-v1-你的key"
```

> **安全提醒：** `config.local.yml` 已在 `.gitignore` 中，不会被提交。不要将 API key 写入其他文件。

---

## 2. 首次运行 `cpho index`

### 2.1 准备工作空间

将你的物理竞赛题目 PDF/图片放入一个目录：

```
/path/to/your/workspace/
├── problem_1.pdf
├── problem_1-answer.pdf    # answer key（命名匹配: {name}-answer.{ext}）
├── problem_2.png
├── problem_2-answer.png
└── ...
```

命名规则：
- 题目文件：`{name}.{pdf|png|jpg|jpeg}`
- 答案文件：`{name}-answer.{ext}`（自动配对）
- 没有答案文件的题目也会被索引，但标签质量可能降低

### 2.2 Dry-run 验证

先验证 workspace 结构和词表是否正常（不调用 LLM、不写文件）：

```bash
uv run cpho index /path/to/your/workspace --dry-run
```

应看到 `扫描题目数: N` 的输出，所有计数器为 0。

### 2.3 正式索引

```bash
uv run cpho index /path/to/your/workspace
```

输出示例：

```
索引统计 (workspace: /path/to/your/workspace)
─────────────────────────
扫描题目数:        5
  文件变化:        5
  无变化:          0

OCR 复用:          0
OCR 重生成:        5
OCR 引擎升级:      未检测到

标签层:
  重新生成:        5
  跳过 (fingerprint): 0
  精炼层 (用户笔记):  0

候选词表:
  本次新提议:      3
  累计待审:        3  (运行 `cpho index --list-candidates` 查看)

完成. 索引: /path/to/your/workspace/.cpho/index.jsonl
```

### 2.4 验证索引结果

```bash
# 查看生成的索引文件
head -1 /path/to/your/workspace/.cpho/index.jsonl | python -m json.tool

# 验证增量更新：再跑一次，应全部跳过
uv run cpho index /path/to/your/workspace
# 预期: tags_skipped == N, tags_regenerated == 0
```

---

## 3. 主题分类浏览

### 3.1 查看主题树

```bash
uv run cpho topic list
```

输出内置的 5 大主题分类树（力学、热学、电磁学、光学、近代物理），2-3 层深度。

### 3.2 按主题浏览题目

```bash
# 所有力学题目
uv run cpho topic browse 力学 /path/to/your/workspace

# 天体运动子主题
uv run cpho topic browse 力学/天体运动 /path/to/your/workspace
```

### 3.3 组卷（按主题+标签筛选）

```bash
# 按主题筛选
uv run cpho compose --topic 力学/天体运动 /path/to/your/workspace

# 按标签筛选
uv run cpho compose --tags angular_momentum_conservation,energy_conservation /path/to/your/workspace

# 组合筛选：找所有天体运动且用到角动量守恒的题目
uv run cpho compose --topic 力学/天体运动 --tags angular_momentum_conservation /path/to/your/workspace
```

---

## 4. 候选标签审查

LLM 生成标签时，如果发现与内置词表不匹配的标签，会作为「候选标签」记录。你需要定期审查：

```bash
# 查看候选标签
uv run cpho index /path/to/your/workspace --list-candidates
```

输出格式：`{中文名} ({内部ID建议}) x{出现次数}`

**手动操作：**

1. 出现次数高的候选标签可能值得加入词表
2. 编辑 `src/cpho_cli/vocabulary/builtin.yml` 或对应的 `builtin/*.yml` 子文件
3. 也可以在 workspace 级别覆盖：创建 `/path/to/workspace/.cpho/vocabulary/workspace.yml`

---

## 5. 内置词表审查

Phase 2 生成了 837 个标签（42 个核心 + 扩展板）。建议审查：

```bash
# 查看核心词表
cat src/cpho_cli/vocabulary/builtin.yml

# 查看扩展板
ls src/cpho_cli/vocabulary/builtin/
cat src/cpho_cli/vocabulary/builtin/05_mechanics_advanced.yml

# 查看重复 internal_id 列表（已知问题记录在此）
cat docs/builtin-vocabulary-manual.md
```

**手动操作：**

1. 检查 `docs/builtin-vocabulary-manual.md` 中列出的重复 `internal_id`
2. 对于语义重复的标签，决定保留哪一个并删除另一个
3. 审查中文 `display_zh` 显示名是否准确

---

## 6. 主题分类词表自定义

### 6.1 查看内置主题树

```bash
cat src/cpho_cli/vocabulary/topics/builtin_topics.yml
```

5 个根节点：`mechanics`（力学）、`thermodynamics`（热学）、`electromagnetism`（电磁学）、`optics`（光学）、`modern_physics`（近代物理）。

### 6.2 Workspace 级别覆盖

创建 `.cpho/topics/workspace_topics.yml`：

```yaml
version: "v0.1-custom"
roots:
  - id: mechanics
    display_zh: 力学
    children:
      - id: my_new_subtopic
        display_zh: 我的自定义子主题
        children: []
```

覆盖规则：
- 同 `id` 节点：覆盖 `display_zh`，递归合并 `children`
- 新 `id` 节点：追加
- 不需要写完整树，只写要修改/新增的部分

### 6.3 私有覆盖

`.cpho/topics/private_topics.yml` 结构同上，优先级最高（builtin < workspace < private）。

---

## 7. OCR 引擎升级处理

如果你升级了 `rapidocr-onnxruntime` 版本，再次索引时会触发交互提示：

```
检测到 OCR 引擎变更:
  旧版本: 1.3.22
  新版本: 1.4.0
受影响条目: 15

请选择:
  [a] 重建全部
  [b] 仅重建受影响条目
  [c] 暂时跳过，保持现有 OCR
  [d] 仅索引新增题目，不动旧条目
选择 [a/b/c/d]:
```

建议：
- **大版本升级**（OCR 质量可能明显变化）：选 `a`
- **小版本升级**（patch 级别）：选 `c` 或 `d`
- **想试新版本效果**：选 `b`

也可以跳过交互，直接指定策略：

```bash
uv run cpho index /path/to/workspace --ocr-strategy reuse    # 保持现有
uv run cpho index /path/to/workspace --ocr-strategy rebuild   # 全部重建
uv run cpho index /path/to/workspace --ocr-strategy new-only  # 仅新题
```

---

## 8. Python API 使用（面向 Phase 3 开发）

Phase 2 导出的 API 可直接 import：

```python
from cpho_cli.core.index import (
    # 索引构建
    build_index,
    
    # 查询 API
    query_index,
    get_problem_entry,
    find_related_problems,
    
    # 主题 API
    find_problems_by_topic,
    get_topic_tree,
    compose_problem_list,
    
    # 用户笔记
    get_problem_notes,
    set_problem_notes,
    
    # 词表
    load_vocabulary,
    list_pending_candidates,
)
```

快速验证：

```bash
uv run python -c "
from cpho_cli.core.index import query_index, find_related_problems, get_topic_tree
print('API import OK')
"
```

---

## 9. 用户笔记（错题本数据预留）

Phase 2 实现了数据层（读写 JSON），但没有编辑交互。手动使用：

```python
from pathlib import Path
from datetime import datetime, timezone
from cpho_cli.models.index import UserNotebookEntry
from cpho_cli.core.index import get_problem_notes, set_problem_notes

workspace = Path("/path/to/your/workspace")

# 写入笔记
notes = UserNotebookEntry(
    problem_id="problem_1",
    key_points=["利用角动量守恒求解"],
    stuck_points=["忽略了向心加速度方向"],
    updated_at=datetime.now(timezone.utc),
)
set_problem_notes(workspace, notes)

# 读取笔记
result = get_problem_notes(workspace, "problem_1")
print(result.key_points)
```

笔记存储在 `{workspace}/.cpho/notebook/{problem_id}.json`。

写入笔记后重新索引，`refinement_only` 计数器会增加（不重跑 OCR/LLM，只更新笔记字段）。

---

## 10. 测试验证

确认一切正常：

```bash
# 全量测试（216 个测试，约 7 秒）
uv run pytest -q

# 代码质量
uv run ruff check src/ tests/
uv run mypy src/cpho_cli/

# 确认 solve.py 未被修改（R4 约束）
git diff --name-only src/cpho_cli/core/solve.py
# 应无输出
```

---

## 11. Phase 1 遗留待办

Phase 1 有几项待办尚未完成，建议在进入 Phase 3 前处理：

1. **添加 20-30 道真实物理金牌题目及答案**（golden test set）
2. **运行 `cpho eval golden_tests/`** 验证 Phase 1 pipeline 通过率
3. **验证 RapidOCR 对中文+LaTeX 扫描件的质量**，如果不够好考虑 PaddleOCR fallback

---

## 快速参考

| 命令 | 说明 |
|------|------|
| `cpho index <workspace>` | 索引工作空间 |
| `cpho index <workspace> --dry-run` | 验证 workspace（不调 LLM） |
| `cpho index <workspace> --force` | 强制全量重建 |
| `cpho index <workspace> --only-new` | 仅索引新增题目 |
| `cpho index <workspace> --quiet` | 静默模式 |
| `cpho index <workspace> --list-candidates` | 查看候选标签 |
| `cpho topic list` | 显示主题分类树 |
| `cpho topic browse <路径> <workspace>` | 按主题浏览题目 |
| `cpho compose --topic <路径> --tags <id1,id2> <workspace>` | 组卷筛选 |
| `cpho solve <problem.pdf>` | 解题（Phase 1） |
| `cpho eval <golden_root>` | 评估（Phase 1） |
