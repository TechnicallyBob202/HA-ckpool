# Pool Coordinator - Home Assistant Integration

A Home Assistant custom integration for monitoring mining pool statistics (ckpool with ckstats API). Provides real-time visibility into pool-level metrics and individual user/miner performance.

## 🎯 Features

### Pool Statistics
- 📊 **Real-time Pool Metrics** - Current pool hashrate, user count, worker count
- 📈 **Multi-timeframe Hashrate** - 1m, 5m, 15m, 1h, 6h, 24h, 7d averages
- 💾 **Share Statistics** - Accepted/rejected shares, shares per second metrics
- ⛏️ **Network Metrics** - Network difficulty, best share difficulty
- ⏱️ **Pool Uptime** - Runtime and last update timestamp
- 🔄 **Worker Status** - Connected, idle, and disconnected worker counts

### User/Miner Statistics
- 👤 **User Address** - Mining address for primary user
- ⚡ **User Hashrate** - 1h and 24h hashrate for primary user
- 💎 **User Shares** - Total shares and best share difficulty
- 🖥️ **Worker Count** - Number of workers connected for this user
- ⏰ **Last Share Time** - When the user last submitted a valid share

### Architecture
- 🏗️ **Proper HA Integration** - Uses DataUpdateCoordinator and config entries
- 🔧 **Simple Configuration** - Easy setup via Home Assistant UI
- 📱 **Full Device Registry** - Pool appears as device with sensors
- 🌍 **Community Ready** - Well-documented, maintainable codebase

## 📦 Installation

### Manual Installation

1. **Create directory structure:**
   ```bash
   mkdir -p ~/.homeassistant/custom_components/pool_coordinator
   ```

2. **Copy integration files:**
   ```bash
   cp -r custom_components/pool_coordinator/* \
     ~/.homeassistant/custom_components/pool_coordinator/
   ```

3. **Restart Home Assistant**
   - Settings → System → Restart

4. **Add Integration:**
   - Settings → Devices & Services
   - Click "+ Add Integration"
   - Search for "Pool Coordinator"
   - Configure host and port

### File Structure

```
custom_components/pool_coordinator/
├── __init__.py                  # Entry point
├── const.py                     # Constants
├── config_flow.py               # Configuration flow
├── sensor.py                    # Sensor platform
├── strings.json                 # UI text localization
├── manifest.json                # Integration metadata
└── coordinator_pool.py          # ckstats API coordinator
```

## ⚙️ Configuration

1. After adding the integration, configure:
   - **Pool Host**: Hostname or IP of your ckpool server (default: localhost)
   - **Pool Port**: Port for ckstats API (default: 5000)
   - **Test Connection**: Integration will verify connectivity

2. Click Submit

3. Sensors will appear within 30 seconds

**What you need:**
- ckpool mining pool software running with ckstats API enabled
- ckstats API accessible at `http://<host>:<port>/api`
- Network connectivity between Home Assistant and pool server

## 📊 Sensors

### Pool Sensors (20 Total)

| Sensor | Description | Unit |
|--------|-------------|------|
| Pool ID | Unique pool identifier | - |
| Pool Runtime | How long pool has been running | Seconds |
| Pool Last Update | When stats were last updated | Timestamp |
| Connected Users | Number of users with active connections | - |
| Connected Workers | Total number of connected workers | - |
| Idle Workers | Number of idle workers | - |
| Disconnected Workers | Number of disconnected workers | - |
| Pool Hashrate (1m) | Average hashrate last 1 minute | H/s |
| Pool Hashrate (5m) | Average hashrate last 5 minutes | H/s |
| Pool Hashrate (15m) | Average hashrate last 15 minutes | H/s |
| Pool Hashrate (1h) | Average hashrate last 1 hour | H/s |
| Pool Hashrate (6h) | Average hashrate last 6 hours | H/s |
| Pool Hashrate (24h) | Average hashrate last 24 hours | H/s |
| Pool Hashrate (7d) | Average hashrate last 7 days | H/s |
| Network Difficulty | Current Bitcoin network difficulty | - |
| Best Share Difficulty | Best share ever submitted to pool | - |
| Total Shares Accepted | All-time accepted shares | - |
| Total Shares Rejected | All-time rejected shares | - |
| Shares Per Second (1m) | Share rate last 1 minute | SPS |
| Shares Per Second (5m) | Share rate last 5 minutes | SPS |
| Shares Per Second (15m) | Share rate last 15 minutes | SPS |
| Shares Per Second (1h) | Share rate last 1 hour | SPS |

### User Sensors (7 Total - From Primary User)

| Sensor | Description | Unit |
|--------|-------------|------|
| User Address | Bitcoin address for primary user | - |
| User Hashrate (1h) | User's hashrate last 1 hour | H/s |
| User Hashrate (24h) | User's hashrate last 24 hours | H/s |
| User Total Shares | Total shares submitted by user | - |
| User Best Share Difficulty | Best share difficulty from user | - |
| User Worker Count | Number of workers this user has | - |
| User Last Share Time | When user last submitted a share | Timestamp |

**Total: 27 sensors per pool instance**

## 🤖 Automation Examples

### High Hashrate Alert

```yaml
automation:
  - alias: "Pool Coordinator - Pool Hashrate Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.pool_coordinator_pool_pool_hashrate_1h
        above: 500000000000  # 500 GH/s
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "⚡ High Pool Hashrate"
          message: "Pool hashrate: {{ trigger.to_state.state | float(0) / 1e9 | round(2) }} GH/s"
```

