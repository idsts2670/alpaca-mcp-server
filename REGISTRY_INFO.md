# Registry Information for Alpaca MCP Server

This file contains metadata and submission information for various MCP server registries.

## Cursor MCP Directory Submission

**Server Name:** Alpaca MCP Server
**Description:** Comprehensive Alpaca Trading API integration for Model Context Protocol
**Logo URL:** https://alpaca.markets/favicon.ico
**Repository:** https://github.com/idsts2670/alpaca-mcp-server

**Installation Command:**
```bash
uvx alpaca-mcp-server
```

**Configuration Example:**
```json
{
  "mcpServers": {
    "alpaca": {
      "command": "uvx",
      "args": ["alpaca-mcp-server", "serve"],
      "env": {
        "ALPACA_API_KEY": "your_api_key",
        "ALPACA_SECRET_KEY": "your_secret_key"
      }
    }
  }
}
```

**Features (31 Comprehensive Tools):**

**Account & Portfolio (3 tools):**
- Account info with balances and buying power
- Portfolio positions with P&L tracking
- Individual position details and management

**Stock Market Data (6 tools):**
- Real-time quotes with bid/ask spreads
- Historical bars with flexible timeframes (1Min to 1Month)
- Individual trade data and market snapshots
- Latest trade and bar information

**Cryptocurrency (2 tools):**
- Historical crypto price bars and quotes
- Support for BTC/USD, ETH/USD, and other pairs

**Order Management (5 tools):**
- Stock orders: market, limit, stop, stop-limit, trailing-stop
- Crypto orders: market, limit, stop-limit with GTC/IOC
- Order history with advanced filtering
- Cancel individual orders or all orders

**Position Management (3 tools):**
- Close positions (partial or complete by qty/percentage)
- Liquidate entire portfolio
- Exercise option contracts

**Asset Discovery (2 tools):**
- Detailed asset information and trading status
- Browse all available tradable instruments

**Watchlists (3 tools):**
- Create and manage multiple watchlists
- Add/remove symbols for tracking
- Organize investment ideas and research

**Market Info (2 tools):**
- Market clock with trading hours and status
- Market calendar with holidays and sessions

**Corporate Actions (1 tool):**
- Earnings, dividends, stock splits
- Historical and upcoming events

**Options Trading (4 tools):**
- Search contracts with expiration/strike filtering
- Real-time quotes with Greeks (Delta, Gamma, Theta, Vega)
- Comprehensive snapshots with implied volatility
- Single-leg and multi-leg strategies (spreads, straddles)

**Additional Capabilities:**
- Paper trading mode for safe testing
- Live trading with real funds
- Natural language operation through AI assistants

**Setup Instructions:**
1. Install: `uvx alpaca-mcp-server`
2. Configure: `alpaca-mcp init`
3. Add to Cursor MCP configuration
4. Start trading with natural language!

---

## GitHub MCP Registry

**Namespace:** io.github.idsts2670/alpaca-mcp-server
**Manifest URL:** https://github.com/idsts2670/alpaca-mcp-server/.well-known/mcp/manifest.json
**PyPI Package:** alpaca-mcp-server

---

## Docker MCP Registry

**Image Name:** alpaca/mcp-server
**Registry File:** server.yaml
**Transport:** stdio

---

## Claude Connector

**Connection Type:** Remote server (optional)
**Protocol:** MCP over HTTP
**Authentication:** Alpaca API keys

---

## Installation Methods Summary

| Method | Command | Use Case |
|--------|---------|----------|
| uvx | `uvx alpaca-mcp-server` | Quick installation |
| pip | `pip install alpaca-mcp-server` | Python environment |
| Docker | `docker run alpaca/mcp-server` | Containerized deployment |
| Git | `uvx git+https://github.com/idsts2670/alpaca-mcp-server.git` | Development |

## Configuration

All installation methods require Alpaca API credentials:

1. **Initialize configuration:**
   ```bash
   alpaca-mcp init
   ```

2. **Start server:**
   ```bash
   alpaca-mcp serve
   ```

3. **Configure MCP client** with the generated configuration.

## Support

- **Issues:** https://github.com/idsts2670/alpaca-mcp-server/issues
- **Documentation:** https://github.com/idsts2670/alpaca-mcp-server#readme
- **License:** MIT