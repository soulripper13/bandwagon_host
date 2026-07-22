"""Sensor platform for Bandwagon Host VPS integration."""
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    EntityCategory,
    PERCENTAGE,
    UnitOfInformation,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .entity import BandwagonEntity


def _join_values(value: Any) -> str | None:
    """Render an API list without exposing Python container syntax."""
    if not value:
        return None
    if isinstance(value, (list, tuple, set)):
        return ", ".join(str(item) for item in value)
    return str(value)


def _format_ptr(value: Any) -> str | None:
    """Render reverse DNS mappings compactly."""
    if not value:
        return None
    if isinstance(value, dict):
        return ", ".join(f"{ip}: {ptr}" for ip, ptr in value.items())
    return str(value)


def _disk_total_bytes(data: dict) -> float:
    """Return the actual KVM image size when available."""
    actual_quota_gb = data.get("ve_disk_quota_gb")
    if actual_quota_gb not in (None, ""):
        try:
            return float(actual_quota_gb) * 1024**3
        except (TypeError, ValueError):
            pass
    try:
        return float(data.get("plan_disk", 0))
    except (TypeError, ValueError):
        return 0

@dataclass(frozen=True, kw_only=True)
class BandwagonSensorEntityDescription(SensorEntityDescription):
    """Class describing Bandwagon Host VPS sensor entities."""
    value_fn: Callable[[dict], Any]


