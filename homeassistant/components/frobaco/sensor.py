"""Fronius Battery Control Sensors."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from . import pyfrodbus
from .const import (
    DOMAIN,
    PYFRODBUS_COORDINATOR,
    PYFRODBUS_DEVICE_INFO,
    PYFRODBUS_SENSORS,
)

SENSOR_ENTITIES: dict[str, SensorEntityDescription] = {
    "storage_control_mode": SensorEntityDescription(
        key="storage_control_mode",
        name="Storage Control Mode",
    ),
    "battery_charge_rate": SensorEntityDescription(
        key="battery_charge_rate",
        name="Battery Charge Rate",
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
    ),
    "battery_max_discharge_percent": SensorEntityDescription(
        key="battery_max_discharge_percent",
        name="Battery Max Discharge Percent",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.BATTERY,
    ),
    "battery_max_charge_percent": SensorEntityDescription(
        key="battery_max_charge_percent",
        name="Battery Max Charge Percent",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.BATTERY,
    ),
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SMA sensors."""
    fro_data = hass.data[DOMAIN][config_entry.entry_id]

    coordinator = fro_data[PYFRODBUS_COORDINATOR]
    device_info = fro_data[PYFRODBUS_DEVICE_INFO]
    available_sensors = fro_data[PYFRODBUS_SENSORS]

    if TYPE_CHECKING:
        assert config_entry.unique_id

    async_add_entities(
        FroniusModbusTcpSensor(
            coordinator,
            config_entry.unique_id,
            SENSOR_ENTITIES.get(sensor.name),
            sensor,
            device_info,
        )
        for sensor in available_sensors
    )


class FroniusModbusTcpSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Fronius Battery Control sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        config_entry_unique_id: str,
        sensor_entity_description: SensorEntityDescription | None,
        sensor: pyfrodbus.Sensor,
        device_info: DeviceInfo,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        if sensor_entity_description is None:
            raise Exception  # noqa: TRY002
        self.entity_description = sensor_entity_description
        self._sensor = sensor
        self._attr_device_info = device_info
        self._attr_unique_id = (
            f"{config_entry_unique_id}-{sensor_entity_description.key}"
        )

    @property
    def name(self) -> str:
        """Return the name of the sensor prefixed with the device name."""

        if self._attr_device_info is None:
            raise Exception  # noqa: TRY002

        name_prefix = f"frobaco-{self._attr_device_info.get("serial_number")}"

        return f"{name_prefix} {super().name}"

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self._sensor.state

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()
        # self._sensor.enabled = True

    async def async_will_remove_from_hass(self) -> None:
        """Run when entity will be removed from hass."""
        await super().async_will_remove_from_hass()
        # self._sensor.enabled = False
