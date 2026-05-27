# explain

## 用途

生成 Explain v2 板块讲解：思路描述、标答替换、其他方法。Explain 会优先读取匹配的知识文件并在输出中标注来源。

## 前置条件

- 已选中当前题目：`/show <id>`。
- 推荐先运行 `/solve`。
- 已配置 LLM provider。

## 用法 / 参数

```text
/explain --panel approach --panel answer_replacement
```

Panel：

- `approach` — 思路描述，不输出完整数学推导。
- `answer_replacement` — 补全标答跳步，可直接替代标准答案。
- `alternative_methods` — 比较其他物理或数学处理方法。

## 典型输出

输出只包含用户选择的板块。每个板块末尾包含参考来源：

- 匹配知识文件路径和 `canonical_tag_id`
- `input_modality_used` provenance

## 导出文件说明

输出为一个 `.explain.md`。候选标签会先确认，再通过 `add_problem_tags(skill_name="explain")` 写入 index user_tags。

## 端到端完整示例

```text
cpho> /show 1
cpho> /solve --auto-confirm
cpho> /explain --panel approach --panel answer_replacement
→ 进入 Probe 模式？(`/probe` 或 Enter 跳过)
```
