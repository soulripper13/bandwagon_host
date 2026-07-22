"""Switch platform for Bandwagon Host VPS integration."""
import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
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
    """Set up Bandwagon Host VPS switch."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([BandwagonPowerSwitch(coordinator, entry)])


class BandwagonPowerSwitch(BandwagonEntity, SwitchEntity):
    """Representation of a Bandwagon Host VPS power switch."""

    def __init__(self, coordinator, entry) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{self.veid}_power_switch"
        self._attr_name = "Power"
        self._attr_icon = "mdi:power"
        self._bandwagon_key = "power"
        self._is_optimistic_on = None

    @property
    def is_on(self) -> bool:
        """Return true if VPS is running or starting."""
        if self._is_optimistic_on is not None:
            return self._is_optimistic_on
        
        data = self.coordinator.data or {}
        
        # Check KVM hypervisor status
        if "ve_status" in data and data.get("ve_status") is not None:
            status = str(data.get("ve_status", "")).strip().lower()
            return status in ("running", "starting")
            
        # Check OpenVZ hypervisor status
        if "vz_status" in data:
            vz = data.get("vz_status") or {}
            nproc = vz.get("nproc", 0)
            try:
                if int(nproc) > 0:
                    return True
            except (ValueError, TypeError):
                pass
            return False

        # Fallback check (e.g. if load_average is reported)
        load = data.get("load_average")
        if load not in (None, "", "0.00 0.00 0.00"):
            return True

        return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the VPS on."""
        self._is_optimistic_on = True
        self.async_write_ha_state()
        
        api = self.hass.data[DOMAIN][self.entry.entry_id]["api"]
        try:
            await api.start()
        except Exception as err:
            _LOGGER.error("Failed to start VPS %s: %s", self.veid, err)
            raise HomeAssistantError(f"Failed to start VPS {self.veid}: {err}") from err
        finally:
            self._is_optimistic_on = None
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the VPS off."""
        self._is_optimistic_on = False
        self.async_write_ha_state()
        
        api = self.hass.data[DOMAIN][self.entry.entry_id]["api"]
        try:
            await api.stop()
        except Exception as err:
            _LOGGER.error("Failed to stop VPS %s: %s", self.veid, err)
            raise HomeAssistantError(f"Failed to stop VPS {self.veid}: {err}") from err
        finally:
            self._is_optimistic_on = None
            await self.coordinator.async_request_refresh()
