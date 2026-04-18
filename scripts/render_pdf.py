#!/usr/bin/env python3
"""
Render an HTML file to PDF using Playwright (headless Chromium).

Examples:
  python scripts/render_pdf.py index.generate.resume.html
  python scripts/render_pdf.py index.generate.resume.html --output resume.pdf
  python scripts/render_pdf.py input.html --margin-mm 3 --scale 0.7

Defaults: A4, print backgrounds, margin 2mm, scale 0.65.

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
    format: str = "A4",
    scale: float = 0.65,
    margin_mm: float = 2.0,
) -> None:
  sync_playwright = ensure_playwright()
  with sync_playwright() as p:
    browser = p.chromium.launch()
    try:
      page = browser.new_page()
      page.goto(input_path.resolve().as_uri(), wait_until="networkidle")
      page.pdf(
          path=str(output_path),
          format=format,
          print_background=True,
          scale=scale,
          margin={
              "top": f"{margin_mm}mm",
              "right": f"{margin_mm}mm",
              "bottom": f"{margin_mm}mm",
              "left": f"{margin_mm}mm",
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
  parser.add_argument("--margin-mm", type=float, default=2.0, help="Uniform margin in mm (default: 2).")
  return parser.parse_args(argv)


def main(argv: list[str]) -> None:
  args = parse_args(argv)
  if not args.input.exists():
    fail(f"Input not found: {args.input}")
  output = args.output if args.output else args.input.with_suffix(".pdf")
  render_pdf(args.input, output, format=args.format, scale=args.scale, margin_mm=args.margin_mm)


if __name__ == "__main__":
  main(sys.argv[1:])
