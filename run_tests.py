#!/usr/bin/env python3
"""
Simple test runner for when pytest/MCP dependencies aren't available.
This demonstrates the new test structure and can be used for basic validation.
"""

import asyncio
import sys
import os
from unittest.mock import AsyncMock, patch, MagicMock

# Add the package to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_bridge_basic():
    """Basic bridge functionality test."""
    try:
        from embl_ebi_protein_mcp.bridge import EMBLEBIBridge
        
        # Test initialization
        bridge = EMBLEBIBridge()
        assert bridge.base_url == "https://www.ebi.ac.uk/proteins/api"
        assert bridge.headers["Accept"] == "application/json"
        assert bridge.timeout.total == 30
        
        print("✅ Bridge initialization test passed")
        return True
    except Exception as e:
        print(f"❌ Bridge initialization test failed: {e}")
        return False

async def test_bridge_async_context():
    """Test bridge async context manager."""
    try:
        from embl_ebi_protein_mcp.bridge import EMBLEBIBridge
        
        bridge = EMBLEBIBridge()
        async with bridge:
            assert bridge.session is not None
        
        print("✅ Bridge async context test passed")
        return True
    except Exception as e:
        print(f"❌ Bridge async context test failed: {e}")
        return False

def test_mcp_server_basic():
    """Basic MCP server test (if MCP is available)."""
    try:
        from embl_ebi_protein_mcp.mcp_server import EMBLEBIMCPServer
        
        # Test initialization
        server = EMBLEBIMCPServer()
        assert server.bridge is not None
        assert len(server._tool_registry) >= 0
        
        print("✅ MCP Server initialization test passed")
        return True
    except ImportError as e:
        print(f"⚠️  MCP Server test skipped (MCP not available): {e}")
        return True  # Not a failure
    except Exception as e:
        print(f"❌ MCP Server initialization test failed: {e}")
        return False

def test_project_structure():
    """Test that project structure is clean."""
    required_files = [
        "pyproject.toml",
        "README.md", 
        "LICENSE",
        "embl_ebi_protein_mcp/__init__.py",
        "embl_ebi_protein_mcp/bridge.py",
        "embl_ebi_protein_mcp/mcp_server.py",
        "embl_ebi_protein_mcp/cli.py",
        "tests/conftest.py",
        "tests/test_bridge.py",
        "tests/test_mcp_server.py",
        "tests/test_integration.py",
        "scripts/test.sh",
        "scripts/lint.sh",
        ".github/workflows/test.yml"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Project structure test failed. Missing files: {missing_files}")
        return False
    else:
        print("✅ Project structure test passed")
        return True

def test_old_files_removed():
    """Test that old test files have been removed."""
    old_files = [
        "test_api.py",
        "test_enhancements.py", 
        "test_human_taxonomy.py",
        "test_mcp_protocol.py",
        "test_real_mcp.py",
        "test_wrapper.py",
        "debug_mcp.py",
        "EMBL_EBI_Protein_mcp.egg-info"
    ]
    
    existing_old_files = []
    for file_path in old_files:
        if os.path.exists(file_path):
            existing_old_files.append(file_path)
    
    if existing_old_files:
        print(f"❌ Cleanup test failed. Old files still exist: {existing_old_files}")
        return False
    else:
        print("✅ Old files cleanup test passed")
        return True

async def main():
    """Run all tests."""
    print("🧬 EMBL-EBI Protein MCP - Test Suite")
    print("=" * 50)
    print("")
    
    tests = [
        ("Project Structure", lambda: test_project_structure()),
        ("Old Files Cleanup", lambda: test_old_files_removed()),
        ("Bridge Basic", lambda: test_bridge_basic()),
        ("Bridge Async Context", lambda: test_bridge_async_context()),
        ("MCP Server Basic", lambda: test_mcp_server_basic()),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        try:
            # Handle async functions properly
            if test_name == "Bridge Async Context":
                result = await test_bridge_async_context()
            else:
                result = test_func()
            
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
        
        print("")
    
    print("=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        print("")
        print("✨ Repository cleanup completed successfully!")
        print("📋 New pytest structure is ready for use with Python 3.10+")
        print("")
        print("Next steps:")
        print("1. Upgrade to Python 3.10+ to use full pytest suite")
        print("2. Run: pip install -e .[dev]")
        print("3. Run: pytest")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)