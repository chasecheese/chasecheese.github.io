#!/usr/bin/env python3
"""
Build the site HTML from structured content files under contents/.

Default inputs / outputs:
  personal data : contents/profile.json
  site chrome   : contents/site.json       (layouts, favicon, footer)
  analytics     : contents/analytics.html  (raw snippet, optional)
  main output   : index.generate.html      (main layout)
  resume output : index.generate.resume.html (full-width override for PDF)

Usage:
  python scripts/build_site.py                                # defaults
  python scripts/build_site.py --input contents/alt.json      # custom data file
  python scripts/build_site.py --output bar.html              # custom main output
"""

from __future__ import annotations

import argparse
import json
import sys
from html import escape
from pathlib import Path
from typing import Any, Dict, List, Tuple
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = ROOT / "contents" / "profile.json"
DEFAULT_ANALYTICS_FILE = ROOT / "contents" / "analytics.html"
DEFAULT_PUBLICATIONS = ROOT / "contents" / "publications.json"
DEFAULT_SITE_CONFIG = ROOT / "contents" / "site.json"
DEFAULT_MAIN_LAYOUT: Dict[str, Any] = {"left": 1, "main": 10, "right": 1, "spacers": 2}
DEFAULT_RESUME_LAYOUT: Dict[str, Any] = {"left": 0, "main": 12, "right": 0, "spacers": 1}


def read_content(json_path: Path) -> Dict[str, Any]:
  try:
    return json.loads(json_path.read_text(encoding="utf-8"))
  except FileNotFoundError:
    raise ValueError(f"{json_path}: file not found") from None
  except json.JSONDecodeError as e:
    raise ValueError(f"{json_path}: invalid JSON: {e}") from e


def esc(val: Any) -> str:
  return escape(str(val)) if val is not None else ""


def favicon_data_url(emoji: str) -> str:
  glyph = emoji or "🌐"
  svg = (
      f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'>"
      f"<text y='0.9em' font-size='90'>{glyph}</text></svg>"
  )
  return "data:image/svg+xml," + quote(svg)


def col_classes(layout: Dict[str, Any]) -> Tuple[str, str, str]:
  left = int(layout.get("left", 2))
  right = int(layout.get("right", left))
  main = int(layout["main"]) if "main" in layout else max(12 - left - right, 1)
  return (f"col-md-{left}", f"col-md-{main}", f"col-md-{right}")


def read_analytics_snippet(path: Path | None) -> str:
  """Return raw HTML from an analytics snippet file, or empty string if missing."""
  if path is None or not path.exists():
    return ""
  return path.read_text(encoding="utf-8").strip()


def read_site_config(path: Path) -> Dict[str, Any]:
  """Load site-wide rendering config (layout, favicon, footer). Missing file = empty."""
  if not path.exists():
    return {}
  return json.loads(path.read_text(encoding="utf-8"))


def normalize_interest(item: Any) -> Dict[str, Any]:
  if isinstance(item, str):
    return {"text": item}
  return item or {}


def normalize_author(item: Any) -> Dict[str, Any]:
  if isinstance(item, str):
    return {"name": item}
  return item or {}


def render_profile(profile: Dict[str, Any], cols: Tuple[str, str, str]) -> str:
  left_col, main_col, right_col = cols
  return f"""
  <div class="container">
    <div class="row">
      <div class="{left_col}"></div>
      <div class="{main_col}">
        <div class="media">
          <a class="media-left" href="#">
            <img src="{esc(profile.get("avatar"))}" class="img-thumbnail rounded-circle float-start profile__avatar"
              alt="{esc(profile.get("name"))}" loading="lazy" decoding="async">
          </a>
          <div class="media-body">
            <div class="profile text-end">
              <h1>{esc(profile.get("name"))}</h1>
              {''.join(f'<span class="profile__meta">{esc(line)}<br /></span>' for line in profile.get("titles", []))}
              {''.join(f'<span class="profile__contact">{esc(email)}<br /></span>' for email in profile.get("emails", []))}
            </div>
          </div>
        </div>
      </div>
      <div class="{right_col}"></div>
    </div>
  </div>
  """


