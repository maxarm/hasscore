"""The Fronius Modbus TCP integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

PLATFORMS: list[Platform] = [Platform.SENSOR]

# T O D O Create ConfigEntry type alias with API object
# Alias name should be prefixed by integration name
# type New_NameConfigEntry = ConfigEntry[MyApi]  # noqa: F821


# T O D O Update entry annotation
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Fronius Modbus TCP from a config entry."""

    # T O D O 1. Create API instance
    # T O D O 2. Validate the API connection (and authentication)
    # T O D O 3. Store an API object for your platforms to access
    # entry.runtime_data = MyAPI(...)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


# T O D O Update entry annotation
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
