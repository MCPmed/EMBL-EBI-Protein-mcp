#!/usr/bin/env python3
"""
EMBL-EBI Proteins API Bridge
Functionality wrapper for the EMBL-EBI Proteins REST API
"""

import logging
import asyncio
from typing import Any, Dict, Optional
from urllib.parse import urlencode
import aiohttp
from aiohttp import ClientTimeout, ClientError

logger = logging.getLogger("embl-ebi-bridge")


class EMBLEBIBridge:
    """
    Functionality wrapper for the EMBL-EBI Proteins REST API
    Handles all API interactions and data processing
    """
    
    def __init__(self):
        self.base_url = "https://www.ebi.ac.uk/proteins/api"
        self.session: Optional[aiohttp.ClientSession] = None
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "EMBL-EBI-MCP-Client/1.0"
        }
        self.timeout = ClientTimeout(total=30, connect=10)
        self.max_retries = 3
        self.retry_delay = 1.0
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make HTTP request to the API with retry logic"""
        if not self.session:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
        
        # Properly join URL parts
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        if params:
            # Clean up None values
            params = {k: v for k, v in params.items() if v is not None}
            url += f"?{urlencode(params)}"
        
        logger.info(f"Making request to: {url}")
        
        for attempt in range(self.max_retries):
            try:
                async with self.session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 404:
                        error_text = await response.text()
                        raise ValueError(f"Resource not found (404): {error_text}")
                    elif response.status == 429:
                        # Rate limited - wait and retry
                        retry_after = int(response.headers.get('Retry-After', self.retry_delay * (attempt + 1)))
                        logger.warning(f"Rate limited. Waiting {retry_after} seconds before retry...")
                        await asyncio.sleep(retry_after)
                        continue
                    elif response.status >= 500:
                        # Server error - retry
                        error_text = await response.text()
                        if attempt < self.max_retries - 1:
                            logger.warning(f"Server error {response.status}. Retrying in {self.retry_delay * (attempt + 1)} seconds...")
                            await asyncio.sleep(self.retry_delay * (attempt + 1))
                            continue
                        raise Exception(f"Server error {response.status}: {error_text}")
                    else:
                        error_text = await response.text()
                        raise Exception(f"API request failed with status {response.status}: {error_text}")
            
            except ClientError as e:
                # Network errors - retry
                if attempt < self.max_retries - 1:
                    logger.warning(f"Network error: {str(e)}. Retrying in {self.retry_delay * (attempt + 1)} seconds...")
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                logger.error(f"Request failed after {self.max_retries} attempts: {str(e)}")
                raise
            except asyncio.TimeoutError:
                if attempt < self.max_retries - 1:
                    logger.warning(f"Request timeout. Retrying in {self.retry_delay * (attempt + 1)} seconds...")
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                logger.error(f"Request timeout after {self.max_retries} attempts")
                raise
            except Exception as e:
                logger.error(f"Request failed: {str(e)}")
                raise
        
        raise Exception(f"Failed to complete request after {self.max_retries} attempts")
    
    # Proteins endpoints
    async def find_protein_accession(self, gene_name: str, organism: str = "human") -> Dict[str, Any]:
        """Find UniProt accession for a gene/protein name
        
        Args:
            gene_name: Gene or protein name (e.g., 'p53', 'TP53', 'insulin')
            organism: Organism name or taxonomy (default: 'human')
        
        Returns:
            Dictionary with search results including accession numbers
        """
        # Map common organism names to taxonomy IDs
        organism_map = {
            "human": "9606",
            "mouse": "10090", 
            "rat": "10116",
            "yeast": "559292",
            "e.coli": "83333",
            "drosophila": "7227"
        }
        
        params = {"offset": 0, "size": 10}
        
        # Use taxonomy ID if organism is recognized
        if organism.lower() in organism_map:
            params["taxid"] = organism_map[organism.lower()]
        else:
            params["organism"] = organism
            
        # Search by gene name
        params["gene"] = gene_name
        
        try:
            result = await self._make_request("proteins", params)
            return result
        except Exception:
            # Fallback to protein name search
            params.pop("gene", None)
            params["protein"] = gene_name
            return await self._make_request("proteins", params)

    async def get_protein_summary(self, gene_name: str, organism: str = "human") -> Dict[str, Any]:
        """Get a comprehensive protein summary including basic info, features, and interactions
        
        Args:
            gene_name: Gene or protein name (e.g., 'p53', 'TP53', 'insulin')
            organism: Organism name (default: 'human')
        
        Returns:
            Dictionary with protein summary including accession, basic info, features, and interactions
        """
        try:
            # First find the accession
            search_result = await self.find_protein_accession(gene_name, organism)
            
            if not search_result or len(search_result) == 0:
                return {"error": f"No protein found for {gene_name} in {organism}"}
            
            # Get the first (most relevant) result
            protein = search_result[0] if isinstance(search_result, list) else search_result
            accession = protein.get("accession")
            
            if not accession:
                return {"error": "No accession found in search results"}
            
            # Get detailed protein info
            summary = {
                "gene_name": gene_name,
                "organism": organism,
                "accession": accession,
                "basic_info": protein
            }
            
            # Try to get additional info (features, interactions) but don't fail if they error
            try:
                features = await self.get_features_by_accession(accession)
                summary["features"] = features
            except Exception as e:
                summary["features_error"] = str(e)
            
            try:
                interactions = await self.get_protein_interactions(accession)
                summary["interactions"] = interactions
            except Exception as e:
                summary["interactions_error"] = str(e)
            
            return summary
            
        except Exception as e:
            return {"error": f"Failed to get protein summary: {str(e)}"}

    async def search_proteins(self, query: str, size: int = 20, offset: int = 0, **kwargs) -> Dict[str, Any]:
        """Search UniProt entries
        
        Args:
            query: Search term - will be used as protein name by default
            size: Number of results to return
            offset: Offset for pagination
            **kwargs: Additional search parameters like accession, gene, organism, taxid, etc.
        """
        params = {"offset": offset, "size": size}
        
        # If additional parameters are provided, use them
        if kwargs:
            params.update(kwargs)
        else:
            # Default to protein name search
            params["protein"] = query
            
        return await self._make_request("proteins", params)
    
    async def get_protein_by_accession(self, accession: str) -> Dict[str, Any]:
        """Get UniProt entry by accession"""
        return await self._make_request(f"proteins/{accession}")
    
    async def get_protein_interactions(self, accession: str) -> Dict[str, Any]:
        """Get UniProt interactions by accession"""
        return await self._make_request(f"proteins/interaction/{accession}")
    
    async def get_protein_isoforms(self, accession: str) -> Dict[str, Any]:
        """Get UniProt isoform entries from parent entry accession"""
        return await self._make_request(f"proteins/{accession}/isoforms")
    
    async def get_protein_by_crossref(self, dbtype: str, dbid: str) -> Dict[str, Any]:
        """Get UniProt entries by cross reference"""
        return await self._make_request(f"proteins/{dbtype}:{dbid}")
    
    # Features endpoints
    async def search_features(self, query: str, size: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Search protein sequence features in UniProt"""
        # For features, use accession parameter for searching
        params = {"offset": offset, "size": size, "accession": query}
        return await self._make_request("features", params)
    
    async def get_features_by_accession(self, accession: str) -> Dict[str, Any]:
        """Get UniProt protein sequence features by accession"""
        return await self._make_request(f"features/{accession}")
    
    async def get_features_by_type(self, feature_type: str, size: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Search protein sequence features of a given type in UniProt"""
        params = {"offset": offset, "size": size}
        return await self._make_request(f"features/type/{feature_type}", params)
    
    # Variation endpoints
    async def search_variations(self, query: str, size: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Search natural variants in UniProt"""
        # For variations, use accession parameter for searching
        params = {"offset": offset, "size": size, "accession": query}
        return await self._make_request("variation", params)
    
    async def get_variations_by_accession(self, accession: str) -> Dict[str, Any]:
        """Get natural variants by UniProt accession"""
        return await self._make_request(f"variation/{accession}")
    
    async def get_variations_by_dbsnp(self, dbid: str) -> Dict[str, Any]:
        """Get natural variants in UniProt by NIH-NCBI SNP database identifier"""
        return await self._make_request(f"variation/dbsnp/{dbid}")
    
    async def get_variations_by_hgvs(self, hgvs: str) -> Dict[str, Any]:
        """Get natural variants in UniProt by HGVS expression"""
        return await self._make_request(f"variation/hgvs/{hgvs}")
    
    async def get_variations_by_locations(self, accession_locations: str) -> Dict[str, Any]:
        """Get natural variants by list of accession and its locations"""
        return await self._make_request(f"variation/accession_locations/{accession_locations}")
    
    # Antigen endpoints
    async def search_antigens(self, query: str, size: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Search antigens in UniProt"""
        # For antigens, use accession parameter for searching
        params = {"offset": offset, "size": size, "accession": query}
        return await self._make_request("antigen", params)
    
    async def get_antigen_by_accession(self, accession: str) -> Dict[str, Any]:
        """Get antigen by UniProt accession"""
        return await self._make_request(f"antigen/{accession}")
    
    # Epitope endpoints
    async def search_epitopes(self, query: str, size: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Search epitopes in UniProt"""
        params = {"offset": offset, "size": size, "query": query}
        return await self._make_request("epitope", params)
    
    async def get_epitope_by_accession(self, accession: str) -> Dict[str, Any]:
        """Get epitope by UniProt accession"""
        return await self._make_request(f"epitope/{accession}")
    
    # Mutagenesis endpoints
    async def search_mutagenesis(self, query: str, size: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Search mutagenesis in UniProt"""
        params = {"offset": offset, "size": size, "query": query}
        return await self._make_request("mutagenesis", params)
    
    async def get_mutagenesis_by_accession(self, accession: str) -> Dict[str, Any]:
        """Get mutagenesis mapped to UniProt by accession"""
        return await self._make_request(f"mutagenesis/{accession}")
    
    # RNA Editing endpoints
    async def search_rna_editing(self, query: str, size: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Search RNA editing in UniProt"""
        params = {"offset": offset, "size": size, "query": query}
        return await self._make_request("rna-editing", params)
    
    async def get_rna_editing_by_accession(self, accession: str) -> Dict[str, Any]:
        """Get RNA editing mapped to UniProt by accession"""
        return await self._make_request(f"rna-editing/{accession}")
    
    # Proteomics endpoints
    async def search_proteomics(self, query: str, size: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Search proteomics peptides in UniProt"""
        params = {"offset": offset, "size": size, "query": query}
        return await self._make_request("proteomics", params)
    
    async def get_proteomics_by_accession(self, accession: str) -> Dict[str, Any]:
        """Get proteomics peptides mapped to UniProt by accession"""
        return await self._make_request(f"proteomics/{accession}")
    
    async def search_proteomics_nonptm(self, query: str, size: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Search non-PTM proteomics peptides in UniProt"""
        params = {"offset": offset, "size": size, "query": query}
        return await self._make_request("proteomics/nonPtm", params)
    
    async def get_proteomics_nonptm_by_accession(self, accession: str) -> Dict[str, Any]:
        """Get non-PTM proteomics peptides mapped to UniProt by accession"""
        return await self._make_request(f"proteomics/nonPtm/{accession}")
    
    async def search_proteomics_ptm(self, query: str, size: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Search PTM proteomics peptides in UniProt"""
        params = {"offset": offset, "size": size, "query": query}
        return await self._make_request("proteomics/ptm", params)
    
    async def get_proteomics_ptm_by_accession(self, accession: str) -> Dict[str, Any]:
        """Get PTM proteomics peptides mapped to UniProt by accession"""
        return await self._make_request(f"proteomics/ptm/{accession}")
    
    async def search_hpp(self, query: str, size: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Search HPP peptides in UniProt"""
        params = {"offset": offset, "size": size, "query": query}
        return await self._make_request("hpp", params)
    
    async def get_hpp_by_accession(self, accession: str) -> Dict[str, Any]:
        """Get HPP peptides mapped to UniProt by accession"""
        return await self._make_request(f"hpp/{accession}")
    
    async def get_proteomics_species(self) -> Dict[str, Any]:
        """Get proteomics species metadata in UniProt"""
        return await self._make_request("proteomics/species")
    
    async def search_proteomics_species(self, query: str) -> Dict[str, Any]:
        """Search proteomics species metadata in UniProt"""
        params = {"query": query}
        return await self._make_request("proteomics/species/search", params)
    
    # Proteomes endpoints
    async def search_proteomes(self, query: str, size: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Search proteomes in UniProt"""
        params = {"offset": offset, "size": size, "query": query}
        return await self._make_request("proteomes", params)
    
    async def get_proteome_by_upid(self, upid: str) -> Dict[str, Any]:
        """Get proteome by proteome UPID"""
        return await self._make_request(f"proteomes/{upid}")
    
    async def get_proteome_proteins(self, upid: str) -> Dict[str, Any]:
        """Get proteins by proteome UPID"""
        return await self._make_request(f"proteomes/proteins/{upid}")
    
    async def search_genecentric(self, query: str, size: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Search gene centric proteins"""
        params = {"offset": offset, "size": size, "query": query}
        return await self._make_request("genecentric", params)
    
    async def get_genecentric_by_accession(self, accession: str) -> Dict[str, Any]:
        """Get gene centric proteins by UniProt accession"""
        return await self._make_request(f"genecentric/{accession}")
    
    # Taxonomy endpoints
    async def get_taxonomy_by_id(self, tax_id: str) -> Dict[str, Any]:
        """Get details about a taxonomy node"""
        return await self._make_request(f"taxonomy/id/{tax_id}")
    
    async def get_taxonomy_node_by_id(self, tax_id: str) -> Dict[str, Any]:
        """Get taxonomy node details"""
        return await self._make_request(f"taxonomy/id/{tax_id}/node")
    
    async def get_taxonomy_children(self, tax_id: str) -> Dict[str, Any]:
        """Get children nodes of a taxonomy node"""
        return await self._make_request(f"taxonomy/id/{tax_id}/children")
    
    async def get_taxonomy_children_nodes(self, tax_id: str) -> Dict[str, Any]:
        """Get children node details of a taxonomy node"""
        return await self._make_request(f"taxonomy/id/{tax_id}/children/node")
    
    async def get_taxonomy_parent(self, tax_id: str) -> Dict[str, Any]:
        """Get parent node of a taxonomy node"""
        return await self._make_request(f"taxonomy/id/{tax_id}/parent")
    
    async def get_taxonomy_parent_node(self, tax_id: str) -> Dict[str, Any]:
        """Get parent node details of a taxonomy node"""
        return await self._make_request(f"taxonomy/id/{tax_id}/parent/node")
    
    async def get_taxonomy_siblings(self, tax_id: str) -> Dict[str, Any]:
        """Get sibling nodes of a taxonomy node"""
        return await self._make_request(f"taxonomy/id/{tax_id}/siblings")
    
    async def get_taxonomy_siblings_nodes(self, tax_id: str) -> Dict[str, Any]:
        """Get sibling node details of a taxonomy node"""
        return await self._make_request(f"taxonomy/id/{tax_id}/siblings/node")
    
    async def get_taxonomy_lineage(self, tax_id: str) -> Dict[str, Any]:
        """Get taxonomic lineage for a given taxonomy node"""
        return await self._make_request(f"taxonomy/lineage/{tax_id}")
    
    async def get_taxonomy_by_name(self, name: str) -> Dict[str, Any]:
        """Get taxonomy nodes with specific name"""
        return await self._make_request(f"taxonomy/name/{name}")
    
    async def get_taxonomy_nodes_by_name(self, name: str) -> Dict[str, Any]:
        """Get taxonomy node details with specific name"""
        return await self._make_request(f"taxonomy/name/{name}/node")
    
    async def get_taxonomy_ancestor(self, ids: str) -> Dict[str, Any]:
        """Get lowest common ancestor of taxonomy nodes"""
        return await self._make_request(f"taxonomy/ancestor/{ids}")
    
    async def get_taxonomy_by_ids(self, ids: str) -> Dict[str, Any]:
        """Get multiple taxonomy node details"""
        return await self._make_request(f"taxonomy/ids/{ids}")
    
    async def get_taxonomy_nodes_by_ids(self, ids: str) -> Dict[str, Any]:
        """Get multiple taxonomy node details (nodes only)"""
        return await self._make_request(f"taxonomy/ids/{ids}/node")
    
    async def get_taxonomy_path(self, tax_id: str, direction: str = "TOP", depth: int = 1) -> Dict[str, Any]:
        """Get taxonomic path"""
        params = {"id": tax_id, "direction": direction, "depth": depth}
        return await self._make_request("taxonomy/path", params)
    
    async def get_taxonomy_path_nodes(self, tax_id: str, direction: str = "TOP", depth: int = 1) -> Dict[str, Any]:
        """Get taxonomic path nodes"""
        params = {"id": tax_id, "direction": direction, "depth": depth}
        return await self._make_request("taxonomy/path/nodes", params)
    
    async def get_taxonomy_relationship(self, id_from: str, id_to: str) -> Dict[str, Any]:
        """Get relationship between two taxonomy nodes"""
        params = {"from": id_from, "to": id_to}
        return await self._make_request("taxonomy/relationship", params)
    
    # Coordinates endpoints
    async def search_coordinates(self, query: str, size: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Search genomic coordinates for UniProt entries"""
        params = {"offset": offset, "size": size, "query": query}
        return await self._make_request("coordinates", params)
    
    async def get_coordinates_by_accession(self, accession: str) -> Dict[str, Any]:
        """Get genomic coordinates for a UniProt accession"""
        return await self._make_request(f"coordinates/{accession}")
    
    async def get_coordinates_by_crossref(self, dbtype: str, dbid: str) -> Dict[str, Any]:
        """Get coordinates by genomic database cross reference"""
        return await self._make_request(f"coordinates/{dbtype}:{dbid}")
    
    async def get_coordinates_by_location(self, accession: str, position: str) -> Dict[str, Any]:
        """Get genome coordinate by protein sequence position"""
        return await self._make_request(f"coordinates/location/{accession}:{position}")
    
    async def get_coordinates_by_genome_location(self, taxonomy: str, chromosome: str, position: str) -> Dict[str, Any]:
        """Get genome coordinate by genomic position"""
        return await self._make_request(f"coordinates/glocation/{taxonomy}/{chromosome}:{position}")
    
    async def get_coordinates_by_taxonomy_locations(self, taxonomy: str, locations: str) -> Dict[str, Any]:
        """Search UniProt entries by taxonomy and genomic coordinates"""
        return await self._make_request(f"coordinates/{taxonomy}/{locations}")
    
    async def get_coordinates_features_by_taxonomy_locations(self, taxonomy: str, locations: str) -> Dict[str, Any]:
        """Search UniProt entries by taxonomy and genomic coordinates (features)"""
        return await self._make_request(f"coordinates/{taxonomy}/{locations}/feature")
    
    # UniParc endpoints
    async def search_uniparc(self, query: str, size: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Search UniParc entries"""
        params = {"offset": offset, "size": size, "query": query}
        return await self._make_request("uniparc", params)
    
    async def get_uniparc_by_upi(self, upi: str) -> Dict[str, Any]:
        """Get UniParc entry by UniParc UPI"""
        return await self._make_request(f"uniparc/upi/{upi}")
    
    async def get_uniparc_by_accession(self, accession: str) -> Dict[str, Any]:
        """Get UniParc entry by UniProt accession"""
        return await self._make_request(f"uniparc/accession/{accession}")
    
    async def get_uniparc_by_dbref(self, dbid: str) -> Dict[str, Any]:
        """Get UniParc entries by cross reference accessions"""
        return await self._make_request(f"uniparc/dbreference/{dbid}")
    
    async def get_uniparc_by_proteome(self, upid: str) -> Dict[str, Any]:
        """Get UniParc entries by Proteome UPID"""
        return await self._make_request(f"uniparc/proteome/{upid}")
    
    async def get_uniparc_bestguess(self, query: str) -> Dict[str, Any]:
        """Get UniParc longest sequence for entries"""
        params = {"query": query}
        return await self._make_request("uniparc/bestguess", params)
    
    async def post_uniparc_sequence(self, sequence: str) -> Dict[str, Any]:
        """Get UniParc entries by sequence (POST request)"""
        # This would require a POST request implementation
        # For now, we'll raise NotImplementedError
        raise NotImplementedError("POST requests not implemented in this bridge")