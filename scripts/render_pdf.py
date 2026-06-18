#!/usr/bin/env python3
"""
Render an HTML file to PDF using Playwright (headless Chromium).

Examples:
  python scripts/render_pdf.py index.generate.resume.html
  python scripts/render_pdf.py index.generate.resume.html --output resume.pdf
  python scripts/render_pdf.py input.html --margin-mm 3 --scale 0.7

Defaults: A4, print backgrounds, margin 10mm (top/bottom) / 2mm (left/right), scale 0.65.

Prerequisite (once):
  uv pip install playwright
  python -m playwright install chromium
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def fail(msg: str) -> None:
  print(msg, file=sys.stderr)
  sys.exit(1)


def ensure_playwright():
  try:
    from playwright.sync_api import sync_playwright  # type: ignore
  except ImportError:
    fail(
        "Playwright is required. Install with:\n"
        "  uv pip install playwright\n"
        "  python -m playwright install chromium"
    )
  return sync_playwright


def render_pdf(
    input_path: Path,
    output_path: Path,
    base_dir: Path | None = None,
    format: str = "A4",
    scale: float = 0.65,
    margin_v_mm: float = 10.0,
    margin_h_mm: float = 2.0,
) -> None:
  sync_playwright = ensure_playwright()
  base = (base_dir or input_path.resolve().parent).resolve()
  html = input_path.resolve().read_text(encoding="utf-8")
  base_url = base.as_uri() + "/"
  with sync_playwright() as p:
    browser = p.chromium.launch()
    try:
      page = browser.new_page()
      page.goto(base_url, wait_until="domcontentloaded")
      page.set_content(html, wait_until="networkidle")
      page.pdf(
          path=str(output_path),
          format=format,
          print_background=True,
          scale=scale,
          margin={
              "top": f"{margin_v_mm}mm",
              "right": f"{margin_h_mm}mm",
              "bottom": f"{margin_v_mm}mm",
              "left": f"{margin_h_mm}mm",
          },
      )
    finally:
      browser.close()
  print(f"Wrote {output_path}")


def parse_args(argv: list[str]) -> argparse.Namespace:
  parser = argparse.ArgumentParser(description="Render an HTML file to PDF via headless Chromium.")
  parser.add_argument("input", type=Path, help="Input HTML file.")
  parser.add_argument("--output", "-o", type=Path, default=None,
                      help="Output PDF path (default: input with .pdf suffix).")
  parser.add_argument("--format", default="A4", help="Paper format (default: A4).")
  parser.add_argument("--scale", type=float, default=0.65, help="Print scale (default: 0.65).")
  parser.add_argument("--margin-v-mm", type=float, default=10.0, help="Top/bottom margin in mm (default: 10).")
  parser.add_argument("--margin-h-mm", type=float, default=2.0, help="Left/right margin in mm (default: 2).")
  parser.add_argument("--base-dir", type=Path, default=None,
                      help="Base directory for resolving relative paths in the HTML (default: input file's directory).")
  return parser.parse_args(argv)


def main(argv: list[str]) -> None:
  args = parse_args(argv)
  if not args.input.exists():
    fail(f"Input not found: {args.input}")
  output = args.output if args.output else args.input.with_suffix(".pdf")
  render_pdf(args.input, output, base_dir=args.base_dir, format=args.format,
             scale=args.scale, margin_v_mm=args.margin_v_mm, margin_h_mm=args.margin_h_mm)


if __name__ == "__main__":
  main(sys.argv[1:])
