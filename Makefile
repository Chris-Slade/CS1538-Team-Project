PY := python
SRC := $(filter %.py, $(shell git ls-files))
PYLINT_IGNORE :=       \
	missing-docstring  \
	bad-continuation   \
	wrong-import-order \
	bad-whitespace     \
	unused-wildcard-import \
	too-few-public-methods \
	invalid-name
PD_OPTS :=

compile:
	$(PY) -mpy_compile $(SRC)

test:
	$(PY) -munittest t/*.py -v

lint:
	pylint $(SRC) $(foreach i, $(PYLINT_IGNORE), -d $i)

tags: $(SRC)
	ctags $(SRC)

.PHONY: compile lint tags test view
