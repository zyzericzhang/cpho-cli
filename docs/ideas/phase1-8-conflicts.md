# CPHO CLI Phase 1–8 Ideas Conflicts

Priority 1（.planning/phases/06–08 CONTEXT.md + DISCUSSION-LOG.md，PROJECT.md）作为最高优先级，其记录的所有 ideas 作为基准。

# Priority 2 读完后发现的冲突

## Explain Tone 设计 vs Explain 板块设计

低优先级来源：new-understanding-2026-05-26.md §三「确定设计」——Explain 有多 Tone 支持（老师型/密集型/简短型），每种 Tone 有独立 prompt 版本，用户可以选择多个 Tone 生成好几版讲解。

高优先级来源：Phase 07 CONTEXT.md D-14——"v1.0 Tone-based Explain 代码完全删除（core/explain.py + models/explain.py 中 Tone 相关模型），hard-cut。"；new-understanding-2026-05-27.md §六——"本轮对 Explain 做了较大调整，以下内容覆盖上一轮的 Tone 设计。"

结论：以 Phase 07 CONTEXT.md 的板块设计（思路描述/标答替换/其他方法）为准。0526 的 Tone 设计已被废弃，不写入 ideas-summary。

# Priority 3 读完后发现的冲突

## Explain v1.0 实现设计 vs Explain v2 板块设计

低优先级来源：Phase 3 CONTEXT.md D-07、D-08、D-09——Explain v1.0 的具体实现：asyncio.gather 对每个 Tone 各跑一次 SkillRuntime.run()；两阶段 LLM 调用（阶段一原答案逐步讲解+超越原答案推导，阶段二句子级 explain）；分栏目输出结构（①整道题物理图像 ②原答案逐步讲解 ③超越原答案的更清晰推导 ④句子级 explain）；三种 Tone 的 prompt 各写一版（老师型/密集型/简短型）。

高优先级来源：Phase 07 CONTEXT.md D-13、D-14——"单 SkillPipeline + 共享 preamble（KnowledgeResolver 查询 + 读题）+ 三板块并行 step；v1.0 Tone-based Explain 代码完全删除，hard-cut。"

结论：以 Phase 07 CONTEXT.md 的板块架构为准。Phase 3 v1.0 的 Tone/两阶段/分栏目结构已被替换，不写入 ideas-summary。

