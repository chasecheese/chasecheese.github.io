# AGENTS.md

Guidance for coding agents working in this repository. Human-facing template
usage docs live in `README.md`.

## Project Overview

This is a static personal homepage template with a generated PDF CV. Personal
content lives in JSON files, while Python scripts render the web page and PDF.

## Commands

Use the virtualenv Python when running project scripts:

```sh
.venv/bin/python scripts/deploy.py build
.venv/bin/python scripts/deploy.py generate
.venv/bin/python scripts/deploy.py
```

- `build` regenerates the HTML preview files.
- `generate` builds HTML and renders the PDF CV.
- The default command builds, renders, and copies publishable files into place.

If the virtualenv is missing:

```sh
uv venv --python 3.12
uv pip install -e .
.venv/bin/python -m playwright install chromium
```

## File Roles

```text
contents/profile.json    # Personal CV/homepage content
contents/site.json       # Site settings: layout, favicon emoji, footer emoji, footer text
contents/analytics.html  # Optional analytics snippet for the main page only
scripts/build_site.py    # JSON content and site settings -> HTML
scripts/render_pdf.py    # HTML -> PDF via Playwright/Chromium
scripts/deploy.py        # Build / generate / publish workflow
styles/site.css          # Site-specific CSS
bootstrap-5.3.2-dist/    # Vendored Bootstrap files
fonts/                   # Vendored web fonts
files/                   # Public assets and published resume PDF
```

## Editing Rules

- Personal content changes should go in `contents/profile.json`.
- Site-level settings should go in `contents/site.json`.
- Visual changes should go in `styles/site.css`.
- Rendering or schema changes should go in `scripts/build_site.py`.
- Update `README.md` when changing user-facing setup, commands, or content
  format.
- Do not modify vendored Bootstrap or font files unless the task explicitly
  requires it.

## Generated And Published Files

- `index.generate.html`, `index.generate.resume.html`, and
  `index.generate.resume.pdf` are generated preview/build artifacts and should
  not be manually edited.
- `index.html` and `files/resume.pdf` are the publishable GitHub Pages outputs.
  Keep them in sync by running the default deploy command when publishing.

## Schema Conventions

- `publications[].authors[]` accepts either plain strings or
  `{ "name": "...", "self": true }` objects.
- Self-author highlighting is explicit per publication. Do not infer it from
  `profile.name`.
- `publications[].tag` defaults to `[{abbr}]` when omitted.
- `research_interests[]` accepts plain strings, or `{text, url}` objects when a
  link is needed.
- `site.json` `layout` and `resume_layout` are shallow-merged over defaults in
  `scripts/build_site.py`.
- `site.json` `footer_emoji` defaults to `"🌈"`; set it to an empty string to
  render the footer without any leading glyph.

## CSS And HTML Coupling

Class names emitted by `scripts/build_site.py` are styled in `styles/site.css`.
When renaming or adding classes, update both sides together.

Use the existing BEM-style naming pattern, for example:

```text
profile__link
timeline__item
publication__author--self
award-list__item
```

Keep visual constants such as colors, font families, spacing, and widths in CSS
instead of inline HTML styles.

## Dependency Notes

- Python dependencies live in `pyproject.toml`.
- `.python-version` pins the Python version for `uv`.
- Avoid adding new runtime dependencies unless they materially simplify the
  build or PDF generation workflow.
