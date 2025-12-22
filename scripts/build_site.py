#!/usr/bin/env python3
"""
Builds the site HTML from a Markdown file that contains a JSON frontmatter block.

Usage:
  python scripts/build_site.py            # uses contents/content.md -> <repo_root>/*.generate.html + *.resume.html
  python scripts/build_site.py input.md   # outputs to repo root with *.generate.html + *.resume.html
  python scripts/build_site.py input.md output.html  # primary output name at repo root; resume also emitted

The Markdown file should start with a frontmatter block:
---json
{ ...json data... }
---
"""

from __future__ import annotations

import json
import sys
from html import escape
from pathlib import Path
from urllib.parse import quote
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent


def read_frontmatter(md_path: Path) -> Dict[str, Any]:
  text = md_path.read_text(encoding="utf-8")
  if not text.startswith("---json"):
    raise ValueError("Markdown must start with a ---json frontmatter block.")
  parts = text.split("---", 2)
  if len(parts) < 3:
    raise ValueError("Frontmatter must be terminated by a line with ---")
  frontmatter = parts[1]
  return json.loads(frontmatter.strip().removeprefix("json").strip())


def esc(val: Any) -> str:
  return escape(str(val)) if val is not None else ""


def favicon_data_url(emoji: str) -> str:
  glyph = emoji or "🌐"
  svg = f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='0.9em' font-size='90'>{glyph}</text></svg>"
  return "data:image/svg+xml," + quote(svg)


def col_classes(layout: Dict[str, Any]) -> Tuple[str, str, str]:
  left = int(layout.get("left", layout.get("side", 2)))
  right = int(layout.get("right", layout.get("side_right", layout.get("side-right", left))))
  if "main" in layout:
    main = int(layout.get("main"))
  else:
    main = 12 - left - right
  if main <= 0:
    main = 8
  return (f"col-md-{left}", f"col-md-{main}", f"col-md-{right}")


def render_profile(data: Dict[str, Any], cols: Tuple[str, str, str]) -> str:
  left_col, main_col, right_col = cols
  links_html = "".join(
      f'<a class="link-accent profile__link" href="{esc(link.get("url"))}" target="_blank" '
      f'rel="noopener noreferrer" aria-label="{esc(link.get("label"))}">{esc(link.get("label"))}</a>'
      for link in data.get("links", [])
      if link.get("url")
  )
  return f"""
  <div class="container">
    <div class="row">
      <div class="{left_col}"></div>
      <div class="{main_col}">
        <div class="media">
          <a class="media-left" href="#">
            <img src="{esc(data.get("avatar"))}" class="img-thumbnail rounded-circle float-start profile__avatar"
              style="width: 180px;" alt="{esc(data.get("name"))}" loading="lazy" decoding="async">
          </a>
          <div class="media-body">
            <div class="profile text-end">
              <h1>{esc(data.get("name"))}</h1>
              {''.join(f'<span class="profile__meta">{esc(line)}<br /></span>' for line in data.get("titles", []))}
              {''.join(f'<span class="profile__contact">{esc(email)}<br /></span>' for email in data.get("emails", []))}
              <div class="profile__links">
                {links_html}
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="{right_col}"></div>
    </div>
  </div>
  """


def render_interests(items: List[Dict[str, Any]], cols: Tuple[str, str, str]) -> str:
  left_col, main_col, right_col = cols
  interests = []
  for item in items:
    text = esc(item.get("text"))
    url = item.get("url")
    if url:
      interests.append(f'<a target="_blank" href="{esc(url)}" class="link-accent" rel="noopener noreferrer">{text}</a>')
    else:
      interests.append(text)
  return f"""
  <div class="container">
    <div class="row">
      <div class="{left_col}"></div>
      <div class="{main_col}">
        <h2>Research Interests</h2>
      </div>
      <div class="{right_col}"></div>
    </div>
    <div class="row">
      <div class="{left_col}"></div>
      <div class="{main_col}">
        <div class="row">
          <span class="research__item">
            {", ".join(interests)}
          </span>
        </div>
      </div>
      <div class="{right_col}"></div>
    </div>
  </div>
  """


def render_timeline(title: str, entries: List[Dict[str, Any]], cols: Tuple[str, str, str]) -> str:
  left_col, main_col, right_col = cols
  items_html = []
  for entry in entries:
    items_html.append(
        f"""
          <div class="timeline__item">
            <span class="timeline__header">
              <span class="timeline__org">
                <img src="{esc(entry.get("logo"))}" alt="{esc(entry.get("org"))} logo" class="timeline__logo" />
                <span class="timeline__name">{esc(entry.get("org"))}</span>
              </span>
              <span class="timeline__date">{esc(entry.get("date"))}</span>
            </span>
            {''.join(f'<span class="timeline__role">{esc(role)}</span>' for role in entry.get("roles", []))}
          </div>
        """
    )
  return f"""
  <div class="container">
    <div class="row">
      <div class="{left_col}"></div>
      <div class="{main_col}">
        <h2>{esc(title)}</h2>
      </div>
      <div class="{right_col}"></div>
    </div>
    <div class="row">
      <div class="{left_col}"></div>
      <div class="{main_col}">
        <div class="timeline">
          {''.join(items_html)}
        </div>
      </div>
      <div class="{right_col}"></div>
    </div>
  </div>
  """


