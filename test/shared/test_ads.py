# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""get_ads."""

import asyncio

from conftest import connection_error, json_response
from responses import ADS
from tools import get_ads


def test_get_ads_returns_the_ads(mock_transport):
    mock_transport(json_response(ADS))

    result = asyncio.run(get_ads("telescopes"))

    assert result == ADS
    assert result[0]["redirectUrl"] == "/product/66VCHSJNUP"


def test_get_ads_sends_the_category_as_context_keys(mock_transport):
    """The category argument is passed as the contextKeys query parameter."""
    seen = mock_transport(json_response(ADS))

    asyncio.run(get_ads("telescopes"))

    assert str(seen[0].url) == "http://localhost:8080/api/data?contextKeys=telescopes"


def test_get_ads_returns_an_error_string_when_unreachable(mock_transport):
    """Note the wording differs from the product tools - each tool spells its
    own error prefix, so they are pinned individually."""
    mock_transport(connection_error("connection refused"))

    result = asyncio.run(get_ads("telescopes"))

    assert result == "Error fetching ads: connection refused"
