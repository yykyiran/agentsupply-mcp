# agentsupply-mcp

**MCP server for AI agent shopping.** Connect your AI agent to agentsupply.top — search, compare, order, and set up auto-refills through natural language.

📖 **[Agent Integration Guide](INTEGRATION.md)** — Full API reference for autonomous agents
🤖 **LLMs.txt** — [/LLMS.txt](LLMS.txt) — LLM-friendly discovery file

```json
// Claude Desktop → MCP 配置
{
  "mcpServers": {
    "agentsupply": {
      "command": "uvx",
      "args": ["agentsupply-mcp"]
    }
  }
}
```

## What is this?

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server that gives AI agents access to a curated product catalog. Your agent can:

- **Search** products by name, category, price
- **Get details** on specific products (specs, stock, ratings)
- **Compare** products side by side
- **Place orders** with shipping address
- **Track orders** and check delivery status
- **Auto-refill** subscriptions (coming soon)

## Installation

```bash
# via pip
pip install agentsupply-mcp

# or via uv (recommended for Claude Desktop)
uvx agentsupply-mcp
```

## Usage

### With Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "agentsupply": {
      "command": "uvx",
      "args": ["agentsupply-mcp"]
    }
  }
}
```

### With any MCP client

```bash
# Run the server on stdio
agentsupply-mcp

# Or with Python directly
python -m agentsupply_mcp.server
```

### With Cursor / VS Code

Configure the MCP server in your editor's MCP settings using the same command.

## Example prompts

Once connected, your agent can handle prompts like:

- *"Find a 65W GaN charger under $30"*
- *"Compare the 65W and 100W GaN chargers"*
- *"Order the 65W charger, shipping to 123 Main St, New York"*
- *"What's the status of my order?"*

## Tools available

| Tool | Description |
|------|-------------|
| `search_products` | Search by name, category, max price |
| `get_product` | Full details for one SKU |
| `compare_products` | Side-by-side comparison |
| `get_categories` | Browse all categories |
| `place_order` | Place an order with shipping address |
| `track_order` | Check order status |

## About

agentsupply.top is an AI-native e-commerce platform. This MCP server gives agents direct API access — no web scraping, no CAPTCHAs, no marketing fluff. Just clean structured data for agent decision-making.

## License

MIT
