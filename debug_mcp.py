#!/usr/bin/env python3
"""
Debug script to test MCP tool calls
"""

import asyncio
import json
from embl_ebi_protein_mcp.mcp_server import EMBLEBIMCPServer

async def simulate_mcp_call():
    """Simulate how MCP might call our tools"""
    server = EMBLEBIMCPServer()
    
    # Get the actual registered tool wrapper from the server
    # We need to check how tools are stored in the MCP server
    print("Server tools registry:", list(server._tool_registry.keys()))
    
    # Let's try to call the tool the way MCP would
    try:
        # Simulate the way MCP calls tools - we need to understand this better
        print("\n=== Testing search_proteins ===")
        
        # Try direct call to our handler
        handler = server._tool_registry['search_proteins']
        result = await handler({"query": "p53", "size": 5})
        print(f"Direct handler result: {type(result)}")
        
        # Now let's see if we can access the actual MCP server's tool
        mcp_server = server.get_server()
        print(f"MCP Server type: {type(mcp_server)}")
        print(f"MCP Server has tools: {hasattr(mcp_server, '_tool_handlers')}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(simulate_mcp_call())