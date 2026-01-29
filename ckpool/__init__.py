"""The Pool Coordinator integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_POOL_HOST, CONF_POOL_PORT, DOMAIN
from .coordinator_pool import PoolCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Pool Coordinator from a config entry."""
    _LOGGER.info("Setting up Pool Coordinator integration")
    
    try:
        # Setup Pool (ckstats API polling)
        coordinator = PoolCoordinator(hass, entry.data)
        coordinator._config_entry_id = entry.entry_id
        await coordinator.async_config_entry_first_refresh()
    
    except RuntimeError as err:
        _LOGGER.error("Failed to connect to pool API: %s", err)
        return False
    except Exception as err:  # pylint: disable=broad-except
        _LOGGER.error("Unexpected error during setup: %s", err)
        return False
    
    # Store coordinator
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
    }
    
    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        entry_data = hass.data[DOMAIN].pop(entry.entry_id)
        coordinator = entry_data["coordinator"]
        await coordinator.async_shutdown()
    
    return unload_ok
