#!/usr/bin/env python3
"""
Simple test script to verify EMBL-EBI API functionality
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from embl_ebi_protein_mcp.bridge import EMBLEBIBridge


async def test_protein_api():
    """Test protein endpoints"""
    async with EMBLEBIBridge() as bridge:
        print("\n=== Testing Protein API ===")
        
        # Test getting a protein by accession
        try:
            result = await bridge.get_protein_by_accession("P12345")
            print(f"✓ Get protein by accession P12345: {result.get('id', 'No ID')} - {result.get('protein', {}).get('recommendedName', {}).get('fullName', {}).get('value', 'No name')}")
        except Exception as e:
            print(f"✗ Get protein by accession failed: {e}")
        
        # Test searching proteins
        try:
            result = await bridge.search_proteins("insulin", size=5)
            # Handle both dict with 'results' key and direct list response
            if isinstance(result, dict):
                count = len(result.get('results', []))
            elif isinstance(result, list):
                count = len(result)
            else:
                count = 0
            print(f"✓ Search proteins for 'insulin': Found {count} results")
        except Exception as e:
            print(f"✗ Search proteins failed: {e}")


async def test_taxonomy_api():
    """Test taxonomy endpoints"""
    async with EMBLEBIBridge() as bridge:
        print("\n=== Testing Taxonomy API ===")
        
        # Test getting taxonomy by ID (human)
        try:
            result = await bridge.get_taxonomy_by_id("9606")
            print(f"✓ Get taxonomy by ID 9606: {result.get('scientificName', 'No name')} ({result.get('commonName', 'No common name')})")
        except Exception as e:
            print(f"✗ Get taxonomy by ID failed: {e}")
        
        # Test getting taxonomy by name
        try:
            result = await bridge.get_taxonomy_by_name("Homo sapiens")
            count = len(result.get('taxonomies', []))
            print(f"✓ Get taxonomy by name 'Homo sapiens': Found {count} results")
        except Exception as e:
            print(f"✗ Get taxonomy by name failed: {e}")


async def test_features_api():
    """Test features endpoints"""
    async with EMBLEBIBridge() as bridge:
        print("\n=== Testing Features API ===")
        
        # Test getting features by accession
        try:
            result = await bridge.get_features_by_accession("P12345")
            count = len(result.get('features', []))
            print(f"✓ Get features by accession P12345: Found {count} features")
        except Exception as e:
            print(f"✗ Get features by accession failed: {e}")


async def test_variations_api():
    """Test variations endpoints"""
    async with EMBLEBIBridge() as bridge:
        print("\n=== Testing Variations API ===")
        
        # Test getting variations by accession (try P04637 - p53 which should have variations)
        try:
            result = await bridge.get_variations_by_accession("P04637")
            count = len(result.get('features', []))
            print(f"✓ Get variations by accession P04637: Found {count} variations")
        except Exception as e:
            print(f"✗ Get variations by accession failed: {e}")
            
        # Fallback test with original accession
        try:
            result = await bridge.get_variations_by_accession("P12345")
            count = len(result.get('features', []))
            print(f"✓ Get variations by accession P12345: Found {count} variations")
        except Exception as e:
            print(f"Note: P12345 has no variation data (expected for some proteins)")


async def main():
    """Run all tests"""
    print("Testing EMBL-EBI Protein API functionality...")
    
    await test_protein_api()
    await test_taxonomy_api()
    await test_features_api()
    await test_variations_api()
    
    print("\n=== Test Complete ===")


if __name__ == "__main__":
    asyncio.run(main())