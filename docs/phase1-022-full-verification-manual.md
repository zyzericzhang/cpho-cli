# Phase 1 → Phase 02.2 完整验证手册

**目标工作空间:** `/Users/ericzhang/Desktop/物理竞赛资料`
**项目根目录:** `/Users/ericzhang/Desktop/cpho-cli`
**验证日期:** 2026-05-24
**前置:** `config.local.yml` 已配置 OpenRouter API key

---

## 0. 前置检查

```bash
cd /Users/ericzhang/Desktop/cpho-cli

# 确认 API key 已配置
grep -c 'sk-or' config.local.yml

# 确认全量测试通过
uv run pytest -q | tail -3
# 预期: 309 passed

# 确认 CLI 可用
uv run cpho --help
```

---

## 第一部分：Phase 1 — Core Foundation

### 1.1 验证 `cpho solve` 基础管线

```bash
# 找一份单题 PDF 试跑（如果没有，跳到 1.2 用 --dry-run）
ls "/Users/ericzhang/Desktop/物理竞赛资料"/*.pdf | head -5
```

**试跑（需要 API key）：**

```bash
uv run cpho solve "/Users/ericzhang/Desktop/物理竞赛资料/芝士研学自命题50例.pdf" \
  --provider default \
  --output-dir /tmp/cpho-verify-output
```

**通过标准：**
- [ ] 命令正常结束，exit code 0
- [ ] `/tmp/cpho-verify-output/` 下生成了解题输出文件
- [ ] 输出包含中文推导步骤

**Dry-run 验证（不需要 API key）：**

```bash
uv run cpho solve "/Users/ericzhang/Desktop/物理竞赛资料/芝士研学自命题50例.pdf" --dry-run
```

**通过标准：**
- [ ] 命令正常结束
- [ ] 输出提示"dry-run 模式"或类似信息，未实际调用 LLM

**带答案配对的测试（如果存在答案文件）：**

```bash
# 查找是否有答案配对文件（命名规则: {name}-answer.{ext}）
find "/Users/ericzhang/Desktop/物理竞赛资料" -name "*-answer*" | head -5
```

如果有答案文件，试跑：

```bash
uv run cpho solve "<题目PDF路径>" --answer "<答案PDF路径>" --dry-run
```

### 1.2 验证 API Key 配置方式 (CORE-01)

```bash
# 方式1: config.local.yml（已配置）
uv run cpho solve --help | grep -E '\-\-config|\-\-provider'

# 方式2: 环境变量覆盖
OPENROUTER_API_KEY="test" uv run cpho solve "/Users/ericzhang/Desktop/物理竞赛资料/芝士研学自命题50例.pdf" --dry-run 2>&1 | head -5
# 预期: 不报 API key 错误（dry-run 不实际调用）

# 方式3: 指定 provider profile
uv run cpho solve "/Users/ericzhang/Desktop/物理竞赛资料/芝士研学自命题50例.pdf" --provider default --dry-run
```

**通过标准：**
- [ ] 三种配置方式均不报配置错误
- [ ] `config.local.yml` 在 `.gitignore` 中（`git check-ignore config.local.yml` 有输出）

### 1.3 验证 Workspace 自动发现 (CORE-02)

```bash
# 确认 workspace 包含 PDF 和图片
find "/Users/ericzhang/Desktop/物理竞赛资料" -type f \( -name "*.pdf" -o -name "*.png" -o -name "*.jpg" \) | wc -l
```

**通过标准：**
- [ ] 输出 > 0（真实资料目录下有 PDF/图片文件）

### 1.4 Phase 1 总体通过标准

- [ ] `cpho solve --dry-run` 不报错
- [ ] `cpho solve` 真实调用生成解题输出（如 API key 可用）
- [ ] 三种 API key 配置方式均可工作
- [ ] workspace 包含 PDF/图片文件

---

## 第二部分：Phase 2 — Tag Indexing

### 2.1 Dry-run 验证

```bash
uv run cpho index "/Users/ericzhang/Desktop/物理竞赛资料" --dry-run
```

**通过标准：**
- [ ] 命令正常结束，exit code 0
- [ ] 输出显示 `扫描题目数: N`（N > 0）
- [ ] 所有计数器为 0（dry-run 不实际执行 OCR/LLM）

### 2.2 正式索引

> ⚠️ 此步骤会调用 OpenRouter API（产生费用），且会在 workspace 下写入 `.cpho/` 目录。
> 如果只想验证不写入，先跳到 2.3 用已存在的索引文件验证。

```bash
uv run cpho index "/Users/ericzhang/Desktop/物理竞赛资料" --force --ocr-strategy reuse
```

