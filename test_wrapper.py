#!/usr/bin/env python3
"""
Test the tool wrapper directly to see the argument issue
"""

import asyncio
import json
from embl_ebi_protein_mcp.mcp_server import EMBLEBIMCPServer

async def test_wrapper():
    """Test the wrapper directly"""
    server = EMBLEBIMCPServer()
    
    # Get the MCP server and try to understand how tools are called
    mcp_server = server.get_server()
    
    # Check the internal tool structure
    if hasattr(mcp_server, '_tool_cache'):
        print("Tool cache:", mcp_server._tool_cache)
    
    # Let's manually call the wrapper with different argument patterns to find the issue
    print("\n=== Testing argument patterns ===")
    
    # Get our custom wrapper - we need to find it
    # The wrapper should be registered in the MCP server
    
    # Let's try to manually simulate what MCP might pass
    test_arguments = {"query": "p53", "size": 5}
    
    # Test 1: Direct dict
    print("Test 1: Direct dict argument")
    try:
        # We can't easily access the wrapper, so let's test our handler differently
        handler = server._tool_registry['search_proteins']
        result = await handler(test_arguments)
        print(f"✓ Handler works with dict: {type(result)}")
    except Exception as e:
        print(f"✗ Handler failed: {e}")
    
    print("\nDebugging complete")

if __name__ == "__main__":
    asyncio.run(test_wrapper())