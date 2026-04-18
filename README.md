# chasecheese.github.io

Static personal homepage + PDF résumé, generated from a handful of content and config files.

## Quick start

Edit the content files under `contents/`, then run:

```sh
.venv/bin/python scripts/deploy.py           # full: build + pdf + publish
.venv/bin/python scripts/deploy.py build     # just regenerate *.generate.html
.venv/bin/python scripts/deploy.py generate  # build + resume PDF, no publish
```

`deploy.py` auto-detects `.venv/bin/python`, so you do not need to activate the venv first.

## One-time setup

Requires [uv](https://docs.astral.sh/uv/) and Python 3.12:

```sh
uv venv --python 3.12
uv pip install -e .          # or: uv pip install playwright
.venv/bin/python -m playwright install chromium
```

## Project layout

```text
contents/profile.json         # your CV data — personal content
contents/site.json            # site chrome: layouts, favicon, footer
contents/analytics.html       # analytics snippet injected verbatim into main page
scripts/build_site.py         # contents -> HTML (main + resume layouts)
scripts/render_pdf.py         # HTML -> PDF via headless Chromium
scripts/deploy.py             # build / generate / deploy orchestrator
styles/site.css               # site-specific CSS on top of Bootstrap
bootstrap-5.3.2-dist/         # vendored Bootstrap (offline PDF rendering needs it)
fonts/                        # Fira Sans woff2 files used by site.css
files/                        # avatars, logos, and the published resume.pdf
index.html                    # deployed homepage (copied from index.generate.html)
index.generate*.{html,pdf}    # build artifacts (gitignored)
```

Content is split by concern so you never have to mix "my data" with "how the site renders":

- **`contents/profile.json`** — your profile, experience, education, publications, etc.
- **`contents/site.json`** — layout widths, section spacing, favicon emoji, footer line.
- **`contents/analytics.html`** — whatever `<script>` your analytics provider gives you.

## `contents/profile.json` (personal data)

Plain JSON — your CV.

| Key | Type | Notes |
| --- | --- | --- |
| `profile.name` / `avatar` / `titles[]` / `emails[]` | — | Hero block |
| `profile.links[]` | `{label, url}` | Links row under the hero |
| `research_interests[]` | `str` \| `{text, url?}` | String shorthand when no link needed |
| `experience[]` / `education[]` | `{org, logo, date, roles[]}` | Timeline entries |
| `publications[]` | `{abbr, title, venue, authors[], link?, tag?}` | `tag` defaults to `[abbr]` when omitted |
| `teaching_assistant[]` / `awards[]` | `{title, date}` | Simple list rows |

### Author entries

`publications[].authors[]` accepts either:

- a bare string — `"Haonan Li"` (for co-authors)
- an object — `{ "name": "Mingxin Li", "self": true }` (to highlight yourself)

Marking `self` is explicit on purpose: author names in papers don't always match your profile name exactly, and fork-users need a clear, local signal instead of implicit name matching.

## `contents/site.json` (site chrome)

| Key | Type | Notes |
| --- | --- | --- |
| `icon_emoji` | str | Favicon glyph (rendered as SVG data URL) |
| `footer_note` | str | Footer text after the 🌈 |
| `layout.left` / `main` / `right` | int | Bootstrap col widths for main page (sum ≤ 12) |
| `layout.spacers` | int | Blank rows between sections on main page |
| `resume_layout` | same shape as `layout` | Override used when rendering the résumé HTML |

Both layouts are merged over built-in defaults (`main: {1,10,1,spacers:2}`, `resume: {0,12,0,spacers:1}`), so you can override just the fields you care about.

## `contents/analytics.html` (optional)

Injected verbatim into the `<head>` of the main page (never the résumé). Paste whatever snippet your provider gives you — Google Analytics, Plausible, Umami, a custom script — into that file, or delete the file to disable analytics entirely.

## Deploy flow

`scripts/deploy.py` runs staged pipelines keyed by the CLI arg:

1. **build** — `build_site.py` reads `contents/` and writes `index.generate.html` (main) and `index.generate.resume.html` (full-width).
2. **generate** — `render_pdf.py` turns the resume HTML into `index.generate.resume.pdf`.
3. **deploy** — copies `index.generate.html` → `index.html` and `index.generate.resume.pdf` → `files/resume.pdf`.

Only `index.html` and `files/resume.pdf` are served by GitHub Pages; the `*.generate.*` intermediates are gitignored.

## Troubleshooting

- **Playwright missing** — rerun the one-time setup; confirm `.venv/bin/playwright` exists.
- **Chromium not installed** — `.venv/bin/python -m playwright install chromium`.
- **Fonts look wrong in PDF** — `render_pdf.py` waits for `networkidle`; make sure the woff2 files under `fonts/` are reachable from the HTML path.
- **Change analytics provider** — replace the snippet in `contents/analytics.html`.
