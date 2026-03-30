# MCP Chat with File System Access

MCP Chat is a command-line interface application that enables interactive chat capabilities with AI models through the OpenAI API. The application supports file system operations with controlled access to specified directories, video conversion capabilities, and extensible tool integrations via the MCP (Model Context Protocol) architecture.

## Prerequisites

- Python 3.10+
- OpenAI API Key
- FFmpeg (for video conversion features)

## Setup

_You must have FFmpeg already installed to convert a video file_. To install FFmpeg on MacOS run:

```
brew install ffmpeg
```

### Step 1: Configure the environment variables

1. Copy the `.env.example` file to create a new `.env` file:

```bash
cp .env.example .env
```

2. Edit the `.env` file and set your environment variables:

```
OPENAI_MODEL="gpt-5.4"  # Or your preferred OpenAI model
OPENAI_API_KEY=""  # Enter your OpenAI API key
```

### Step 2: Run the project

This repo uses `uv` and the root `Makefile`.

When running the project, you must specify one or more root directories that the MCP server will have access to. Only files and directories within these roots can be accessed by the server.

From the repository root:

```bash
make roots-main ROOTS='.'
```

Examples:

```bash
# Single directory
make roots-main ROOTS='/path/to/videos'

# Multiple directories
make roots-main ROOTS='/home/user/videos /mnt/storage/media ~/Documents'
```

## Features

### File System Access

The server can only access files and directories within the specified root paths. This provides security by limiting file system access to approved locations.

### Available Tools

- **list_roots**: List all accessible root directories
- **read_dir**: Read contents of a directory (must be within a root)
- **read_file**: Read a text file (must be within a root)
- **convert_video**: Convert MP4 videos to other formats (avi, mov, webm, mkv, gif)

### Video Conversion

The video conversion tool uses FFmpeg to convert MP4 files to various formats:

- Standard video formats: AVI, MOV, WebM, MKV
- GIF conversion with optimized settings
- Medium quality preset for balanced file size and quality