**通过标准：**
- [ ] 命令正常结束
- [ ] 输出包含分层统计：
  - `扫描题目数`
  - `试卷切分`: `切分试卷数`, `提取题目数`, `规则切分`, `LLM 切分`, `单题路径`
  - `OCR 复用` / `OCR 重生成`
  - `标签层`: `重新生成` / `跳过 (fingerprint)`
- [ ] 提示 `完成. 索引: /Users/ericzhang/Desktop/物理竞赛资料/.cpho/index.jsonl`

### 2.3 验证索引文件

```bash
INDEX="/Users/ericzhang/Desktop/物理竞赛资料/.cpho/index.jsonl"

# 确认文件存在且非空
test -s "$INDEX" && echo "OK: index exists ($(wc -l < "$INDEX") lines)" || echo "FAIL: index missing or empty"
```

**查看第一条记录的全部字段：**

```bash
head -1 "/Users/ericzhang/Desktop/物理竞赛资料/.cpho/index.jsonl" | python3 -m json.tool
```

**通过标准：**
- [ ] 包含关键字段: `problem_id`, `problem_path`, `problem_page_range`, `tags`
- [ ] `problem_id` 格式如 `<sha256>:01`、`<sha256>:02`
- [ ] `tags` 包含 `physics_model`, `math_technique`, `heuristic` 三类标签
- [ ] 标签有 `id` 和 `display_zh` 字段

**抽查切分效果：**

```bash
python3 - <<'PY'
import json
from collections import Counter
from pathlib import Path

index = Path("/Users/ericzhang/Desktop/物理竞赛资料/.cpho/index.jsonl")
counts = Counter()
for line in index.read_text(encoding="utf-8").splitlines():
    row = json.loads(line)
    counts[row["problem_path"]] += 1

print(f"总题目数: {sum(counts.values())}")
print(f"涉及文件数: {len(counts)}")
print(f"每题平均题目数: {sum(counts.values())/len(counts):.1f}")
print()

# 列出被切出多题的 PDF（即试卷切分生效的文件）
multi = [(path, cnt) for path, cnt in counts.items() if cnt > 1]
print(f"多题文件 (被切出 >1 题): {len(multi)} 个")
for path, count in sorted(multi, key=lambda x: -x[1])[:15]:
    print(f"  {count:>3} 题  {path}")
PY
```

**通过标准：**
- [ ] 至少有一些文件被切分出 >1 题（证明 Phase 02.1 切分生效）
- [ ] `problem_page_range` 为 `[start, end]` 1-indexed 格式

### 2.4 增量更新验证 (IDX-02)

```bash
# 再跑一次 index，不强制重建
uv run cpho index "/Users/ericzhang/Desktop/物理竞赛资料" 2>&1 | grep -E '跳过|复用|无变化'
```

**通过标准：**
- [ ] 第二次运行大部分条目被跳过（fingerprint 匹配）
- [ ] `标签层: 跳过 (fingerprint)` > 0
- [ ] `OCR 复用` > 0（如果之前跑过 OCR）

### 2.5 候选标签检查

```bash
uv run cpho index "/Users/ericzhang/Desktop/物理竞赛资料" --list-candidates
```

**通过标准：**
- [ ] 命令正常执行（可能有或没有候选标签，均正常）

### 2.6 Phase 2 总体通过标准

- [ ] `cpho index --dry-run` 正常
- [ ] `cpho index --force` 生成 JSONL 索引文件
- [ ] JSONL 每行一道题（不是一份 PDF）
- [ ] 增量更新生效（二次运行大量跳过）
- [ ] 标签包含三类（physics_model / math_technique / heuristic）

---

## 第三部分：Phase 02.1 — Paper Splitting

### 3.1 切分统计验证

在 2.2 的 index 输出中查看：

```bash
# 重新运行 index，重点关注切分统计
uv run cpho index "/Users/ericzhang/Desktop/物理竞赛资料" 2>&1 | grep -A 8 '试卷切分'
```

**通过标准：**
- [ ] `切分试卷数` > 0
- [ ] `提取题目数` >= `切分试卷数`（至少相等）
- [ ] 如果存在多题试卷 PDF，`提取题目数` > `切分试卷数`
- [ ] 统计行包含: `规则切分`, `LLM 切分`, `单题路径`

### 3.2 ProblemEntry 结构验证

