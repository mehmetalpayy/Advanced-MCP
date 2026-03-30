.PHONY: help sampling-client roots-main notifications-client transport-http-server

help:
	@echo "Available targets:"
	@echo "  make sampling-client"
	@echo "  make roots-main ROOTS='.'"
	@echo "  make notifications-client"
	@echo "  make transport-http-server"

sampling-client:
	uv run --project sampling -m sampling.client

ROOTS ?= .

roots-main:
	uv run --project roots -m roots.main $(ROOTS)

notifications-client:
	uv run --project notifications -m notifications.client

transport-http-server:
	PYTHONPATH=. uv run --project transport-http transport-http/main.py
