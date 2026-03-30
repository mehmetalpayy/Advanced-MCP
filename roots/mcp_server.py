from pathlib import Path

from dotenv import load_dotenv
from utils import Logger
from roots.core.video_converter import VideoConverter
from roots.core.utils import file_url_to_path
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp import Context
from pydantic import Field

load_dotenv()

mcp = FastMCP("VidsMCP", log_level="ERROR")


async def is_path_allowed(requested_path: Path, ctx: Context) -> bool:
    Logger.info(f"[MCP-SERVER] Checking path access for: {requested_path}")
    roots_result = await ctx.session.list_roots()
    client_roots = roots_result.roots

    if not requested_path.exists():
        Logger.warn(f"[MCP-SERVER] Path does not exist: {requested_path}")
        return False

    if requested_path.is_file():
        requested_path = requested_path.parent

    for root in client_roots:
        root_path = file_url_to_path(root.uri)
        try:
            requested_path.relative_to(root_path)
            Logger.info(
                f"[MCP-SERVER] Path allowed under root: {root_path}"
            )
            return True
        except ValueError:
            continue

    Logger.warn(f"[MCP-SERVER] Path denied: {requested_path}")
    return False


@mcp.tool()
async def convert_video(
    input_path: str = Field(description="Path to the input MP4 file"),
    format: str = Field(description="Output format (e.g. 'mov')"),
    *,
    ctx: Context,
):
    """Convert an MP4 video file to another format using ffmpeg"""
    Logger.info(
        f"[MCP-SERVER] convert_video called with input_path={input_path}, format={format}"
    )
    input_file = VideoConverter.validate_input(input_path)

    # Ensure the input file is contained in a root
    if not await is_path_allowed(input_file, ctx):
        raise ValueError(f"Access to path is not allowed: {input_path}")

    return await VideoConverter.convert(input_path, format)


@mcp.tool()
async def list_roots(ctx: Context):
    """
    List all directories that are accessible to this server.
    These are the root directories where files can be read from or written to.
    """
    Logger.info("[MCP-SERVER] list_roots called")
    roots_result = await ctx.session.list_roots()
    client_roots = roots_result.roots

    return [file_url_to_path(root.uri) for root in client_roots]


@mcp.tool()
async def read_dir(
    path: str = Field(description="Path to a directory to read"),
    *,
    ctx: Context,
):
    """Read directory contents. Path must be within one of the client's roots."""
    Logger.info(f"[MCP-SERVER] read_dir called for path: {path}")
    requested_path = Path(path).resolve()

    if not await is_path_allowed(requested_path, ctx):
        raise ValueError("Error: can only read directories within a root")

    return [entry.name for entry in requested_path.iterdir()]


@mcp.tool()
async def read_file(
    path: str = Field(description="Path to a text file to read"),
    *,
    ctx: Context,
):
    """Read text file contents. Path must be within one of the client's roots."""
    Logger.info(f"[MCP-SERVER] read_file called for path: {path}")
    requested_path = Path(path).resolve()

    if not requested_path.exists():
        raise ValueError(f"Error: file does not exist: {path}")

    if not requested_path.is_file():
        raise ValueError(f"Error: path is not a file: {path}")

    if not await is_path_allowed(requested_path, ctx):
        raise ValueError("Error: can only read files within a root")

    return requested_path.read_text(encoding="utf-8")


if __name__ == "__main__":
    Logger.info("[MCP-SERVER] Starting roots MCP server")
    mcp.run(transport="stdio")
