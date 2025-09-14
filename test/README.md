# Test Directory

This directory contains all test files for the Particle Physics Agent project.

## Test Files

### Python Tests

#### Core Integration Tests
- **`test_simplified_integration.py`** - Tests the simplified agent search integration using only ParticlePhysics MCP
- **`demo_simplified_integration.py`** - Demo showing the simplified integration in action
- **`test_experimental_integration.py`** - Tests for experimental MCP integration features
- **`test_experimental_mcp_integration.py`** - Comprehensive MCP integration testing

#### MCP Server Tests  
- **`test_simple_experimental.py`** - Basic experimental MCP server functionality test
- **`test_mcp_compile.py`** - Tests MCP compilation and server communication

#### Metrics and Error Handling Tests
- **`test_tool_metrics.py`** - Tests for tool usage metrics and performance monitoring
- **`quick_test_metrics.py`** - Quick metrics validation tests
- **`test_structured_errors.py`** - Tests for structured error handling

### HTML Test Clients

#### MCP Integration Tests
- **`test-mcp-integration.html`** - HTML client for testing MCP integration
- **`mcp_compile_client.html`** - Web client for MCP compilation testing

#### SSE and Real-time Tests
- **`sse_client_test.html`** - Server-Sent Events client testing

## Running Tests

### Individual Tests
```bash
# Run from project root
cd /path/to/Particle-Physics-Agent-test

# Core integration test
python test/test_simplified_integration.py

# Demo the integration
python test/demo_simplified_integration.py

# Test MCP functionality
python test/test_simple_experimental.py
```

### All Tests
```bash
# Run all Python tests
find test/ -name "test_*.py" -exec python {} \;

# Run all Python files (including demos)
find test/ -name "*.py" -exec python {} \;
```

## Test Categories

1. **Integration Tests** - Test how different components work together
2. **MCP Tests** - Test Model Context Protocol functionality
3. **Performance Tests** - Test metrics and performance monitoring
4. **Client Tests** - HTML/JavaScript clients for web-based testing
5. **Demo Tests** - Demonstration files showing functionality

## Key Features Tested

- ✅ ParticlePhysics MCP integration (single source of truth)
- ✅ Agent search functionality  
- ✅ Particle validation and information retrieval
- ✅ Diagram generation support
- ✅ Error handling and structured responses
- ✅ Performance metrics and monitoring
- ✅ Web client integration
- ✅ Server-Sent Events functionality

## Dependencies

Most tests require:
- `asyncio` for async functionality
- `logging` for test output
- Access to experimental MCP server
- Internet connection for MCP communication

## Notes

- Tests are designed to be run from the project root directory
- Some tests may show PDG import warnings but still function correctly
- HTML test files can be opened in a browser for manual testing
- All tests use the experimental ParticlePhysics MCP as the single source of truth
