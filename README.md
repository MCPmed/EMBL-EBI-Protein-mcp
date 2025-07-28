# EMBL-EBI Protein MCP Server

> ⚠️ **UNDER CONSTRUCTION** ⚠️
>
> This project is currently under active development. While the core functionality is operational, please be aware that:
> - **No guarantee is provided** that the software is bug-free
> - Breaking changes may occur without notice
> - Some features may be incomplete or experimental
> - Use at your own risk in production environments
>
> Feedback and contributions are welcome as we work to improve the server!

A Model Context Protocol (MCP) server providing access to the EMBL-EBI Protein database. This server enables LLMs and other MCP clients to search, retrieve, and analyze protein data from UniProt and related databases.

## Quick Start

### Installation

**Requirements**: Python 3.10+ (due to MCP library requirements)

```bash
# Create virtual environment with Python 3.10+
python3.11 -m venv venv  
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .
```

### Running the MCP Server

```bash
# Start the MCP server
embl_ebi_protein_mcp
```

The server runs on stdio and is ready to accept MCP protocol requests.

## Features

### New Enhanced Tools (Recommended)
- **`get_protein_summary`** - One-stop comprehensive protein lookup (BEST STARTING POINT)
- **`find_protein_accession`** - Easy protein ID lookup for common names

### Core Protein Tools
- **`search_proteins`** - Search UniProt protein database by text query
- **`get_protein_by_accession`** - Get detailed protein information by UniProt accession
- **`get_protein_interactions`** - Get known protein-protein interactions
- **`get_protein_isoforms`** - Get alternative protein isoforms (splice variants)

### Protein Features & Analysis
- **`search_features`** - Search for specific protein sequence features
- **`get_features_by_accession`** - Get all sequence features for a protein
- **`get_features_by_type`** - Get features by specific type (domains, sites, etc.)
- **`search_variations`** - Search natural variants in proteins
- **`get_variations_by_accession`** - Get variations by UniProt accession

### Taxonomy & Classification
- **`get_taxonomy_by_id`** - Get taxonomic information by NCBI taxonomy ID
- **`get_taxonomy_lineage`** - Get complete taxonomic lineage
- **`get_taxonomy_children`** - Get taxonomy children by ID

### Advanced Analysis
- **`search_proteomes`** - Search proteomes
- **`get_proteome_by_upid`** - Get proteome by UniProt Proteome ID
- **`search_coordinates`** - Search genomic coordinates
- **`search_uniparc`** - Search UniParc entries

**Total: 30 tools available**

## Usage Examples

### For LLMs (via MCP client)

```javascript
// Find human p53 protein - comprehensive overview
{
  "method": "tools/call",
  "params": {
    "name": "get_protein_summary",
    "arguments": {
      "gene_name": "p53",
      "organism": "human"
    }
  }
}

// Find insulin in mouse
{
  "method": "tools/call", 
  "params": {
    "name": "find_protein_accession",
    "arguments": {
      "gene_name": "insulin",
      "organism": "mouse"
    }
  }
}
```

### Python API Usage

```python
import asyncio
from embl_ebi_protein_mcp.bridge import EMBLEBIBridge

async def example():
    async with EMBLEBIBridge() as bridge:
        # Find protein accession
        result = await bridge.find_protein_accession("p53", "human")
        print(f"Found: {result[0]['accession']}")
        
        # Get comprehensive summary
        summary = await bridge.get_protein_summary("insulin", "human")
        print(f"Insulin accession: {summary['accession']}")

asyncio.run(example())
```

## Supported Organisms

The server includes convenient organism name mapping:

| Common Name | Taxonomy ID | Example Usage |
|-------------|-------------|---------------|
| human       | 9606        | `"organism": "human"` |
| mouse       | 10090       | `"organism": "mouse"` |
| rat         | 10116       | `"organism": "rat"` |
| yeast       | 559292      | `"organism": "yeast"` |
| e.coli      | 83333       | `"organism": "e.coli"` |
| drosophila  | 7227        | `"organism": "drosophila"` |

## MCP Client Configuration

### Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "embl-ebi-proteins": {
      "command": "embl_ebi_protein_mcp",
      "env": {}
    }
  }
}
```

### Other MCP Clients

The server follows the standard MCP protocol and should work with any MCP-compatible client.

## Testing

```bash
# Test the API functionality
python test_api.py

# Test enhanced features
python test_enhancements.py

# Run with debug logging
DEBUG=1 embl_ebi_protein_mcp
```

## API Endpoints Used

This server accesses the following EMBL-EBI REST API endpoints:

- **Proteins**: `https://www.ebi.ac.uk/proteins/api/proteins`
- **Features**: `https://www.ebi.ac.uk/proteins/api/features`
- **Variations**: `https://www.ebi.ac.uk/proteins/api/variation`
- **Taxonomy**: `https://www.ebi.ac.uk/proteins/api/taxonomy`
- **Proteomes**: `https://www.ebi.ac.uk/proteins/api/proteomes`
- **Coordinates**: `https://www.ebi.ac.uk/proteins/api/coordinates`
- **UniParc**: `https://www.ebi.ac.uk/proteins/api/uniparc`

## Development

### Project Structure

```
EMBL-EBI-Protein-mcp/
├── embl_ebi_protein_mcp/
│   ├── __init__.py
│   ├── bridge.py          # API bridge to EMBL-EBI
│   ├── mcp_server.py      # MCP server implementation
│   ├── cli.py             # Command-line interface
│   └── main.py            # Main entry point
├── test_api.py            # API functionality tests
├── test_enhancements.py   # Enhanced features tests
├── ENHANCEMENTS.md        # Enhancement documentation
└── pyproject.toml         # Package configuration
```

### Development Setup

```bash
# Install with development dependencies
pip install -e .[dev]

# Run linting
black embl_ebi_protein_mcp/
flake8 embl_ebi_protein_mcp/

# Type checking
mypy embl_ebi_protein_mcp/
```

## Recent Enhancements

- Added `get_protein_summary` for comprehensive protein lookup
- Added `find_protein_accession` for easy ID lookup
- Enhanced all tool descriptions with usage guidance and examples
- Added organism name mapping for better usability
- Improved error handling and fallback strategies
- Added clear workflow guidance for LLMs

See [ENHANCEMENTS.md](ENHANCEMENTS.md) for detailed information.

## Known Limitations

- Some proteins may not have complete data in all endpoints
- Large result sets may be truncated or timeout
- The API requires specific UniProt accession formats for some endpoints
- Rate limiting may apply for high-volume usage

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

- **Issues**: Use the [GitHub issue tracker](https://github.com/MCPmed/EMBL-EBI-Protein-mcp/issues)
- **Questions**: Open a discussion on GitHub
- **API Documentation**: [EMBL-EBI Proteins API](https://www.ebi.ac.uk/proteins/api/)

---

**Note**: This is an unofficial implementation and is not affiliated with EMBL-EBI. All data is accessed through their public REST API.