```bash
python3 - <<'PY'
import json
from pathlib import Path

index = Path("/Users/ericzhang/Desktop/物理竞赛资料/.cpho/index.jsonl")
# 找一条来自多题试卷的记录
from collections import Counter
path_counts = Counter()
rows = []
for line in index.read_text(encoding="utf-8").splitlines():
    row = json.loads(line)
    rows.append(row)
    path_counts[row.get("problem_path", "")] += 1

# 找一条对应多题文件的记录
for path, cnt in path_counts.most_common(5):
    if cnt > 1:
        sample = [r for r in rows if r.get("problem_path") == path][:3]
        print(f"\n=== {path} ({cnt} 题) ===")
        for r in sample:
            print(f"  problem_id: {r.get('problem_id')}")
            print(f"  problem_page_range: {r.get('problem_page_range')}")
            print(f"  tags keys: {list(r.get('tags', {}).keys()) if isinstance(r.get('tags'), dict) else 'N/A'}")
            print()
        break
PY
```

**通过标准：**
- [ ] 同一 `problem_path` 可对应多行（多道题）
- [ ] 每条记录有独立的 `problem_page_range`
- [ ] `problem_id` 格式如 `<sha256>:01`、`<sha256>:02`

### 3.3 Phase 02.1 总体通过标准

- [ ] 索引输出包含试卷切分统计行
- [ ] 多题试卷被正确拆分为多条索引记录
- [ ] 每条记录有 `problem_page_range` 字段
- [ ] `problem_id` 包含试卷哈希 + 题号后缀

---

## 第四部分：Phase 02.2 — TUI REPL

### 4.1 启动 REPL

```bash
uv run cpho repl --workspace "/Users/ericzhang/Desktop/物理竞赛资料"
```

**通过标准：**
- [ ] 看到 banner 信息（workspace 路径、index 状态、provider 等）
- [ ] 看到 `cpho>` 提示符
- [ ] 可以输入命令

### 4.2 `/help` 命令 (SC-1)

在 REPL 中输入：

```
/help
```

**通过标准：**
- [ ] 列出所有 13 个命令，按分类分组
- [ ] 分类包括: `帮助` (`/help`)、`设置` (`/set`)、`工作空间` (`/workspace`, `/status`, `/config`, `/index`, `/reload-index`, `/resume`)、`搜索` (`/search`, `/show`)、`调试` (`/run`)、`技能` (`/explain`, `/quiz`)

```
/help search
```

**通过标准：**
- [ ] 显示 `/search` 的详细用法和参数说明

### 4.3 `/workspace` 和 `/status` 命令

```
/workspace /Users/ericzhang/Desktop/物理竞赛资料
/status
```

**通过标准：**
- [ ] `/workspace` 设置工作空间，输出确认信息
- [ ] `/status` 显示索引状态（题目数、标签数、索引修改时间等）
- [ ] 如果索引文件存在，`problem_count` > 0

### 4.4 `/config` 命令

```
/config
```

**通过标准：**
- [ ] 显示当前配置（workspace、max_results、output_format、provider 等）
- [ ] 不显示 API key 等敏感信息

### 4.5 `/set` 命令

```
/set max_results 10
/set output_format compact
/config
```

**通过标准：**
- [ ] `/set` 接受并保存设置
- [ ] `/config` 反映更新后的值
- [ ] `/set invalid_key value` 被拒绝（仅 allowlist 字段可写）

### 4.6 `/index` 命令 (D-20 dry-run 强制预览)

> ⚠️ 先在 REPL 中设置好 workspace，然后运行：

```
/index
```

**通过标准：**
- [ ] 首先显示 dry-run 预览（统计信息）
- [ ] **必须**出现确认提示（如 `确认执行索引? [y/N]`）
- [ ] 输入 `n` 取消 —— 确认未实际执行索引
- [ ] 再次 `/index`，输入 `y` 确认 —— 开始实际索引构建

**测试 `/index --dry-run`：**

```
/index --dry-run
```

**通过标准：**
- [ ] 仅显示预览，不询问确认，不实际构建

### 4.7 `/search` 命令 (SC-2)

先确保索引存在（通过 `/index` 构建或已有 JSONL），然后：

```
/search --physics-model newton_second_law
```

**通过标准：**
- [ ] 输出匹配结果表格
- [ ] 表格包含题目 ID、标签摘要等信息
- [ ] 显示匹配数量

**位置参数搜索：**

```
/search 力学
```

**通过标准：**
- [ ] 执行搜索（可能返回全部或过滤后的结果——取决于 tag cache 是否预热）
- [ ] 不报错

**测试 `/search --help`：**

```
/search --help
```

**通过标准：**
- [ ] 显示所有过滤选项: `--physics-model`, `--math-technique`, `--heuristic`, `--match-mode`

### 4.8 `/show` 命令 (SC-3)

在上一步 `/search` 之后：

```
/show 1
```

**通过标准：**
- [ ] 显示第 1 道题的详细信息
- [ ] 包含: problem_id、来源试卷路径、页范围、标签（含中文显示名）
- [ ] 包含 OCR 文本内容

```
/show 1 --full
```

**通过标准：**
- [ ] 显示完整 OCR 文本（通过 pager 分页）

**边界测试：**

```
/show 99999
```

**通过标准：**
- [ ] 输出 `序号超出范围` 或类似提示（不崩溃）

```
/show nonexistent_id_12345
```

**通过标准：**
- [ ] 输出 `未找到题目: nonexistent_id_12345`（不是 `未找到索引`）

**未搜索直接 `/show`：**

重启 REPL 或 `/resume` 后直接输入 `/show 1`。

**通过标准：**
- [ ] 提示 `尚未搜索` 或类似信息（不崩溃）

### 4.9 会话状态跨命令共享 (SC-2)

```
/search --physics-model newton_second_law
/search --physics-model energy_conservation
```

**通过标准：**
- [ ] 两次搜索独立执行
- [ ] `/show 1` 显示的是最近一次搜索的第 1 道题

### 4.10 `/reload-index` 和 `/resume` 命令

```
/reload-index
/status
```

**通过标准：**
- [ ] `/reload-index` 重新加载索引元数据
- [ ] `/status` 反映最新状态

```
/resume
```

**通过标准：**
- [ ] 如果索引未变化，恢复上次搜索上下文
- [ ] 如果索引已变化（mtime 不同），清除旧的搜索上下文

### 4.11 Tab 自动补全

在 REPL 中测试：

1. 输入 `/` 然后按 Tab
   - [ ] 列出所有 13 个命令名
2. 输入 `/sea` 然后按 Tab
   - [ ] 自动补全为 `/search`
3. 输入 `/search --` 然后按 Tab
   - [ ] 列出所有选项 flag（`--physics-model`, `--math-technique`, `--heuristic`, `--match-mode`）
4. 输入 `/search --physics-model ` 然后按 Tab（空格后）
   - [ ] 列出索引中的 physics_model 标签 ID（如已 index 过）
5. 输入 `/set ` 然后按 Tab
   - [ ] 列出可设置的字段名

### 4.12 `/run` 调试命令

```
/run builtin_skills
```

**通过标准：**
- [ ] 显示 skill spec 信息（不执行 skill 步骤）
- [ ] 不会真正调用 LLM

### 4.13 Phase 3 Stub 命令

```
/explain
/quiz
```

**通过标准：**
- [ ] 均显示 "Phase 3 未实现，请期待。"（不崩溃，不报 Python 异常）

### 4.14 会话持久化

退出 REPL（Ctrl+D 或 `/quit`），然后重新启动：

```bash
uv run cpho repl --workspace "/Users/ericzhang/Desktop/物理竞赛资料"
```

进入后检查：

```
/config
```

**通过标准：**
- [ ] `max_results`、`output_format` 等设置被保留（如果上次 `/set` 过）
- [ ] `workspace` 被持久化（如果上次 `/workspace` 过且未用 `--workspace` 覆盖）

**索引上下文恢复：**

```
/status
/search --physics-model newton_second_law
/show 1
```

退出并重新进入 REPL 后：

```
/resume
/show 1
```

**通过标准：**
- [ ] 如果索引未变，`/resume` 恢复上次搜索结果，`/show 1` 仍然有效

### 4.15 REPL 在无索引 workspace 下启动

```bash
# 用临时空目录启动
uv run cpho repl --workspace /tmp/cpho-empty-test
```

进入后：

```
/status
```

**通过标准：**
- [ ] `/status` 显示"索引未构建"或类似提示（不崩溃）
- [ ] `/search` 提示需要先构建索引（不崩溃）

```
/help
/set max_results 5
```

**通过标准：**
- [ ] 非索引命令（`/help`, `/set`）正常工作

### 4.16 Phase 02.2 总体通过标准

- [ ] `cpho repl` 启动成功，显示 `cpho>` 提示符
- [ ] `/help` 列出全部 13 个命令
- [ ] `/search` + `/show` 闭环工作正常
- [ ] 搜索结果跨命令共享（session state）
- [ ] Tab 补全对所有命令和选项生效
- [ ] `/index` 强制 dry-run 预览 + 确认
- [ ] 无索引时非索引命令仍正常工作
- [ ] `/explain` `/quiz` stub 不崩溃
- [ ] 会话持久化：设置跨 REPL 重启保留
- [ ] Ctrl+D 正常退出

---

## 第五部分：主题分类 (Phase 2)

### 5.1 主题树

