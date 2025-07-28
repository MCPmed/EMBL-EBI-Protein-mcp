#!/usr/bin/env python3
"""
EMBL-EBI Proteins API MCP Server Package
"""

from .bridge import EMBLEBIBridge

__version__ = "0.1.0"
__author__ = "M. Flotho"
__email__ = "matthias.flotho@ccb.uni-saarland.de"

__all__ = ["EMBLEBIBridge"]

# Lazy import of MCP server to avoid import errors when MCP is not installed
def get_mcp_server():
    try:
        from .mcp_server import EMBLEBIMCPServer
        return EMBLEBIMCPServer
    except ImportError as e:
        raise ImportError(f"MCP server requires the 'mcp' package to be installed: {e}")