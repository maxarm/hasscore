"""Config flow for Fronius Battery Control."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv

from .const import DEFAULT_PORT, DOMAIN
from .pyfrodbus import FroniusModbusTcp

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    host = data[CONF_HOST]
    port = data[CONF_PORT]

    fronius_modbus_tcp = FroniusModbusTcp(host, port)

    return await fronius_modbus_tcp.device_info()


class FroniusModbusTcpConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Fronius Battery Control."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize."""
        self._data: dict[str, Any] = {
            CONF_HOST: vol.UNDEFINED,
            CONF_PORT: DEFAULT_PORT,
        }

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """First step in config flow."""
        errors = {}
        if user_input is not None:
            self._data[CONF_HOST] = user_input[CONF_HOST]
            self._data[CONF_PORT] = user_input[CONF_PORT]

            try:
                device_info = await validate_input(self.hass, user_input)
            except Exception:
                _LOGGER.exception("Exception occurred")
                errors["base"] = "unknown"

            if not errors:
                await self.async_set_unique_id(device_info["serial"])
                self._abort_if_unique_id_configured(updates=self._data)
                return self.async_create_entry(
                    title=self._data[CONF_HOST], data=self._data
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=self._data[CONF_HOST]): cv.string,
                    vol.Optional(
                        CONF_PORT, default=self._data[CONF_PORT]
                    ): cv.positive_int,
                }
            ),
            errors=errors,
        )
