"""Constants for the Bandwagon Host VPS integration."""
from homeassistant.const import Platform

DOMAIN = "bandwagon_host"

# Configuration and options keys
CONF_VEID = "veid"
CONF_API_KEY = "api_key"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_SCAN_INTERVAL = 60

# Platforms
PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.BUTTON,
]
