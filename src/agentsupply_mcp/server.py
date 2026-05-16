"""
agentsupply-mcp — MCP server for AI agent shopping.

Connect your AI agent to agentsupply.top: search, compare, order,
and set up auto-refills — all through natural language.
"""

import json
import httpx
import sys
from typing import Optional

API_BASE = "https://agentsupply.top"


def _get(agent_id: str, path: str, params: dict = None) -> dict:
    """Make a GET request to the Agent Commerce API."""
    headers = {"X-Agent-ID": agent_id, "User-Agent": "agentsupply-mcp/0.1"}
    with httpx.Client(base_url=API_BASE, headers=headers, timeout=15) as client:
        resp = client.get(path, params=params)
        resp.raise_for_status()
        return resp.json()


def _post(agent_id: str, path: str, data: dict = None) -> dict:
    """Make a POST request to the Agent Commerce API."""
    headers = {
        "X-Agent-ID": agent_id,
        "User-Agent": "agentsupply-mcp/0.1",
        "Content-Type": "application/json",
    }
    with httpx.Client(base_url=API_BASE, headers=headers, timeout=15) as client:
        resp = client.post(path, json=data)
        resp.raise_for_status()
        return resp.json()


def _fmt_product(p: dict) -> str:
    """Format a product dict for LLM display."""
    specs = "; ".join(f"{k}={v}" for k, v in p.get("specs", {}).items()) if p.get("specs") else ""
    return (
        f"SKU: {p['sku']}\n"
        f"Name: {p['name']}\n"
        f"Brand: {p['brand']}\n"
        f"Price: {p['price']}\n"
        f"Category: {p['category']} > {p['subcategory']}\n"
        f"Specs: {specs}\n"
        f"Stock: {p.get('stock', 0)} units\n"
        f"Rating: {p.get('avg_rating', 'N/A')}/5\n"
        f"Orders: {p.get('total_orders', 0)}\n"
    )


def create_server():
    """Create and return the MCP server instance."""
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP(
        "Agent Commerce",
        description="AI agent shopping platform — search, compare, order, and auto-refill products.",
    )

    @mcp.tool()
    def search_products(
        query: str = "",
        category: str = "",
        max_price_cents: int = 9999999,
        limit: int = 10,
    ) -> str:
        """
        Search for products by name, description, or category.
        
        Examples:
        - "65W GaN charger dual USB-C"
        - "wireless mouse ergonomic"
        - "electronic accessories"
        
        Use max_price_cents to filter by maximum price in USD cents.
        Use category to narrow results (e.g., "electronics", "home", "sports").
        """
        params = {"q": query, "limit": limit, "max_price": max_price_cents}
        if category:
            params["category"] = category

        try:
            data = _get("agent", "/v1/products/search", params)
        except Exception as e:
            return f"Error searching products: {e}"

        products = data.get("results", [])
        if not products:
            return "No products found. Try a different search term or broader category."

        return f"Found {len(products)} products:\n\n" + "\n---\n".join(
            _fmt_product(p) for p in products
        )

    @mcp.tool()
    def get_product(sku: str) -> str:
        """
        Get detailed information about a specific product by its SKU.
        Use this after search_products to examine a product in detail before ordering.
        """
        try:
            product = _get("agent", f"/v1/products/{sku}")
        except Exception as e:
            return f"Error: {e}"

        if not product or "error" in product:
            return f"Product not found: {sku}"

        return _fmt_product(product) + (
            f"\nDescription: {product.get('description', '')[:500]}"
        )

    @mcp.tool()
    def compare_products(sku1: str, sku2: str) -> str:
        """
        Compare two products by their SKUs side by side.
        Helps an agent decide between options.
        """
        try:
            data = _post("agent", "/v1/products/compare", {"skus": [sku1, sku2]})
        except Exception as e:
            return f"Error comparing products: {e}"

        products = data.get("results", [])
        if not products:
            return "One or both products not found."

        return "Comparison:\n\n" + "\n---\n".join(_fmt_product(p) for p in products)

    @mcp.tool()
    def get_categories() -> str:
        """Get all product categories available on the platform."""
        try:
            data = _get("agent", "/v1/categories")
        except Exception as e:
            return f"Error fetching categories: {e}"

        cats = data.get("categories", [])
        if not cats:
            return "No categories available."

        lines = []
        for c in cats:
            subs = ", ".join(c.get("subcategories", []))
            lines.append(f"- {c['name']}" + (f" ({subs})" if subs else ""))
        return "Categories:\n" + "\n".join(lines)

    @mcp.tool()
    def place_order(
        sku: str,
        quantity: int = 1,
        name: str = "",
        street: str = "",
        city: str = "",
        state: str = "",
        zip_code: str = "",
        country: str = "US",
        phone: str = "",
    ) -> str:
        """
        Place an order for a product.
        
        You need:
        - sku: the product SKU (from search_products or get_product)
        - quantity: how many to order
        - Shipping address: name, street, city, state, zip_code, country
        
        The agent should confirm the order details with the user before placing.
        """
        items = [{"sku": sku, "qty": quantity}]
        address = {
            "name": name, "street": street, "city": city,
            "state": state, "zip": zip_code, "country": country, "phone": phone,
        }

        try:
            result = _post("agent", "/v1/orders", {
                "items": items,
                "shipping_address": address,
                "agent_id": "agentsupply-mcp",
            })
        except Exception as e:
            return f"Error placing order: {e}"

        if result.get("success"):
            items_summary = "; ".join(
                f"{i['qty']}x {i.get('name', i['sku'])} (${i['price_cents']/100:.2f} each)"
                for i in result.get("items", [])
            )
            return (
                f"Order placed successfully.\n"
                f"Order ID: {result['order_id']}\n"
                f"Items: {items_summary}\n"
                f"Total: {result['total']}\n"
                f"\nYou can check the status with: track_order(order_id='{result['order_id']}')"
            )
        else:
            return f"Order failed: {result.get('error', 'Unknown error')}"

    @mcp.tool()
    def track_order(order_id: str) -> str:
        """Track the status of a previously placed order by its Order ID."""
        try:
            result = _get("agent", f"/v1/orders/{order_id}")
        except Exception as e:
            return f"Error: {e}"

        if not result or "error" in result:
            return f"Order not found: {order_id}"

        items_str = "; ".join(
            f"{i.get('qty', 1)}x {i.get('sku', '?')}"
            for i in result.get("items", [])
        )
        return (
            f"Order: {result['order_id']}\n"
            f"Status: {result['status']}\n"
            f"Items: {items_str}\n"
            f"Total: {result['total']}\n"
            f"Tracking: {result.get('tracking_number', 'N/A')} ({result.get('carrier', 'N/A')})\n"
            f"Created: {result.get('created_at', 'N/A')[:10]}"
        )

    return mcp


def main():
    """Entry point: run the MCP server on stdio."""
    mcp = create_server()
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
