"""Data update coordinator for the Bandwagon Host VPS integration."""
from datetime import timedelta
import logging
import time

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed

from .const import DOMAIN
from .api import BandwagonAPI, CannotConnect, InvalidAuth, BandwagonError, RateLimited

_LOGGER = logging.getLogger(__name__)

class BandwagonDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Bandwagon Host VPS data."""

    def __init__(self, hass: HomeAssistant, api: BandwagonAPI, scan_interval: int) -> None:
        """Initialize the coordinator."""
        self.api = api
        self._last_rate_limit_update = 0.0
        self._rate_limit_data: dict = {}
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=max(30, scan_interval)),
        )

    async def _async_update_data(self) -> dict:
        """Fetch data from Bandwagon Host VPS REST API."""
        try:
            data = await self.api.get_live_service_info()
            data.pop("screendump_png_base64", None)

            now = time.monotonic()
            if now - self._last_rate_limit_update >= 900:
                try:
                    rate_data = await self.api.get_rate_limit_status()
                except InvalidAuth:
                    raise
                except BandwagonError as err:
                    _LOGGER.debug("Unable to update Bandwagon API rate limits: %s", err)
                    self._last_rate_limit_update = now
                else:
                    self._rate_limit_data = {
                        "remaining_points_15min": rate_data.get("remaining_points_15min"),
                        "remaining_points_24h": rate_data.get("remaining_points_24h"),
                    }
                    self._last_rate_limit_update = now

            data.update(
                {key: value for key, value in self._rate_limit_data.items() if value is not None}
            )
            return data
        except CannotConnect as err:
            raise UpdateFailed(f"Error communicating with Bandwagon Host API: {err}") from err
        except InvalidAuth as err:
            raise ConfigEntryAuthFailed("Bandwagon Host API credentials are no longer valid") from err
        except RateLimited as err:
            raise UpdateFailed(f"Bandwagon Host API rate limit exceeded: {err}") from err
        except BandwagonError as err:
            raise UpdateFailed(f"Bandwagon Host API returned error: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error fetching Bandwagon Host data: {err}") from err
