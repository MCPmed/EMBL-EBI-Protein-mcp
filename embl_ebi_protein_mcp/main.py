#!/usr/bin/env python3
"""
CLI entry point for the EMBL-EBI Proteins API MCP Server
This is the entry point used by the console script defined in pyproject.toml
"""

import asyncio
import logging
import sys
import mcp.server.stdio
from mcp.server.models import InitializationOptions
from .mcp_server import EMBLEBIMCPServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)

logger = logging.getLogger("embl-ebi-cli")


async def run_server():
    """
    Run the MCP server
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
        logger.info(f"Available tools: {len(mcp_server.get_tool_definitions())}")
        
        # Run the server with minimal configuration
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            logger.info("Server running on stdio")
            
            # Create minimal initialization options
            init_options = InitializationOptions(
                server_name="embl-ebi-proteins",
                server_version="0.1.0",
                capabilities={}
            )
            
            await server.run(read_stream, write_stream, init_options)
    
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}", exc_info=True)
        raise


def main():
    """
    Main CLI entry point - this is what gets called by the console script
    """
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