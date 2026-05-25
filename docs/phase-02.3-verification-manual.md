# Phase 02.3 验证手册

本文记录 Phase 02.3 的人工/自动验证方法。原始证据保存在 `.planning/verification/02.3-real-workspace/TRANSCRIPT.md`，真实工作区副本保存在 `.planning/verification/02.3-real-workspace/sample-workspace/`。

## 阶段目标

Phase 02.3 验证以下结论：

- `index` 不再依赖 `SolveReport`，默认只用 OCR 文本和 vocabulary 做标签归一化。
- `solve` 降级为 builtin skill，通过 `SkillRuntime` 执行。
- 删除旧的 eval/golden 框架。
- `index` 提供 tag-add/tag-set/tag-remove 写 API，并记录 provenance。
- `solve` 和 opt-in 的 `index --vision` 支持多模态输入；默认仍为 OCR 路径。

## CLI 功能验证

基础命令：

```bash
uv run pytest
uv run cpho --help
uv run cpho index --help
uv run cpho index tag-add --help
uv run cpho index tag-remove --help
uv run cpho index tag-set --help
uv run cpho solve --help
uv run cpho repl --help
```

真实工作区副本上的 index 验证：

```bash
uv run cpho index .planning/verification/02.3-real-workspace/sample-workspace --force --ocr-strategy reuse --quiet
```

tag 写入验证使用 `sample-workspace/.cpho/index.jsonl` 中的真实 `problem_id`：

```bash
uv run cpho index tag-add --workspace .planning/verification/02.3-real-workspace/sample-workspace --problem-id <problem_id> --tag energy_conservation --skill-name verification --reasoning 验证追加
uv run cpho index tag-set --workspace .planning/verification/02.3-real-workspace/sample-workspace --problem-id <problem_id> --tag free_body_diagram --skill-name verification --reasoning 验证替换
uv run cpho index tag-remove --workspace .planning/verification/02.3-real-workspace/sample-workspace --problem-id <problem_id> --tag free_body_diagram
```

`--vision` 验证重点：

- `uv run cpho index --help` 必须显示 `--vision`。
- help 文案必须说明默认使用 OCR，开启后可能上传 PDF/图片到 provider。
- 不传 `--vision` 时，默认索引路径仍是 OCR-only。

`solve` 验证：

```bash
uv run cpho solve <problem.pdf> --answer <answer.pdf> --dry-run
```

如果运行非 dry-run 并遇到 provider/billing 错误，按 `TRANSCRIPT.md` 记录处理。本轮真实 provider 返回 OpenRouter 402，原因是文件请求余额不足；这不是代码失败。

## REPL 功能验证

自动化测试：

```bash
uv run pytest tests/test_repl_commands.py tests/test_repl_workspace_commands.py -x
```

手动 REPL 检查：

```text
/status
/set provider <profile-name>
/index --all --dry-run
/index --all --vision
/index --all --force-all
```

检查点：

- `/index` 会先 dry-run preview，再确认真实执行。
- `/index --vision` 只在显式传入时启用。
- `/set provider` 后，`SessionState.model_capabilities` 会刷新。
- capability 检测失败时，REPL 不崩溃，降级为 text-only，并显示中文警告。

## 真实工作区样本

样本来自 `/Users/ericzhang/Desktop/物理竞赛资料`，复制到：

```text
.planning/verification/02.3-real-workspace/sample-workspace/
```

本轮样本：

- `2023机构卷/2023北斗学友暑假/力学2试题.pdf`
- `2023机构卷/2023北斗学友暑假/力学2解析.pdf`
- `2023机构卷/2023学而思物理复赛营/mmexport1690538958488.jpg`

保留产物：

- `.planning/verification/02.3-real-workspace/sample-workspace/.cpho/index.jsonl`
- `.planning/verification/02.3-real-workspace/sample-workspace/.cpho/cache/ocr/`
- `.planning/verification/02.3-real-workspace/sample-workspace/.cpho/run-trace.jsonl`
- `.planning/verification/02.3-real-workspace/solve-output-fake/`

不要把验证命令直接跑在原始 `/Users/ericzhang/Desktop/物理竞赛资料` 上。

## 失败修复记录

本轮唯一代码/测试修复：

- 失败命令：`uv run pytest`
- 失败文件：`tests/test_index_ocr_upgrade.py`
- 原因：测试 fixture 仍硬编码旧 `tag_schema_version="v2"`，Phase 02.3 已升级为 `TAG_SCHEMA_VERSION="v3"`。
- 修复：测试改为导入并使用当前 `TAG_SCHEMA_VERSION`。
- 复验：`uv run pytest tests/test_index_ocr_upgrade.py -x` 和 `uv run pytest` 均通过。

非代码阻塞：

- `uv run cpho solve <pdf> --answer <pdf>` 触发 OpenRouter 文件请求，返回 402，提示文件请求需要余额。
- 处理：记录在 `TRANSCRIPT.md`；继续执行 `--dry-run` 和 fake-provider solve artifact 验证。

## 索引与 provenance 检查

打开 `sample-workspace/.cpho/index.jsonl`，检查：

- `solve_report_path` 不存在。
- `user_tags` 与 LLM 机打标签分离。
- `user_tags[*].skill_name`、`timestamp`、`reasoning_snippet` 存在。
- `canonical_tags` 记录匹配 vocabulary 的标签。
- `unverified_tags` 记录未匹配 vocabulary 的标签。

`--force` 应保留 `user_tags`；`--force-all` 才清空 skill/用户写入标签。

## 提示词调整笔记

这不是 eval 框架，只是人工校验输出质量后的调整入口。

可调整文件：

- `src/cpho_cli/builtin_skills/solve/prompts/normalize.md.j2`
- `src/cpho_cli/builtin_skills/solve/prompts/answer_structure.md.j2`
- `src/cpho_cli/builtin_skills/solve/prompts/derive.md.j2`
- `src/cpho_cli/builtin_skills/solve/prompts/cross_check.md.j2`
- `src/cpho_cli/builtin_skills/solve/prompts/discrepancies.md.j2`
- `src/cpho_cli/builtin_skills/solve/prompts/final_report.md.j2`
- `src/cpho_cli/core/index/prompts/tag_refinement.md.j2`
- `src/cpho_cli/core/index/prompts/topic_assignment.md.j2`

调整原则：

- 保持输出 JSON schema 不变。
- 不允许提示词要求模型编造 vocabulary 外的 canonical id。
- 若真实输出标签过多，优先收紧 `tag_refinement.md.j2` 的选择数量/置信条件。
- 若 solve 推导缺少“为什么想到这一步”，优先加强 `derive.md.j2` 和 `final_report.md.j2`。
- 修改提示词后必须重跑相关测试和真实副本 smoke：

```bash
uv run pytest tests/test_index_tagging.py tests/test_solve.py tests/test_phase023_acceptance.py -x
uv run cpho index .planning/verification/02.3-real-workspace/sample-workspace --force --ocr-strategy reuse --quiet
```

详细命令和本轮产物见 `.planning/verification/02.3-real-workspace/TRANSCRIPT.md`。
