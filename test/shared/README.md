<!-- Copyright The OpenTelemetry Authors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Shared tool tests

Unit tests for `src/shared/tools.py`, the functions the MCP server registers as
tools and the agent falls back to when `MCP_ENABLED=False`.

These are unit tests, not telemetry tests: httpx is mocked at the transport
layer, so the suite runs in well under a second **with the demo stopped**. It is
the counterpart to `test/telemetry`, which asserts against a running stack.

## Running

```sh
python3 -m venv .venv && . .venv/bin/activate
pip install --require-hashes -r test/shared/requirements.txt
python -m pytest test/shared
```

## Updating dependencies

Same pip-compile workflow as `test/telemetry`: edit `requirements.in`, then

```sh
pip-compile --allow-unsafe --generate-hashes --no-emit-index-url \
  --output-file=test/shared/requirements.txt --strip-extras test/shared/requirements.in
```

## What is covered

`list_products`, `get_product`, `get_ads`, `get_recommendations` and
`get_supported_currencies`. The cart, checkout and shipping tools are not
covered yet.

Each tool has two tests that matter:

* **the success path** - the parsed JSON is returned unmodified
* **the error path** - the tool returns an *error string* rather than raising

The error-string convention is the important one. Every tool wraps its request
in `try/except Exception` and returns `f"<prefix>: {e}"`, so a caller never sees
an exception - the model just receives a string where it expected data. The
prefixes differ per tool (`Error fetching ads` vs `Error while fetching product
list`), so each is asserted exactly.

Non-2xx responses reach the same branch via `raise_for_status()`. The tests
trigger it with a connection failure instead, because `httpx.ConnectError`
stringifies to exactly the message it was given, which keeps the assertions on
the tools' own wording rather than on httpx's HTTP error text.

## Fixtures

`responses.py` holds real payloads captured with curl against a running stack -
see the docstring there for the exact commands. Do not invent shapes by hand:
re-capture if the API changes.