def render_profile_links(links: List[Dict[str, Any]], cols: Tuple[str, str, str]) -> str:
  left_col, main_col, right_col = cols
  link_items = [
      f'<a class="link-accent profile__link" href="{esc(link.get("url"))}" target="_blank" '
      f'rel="noopener noreferrer" aria-label="{esc(link.get("label"))}">{esc(link.get("label"))}</a>'
      for link in links
      if link.get("url")
  ]
  if not link_items:
    return ""
  return f"""
  <div class="container">
    <div class="row">
      <div class="{left_col}"></div>
      <div class="{main_col}">
        <div class="profile__links">
          {''.join(link_items)}
        </div>
      </div>
      <div class="{right_col}"></div>
    </div>
  </div>
  """


def render_interests(items: List[Any], cols: Tuple[str, str, str]) -> str:
  left_col, main_col, right_col = cols
  interests = []
  for raw in items:
    item = normalize_interest(raw)
    text = esc(item.get("text"))
    url = item.get("url")
    if url:
      interests.append(
          f'<a target="_blank" href="{esc(url)}" class="link-accent" rel="noopener noreferrer">{text}</a>'
      )
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


def render_role(role: Any) -> str:
  if isinstance(role, str):
    return esc(role)
  text = esc(role.get("text", ""))
  for fragment, url in (role.get("links") or {}).items():
    escaped_fragment = esc(fragment)
    link = (f'<a class="link-accent" href="{esc(url)}" target="_blank" '
            f'rel="noopener noreferrer">{escaped_fragment}</a>')
    text = text.replace(escaped_fragment, link)
  return text


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
            {''.join(f'<span class="timeline__role">{render_role(role)}</span>' for role in entry.get("roles", []))}
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
    abbr = entry.get("abbr", "")
    title = esc(entry.get("title"))
    link = entry.get("link")

    if link:
      title_html = f'<a class="publication__title-link" href="{esc(link)}" target="_blank" rel="noopener noreferrer">{title}</a>'
    else:
      title_html = title

    badge_html = f'<b class="publication__badge">{esc(abbr)}</b> / ' if abbr else ""

    authors = [normalize_author(a) for a in entry.get("authors", [])]
    max_visible = 10
    self_idx = next((i for i, a in enumerate(authors) if a.get("self")), -1)
    if self_idx >= max_visible - 1:
      max_visible = self_idx + 2
    need_collapse = len(authors) > max_visible
    hidden_count = len(authors) - max_visible

    author_parts = []
    for idx, a in enumerate(authors):
      name = esc(a.get("name"))
      is_hidden = need_collapse and idx >= max_visible
      is_last = idx == len(authors) - 1

      if need_collapse and idx == max_visible:
        author_parts.append(
            f'<span class="publication__more" role="button" '
            f"onclick=\"this.style.display='none';"
            f"var p=this.closest('.publication__authors');"
            f"var h=p.querySelectorAll('.publication__author-hidden');"
            f"h.forEach(function(e,i){{e.style.display='';e.style.opacity='0';"
            f"setTimeout(function(){{e.style.opacity='1'}},i*40)}})\">"
            f"and {hidden_count} more</span>"
        )

      if is_hidden:
        if a.get("self"):
          author_parts.append(
              f'<span class="publication__author-hidden" style="display:none">'
              f', <span class="publication__author--self"><b><u>{name}</u></b></span></span>'
          )
        else:
          author_parts.append(
              f'<span class="publication__author-hidden" style="display:none">'
              f', <span class="publication__author">{name}</span></span>'
          )
      else:
        is_last_visible = (need_collapse and idx == max_visible - 1) or (not need_collapse and is_last)
        sep = "" if is_last_visible else ", "
        if a.get("self"):
          author_parts.append(f'<span class="publication__author--self"><b><u>{name}</u></b></span>{sep}')
        else:
          author_parts.append(f'<span class="publication__author">{name}</span>{sep}')

    venue = esc(entry.get("venue", ""))

    award = entry.get("award")
    award_html = f'\n                <div class="publication__award">{esc(award)}</div>' if award else ""

    links_list = list(entry.get("links", []))
    if not links_list and link:
      links_list = [{"label": "PAPER", "url": link}]
    link_parts = []
    for lnk in links_list:
      url = lnk.get("url", "")
      label = esc(lnk.get("label", "Link"))
      if url:
        link_parts.append(
            f'<a class="publication__btn" href="{esc(url)}" '
            f'target="_blank" rel="noopener noreferrer">{label}</a>'
        )

    bib = entry.get("bib")
    if bib:
      link_parts.append(
          '<a class="publication__btn" role="button" '
          "onclick=\"var b=this.closest('.publication__entry').querySelector('.publication__bib');"
          "b.style.display=b.style.display==='none'?'':'none'\">BIB</a>"
      )

    links_html = f'\n                <div class="publication__links">{"".join(link_parts)}</div>' if link_parts else ""
    bib_html = f'\n                <div class="publication__bib" style="display:none"><pre>{esc(bib)}</pre></div>' if bib else ""

    items_html.append(
        f"""
            <li>
              <div class="publication__entry">
                <div class="publication__title">
                  {badge_html}{title_html}
                </div>
                <div class="publication__authors">
                  {"".join(author_parts)}
                </div>
                <div class="publication__venue">
                  <em>{venue}</em>
                </div>{award_html}{links_html}{bib_html}
              </div>
            </li>
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
        <ul class="publication list-unstyled">
          {''.join(items_html)}
        </ul>
      </div>
      <div class="{right_col}"></div>
    </div>
  </div>
  """


def render_list_section(
    title: str,
    items: List[Dict[str, Any]],
    list_cls: str,
    cols: Tuple[str, str, str],
) -> str:
  """Render a two-column (title / date) list section.

  `list_cls` is the BEM block (e.g. "ta-list"). Each row uses `{list_cls}__item`.
  """
  left_col, main_col, right_col = cols
  item_cls = f"{list_cls}__item"
  list_items = "".join(
      f'<li class="{item_cls}"><span>{esc(item.get("title"))}</span>'
      f' <span>{esc(item.get("date"))}</span></li>'
      for item in items
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
        <ul class="list-unstyled mb-0 {list_cls}">
          {list_items}
        </ul>
      </div>
      <div class="{right_col}"></div>
    </div>
  </div>
  """


def render_footer(note: str, emoji: str, copyright: str, cols: Tuple[str, str, str]) -> str:
  left_col, _, right_col = cols
  prefix = f"{esc(emoji)} " if emoji else ""
  copyright_html = f'\n          <span class="footer__copyright">{copyright}</span>' if copyright else ""
  return f"""
  <div class="container">
    <div class="row">
      <div class="{left_col}"></div>
      <footer class="text-center">
        <div>
          <span class="footer__note">{prefix}{esc(note)}</span>
        </div>{copyright_html}
      </footer>
      <div class="{right_col}"></div>
    </div>
  </div>
  """


def build_page(
    data: Dict[str, Any],
    layout: Dict[str, Any],
    icon_emoji: str = "🌐",
    footer_note: str = "",
    footer_emoji: str = "🌈",
    footer_copyright: str = "",
    analytics_path: Path | None = None,
) -> str:
  spacer = '<div class="row"><p></p></div>'
  spacer_count = max(int(layout.get("spacers", 2)), 0)
  section_gap = "\n".join([spacer] * spacer_count)
  cols = col_classes(layout)
  icon_href = favicon_data_url(icon_emoji)
  ga_script = read_analytics_snippet(analytics_path)
  profile = data.get("profile", {})
  return f"""<!doctype html>
<html lang="en">
<head>
{ga_script}
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="This site is built by bootstrap v5.3.2">
  <meta name="author" content="{esc(profile.get("name"))}">
  <meta content="text/html; charset=UTF-8" http-equiv="Content-Type" />
  <link href="./bootstrap-5.3.2-dist/css/bootstrap.min.css" rel="stylesheet" type="text/css">
  <title>{esc(profile.get("name", "Site"))}</title>
  <link href="./styles/site.css" rel="stylesheet" type="text/css">
  <link rel="icon" href="{icon_href}">
</head>
<body>
  {render_profile(profile, cols)}
  {render_profile_links(profile.get("links", []), cols)}
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
  {section_gap}
  {render_interests(data.get("research_interests", []), cols)}
  {section_gap}
  {render_timeline("Experience", data.get("experience", []), cols)}
  {section_gap}
  {render_timeline("Education", data.get("education", []), cols)}
  {section_gap}
  {render_publications(data.get("publications", []), cols)}
  {section_gap}
  {render_list_section("Teaching Assistant", data.get("teaching_assistant", []), "ta-list", cols)}
  {section_gap}
  {render_list_section("Awards and Grants", data.get("awards", []), "award-list", cols)}
  {section_gap}
  {render_footer(footer_note, footer_emoji, footer_copyright, cols)}
</body>
</html>
"""


def parse_args(argv: List[str]) -> argparse.Namespace:
  parser = argparse.ArgumentParser(description="Build site HTML from JSON content files.")
  parser.add_argument("--input", type=Path, default=DEFAULT_INPUT,
                      help="Personal data JSON (default: contents/profile.json).")
  parser.add_argument("--output", type=Path, default=None,
                      help="Main HTML output path (default: <input-stem>.generate.html in repo root).")
  return parser.parse_args(argv)


def main(argv: List[str]) -> None:
  args = parse_args(argv)
  input_path: Path = args.input
  out_path: Path = args.output if args.output else ROOT / (input_path.stem + ".generate.html")

  data = read_content(input_path)

  if "publications" not in data and DEFAULT_PUBLICATIONS.exists():
    data["publications"] = json.loads(DEFAULT_PUBLICATIONS.read_text(encoding="utf-8"))

  contents_dir = DEFAULT_PUBLICATIONS.parent
  for pub in data.get("publications", []):
    if "bib" not in pub and "bib_file" in pub:
      bib_path = contents_dir / pub["bib_file"]
      if bib_path.exists():
        pub["bib"] = bib_path.read_text(encoding="utf-8").strip()

  site = read_site_config(DEFAULT_SITE_CONFIG)
  main_layout = {**DEFAULT_MAIN_LAYOUT, **(site.get("layout") or {})}
  resume_layout = {**DEFAULT_RESUME_LAYOUT, **(site.get("resume_layout") or {})}
  icon_emoji = site.get("icon_emoji") or "🌐"
  footer_note = site.get("footer_note", "")
  footer_emoji = site.get("footer_emoji", "🌈")
  footer_copyright = site.get("footer_copyright", "")

  out_path.parent.mkdir(parents=True, exist_ok=True)
  out_path.write_text(
      build_page(data, main_layout, icon_emoji=icon_emoji, footer_note=footer_note,
                 footer_emoji=footer_emoji, footer_copyright=footer_copyright,
                 analytics_path=DEFAULT_ANALYTICS_FILE),
      encoding="utf-8",
  )
  print(f"Wrote {out_path}")

  resume_out = out_path.parent / (out_path.stem + ".resume" + out_path.suffix)
  resume_out.write_text(
      build_page(data, resume_layout, icon_emoji=icon_emoji, footer_note=footer_note,
                 footer_emoji=footer_emoji, footer_copyright=footer_copyright),
      encoding="utf-8",
  )
  print(f"Wrote {resume_out}")


if __name__ == "__main__":
  main(sys.argv[1:])
