"""Sensor platform for CKPool integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass
class CKPoolSensorEntityDescriptionMixin:
    """Mixin for required keys."""

    value_fn: Callable[[dict[str, Any]], Any]


@dataclass
class CKPoolSensorEntityDescription(
    SensorEntityDescription, CKPoolSensorEntityDescriptionMixin
):
    """Describes CKPool sensor entity."""

    attr_fn: Callable[[dict[str, Any]], dict[str, Any]] | None = None


def format_hashrate(hashrate_hs: float | int) -> str:
    """Format hashrate with dynamic units (TH/s, GH/s, MH/s, KH/s, or H/s)."""
    try:
        hashrate = float(hashrate_hs)
        
        # Define thresholds and units
        if hashrate >= 1_000_000_000_000:  # >= 1 TH/s
            return f"{hashrate / 1_000_000_000_000:.2f} TH/s"
        elif hashrate >= 1_000_000_000:  # >= 1 GH/s
            return f"{hashrate / 1_000_000_000:.2f} GH/s"
        elif hashrate >= 1_000_000:  # >= 1 MH/s
            return f"{hashrate / 1_000_000:.2f} MH/s"
        elif hashrate >= 1_000:  # >= 1 KH/s
            return f"{hashrate / 1_000:.2f} KH/s"
        else:  # < 1 KH/s, show as H/s
            return f"{hashrate:.2f} H/s"
    except (ValueError, TypeError):
        return "0 H/s"


def format_difficulty(difficulty: float | int) -> str:
    """Format difficulty with dynamic units (T, G, M, K, or raw)."""
    try:
        diff = float(difficulty)
        
        # Define thresholds and units
        if diff >= 1_000_000_000_000:  # >= 1 T
            return f"{diff / 1_000_000_000_000:.2f}T"
        elif diff >= 1_000_000_000:  # >= 1 G
            return f"{diff / 1_000_000_000:.2f}G"
        elif diff >= 1_000_000:  # >= 1 M
            return f"{diff / 1_000_000:.2f}M"
        elif diff >= 1_000:  # >= 1 K
            return f"{diff / 1_000:.2f}K"
        else:  # < 1 K, show as raw number
            return f"{diff:.2f}"
    except (ValueError, TypeError):
        return "0"


def _format_timestamp(timestamp_ms: int | float) -> str:
    """Format millisecond timestamp to readable format."""
    if not timestamp_ms or timestamp_ms == 0:
        return "Never"
    try:
        timestamp_s = timestamp_ms / 1000
        dt = datetime.fromtimestamp(timestamp_s)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, OSError):
        return "Unknown"


# ============================================================================
# Pool Sensor Types (ckstats API)
# ============================================================================

POOL_SENSOR_TYPES: tuple[CKPoolSensorEntityDescription, ...] = (
    CKPoolSensorEntityDescription(
        key="pool_id",
        name="Pool ID",
        icon="mdi:identifier",
        value_fn=lambda data: data.get("id", "Unknown"),
    ),
    CKPoolSensorEntityDescription(
        key="pool_runtime",
        name="Pool Runtime",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:clock-outline",
        value_fn=lambda data: data.get("runtime", 0),
    ),
    CKPoolSensorEntityDescription(
        key="pool_timestamp",
        name="Pool Last Update",
        icon="mdi:clock-check-outline",
        value_fn=lambda data: data.get("timestamp", "Unknown"),
    ),
    CKPoolSensorEntityDescription(
        key="pool_users",
        name="Connected Users",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:account-multiple",
        value_fn=lambda data: data.get("users", 0),
    ),
    CKPoolSensorEntityDescription(
        key="pool_workers",
        name="Connected Workers",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:lan-connect",
        value_fn=lambda data: data.get("workers", 0),
    ),
    CKPoolSensorEntityDescription(
        key="pool_idle",
        name="Idle Workers",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:sleep",
        value_fn=lambda data: data.get("idle", 0),
    ),
    CKPoolSensorEntityDescription(
        key="pool_disconnected",
        name="Disconnected Workers",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:lan-disconnect",
        value_fn=lambda data: data.get("disconnected", 0),
    ),
    CKPoolSensorEntityDescription(
        key="pool_hashrate_1m",
        name="Pool Hashrate (1m)",
        icon="mdi:speedometer",
        value_fn=lambda data: format_hashrate(data.get("hashrate1m", 0)),
    ),
    CKPoolSensorEntityDescription(
        key="pool_hashrate_5m",
        name="Pool Hashrate (5m)",
        icon="mdi:speedometer",
        value_fn=lambda data: format_hashrate(data.get("hashrate5m", 0)),
    ),
    CKPoolSensorEntityDescription(
        key="pool_hashrate_15m",
        name="Pool Hashrate (15m)",
        icon="mdi:speedometer",
        value_fn=lambda data: format_hashrate(data.get("hashrate15m", 0)),
    ),
    CKPoolSensorEntityDescription(
        key="pool_hashrate_1h",
        name="Pool Hashrate (1h)",
        icon="mdi:speedometer",
        value_fn=lambda data: format_hashrate(data.get("hashrate1hr", 0)),
    ),
    CKPoolSensorEntityDescription(
        key="pool_hashrate_6h",
        name="Pool Hashrate (6h)",
        icon="mdi:speedometer",
        value_fn=lambda data: format_hashrate(data.get("hashrate6hr", 0)),
    ),
    CKPoolSensorEntityDescription(
        key="pool_hashrate_1d",
        name="Pool Hashrate (24h)",
        icon="mdi:speedometer",
        value_fn=lambda data: format_hashrate(data.get("hashrate1d", 0)),
    ),
    CKPoolSensorEntityDescription(
        key="pool_hashrate_7d",
        name="Pool Hashrate (7d)",
        icon="mdi:speedometer",
        value_fn=lambda data: format_hashrate(data.get("hashrate7d", 0)),
    ),
    CKPoolSensorEntityDescription(
        key="pool_difficulty",
        name="Network Difficulty",
        native_unit_of_measurement="%",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:target",
        value_fn=lambda data: data.get("diff", 0),
    ),
    CKPoolSensorEntityDescription(
        key="pool_best_share",
        name="Best Share Difficulty",
        icon="mdi:star",
        value_fn=lambda data: format_difficulty(data.get("bestshare", 0)),
    ),
    CKPoolSensorEntityDescription(
        key="pool_shares_accepted",
        name="Total Shares Accepted",
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:check-circle",
        value_fn=lambda data: data.get("accepted", 0),
    ),
    CKPoolSensorEntityDescription(
        key="pool_shares_rejected",
        name="Total Shares Rejected",
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:close-circle",
        value_fn=lambda data: data.get("rejected", 0),
    ),
    CKPoolSensorEntityDescription(
        key="pool_sps_1m",
        name="Shares Per Second (1m)",
        native_unit_of_measurement="SPS",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:share",
        value_fn=lambda data: data.get("SPS1m", 0),
    ),
    CKPoolSensorEntityDescription(
        key="pool_sps_5m",
        name="Shares Per Second (5m)",
        native_unit_of_measurement="SPS",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:share",
        value_fn=lambda data: data.get("SPS5m", 0),
    ),
    CKPoolSensorEntityDescription(
        key="pool_sps_15m",
        name="Shares Per Second (15m)",
        native_unit_of_measurement="SPS",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:share",
        value_fn=lambda data: data.get("SPS15m", 0),
    ),
    CKPoolSensorEntityDescription(
        key="pool_sps_1h",
        name="Shares Per Second (1h)",
        native_unit_of_measurement="SPS",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:share",
        value_fn=lambda data: data.get("SPS1h", 0),
    ),
)

# ============================================================================
# User Sensor Types (Primary user from /api/users)
# ============================================================================

USER_SENSOR_TYPES: tuple[CKPoolSensorEntityDescription, ...] = (
    CKPoolSensorEntityDescription(
        key="user_address",
        name="User Address",
        icon="mdi:wallet",
        value_fn=lambda data: data.get("userAddress", "Unknown"),
    ),
    CKPoolSensorEntityDescription(
        key="user_hashrate_1h",
        name="User Hashrate (1h)",
        icon="mdi:speedometer",
        value_fn=lambda data: format_hashrate(data.get("hashrate1hr", 0)),
    ),
    CKPoolSensorEntityDescription(
        key="user_hashrate_1d",
        name="User Hashrate (24h)",
        icon="mdi:speedometer",
        value_fn=lambda data: format_hashrate(data.get("hashrate1d", 0)),
    ),
    CKPoolSensorEntityDescription(
        key="user_shares",
        name="User Total Shares",
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:share",
        value_fn=lambda data: data.get("shares", 0),
    ),
    CKPoolSensorEntityDescription(
        key="user_best_share",
        name="User Best Share Difficulty",
        icon="mdi:star",
        value_fn=lambda data: format_difficulty(data.get("bestEver", 0)),
    ),
    CKPoolSensorEntityDescription(
        key="user_workers",
        name="User Worker Count",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:lan-connect",
        value_fn=lambda data: data.get("workerCount", 0),
    ),
    CKPoolSensorEntityDescription(
        key="user_last_share",
        name="User Last Share Time",
        icon="mdi:clock-outline",
        value_fn=lambda data: _format_timestamp(data.get("lastShare", 0)),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors based on device type."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    coordinator = entry_data["coordinator"]
    
    # Track which sensors we've created
    created_sensors: set[str] = set()

    @callback
    def async_add_pool_sensors() -> None:
        """Add sensors for pool and user data."""
        new_entities: list[CKPoolSensor] = []
        
        # Add pool sensors
        if "pool" not in created_sensors:
            _LOGGER.info("Creating pool sensors")
            created_sensors.add("pool")
            
            for description in POOL_SENSOR_TYPES:
                new_entities.append(
                    CKPoolSensor(
                        coordinator,
                        "pool",
                        description,
                    )
                )
        
        # Add user sensors (from primary user)
        if "user" not in created_sensors:
            user = coordinator.get_primary_user()
            if user:
                _LOGGER.info("Creating user sensors")
                created_sensors.add("user")
                
                for description in USER_SENSOR_TYPES:
                    new_entities.append(
                        CKPoolSensor(
                            coordinator,
                            "user",
                            description,
                        )
                    )
            else:
                _LOGGER.debug("No user data available yet")
        
        if new_entities:
            async_add_entities(new_entities)

    # Add listener and trigger initial creation
    coordinator.async_add_listener(async_add_pool_sensors)
    async_add_pool_sensors()


class CKPoolSensor(CoordinatorEntity, SensorEntity):
    """Representation of a CKPool sensor."""

    entity_description: CKPoolSensorEntityDescription

    def __init__(
        self,
        coordinator: Any,
        sensor_type: str,
        description: CKPoolSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._sensor_type = sensor_type
        
        # Entity ID
        self._attr_unique_id = f"ckpool_{sensor_type}_{description.key}"
        
        # Device info - all sensors belong to the pool device
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"ckpool_{coordinator.host}_{coordinator.port}")},
            "name": "CKPool",
            "manufacturer": "ckpool",
            "model": "ckpool (ckstats)",
        }
        
        # Entity name
        self._attr_name = f"CKPool {description.name}"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        if self._sensor_type == "user":
            return self.coordinator.get_primary_user() is not None
        else:
            return bool(self.coordinator.pool_data)

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if self._sensor_type == "user":
            # User sensor - get primary user data
            user = self.coordinator.get_primary_user()
            data = user
            if not data:
                return None
        else:
            # Pool sensor - get pool data
            data = self.coordinator.pool_data
            if not data:
                return None
        
        return self.entity_description.value_fn(data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional attributes."""
        if self.entity_description.attr_fn is None:
            return None
        
        if self._sensor_type == "user":
            user = self.coordinator.get_primary_user()
            if not user:
                return None
            data = user
        else:
            data = self.coordinator.pool_data
            if not data:
                return None
        
        return self.entity_description.attr_fn(data)