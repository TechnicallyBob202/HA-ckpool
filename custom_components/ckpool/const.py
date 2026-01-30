"""Constants for the CKPool integration."""
from typing import Final

DOMAIN: Final = "ckpool"

# ============================================================================
# Pool (ckstats) HTTP CONFIGURATION
# ============================================================================

POOL_DEFAULT_HOST: Final = "localhost"
POOL_DEFAULT_PORT: Final = 5000
POOL_DEFAULT_POLL_INTERVAL: Final = 300  # 5 minutes for pool stats

POOL_API_CURRENT_ENDPOINT: Final = "/pool/current"
POOL_API_HISTORY_ENDPOINT: Final = "/pool/history"
POOL_API_UPTIME_ENDPOINT: Final = "/pool/uptime"
POOL_API_USERS_ENDPOINT: Final = "/users"
POOL_API_WORKERS_ENDPOINT: Final = "/workers"
POOL_API_HEALTH_ENDPOINT: Final = "/health"

# ============================================================================
# CONFIG FLOW KEYS
# ============================================================================

CONF_POOL_HOST: Final = "pool_host"
CONF_POOL_PORT: Final = "pool_port"

# ============================================================================
# PLATFORMS
# ============================================================================

PLATFORMS: Final = ["sensor"]

# ============================================================================
# DEVICE INFO
# ============================================================================

MANUFACTURER_CKPOOL: Final = "ckpool"
MODEL_CKPOOL: Final = "ckpool (ckstats)"