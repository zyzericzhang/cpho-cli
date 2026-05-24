# Phase 02.1 Manual Acceptance Guide

本文说明 Phase 02.1 结束前需要人工确认的验收点，重点是如何在真实资料目录 `/Users/ericzhang/Desktop/物理竞赛资料` 上试跑当前已经实现的试卷切分和索引能力。

## 目标

Phase 02.1 的目标不是把 PDF 物理切成多个小 PDF，而是把一份多题试卷虚拟切分为多个 `ProblemEntry`，再让 `cpho index` 为每道大题写一条索引记录。

人工验收需要确认：

- `cpho index` 能扫描真实资料目录。
- 输出里出现试卷切分统计：`切分试卷数`、`提取题目数`、`规则切分`、`LLM 切分`、`单题路径`。
- `.cpho/index.jsonl` 中每行代表一道题，而不是一份 PDF。
- 多题试卷的 `problems_extracted` 大于 `papers_split`。
- 抽样查看的索引记录包含 `problem_id`、`problem_path`、`problem_page_range`。
- 不需要旧索引迁移；旧 schema 会在重建时丢弃并重新生成。

## 前置检查

在项目根目录运行：

```bash
cd /Users/ericzhang/Desktop/cpho-cli
uv run cpho index --help
uv run pytest tests/test_phase021_acceptance.py -x
```

第二条命令会运行离线验收烟测。当前实现会在真实目录存在时抽样 3 份实际 PDF，但使用 fake OCR/LLM/tagging，避免真实网络调用。

## 配置要求

真实 `cpho index` 会执行 OCR 和 LLM 标签生成。请确认本地有可用配置：

```bash
test -f config.local.yml && sed -n '1,80p' config.local.yml
```

如果配置不在项目根目录，用 `--config` 指向它。若有多个 provider profile，用 `--provider` 指定。

## 推荐试跑命令

先做不写文件的 workspace/vocabulary 烟测：

```bash
uv run cpho index "/Users/ericzhang/Desktop/物理竞赛资料" --dry-run
```

注意：`--dry-run` 不会真正 OCR、切分、标签生成或写 JSONL；它只能证明 workspace 和词表加载没有明显问题。

正式验收使用：

```bash
uv run cpho index "/Users/ericzhang/Desktop/物理竞赛资料" --force --ocr-strategy reuse
```

如果你的配置文件不在默认位置：

```bash
uv run cpho index "/Users/ericzhang/Desktop/物理竞赛资料" \
  --config /path/to/config.local.yml \
  --provider default \
  --force \
  --ocr-strategy reuse
```

这会在真实资料目录下写入或更新：

- `/Users/ericzhang/Desktop/物理竞赛资料/.cpho/index.jsonl`
- `/Users/ericzhang/Desktop/物理竞赛资料/.cpho/ocr-cache/`
- `/Users/ericzhang/Desktop/物理竞赛资料/.cpho/run-trace.jsonl`
- `/Users/ericzhang/Desktop/物理竞赛资料/.cpho/vocabulary/pending.yml`，如果有候选标签

如果不想直接改真实目录，先复制一个小样本目录再跑同样命令。

## 输出验收

命令完成后，应看到类似结构：

```text
索引统计 (workspace: /Users/ericzhang/Desktop/物理竞赛资料)
─────────────────────────
扫描题目数:        ...

试卷切分:
  切分试卷数:      ...
  提取题目数:      ...
  规则切分:        ...
  LLM 切分:        ...
  单题路径:        ...
```

人工通过标准：

- `切分试卷数` 大于 0。
- 对多题试卷样本，`提取题目数` 应大于 `切分试卷数`。
- 如果大量 PDF 是多题试卷，但 `提取题目数 == 切分试卷数`，说明切分没有真正展开，需要抽查 OCR 文本或规则/LLM fallback。
- `规则切分` 表示题号标记足够清晰，未走 LLM fallback。
- `LLM 切分` 表示规则切分不可信时使用了 provider fallback。
- `单题路径` 主要对应图片或单页无题号输入。

## JSONL 抽查

确认索引文件存在：

```bash
INDEX="/Users/ericzhang/Desktop/物理竞赛资料/.cpho/index.jsonl"
test -s "$INDEX" && wc -l "$INDEX"
```

查看前 5 条记录的关键字段：

```bash
python - <<'PY'
import json
from pathlib import Path

index = Path("/Users/ericzhang/Desktop/物理竞赛资料/.cpho/index.jsonl")
for line in index.read_text(encoding="utf-8").splitlines()[:5]:
    row = json.loads(line)
    print({
        "problem_id": row.get("problem_id"),
        "problem_path": row.get("problem_path"),
        "problem_page_range": row.get("problem_page_range"),
    })
PY
```

人工通过标准：

- `problem_id` 形如 `<paper_sha256>:01`、`<paper_sha256>:02`。
- 同一个 `problem_path` 可以出现多行，对应同一份试卷里的多道大题。
- `problem_page_range` 是 1-indexed 的页范围，例如 `[1, 1]`、`[2, 3]`。
- 不应再看到只有整份 PDF 粒度且没有 `problem_page_range` 的旧索引记录。

按文件统计每份 PDF 被切出多少题：

```bash
python - <<'PY'
import json
from collections import Counter
from pathlib import Path

index = Path("/Users/ericzhang/Desktop/物理竞赛资料/.cpho/index.jsonl")
counts = Counter()
for line in index.read_text(encoding="utf-8").splitlines():
    row = json.loads(line)
    counts[row["problem_path"]] += 1

for path, count in counts.most_common(20):
    print(f"{count:>3}  {path}")
PY
```

人工抽样标准：

- 选择 3 份你知道是多题试卷的 PDF。
- 每份应至少切出 2 条记录。
- 页范围应连续或基本合理；允许后续再调优 OCR/LLM prompt，但不能退回“一份卷一条记录”。

## 候选标签检查

如果输出提示有待审候选标签：

```bash
uv run cpho index "/Users/ericzhang/Desktop/物理竞赛资料" --list-candidates
```

这不是 Phase 02.1 的核心验收点，但可以确认标签层仍在正常工作。

## 常见问题

### 配置或 API key 报错

确认 `config.local.yml` 或环境变量里有 provider key。真实 index 会调用 LLM 做标签生成，除非测试里显式注入 fake provider。

### OCR 升级提示

如果出现 OCR 引擎升级选择，按需要选择：

- `a` 重建全部
- `b` 只重建受影响条目
- `c` 暂时复用旧 OCR
- `d` 只索引新增题目

Phase 02.1 已处理旧 index schema；旧行缺少 `problem_page_range` 或 `split_prompt_version` 时应被视为 stale 并重建，而不是崩溃。

### 切分数量明显偏低

先看输出中 `规则切分` 和 `LLM 切分`：

- `规则切分` 很低：OCR 文本可能没有清楚识别 `第N题`、`N.`、`(N)`、`Problem N`、`题N`。
- `LLM 切分` 为 0 且规则失败：检查 provider 配置是否可用。
- 全部走 `单题路径`：检查 workspace 是否主要是图片或单页输入。

## 当前阶段不要求人工验证的内容

- 不要求生成每道题的派生 PDF 文件。
- 不要求旧索引迁移脚本；重跑 `cpho index --force` 即可重建。
- 不要求把小问 `(1)(2)(3)` 进一步切分；本阶段只切到大题粒度。
- 不要求改造 `cpho solve` 直接消费 `ProblemEntry`；本阶段只保证索引层已经按题目粒度工作。
