# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""get_supported_currencies."""

import asyncio

from conftest import connection_error, json_response
from responses import CURRENCIES
from tools import get_supported_currencies


def test_get_supported_currencies_returns_the_codes(mock_transport):
    """The endpoint returns a flat list of ISO 4217 strings, not objects."""
    mock_transport(json_response(CURRENCIES))

    result = asyncio.run(get_supported_currencies())

    assert result == CURRENCIES
    assert result[0] == "ZAR"


def test_get_supported_currencies_calls_the_currency_endpoint(mock_transport):
    seen = mock_transport(json_response(CURRENCIES))

    asyncio.run(get_supported_currencies())

    assert str(seen[0].url) == "http://localhost:8080/api/currency"


def test_get_supported_currencies_returns_an_error_string_when_unreachable(mock_transport):
    mock_transport(connection_error("connection refused"))

    result = asyncio.run(get_supported_currencies())

    assert result == "Error while fetching currency list: connection refused"
