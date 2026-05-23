# 物理竞赛题集标签提取任务

## 你的任务

阅读我提供的物理竞赛题目，从**每道题**中提取解题所需的知识点/技巧/策略，输出为符合规范的 YAML 词汇标签文件。

### 重要前置说明

1. **输入是按题目拆好的单题文件**，不是整张试卷。每道题独立提取标签。
2. **你只提取标签（tags）**，不要做主题分类（topics）。标签和主题是两套独立系统：
   - **标签（你在做的事）**：这道题用了什么知识/技巧/策略？一题可以有多个标签。
   - **主题（不是你在做的事）**：这道题属于什么学科领域？（力学/热学/电磁学...）一题只有一个主题路径。
3. **标签是多维度的 insights** — 它们是在解题过程中发现的，不是僵硬的学科分类。同一道题可以同时有物理定律标签、数学技巧标签、启发策略标签。

## 输出格式

输出一个完整的 YAML 文件，结构如下：

```yaml
version: "v0.1"
tags:
  - internal_id: partition_function        # snake_case，英文，唯一标识
    display_zh: 配分函数                    # 中文显示名称
    category: physics_law                  # 必须是下面5个值之一
    aliases: ["Z函数", "状态和"]            # 别名列表，至少包含1个常用别称
    description: 用配分函数联系微观态与宏观热力学量。 # 一句话说明，中文，句号结尾
```

## category 必须严格使用以下 5 个值

| category 值 | 含义 | 判断标准 |
|-------------|------|---------|
| `physics_law` | 物理定律 | 题目涉及的具体物理原理，如配分函数、天体运动有效势能，干涉或衍射。注意太基础的比如牛顿定律去掉 |
| `math_technique` | 数学技巧 | 解题用到的数学工具，如微分方程凑全微分、级数展开、积分方法 |
| `heuristic` | 启发策略 | 解题思路层面的选择，如采用相图，如光力类比 |
| `physics_model` | 物理模型 | 比如有很多题目可能是从论文中节选下来的，会涉及到具体的模型，比如彩虹模型，注意要具体 |
| `approximation` | 近似方法 | 明确的近似手段，如积分展开、小角近似，注意不是那种宽泛的小角近似，而是具体的近似方式 |

## 字段规范

- `internal_id`: snake_case 英文，全小写，单词用下划线连接。例如 `angular_momentum_conservation`。保持简洁，控制在 2-5 个单词。
- `display_zh`: 中文，使用中国大陆物理竞赛通用术语。不要用台湾用语。简洁，通常 2-8 个字。
- `category`: 必须严格等于上面表格中的 5 个值之一，不能自创。
- `aliases`: 必填，至少 1 个。包含常见的中文别称、英文别称、公式缩写。每个 alias 尽量简短。
- `description`: 一句话说明这个标签是什么，中文，以句号结尾。控制在 15-30 字。
- **不要写** `status`、`visibility`、`layer` 字段 — 这些由系统自动补充。

## 提取原则

1. **按题提取**：输入是一道一道独立的题目，每道题单独分析其需要的标签。不要跨题目合并标签。
2. **多维度覆盖**：每道题通常涉及多个标签类别 — 物理定律 + 数学技巧 + 启发策略。每个类别中相关的都要提取，不要遗漏。
3. **粒度适中**：标签不要太细（如"匀加速直线运动"太具体）也不要太粗（如"力学"太笼统 — 那是主题分类的活，不是你做的）。
4. **去重**：相同概念的标签只出现一次。不同题目反复用到的同一个标签只写一条。
5. **从题目出发**：只提取题目实际需要的知识点，不要凭空列举物理公式。
6. **参考已有标签**：以下 42 个标签已存在（已按新分类体系重组），你的输出中不要重复它们：

已存在的 physics_law (10个):
  momentum_conservation, energy_conservation, angular_momentum_conservation,
  ideal_gas_law, first_law_thermo, second_law_thermo,
  electrostatics_gauss, circuit_kirchhoff, electromagnetic_induction,
  wave_interference

已存在的 physics_model (4个):
  circular_motion, simple_harmonic_motion, rigid_body_rotation,
  geometric_optics

已存在的 math_technique (12个):
  dimensional_analysis, small_angle_approximation, taylor_expansion,
  separation_of_variables, ode_first_order, ode_second_order,
  vector_decomposition, coordinate_transform, calculus_integral,
  binomial_approximation, symmetry_argument, limit_analysis

已存在的 heuristic (14个):
  reference_frame_choice, conservation_law_selection,
  coordinate_system_choice, free_body_diagram, identify_constraint,
  symmetry_recognition, limiting_case_check, boundary_condition_setup,
  variable_substitution, equivalent_circuit, superposition_principle,
  analogy_mapping, newton_second_law, system_selection

已存在的 approximation (2个):
  approximation_to_first_order, approximation_to_second_order

> 注意：以上 42 个标签已从旧分类体系（physics_model / system_selection 等）重组到新 5 分类。如果你对某个标签的分类归属有异议，请在新输出的标签中注明你的建议。

## 验证要求

输出前请自查：
- [ ] 所有 `category` 值都在 5 个允许值范围内
- [ ] 所有 `internal_id` 是 snake_case 且不重复
- [ ] 没有 `status`/`visibility`/`layer` 字段
- [ ] 没有与已存在标签重复的 internal_id
- [ ] 每个标签至少 1 个 alias
- [ ] YAML 语法合法（注意冒号后空格、缩进用2空格）
- [ ] 标签不涉及主题分类的内容（那是另一个系统做的事）
