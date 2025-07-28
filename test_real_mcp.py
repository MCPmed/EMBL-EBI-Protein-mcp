#!/usr/bin/env python3
"""
Test the MCP server with a real protocol call
"""

import asyncio
import json
import sys
from mcp.server import Server
from embl_ebi_protein_mcp.mcp_server import EMBLEBIMCPServer

async def test_mcp_protocol():
    """Test the MCP protocol directly"""
    
    # Create our server
    mcp_server_wrapper = EMBLEBIMCPServer()
    server = mcp_server_wrapper.get_server()
    
    # Set up list_tools handler
    @server.list_tools()
    async def handle_list_tools():
        return mcp_server_wrapper.get_tool_definitions()
    
    print("=== Testing MCP Server Protocol ===")
    
    # First, list tools
    try:
        tools = await handle_list_tools()
        print(f"✓ Listed {len(tools)} tools")
        
        # Find search_proteins tool
        search_tool = None
        for tool in tools:
            if tool.name == "search_proteins":
                search_tool = tool
                break
        
        if search_tool:
            print(f"✓ Found search_proteins tool: {search_tool.description}")
        else:
            print("✗ search_proteins tool not found")
            return
        
    except Exception as e:
        print(f"✗ Failed to list tools: {e}")
        return
    
    # Now try to call the tool
    # The MCP server should have internal handlers registered
    print("\n=== Testing Tool Call ===")
    
    # We need to simulate how the MCP client would call our tool
    # Let's check if we can access the internal tool handlers
    if hasattr(server, '_tool_handlers'):
        print("Server has _tool_handlers")
    
    # Try to find our registered tool
    print("Server attributes related to tools:")
    attrs = [attr for attr in dir(server) if 'tool' in attr.lower() or 'call' in attr.lower()]
    print(attrs)

if __name__ == "__main__":
    asyncio.run(test_mcp_protocol())