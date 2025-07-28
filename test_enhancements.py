#!/usr/bin/env python3
"""
Test script demonstrating the enhanced EMBL-EBI MCP server functionality
"""

import asyncio
from embl_ebi_protein_mcp.bridge import EMBLEBIBridge

async def test_enhancements():
    """Test the new enhanced functionality"""
    async with EMBLEBIBridge() as bridge:
        print("🧬 Testing Enhanced EMBL-EBI Protein MCP Server")
        print("=" * 50)
        
        # Test 1: Find protein accession (new feature)
        print("\n1️⃣ Testing find_protein_accession for 'p53' in human:")
        try:
            result = await bridge.find_protein_accession("p53", "human")
            if isinstance(result, list) and len(result) > 0:
                accession = result[0].get("accession", "Not found")
                protein_name = result[0].get("protein", {}).get("recommendedName", {}).get("fullName", {}).get("value", "Unknown")
                print(f"   ✅ Found: {accession} - {protein_name}")
            else:
                print(f"   ⚠️ No results found")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 2: Protein summary (new feature)
        print("\n2️⃣ Testing get_protein_summary for 'insulin' in human:")
        try:
            result = await bridge.get_protein_summary("insulin", "human")
            if "error" not in result:
                accession = result.get("accession", "Unknown")
                gene_name = result.get("gene_name", "Unknown")
                print(f"   ✅ Summary for {gene_name}: {accession}")
                print(f"   📊 Features: {'✅' if 'features' in result else '❌'}")
                print(f"   🤝 Interactions: {'✅' if 'interactions' in result else '❌'}")
            else:
                print(f"   ❌ Error: {result.get('error')}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 3: Organism mapping (enhanced feature)
        print("\n3️⃣ Testing organism mapping for 'insulin' in mouse:")
        try:
            result = await bridge.find_protein_accession("insulin", "mouse")
            if isinstance(result, list) and len(result) > 0:
                accession = result[0].get("accession", "Not found") 
                organism = result[0].get("organism", {}).get("names", [{}])[0].get("value", "Unknown")
                print(f"   ✅ Mouse insulin: {accession} from {organism}")
            else:
                print(f"   ⚠️ No results found")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 Enhancement testing complete!")
        print("\n📋 New features added:")
        print("   • get_protein_summary - One-stop protein information")
        print("   • find_protein_accession - Easy protein ID lookup")
        print("   • Improved tool descriptions with emojis and examples")
        print("   • Better organism name mapping (human, mouse, rat, etc.)")
        print("   • Clear workflow guidance for LLMs")

if __name__ == "__main__":
    asyncio.run(test_enhancements())