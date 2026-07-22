"""Base entity class for Bandwagon Host VPS integration."""
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_VEID

class BandwagonEntity(CoordinatorEntity):
    """Base class for all Bandwagon Host entities."""

    def __init__(self, coordinator, entry) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self.entry = entry
        self.veid = entry.data[CONF_VEID]

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Expose stable metadata for frontend entity discovery."""
        attributes = {"bandwagon_veid": str(self.veid)}
        hostname = (self.coordinator.data or {}).get("hostname")
        if hostname:
            attributes["bandwagon_hostname"] = str(hostname)
        key = getattr(self, "_bandwagon_key", None)
        description = getattr(self, "entity_description", None)
        if description is not None:
            key = description.key
        if key:
            attributes["bandwagon_key"] = key
        return attributes

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this Bandwagon VPS."""
        data = self.coordinator.data or {}
        hostname = data.get("hostname", f"VEID {self.veid}")
        plan = data.get("plan", "Unknown")
        os_version = data.get("os", "Unknown")
        node_location = data.get("node_location", "Unknown")

        return DeviceInfo(
            identifiers={(DOMAIN, self.veid)},
            name=f"VPS: {hostname}",
            manufacturer="Bandwagon Host",
            model=f"Plan: {plan}",
            sw_version=os_version,
            hw_version=node_location,
            configuration_url="https://kiwivm.it7.net",
        )
