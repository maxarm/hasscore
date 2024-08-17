"""The Fronius Battery Control numbers that can be adjusted."""

import logging
from typing import TYPE_CHECKING

from homeassistant import config_entries, core
from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
)
from homeassistant.const import EntityCategory, UnitOfPower
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    MAX_SELECTABLE_CHARGE_POWER,
    PYFRODBUS_DEVICE_INFO,
    PYFRODBUS_OBJECT,
)
from .pyfrodbus import FroniusModbusTcp

_LOGGER = logging.getLogger(__name__)


NUMBERS: tuple[NumberEntityDescription, ...] = (
    NumberEntityDescription(
        key="battery_max_discharge_power",
        name="Battery Max Discharge Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=NumberDeviceClass.BATTERY,
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=True,
        native_max_value=MAX_SELECTABLE_CHARGE_POWER,
        native_min_value=-MAX_SELECTABLE_CHARGE_POWER,
        native_step=1,
    ),
    NumberEntityDescription(
        key="battery_max_charge_power",
        name="Battery Max Charge Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=NumberDeviceClass.BATTERY,
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=True,
        native_max_value=MAX_SELECTABLE_CHARGE_POWER,
        native_min_value=-MAX_SELECTABLE_CHARGE_POWER,
        native_step=1,
    ),
    NumberEntityDescription(
        key="storage_control_mode",
        name="Storage Control Mode",
        device_class=NumberDeviceClass.BATTERY,
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=True,
        native_max_value=3,
        native_min_value=0,
        native_step=1,
    ),
)


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Config entry setup."""
    fro_data = hass.data[DOMAIN][config_entry.entry_id]

    pyfrodbus = fro_data[PYFRODBUS_OBJECT]
    device_info = fro_data[PYFRODBUS_DEVICE_INFO]

    if TYPE_CHECKING:
        assert config_entry.unique_id

    for desc in NUMBERS:
        if desc.key == "battery_max_charge_power":
            battery_max_charge_power_number = BatteryMaxChargePowerNumber(
                hass,
                config_entry.unique_id,
                desc,
                pyfrodbus,
                device_info,
            )
        if desc.key == "battery_max_discharge_power":
            battery_max_discharge_power_number = BatteryMaxDischargePowerNumber(
                hass,
                config_entry.unique_id,
                desc,
                pyfrodbus,
                device_info,
            )
        if desc.key == "storage_control_mode":
            storage_control_mode = StorageControlModeNumber(
                hass,
                config_entry.unique_id,
                desc,
                pyfrodbus,
                device_info,
            )

    async_add_entities(
        [
            battery_max_charge_power_number,
            battery_max_discharge_power_number,
            storage_control_mode,
        ]
    )


class FroniusModbusTcpNumber(NumberEntity):
    """Representation of a number that allows adjusting Fronius sensors via FroniusModbusTcp."""

    def __init__(
        self,
        hass: core.HomeAssistant,
        config_entry_unique_id: str,
        description: NumberEntityDescription,
        pyfrodbus: FroniusModbusTcp,
        device_info: DeviceInfo,
    ) -> None:
        """Initialize the number."""
        super().__init__()

        self.entity_description = description
        self._attr_available = True
        self._attr_device_info = device_info
        self._attr_unique_id = f"{config_entry_unique_id}-{description.key}"
        self._pyfrodbus = pyfrodbus
        self._last_value: float | None = 0
        self._hass = hass

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        self._last_value = value

    def get_battery_charge_rate(self) -> float:
        """Get the current battery charge rate value."""
        battery_charge_rate_sensor_name = (
            f"sensor.{self.get_name("battery_charge_rate")}"
        )

        battery_charge_rate_state = self._hass.states.get(
            battery_charge_rate_sensor_name
        )
        if battery_charge_rate_state is not None:
            battery_charge_rate = battery_charge_rate_state.state
        else:
            _LOGGER.error("No state found for %s", battery_charge_rate_sensor_name)
            raise Exception("No state found for battery_charge_rate")  # noqa: TRY002
        return int(battery_charge_rate)

    @property
    def native_value(self) -> float | None:
        """Return the entity value to represent the entity state."""
        return self._last_value

    @property
    def name(self) -> str:
        """Return the name of the number prefixed with the device name."""
        if self._attr_device_info is None:
            raise Exception  # noqa: TRY002
        return self.get_name(super().name)

    def get_name(self, number_name):  # noqa: D102
        name_prefix = f"frobaco_{self._attr_device_info.get("serial_number")}"
        return f"{name_prefix}_{number_name}"


class BatteryMaxChargePowerNumber(FroniusModbusTcpNumber):
    """Representation of a number that allows adjusting BatteryMaxChargePercent."""

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        await super().async_set_native_value(value)

        try:
            battery_charge_rate = self.get_battery_charge_rate()
        except Exception:  # noqa: BLE001
            return

        percent_value = value / float(battery_charge_rate) * 100
        self._pyfrodbus.write_data(
            parameter="battery_max_charge_percent", value=int(percent_value)
        )


class BatteryMaxDischargePowerNumber(FroniusModbusTcpNumber):
    """Representation of a number that allows adjusting BatteryMaxDischargePercent."""

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        await super().async_set_native_value(value)

        try:
            battery_charge_rate = self.get_battery_charge_rate()
        except Exception:  # noqa: BLE001
            return

        percent_value = value / float(battery_charge_rate) * 100
        self._pyfrodbus.write_data(
            parameter="battery_max_discharge_percent", value=int(percent_value)
        )


class StorageControlModeNumber(FroniusModbusTcpNumber):
    """Representation of a number that allows adjusting StorageControlModeNumber."""

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        await super().async_set_native_value(value)
        self._pyfrodbus.write_data(parameter="storage_control_mode", value=int(value))
