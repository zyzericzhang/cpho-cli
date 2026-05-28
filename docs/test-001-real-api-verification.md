# Test 001 Real API Verification

Date: 2026-05-27
Branch: `codex/phase8-community-errors`
Workspace: `/Users/ericzhang/Desktop/cpho-cli-verification-001/workspace`
Artifacts root: `/Users/ericzhang/Desktop/cpho-cli-verification-001`

Secrets: not printed; temporary configs use `OPENROUTER_API_KEY` env reference only.

Models used:

- `google/gemini-2.0-flash-lite-001` for index and first normalize attempt.
- `openai/gpt-4o-mini` for solve retry, explain, probe, and model-panel checks.

Real source files sampled from `/Users/ericzhang/Desktop/物理竞赛资料`:

- `2023机构卷/2023北斗学友暑假/力学1试题.pdf`
- `2023机构卷/2023北斗学友暑假/力学1解析.pdf`
- `2023机构卷/2023北斗学友暑假/力学2试题.pdf`

## 01-index-build-vision

- 测试状态: 已测试
- 成功状态: 成功
- 描述: 使用真实 OpenRouter API 和 `--vision` 构建小 workspace 索引。首轮扫描 1 个真实单页 PDF/解析 pair，生成 1 道题；补充第二个真实 PDF 后增量索引成功。
- 产出位置:
  - `/Users/ericzhang/Desktop/cpho-cli-verification-001/workspace/.cpho/index.jsonl`
  - `/Users/ericzhang/Desktop/cpho-cli-verification-001/workspace/.cpho/run-trace.jsonl`
  - `/Users/ericzhang/Desktop/cpho-cli-verification-001/workspace/.cpho/vocabulary/pending.yml`
- 备注: 第二轮增量索引把 workspace 内 compose artifact PDF 也扫入索引，说明用户输出目录放在 workspace 内时会污染 index。

## 02-solve-real-api

- 测试状态: 已测试
- 成功状态: 不成功
- 描述: `cpho solve` 使用真实 PDF 和真实解析。`google/gemini-2.0-flash-lite-001` 与 `openai/gpt-4o-mini` 均在 `extract_official_steps` 失败，错误为返回内容不是可直接 `json.loads` 的 JSON。
- 产出位置:
  - 失败尝试目录: `/Users/ericzhang/Desktop/cpho-cli-verification-001/artifacts/01-solve`
  - 失败重试目录: `/Users/ericzhang/Desktop/cpho-cli-verification-001/artifacts/01-solve-gpt`
- 问题: 中间 step 只靠 prompt 要求 JSON，模型返回 fenced JSON 时运行时不会剥离代码块。

## 03-knowledge-normalize-real-api

- 测试状态: 已测试
- 成功状态: 不成功
- 描述: `cpho knowledge normalize` 使用真实 OpenRouter API 标准化 markdown 知识笔记。模型返回 fenced JSON，当前代码直接 `json.loads` 导致失败。
- 产出位置:
  - source: `/Users/ericzhang/Desktop/cpho-cli-verification-001/workspace/knowledge-source.md`
- 问题: 与 solve 同类，需要统一 JSON 提取/解析。

## 04-knowledge-dry-publish-find

- 测试状态: 已测试
- 成功状态: 成功
- 描述: 使用 `--dry-run` 生成 draft，发布到 private knowledge，再用 indexed problem id 查找。`knowledge find` 返回 private knowledge，match_kind 为 `same_category`。
- 产出位置:
  - draft: `/Users/ericzhang/Desktop/cpho-cli-verification-001/workspace/.cpho/knowledge/drafts/20260527162455-knowledge-source.md`
  - published: `/Users/ericzhang/Desktop/cpho-cli-verification-001/workspace/.cpho/knowledge/files/published/20260527162455-knowledge-source.md`

## 05-explain-panels-with-knowledge

- 测试状态: 已测试
- 成功状态: 成功
- 描述: 通过 core explain 跑真实 streaming API，选择 `approach` + `answer_replacement` 两个 panel，并注入 private knowledge 来源。
- 产出位置:
  - `/Users/ericzhang/Desktop/cpho-cli-verification-001/workspace/artifacts/04-explain/explain/ff4fb3f28b71e30ccb6a9c48f585786f876fa2e8f4f816e3f89ef3564bc4a1eb_01.explain.md`

## 06-probe-real-api

