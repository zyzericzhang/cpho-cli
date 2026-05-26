# Explain

Explain turns a competition physics problem and its official answer into one or more teacher-facing explanations. It is a prose skill: tone selection and stream merging are handled by `cpho_cli.core.explain`, while each prompt focuses on a single tone and stage.

The skill is answer-aware. When a Solve review exists, accepted discrepancies and official-answer corrections are included in the prompt context so the explanation does not repeat known answer issues as fact.

