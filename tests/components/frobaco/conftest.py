"""Test fixtures for brother."""

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest

from homeassistant.components.frobaco.const import DOMAIN
from homeassistant.components.frobaco.pyfrodbus import FroniusModbusClient
from homeassistant.const import CONF_HOST, CONF_PORT

from tests.common import MockConfigEntry


class MockFroniusModbusClient(FroniusModbusClient):
    """Mock FroniusModbusClient type."""

    # pylint: disable=super-init-not-called
    def __init__(self, host: str, port: int) -> None:
        """Initialize the MockFroniusModbusTCP type."""
        return

    def read_uint16(self, addr):  # noqa: D102
        if addr == 40357:  # battery_max_charge_percent
            return 10000
        return 0

    def write_uint16(self, addr, value):  # noqa: D102
        return


@pytest.fixture
def mock_setup_entry() -> Generator[AsyncMock]:
    """Override async_setup_entry."""
    with patch(
        "homeassistant.components.frobaco.async_setup_entry", return_value=True
    ) as mock_setup_entry:
        yield mock_setup_entry


@pytest.fixture
def mock_unload_entry() -> Generator[AsyncMock]:
    """Override async_unload_entry."""
    with patch(
        "homeassistant.components.frobaco.async_unload_entry", return_value=True
    ) as mock_unload_entry:
        yield mock_unload_entry


@pytest.fixture
def mock_modbus_client() -> Generator[MockFroniusModbusClient]:  # noqa: D103
    with patch(
        "homeassistant.components.frobaco.pyfrodbus.get_modbus_client",
        return_value=MockFroniusModbusClient("hosty", 123),
    ) as mock_modbus_client:
        yield mock_modbus_client


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Mock a config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        entry_id="f1e2b9837e8adaed6fa682acaa216fd9",
        unique_id="0123456789",
        data={CONF_HOST: "localhost", CONF_PORT: 1234},
    )
