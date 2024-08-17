"""Test init of Frobaco integration."""

from unittest.mock import MagicMock, patch

from homeassistant.components.frobaco.const import (
    DOMAIN,
    PYFRODBUS_DEVICE_INFO,
    PYFRODBUS_OBJECT,
    PYFRODBUS_SENSORS,
)
from homeassistant.components.frobaco.pyfrodbus import FroniusModbusTcp
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant

from . import init_integration
from .conftest import MockFroniusModbusClient

from tests.common import MockConfigEntry


async def test_async_setup_entry_basics(
    hass: HomeAssistant,
    mock_modbus_client: MockFroniusModbusClient,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test a successful setup entry."""
    await init_integration(hass, mock_config_entry)

    assert mock_config_entry.state is ConfigEntryState.LOADED

    hass_data = hass.data[DOMAIN][mock_config_entry.entry_id]

    assert len(hass_data[PYFRODBUS_SENSORS]) == 4
    assert isinstance(hass_data[PYFRODBUS_OBJECT], FroniusModbusTcp)
    assert hass_data[PYFRODBUS_DEVICE_INFO]["manufacturer"] == "Fronius"
    assert hass_data[PYFRODBUS_DEVICE_INFO]["serial_number"] == "9137319fro"


async def test_async_setup_entry_sensor_states(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test that sensors are created as expected after init."""

    def assert_state(hass: HomeAssistant, sensor, expected_value):
        sensor = hass.states.get(sensor)
        assert sensor
        assert int(float(sensor.state)) == expected_value

    def read_uint16_side_effect(*args, **kwargs):
        if args[0] == 40357:  # charge
            return 9900
        if args[0] == 40356:  # discharge
            return 9800
        if args[0] == 40346:  # charge_rate
            return 123
        if args[0] == 40349:  # control_mode
            return 7
        return 0

    client_mock = MagicMock()
    # client_mock.read_uint16.return_value = 9900
    client_mock.read_uint16.side_effect = read_uint16_side_effect

    with patch(
        "homeassistant.components.frobaco.pyfrodbus.get_modbus_client",
        return_value=client_mock,
    ):
        await init_integration(hass, mock_config_entry)
        assert_state(hass, "sensor.frobaco_9137319fro_battery_max_charge_percent", 99)
        assert_state(
            hass, "sensor.frobaco_9137319fro_battery_max_discharge_percent", 98
        )
        assert_state(hass, "sensor.frobaco_9137319fro_battery_charge_rate", 123)
        assert_state(hass, "sensor.frobaco_9137319fro_storage_control_mode", 7)
