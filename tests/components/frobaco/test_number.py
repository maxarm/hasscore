"""Tests for our Number types."""

from unittest.mock import MagicMock, patch

from homeassistant.components.number import (
    ATTR_VALUE,
    DOMAIN as NUMBER_DOMAIN,
    SERVICE_SET_VALUE,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant

from . import init_integration

from tests.common import MockConfigEntry


async def test_async_setup_entry_basics(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test that changing the number charge power writes the correct value for the max_charge_percent."""

    def read_uint16_side_effect(*args, **kwargs):
        if args[0] == 40357:  # charge
            return 10000
        if args[0] == 40346:  # charge_rate
            return 20000
        return 0

    client_mock = MagicMock()
    client_mock.read_uint16.side_effect = read_uint16_side_effect
    client_mock.write_uint16 = MagicMock()

    with patch(
        "homeassistant.components.frobaco.pyfrodbus.get_modbus_client",
        return_value=client_mock,
    ):
        await init_integration(hass, mock_config_entry)

        number_entity_name = "number.frobaco_9137319fro_battery_max_charge_power"
        number_entity = hass.states.get(number_entity_name)
        assert number_entity

        test_value = 1000.0
        await hass.services.async_call(
            NUMBER_DOMAIN,
            SERVICE_SET_VALUE,
            {
                ATTR_ENTITY_ID: number_entity_name,
                ATTR_VALUE: test_value,
            },
            blocking=True,
        )

        await hass.async_block_till_done()

        client_mock.write_uint16.assert_called_once_with(40357, 500)
