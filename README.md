# Personal Homepage Template

A small static-site template for a personal academic homepage and PDF CV. The
site is generated from JSON content files, so most updates only require editing
your profile data instead of touching HTML.

## First-Time Setup

This project uses Python 3.12 and Playwright for PDF generation.

```sh
uv venv --python 3.12
uv pip install -e .
.venv/bin/python -m playwright install chromium
```

After setup, you can use `scripts/deploy.py` for the normal workflow. The script
will automatically use `.venv/bin/python` when it exists.

## Customize The Template

1. Edit `contents/profile.json` with your name, links, education, experience,
   publications, teaching, and awards.
2. Put your images and other public files in `files/`, then reference them from
   `profile.json`.
3. Adjust site-level settings in `contents/site.json`.
4. Build the site:

```sh
.venv/bin/python scripts/deploy.py build
```

Open `index.generate.html` in a browser to preview the generated page.

## Common Commands

```sh
.venv/bin/python scripts/deploy.py build
.venv/bin/python scripts/deploy.py generate
.venv/bin/python scripts/deploy.py
```

- `build` regenerates the HTML preview files.
- `generate` also renders the PDF CV.
- The default command builds, renders the PDF, and copies the publishable files
  into place.

## What To Edit

```text
contents/profile.json    # Your personal content
contents/site.json       # Site settings such as layout, icon, and footer text
contents/analytics.html  # Optional analytics snippet
files/                   # Public assets such as avatar, logos, and PDFs
styles/site.css          # Visual styling
```

Most template users only need `contents/profile.json`, `contents/site.json`, and
`files/`. Edit `styles/site.css` when you want to change the visual design.

## Content Format

`contents/profile.json` is the main source of truth for the page. It supports
these sections:

| Field | Purpose |
| --- | --- |
| `profile` | Name, avatar, titles, email addresses, and profile links |
| `research_interests` | Short text items, optionally with links |
| `experience` | Timeline entries with organization, logo, date, and roles |
| `education` | Timeline entries with school, logo, date, and degree/advisor text |
| `publications` | Publication title, venue, authors, link, and display tag |
| `teaching_assistant` | Simple title/date rows |
| `awards` | Simple title/date rows |

Authors in `publications[].authors` can be written as plain strings:

```json
"Jane Doe"
```

Use an object when you want to highlight yourself:

```json
{ "name": "Your Name", "self": true }
```

Research interests can also be plain strings, or objects when a link is useful:

```json
{ "text": "Systems", "url": "https://example.com" }
```

## Site Settings

`contents/site.json` controls settings that are not personal CV content:

| Field | Purpose |
| --- | --- |
| `icon_emoji` | Emoji used for the browser favicon |
| `footer_emoji` | Emoji prefix shown before the footer text (empty string to disable) |
| `footer_note` | Footer text |
| `layout` | Column layout and section spacing for the web page |
| `resume_layout` | Layout override for the PDF CV HTML |

The layout fields are Bootstrap column widths. Keep `left + main + right` within
12.

## Generated Files

The build scripts create intermediate files:

```text
index.generate.html
index.generate.resume.html
index.generate.resume.pdf
```

The publishable files are:

```text
index.html
files/resume.pdf
```

For GitHub Pages, commit the publishable files after running the default deploy
command.

## Project Layout

```text
scripts/build_site.py   # JSON content -> HTML
scripts/render_pdf.py   # HTML -> PDF
scripts/deploy.py       # Build / generate / publish workflow
styles/site.css         # Site-specific CSS
bootstrap-5.3.2-dist/   # Local Bootstrap files used by the generated page
fonts/                  # Local web fonts
templates/              # Optional/reference template files
```

## Troubleshooting

- If PDF generation fails because Chromium is missing, run
  `.venv/bin/python -m playwright install chromium`.
- If fonts or images look wrong, check that the paths in `profile.json` point to
  files that exist in the repository.
- If `index.html` looks stale, run the default deploy command instead of only
  running `build`.
