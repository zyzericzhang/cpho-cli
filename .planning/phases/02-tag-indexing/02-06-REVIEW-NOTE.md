# Phase 2 Starter Vocabulary — Review Note

## 背景

builtin.yml 内含 42 个 starter canonical tag，由 Phase 2 researcher 基于通用物理竞赛知识起草（[ASSUMED] 标记）。
这些标签的 `internal_id` 一旦发布，重命名属于 breaking schema change，需要全量重跑索引才能迁移。
此 review 在 ID 锁定前请用户（domain expert）调整中文展示名 / 别名 / 描述。

## 用户回答

请逐项回答（"skip" 表示接受默认）：

1. **物理模型类（15 条）**：是否有遗漏的常见竞赛模型？例如：相对论、广义动量、变质量系统、谐振耦合？
   - [ ] 添加新条目（请列出 internal_id + display_zh）
   - [ ] 接受现状

2. **数学技巧类（12 条）**：是否有遗漏？例如：留数定理、Fourier 级数、Lagrange 乘子、变分？
   - [ ] 添加新条目
   - [ ] 接受现状

3. **启发/策略类（15 条）**：display_zh 是否符合教练日常用语？
   - 示例疑问：`研究对象选择` vs `系统选取`？`受力分析` vs `分离体图`？
   - [ ] 修改具体 display_zh（列出 internal_id → 新 display_zh）
   - [ ] 接受现状

4. **别名补全**：你能至少给以下 5 个 high-traffic tag 各加一个别名吗？
   - newton_second_law
   - momentum_conservation
   - small_angle_approximation
   - free_body_diagram
   - symmetry_recognition

5. **category 归类争议**：以下条目是否分类正确？
   - `superposition_principle` → heuristic（也许应为 math_technique？）
   - `analogy_mapping` → heuristic
   - `equivalent_circuit` → heuristic（也许应为 physics_model？）

## 修改后必跑

```
uv run pytest tests/test_index_builtin_vocab.py -x
```

## 不在此 review 范围

- 添加 candidate tag 流程（Plan 02-04 中的 candidate tag 机制会接住 LLM 提议的新 tag，无需在 builtin.yml 中提前枚举）。
- 用户私有词表（workspace.yml / private.yml）由用户自行维护，不在内置 review 范围。
