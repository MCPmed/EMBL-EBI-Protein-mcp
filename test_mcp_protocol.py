#!/usr/bin/env python3
"""
Test MCP protocol with proper initialization
"""

import asyncio
import json
import sys
import subprocess

async def test_mcp_with_init():
    """Test MCP with proper initialization"""
    
    # Start the server
    proc = subprocess.Popen(['embl_ebi_protein_mcp'], 
                           stdin=subprocess.PIPE, 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE,
                           text=True)
    
    try:
        # Step 1: Initialize
        init_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            },
            "id": 1
        }
        
        print("Sending initialize request...")
        proc.stdin.write(json.dumps(init_request) + "\n")
        proc.stdin.flush()
        
        # Read response
        response = proc.stdout.readline()
        print(f"Initialize response: {response.strip()}")
        
        # Step 2: Send initialized notification
        initialized = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        print("Sending initialized notification...")
        proc.stdin.write(json.dumps(initialized) + "\n")
        proc.stdin.flush()
        
        await asyncio.sleep(0.1)  # Give it a moment
        
        # Step 3: Call the tool
        tool_call = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "search_proteins",
                "arguments": {"query": "p53", "size": 5}
            },
            "id": 2
        }
        
        print("Sending tool call...")
        proc.stdin.write(json.dumps(tool_call) + "\n")
        proc.stdin.flush()
        
        # Read response
        await asyncio.sleep(1)  # Give it time to process
        
        # Try to read any available output
        try:
            response = proc.stdout.readline()
            if response:
                print(f"Tool call response: {response.strip()}")
            else:
                print("No immediate response")
        except:
            print("Could not read response")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    asyncio.run(test_mcp_with_init())