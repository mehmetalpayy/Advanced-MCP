<h1 align="center"><strong>Advanced MCP</strong></h1>

## Overview

Welcome to the **advanced-mcp** repository.

This project is a collection of focused, hands-on demonstrations of advanced [Model Context Protocol (MCP)](https://modelcontextprotocol.io) concepts. Each sub-project is self-contained and targets a specific MCP feature:

- **notifications** — real-time log and progress notifications over STDIO,
- **sampling** — server-initiated LLM calls delegated back to the client,
- **roots** — client-controlled filesystem access boundaries with tool integration,
- **transport-http** — stateless streamable HTTP transport with a web demo UI.

A shared `utils/` package provides structured logging (via `rich`) used by all sub-projects.

## Task Description

The objective of this repository is to provide clean, runnable baselines for:

- understanding how MCP notifications (logging + progress) flow from server to client,
- implementing MCP sampling so the server can request LLM completions from the client,
- enforcing root-based filesystem access control in a chat application,
- running an MCP server over streamable HTTP with SSE support,
- and observing all of the above with rich, structured log output.

## Repository Structure

```
Advanced-MCP/
├── Makefile                    # Shortcuts to run each sub-project
├── utils/
│   ├── __init__.py
│   └── logger.py               # Shared Rich-based logger (Logger class)
├── notifications/
│   ├── server.py               # FastMCP server: add tool with ctx.info + progress
│   ├── client.py               # MCP client: logging_callback + progress_callback
│   └── pyproject.toml
├── sampling/
│   ├── server.py               # FastMCP server: summarize tool using ctx.session.create_message
│   ├── client.py               # MCP client: sampling_callback → OpenAI API
│   └── pyproject.toml
├── roots/
│   ├── main.py                 # Interactive CLI chat app entry point
│   ├── mcp_server.py           # FastMCP server: list_roots, read_dir, read_file, convert_video
│   ├── mcp_client.py           # MCPClient: roots support + list_roots_callback
│   ├── core/
│   │   ├── openai.py           # OpenAI chat service wrapper
│   │   ├── chat.py             # Chat logic
│   │   ├── cli_chat.py         # CLI-aware chat with tool dispatch
│   │   ├── cli.py              # CLI app loop
│   │   ├── tools.py            # Tool schema helpers
│   │   ├── utils.py            # file_url_to_path and other helpers
│   │   └── video_converter.py  # FFmpeg-based video conversion
│   └── pyproject.toml
├── transport-http/
│   ├── main.py                 # FastMCP server over streamable-http + custom HTML route
│   ├── index.html              # Web demo UI for MCP over HTTP
│   └── pyproject.toml
```

## Sub-Project Descriptions

### 1) `notifications` — Log & Progress Notifications

Demonstrates how a server emits structured log messages (`ctx.info`) and progress updates (`ctx.report_progress`) that the client receives as real-time notifications over STDIO.

| File | Role |
|---|---|
| `server.py` | `add` tool that reports log + progress events during execution |
| `client.py` | Registers `logging_callback` and `progress_callback`; calls `add(1, 3)` |

### 2) `sampling` — Server-Initiated LLM Calls

Demonstrates MCP **sampling**: the server calls `ctx.session.create_message(...)` to ask the *client* to perform an LLM completion. The client holds the API key and model, keeping credentials out of the server.

| File | Role |
|---|---|
| `server.py` | `summarize` tool that delegates inference back to the client via sampling |
| `client.py` | Registers `sampling_callback`; forwards messages to OpenAI and returns the result |

### 3) `roots` — Filesystem Access with Roots

Demonstrates MCP **roots**: the client advertises allowed filesystem directories, and the server validates all file/directory access against those roots before executing any operation.

| File | Role |
|---|---|
| `mcp_server.py` | Tools: `list_roots`, `read_dir`, `read_file`, `convert_video` — all root-gated |
| `mcp_client.py` | `MCPClient` class; registers `list_roots_callback`; propagates root paths to server |
| `main.py` | Wires OpenAI chat + MCP client; starts interactive terminal session |
| `core/` | OpenAI wrapper, CLI loop, video conversion via FFmpeg |

### 4) `transport-http` — Streamable HTTP Transport

Demonstrates running an MCP server over **streamable HTTP** instead of STDIO. Includes an interactive web UI that walks through the full MCP handshake step by step.

| File | Role |
|---|---|
| `main.py` | FastMCP server with `stateless_http=True`; serves `add` tool and the demo HTML page |
| `index.html` | Browser-based UI: Initialize → Initialized Notification → Tool Call → SSE stream |

## Installation and Setup

### Prerequisites

- Python 3.10+
- [`uv`](https://github.com/astral-sh/uv) package manager
- FFmpeg (only required for `roots` video conversion feature)

### 1. Clone the Repository

```bash
git clone https://github.com/mehmetalpayy/Advanced-MCP.git
cd Advanced-MCP
```

### 2. Configure Environment Variables

Each sub-project that needs credentials has its own `.env.example`:

```bash
# For sampling (OpenAI key required)
cp sampling/.env.example sampling/.env

# For roots (OpenAI key required)
cp roots/.env.example roots/.env
```

Minimum required values:

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=...
```

### 3. Install Dependencies

Each sub-project manages its own dependencies via `pyproject.toml`. Dependencies are installed automatically when running with `uv`:

```bash
uv sync --project notifications
uv sync --project sampling
uv sync --project roots
uv sync --project transport-http
```

## Running the Sub-Projects

### Notifications

```bash
make notifications-client
```

Spawns the server over STDIO and calls the `add` tool, printing log and progress notifications as they arrive.

### Sampling

```bash
make sampling-client
```

Spawns the server over STDIO, calls the `summarize` tool, and handles the sampling callback by forwarding the request to OpenAI.

### Roots

```bash
make roots-main ROOTS='.'
```

Starts an interactive chat session. The MCP server can only access files within the specified root directories.

Examples:

```bash
# Single directory
make roots-main ROOTS='/path/to/videos'

# Multiple directories
make roots-main ROOTS='/home/user/videos /mnt/storage/media'
```

Type `exit` to quit.

### Transport HTTP

```bash
make transport-http-server
```

Starts the MCP server at `http://localhost:8000`. Open `http://localhost:8000` in a browser to use the step-by-step demo UI.

## Available Tools by Sub-Project

| Sub-project | Tool | Description |
|---|---|---|
| `notifications` | `add(a, b)` | Returns `a + b`; emits log and progress events |
| `sampling` | `summarize(text)` | Summarizes text via client-side LLM sampling |
| `roots` | `list_roots()` | Lists all accessible root directories |
| `roots` | `read_dir(path)` | Lists contents of a directory within a root |
| `roots` | `read_file(path)` | Reads a text file within a root |
| `roots` | `convert_video(path, format)` | Converts MP4 to AVI/MOV/WebM/MKV/GIF via FFmpeg |
| `transport-http` | `add(a, b)` | Same as notifications but served over HTTP with SSE |

## Logging and Observability

All sub-projects use the shared `utils/logger.py` (`Logger` class) backed by `rich`. Logs are emitted to stderr with timestamps, log level, and source location.

Each log line is prefixed with its origin to make the server/client boundary visible:

- `[SERVER]` — emitted by the MCP server process
- `[CLIENT]` — emitted by the MCP client process
- `[MCP-SERVER]` / `[MCP-CLIENT]` — used in the `roots` sub-project
- `[ROOTS]` — used by the `roots` application orchestration layer

## Troubleshooting

### OpenAI / API errors

- Verify `OPENAI_API_KEY` is set correctly in the relevant `.env` file.
- Verify `OPENAI_MODEL` matches a model available to your API key.

### Roots: path access denied

- Ensure the path you're requesting is under one of the roots passed to `make roots-main ROOTS=...`.
- Only absolute or resolvable paths are accepted.

### Transport HTTP: connection refused

- Confirm the server is running (`make transport-http-server`).
- Default port is `8000`. Ensure nothing else is bound to it.

### FFmpeg not found

- Install FFmpeg: `brew install ffmpeg` (macOS) or `sudo apt install ffmpeg` (Linux).
- FFmpeg is only required for the `convert_video` tool in the `roots` sub-project.

## Resources

This repository was built alongside the Anthropic **Model Context Protocol: Advanced Topics** training course:

- [MCP Advanced Topics — Anthropic Skill Jar](https://anthropic.skilljar.com/model-context-protocol-advanced-topics)

## Contributing

1. Create a branch.
2. Implement changes in the relevant sub-project.
3. Verify logging output clearly distinguishes `[SERVER]` and `[CLIENT]` roles.
4. Open a PR describing:
   - what changed,
   - which MCP concept it relates to,
   - and how it was tested.
