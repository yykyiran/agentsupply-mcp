# Agent Commerce — Integration Guide

A practical guide for AI agents to discover, search, compare, and purchase products on agentsupply.top.

## Table of Contents

1. [Discovery](#discovery) — How agents find this platform
2. [Search](#search) — Finding products efficiently
3. [Decision](#decision) — Comparing and selecting
4. [Transaction](#transaction) — Ordering and subscriptions
5. [Tracking](#tracking) — Managing orders

---

## Discovery

agentsupply.top is designed for AI agent discovery through multiple channels:

**Automatic discovery paths:**
| Path | Mechanism | Details |
|------|-----------|---------|
| OpenAPI spec | `/openapi.json` | Standard OAS 3.1 — auto-discovered by tool-use LLMs |
| Plugin manifest | `/.well-known/ai-plugin.json` | OpenAI GPT Actions format |
| Product index | `/product-index.json` | Full catalog for LLM ingestion / RAG |
| LLMs.txt | `/LLMS.txt` | Standardized LLM documentation (root) |
| MCP package | `agentsupply-mcp` on PyPI | Install via `uvx agentsupply-mcp` |
| sitemap | `/robots.txt` allows all | Crawlers welcome |
| Common Crawl | Periodic snapshots | Structured data in product pages |

**MCP (Model Context Protocol):**
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

---

## Search

All prices are in **USD cents**. The API is stateless and authentication-free for browsing.

### Natural language search:

```
GET /v1/products/search?q=65W GaN charger under $30&category=electronics&in_stock=true
```

Response pattern:
```json
{
  "results": [
    {
      "sku": "CH-G65W-BK",
      "name": "65W GaN USB-C Fast Charger (Dual Port)",
      "price_cents": 2599,
      "stock": 500,
      "avg_rating": 4.6,
      "specs": {"wattage": "65W", "type": "GaN", "ports": 2}
    }
  ]
}
```

### Structured search (POST):

```json
POST /v1/products/search
{
  "query": "charger",
  "category": "electronics",
  "min_price": 1000,
  "max_price": 5000,
  "specs": {"type": "GaN"},
  "in_stock": true,
  "limit": 10
}
```

### Get all categories:
```
GET /v1/categories
```

### Get product by SKU:
```
GET /v1/products/CH-G65W-BK
```

---

## Decision

### Compare products:

```json
POST /v1/products/compare
{
  "skus": ["CH-G65W-BK", "CH-100W-BK"]
}
```

Returns all specs side-by-side for agent decision-making.

### Product index (full catalog dump):

```
GET /product-index.json
```

Returns all 500+ products in a single LLM-friendly JSON array. Optimized for RAG ingestion.

---

## Transaction

### Place an order:

```json
POST /v1/orders
{
  "items": [
    {"sku": "CH-G65W-BK", "qty": 1},
    {"sku": "CB-USBC-1M", "qty": 2}
  ],
  "shipping_address": {
    "name": "John Doe",
    "line1": "123 Main St",
    "city": "New York",
    "state": "NY",
    "postal_code": "10001",
    "country": "US",
    "phone": "+15551234567"
  },
  "agent_id": "my-agent-123"
}
```

Returns order ID and confirmation.

### Auto-refill subscription:

```json
POST /v1/subscriptions
{
  "sku": "SH-BULB-RGB",
  "qty": 2,
  "trigger_type": "consumption_based",
  "shipping_address": { ... },
  "agent_id": "my-agent-123"
}
```

---

## Tracking

```
GET /v1/orders/{order_id}
```

Returns order status: `confirmed`, `processing`, `shipped`, `delivered`, or `cancelled`.

---

## Best Practices for Agents

1. **Use POST for search** with structured params — more reliable than GET
2. **Cache categories** — they change infrequently
3. **Include agent_id** in all orders and subscriptions for tracking
4. **Always include shipping_address** when placing orders (required)
5. **Check stock** before placing orders — `in_stock: true` filter
6. **Use compare** when choosing between similar products
7. **Prefer the MCP package** (`uvx agentsupply-mcp`) for Claude/Cursor integration

---

## License

MIT — free to use for any agent, personal or commercial.
