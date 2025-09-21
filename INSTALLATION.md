# Alpaca MCP Server - Installation Guide

## Quick Start

### 1. Install from GitHub

```bash
# Install the package
uvx --from git+https://github.com/idsts2670/alpaca-mcp-server.git alpaca-mcp

# Or install globally
pip install git+https://github.com/idsts2670/alpaca-mcp-server.git
```

### 2. Configure Your Credentials

After installation, run the setup command:

```bash
alpaca-mcp init
```

This will guide you through:
- Entering your Alpaca API Key
- Entering your Alpaca Secret Key  
- Choosing between paper trading (recommended) or live trading
- Creating a `.env` configuration file

### 3. Start the Server

Once configured, start the MCP server:

```bash
# Start with default stdio transport
alpaca-mcp serve

# Start with HTTP transport (for remote access)
alpaca-mcp serve --transport http --host 0.0.0.0 --port 8000
```

## Available Commands

- `alpaca-mcp` - Show welcome message and setup guidance
- `alpaca-mcp init` - Configure your Alpaca API credentials
- `alpaca-mcp serve` - Start the MCP server
- `alpaca-mcp-serve` - Alternative command to start server
- `alpaca-mcp-init` - Alternative command to configure credentials

## Getting Your Alpaca API Keys

1. Go to [Alpaca Markets](https://app.alpaca.markets/)
2. Sign up for a free account
3. Navigate to your account settings
4. Generate API keys for paper trading (recommended for testing)
5. Copy your API Key and Secret Key

## Paper Trading vs Live Trading

- **Paper Trading (Recommended)**: Uses virtual money, perfect for testing strategies
- **Live Trading**: Uses real money, only use when you're ready to trade

The setup process will automatically configure the correct API endpoints based on your choice.

## Troubleshooting

### Credentials Not Found Error
If you see "Alpaca API credentials not found", run:
```bash
alpaca-mcp init
```

### Permission Errors
Make sure you have write permissions in the directory where you're running the commands.

### Network Issues
For remote access, use HTTP transport:
```bash
alpaca-mcp serve --transport http --host 0.0.0.0 --port 8000
```

## Next Steps

Once your server is running, you can:
1. Connect it to Claude Desktop or other MCP clients
2. Use it for trading analysis and execution
3. Explore the various trading tools and functions available

For more information, see the main [README.md](README.md) file.
