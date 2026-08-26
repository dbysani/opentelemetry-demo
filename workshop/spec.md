# Spec: `find_products_under_budget(max_budget_usd)`

**Location:** `src/shared/tools.py`
**Status:** authoritative acceptance criteria

## Purpose

Given a shopper's budget in US dollars, return every Astronomy Shop product they can afford —
so that the shopper only sees products whose actual catalog price is less than or equal to
their budget.

## Inputs

| Parameter | Type | Constraints |
|---|---|---|
| `max_budget_usd` | number | US dollars. Must be greater than 0. |

No other parameters. This function is registered as an MCP tool, so every parameter appears in
the schema the model sees — a parameter the model can see is one it can hallucinate a value for.

## Behaviour

| Case | Required behaviour |
|---|---|
| Positive budget | Return all qualifying products |
| Price equals budget exactly | **INCLUDED.** The comparison is `price <= budget`, not `<` |
| Currency | USD only. Skip any item not priced in USD. |
| Money representation | `units + nanos / 1_000_000_000`, computed with exact arithmetic (`Decimal` or integer cents). Never float. |
| Ordering | Cheapest to most expensive |
| Response fields | `id`, `name`, `price` only — **no `description`** |
| Nothing affordable | Empty list |
| Budget zero or negative | Validation error, returned before any network call |
| Budget non-numeric | Validation error |
| Product retrieval fails | Return an error. **Never an empty list, never a fabricated price.** |
| Where arithmetic happens | In this function. The model must not recompute or re-filter the result. |

## Upstream contract

`list_products()` returns a list on success and an **error string** on failure — it does not
raise. Any implementation must check the type of the result before iterating it. Iterating an
error string yields characters, not products.

Returning an empty list on upstream failure is the dangerous default: the agent reports it to
the customer as "you can't afford anything," which is a wrong answer delivered with total
confidence and no error anywhere in the trace.

## Return shape

```python
[
    {"id": "HQTGWGPNH4", "name": "The Comet Book",   "price_usd": "0.99"},
    {"id": "L9ECAV7KIM", "name": "Lens Cleaning Kit", "price_usd": "21.95"},
]
```

On failure, a string beginning with `Error`.

## Worked expectations

| Budget | Result |
|---|---|
| `$0.50` | `[]` |
| `$1.00` | The Comet Book |
| `$21.94` | The Comet Book |
| `$21.95` | The Comet Book, Lens Cleaning Kit |
| `$70.00` | The Comet Book, Lens Cleaning Kit, Red Flashlight, Solar Filter |
| `$0` | Validation error |
| `-$5` | Validation error |

## Out of scope

- Currency conversion — USD only
- Stock levels, shipping, tax
- Recommendations or upsell
- Any change to protobufs, the Product Catalog service, the database, or the frontend

## Open questions

- Should a budget above the most expensive item warn, or just return everything?
  **Assumed:** return everything.
- Should the response include a count or other metadata? **Assumed:** no — the caller can count.

## Constraints on the implementation

- No new dependency unless justified. `Decimal` is standard library.
- No new database query — reuse the existing `/api/products` call
- Smallest reviewable diff; one file