SENSOR_DESCRIPTIONS: list[BandwagonSensorEntityDescription] = [
    BandwagonSensorEntityDescription(
        key="ve_status",
        name="Status",
        icon="mdi:server",
        value_fn=lambda data: (
            str(data.get("ve_status")).strip().capitalize()
            if data.get("ve_status") is not None
            else (
                "Running"
                if (data.get("vz_status") or {}).get("nproc") not in (None, 0, "0")
                else "Stopped"
            )
            if "vz_status" in data
            else "Unknown"
        ),
    ),
    BandwagonSensorEntityDescription(
        key="ip_addresses",
        name="IP Addresses",
        icon="mdi:ip",
        value_fn=lambda data: ", ".join(data.get("ip_addresses", [])) if data.get("ip_addresses") else None,
    ),
    BandwagonSensorEntityDescription(
        key="ssh_port",
        name="SSH Port",
        icon="mdi:port",
        value_fn=lambda data: data.get("ssh_port"),
    ),
    BandwagonSensorEntityDescription(
        key="data_used",
        name="Monthly Data Used",
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.GIGABYTES,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:swap-vertical",
        value_fn=lambda data: round((data.get("data_counter", 0) * data.get("monthly_data_multiplier", 1.0)) / (1024**3), 2) if "data_counter" in data else None,
    ),
    BandwagonSensorEntityDescription(
        key="data_limit",
        name="Monthly Data Limit",
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.GIGABYTES,
        icon="mdi:package-down",
        value_fn=lambda data: round((data.get("plan_monthly_data", 0) * data.get("monthly_data_multiplier", 1.0)) / (1024**3), 2) if "plan_monthly_data" in data else None,
    ),
    BandwagonSensorEntityDescription(
        key="data_remaining",
        name="Monthly Data Remaining",
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.GIGABYTES,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:swap-horizontal",
        value_fn=lambda data: round((max(0, data.get("plan_monthly_data", 0) - data.get("data_counter", 0)) * data.get("monthly_data_multiplier", 1.0)) / (1024**3), 2) if "plan_monthly_data" in data and "data_counter" in data else None,
    ),
    BandwagonSensorEntityDescription(
        key="data_usage_percent",
        name="Monthly Data Usage",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:chart-donut",
        value_fn=lambda data: round(
            min(100, (data.get("data_counter", 0) / data.get("plan_monthly_data", 1)) * 100), 1
        ) if data.get("plan_monthly_data", 0) > 0 else None,
    ),
    BandwagonSensorEntityDescription(
        key="data_next_reset",
        name="Data Reset Date",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:calendar-clock",
        value_fn=lambda data: dt_util.utc_from_timestamp(data.get("data_next_reset")) if data.get("data_next_reset") else None,
    ),
    BandwagonSensorEntityDescription(
        key="ram_used",
        name="RAM Used",
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.MEGABYTES,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:memory",
        value_fn=lambda data: round(max(0, data.get("plan_ram", 0) - (data.get("mem_available_kb", 0) * 1024)) / (1024**2), 1) if "plan_ram" in data and "mem_available_kb" in data else None,
    ),
    BandwagonSensorEntityDescription(
        key="ram_total",
        name="RAM Total",
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.MEGABYTES,
        icon="mdi:memory",
        value_fn=lambda data: round(data.get("plan_ram", 0) / (1024**2), 1) if data.get("plan_ram") else None,
    ),
    BandwagonSensorEntityDescription(
        key="ram_usage_percent",
        name="RAM Usage",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:memory",
        value_fn=lambda data: round((max(0, data.get("plan_ram", 0) - (data.get("mem_available_kb", 0) * 1024)) / data.get("plan_ram", 1)) * 100, 1) if "plan_ram" in data and "mem_available_kb" in data and data.get("plan_ram", 0) > 0 else None,
    ),
    BandwagonSensorEntityDescription(
        key="disk_used",
        name="Disk Used",
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.GIGABYTES,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:harddisk",
        value_fn=lambda data: round(data.get("ve_used_disk_space_b", 0) / (1024**3), 2) if "ve_used_disk_space_b" in data else None,
    ),
    BandwagonSensorEntityDescription(
        key="disk_total",
        name="Disk Total",
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.GIGABYTES,
        icon="mdi:harddisk",
        value_fn=lambda data: round(_disk_total_bytes(data) / (1024**3), 2) if _disk_total_bytes(data) > 0 else None,
    ),
    BandwagonSensorEntityDescription(
        key="disk_usage_percent",
        name="Disk Usage",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:harddisk",
        value_fn=lambda data: round((data.get("ve_used_disk_space_b", 0) / _disk_total_bytes(data)) * 100, 1) if "ve_used_disk_space_b" in data and _disk_total_bytes(data) > 0 else None,
    ),
    BandwagonSensorEntityDescription(
        key="swap_total",
        name="Swap Total",
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.MEGABYTES,
        icon="mdi:folder-swap",
        value_fn=lambda data: round(data.get("swap_total_kb", 0) / 1024, 1) if data.get("swap_total_kb") else (round(data.get("plan_swap", 0) / (1024**2), 1) if data.get("plan_swap") else None),
    ),
    BandwagonSensorEntityDescription(
        key="swap_available",
        name="Swap Available",
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.MEGABYTES,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:folder-swap",
        value_fn=lambda data: round(data.get("swap_available_kb", 0) / 1024, 1) if data.get("swap_available_kb") else None,
    ),
    BandwagonSensorEntityDescription(
        key="load_average",
        name="Load Average",
        icon="mdi:cpu-64-bit",
        value_fn=lambda data: data.get("load_average"),
    ),
    BandwagonSensorEntityDescription(
        key="node_alias",
        name="Node Alias",
        icon="mdi:server-network",
        value_fn=lambda data: data.get("node_alias"),
    ),
    BandwagonSensorEntityDescription(
        key="node_datacenter",
        name="Datacenter",
        icon="mdi:office-building-marker-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("node_datacenter"),
    ),
    BandwagonSensorEntityDescription(
        key="ipv6_tunnel_endpoint",
        name="IPv6 Tunnel Endpoint",
        icon="mdi:ip-network-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("ipv6_sit_tunnel_endpoint"),
    ),
    BandwagonSensorEntityDescription(
        key="vm_type",
        name="Hypervisor",
        icon="mdi:server-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: str(data["vm_type"]).upper() if data.get("vm_type") else None,
    ),
    BandwagonSensorEntityDescription(
        key="hostname",
        name="Hostname",
        icon="mdi:server-network",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("hostname"),
    ),
    BandwagonSensorEntityDescription(
        key="live_hostname",
        name="Live Hostname",
        icon="mdi:console-network-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("live_hostname"),
    ),
    BandwagonSensorEntityDescription(
        key="operating_system",
        name="Operating System",
        icon="mdi:linux",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("os"),
    ),
    BandwagonSensorEntityDescription(
        key="mac_address",
        name="MAC Address",
        icon="mdi:network-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("ve_mac1"),
    ),
    BandwagonSensorEntityDescription(
        key="private_ip_addresses",
        name="Private IP Addresses",
        icon="mdi:ip-network",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: _join_values(data.get("private_ip_addresses")),
    ),
    BandwagonSensorEntityDescription(
        key="reverse_dns",
        name="Reverse DNS",
        icon="mdi:dns-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: _format_ptr(data.get("ptr")),
    ),
    BandwagonSensorEntityDescription(
        key="mounted_iso",
        name="Mounted ISO",
        icon="mdi:disc",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("iso1") or None,
    ),
    BandwagonSensorEntityDescription(
        key="ipv6_limit",
        name="IPv6 Subnet Limit",
        icon="mdi:numeric-6-box-multiple-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("plan_max_ipv6s"),
    ),
    BandwagonSensorEntityDescription(
        key="actual_disk_quota",
        name="Actual Disk Quota",
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.GIGABYTES,
        icon="mdi:harddisk",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("ve_disk_quota_gb"),
    ),
    BandwagonSensorEntityDescription(
        key="bandwidth_multiplier",
        name="Bandwidth Accounting Multiplier",
        icon="mdi:multiplication-box",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("monthly_data_multiplier"),
    ),
    BandwagonSensorEntityDescription(
        key="suspension_count",
        name="Suspension Count",
        icon="mdi:counter",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("suspension_count"),
    ),
    BandwagonSensorEntityDescription(
        key="total_abuse_points",
        name="Abuse Points",
        icon="mdi:alert-decagram-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("total_abuse_points"),
    ),
    BandwagonSensorEntityDescription(
        key="max_abuse_points",
        name="Maximum Abuse Points",
        icon="mdi:alert-decagram",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("max_abuse_points"),
    ),
    BandwagonSensorEntityDescription(
        key="remaining_points_15min",
        name="API Points Remaining (15 min)",
        icon="mdi:speedometer",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("remaining_points_15min"),
    ),
    BandwagonSensorEntityDescription(
        key="remaining_points_24h",
        name="API Points Remaining (24 h)",
        icon="mdi:speedometer-medium",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("remaining_points_24h"),
    ),
    BandwagonSensorEntityDescription(
        key="node_location",
        name="Node Location",
        icon="mdi:map-marker",
        value_fn=lambda data: data.get("node_location"),
    ),
    BandwagonSensorEntityDescription(
        key="plan",
        name="Plan",
        icon="mdi:card-account-details",
        value_fn=lambda data: data.get("plan"),
    ),
    BandwagonSensorEntityDescription(
        key="is_cpu_throttled",
        name="CPU Throttled",
        icon="mdi:speedometer-slow",
        value_fn=lambda data: "Yes" if data.get("is_cpu_throttled") == 1 else ("No" if "is_cpu_throttled" in data else None),
    ),
    BandwagonSensorEntityDescription(
        key="is_disk_throttled",
        name="Disk Throttled",
        icon="mdi:speedometer-slow",
        value_fn=lambda data: "Yes" if data.get("is_disk_throttled") == 1 else ("No" if "is_disk_throttled" in data else None),
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bandwagon Host VPS sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    
    async_add_entities(
        BandwagonSensor(coordinator, entry, description)
        for description in SENSOR_DESCRIPTIONS
    )


class BandwagonSensor(BandwagonEntity, SensorEntity):
    """Representation of a Bandwagon Host VPS sensor."""

    entity_description: BandwagonSensorEntityDescription

    def __init__(
        self,
        coordinator,
        entry,
        description: BandwagonSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self.entity_description = description
        self._attr_unique_id = f"{self.veid}_{description.key}"
        self.entity_id = f"sensor.bandwagon_host_{self.veid}_{description.key}"

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        data = self.coordinator.data or {}
        return self.entity_description.value_fn(data)
