#!/usr/bin/env python3
"""
Render an HTML file to PDF using Playwright (headless Chromium).

Usage:
  python scripts/render_pdf.py input.html                 # writes input.pdf
  python scripts/render_pdf.py input.html out.pdf         # custom output
  python scripts/render_pdf.py input.html out.pdf 2 0.65  # margin_mm scale

Defaults: A4, print backgrounds, margin 2mm, scale 0.65

Prerequisite (once):
  pip install playwright
  python -m playwright install chromium
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional


def fail(msg: str) -> None:
  print(msg, file=sys.stderr)
  sys.exit(1)


def ensure_playwright():
  try:
    from playwright.sync_api import sync_playwright  # type: ignore
  except Exception:
    fail(
        "Playwright is required. Install with:\n"
        "  pip install playwright\n"
        "  python -m playwright install chromium"
    )
  return sync_playwright


def render_pdf(
    input_path: Path,
    output_path: Path,
    format: str = "A4",
    scale: float = 0.65,
    margin_mm: float = 2,
) -> None:
  sync_playwright = ensure_playwright()
  with sync_playwright() as p:
    browser = p.chromium.launch()
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
    browser.close()
  print(f"Wrote {output_path}")


def main(argv: list[str]) -> None:
  if len(argv) < 2:
    fail("Usage: python scripts/render_pdf.py input.html [output.pdf] [margin_mm] [scale]")
  input_path = Path(argv[1])
  if not input_path.exists():
    fail(f"Input not found: {input_path}")
  if len(argv) > 2:
    output_path = Path(argv[2])
  else:
    output_path = input_path.with_suffix(".pdf")

  margin_mm = float(argv[3]) if len(argv) > 3 else 2.0
  scale = float(argv[4]) if len(argv) > 4 else 0.65

  render_pdf(input_path, output_path, margin_mm=margin_mm, scale=scale)


if __name__ == "__main__":
  main(sys.argv)

