# chasecheese.github.io

Homepage is generated from JSON frontmatter + templates. Use the helper scripts below to build, generate PDF, and deploy.

## Quick start
- `python scripts/deploy.py build` — produce `index.generate.html` and `index.generate.resume.html`
- `python scripts/deploy.py generate` — build + render `index.generate.resume.pdf`
- `python scripts/deploy.py deploy` — full pipeline (build + pdf + move to `index.html` and `files/resume.pdf`)

## Content configuration (`contents/index.md`)
Frontmatter fields drive the page:
- `layout.left|main|right` — bootstrap column widths
- `icon_emoji` — favicon emoji
- `analytics_html` — raw analytics snippet (e.g., GA). Leave empty to skip, or replace GA ID here
- `profile.name|avatar|titles[]|emails[]`
- `profile.links[]` — `label`, `url` (e.g., GitHub, CV)
- `research_interests[]` — `text`, optional `url`
- `experience[]`, `education[]` — each with `org`, `logo`, `date`, `roles[]`
- `publications[]` — `tag`, `title`, optional `link`, `authors[]` (`self: true` to highlight), `venue`, `abbr`
- `teaching_assistant[]`, `awards[]` — `title`, `date`
- `footer_note` — footer text

Edit the JSON frontmatter, then run one of the deploy stages.

## Tools
- `scripts/build_site.py` — converts frontmatter to HTML (main + resume layout)
- `scripts/render_pdf.py` — renders HTML to PDF (uses Playwright/Chromium)
- `scripts/deploy.py` — orchestrates build/generate/deploy stages

Prereqs: Python 3; for PDF, install Playwright once:
```
pip install playwright
python -m playwright install chromium
```