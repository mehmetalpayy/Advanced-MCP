.PHONY: help sampling-client roots-main notifications-client

help:
	@echo "Available targets:"
	@echo "  make sampling-client"
	@echo "  make roots-main ROOTS='.'"
	@echo "  make notifications-client"

sampling-client:
	uv run --project sampling -m sampling.client

ROOTS ?= .

roots-main:
	uv run --project roots -m roots.main $(ROOTS)

notifications-client:
	uv run --project notifications -m notifications.client
