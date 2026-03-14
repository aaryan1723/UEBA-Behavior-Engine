"""
Dynamic MCP Tool Loader

Discovers and registers all tools from the tools directory.

Flow
----
1. Discover loader file location
2. Resolve project root
3. Append tools directory to Python path
4. Discover tool modules
5. Import modules dynamically
6. Register tools with MCP server

Each tool must implement:

    def register_tool(server)

Author: Aryan Patel
"""

import sys
import importlib
from pathlib import Path
from config.logging_config import get_logger

logger = get_logger(__name__)


def load_tools(server):
    """
    Discover and register all MCP tools dynamically
    """

    try:

        # -------------------------------------------------
        # Step 1: Discover current loader location
        # -------------------------------------------------

        loader_path = Path(__file__).resolve()

        logger.info(f"Tool loader location: {loader_path}")

        # -------------------------------------------------
        # Step 2: Resolve project root
        # src/core/tool_loader.py -> src/
        # -------------------------------------------------

        project_src_path = loader_path.parent.parent

        logger.info(f"Resolved project src path: {project_src_path}")

        # -------------------------------------------------
        # Step 3: Locate tools directory
        # -------------------------------------------------

        tools_path = project_src_path / "tools"

        if not tools_path.exists():
            raise RuntimeError(f"Tools directory not found: {tools_path}")

        logger.info(f"Tools directory discovered: {tools_path}")

        # -------------------------------------------------
        # Step 4: Append tools directory to Python path
        # -------------------------------------------------

        if str(project_src_path) not in sys.path:
            sys.path.append(str(project_src_path))

        # -------------------------------------------------
        # Step 5: Discover tool files
        # -------------------------------------------------

        tool_files = list(tools_path.glob("*.py"))

        logger.info(f"Discovered {len(tool_files)} tool files")

        # -------------------------------------------------
        # Step 6: Import and register tools
        # -------------------------------------------------

        for tool_file in tool_files:

            if tool_file.name == "__init__.py":
                continue

            module_name = f"tools.{tool_file.stem}"

            try:

                logger.info(f"Loading tool module: {module_name}")

                module = importlib.import_module(module_name)

                if hasattr(module, "register_tool"):

                    module.register_tool(server)

                    logger.info(
                        f"Tool registered successfully: {tool_file.stem}"
                    )

                else:

                    logger.warning(
                        f"{module_name} does not expose register_tool(server)"
                    )

            except Exception:
                logger.exception(f"Failed to load tool: {module_name}")

    except Exception:
        logger.exception("Tool loading process failed")
        raise