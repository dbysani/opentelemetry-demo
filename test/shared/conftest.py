# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Shared fixtures for the src/shared/tools.py unit tests.

Unlike test/telemetry, which asserts against a running demo, these tests never
touch the network: httpx is mocked at the transport layer, so the whole suite
passes with the stack down.

Everything above the transport is the real thing - httpx builds the request,
applies params, and parses the response body - so the tests exercise the same
code path the MCP tools run in production.
"""

import os
import sys
from pathlib import Path

import httpx
import pytest

# The tools are deployed by copying src/shared/tools.py next to the importing
# code (src/mcp/Dockerfile and src/agent/Dockerfile both do this), so they are
# imported as a top-level `tools` module rather than a package. Mirror that here.
SHARED_SRC = Path(__file__).resolve().parents[2] / "src" / "shared"
sys.path.insert(0, str(SHARED_SRC))

# tools.py reads APPLICATION_ENDPOINT into a module-level BASE_URL at import
# time, so this must be set before any test module imports it. pytest loads
# conftest.py first, which makes this the only reliable place to pin it.
BASE_URL = "localhost:8080"
os.environ["APPLICATION_ENDPOINT"] = BASE_URL


def json_response(payload, status_code=200):
    """Transport handler returning `payload` as JSON for any request."""

    def handler(request):
        return httpx.Response(status_code, json=payload)

    return handler


def connection_error(message):
    """Transport handler that fails to connect.

    Raising here is what drives every tool into its `except Exception` branch,
    and httpx.ConnectError stringifies to exactly `message`, which keeps the
    resulting error string assertable without matching on httpx internals.
    """

    def handler(request):
        raise httpx.ConnectError(message)

    return handler


@pytest.fixture
def mock_transport(monkeypatch):
    """Install a fake httpx transport and return the list of requests it sees.

    The tools construct their own `httpx.AsyncClient` internally with no seam to
    inject into, so patch the class to always carry a MockTransport.
    """

    def install(handler):
        requests_seen = []

        def recording_handler(request):
            requests_seen.append(request)
            return handler(request)

        real_async_client = httpx.AsyncClient

        def factory(*args, **kwargs):
            kwargs["transport"] = httpx.MockTransport(recording_handler)
            return real_async_client(*args, **kwargs)

        monkeypatch.setattr(httpx, "AsyncClient", factory)
        return requests_seen

    return install
