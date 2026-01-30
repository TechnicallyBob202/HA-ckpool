"""Config flow for CKPool integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CONF_POOL_HOST,
    CONF_POOL_PORT,
    DOMAIN,
    POOL_DEFAULT_HOST,
    POOL_DEFAULT_PORT,
)

_LOGGER = logging.getLogger(__name__)


class PoolConnectionFailed(HomeAssistantError):
    """Error to indicate pool connection failed."""


class CKPoolConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for CKPool."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - configure pool connection."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            host = user_input[CONF_POOL_HOST]
            port = user_input[CONF_POOL_PORT]
            
            # Validate port
            if not 1 <= port <= 65535:
                errors[CONF_POOL_PORT] = "invalid_port"
            
            # Validate host
            if not host or host.isspace():
                errors[CONF_POOL_HOST] = "invalid_host"
            
            if not errors:
                # Test connection to pool API
                try:
                    import aiohttp
                    url = f"http://{host}:{port}/api/health"
                    timeout = aiohttp.ClientTimeout(total=5)
                    
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        async with session.get(url) as response:
                            if response.status != 200:
                                errors["base"] = "pool_connection_failed"
                except Exception as err:  # pylint: disable=broad-except
                    _LOGGER.debug("Pool connection test failed: %s", err)
                    errors["base"] = "pool_connection_failed"
            
            if not errors:
                # Check if already configured
                await self.async_set_unique_id(f"ckpool_{host}_{port}")
                self._abort_if_unique_id_configured()
                
                # Store config and create entry
                config_data = {
                    CONF_POOL_HOST: host,
                    CONF_POOL_PORT: port,
                }
                
                return self.async_create_entry(
                    title=f"CKPool ({host}:{port})",
                    data=config_data,
                )
        
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_POOL_HOST, default=POOL_DEFAULT_HOST): str,
                    vol.Optional(CONF_POOL_PORT, default=POOL_DEFAULT_PORT): int,
                }
            ),
            errors=errors,
            description_placeholders={
                "default_host": POOL_DEFAULT_HOST,
                "default_port": str(POOL_DEFAULT_PORT),
            },
        )