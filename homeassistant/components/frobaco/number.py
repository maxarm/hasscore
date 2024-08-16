"""The Fronius Battery Control numbers that can be adjusted."""

import logging
from typing import TYPE_CHECKING

from homeassistant import config_entries, core
from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
)
from homeassistant.const import PERCENTAGE, EntityCategory
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, PYFRODBUS_DEVICE_INFO, PYFRODBUS_OBJECT
from .pyfrodbus import FroniusModbusTcp

_LOGGER = logging.getLogger(__name__)


NUMBERS: tuple[NumberEntityDescription, ...] = (
    NumberEntityDescription(
        key="battery_max_discharge_percent",
        name="Battery Max Discharge Percent",
        native_unit_of_measurement=PERCENTAGE,
        device_class=NumberDeviceClass.BATTERY,
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=True,
        native_max_value=100,
        native_min_value=-100,
        native_step=1,
    ),
    NumberEntityDescription(
        key="battery_max_charge_percent",
        name="Battery Max Charge Percent",
        native_unit_of_measurement=PERCENTAGE,
        device_class=NumberDeviceClass.BATTERY,
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=True,
        native_max_value=100,
        native_min_value=-100,
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

    async_add_entities(
        FroniusModbusTcpNumber(
            config_entry.unique_id, description, pyfrodbus, device_info
        )
        for description in NUMBERS
    )


class FroniusModbusTcpNumber(NumberEntity):
    """Representation of a number that allows adjusting Fronius sensors via FroniusModbusTcp."""

    def __init__(
        self,
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

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        self._pyfrodbus.write_data(
            parameter=self.entity_description.key, value=int(value)
        )
        self._last_value = value

    @property
    def native_value(self) -> float | None:
        """Return the entity value to represent the entity state."""
        return self._last_value

    @property
    def name(self) -> str:
        """Return the name of the number prefixed with the device name."""
        if self._attr_device_info is None:
            raise Exception  # noqa: TRY002
        name_prefix = f"frobaco-{self._attr_device_info.get("serial_number")}"
        return f"{name_prefix} {super().name}"
