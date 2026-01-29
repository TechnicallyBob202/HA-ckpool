"""Sensor platform for Pool Coordinator integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class PoolCoordinatorSensorEntityDescriptionMixin:
    """Mixin for required keys."""

    value_fn: Callable[[dict[str, Any]], Any]


@dataclass
class PoolCoordinatorSensorEntityDescription(
    SensorEntityDescription, PoolCoordinatorSensorEntityDescriptionMixin
):
    """Describes Pool Coordinator sensor entity."""

    attr_fn: Callable[[dict[str, Any]], dict[str, Any]] | None = None


# ============================================================================
# Pool Sensor Types (ckstats API)
# ============================================================================

POOL_SENSOR_TYPES: tuple[PoolCoordinatorSensorEntityDescription, ...] = (
    PoolCoordinatorSensorEntityDescription(
        key="pool_id",
        name="Pool ID",
        icon="mdi:identifier",
        value_fn=lambda data: data.get("id", "Unknown"),
    ),
    PoolCoordinatorSensorEntityDescription(
        key="pool_runtime",
        name="Pool Runtime",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:clock-outline",
        value_fn=lambda data: data.get("runtime", 0),
    ),
    PoolCoordinatorSensorEntityDescription(
        key="pool_timestamp",
        name="Pool Last Update",
        icon="mdi:clock-check-outline",
        value_fn=lambda data: data.get("timestamp", "Unknown"),
    ),
    PoolCoordinatorSensorEntityDescription(
        key="pool_users",
        name="Connected Users",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:account-multiple",
        value_fn=lambda data: data.get("users", 0),
    ),
    PoolCoordinatorSensorEntityDescription(
        key="pool_workers",
        name="Connected Workers",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:lan-connect",
        value_fn=lambda data: data.get("workers", 0),
    ),
    PoolCoordinatorSensorEntityDescription(
        key="pool_idle",
        name="Idle Workers",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:sleep",
        value_fn=lambda data: data.get("idle", 0),
    ),
    PoolCoordinatorSensorEntityDescription(
        key="pool_disconnected",
        name="Disconnected Workers",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:lan-disconnect",
        value_fn=lambda data: data.get("disconnected", 0),
    ),
    PoolCoordinatorSensorEntityDescription(
        key="pool_hashrate_1m",
        name="Pool Hashrate (1m)",
        native_unit_of_measurement="H/s",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:speedometer",
        value_fn=lambda data: data.get("hashrate1m", 0),
    ),
    PoolCoordinatorSensorEntityDescription(
        key="pool_hashrate_5m",
        name="Pool Hashrate (5m)",
        native_unit_of_measurement="H/s",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:speedometer",
        value_fn=lambda data: data.get("hashrate5m", 0),
    ),
    PoolCoordinatorSensorEntityDescription(
        key="pool_hashrate_15m",
        name="Pool Hashrate (15m)",
        native_unit_of_measurement="H/s",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:speedometer",
        value_fn=lambda data: data.get("hashrate15m", 0),
    ),
    PoolCoordinatorSensorEntityDescription(
        key="pool_hashrate_1h",
        name="Pool Hashrate (1h)",
        native_unit_of_measurement="H/s",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:speedometer",
        value_fn=lambda data: data.get("hashrate1hr", 0),
    ),
    PoolCoordinatorSensorEntityDescription(
        key="pool_hashrate_6h",
        name="Pool Hashrate (6h)",
        native_unit_of_measurement="H/s",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:speedometer",
        value_fn=lambda data: data.get("hashrate6hr", 0),
    ),
    PoolCoordinatorSensorEntityDescription(
        key="pool_hashrate_1d",
        name="Pool Hashrate (24h)",
        native_unit_of_measurement="H/s",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:speedometer",
        value_fn=lambda data: data.get("hashrate1d", 0),
    ),
    PoolCoordinatorSensorEntityDescription(
        key="pool_hashrate_7d",
        name="Pool Hashrate (7d)",
        native_unit_of_measurement="H/s",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:speedometer",
        value_fn=lambda data: data.get("hashrate7d", 0),
    ),
    PoolCoordinatorSensorEntityDescription(
        key="pool_difficulty",
        name="Network Difficulty",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:target",
        value_fn=lambda data: data.get("diff", 0),
    ),
    PoolCoordinatorSensorEntityDescription(
        key="pool_best_share",
        name="Best Share Difficulty",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:star",
        value_fn=lambda data: data.get("bestshare", 0),
    ),
    PoolCoordinatorSensorEntityDescription(
        key="pool_shares_accepted",
        name="Total Shares Accepted",
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:check-circle",
        value_fn=lambda data: data.get("accepted", 0),
    ),
    PoolCoordinatorSensorEntityDescription(
        key="pool_shares_rejected",
        name="Total Shares Rejected",
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:close-circle",
        value_fn=lambda data: data.get("rejected", 0),
    ),
    PoolCoordinatorSensorEntityDescription(
        key="pool_sps_1m",
        name="Shares Per Second (1m)",
        native_unit_of_measurement="SPS",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:share",
        value_fn=lambda data: data.get("SPS1m", 0),
    ),
    PoolCoordinatorSensorEntityDescription(
        key="pool_sps_5m",
        name="Shares Per Second (5m)",
        native_unit_of_measurement="SPS",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:share",
        value_fn=lambda data: data.get("SPS5m", 0),
    ),
    PoolCoordinatorSensorEntityDescription(
        key="pool_sps_15m",
        name="Shares Per Second (15m)",
        native_unit_of_measurement="SPS",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:share",
        value_fn=lambda data: data.get("SPS15m", 0),
    ),
    PoolCoordinatorSensorEntityDescription(
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

USER_SENSOR_TYPES: tuple[PoolCoordinatorSensorEntityDescription, ...] = (
    PoolCoordinatorSensorEntityDescription(
        key="user_address",
        name="User Address",
        icon="mdi:wallet",
        value_fn=lambda data: data.get("userAddress", "Unknown"),
    ),
    PoolCoordinatorSensorEntityDescription(
        key="user_hashrate_1h",
        name="User Hashrate (1h)",
        native_unit_of_measurement="H/s",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:speedometer",
        value_fn=lambda data: data.get("hashrate1hr", 0),
    ),
    PoolCoordinatorSensorEntityDescription(
        key="user_hashrate_1d",
        name="User Hashrate (24h)",
        native_unit_of_measurement="H/s",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:speedometer",
        value_fn=lambda data: data.get("hashrate1d", 0),
    ),
    PoolCoordinatorSensorEntityDescription(
        key="user_shares",
        name="User Total Shares",
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:share",
        value_fn=lambda data: data.get("shares", 0),
    ),
    PoolCoordinatorSensorEntityDescription(
        key="user_best_share",
        name="User Best Share Difficulty",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:star",
        value_fn=lambda data: data.get("bestEver", 0),
    ),
    PoolCoordinatorSensorEntityDescription(
        key="user_workers",
        name="User Worker Count",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:lan-connect",
        value_fn=lambda data: data.get("workerCount", 0),
    ),
    PoolCoordinatorSensorEntityDescription(
        key="user_last_share",
        name="User Last Share Time",
        icon="mdi:clock-outline",
        value_fn=lambda data: data.get("lastShare", "Never"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors for pool and user data."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    coordinator = entry_data["coordinator"]
    
    # Track which entity groups we've created
    created_entities: set[str] = set()

    @callback
    def async_add_pool_and_user_sensors() -> None:
        """Add sensors for pool and user data."""
        new_entities: list[PoolCoordinatorSensor] = []
        
        # Add pool sensors (20 sensors)
        if "pool" not in created_entities:
            _LOGGER.info("Creating pool sensors")
            created_entities.add("pool")
            
            for description in POOL_SENSOR_TYPES:
                new_entities.append(
                    PoolCoordinatorSensor(
                        coordinator,
                        "pool",
                        description,
                    )
                )
        
        # Add user sensors (7 sensors from primary user)
        if "user" not in created_entities:
            user = coordinator.get_primary_user()
            if user:
                _LOGGER.info("Creating user sensors")
                created_entities.add("user")
                
                for description in USER_SENSOR_TYPES:
                    new_entities.append(
                        PoolCoordinatorSensor(
                            coordinator,
                            "user",
                            description,
                        )
                    )
            else:
                _LOGGER.debug("No user data available yet")
        
        if new_entities:
            async_add_entities(new_entities)

    coordinator.async_add_listener(async_add_pool_and_user_sensors)
    async_add_pool_and_user_sensors()


class PoolCoordinatorSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Pool Coordinator sensor."""

    entity_description: PoolCoordinatorSensorEntityDescription

    def __init__(
        self,
        coordinator: Any,
        entity_type: str,
        description: PoolCoordinatorSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._entity_type = entity_type
        
        # Entity ID
        self._attr_unique_id = f"pool_coordinator_{entity_type}_{description.key}"
        
        # Device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, "pool")},
            "name": "Mining Pool (ckpool)",
            "manufacturer": "ckpool",
            "model": "ckpool (ckstats)",
        }
        
        # Entity name
        if entity_type == "user":
            self._attr_name = f"User {description.name}"
        else:
            self._attr_name = f"Pool {description.name}"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        if self._entity_type == "user":
            return self.coordinator.get_primary_user() is not None
        else:
            return bool(self.coordinator.pool_data)

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if self._entity_type == "user":
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
        
        if self._entity_type == "user":
            user = self.coordinator.get_primary_user()
            if not user:
                return None
            data = user
        else:
            data = self.coordinator.pool_data
            if not data:
                return None
        
        return self.entity_description.attr_fn(data)
