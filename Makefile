PYTHON   := .venv/bin/python
BUILDDIR := build

BIBS     := $(wildcard contents/bibs/*.bib)
SOURCES  := contents/profile.json contents/publications.json contents/site.json \
            scripts/build_site.py styles/site.css $(BIBS)

MAIN_HTML       := $(BUILDDIR)/index.html
RESUME_HTML     := $(BUILDDIR)/index.resume.html
RESUME_PDF      := $(BUILDDIR)/resume.pdf

.PHONY: all html pdf deploy clean setup

all: html

html: $(MAIN_HTML)

pdf: $(RESUME_PDF)

$(MAIN_HTML): $(SOURCES) contents/analytics.html
	$(PYTHON) scripts/build_site.py \
		--input contents/profile.json \
		--output $(MAIN_HTML)

$(RESUME_HTML): $(MAIN_HTML)

$(RESUME_PDF): $(RESUME_HTML)
	$(PYTHON) scripts/render_pdf.py $(RESUME_HTML) --output $(RESUME_PDF) --base-dir .

deploy: $(MAIN_HTML) $(RESUME_PDF)
	cp $(MAIN_HTML) index.html
	mkdir -p files
	cp $(RESUME_PDF) files/resume.pdf
	@echo "Deployed index.html and files/resume.pdf"

clean:
	rm -rf $(BUILDDIR)

setup:
	uv venv --python 3.12
	uv pip install -e .
	$(PYTHON) -m playwright install chromium