```bash
uv run cpho topic list
```

**通过标准：**
- [ ] 显示 5 大分类（力学、热学、电磁学、光学、近代物理）
- [ ] 2-3 层树状结构

### 5.2 主题浏览

```bash
uv run cpho topic browse 力学 "/Users/ericzhang/Desktop/物理竞赛资料"
```

**通过标准：**
- [ ] 列出力学分类下的题目（如果索引中有力学题目）
- [ ] 不报错（即使没有匹配题目）

### 5.3 组卷

```bash
uv run cpho compose --topic 力学 "/Users/ericzhang/Desktop/物理竞赛资料"
```

**通过标准：**
- [ ] 列出匹配的题目
- [ ] 不带 `--topic` 和 `--tags` 时列出全部题目

```bash
uv run cpho compose --tags angular_momentum_conservation "/Users/ericzhang/Desktop/物理竞赛资料"
```

**通过标准：**
- [ ] 按标签筛选题目
- [ ] 支持逗号分隔多标签

---

## 第六部分：结构性约束验证

### 6.1 prompt_toolkit 隔离 (D-07)

```bash
# core/ 目录不应引入 prompt_toolkit
grep -rn 'prompt_toolkit\|cmd2' src/cpho_cli/core/ && echo "FAIL" || echo "PASS"
```

### 6.2 REPL 目录 cmd2 隔离

```bash
grep -rn 'import cmd2\|from cmd2' src/cpho_cli/cli/repl/ && echo "FAIL" || echo "PASS"
```

### 6.3 Lazy import

```bash
# 导入 cli.app 不应加载 prompt_toolkit
uv run python -c "import sys; import cpho_cli.cli.app; assert 'prompt_toolkit' not in sys.modules, 'prompt_toolkit loaded eagerly!'; print('PASS')"
```

### 6.4 代码质量

```bash
uv run ruff check src/cpho_cli/cli/repl/ && echo "ruff PASS"
uv run mypy src/cpho_cli/cli/repl/ && echo "mypy PASS"
```

---

## 第七部分：全量回归测试

```bash
cd /Users/ericzhang/Desktop/cpho-cli

# 全量测试
uv run pytest -q
# 预期: 309 passed

# REPL 专项测试
uv run pytest tests/test_repl_*.py -q
# 预期: ~32+ passed

# 验收测试
uv run pytest tests/test_repl_phase02_2_acceptance.py -q
# 预期: 4+ passed

# Phase 02.1 验收测试
uv run pytest tests/test_phase021_acceptance.py -q
# 预期: passed
```

---

## 验证清单汇总

### Phase 1 (Core Foundation)
- [ ] `cpho solve --dry-run` 正常
- [ ] API key 三种配置方式可用
- [ ] workspace 有 PDF/图片文件

### Phase 2 (Tag Indexing)
- [ ] `cpho index --dry-run` 正常
- [ ] `cpho index --force` 生成 JSONL
- [ ] JSONL 每行一道题
- [ ] 增量更新生效
- [ ] 标签包含三类 (physics_model / math_technique / heuristic)
- [ ] `cpho topic list` 显示主题树
- [ ] `cpho topic browse` 可用
- [ ] `cpho compose` 可用

### Phase 02.1 (Paper Splitting)
- [ ] 索引输出包含切分统计行
- [ ] 多题试卷正确拆分
- [ ] 每条记录有 `problem_page_range`
- [ ] `problem_id` 格式正确

### Phase 02.2 (TUI REPL)
- [ ] `cpho repl` 启动成功
- [ ] `/help` 列出 13 个命令
- [ ] `/search` + `/show` 闭环
- [ ] Tab 补全生效
- [ ] `/index` dry-run 预览+确认
- [ ] 无索引时非索引命令正常
- [ ] 会话持久化
- [ ] Phase 3 stub 不崩溃
- [ ] lazy import 隔离
- [ ] prompt_toolkit/cmd2 隔离

### 结构性约束
- [ ] core/ 无 prompt_toolkit
- [ ] cli/repl/ 无 cmd2
- [ ] lazy import 正确
- [ ] ruff + mypy 通过
- [ ] 309 tests pass

---

## 已知问题（非阻塞）

1. **WR-01**: 全新 REPL 中 `/search 力学`（位置参数）可能返回全部题目而非过滤结果——需要先 `/index` 预热 tag cache
2. **WR-02**: `cpho repl --config <path>` 的 config path 不被 `/index` 继承——需在 REPL 内重新指定
3. **WR-03**: 少数错误消息可能不够精确（`IndexNotFoundError` 和 `ProblemNotIndexedError` 共享消息）
