# EMBL-EBI-Protein-mcp

A Model Context Protocol (MCP) server for EMBL-EBI Protein database access

## Installation

Install the package in development mode:

```bash
pip install -e .
```

Or install from PyPI (when available):

```bash
pip install EMBL-EBI-Protein-mcp
```

## Usage


### Command Line Interface

The package provides a `EMBL-EBI-Protein-mcp` command for usage:

```bash
# Get help
EMBL-EBI-Protein-mcp --help

# Run your main functionality
EMBL-EBI-Protein-mcp <args>
```



### MCP Server

The package provides an MCP server for integration with MCP-compatible clients:

```bash
# Run the MCP server
EMBL-EBI-Protein-mcp-server
```

The MCP server provides the following tools:

- **tool1**: Description of tool1
- **tool2**: Description of tool2
- **tool3**: Description of tool3


### Python API

```python
from embl-ebi-protein-mcp.main import EMBLEBIProteinmcpBridge

# Initialize the bridge
bridge = EMBLEBIProteinmcpBridge()

# Use your functionality
result = bridge.your_method()
```

## Features

- **Feature 1**: Description of feature 1
- **Feature 2**: Description of feature 2
- **Feature 3**: Description of feature 3

- **MCP Integration**: Full Model Context Protocol server implementation


## API Methods

### Core Methods

- `method1()`: Description of method1
- `method2()`: Description of method2
- `method3()`: Description of method3

### Configuration

The package uses a configuration class for settings:

```python
from embl-ebi-protein-mcp.main import EMBLEBIProteinmcpConfig, EMBLEBIProteinmcpBridge

config = EMBLEBIProteinmcpConfig(
    base_url="https://api.example.com",
    api_key="your_api_key",
    timeout=30.0
)

bridge = EMBLEBIProteinmcpBridge(config)
```


## MCP Server Configuration

To use the MCP server with an MCP client, configure it as follows:

```json
{
  "mcpServers": {
    "EMBL-EBI-Protein-mcp": {
      "command": "EMBL-EBI-Protein-mcp-server",
      "env": {}
    }
  }
}
```

The server will automatically handle:
- JSON-RPC communication
- Tool discovery and invocation
- Error handling and reporting


## Development

### Setup Development Environment

```bash
# Install in development mode with dev dependencies
pip install -e .[dev]

# Run tests
pytest

# Format code
black embl-ebi-protein-mcp/

# Type checking
mypy embl-ebi-protein-mcp/
```

### Project Structure

```
EMBL-EBI-Protein-mcp/
├── pyproject.toml      # Package configuration
├── README.md          # This file
├── LICENSE            # MIT License
├── embl-ebi-protein-mcp/         # Main package
│   ├── __init__.py    # Package initialization
│   ├── main.py        # Core functionality

│   └── cli.py         # Command-line interface


│   └── mcp_server.py  # MCP server implementation

└── tests/             # Test files
    ├── __init__.py
    └── test_main.py   # Tests for main functionality
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## Support

For issues and questions, please use the GitHub issue tracker. 