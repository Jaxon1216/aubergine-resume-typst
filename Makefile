TYPST ?= typst
TINYMIST ?= tinymist
PYTHON ?= python3
PDFTOPPM ?= pdftoppm
RESUME_LANG ?= zh
FONT_PRESET ?= open-source
ifneq ($(FONT_PRESET),open-source)
ifneq ($(FONT_PRESET),original)
$(error FONT_PRESET 可选 open-source 或 original，当前为 "$(FONT_PRESET)")
endif
endif
ifneq ($(RESUME_LANG),zh)
ifneq ($(RESUME_LANG),en)
$(error RESUME_LANG 可选 zh 或 en，当前为 "$(RESUME_LANG)")
endif
endif
SOURCE := resume.typ
LANG_SUFFIX := $(if $(filter en,$(RESUME_LANG)),-en,)
FONT_SUFFIX := $(if $(filter original,$(FONT_PRESET)),-original,)
SETTINGS := $(if $(filter original,$(FONT_PRESET)),resume/settings.original.toml,resume/settings.toml)
PDF := output/pdf/resume$(FONT_SUFFIX)$(LANG_SUFFIX).pdf
EXAMPLE := docs/example$(FONT_SUFFIX)$(LANG_SUFFIX).pdf
PREVIEW := docs/preview$(FONT_SUFFIX)$(LANG_SUFFIX)
FLAGS := --root . --font-path fonts --input lang=$(RESUME_LANG) --input settings=$(SETTINGS)
TYPST_FLAGS ?=
DEPS := $(shell find resume typst fonts -type f) scripts/check_original_fonts.py
CHECK_FONTS := $(if $(filter original,$(FONT_PRESET)),TYPST="$(TYPST)" $(PYTHON) scripts/check_original_fonts.py --settings "$(SETTINGS)" $(filter --ignore-system-fonts,$(TYPST_FLAGS)),:)

.PHONY: all pdf en original original-en preview watch info example clean test
all: pdf
pdf: $(PDF)

$(PDF): $(SOURCE) $(DEPS) Makefile
	@mkdir -p $(dir $@)
	@$(CHECK_FONTS)
	$(TYPST) compile $(FLAGS) $(TYPST_FLAGS) $(SOURCE) $@

en:
	$(MAKE) RESUME_LANG=en pdf

original:
	$(MAKE) FONT_PRESET=original pdf

original-en:
	$(MAKE) RESUME_LANG=en FONT_PRESET=original pdf

preview:
	@$(CHECK_FONTS)
	$(TINYMIST) preview $(FLAGS) --open $(SOURCE)

watch:
	@mkdir -p $(dir $(PDF))
	@$(CHECK_FONTS)
	$(TYPST) watch $(FLAGS) $(TYPST_FLAGS) $(SOURCE) $(PDF)

info:
	@$(CHECK_FONTS)
	$(TYPST) eval $(FLAGS) $(TYPST_FLAGS) --in $(SOURCE) 'query(<resume-layout>).first().value' --pretty

# 公开示例均须为虚构内容；语言和字体预设通过变量选择。
example: $(PDF)
	@mkdir -p docs
	cp $(PDF) $(EXAMPLE)
	$(PDFTOPPM) -f 1 -singlefile -scale-to 2200 -png $(EXAMPLE) $(PREVIEW)

clean:
	rm -rf output

test:
	$(PYTHON) tests/test_template.py
	$(PYTHON) tests/test_personalization.py
