# MCP Sampling Demo

## Setup

Copy the example environment file and fill in your key:

```bash
cp .env.example .env
```

Install dependencies using uv:

```bash
uv sync
```

## Running the Project

Run the MCP client:

```bash
make sampling-client
```

The client starts `sampling.server` over stdio and handles the sampling request
by calling the OpenAI API. The model is currently fixed in `client.py`.
