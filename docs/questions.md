# 调研问题

> 本文件由 explore 会话追加。格式：`[状态] YYYY-MM-DD — 问题描述`

---

## CPHO CLI 产品 — 技术选型与方案调研

### 待调研

- [ ] 2026-05-19 — **基座框架选型**：Aider vs TalkPipe vs GangDan vs 从头搭建，哪个最适合作为物理竞赛题目解析 CLI 的基座？评估维度：架构可定制性、MIT/BSD 协议、社区活跃度、Python 版本兼容性。
- [ ] 2026-05-19 — **本地 OCR 管线方案**：PDF 和扫描版试卷图片 → LaTeX 文本的最佳本地 OCR 方案是什么？需要对比 Tesseract + 后处理、PaddleOCR、Mathpix API（非本地但精度高）、Nougat（学术 PDF 专用）。
- [ ] 2026-05-19 — **Prompt-as-Code 实践**：如何在 Python CLI 中实现 Markdown 文件 → 模板变量插值 → JSON Schema 强制 → LLM 调用的三层组装？是否有现成的库（如 LangChain ChatPromptTemplate）可以直接用？
- [ ] 2026-05-19 — **Planner-Worker 架构在本地 CLI 中的简化实现**：不需要 Postgres/SSE，本地如何实现 Task DAG 的调度？Python 标准库方案（asyncio + 依赖图拓扑排序）是否足够？
- [ ] 2026-05-19 — **与现有 CPHO 线上平台的联动接口设计**：未来 CLI → 线上同步解析配置和结果，需要什么样的 API 契约？是否需要 CLI 端的认证机制？
