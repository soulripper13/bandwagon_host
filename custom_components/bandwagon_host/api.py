"""API client for Bandwagon Host / KiwiVM REST API."""
import asyncio
import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)

class BandwagonError(Exception):
    """Base exception for Bandwagon Host API."""

class CannotConnect(BandwagonError):
    """Exception to indicate connection failure."""

class InvalidAuth(BandwagonError):
    """Exception to indicate authentication failure."""

class RateLimited(BandwagonError):
    """Exception raised when the API rate limit is exhausted."""

class BandwagonAPI:
    """Client wrapper for Bandwagon Host VPS REST API."""

    def __init__(self, session: aiohttp.ClientSession, veid: str, api_key: str):
        """Initialize the API client."""
        self.session = session
        self.veid = str(veid).strip()
        self.api_key = str(api_key).strip()
        self.base_url = "https://api.64clouds.com/v1"

    async def _request(self, endpoint: str, params: dict[str, Any] | None = None) -> dict:
        """Perform a request to the API."""
        if params is None:
            params = {}
        
        # Merge credentials into query parameters (as requested by API)
        request_data = {
            "veid": self.veid,
            "api_key": self.api_key,
            **params
        }
        
        url = f"{self.base_url}/{endpoint}"
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with self.session.post(url, data=request_data, timeout=timeout) as response:
                if response.status in (401, 403):
                    raise InvalidAuth("Authentication failed (invalid VEID or API key)")
                if response.status == 429:
                    raise RateLimited("Bandwagon Host API rate limit exceeded")
                if response.status != 200:
                    raise CannotConnect(f"HTTP error {response.status} connecting to Bandwagon API")
                
                # Use content_type=None in case Content-Type header is not application/json
                data = await response.json(content_type=None)
                
                # Check for API-level errors
                if not isinstance(data, dict):
                    raise BandwagonError("Bandwagon Host API returned an unexpected response")

                error_code = data.get("error")
                if error_code not in (None, 0, "0"):
                    msg = str(data.get("message", f"API error code {error_code}"))
                    # Error code 7 is typically invalid credentials/VEID/API key for 64clouds API.
                    if "invalid" in msg.lower() or "authentication" in msg.lower() or error_code == 7:
                        raise InvalidAuth(msg)
                    raise BandwagonError(msg)
                
                return data
        except aiohttp.ClientConnectorError as err:
            raise CannotConnect(f"Connection error: {err}") from err
        except asyncio.TimeoutError as err:
            raise CannotConnect(f"Timeout error: {err}") from err
        except BandwagonError:
            raise
        except Exception as err:
            raise BandwagonError(f"Unexpected error: {err}") from err

    async def get_service_info(self) -> dict:
        """Get basic service info."""
        return await self._request("getServiceInfo")

    async def get_live_service_info(self) -> dict:
        """Get live service info (takes up to 15 seconds)."""
        return await self._request("getLiveServiceInfo")

    async def start(self) -> dict:
        """Start the VPS."""
        return await self._request("start")

    async def stop(self) -> dict:
        """Stop the VPS."""
        return await self._request("stop")

    async def restart(self) -> dict:
        """Restart the VPS."""
        return await self._request("restart")

    async def kill(self) -> dict:
        """Kill (force stop) the VPS."""
        return await self._request("kill")

    async def get_rate_limit_status(self) -> dict:
        """Get remaining API points for the current intervals."""
        return await self._request("getRateLimitStatus")
