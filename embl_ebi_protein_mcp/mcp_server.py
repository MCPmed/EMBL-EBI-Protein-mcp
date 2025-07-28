#!/usr/bin/env python3
"""
MCP Server for EMBL-EBI Proteins API
Handles MCP protocol and tool definitions
"""

import json
import logging
from typing import Any, Dict, List, Callable
from mcp.server import Server
import mcp.types as types

# Handle both relative and absolute imports
try:
    from .bridge import EMBLEBIBridge
except ImportError:
    try:
        from embl_ebi_protein_mcp.bridge import EMBLEBIBridge
    except ImportError:
        from bridge import EMBLEBIBridge

logger = logging.getLogger("embl-ebi-mcp-server")


class EMBLEBIMCPServer:
    """
    MCP Server implementation for EMBL-EBI Proteins API
    Handles MCP protocol and tool definitions
    """
    
    def __init__(self):
        self.server = Server("embl-ebi-proteins")
        self.bridge = EMBLEBIBridge()
        self._tool_registry = {}
        self._setup_tools()
        self._register_global_tool_handler()
    
    def _register_tool(self, name: str, handler: Callable):
        """Register a tool handler in our registry (not directly with MCP server)"""
        self._tool_registry[name] = handler
        logger.info(f"Registered tool in registry: {name}")
    
    def _register_global_tool_handler(self):
        """Register a single global tool handler that routes to specific tools"""
        
        @self.server.call_tool()
        async def global_tool_handler(tool_name: str, arguments: dict) -> list[types.TextContent]:
            """Global handler that routes tool calls to the correct handler"""
            try:
                logger.info(f"Global handler called for tool: {tool_name} with arguments: {arguments}")
                
                # Find the handler for this tool
                if tool_name not in self._tool_registry:
                    logger.error(f"Tool not found: {tool_name}")
                    return [types.TextContent(
                        type="text",
                        text=f"Error: Tool '{tool_name}' not found"
                    )]
                
                # Call the specific tool handler
                handler = self._tool_registry[tool_name]
                logger.info(f"Calling handler for {tool_name}")
                result = await handler(arguments)
                logger.info(f"Tool {tool_name} completed successfully")
                return result
                
            except Exception as e:
                logger.error(f"Error in global tool handler for {tool_name}: {str(e)}", exc_info=True)
                return [types.TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
        
        logger.info("Registered global tool handler")
    
    def _setup_tools(self):
        """Register all available tools"""
        
        # Proteins tools
        async def get_protein_summary(arguments: dict) -> list[types.TextContent]:
            """Get comprehensive protein summary with all relevant information"""
            gene_name = arguments.get("gene_name", "")
            organism = arguments.get("organism", "human")
            
            if not gene_name:
                raise ValueError("gene_name parameter is required")
            
            async with self.bridge as bridge:
                result = await bridge.get_protein_summary(gene_name, organism)
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        async def find_protein_accession(arguments: dict) -> list[types.TextContent]:
            """Find UniProt accession number for a gene/protein name"""
            gene_name = arguments.get("gene_name", "")
            organism = arguments.get("organism", "human")
            
            if not gene_name:
                raise ValueError("gene_name parameter is required")
            
            async with self.bridge as bridge:
                result = await bridge.find_protein_accession(gene_name, organism)
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        async def search_proteins(arguments: dict) -> list[types.TextContent]:
            """Search UniProt protein entries"""
            query = arguments.get("query", "")
            size = arguments.get("size", 20)
            offset = arguments.get("offset", 0)
            
            async with self.bridge as bridge:
                result = await bridge.search_proteins(query, size, offset)
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        async def get_protein_by_accession(arguments: dict) -> list[types.TextContent]:
            """Get protein details by UniProt accession"""
            accession = arguments.get("accession")
            if not accession:
                raise ValueError("accession parameter is required")
            
            async with self.bridge as bridge:
                result = await bridge.get_protein_by_accession(accession)
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        async def get_protein_interactions(arguments: dict) -> list[types.TextContent]:
            """Get protein interactions by UniProt accession"""
            accession = arguments.get("accession")
            if not accession:
                raise ValueError("accession parameter is required")
            
            async with self.bridge as bridge:
                result = await bridge.get_protein_interactions(accession)
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        async def get_protein_isoforms(arguments: dict) -> list[types.TextContent]:
            """Get protein isoforms by UniProt accession"""
            accession = arguments.get("accession")
            if not accession:
                raise ValueError("accession parameter is required")
            
            async with self.bridge as bridge:
                result = await bridge.get_protein_isoforms(accession)
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        # Features tools
        async def search_features(arguments: dict) -> list[types.TextContent]:
            """Search protein sequence features"""
            query = arguments.get("query", "")
            size = arguments.get("size", 20)
            offset = arguments.get("offset", 0)
            
            async with self.bridge as bridge:
                result = await bridge.search_features(query, size, offset)
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        async def get_features_by_accession(arguments: dict) -> list[types.TextContent]:
            """Get protein features by UniProt accession"""
            accession = arguments.get("accession")
            if not accession:
                raise ValueError("accession parameter is required")
            
            async with self.bridge as bridge:
                result = await bridge.get_features_by_accession(accession)
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        async def get_features_by_type(arguments: dict) -> list[types.TextContent]:
            """Get protein features by feature type"""
            feature_type = arguments.get("feature_type")
            if not feature_type:
                raise ValueError("feature_type parameter is required")
            
            size = arguments.get("size", 20)
            offset = arguments.get("offset", 0)
            
            async with self.bridge as bridge:
                result = await bridge.get_features_by_type(feature_type, size, offset)
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        # Variation tools
        async def search_variations(arguments: dict) -> list[types.TextContent]:
            """Search natural variants"""
            query = arguments.get("query", "")
            size = arguments.get("size", 20)
            offset = arguments.get("offset", 0)
            
            async with self.bridge as bridge:
                result = await bridge.search_variations(query, size, offset)
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        async def get_variations_by_accession(arguments: dict) -> list[types.TextContent]:
            """Get variations by UniProt accession"""
            accession = arguments.get("accession")
            if not accession:
                raise ValueError("accession parameter is required")
            
            async with self.bridge as bridge:
                result = await bridge.get_variations_by_accession(accession)
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        async def get_variations_by_dbsnp(arguments: dict) -> list[types.TextContent]:
            """Get variations by dbSNP ID"""
            dbid = arguments.get("dbid")
            if not dbid:
                raise ValueError("dbid parameter is required")
            
            async with self.bridge as bridge:
                result = await bridge.get_variations_by_dbsnp(dbid)
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        # Antigen tools
        async def search_antigens(arguments: dict) -> list[types.TextContent]:
            """Search antigens"""
            query = arguments.get("query", "")
            size = arguments.get("size", 20)
            offset = arguments.get("offset", 0)
            
            async with self.bridge as bridge:
                result = await bridge.search_antigens(query, size, offset)
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        async def get_antigen_by_accession(arguments: dict) -> list[types.TextContent]:
            """Get antigen by UniProt accession"""
            accession = arguments.get("accession")
            if not accession:
                raise ValueError("accession parameter is required")
            
            async with self.bridge as bridge:
                result = await bridge.get_antigen_by_accession(accession)
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        # Epitope tools
        async def search_epitopes(arguments: dict) -> list[types.TextContent]:
            """Search epitopes"""
            query = arguments.get("query", "")
            size = arguments.get("size", 20)
            offset = arguments.get("offset", 0)
            
            async with self.bridge as bridge:
                result = await bridge.search_epitopes(query, size, offset)
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        async def get_epitope_by_accession(arguments: dict) -> list[types.TextContent]:
            """Get epitope by UniProt accession"""
            accession = arguments.get("accession")
            if not accession:
                raise ValueError("accession parameter is required")
            
            async with self.bridge as bridge:
                result = await bridge.get_epitope_by_accession(accession)
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        # Proteomics tools
        async def search_proteomics(arguments: dict) -> list[types.TextContent]:
            """Search proteomics data"""
            query = arguments.get("query", "")
            size = arguments.get("size", 20)
            offset = arguments.get("offset", 0)
            
            async with self.bridge as bridge:
                result = await bridge.search_proteomics(query, size, offset)
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        async def get_proteomics_by_accession(arguments: dict) -> list[types.TextContent]:
            """Get proteomics data by UniProt accession"""
            accession = arguments.get("accession")
            if not accession:
                raise ValueError("accession parameter is required")
            
            async with self.bridge as bridge:
                result = await bridge.get_proteomics_by_accession(accession)
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        async def get_proteomics_species(arguments: dict) -> list[types.TextContent]:
            """Get proteomics species metadata"""
            async with self.bridge as bridge:
                result = await bridge.get_proteomics_species()
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        # Proteomes tools
        async def search_proteomes(arguments: dict) -> list[types.TextContent]:
            """Search proteomes"""
            query = arguments.get("query", "")
            size = arguments.get("size", 20)
            offset = arguments.get("offset", 0)
            
            async with self.bridge as bridge:
                result = await bridge.search_proteomes(query, size, offset)
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        async def get_proteome_by_upid(arguments: dict) -> list[types.TextContent]:
            """Get proteome by UPID"""
            upid = arguments.get("upid")
            if not upid:
                raise ValueError("upid parameter is required")
            
            async with self.bridge as bridge:
                result = await bridge.get_proteome_by_upid(upid)
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        async def get_proteome_proteins(arguments: dict) -> list[types.TextContent]:
            """Get proteins by proteome UPID"""
            upid = arguments.get("upid")
            if not upid:
                raise ValueError("upid parameter is required")
            
            async with self.bridge as bridge:
                result = await bridge.get_proteome_proteins(upid)
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        # Taxonomy tools
        async def get_taxonomy_by_id(arguments: dict) -> list[types.TextContent]:
            """Get taxonomy details by ID"""
            tax_id = arguments.get("tax_id")
            if not tax_id:
                raise ValueError("tax_id parameter is required")
            
            async with self.bridge as bridge:
                result = await bridge.get_taxonomy_by_id(str(tax_id))
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        async def get_taxonomy_lineage(arguments: dict) -> list[types.TextContent]:
            """Get taxonomic lineage by ID"""
            tax_id = arguments.get("tax_id")
            if not tax_id:
                raise ValueError("tax_id parameter is required")
            
            async with self.bridge as bridge:
                result = await bridge.get_taxonomy_lineage(str(tax_id))
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        async def get_taxonomy_children(arguments: dict) -> list[types.TextContent]:
            """Get taxonomy children by ID"""
            tax_id = arguments.get("tax_id")
            if not tax_id:
                raise ValueError("tax_id parameter is required")
            
            async with self.bridge as bridge:
                result = await bridge.get_taxonomy_children(str(tax_id))
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        # Coordinates tools
        async def search_coordinates(arguments: dict) -> list[types.TextContent]:
            """Search genomic coordinates"""
            query = arguments.get("query", "")
            size = arguments.get("size", 20)
            offset = arguments.get("offset", 0)
            
            async with self.bridge as bridge:
                result = await bridge.search_coordinates(query, size, offset)
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        async def get_coordinates_by_accession(arguments: dict) -> list[types.TextContent]:
            """Get genomic coordinates by UniProt accession"""
            accession = arguments.get("accession")
            if not accession:
                raise ValueError("accession parameter is required")
            
            async with self.bridge as bridge:
                result = await bridge.get_coordinates_by_accession(accession)
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        # UniParc tools
        async def search_uniparc(arguments: dict) -> list[types.TextContent]:
            """Search UniParc entries"""
            query = arguments.get("query", "")
            size = arguments.get("size", 20)
            offset = arguments.get("offset", 0)
            
            async with self.bridge as bridge:
                result = await bridge.search_uniparc(query, size, offset)
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        async def get_uniparc_by_upi(arguments: dict) -> list[types.TextContent]:
            """Get UniParc entry by UPI"""
            upi = arguments.get("upi")
            if not upi:
                raise ValueError("upi parameter is required")
            
            async with self.bridge as bridge:
                result = await bridge.get_uniparc_by_upi(upi)
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        async def get_uniparc_by_accession(arguments: dict) -> list[types.TextContent]:
            """Get UniParc entry by UniProt accession"""
            accession = arguments.get("accession")
            if not accession:
                raise ValueError("accession parameter is required")
            
            async with self.bridge as bridge:
                result = await bridge.get_uniparc_by_accession(accession)
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        # Register all tools using the explicit registration method
        self._register_tool("get_protein_summary", get_protein_summary)
        self._register_tool("find_protein_accession", find_protein_accession)
        self._register_tool("search_proteins", search_proteins)
        self._register_tool("get_protein_by_accession", get_protein_by_accession)
        self._register_tool("get_protein_interactions", get_protein_interactions)
        self._register_tool("get_protein_isoforms", get_protein_isoforms)
        self._register_tool("search_features", search_features)
        self._register_tool("get_features_by_accession", get_features_by_accession)
        self._register_tool("get_features_by_type", get_features_by_type)
        self._register_tool("search_variations", search_variations)
        self._register_tool("get_variations_by_accession", get_variations_by_accession)
        self._register_tool("get_variations_by_dbsnp", get_variations_by_dbsnp)
        self._register_tool("search_antigens", search_antigens)
        self._register_tool("get_antigen_by_accession", get_antigen_by_accession)
        self._register_tool("search_epitopes", search_epitopes)
        self._register_tool("get_epitope_by_accession", get_epitope_by_accession)
        self._register_tool("search_proteomics", search_proteomics)
        self._register_tool("get_proteomics_by_accession", get_proteomics_by_accession)
        self._register_tool("get_proteomics_species", get_proteomics_species)
        self._register_tool("search_proteomes", search_proteomes)
        self._register_tool("get_proteome_by_upid", get_proteome_by_upid)
        self._register_tool("get_proteome_proteins", get_proteome_proteins)
        self._register_tool("get_taxonomy_by_id", get_taxonomy_by_id)
        self._register_tool("get_taxonomy_lineage", get_taxonomy_lineage)
        self._register_tool("get_taxonomy_children", get_taxonomy_children)
        self._register_tool("search_coordinates", search_coordinates)
        self._register_tool("get_coordinates_by_accession", get_coordinates_by_accession)
        self._register_tool("search_uniparc", search_uniparc)
        self._register_tool("get_uniparc_by_upi", get_uniparc_by_upi)
        self._register_tool("get_uniparc_by_accession", get_uniparc_by_accession)
        
        logger.info(f"Registered {len(self._tool_registry)} tools")
    
    def get_server(self) -> Server:
        """Get the configured MCP server"""
        return self.server
    
    def get_tool_definitions(self) -> List[types.Tool]:
        """Get all tool definitions for the server"""
        return [
            # Proteins tools
            types.Tool(
                name="get_protein_summary",
                description="⭐ BEST STARTING POINT: Get comprehensive protein information in one call. Automatically finds the protein, gets basic details, sequence features, and interactions. Perfect for getting an overview of any protein. Example: gene_name='p53' returns everything about human p53.",
                inputSchema={
                    "type": "object", 
                    "properties": {
                        "gene_name": {
                            "type": "string",
                            "description": "Gene or protein name (e.g., 'p53', 'insulin', 'BRCA1', 'hemoglobin', 'myosin')"
                        },
                        "organism": {
                            "type": "string",
                            "description": "Organism name - supports: 'human' (default), 'mouse', 'rat', 'yeast', 'e.coli', 'drosophila'",
                            "default": "human"
                        }
                    },
                    "required": ["gene_name"]
                }
            ),
            types.Tool(
                name="find_protein_accession", 
                description="🔍 Find UniProt accession numbers for protein/gene names. Use when you only need the accession ID for other functions. For complete protein info, use get_protein_summary instead.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "gene_name": {
                            "type": "string", 
                            "description": "Gene or protein name (e.g., 'p53', 'TP53', 'insulin', 'BRCA1', 'hemoglobin')"
                        },
                        "organism": {
                            "type": "string",
                            "description": "Organism name - supports: 'human' (default), 'mouse', 'rat', 'yeast', 'e.coli', 'drosophila', or any species name",
                            "default": "human"
                        }
                    },
                    "required": ["gene_name"]
                }
            ),
            types.Tool(
                name="search_proteins",
                description="🔍 Search UniProt protein database by text query. Returns proteins that match your search terms in their names, descriptions, or annotations. Use when you want to browse proteins related to a topic.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search terms (e.g., 'kinase', 'tumor suppressor', 'insulin receptor')"
                        },
                        "size": {
                            "type": "integer",
                            "description": "Number of results to return (1-100, default: 20)",
                            "default": 20
                        },
                        "offset": {
                            "type": "integer", 
                            "description": "Starting position for pagination (default: 0)",
                            "default": 0
                        }
                    },
                    "required": ["query"]
                }
            ),
            types.Tool(
                name="get_protein_by_accession",
                description="📋 Get complete protein information using UniProt accession. Returns detailed data including sequence, function, structure, interactions, and references. Use after finding accession with find_protein_accession.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "accession": {
                            "type": "string",
                            "description": "UniProt accession number (e.g., P04637 for human p53, P01308 for human insulin)"
                        }
                    },
                    "required": ["accession"]
                }
            ),
            types.Tool(
                name="get_protein_interactions",
                description="🤝 Get known protein-protein interactions. Shows which other proteins interact with your protein of interest, useful for understanding biological pathways and networks.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "accession": {
                            "type": "string",
                            "description": "UniProt accession number (get this first with find_protein_accession)"
                        }
                    },
                    "required": ["accession"]
                }
            ),
            types.Tool(
                name="get_protein_isoforms",
                description="🧬 Get alternative protein isoforms (splice variants). Shows different versions of the same protein created by alternative splicing.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "accession": {
                            "type": "string",
                            "description": "UniProt accession number of the main protein entry"
                        }
                    },
                    "required": ["accession"]
                }
            ),
            
            # Features tools
            types.Tool(
                name="search_features",
                description="🎯 Search for specific protein sequence features across all proteins. Use when looking for particular domains, binding sites, or structural elements.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Feature search terms (e.g., 'DNA binding domain', 'kinase domain', 'signal peptide')"
                        },
                        "size": {
                            "type": "integer",
                            "description": "Number of results to return (1-100, default: 20)",
                            "default": 20
                        },
                        "offset": {
                            "type": "integer",
                            "description": "Starting position for pagination (default: 0)",
                            "default": 0
                        }
                    },
                    "required": ["query"]
                }
            ),
            types.Tool(
                name="get_features_by_accession",
                description="🎯 Get all sequence features for a specific protein. Shows domains, binding sites, modifications, and structural annotations for the protein.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "accession": {
                            "type": "string",
                            "description": "UniProt accession number (get this first with find_protein_accession)"
                        }
                    },
                    "required": ["accession"]
                }
            ),
            types.Tool(
                name="get_features_by_type",
                description="Get protein features by feature type",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "feature_type": {
                            "type": "string",
                            "description": "Feature type (e.g., DOMAIN, REGION, SITE)"
                        },
                        "size": {
                            "type": "integer",
                            "description": "Number of results to return (default: 20)",
                            "default": 20
                        },
                        "offset": {
                            "type": "integer",
                            "description": "Offset for pagination (default: 0)",
                            "default": 0
                        }
                    },
                    "required": ["feature_type"]
                }
            ),
            
            # Add remaining tool definitions (truncated for brevity - same as before)
            types.Tool(
                name="search_variations",
                description="Search natural variants in proteins",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query for variations"},
                        "size": {"type": "integer", "description": "Number of results (default: 20)", "default": 20},
                        "offset": {"type": "integer", "description": "Offset for pagination (default: 0)", "default": 0}
                    },
                    "required": ["query"]
                }
            ),
            types.Tool(
                name="get_variations_by_accession",
                description="Get variations by UniProt accession",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "accession": {"type": "string", "description": "UniProt accession number"}
                    },
                    "required": ["accession"]
                }
            ),
            types.Tool(
                name="get_variations_by_dbsnp",
                description="Get variations by dbSNP ID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dbid": {"type": "string", "description": "dbSNP identifier"}
                    },
                    "required": ["dbid"]
                }
            ),
            types.Tool(
                name="search_antigens",
                description="Search antigens in UniProt",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query for antigens"},
                        "size": {"type": "integer", "description": "Number of results (default: 20)", "default": 20},
                        "offset": {"type": "integer", "description": "Offset for pagination (default: 0)", "default": 0}
                    },
                    "required": ["query"]
                }
            ),
            types.Tool(
                name="get_antigen_by_accession",
                description="Get antigen by UniProt accession",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "accession": {"type": "string", "description": "UniProt accession number"}
                    },
                    "required": ["accession"]
                }
            ),
            types.Tool(
                name="search_epitopes",
                description="Search epitopes in UniProt",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query for epitopes"},
                        "size": {"type": "integer", "description": "Number of results (default: 20)", "default": 20},
                        "offset": {"type": "integer", "description": "Offset for pagination (default: 0)", "default": 0}
                    },
                    "required": ["query"]
                }
            ),
            types.Tool(
                name="get_epitope_by_accession",
                description="Get epitope by UniProt accession",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "accession": {"type": "string", "description": "UniProt accession number"}
                    },
                    "required": ["accession"]
                }
            ),
            types.Tool(
                name="search_proteomics",
                description="Search proteomics data",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query for proteomics data"},
                        "size": {"type": "integer", "description": "Number of results (default: 20)", "default": 20},
                        "offset": {"type": "integer", "description": "Offset for pagination (default: 0)", "default": 0}
                    },
                    "required": ["query"]
                }
            ),
            types.Tool(
                name="get_proteomics_by_accession",
                description="Get proteomics data by UniProt accession",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "accession": {"type": "string", "description": "UniProt accession number"}
                    },
                    "required": ["accession"]
                }
            ),
            types.Tool(
                name="get_proteomics_species",
                description="Get proteomics species metadata",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            types.Tool(
                name="search_proteomes",
                description="Search proteomes",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query for proteomes"},
                        "size": {"type": "integer", "description": "Number of results (default: 20)", "default": 20},
                        "offset": {"type": "integer", "description": "Offset for pagination (default: 0)", "default": 0}
                    },
                    "required": ["query"]
                }
            ),
            types.Tool(
                name="get_proteome_by_upid",
                description="Get proteome by UPID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "upid": {"type": "string", "description": "UniProt Proteome ID"}
                    },
                    "required": ["upid"]
                }
            ),
            types.Tool(
                name="get_proteome_proteins",
                description="Get proteins by proteome UPID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "upid": {"type": "string", "description": "UniProt Proteome ID"}
                    },
                    "required": ["upid"]
                }
            ),
            types.Tool(
                name="get_taxonomy_by_id",
                description="🌳 Get taxonomic information for an organism. Returns scientific name, common name, and classification details. Common IDs: human=9606, mouse=10090, yeast=559292.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "tax_id": {"type": "string", "description": "NCBI Taxonomy ID (e.g., '9606' for human, '10090' for mouse)"}
                    },
                    "required": ["tax_id"]
                }
            ),
            types.Tool(
                name="get_taxonomy_lineage",
                description="🌳 Get complete taxonomic lineage showing evolutionary classification from species to domain (e.g., Homo sapiens → Primates → Mammalia → Chordata → Eukaryota).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "tax_id": {"type": "string", "description": "NCBI Taxonomy ID (e.g., '9606' for human lineage)"}
                    },
                    "required": ["tax_id"]
                }
            ),
            types.Tool(
                name="get_taxonomy_children",
                description="Get taxonomy children by ID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "tax_id": {"type": "string", "description": "NCBI Taxonomy ID"}
                    },
                    "required": ["tax_id"]
                }
            ),
            types.Tool(
                name="search_coordinates",
                description="Search genomic coordinates",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query for coordinates"},
                        "size": {"type": "integer", "description": "Number of results (default: 20)", "default": 20},
                        "offset": {"type": "integer", "description": "Offset for pagination (default: 0)", "default": 0}
                    },
                    "required": ["query"]
                }
            ),
            types.Tool(
                name="get_coordinates_by_accession",
                description="Get genomic coordinates by UniProt accession",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "accession": {"type": "string", "description": "UniProt accession number"}
                    },
                    "required": ["accession"]
                }
            ),
            types.Tool(
                name="search_uniparc",
                description="Search UniParc entries",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query for UniParc entries"},
                        "size": {"type": "integer", "description": "Number of results (default: 20)", "default": 20},
                        "offset": {"type": "integer", "description": "Offset for pagination (default: 0)", "default": 0}
                    },
                    "required": ["query"]
                }
            ),
            types.Tool(
                name="get_uniparc_by_upi",
                description="Get UniParc entry by UPI",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "upi": {"type": "string", "description": "UniParc identifier (UPI)"}
                    },
                    "required": ["upi"]
                }
            ),
            types.Tool(
                name="get_uniparc_by_accession",
                description="Get UniParc entry by UniProt accession",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "accession": {"type": "string", "description": "UniProt accession number"}
                    },
                    "required": ["accession"]
                }
            )
        ]