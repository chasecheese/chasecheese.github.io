#!/usr/bin/env python3
"""
Orchestrate build → generate → deploy.

Usage:
  python scripts/deploy.py [stage]

Stages (inclusive):
  build    - run build_site to produce generated HTMLs
  generate - build + render resume PDF
  deploy   - build + generate + move outputs into final locations (default)
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(cmd: list[str]) -> None:
  subprocess.run(cmd, check=True, cwd=str(ROOT))


def build() -> None:
  run([sys.executable, str(ROOT / "scripts" / "build_site.py"), str(ROOT / "contents" / "index.md")])


def generate() -> None:
  run([sys.executable, str(ROOT / "scripts" / "render_pdf.py"), str(ROOT / "index.generate.resume.html")])


def deploy_outputs() -> None:
  (ROOT / "index.generate.html").replace(ROOT / "index.html")
  (ROOT / "index.generate.resume.pdf").replace(ROOT / "files" / "resume.pdf")


def main(argv: list[str]) -> None:
  stages = ["build", "generate", "deploy"]
  target = argv[1] if len(argv) > 1 else "deploy"
  if target not in stages:
    print(f"Unknown stage '{target}'. Choose from: {', '.join(stages)}")
    sys.exit(1)

  build()
  if target == "build":
    return

  generate()
  if target == "generate":
    return

  deploy_outputs()


if __name__ == "__main__":
  main(sys.argv)

