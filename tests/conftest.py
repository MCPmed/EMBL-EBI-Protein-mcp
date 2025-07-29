"""
Pytest configuration and fixtures for EMBL-EBI Protein MCP tests.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from embl_ebi_protein_mcp.bridge import EMBLEBIBridge
from embl_ebi_protein_mcp.mcp_server import EMBLEBIMCPServer


@pytest.fixture
def bridge():
    """Create a mock EMBLEBIBridge instance for testing."""
    bridge = EMBLEBIBridge()
    return bridge


@pytest.fixture
def mock_bridge():
    """Create a fully mocked EMBLEBIBridge instance."""
    bridge = MagicMock(spec=EMBLEBIBridge)
    
    # Mock common methods
    bridge.get_protein_by_accession = AsyncMock()
    bridge.search_proteins = AsyncMock()
    bridge.get_taxonomy_by_id = AsyncMock()
    bridge.find_protein_accession = AsyncMock()
    bridge.get_protein_summary = AsyncMock()
    bridge.get_features_by_accession = AsyncMock()
    bridge.get_protein_interactions = AsyncMock()
    
    return bridge


@pytest.fixture
def mcp_server():
    """Create an EMBLEBIMCPServer instance for testing."""
    return EMBLEBIMCPServer()


@pytest.fixture
def mock_mcp_server(mock_bridge):
    """Create an EMBLEBIMCPServer with mocked bridge."""
    server = EMBLEBIMCPServer()
    server.bridge = mock_bridge
    return server


@pytest.fixture
def sample_protein_data():
    """Sample protein data for testing."""
    return {
        "accession": "P12345",
        "id": "TEST_HUMAN",
        "protein": {
            "recommendedName": {
                "fullName": {"value": "Test protein"}
            }
        },
        "gene": [{"name": {"value": "TEST"}}],
        "organism": {
            "names": [{"value": "Homo sapiens"}],
            "lineage": ["Eukaryota", "Metazoa", "Chordata", "Mammalia", "Primates", "Hominidae", "Homo"]
        }
    }


@pytest.fixture
def sample_search_results():
    """Sample protein search results for testing."""
    return {
        "results": [
            {
                "accession": "P01308",
                "id": "INS_HUMAN",
                "protein": {
                    "recommendedName": {
                        "fullName": {"value": "Insulin"}
                    }
                },
                "organism": {"names": [{"value": "Homo sapiens"}]}
            },
            {
                "accession": "P01315", 
                "id": "INS_MOUSE",
                "protein": {
                    "recommendedName": {
                        "fullName": {"value": "Insulin"}
                    }
                },
                "organism": {"names": [{"value": "Mus musculus"}]}
            }
        ]
    }


@pytest.fixture
def sample_taxonomy_data():
    """Sample taxonomy data for testing."""
    return {
        "taxonomyId": 9606,
        "mnemonic": "HUMAN",
        "scientificName": "Homo sapiens",
        "commonName": "Human",
        "synonyms": [],
        "lineage": [
            {"taxonomyId": 131567, "scientificName": "cellular organisms"},
            {"taxonomyId": 2759, "scientificName": "Eukaryota"},
            {"taxonomyId": 33154, "scientificName": "Opisthokonta"},
            {"taxonomyId": 33208, "scientificName": "Metazoa"}
        ]
    }


@pytest.fixture
def sample_features_data():
    """Sample protein features data for testing."""
    return {
        "accession": "P12345",
        "features": [
            {
                "type": "Domain",
                "category": "DOMAINS_AND_SITES", 
                "description": "Test domain",
                "location": {
                    "start": {"value": 10, "modifier": "EXACT"},
                    "end": {"value": 100, "modifier": "EXACT"}
                }
            },
            {
                "type": "Active site",
                "category": "DOMAINS_AND_SITES",
                "description": "Test active site", 
                "location": {
                    "start": {"value": 50, "modifier": "EXACT"},
                    "end": {"value": 50, "modifier": "EXACT"}
                }
            }
        ]
    }


@pytest.fixture
def sample_interactions_data():
    """Sample protein interactions data for testing."""
    return {
        "results": [
            {
                "interactantOne": {
                    "uniProtKBAccession": "P12345",
                    "geneName": "TEST1"
                },
                "interactantTwo": {
                    "uniProtKBAccession": "P67890", 
                    "geneName": "TEST2"
                },
                "numberOfExperiments": 3,
                "interactionAc": "EBI-123456"
            }
        ]
    }


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Markers for different test types
pytest_plugins = []


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests (fast, no external dependencies)"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (may be slow, requires network)"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )