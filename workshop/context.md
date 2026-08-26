# Context: Astronomy Shop budget feature

## Flow
- PostgreSQL (`src/postgresql/init.sql`, table `catalog.products`) → Product Catalog service
  → Frontend → `GET /api/products` → `src/shared/tools.py` → MCP server → Agent
- Prices are stored as an integer pair — `price_units` + `price_nanos` — never as a float

## Files
- `src/shared/tools.py` — thin async `httpx` wrappers over the shop HTTP API; `list_products`
  and `get_product` are the read paths we need
- `src/mcp/src/mcp_server/astronomy_shop_mcp_server.py` — registers each tool explicitly,
  one line per tool; nothing is auto-discovered
- `src/agent/src/agents/agents.py` — the Agent loads the registered tool set via MCP

## Patterns
- Tools call the HTTP API, never the database directly. `BASE_URL` comes from the
  `APPLICATION_ENDPOINT` env var, defaulting to `localhost:8080`
- **Tools return an error _string_ on failure — they never raise.** So `list_products()`
  returns a list on success and a `str` on failure, and callers must check the type

## Contracts
- Product response carries `id`, `name`, and a money object (`currencyCode`, `units`, `nanos`).
  Tool docstrings are serialised into the schema sent to the model on every request — they are
  contract, not comment

## Risks / open questions
- `units` + `nanos` arithmetic is where plausible generated money code goes subtly wrong;
  float comparison at an inclusive boundary is the specific hazard
- A currency service exists and the frontend converts. This feature is USD-only, which is a
  deliberate assumption rather than a fact about the system

---

*Smallest implementation seam: a new async function in `src/shared/tools.py` that reuses the
existing `/api/products` call. No protobuf regeneration, no Product Catalog change, no new
database query.*
