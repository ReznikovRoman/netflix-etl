REQUIREMENTS_DIR := requirements
PIP_COMPILE_ARGS := --generate-hashes --no-header --no-emit-index-url --verbose
PIP_COMPILE := cd $(REQUIREMENTS_DIR) && pip-compile $(PIP_COMPILE_ARGS)

.PHONY: fix
fix:
	isort .

.PHONY: lint
lint:
	flake8
	isort -qc .

.PHONY: compile-requirements
compile-requirements:
	pip install -U pip-tools
	$(PIP_COMPILE) requirements.in
	$(PIP_COMPILE) requirements.lint.in
	$(PIP_COMPILE) requirements.dev.in
	test -f $(REQUIREMENTS_DIR)/requirements.local.in && $(PIP_COMPILE) requirements.local.in || exit 0

.PHONY: sync-requirements
sync-requirements:
	pip install -U pip-tools
	cd $(REQUIREMENTS_DIR) && pip-sync requirements.txt requirements.*.txt

.DEFAULT_GOAL :=