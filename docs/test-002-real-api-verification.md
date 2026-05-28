# Test 002 Real API Verification

Date: 2026-05-27
Branch: `codex/phase8-community-errors`

Workspaces:

- `/Users/ericzhang/Desktop/cpho-cli-verification-001/workspace`
- `/Users/ericzhang/Desktop/cpho-cli-verification-002/workspace`

Secrets: not printed; temporary configs use `OPENROUTER_API_KEY` env reference only.

## 01-json-fence-fix-targeted-tests

- 测试状态: 已测试
- 成功状态: 成功
- 描述: Added shared JSON extraction for fenced JSON and verified targeted suites.
- 产出位置:
  - `src/cpho_cli/core/json_utils.py`
  - `tests/test_json_utils.py`
- 结果: `uv run pytest tests/test_json_utils.py tests/test_workspace.py tests/test_skills.py tests/test_knowledge.py tests/test_docs_user.py -q` -> 25 passed.

## 02-solve-real-api

- 测试状态: 已测试
- 成功状态: 成功
- 描述: Retried `cpho solve` with real OpenRouter API after JSON fence parsing fix. All five solve steps completed and produced JSON + Markdown.
- 产出位置:
  - `/Users/ericzhang/Desktop/cpho-cli-verification-001/artifacts/06-solve-after-json-fix/B004-周考-力学试题-report.json`
  - `/Users/ericzhang/Desktop/cpho-cli-verification-001/artifacts/06-solve-after-json-fix/B004-周考-力学试题-report.md`

## 03-knowledge-normalize-real-api

- 测试状态: 已测试
- 成功状态: 成功
- 描述: Retried `cpho knowledge normalize` with real OpenRouter API after JSON fence parsing fix. Draft was written successfully.
- 产出位置:
  - `/Users/ericzhang/Desktop/cpho-cli-verification-001/workspace/.cpho/knowledge/drafts/20260527163320-knowledge-source.md`

## 04-index-artifacts-ignore

- 测试状态: 已测试
- 成功状态: 成功
- 描述: Created a fresh workspace containing a real problem PDF pair and a generated PDF under `artifacts/old-output/`. `cpho index --force --vision` scanned 1 file only, proving artifacts are ignored for new runs.
- 产出位置:
  - `/Users/ericzhang/Desktop/cpho-cli-verification-002/workspace/.cpho/index.jsonl`
- 结果: index contains 1 entry with `problem_path=sample-试题.pdf`.

## 05-community-kb-sync-real-github

- 测试状态: 已测试
- 成功状态: 成功
- 描述: Created a temporary GitHub release `cpho-kb-verification-001` in `zyzericzhang/cpho-cli` containing one public knowledge file, synced it through `cpho knowledge sync`, verified resolver returns `community`, then deleted the temporary release and tag.
- 产出位置:
  - `/Users/ericzhang/Desktop/cpho-cli-verification-002/community-cache/cpho-cli/knowledge/verification-newton.md`
  - `/Users/ericzhang/Desktop/cpho-cli-verification-002/community-cache/cpho-cli/metadata.json`
- Cleanup:
  - GitHub release deleted.
  - Remote tag deleted.
  - `gh release view cpho-kb-verification-001` exit code was 1 after cleanup.

## 06-knowledge-find-community

- 测试状态: 已测试
- 成功状态: 成功
- 描述: With `CPHO_COMMUNITY_KB_DIR` pointing to the synced cache, `cpho knowledge find` returned the community knowledge file with `same_category` match.
- 产出位置:
  - stdout only

## 07-ci-regression

- 测试状态: 已测试
- 成功状态: 成功
- 描述: Full local CI after quick fixes.
- 产出位置:
  - stdout only
- 结果:
  - `uv run pytest -q`: 456 passed, 5 PyMuPDF/SWIG warnings.
  - `uv run ruff check .`: All checks passed.

## Remaining Notes

- Real API feature failures from Test 001 were fixed and passed in Test 002.
- The temporary GitHub release used for community KB verification was removed after sync; local synced cache remains as evidence.

