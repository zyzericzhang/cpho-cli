# 内置标签词表人工维护手册

## 当前结构

内置标签分两层存放：

- `src/cpho_cli/vocabulary/builtin.yml`：核心启动词表，保留最基础的 42 个 canonical tag。
- `src/cpho_cli/vocabulary/builtin/*.yml`：按内容板块拆分的扩展内置词表。本轮从 `docs/builtinchanges.md`、`docs/bc2.md`、`docs/bc3.md` 的每个 `version:` 块生成。

当前板块文件：

1. `01_optics_geometric.yml`：几何光学、光线方程、成像与光学模型。
2. `02_optics_wave_quantum.yml`：干涉、衍射、偏振、散射、波动/量子相关标签。
3. `03_thermal_statistical.yml`：热学、统计物理与输运标签。
4. `04_relativity_nuclear.yml`：相对论、粒子衰变、核物理标签。
5. `05_mechanics_advanced.yml`：高级力学、刚体、轨道、变分、振动和约束模型。
6. `06_electrostatics_electromagnetism.yml`：静电、电路、磁场、电磁波和带电粒子运动。

## 分类规则

`category` 只能使用五个值：

- `physics_law`：具体物理定律、守恒律、边界条件、方程或可直接用于推导的物理关系。
- `physics_model`：具体问题模型或论文/竞赛题常见模型，例如彩虹模型、光镊、导体球电像、陀螺模型。
- `math_technique`：数学工具，例如分离变量、矩阵法、变分法、特殊方程、渐近/积分技巧。
- `heuristic`：解题策略或建模选择，例如换系、边界匹配、能量法、电路对称简化。
- `approximation`：明确近似方法，例如傍轴近似、一阶展开、导心近似、准静态近似。

注意：旧的 `system_selection` 已合并到 `heuristic`；过于基础的教材概念不要强行放进 `physics_law`，必要时作为 `heuristic` 或从 builtin 中删除。

## 手动新增或修改标签步骤

1. 判断标签属于哪个板块。如果是新板块，新建 `src/cpho_cli/vocabulary/builtin/NN_name.yml`，编号保持两位数并放在合适顺序。
2. 每个文件保持如下结构：

```yaml
version: "v0.1"
tags:
  - internal_id: example_tag
    display_zh: 示例标签
    category: heuristic
    aliases: ["示例别名"]
    description: 一句话说明这个标签的用途。
```

3. `internal_id` 必须是稳定 snake_case；发布后尽量不要重命名。重命名会导致已有 `.cpho/index.jsonl` 中的旧标签失效。
4. 扩展板块文件不要手写 `status`、`visibility`、`layer`；loader 会自动补默认值并强制 `layer=builtin`。
5. 同一文件内不要重复 `internal_id`。跨文件重复时，loader 按 `builtin.yml` → `builtin/*.yml` 文件名排序合并，后加载的条目覆盖先加载的条目。

## 本轮发现的跨板块重复

这些重复不一定是错误，但需要人工确认最终 canonical 归属。当前实现保留重复项，并通过稳定加载顺序让后加载板块覆盖前加载板块：

- `asymptotic_matching`: 02_optics_wave_quantum.yml, 05_mechanics_advanced.yml
- `bohr_quantization`: 01_optics_geometric.yml, 03_thermal_statistical.yml
- `brewster_angle`: 01_optics_geometric.yml, 06_electrostatics_electromagnetism.yml
- `capillary_rise`: 02_optics_wave_quantum.yml, 05_mechanics_advanced.yml
- `dimensional_analysis`: 02_optics_wave_quantum.yml, 05_mechanics_advanced.yml
- `dispersion_relation`: 01_optics_geometric.yml, 05_mechanics_advanced.yml
- `effective_potential`: 01_optics_geometric.yml, 05_mechanics_advanced.yml
- `evanescent_wave`: 01_optics_geometric.yml, 06_electrostatics_electromagnetism.yml
- `fraunhofer_diffraction`: 01_optics_geometric.yml, 06_electrostatics_electromagnetism.yml
- `fresnel_diffraction`: 01_optics_geometric.yml, 06_electrostatics_electromagnetism.yml
- `group_velocity`: 01_optics_geometric.yml, 05_mechanics_advanced.yml
- `limiting_case_check`: 02_optics_wave_quantum.yml, 05_mechanics_advanced.yml
- `malus_law`: 01_optics_geometric.yml, 06_electrostatics_electromagnetism.yml
- `phase_velocity`: 01_optics_geometric.yml, 05_mechanics_advanced.yml
- `polarization_state`: 01_optics_geometric.yml, 06_electrostatics_electromagnetism.yml
- `quasi_static_process`: 02_optics_wave_quantum.yml, 05_mechanics_advanced.yml
- `radiation_pressure`: 01_optics_geometric.yml, 02_optics_wave_quantum.yml
- `total_internal_reflection`: 01_optics_geometric.yml, 06_electrostatics_electromagnetism.yml
- `virial_theorem`: 02_optics_wave_quantum.yml, 05_mechanics_advanced.yml

## 修改后必跑检查

在项目根目录运行：

```bash
uv run pytest tests/test_index_models.py tests/test_index_vocabulary.py tests/test_index_builtin_vocab.py -q
uv run ruff check src/cpho_cli/models/index.py src/cpho_cli/core/index/vocabulary.py tests/test_index_models.py tests/test_index_vocabulary.py tests/test_index_builtin_vocab.py
uv run mypy src/cpho_cli/models/index.py src/cpho_cli/core/index/vocabulary.py
uv run python -c "from pathlib import Path; from cpho_cli.core.index.vocabulary import load_merged_vocabulary; v=load_merged_vocabulary(Path('.')); print(len(v.tags), v.version)"
```

## 02-07 相关人工准备

02-07 会引入 topic hierarchy。请保持两个系统分离：

- tag：多标签，描述题目用了哪些知识、技巧、模型、近似和启发。
- topic：单一路径，描述题目属于哪个学科主题，例如 `力学/天体运动/轨道理论`。

整理后续题集时，先把整张试卷拆成单题，再分别做 topic assignment 和 tag extraction。不要把 `力学`、`热学`、`电磁学` 这类主题词写进 builtin tag。
