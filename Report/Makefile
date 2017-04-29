report.pdf: report.md
	pandoc -t latex --latex-engine=xelatex -o $@ $^ $(PD_OPTS)

view: report.pdf
	evince 2>/dev/null $<

.PHONY: view
