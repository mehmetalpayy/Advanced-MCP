.PHONY: help sampling-client

help:
	@echo "Available targets:"
	@echo "  make sampling-client"

sampling-client:
	uv run --project sampling -m sampling.client
