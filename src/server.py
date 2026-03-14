"""
Cognisec UEBA MCP Server

Central execution server responsible for hosting all UEBA tools.

Author: Aryan Patel
"""

import signal
import sys
from fastmcp import FastMCP

from core.tool_loader import load_tools
from config.logging_config import get_logger
from config.settings import get_settings

logger = get_logger(__name__)


def create_server():
    """
    Create the MCP server object.

    NOTE:
    FastMCP v3 only needs the server name here.
    Networking (host/port) is handled internally when `run()` is called.
    """

    settings = get_settings()

    logger.info("Initializing Cognisec UEBA MCP Server")

    server = FastMCP(
        name=settings.MCP_SERVER_NAME
    )

    logger.info(f"MCP Server created | name={settings.MCP_SERVER_NAME}")

    return server


def register_tools(server):
    """
    Discover and register all MCP tools dynamically.
    """

    logger.info("Loading MCP tools from tools directory")

    load_tools(server)

    logger.info("All MCP tools registered successfully")


def shutdown(signal_received, frame):
    """
    Graceful shutdown handler.

    Triggered when the OS sends:
    SIGINT  → Ctrl+C
    SIGTERM → container shutdown
    """

    logger.info("Shutdown signal received. Stopping MCP server gracefully.")
    sys.exit(0)


def main():
    """
    Main entry point of the MCP server.
    """

    try:

        settings = get_settings()

        signal.signal(signal.SIGINT, shutdown)
        signal.signal(signal.SIGTERM, shutdown)

        server = create_server()

        register_tools(server)

        logger.info(
            f"Starting Cognisec UEBA MCP Server "
            f"(host={settings.MCP_HOST}, port={settings.MCP_PORT})"
        )

        server.run(
            transport="streamable-http",
            host=settings.MCP_HOST,
            port=settings.MCP_PORT,
        )

    except Exception:
        logger.exception("MCP Server failed to start")


if __name__ == "__main__":
    main()