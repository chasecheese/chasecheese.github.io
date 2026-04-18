# CLAUDE.md

Project-specific guidance for Claude Code working in this repo. Human-facing docs live in `README.md`.

## Build & deploy

Always invoke Python through the venv:

```sh
.venv/bin/python scripts/deploy.py           # full: build + pdf + publish (default)
.venv/bin/python scripts/deploy.py build     # regenerate index.generate*.html only
.venv/bin/python scripts/deploy.py generate  # build + render resume PDF, no publish
```

`deploy.py` itself auto-detects `.venv/bin/python`, so the child scripts it launches use the correct interpreter even if you invoke `deploy.py` with a different one.

One-time setup (if `.venv` is missing):

```sh
uv venv --python 3.12
uv pip install -e .
.venv/bin/python -m playwright install chromium
```

## File roles (separation of concerns)

```
contents/profile.json    # PERSONAL data — profile, experience, education, publications, etc.
contents/site.json       # SITE CHROME — layouts, icon_emoji, footer_note
contents/analytics.html  # OPTIONAL raw <script> snippet (injected into main page only)
scripts/build_site.py    # profile.json + site.json + analytics.html -> HTML
scripts/render_pdf.py    # HTML -> PDF via headless Chromium
scripts/deploy.py        # orchestrates build -> generate -> deploy stages
styles/site.css          # site-specific CSS; class names mirror build_site.py output
bootstrap-5.3.2-dist/    # vendored Bootstrap — do NOT modify
fonts/                   # vendored Fira Sans woff2 files — do NOT modify
```

Edit rules:

- Personal content changes → `contents/profile.json` only.
- Visual / layout changes → `contents/site.json` and/or `styles/site.css`.
- Schema or rendering logic changes → `scripts/build_site.py` (and update `README.md` schema table).

## Output files

- `index.html` + `files/resume.pdf` — **tracked** and served by GitHub Pages; keep in sync via `deploy.py deploy`.
- `index.generate.html`, `index.generate.resume.html`, `index.generate.resume.pdf` — **gitignored** build artifacts; safe to regenerate anytime.

Do not commit `index.generate.*`.

## Schema conventions (must preserve)

- `publications[].authors[]` accepts bare strings (`"Jane Doe"`) or `{name, self?}` objects. Self-highlighting is explicit per entry — **do not re-introduce implicit name matching** based on `profile.name`.
- `publications[].tag` defaults to `[{abbr}]` when omitted; only set explicitly when the display should differ from the abbreviation (e.g. `abbr: "IEEE TKDE'24"`, `tag: "[TKDE'24]"`).
- `research_interests[]` accepts bare strings; upgrade to `{text, url}` only when a link is needed.
- `site.json` `layout` and `resume_layout` are **shallow-merged** over `DEFAULT_MAIN_LAYOUT` / `DEFAULT_RESUME_LAYOUT` in `build_site.py`. Users can override just a subset of keys (e.g. only `spacers`).

## CSS ↔ Python coupling

Class names use BEM (`block__element--modifier`). The HTML emitters in `scripts/build_site.py` and the rules in `styles/site.css` must stay in sync:

- When renaming a CSS class, grep `scripts/build_site.py` for the old class string and update the emitter.
- When adding a render block, reuse an existing BEM block where possible (e.g. `timeline`, `publication`, `ta-list`, `award-list`).
- Keep visual values (width, color, font-family) in `styles/site.css`; do **not** inline them as HTML `style="..."` attributes in the Python render code.

## Dependency management

- Python deps live in `pyproject.toml`; add new ones there and reinstall via `uv pip install -e .`.
- `.python-version` pins Python 3.12 for uv.
- Do not add runtime dependencies that aren't strictly needed for the build/PDF pipeline.
