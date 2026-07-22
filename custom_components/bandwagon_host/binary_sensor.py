"""Binary sensor platform for Bandwagon Host VPS integration."""
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import BandwagonEntity


def _is_on(value: Any) -> bool:
    """Normalize common API boolean representations."""
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True, kw_only=True)
class BandwagonBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describe a Bandwagon Host binary sensor."""

    value_fn: Callable[[dict], bool | None]


BINARY_SENSOR_DESCRIPTIONS = [
    BandwagonBinarySensorEntityDescription(
        key="suspended",
        name="Suspended",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:server-off",
        value_fn=lambda data: _is_on(data["suspended"]) if "suspended" in data else None,
    ),
    BandwagonBinarySensorEntityDescription(
        key="policy_violation",
        name="Policy Violation",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:alert-octagon",
        value_fn=lambda data: _is_on(data["policy_violation"]) if "policy_violation" in data else None,
    ),
    BandwagonBinarySensorEntityDescription(
        key="ip_nullrouted",
        name="IP Nullrouted",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:shield-alert",
        value_fn=lambda data: bool(data.get("ip_nullroutes")) if "ip_nullroutes" in data else None,
    ),
    BandwagonBinarySensorEntityDescription(
        key="cpu_throttled",
        name="CPU Throttled",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:speedometer-slow",
        value_fn=lambda data: _is_on(data["is_cpu_throttled"]) if "is_cpu_throttled" in data else None,
    ),
    BandwagonBinarySensorEntityDescription(
        key="disk_throttled",
        name="Disk Throttled",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:harddisk-alert",
        value_fn=lambda data: _is_on(data["is_disk_throttled"]) if "is_disk_throttled" in data else None,
    ),
    BandwagonBinarySensorEntityDescription(
        key="ipv6_ready",
        name="IPv6 Available",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:check-network-outline",
        value_fn=lambda data: _is_on(data["location_ipv6_ready"]) if "location_ipv6_ready" in data else None,
    ),
    BandwagonBinarySensorEntityDescription(
        key="private_network_available",
        name="Private Network Available",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:lan-connect",
        value_fn=lambda data: (
            _is_on(data.get("plan_private_network_available"))
            and _is_on(data.get("location_private_network_available"))
            if "plan_private_network_available" in data
            and "location_private_network_available" in data
            else None
        ),
    ),
    BandwagonBinarySensorEntityDescription(
        key="rdns_api_available",
        name="Reverse DNS Management Available",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:dns",
        value_fn=lambda data: _is_on(data["rdns_api_available"]) if "rdns_api_available" in data else None,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bandwagon Host binary sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities(
        BandwagonBinarySensor(coordinator, entry, description)
        for description in BINARY_SENSOR_DESCRIPTIONS
    )


class BandwagonBinarySensor(BandwagonEntity, BinarySensorEntity):
    """Represent a Bandwagon Host binary sensor."""

    entity_description: BandwagonBinarySensorEntityDescription

    def __init__(self, coordinator, entry, description) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, entry)
        self.entity_description = description
        self._attr_unique_id = f"{self.veid}_{description.key}"
        self.entity_id = f"binary_sensor.bandwagon_host_{self.veid}_{description.key}"

    @property
    def is_on(self) -> bool | None:
        """Return the binary sensor state."""
        return self.entity_description.value_fn(self.coordinator.data or {})
