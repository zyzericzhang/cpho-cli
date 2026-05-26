# explain

## 用途

生成多风格物理讲解：整题物理图像、原答案逐步讲解、更清晰推导和句子级 explain。

## 前置条件

- 已选中当前题目：`/show <id>`。
- 推荐先运行 `/solve`。
- 已配置 LLM provider。

## 用法 / 参数

```text
/explain --tone teacher --tone dense
```

Tone：`teacher`、`dense`、`brief`。

## 典型输出

每个 Tone 都包含：

- 整道题物理图像与思路
- 原答案逐步讲解
- 超越原答案的更清晰推导
- 句子级 explain

## 导出文件说明

输出为一个合并的 `.explain.md`。候选标签会先确认，再通过 `add_problem_tags(skill_name="explain")` 写入 index user_tags。

## 端到端完整示例

```text
cpho> /show 1
cpho> /solve --auto-confirm
cpho> /explain --tone teacher --tone brief
→ 进入 Probe 模式？(`/probe` 或 Enter 跳过)
```