def render_publications(entries: List[Dict[str, Any]], cols: Tuple[str, str, str]) -> str:
  left_col, main_col, right_col = cols
  items_html = []
  for entry in entries:
    link = entry.get("link")
    link_html = (
        f'<a class="link-accent publication__link" target="_blank" href="{esc(link)}" rel="noopener noreferrer">[Link]</a>'
        if link
        else '<span class="publication__link link-plain">[Link]</span>'
    )
    authors_html = []
    authors = entry.get("authors", [])
    for idx, a in enumerate(authors):
      cls = "publication__author publication__author--self" if a.get("self") else "publication__author"
      name = esc(a.get("name"))
      sep = "" if idx == len(authors) - 1 else ", "
      authors_html.append(f'<span class="{cls}">{name}{sep}</span>')
    items_html.append(
        f"""
          <div class="publication__item">
            <b><span class="publication__tag">{esc(entry.get("tag"))}</span></b>
            <b class="publication__title">{esc(entry.get("title"))}</b>
            {link_html}
            <br />
            {"".join(authors_html)}
            <br />
            <span class="publication__venue">{esc(entry.get("venue"))}</span>
            <span class="publication__abbr">({esc(entry.get("abbr"))})</span>
          </div>
        """
    )
  return f"""
  <div class="container">
    <div class="row">
      <div class="{left_col}"></div>
      <div class="{main_col}">
        <h2>Publications</h2>
      </div>
      <div class="{right_col}"></div>
    </div>
    <div class="row">
      <div class="{left_col}"></div>
      <div class="{main_col}">
        <div class="publication">
          {''.join(items_html)}
        </div>
      </div>
      <div class="{right_col}"></div>
    </div>
  </div>
  """


def render_list_section(title: str, items: List[Dict[str, Any]], item_cls: str, cols: Tuple[str, str, str]) -> str:
  left_col, main_col, right_col = cols
  list_items = []
  for item in items:
    list_items.append(
        f'<li class="{item_cls}"><span class="{item_cls}__title">{esc(item.get("title"))}</span>'
        f' <span class="{item_cls}__date">{esc(item.get("date"))}</span></li>'
    )
  return f"""
  <div class="container">
    <div class="row">
      <div class="{left_col}"></div>
      <div class="{main_col}">
        <h2>{esc(title)}</h2>
      </div>
      <div class="{right_col}"></div>
    </div>
    <div class="row">
      <div class="{left_col}"></div>
      <div class="{main_col}">
        <ul class="list-unstyled mb-0 {item_cls.replace('__item','')}">
          {''.join(list_items)}
        </ul>
      </div>
      <div class="{right_col}"></div>
    </div>
  </div>
  """


def render_footer(note: str, cols: Tuple[str, str, str]) -> str:
  left_col, _, right_col = cols
  return f"""
  <div class="container">
    <div class="row">
      <div class="{left_col}"></div>
      <footer class="text-center">
        <div>
          <span class="footer__note">&#127752; {esc(note)}</span>
        </div>
      </footer>
      <div class="{right_col}"></div>
    </div>
  </div>
  """


def build_page(data: Dict[str, Any], layout_override: Dict[str, Any] | None = None) -> str:
  spacer = '<div class="row"><p></p></div>'
  double_spacer = spacer + "\n" + spacer
  cols = col_classes(layout_override or data.get("layout", {}))
  icon_href = favicon_data_url(data.get("icon_emoji") or data.get("favicon_emoji") or "🌐")
  return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="This site is built by bootstrap v5.3.2">
  <meta name="author" content="{esc(data.get("profile", {}).get("name"))}">
  <meta content="text/html; charset=UTF-8" http-equiv="Content-Type" />
  <link href="./bootstrap-5.3.2-dist/css/bootstrap.min.css" rel="stylesheet" type="text/css">
  <title>{esc(data.get("profile", {}).get("name", "Site"))}</title>
  <link href="./styles/site.css" rel="stylesheet" type="text/css">
  <link rel="icon" href="{icon_href}">
</head>
<body>
  {render_profile(data.get("profile", {}), cols)}
  {spacer}
  <div class="container">
    <div class="row">
      <div class="{cols[0]}"></div>
      <div class="{cols[1]}">
        <p align="center">
          <hr />
        </p>
      </div>
      <div class="{cols[2]}"></div>
    </div>
  </div>
  {double_spacer}
  {render_interests(data.get("research_interests", []), cols)}
  {double_spacer}
  {render_timeline("Experience", data.get("experience", []), cols)}
  {double_spacer}
  {render_timeline("Education", data.get("education", []), cols)}
  {double_spacer}
  {render_publications(data.get("publications", []), cols)}
  {double_spacer}
  {render_list_section("Teaching Assistant", data.get("teaching_assistant", []), "ta-list__item", cols)}
  {double_spacer}
  {render_list_section("Awards and Honors", data.get("awards", []), "award-list__item", cols)}
  {double_spacer}
  {render_footer(data.get("footer_note", ""), cols)}
</body>
</html>
"""


def main(argv: List[str]) -> None:
  md_path = Path(argv[1]) if len(argv) > 1 else ROOT / "contents/content.md"
  if len(argv) > 2:
    out_name = Path(argv[2]).name
  else:
    out_name = md_path.with_suffix(".generate.html").name
  out_path = ROOT / out_name

  data = read_frontmatter(md_path)

  html = build_page(data)
  out_path.write_text(html, encoding="utf-8")
  print(f"Wrote {out_path}")

  resume_out = ROOT / (out_path.stem + ".resume" + out_path.suffix)
  resume_layout = {"left": 0, "main": 12, "right": 0}
  resume_html = build_page(data, layout_override=resume_layout)
  resume_out.write_text(resume_html, encoding="utf-8")
  print(f"Wrote {resume_out}")


if __name__ == "__main__":
  main(sys.argv)

