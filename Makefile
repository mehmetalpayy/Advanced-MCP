.PHONY: help sampling-client roots-main

help:
	@echo "Available targets:"
	@echo "  make sampling-client"
	@echo "  make roots-main ROOTS='.'"

sampling-client:
	uv run --project sampling -m sampling.client

ROOTS ?= .

roots-main:
	uv run --project roots -m roots.main $(ROOTS)
