# Minimal makefile for Sphinx documentation
#
# 屏幕支持列表文档：make html 生成 HTML，make pdf 生成 PDF。
# html/pdf 之前会自动运行 gen_panel_rst.py，从 ../panels/*.h 重新生成表格。

module_name  := CVITEK_Panel_Support_List
output_file_prefix := CVITEK_Panel_Support_List

# -- 版本信息（统一管理）-------------------------------------------------
VERSION := V1.0
RELEASE_DATE := 2026-06-19
AUTHOR := song.yu

LANG := zh
pdf_name  = $(output_file_prefix)_$(VERSION)_$(LANG).pdf

# 导出环境变量供 conf.py 使用
export VERSION
export RELEASE_DATE
export AUTHOR
export LC_ALL=en_US.UTF-8

SPHINXOPTS    ?= -W -n
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile gen html pdf clean

# 扫描 panels 头文件，重新生成 rst 表格
gen:
	@python3 gen_panel_rst.py

# make html：渲染成 HTML（先生成表格）
html: gen
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo "HTML 输出: $(BUILDDIR)/html/index.html"

# make pdf：渲染成 PDF（先生成表格）
pdf: gen latex
	@cd $(BUILDDIR)/latex && xelatex $(module_name).tex
	@cd $(BUILDDIR)/latex && xelatex $(module_name).tex
	@mv $(BUILDDIR)/latex/$(module_name).pdf $(BUILDDIR)/"${pdf_name}" && rm -rf $(BUILDDIR)/latex
	@echo "PDF 输出: $(BUILDDIR)/${pdf_name}"

# 仅 latex 中间产物，供 pdf 目标调用
latex:
	@$(SPHINXBUILD) -M latex "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

clean:
	@rm -rf $(BUILDDIR)
