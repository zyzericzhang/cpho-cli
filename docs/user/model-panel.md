# model panel

## 用途

查看 skill pipeline 的步骤、prompt 路径、当前模型和多模态标记，并为单个步骤保存 workspace 级模型覆盖配置。

## 前置条件

- 已启动 REPL。
- workspace 可写；workspace 覆盖会写入 `.cpho/skills/<skill_id>.yml`。
- provider 凭证仍来自 `config.local.yml` 或环境变量。

## 用法 / 参数

```text
/skill panel solve
/skill set-model solve extract_official_steps openai/gpt-4o-mini
/model refresh
```

## 典型输出

- `/skill panel` 输出步骤表：Step、Kind、Model、Multimodal、Prompt。
- `/skill set-model` 输出写入的配置路径。
- `/model refresh` 输出 provider 模型数量和来源。

## 导出文件说明

主要文件：

- `.cpho/skills/<skill_id>.yml` — workspace 级 step model override。
- `~/.cache/cpho/models/openrouter.json` — provider 模型列表缓存。

## 端到端完整示例

```text
cpho> /skill panel explain
cpho> /model refresh
cpho> /skill set-model explain approach google/gemini-2.0-flash-lite-001
cpho> /explain --panel approach
```
