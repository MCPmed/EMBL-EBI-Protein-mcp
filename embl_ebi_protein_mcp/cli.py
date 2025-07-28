#!/usr/bin/env python3
"""
Main entry point for the EMBL-EBI Proteins API MCP Server
This can be used as both main.py and cli.py
"""

import asyncio
import logging
import sys
from mcp.server.models import InitializationOptions
from mcp.server.lowlevel.server import NotificationOptions
import mcp.server.stdio

# Handle both package and standalone execution
try:
    from .mcp_server import EMBLEBIMCPServer
except ImportError:
    try:
        from mcp_server import EMBLEBIMCPServer
    except ImportError:
        from embl_ebi_protein_mcp.mcp_server import EMBLEBIMCPServer

# Configure logging with debug level
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)

logger = logging.getLogger("embl-ebi-main")


async def run_server():
    """
    Main entry point for the MCP server
    """
    logger.info("Starting EMBL-EBI Proteins API MCP Server...")
    
    try:
        # Initialize the MCP server
        mcp_server = EMBLEBIMCPServer()
        server = mcp_server.get_server()
        
        # Define available tools for the client
        @server.list_tools()
        async def handle_list_tools():
            """List all available tools"""
            logger.info("Client requesting tool list")
            return mcp_server.get_tool_definitions()
        
        logger.info("Server initialized successfully")
        logger.info("Available tools:")
        for tool in mcp_server.get_tool_definitions():
            logger.info(f"  - {tool.name}: {tool.description}")
        
        # Run the server
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            logger.info("Server running on stdio")
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="embl-ebi-proteins",
                    server_version="0.1.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    ),
                ),
            )
    
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}", exc_info=True)
        raise


def main():
    """Entry point for console script"""
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()