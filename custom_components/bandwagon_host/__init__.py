"""The Bandwagon Host VPS integration."""
import logging
import os
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_VEID,
    CONF_API_KEY,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    PLATFORMS,
)
from .api import BandwagonAPI
from .coordinator import BandwagonDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_register_lovelace_resource(hass: HomeAssistant) -> None:
    """Register Lovelace card resource safely."""
    try:
        # Check if dashboard resources are available
        lovelace = hass.data.get("lovelace")
        if lovelace and hasattr(lovelace, "resources"):
            resources = lovelace.resources
            if resources and hasattr(resources, "async_items") and hasattr(resources, "async_create_item"):
                url = "/bandwagon_host/bandwagon-host-card.js"
                # Check if already registered
                for resource in resources.async_items():
                    if resource.get("url") == url:
                        return
                await resources.async_create_item({
                    "res_type": "module",
                    "url": url,
                })
                _LOGGER.info("Registered Bandwagon Host Lovelace card resource successfully")
    except Exception as err:
        _LOGGER.debug("Could not automatically register Lovelace resource: %s", err)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Bandwagon Host VPS from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    veid = entry.data[CONF_VEID]
    api_key = entry.data[CONF_API_KEY]
    
    # Get scan interval (from options if modified, otherwise config entry data)
    scan_interval = entry.options.get(
        CONF_SCAN_INTERVAL,
        entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    )

    session = async_get_clientsession(hass)
    api = BandwagonAPI(session, veid, api_key)
    
    coordinator = BandwagonDataUpdateCoordinator(hass, api, scan_interval)

    # Fetch initial data before finishing setup
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "api": api,
    }

    # Register static path for Lovelace card
    card_path = os.path.join(os.path.dirname(__file__), "dist/bandwagon-host-card.js")
    if os.path.exists(card_path):
        await hass.http.async_register_static_paths([
            StaticPathConfig(
                "/bandwagon_host/bandwagon-host-card.js",
                card_path,
                cache_headers=False
            )
        ])
        # Attempt to register Lovelace resources programmatically
        hass.async_create_task(async_register_lovelace_resource(hass))

    # Set up all platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Add options update listener
    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)
