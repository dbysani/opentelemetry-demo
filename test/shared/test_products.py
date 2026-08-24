# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""list_products / get_product."""

import asyncio

from conftest import connection_error, json_response
from responses import PRODUCT, PRODUCTS
from tools import get_product, list_products


def test_list_products_returns_the_catalog(mock_transport):
    """A 2xx body is handed back as parsed JSON, unmodified."""
    mock_transport(json_response(PRODUCTS))

    result = asyncio.run(list_products())

    assert result == PRODUCTS


def test_list_products_calls_the_products_endpoint(mock_transport):
    seen = mock_transport(json_response(PRODUCTS))

    asyncio.run(list_products())

    assert str(seen[0].url) == "http://localhost:8080/api/products"


def test_list_products_returns_an_error_string_when_unreachable(mock_transport):
    """Tools never raise: a transport failure comes back as a string, which is
    what the model sees in place of the result."""
    mock_transport(connection_error("connection refused"))

    result = asyncio.run(list_products())

    assert result == "Error while fetching product list: connection refused"


def test_get_product_returns_the_product(mock_transport):
    mock_transport(json_response(PRODUCT))

    result = asyncio.run(get_product("OLJCESPC7Z"))

    assert result == PRODUCT
    # Price is a Money: whole units plus nanos at 10^-9, never a float.
    assert result["priceUsd"] == {"currencyCode": "USD", "units": 101, "nanos": 960000000}


def test_get_product_puts_the_id_in_the_path(mock_transport):
    seen = mock_transport(json_response(PRODUCT))

    asyncio.run(get_product("OLJCESPC7Z"))

    assert str(seen[0].url) == "http://localhost:8080/api/products/OLJCESPC7Z"


def test_get_product_error_string_names_the_product(mock_transport):
    """get_product is the one tool whose error string interpolates its argument."""
    mock_transport(connection_error("connection refused"))

    result = asyncio.run(get_product("OLJCESPC7Z"))

    assert result == "Error while fetching product OLJCESPC7Z: connection refused"