### Pool Offline Alert

```yaml
automation:
  - alias: "Pool Coordinator - Pool Offline"
    trigger:
      - platform: state
        entity_id: sensor.pool_coordinator_pool_pool_hashrate_1m
        to: "unavailable"
        for:
          minutes: 5
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "❌ Pool Offline"
          message: "Pool statistics unavailable for 5+ minutes"
```

### User Statistics Report

```yaml
automation:
  - alias: "Pool Coordinator - User Stats Daily"
    trigger:
      - platform: time
        at: "09:00:00"
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "📊 24h Mining Summary"
          message: >
            Hashrate: {{ states('sensor.pool_coordinator_user_user_hashrate_1d') | float(0) / 1e9 | round(2) }} GH/s
            Shares: {{ states('sensor.pool_coordinator_user_user_total_shares') }}
            Workers: {{ states('sensor.pool_coordinator_user_user_worker_count') }}
```

## 📈 Template Sensors

### Pool Hashrate in GH/s

```yaml
template:
  - sensor:
      - name: "Pool Hashrate (GH/s)"
        unique_id: pool_coordinator_hashrate_gh
        unit_of_measurement: "GH/s"
        state_class: measurement
        state: >
          {{ (states('sensor.pool_coordinator_pool_pool_hashrate_1h') | float(0) / 1e9) | round(3) }}
        icon: mdi:speedometer
```

### Pool Efficiency (Shares Per TH)

```yaml
template:
  - sensor:
      - name: "Pool SPS Efficiency"
        unique_id: pool_coordinator_sps_per_th
        unit_of_measurement: "SPS/TH"
        state: >
          {% set hashrate_gh = (states('sensor.pool_coordinator_pool_pool_hashrate_1h') | float(0) / 1e9) %}
          {% set sps = states('sensor.pool_coordinator_pool_pool_sps_1h') | float(0) %}
          {% if hashrate_gh > 0 %}
            {{ (sps / hashrate_gh / 1000) | round(4) }}
          {% else %}
            0
          {% endif %}
        icon: mdi:chart-line
```

## 🔧 Troubleshooting

### "Failed to connect to pool API"

1. **Verify ckstats API is running:**
   ```bash
   curl http://localhost:5000/api/health
   ```

2. **Check port is correct:**
   - Default ckstats port: 5000
   - Verify in your ckpool configuration

3. **Check firewall:**
   ```bash
   sudo ufw allow 5000
   ```

4. **Verify network connectivity:**
   ```bash
   ping pool-server-ip
   ```

### Sensors Show "Unavailable"

- Wait 30 seconds for first data fetch
- Check Home Assistant logs: Settings → System → Logs
- Verify pool server is running and responsive
- Ensure `/api/pool/current` returns valid JSON

### No User Sensors Appearing

- Pool must have at least one active user
- User data comes from `/api/users` endpoint
- Verify endpoint returns non-empty list:
  ```bash
  curl http://localhost:5000/api/users
  ```

### Reinstalling

1. Settings → Integrations → Pool Coordinator → Delete
2. Delete `custom_components/pool_coordinator` folder
3. Restart Home Assistant
4. Re-add the integration

## 🏗️ Architecture

### Data Flow
```
ckpool/ckstats API
    ↓
PoolCoordinator (5 minute polling)
    ├─ /api/pool/current → pool_data
    └─ /api/users → users_data[0] (primary user)
    ↓
Home Assistant sensors update
```

### Update Interval
- **Poll Frequency**: 5 minutes (configurable)
- **Timeout**: 10 seconds per request
- **Health Check**: On startup only

## 📝 Development

### Adding New Pool Sensors

Edit `POOL_SENSOR_TYPES` in `sensor.py`:

```python
PoolCoordinatorSensorEntityDescription(
    key="my_metric",
    name="My Metric",
    native_unit_of_measurement="unit",
    state_class=SensorStateClass.MEASUREMENT,
    icon="mdi:icon",
    value_fn=lambda data: data.get("api_field", 0),
),
```

### Modifying Poll Interval

Edit `const.py`:
```python
POOL_DEFAULT_POLL_INTERVAL: Final = 300  # Change 300 to desired seconds
```

### Adding New API Endpoints

1. Add endpoint constant in `const.py`:
   ```python
   POOL_API_NEW_ENDPOINT: Final = "/new/endpoint"
   ```

2. Fetch in `coordinator_pool.py`:
   ```python
   new_data = await self._fetch_api(POOL_API_NEW_ENDPOINT)
   ```

3. Create sensors using the data

## 📚 References

- **ckpool Documentation**: https://github.com/ckolivas/ckpool
- **ckstats API**: https://github.com/ckolivas/ckpool/blob/master/docs/API.md
- **Home Assistant Docs**: https://developers.home-assistant.io/
- **Home Assistant Community**: https://community.home-assistant.io/

## 📄 License

MIT License - See LICENSE file

## 🙋 Support

- Open an issue on GitHub
- Check existing issues/discussions first
- Include relevant logs from Settings → System → Logs
- Provide your HA version and integration version

## 🔄 Changelog

### v1.0.0 (2025-01-29)
- ✅ Initial release
- ✅ Pool statistics monitoring (20 sensors)
- ✅ User/miner statistics (7 sensors)
- ✅ ckstats API integration
- ✅ Configurable polling interval

---

**Monitor your mining pool!** 🚀⛏️
