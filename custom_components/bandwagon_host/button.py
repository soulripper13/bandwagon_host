"""Button platform for Bandwagon Host VPS integration."""
import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import BandwagonEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bandwagon Host VPS buttons."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([
        BandwagonRestartButton(coordinator, entry),
        BandwagonKillButton(coordinator, entry),
    ])


class BandwagonRestartButton(BandwagonEntity, ButtonEntity):
    """Button to restart the VPS."""

    def __init__(self, coordinator, entry) -> None:
        """Initialize the button."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{self.veid}_restart_button"
        self._attr_name = "Restart"
        self._attr_icon = "mdi:restart"
        self._bandwagon_key = "restart"

    async def async_press(self) -> None:
        """Press the button."""
        api = self.hass.data[DOMAIN][self.entry.entry_id]["api"]
        try:
            await api.restart()
        except Exception as err:
            _LOGGER.error("Failed to restart VPS %s: %s", self.veid, err)
            raise HomeAssistantError(f"Failed to restart VPS {self.veid}: {err}") from err
        finally:
            await self.coordinator.async_request_refresh()


class BandwagonKillButton(BandwagonEntity, ButtonEntity):
    """Button to forcibly kill the VPS."""

    def __init__(self, coordinator, entry) -> None:
        """Initialize the button."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{self.veid}_kill_button"
        self._attr_name = "Kill (Force Stop)"
        self._attr_icon = "mdi:power-off"
        self._bandwagon_key = "kill"

    async def async_press(self) -> None:
        """Press the button."""
        api = self.hass.data[DOMAIN][self.entry.entry_id]["api"]
        try:
            await api.kill()
        except Exception as err:
            _LOGGER.error("Failed to kill VPS %s: %s", self.veid, err)
            raise HomeAssistantError(f"Failed to force stop VPS {self.veid}: {err}") from err
        finally:
            await self.coordinator.async_request_refresh()
