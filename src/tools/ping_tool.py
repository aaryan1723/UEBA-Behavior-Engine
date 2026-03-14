"""
Ping Tool (Sample Tool)

A simple tool used to verify that:
- tool_loader discovers the module
- register_tool() is executed
- MCP tool registration works

Author: Aryan Patel
"""

from config.logging_config import get_logger

logger = get_logger(__name__)


def register_tool(server):
    """
    Register the ping tool with the MCP server
    """

    logger.info("Registering ping tool")

    @server.tool(
        name="ping",
        description="Simple health check tool to verify MCP tool loading"
    )
    async def ping():

        logger.info("Ping tool executed")

        return {
            "status": "success",
            "message": "pong",
        }