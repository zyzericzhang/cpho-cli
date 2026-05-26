# Phase 3 Solve Decisions

`cpho solve` is now an official-answer review command. It extracts official answer steps, checks
those steps against the problem, classifies likely issue types, and reports free-text
discrepancies. It no longer presents a replacement solution as the primary output.

Discrepancies stay as flexible text because the locked Phase 3 context favored precision over a
premature controlled enum. Optional persistence still goes through existing `add_problem_tags`
with `skill_name="solve"`, which writes to the index `user_tags` layer and leaves machine tag
buckets unchanged.

The CLI supports `--auto-confirm` for batch use. Interactive confirmation remains the default
when candidate discrepancies exist.
