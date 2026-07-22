"""Config flow for Bandwagon Host VPS integration."""
import logging
from typing import Any, Dict, Optional
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_VEID,
    CONF_API_KEY,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
)
from .api import BandwagonAPI, CannotConnect, InvalidAuth

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_VEID): str,
    vol.Required(CONF_API_KEY): str,
})

class BandwagonHostConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Bandwagon Host VPS."""

    VERSION = 1

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None) -> config_entries.FlowResult:
        """Handle the initial step."""
        errors: Dict[str, str] = {}
        if user_input is not None:
            veid = user_input[CONF_VEID].strip()
            api_key = user_input[CONF_API_KEY].strip()

            session = async_get_clientsession(self.hass)
            api = BandwagonAPI(session, veid, api_key)
            try:
                # Validate credentials by fetching basic service info
                service_info = await api.get_service_info()
                hostname = service_info.get("hostname", f"VEID {veid}")
                
                await self.async_set_unique_id(veid)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Bandwagon Host ({hostname})",
                    data={
                        CONF_VEID: veid,
                        CONF_API_KEY: api_key,
                    },
                )
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception in config flow: %s", err)
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_reauth(
        self, entry_data: Dict[str, Any]
    ) -> config_entries.FlowResult:
        """Start reauthentication for an existing entry."""
        self._reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> config_entries.FlowResult:
        """Validate and store a replacement API key."""
        errors: Dict[str, str] = {}
        if user_input is not None and self._reauth_entry is not None:
            veid = self._reauth_entry.data[CONF_VEID]
            api_key = user_input[CONF_API_KEY].strip()
            api = BandwagonAPI(async_get_clientsession(self.hass), veid, api_key)
            try:
                await api.get_service_info()
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected reauthentication error: %s", err)
                errors["base"] = "unknown"
            else:
                return self.async_update_reload_and_abort(
                    self._reauth_entry,
                    data_updates={CONF_API_KEY: api_key},
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): str}),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return BandwagonHostOptionsFlowHandler(config_entry)


class BandwagonHostOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for Bandwagon Host VPS."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: Optional[Dict[str, Any]] = None) -> config_entries.FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Default to previous options or config entry data or default value
        scan_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=scan_interval,
                ): vol.All(vol.Coerce(int), vol.Range(min=30, max=3600)),
            }),
        )
