"""The Fronius Modbus TCP integration."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    EVENT_HOMEASSISTANT_STOP,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    PLATFORMS,
    PYFRODBUS_COORDINATOR,
    PYFRODBUS_DEVICE_INFO,
    PYFRODBUS_OBJECT,
    PYFRODBUS_REMOVE_LISTENER,
)
from .pyfrodbus import FroniusModbusTcp

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Fronius Modbus TCP from a config entry."""
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]

    fronius_modbus_tcp = FroniusModbusTcp(host, port)

    fronius_device = await fronius_modbus_tcp.device_info()

    if entry.unique_id is None:
        raise Exception("unique id is None!")  # noqa: TRY002

    device_info = DeviceInfo(
        identifiers={(DOMAIN, str(entry.unique_id))},
        manufacturer="Fronius",
        serial_number=fronius_device["serial"],
    )

    # Define the coordinator
    async def async_update_data():
        """Update the used Fronius Modbus TCP sensors."""
        try:
            await fronius_modbus_tcp.read()
        except Exception as exc:
            raise UpdateFailed(exc) from exc

    interval = timedelta(
        seconds=entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    )

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="frodbus_tcp",
        update_method=async_update_data,
        update_interval=interval,
    )

    try:
        await coordinator.async_config_entry_first_refresh()
    except ConfigEntryNotReady:  # noqa: TRY302
        # await .close_session()
        raise

    # Ensure we logout on shutdown
    async def async_close_session(event):
        """Close the session."""
        # await .close_session()

    remove_stop_listener = hass.bus.async_listen_once(
        EVENT_HOMEASSISTANT_STOP, async_close_session
    )

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        PYFRODBUS_OBJECT: fronius_modbus_tcp,
        PYFRODBUS_COORDINATOR: coordinator,
        PYFRODBUS_REMOVE_LISTENER: remove_stop_listener,
        PYFRODBUS_DEVICE_INFO: device_info,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        data = hass.data[DOMAIN].pop(entry.entry_id)
        data[PYFRODBUS_REMOVE_LISTENER]()
    return unload_ok
