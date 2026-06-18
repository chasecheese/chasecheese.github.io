#!/usr/bin/env python3
"""
Orchestrate build → generate → deploy.

Usage:
  python scripts/deploy.py [stage]

Stages (each includes the previous):
  build    - render HTMLs into *.generate.html
  generate - build + render index.generate.resume.pdf
  deploy   - build + generate + publish to index.html and files/resume.pdf (default)
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
CONTENT = ROOT / "contents" / "profile.json"
GENERATED_MAIN = ROOT / "index.generate.html"
GENERATED_RESUME_HTML = ROOT / "index.generate.resume.html"
GENERATED_RESUME_PDF = ROOT / "index.generate.resume.pdf"
PUBLISHED_MAIN = ROOT / "index.html"
PUBLISHED_RESUME_PDF = ROOT / "files" / "resume.pdf"

STAGES = ["build", "generate", "deploy"]


def python_bin() -> str:
  venv_py = ROOT / ".venv" / "bin" / "python"
  if venv_py.exists():
    return str(venv_py)
  print("warning: .venv not found; falling back to current interpreter. "
        "Run `uv venv --python 3.12 && uv pip install playwright` to set it up.",
        file=sys.stderr)
  return sys.executable


def run(cmd: list[str]) -> None:
  subprocess.run(cmd, check=True, cwd=str(ROOT))


def build() -> None:
  run([python_bin(), str(SCRIPTS / "build_site.py"),
       "--input", str(CONTENT), "--output", str(GENERATED_MAIN)])


def generate() -> None:
  run([python_bin(), str(SCRIPTS / "render_pdf.py"), str(GENERATED_RESUME_HTML)])


def deploy_outputs() -> None:
  shutil.copyfile(GENERATED_MAIN, PUBLISHED_MAIN)
  print(f"Copied {GENERATED_MAIN.name} -> {PUBLISHED_MAIN.relative_to(ROOT)}")
  PUBLISHED_RESUME_PDF.parent.mkdir(parents=True, exist_ok=True)
  shutil.copyfile(GENERATED_RESUME_PDF, PUBLISHED_RESUME_PDF)
  print(f"Copied {GENERATED_RESUME_PDF.name} -> {PUBLISHED_RESUME_PDF.relative_to(ROOT)}")


def main(argv: list[str]) -> None:
  target = argv[1] if len(argv) > 1 else "deploy"
  if target not in STAGES:
    print(f"Unknown stage '{target}'. Choose from: {', '.join(STAGES)}")
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
