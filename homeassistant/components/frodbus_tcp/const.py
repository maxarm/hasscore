"""Constants for the Fronius Modbus TCP integration."""

from homeassistant.const import Platform

DOMAIN = "frodbus_tcp"

PYFRODBUS_COORDINATOR = "coordinator"
PYFRODBUS_OBJECT = "pyfrodbus"
PYFRODBUS_REMOVE_LISTENER = "remove_listener"
PYFRODBUS_DEVICE_INFO = "device_info"
PYFRODBUS_SENSORS = "sensors"

PLATFORMS = [Platform.SENSOR]

DEFAULT_SCAN_INTERVAL = 5
DEFAULT_PORT = 502
