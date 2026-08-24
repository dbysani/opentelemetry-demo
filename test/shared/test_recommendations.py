# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""get_recommendations."""

import asyncio

from conftest import connection_error, json_response
from responses import RECOMMENDATIONS
from tools import get_recommendations


def test_get_recommendations_returns_products(mock_transport):
    """Recommendations come back as full product objects, not bare ids."""
    mock_transport(json_response(RECOMMENDATIONS))

    result = asyncio.run(get_recommendations("OLJCESPC7Z"))

    assert result == RECOMMENDATIONS
    assert result[0]["id"] == "L9ECAV7KIM"


def test_get_recommendations_sends_the_id_as_product_ids(mock_transport):
    seen = mock_transport(json_response(RECOMMENDATIONS))

    asyncio.run(get_recommendations("OLJCESPC7Z"))

    assert str(seen[0].url) == "http://localhost:8080/api/recommendations?productIds=OLJCESPC7Z"


def test_get_recommendations_returns_an_error_string_when_unreachable(mock_transport):
    mock_transport(connection_error("connection refused"))

    result = asyncio.run(get_recommendations("OLJCESPC7Z"))

    assert result == "Error fetching recommendations: connection refused"
