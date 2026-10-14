DOCS = docs
PYTHON = python
PLANTUML = java -jar ~/plantuml.jar
UMLFILES = $(wildcard ./uml/*.plantuml)
SRC_FILES = $(wildcard src/*.py)

.PHONY: all
all: run check-style fix-style check-types test test-coverage create-docs create-uml clean
	@echo "All done!"

.PHONY: run
run:
	$(PYTHON) src/main.py

.PHONY: check-style
check-style:
	flake8 .

.PHONY: fix-style
fix-style:
	autopep8 --in-place --recursive --aggressive --aggressive .

.PHONY: test
test:
ifeq ($(shell which pytest), )
	@echo "pytest not found. Installing..."
	pip install pytest
endif
	PYTHONPATH=src pytest --verbose --color=yes tests/
	@echo "All unittests passed!"

.PHONY: test-coverage
test-coverage: create-doc-folder
	PYTHONPATH=src pytest --verbose --color=yes --cov --cov-report term-missing --cov-report=html:$(DOCS)/htmlcov tests/
	@echo "All unittests passed!"

.PHONY: check-types
check-types:
ifeq ($(shell which mypy), )
	@echo "mypy not found. Installing mypy..."
	pip install mypy
endif
	mypy --disallow-untyped-defs --strict .
	@echo "Type checking done."

.PHONY: create-doc-folder
create-doc-folder:
	@mkdir -p $(DOCS)

.PHONY: create-docs
create-docs: create-doc-folder
	pdoc --output-dir $(DOCS)/code-docs$(SRC_FILES)
	@echo "html docs created and saved in $(DOCS)/code-docs"

.PHONY: create-uml
create-uml: create-doc-folder
ifeq ($(shell which java), )
	$(error "No java found in $(PATH). Install java to run plantuml")
endif
ifeq ($(wildcard ~/plantuml.jar), )
	@echo "Downloading plantuml.jar in home folder..."
	curl -L -o ~/plantuml.jar https://sourceforge.net/projects/plantuml/files/plantuml.jar/download
	sudo apt install graphviz
endif
	@echo "Creating UML diagrams..."
	@for umlfile in $(UMLFILES); do \
		echo "Processing $$umlfile..."; \
		java -jar ~/plantuml.jar $$umlfile; \
	done
	@echo "UML diagrams created and saved in uml folder"

.PHONY: clean
clean:
	rm -rf `find . -type d -name __pycache__`
	rm -rf `find . -type d -name .pytest_cache`
	rm -rf `find . -type d -name .mypy_cache`
	rm -rf `find . -name .hypothesis`
	rm -rf `find . -name .coverage`