#!/usr/bin/env python3
"""
Test script to demonstrate getting taxonomy information for humans (ID: 9606)
"""

import asyncio
import json
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from embl_ebi_protein_mcp.bridge import EMBLEBIBridge


async def test_human_taxonomy():
    """Test getting taxonomy information for humans using ID 9606"""
    
    print("Testing EMBL-EBI Protein MCP Server - Human Taxonomy Information")
    print("=" * 65)
    
    async with EMBLEBIBridge() as bridge:
        try:
            # Get taxonomy information for humans (ID: 9606)
            print("Fetching taxonomy information for humans (ID: 9606)...")
            result = await bridge.get_taxonomy_by_id("9606")
            
            print("\nSUCCESS! Retrieved taxonomy information:")
            print("-" * 45)
            print(f"Scientific Name: {result.get('scientificName', 'N/A')}")
            print(f"Common Name: {result.get('commonName', 'N/A')}")
            print(f"Taxonomy ID: {result.get('taxonomyId', 'N/A')}")
            print(f"Rank: {result.get('rank', 'N/A')}")
            print(f"Parent ID: {result.get('parentId', 'N/A')}")
            
            # Show the full JSON response
            print("\nFull API Response:")
            print("-" * 20)
            print(json.dumps(result, indent=2))
            
        except Exception as e:
            print(f"ERROR: Failed to retrieve taxonomy information: {e}")
            return False
    
    return True


async def main():
    """Main test function"""
    success = await test_human_taxonomy()
    
    if success:
        print("\n" + "=" * 65)
        print("✓ Test completed successfully!")
        print("The EMBL-EBI protein MCP server is working correctly for taxonomy queries.")
    else:
        print("\n" + "=" * 65)
        print("✗ Test failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())