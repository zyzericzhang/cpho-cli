# Stack Research — CPHO CLI v1.1

**Domain:** Local Python CLI for physics-competition workspace analysis (Knowledge Base + Explain v2 + Model Panel + Cross-platform installers)
**Researched:** 2026-05-27
**Confidence:** HIGH for items 1/2/3/5; **LOW–MEDIUM** for item 4 (installer — user-acknowledged uncertain)

> Scope note: This file ONLY covers v1.1 additions. Validated v1.0 stack (Python 3.12, uv, RapidOCR, prompt_toolkit, wcwidth, PyMuPDF, Jinja2, Pydantic StrictModel, Typer, JSONL storage, OpenRouter via core/llm.py) is reused unchanged.

---

## Recommended Stack — v1.1 Additions

### Core Additions

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **python-docx** | 1.1.x (verify pyproject pin; current line is 1.1+) | Parse `.docx` to text/markdown for multimodal knowledge import | Industry-standard pure-Python OOXML reader. Context7 reputation High (`/python-openxml/python-docx`, 382 snippets). Returns paragraph + run + table objects which our normalization skill can render to markdown chunks before sending to LLM. |
| **mammoth** | 1.8.x | Optional: convert `.docx` → semantic HTML/Markdown | When user docx has nontrivial formatting (lists, headings, tables) we want to preserve structure for the LLM. `python-docx` is reading-API-centric; mammoth produces clean markdown in one call. Use mammoth as the default text path, python-docx as the introspection escape hatch. |
| **Pillow** | ≥10.4 | Open/normalize images, ensure JPEG/PNG and downscale large handwritten photos before sending to multimodal LLM | Already a transitive dep via PyMuPDF; making it direct is cheap. Multimodal LLM gateways (OpenRouter/Gemini) charge per pixel-tile; explicit downscale to ≤2048 long edge controls cost. |
| **httpx** | ≥0.27 | Live model-list HTTP calls to OpenRouter & Gemini; **also retry/backoff for community-knowledge git pulls when falling back to REST** | Async + sync, HTTP/2, sensible timeouts. core/llm.py likely already uses it or `openai` SDK (which uses httpx). Standardize on it across new HTTP touchpoints. |
| **google-genai** (Python SDK) | 1.33+ (Context7: `/googleapis/python-genai` v1_33_0) | List Gemini models via `client.models.list()`; reuse for Gemini API key path of model-panel | Replaces deprecated `google-generativeai`. Provides paginated `models.list()` and proper Pydantic-shaped Model objects (HIGH confidence — verified via Context7). |
| **GitPython** *or* shell `git` subprocess | GitPython 3.1.43+ | Sync community Knowledge Base repo (`git clone --depth 1` + `git pull --ff-only`) | See "GitHub-as-database" section below. Subprocess wrapping `git` is simpler/leaner than GitPython if we only do `clone/fetch/pull` — recommend subprocess + `shutil.which("git")` probe. |
| **platformdirs** | 4.3+ | Cross-platform user-data dir for community KB clone + model-list cache (`~/.cpho/` on mac, `%APPDATA%\cpho\` on Windows) | Required for Windows compat; standard 12-factor location pattern. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **diskcache** | 5.6+ | TTL cache for fetched model lists (e.g. cache for 30 min, refresh on REPL command `/models refresh`) | When users open model-selection panel; avoid hammering OpenRouter on every keystroke. |
| **rapidfuzz** | 3.10+ | Fuzzy match between problem tag and knowledge-file front-matter/title when no exact tag hit | Knowledge file lookup needs graceful fallback: exact tag → fuzzy tag → null. Pure-C, no compile step on Win. |
| **markdown-it-py** | 3.0+ | Parse markdown knowledge files to extract titles, headings, code blocks for indexing | When building knowledge-file index (mirrors existing JSONL pattern used for problems). |
| **olefile** | 0.47+ | Read legacy `.doc` (Word 97-2003) header to **detect format only**, then route through LibreOffice CLI or reject with friendly error | True `.doc` handling in pure Python is unreliable. Recommendation: detect via olefile, recommend user save-as-.docx; show clear "改哪里" error per the v1.1 error-docs requirement. |

### Development / Packaging Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| **PyInstaller** 6.14+ | Build standalone Mac/Windows executables (single-folder mode `--onedir`) | **Primary installer candidate.** Verified via Context7 `/pyinstaller/pyinstaller` v6.14.1. Best ecosystem support, most StackOverflow coverage, RapidOCR + PyMuPDF known-working with explicit `--collect-all` hooks. See risk flag below. |
| **Nuitka** 2.x | Optional fallback if PyInstaller bundle size or startup time hurts | Compiles to C → smaller surface for AV false-positives on Windows, but build times are 5-10× PyInstaller. Use only if PyInstaller path fails. |
| **briefcase** | NOT recommended for this project | BeeWare-stack focused on GUI apps (Toga); CLI/REPL packaging is a second-class citizen. Produces `.dmg`/`.msi` but adds Toga ceremony. |
| **create-dmg** (macOS shell tool) | Wrap PyInstaller `--onedir` bundle into a styled `.dmg` for non-technical Mac users | One-line CI step; no Python required. |
| **WiX Toolset** v4 or **Inno Setup** 6 | Wrap PyInstaller output into Windows installer (`.msi` or `.exe`) | Inno Setup is the lighter, friendlier path for non-technical users; signing is optional but recommended. |

---

## Section-by-Section Findings

### 1. Multimodal File Handling (image / .docx / .doc)

**Recommendation:**

- **Images** (PNG/JPEG/HEIC/handwritten photos): pass **raw bytes** through Pillow for sanity check + downscale, then base64-encode and send via existing `core/llm.py` multimodal interface (already supports OpenRouter's image-content blocks per v1.0). **Do NOT OCR** — that path is reserved for Index per the v1.1 design spec.
- **.docx**: use **`mammoth`** to convert to markdown (preserves headings/lists/tables) and pass the markdown plus any embedded images as multipart multimodal content. Fallback to `python-docx` if mammoth chokes on a specific document — `python-docx` exposes the raw OOXML model.
- **.doc (legacy Word 97-2003)**: do NOT try to parse natively in Python. Detect via `olefile` (magic-byte check), surface a clear error: "Please save as .docx (Word → Save As → Word Document)". Optional escape hatch: shell out to `soffice --headless --convert-to docx` if LibreOffice is installed (detected via `shutil.which`). This matches the v1.1 "改哪里"提示 requirement.

**Why not python-docx alone:** python-docx is great for *creating* and *fine-grained editing* of docx but its read API returns paragraphs without semantic markdown — you'd hand-roll the heading/list rendering. mammoth already does this.

**Integration with v1.0 stack:** wire mammoth output into the same prompt-templating Jinja2 layer used by other skills; no change to `core/llm.py` content-block schema (still `{"type": "text"}` + `{"type": "image_url"}`).

**Confidence:** HIGH (python-docx, mammoth, Pillow all stable, Context7-verified).

---

### 2. GitHub-as-Database for Community Knowledge

**Recommendation: `git clone --depth 1` on first use + `git pull --ff-only` on demand**, NOT submodules, NOT release tarballs.

**Comparison:**

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **git clone --depth 1 + git pull** | User can edit local files & contribute back via PR; standard mental model; supports private forks; partial-fetch if repo grows | Requires `git` binary on user machine (Mac ships, Windows needs install) | ✓ **Recommended.** Detect `git` presence; if missing, fall back to ZIP-tarball download via httpx (read-only path). |
| **git submodule** | Pins to specific commit | Nightmare for non-technical users; nested .git directories; submodule update gotchas; bricks if user moves the parent dir | ✗ Avoid. |
| **gh release downloads** (zip per release) | No git required; immutable versions | No incremental updates; no edit-and-PR flow; community contributor friction; users miss between-release fixes | ⚠ Use only as fallback when `git` not installed. |
| **GitHub Contents API** | Programmatic, no clone needed | Rate-limited (60 req/hr unauthed), per-file fetch is slow for large KBs | ✗ Don't make this the primary path. |

**Concrete layout (recommended):**
```
~/.cpho/                                    (platformdirs user_data_dir)
  community-knowledge/                       (git clone of e.g. github.com/cpho-cli/knowledge)
    .git/
    knowledge/
      mechanics/
        bernoulli-flow.md
        bernoulli-flow.assets/
      em/...
  personal-knowledge/                        (user's own KB; gitignored from CLI repo)
    ...
  cache/
    models-openrouter.json                   (TTL cached)
    models-gemini.json
```

**REPL commands:** `/kb sync` → clone-or-pull; `/kb status` → show last fetch timestamp; `/kb path` → reveal directory so users can edit.

**Integration with v1.0 stack:** lookup precedence in Explain v2: `personal-knowledge/<tag>.md` > `community-knowledge/<tag>.md` > none. Reuse existing JSONL index pattern but emit a `kb_index.jsonl` (tag → file path, source, mtime).

**Confidence:** HIGH — this is the same pattern used by Oh-My-Zsh plugins, Homebrew taps, Helm chart repos, Obsidian community plugins.

---

### 3. Live Model List Fetching

**OpenRouter** — verified via Context7 (`/llmstxt/openrouter_ai_llms_txt`):
- **Endpoint:** `GET https://openrouter.ai/api/v1/models`
- **Auth:** Not strictly required to list, but include `Authorization: Bearer $OPENROUTER_API_KEY` so per-account model visibility (and BYOK-only models) shows up.
- **Response:** `{ "data": [ { id, name, created, input_modalities, output_modalities, context_length, max_output_length, pricing: {prompt, completion, image, request, …}, supported_features: ["tools","json_mode","structured_outputs",…] } ] }`
- **Filtering hook for v1.1:** filter `input_modalities` contains `"image"` to power the "multimodal-capable" badge in the model panel, and to drive the automatic OCR fallback when current model lacks image input.

**Google AI Studio (Gemini)** — verified via Context7 (`/googleapis/python-genai`):
- **Python SDK path (recommended):** `from google import genai; client = genai.Client(api_key=…); for m in client.models.list(config={"page_size": 50}): …` — returns `Model` objects with `name`, `supported_actions`, `input_token_limit`, `output_token_limit`, `supported_generation_methods`.
- **Raw REST path (fallback / if user prefers no extra SDK):** `GET https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY` — paginated, same shape.

**Library landscape:**
- **No mature pip package** unifies "fetch model lists across providers and cache." `litellm` ships a hardcoded model list (the very thing v1.1 says NOT to do) — explicitly rejected.
- **Recommendation:** roll our own thin module `core/model_registry.py` with one fetcher per provider, output normalized to a single `ModelInfo` Pydantic StrictModel, cached via `diskcache` with TTL (default 30 min) and a force-refresh REPL command.

**Integration with v1.0 stack:** ModelInfo registry feeds the new model-selection panel UI (prompt_toolkit fuzzy-select widget). Per-skill-step model is persisted to `config.local.yml` under a new `skill_steps` key — keep the gitignored-config pattern.

**Confidence:** HIGH — both endpoints verified via Context7 in this research session.

---

### 4. Cross-Platform Installers (免 uv)  ⚠ **USER-ACKNOWLEDGED UNCERTAIN**

**Risk flag:** User explicitly marked this 公开提问 / 未敲定. Treat conclusions below as a **starting bet**, not validated truth. Recommend a spike phase before committing.

**Primary recommendation: PyInstaller 6.14+ in `--onedir` mode, wrapped per-platform.**

| Aspect | PyInstaller | Nuitka | Briefcase | cx_Freeze |
|--------|------------|--------|-----------|-----------|
| Maturity | Battle-tested since 2005 | Active, fast-moving | BeeWare project, GUI-first | Older, less active |
| CLI/REPL friendly | ✓ Yes | ✓ Yes | ✗ GUI-focused | ✓ Yes |
| Cross-build (mac→win) | ✗ Must build on target OS | ✗ Same | ✗ Same | ✗ Same |
| Build time | Fast (seconds-minutes) | Slow (5-30 min, true compilation) | Medium | Fast |
| Bundle size | ~80-150 MB for our deps | ~50-100 MB (smaller, compiled) | Similar to PyInstaller | Similar |
| AV false positives on Win | Occasional (UPX adds risk; disable UPX) | Rare (looks like native C exe) | Rare | Occasional |
| RapidOCR / PyMuPDF compat | ✓ Known working (community hooks) | ⚠ Needs `--include-package-data` | Unknown | Unknown |
| Code signing | Documented for both mac (`codesign_identity=`) and win (signtool in spec) | Manual | Built-in `--identity` flag | Manual |
| Installer wrapper needed | Yes (create-dmg / Inno Setup) | Yes | Built-in (dmg/msi) | Yes |

**Why PyInstaller over Briefcase:** Briefcase's "package" command is attractive (built-in `.dmg` / `.msi`) but it's optimized for Toga-GUI apps, prefers a specific `pyproject.toml` shape and an app-bundle entry point. Our app is a REPL — Briefcase will still work but adds friction without clear win.

**Why PyInstaller over Nuitka (initially):** Build time matters for CI; Nuitka's 10× longer builds slow release cadence. Revisit Nuitka if (a) Windows AV false-positives become a user complaint or (b) PyInstaller bundle exceeds ~200 MB.

**Required signing reality (will surprise non-technical users if skipped):**
- **macOS:** Without signing + notarization, Gatekeeper blocks the app with "cannot be verified" dialog → users must right-click → Open. This is poor UX. Apple Developer ID costs $99/year. **Recommendation:** ship signed+notarized for macOS from day 1. Use `pyinstaller --codesign-identity "Developer ID Application: …"` then `xcrun notarytool submit`.
- **Windows:** Unsigned `.exe` triggers SmartScreen warning. Code-signing certs cost $200-700/year. **Recommendation:** ship unsigned for v1.1 with documented "Click 'More info' → Run anyway" workaround; budget for cert in v1.2.

**Concrete plan for v1.1 spike:**
1. Add `packaging/` dir with `cpho.spec` (PyInstaller spec) including hidden-import hooks for `rapidocr_onnxruntime`, `pymupdf`, `prompt_toolkit.contrib`.
2. CI matrix: `macos-latest` + `windows-latest` GitHub runners, build `.app` + `.exe` per release tag.
3. Wrap with `create-dmg` (mac) and Inno Setup (win) into single-download artifacts.
4. Document on README: "Download → drag to Applications / run installer → launch `cpho` from Terminal/PowerShell". This satisfies the "直接下载之后可以直接运行" intent BUT note the binary still launches a terminal; if user wants a click-to-launch GUI shell, that's out of scope (per v1.0 OOS).

**Open spike questions** to answer in dedicated phase:
- Does PyInstaller bundle of RapidOCR + ONNX runtime fit under reasonable size limits on Windows? (RapidOCR pulls ~200 MB ONNX models.)
- Should ONNX models be lazy-downloaded on first OCR call rather than bundled?
- Is there a Windows-specific PowerShell/cmd issue with our prompt_toolkit REPL color/Unicode handling?

**Confidence:** MEDIUM on direction (PyInstaller is the obvious 80% answer); **LOW** on whether everything Just Works without a hands-on spike. **Flag for roadmap: this needs its own phase, not a sub-task.**

---

### 5. Markdown/LaTeX/Image Knowledge File Storage

**Recommendation: Mirror v1.0 workspace pattern — directory-of-files + JSONL index, no DB.**

**Layout:**
```
<knowledge-root>/                    (either ~/.cpho/personal-knowledge or community-knowledge clone)
  knowledge/
    <category>/                       (mechanics, em, thermo, optics, modern, math-tools …)
      <slug>.md                       (markdown body; LaTeX is just $$…$$ inline)
      <slug>.assets/
        diagram-1.png
        handwritten-note.jpg
  kb_index.jsonl                       (auto-generated; one JSON object per knowledge file)
```

**Index schema (Pydantic StrictModel):**
```python
class KnowledgeEntry(StrictModel):
    file_path: Path                   # relative to knowledge-root
    tags: list[str]                   # extracted from front-matter OR LLM-inferred during normalization skill
    title: str
    summary: str                      # first paragraph or LLM-distilled
    source: Literal["personal", "community"]
    format: Literal["markdown", "latex", "image", "docx"]
    embedded_assets: list[Path]
    last_indexed: datetime
    content_hash: str                 # for change detection
```

**Why JSONL not SQLite:** consistent with v1.0; one knowledge base scales to thousands of files comfortably; trivially diffable in PRs to community repo; reindex by re-reading every file.

**Tag-based lookup integration with Explain v2:**
1. Problem has tag `bernoulli-flow` from index layer.
2. Explain v2 step 0 (before any board section): `kb_lookup(tag) → [KnowledgeEntry…]`.
3. If hit: load file content → embed into prompt template as authoritative reference → cite source path in output.
4. If miss: fuzzy-match via rapidfuzz across all entry titles + tags (threshold ~85); if still miss, proceed without KB and emit a log note.

**Front-matter convention** (optional — normalization skill writes this):
```markdown
---
tags: [bernoulli-flow, ideal-fluid, energy-conservation]
title: 伯努利方程在变截面管道中的应用
---
正文…
```

The "user doesn't need to give tags explicitly" requirement is satisfied by the **normalization skill** (two-step: draft → user review → knowledge zone), which fills in the front-matter on the draft and the user can edit before approving.

**Confidence:** HIGH — mirrors validated v1.0 patterns.

---

## Installation

```bash
# Core v1.1 additions (append to pyproject.toml)
uv add mammoth python-docx pillow httpx google-genai platformdirs diskcache rapidfuzz markdown-it-py olefile

# Packaging (dev-only)
uv add --dev pyinstaller
# If we pursue Nuitka fallback later:
# uv add --dev nuitka
```

---

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| mammoth for .docx | python-docx alone | When we need to *write* docx (we don't — read-only path) |
| `git clone` + `git pull` | git submodule | Never — submodules are a UX trap for non-technical users |
| `git clone` + `git pull` | gh release tarball | Fallback only, when user machine lacks `git` |
| PyInstaller | Nuitka | If bundle size or Windows AV becomes blocker post-v1.1 |
| PyInstaller | Briefcase | If we ever ship a GUI variant (v2+) |
| Roll our own model registry | litellm | Never — litellm hardcodes the model list, violating the v1.1 "no hardcoded list" requirement |
| google-genai SDK | Raw REST to `/v1beta/models` | If we want to drop an SDK to shrink installer; trivial replacement |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| **textract** | Unmaintained, drags in heavy Java deps for OCR we don't use here | mammoth + olefile + soffice escape hatch |
| **docx2txt** | Loses all structure (headings, lists) — bad input for LLM | mammoth (preserves semantic markdown) |
| **antiword** | Native binary, no Windows support out of box, .doc only | Detect .doc with olefile → ask user to convert |
| **litellm model registry** | Hardcoded list — directly violates "实时扒取" requirement | Custom `core/model_registry.py` calling provider endpoints |
| **git submodule for community KB** | Hostile UX for non-technical users | `git clone --depth 1` + `git pull` |
| **Briefcase for CLI app** | GUI-app-shaped tool, adds Toga ceremony for no win | PyInstaller --onedir + per-OS wrapper |
| **UPX compression on PyInstaller Windows builds** | Major source of AV false-positives | Disable UPX (`upx=False` in .spec) |
| **GitHub Contents API as primary distribution** | 60 req/hr unauthed; per-file slow; no offline cache | Real git clone |

---

## Stack Patterns by Variant

**If user has `git` installed:**
- Community KB via `git clone --depth 1` + `git pull --ff-only`
- User can fork, edit, PR back

**If user lacks `git`:**
- Detect via `shutil.which("git")` returning None
- Fallback to `httpx.get` of GitHub release ZIP, extract to same `community-knowledge/` path
- Read-only mode; surface "install git for contribute mode" hint

**If user is on macOS:**
- Installer: PyInstaller `--onedir` → `create-dmg` → signed+notarized `.dmg`
- Default config dir: `~/Library/Application Support/cpho/` (via platformdirs)

**If user is on Windows:**
- Installer: PyInstaller `--onedir` → Inno Setup → `.exe` installer
- Default config dir: `%APPDATA%\cpho\` (via platformdirs)
- Verify prompt_toolkit color/Unicode on Windows Terminal vs legacy `cmd.exe` — likely fine on Windows Terminal, may need fallback for legacy.

---

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| google-genai 1.33+ | Python 3.9+ | We're on 3.12 — fine |
| mammoth 1.8.x | Python 3.8+ | Pure Python |
| PyInstaller 6.14 | Python 3.8-3.13 | RapidOCR + ONNX runtime require explicit `--collect-data` |
| GitPython 3.1.43 | git binary 2.x+ on PATH | Prefer subprocess to skip this dep entirely if only basic ops |
| diskcache 5.6 | Any | SQLite-backed; cross-platform |

---

## Integration Touchpoints with v1.0 Stack

| v1.0 Component | v1.1 Touch | Action |
|----------------|------------|--------|
| `core/llm.py` (OpenRouter multimodal) | Knowledge import (image/docx); Explain v2 prompts | Reuse content-block schema unchanged; add new prompt templates only |
| `core/llm.py` model param | Model panel | Add per-call model override; route through new `model_registry` for validation |
| RapidOCR | Index path unchanged | NOT used for KB image import or other v1.1 skills (per design spec) |
| PyMuPDF | Index path unchanged | NOT used for KB (KB doesn't ingest PDFs in v1.1) |
| prompt_toolkit REPL | Model panel UI, `/kb` commands | Add fuzzy-select widget; register new slash commands |
| Jinja2 prompts | Explain v2 (3 boards) + normalization skill | Add 4 new template files; reuse layout |
| Pydantic StrictModel | KnowledgeEntry, ModelInfo | Add 2 new models; same patterns |
| JSONL index | kb_index.jsonl, model cache | New JSONL files alongside problem index |
| Typer CLI | New top-level commands: `cpho kb sync`, `cpho kb add <file>` | Pure additions |
| gitignored `config.local.yml` | `skill_steps.<skill>.<step>.model` | New key; same loading path |

---

## Sources

- Context7 `/llmstxt/openrouter_ai_llms_txt` — verified OpenRouter `GET /v1/models` endpoint, response schema (HIGH confidence)
- Context7 `/googleapis/python-genai` v1_33_0 — verified `client.models.list()` API and pagination (HIGH confidence)
- Context7 `/python-openxml/python-docx` — verified docx read API (HIGH confidence)
- Context7 `/pyinstaller/pyinstaller` v6.14.1 — verified onefile/onedir modes, macOS `codesign_identity`, Windows signtool integration (HIGH confidence)
- Context7 `/websites/nuitka_net_user-documentation` — verified standalone vs onefile vs app modes, GitHub Action recipe (HIGH confidence)
- Context7 `/beeware/briefcase` — verified .msi/.dmg packaging output, macOS notarization flags (MEDIUM — confirms our "not for CLI" call indirectly)
- `docs/new-understanding-2026-05-27.md` — v1.1 design intent
- `.planning/PROJECT.md` — validated v1.0 stack and v1.1 active requirements

**Tools NOT used due to environment issue:** WebSearch and WebFetch returned model-availability errors during this session. All claims above rely on Context7 (HIGH) and prior knowledge cross-checked against Context7. Where Context7 lacked coverage (Inno Setup, create-dmg, code-signing pricing), confidence is MEDIUM and based on prior knowledge — recommend independent verification during the v1.1 installer spike.

---

## Risk Flags for Roadmap

1. **Installer phase (item 4) needs a dedicated spike phase**, NOT a sub-task of another phase. User explicitly marked this 公开提问. Recommend allocating a research+prototype phase before committing.
2. **macOS code-signing budget decision** is a business/cost call ($99/yr Apple Developer ID). Surface to user before installer phase starts.
3. **RapidOCR ONNX model bundling** in PyInstaller may push installer >200 MB. Plan B: lazy-download on first OCR use.
4. **Live model fetching reliability**: provider APIs go down. Cache must serve stale-on-error. Build the fallback BEFORE shipping the panel.
5. **Community KB git dependency**: must gracefully handle "no git installed", "behind corporate proxy", "private fork URLs". Document each error per the v1.1 error-docs requirement.

---
*Stack research for: CPHO CLI v1.1 (Knowledge Base + Explain v2 + Model Panel + Installers)*
*Researched: 2026-05-27*