- 测试状态: 已测试
- 成功状态: 成功
- 描述: 通过 core probe 跑真实 API，max_rounds=1，模型生成一个追问并写出 probe markdown。
- 产出位置:
  - `/Users/ericzhang/Desktop/cpho-cli-verification-001/workspace/artifacts/05-probe/probe/ff4fb3f28b71e30ccb6a9c48f585786f876fa2e8f4f816e3f89ef3564bc4a1eb_01.probe.md`

## 07-related-search

- 测试状态: 已测试
- 成功状态: 成功
- 描述: 使用真实索引结果查找相关题，返回 2 条结果并写出 markdown。
- 产出位置:
  - `/Users/ericzhang/Desktop/cpho-cli-verification-001/workspace/artifacts/03-related/related/ff4fb3f28b71e30ccb6a9c48f585786f876fa2e8f4f816e3f89ef3564bc4a1eb_01.related.md`
- 备注: 第一条相关题来自 compose artifact 被误索引，需修复输出目录污染或默认忽略 artifacts。

## 08-topic-browse

- 测试状态: 已测试
- 成功状态: 成功
- 描述: `cpho topic browse 力学/运动学 <workspace>` 返回 1 道题。
- 产出位置:
  - stdout only
- 备注: `--workspace` 参数尝试失败；当前 CLI 使用位置参数，docs/user 需要保持准确。

## 09-compose-build

- 测试状态: 已测试
- 成功状态: 成功
- 描述: `compose new` 创建 YAML；修正 slot 后 `compose build` 生成题目卷和答案卷。
- 产出位置:
  - `/Users/ericzhang/Desktop/cpho-cli-verification-001/workspace/.cpho/compositions/verification.yml`
  - `/Users/ericzhang/Desktop/cpho-cli-verification-001/workspace/artifacts/02-compose/verification-题目.pdf`
  - `/Users/ericzhang/Desktop/cpho-cli-verification-001/workspace/artifacts/02-compose/verification-答案.pdf`
- 备注: 输出到 workspace 外被 boundary 拒绝；输出到 workspace 内又会被 index 扫描。

## 10-model-panel-and-model-refresh

- 测试状态: 已测试
- 成功状态: 成功
- 描述: REPL command handler 跑 `/skill panel solve`、`/skill set-model solve extract_official_steps openai/gpt-4o-mini`、`/model refresh`。真实 OpenRouter model list 返回 355 个 live models。
- 产出位置:
  - `/Users/ericzhang/Desktop/cpho-cli-verification-001/workspace/.cpho/skills/solve.yml`
  - `~/.cache/cpho/models/openrouter.json`

## 11-repl-start-help

- 测试状态: 已测试
- 成功状态: 成功
- 描述: `cpho repl` 可启动并显示 `/help`。stdin EOF 后进程退出。
- 产出位置:
  - stdout only
- 备注: `/exit` 是未知命令；如果文档提到 `/exit`，需要修正为 EOF/Ctrl-D 或实现退出命令。

## 12-community-kb-sync

- 测试状态: 未测试
- 成功状态: 不成功
- 描述: 第一轮真实 API verification 没有可用的 pinned GitHub community KB release 配置；Phase 8 单元和 acceptance 已用 MockTransport 覆盖成功路径，但本轮未进行真实 GitHub release tarball 成功同步。
- 产出位置:
  - 无

## 13-ci-regression

- 测试状态: 已测试
- 成功状态: 成功
- 描述: Phase 8 完成后全量本地 CI 已通过。
- 产出位置:
  - `docs/phase8-verification.md`
- 结果:
  - `uv run pytest -q`: 452 passed, 5 PyMuPDF/SWIG warnings
  - `uv run ruff check .`: All checks passed

## Summary

本轮未通过项:

1. `solve` real API: fenced JSON/非严格 JSON 导致中间 step 失败。
2. `knowledge normalize` real API: fenced JSON 导致失败。
3. community KB sync: 缺少真实 pinned GitHub release 测试源，未测试成功路径。

需要修复项:

1. 增加统一 JSON 提取函数，接受 fenced JSON，同时保持严格 dict/schema 校验。
2. 防止 index 扫描用户生成 artifacts 或至少文档化并默认输出到 `.cpho/outputs` 等可忽略目录。
3. 校准 docs/user 中 `topic browse` workspace 参数与 REPL 退出方式。

