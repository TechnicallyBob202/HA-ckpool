# Pool Coordinator - Quick Start Guide

## 🚀 30 Second Setup

### For ckpool Users

1. **Add Integration:**
   - Settings → Devices & Services → "+ Add Integration"
   - Search "Pool Coordinator"

2. **Configure:**
   - Pool Host: `localhost` (or your pool server IP)
   - Pool Port: `5000` (default ckstats port)
   - Click Submit

3. **Done!**
   - Sensors appear within 30 seconds
   - All pool metrics start flowing in

## 📊 What You Get

### Pool Metrics
- ⚡ Pool hashrate (1m, 5m, 15m, 1h, 6h, 24h, 7d)
- 👥 User and worker counts
- 📈 Shares per second metrics
- 💎 Best share difficulty
- ⏱️ Pool uptime and runtime
- 🔗 Network difficulty

### Per Primary User
- ⚡ User hashrate (1h, 24h)
- 📊 User total shares
- 💎 User best share difficulty
- 🖥️ Worker count
- ⏰ Last share timestamp

## 🔍 Finding Entity IDs

In Home Assistant:

1. Go to Developer Tools → States
2. Search for "pool_coordinator"
3. Click to see all sensors
4. Copy entity ID (e.g., `sensor.pool_coordinator_pool_pool_hashrate_1h`)

## 🎯 First Automation

### High Hashrate Alert

```yaml
alias: Pool Coordinator - High Hashrate
trigger:
  - platform: numeric_state
    entity_id: sensor.pool_coordinator_pool_pool_hashrate_1h
    above: 500000000000  # 500 GH/s
action:
  - service: notify.mobile_app_your_phone
    data:
      title: "⚡ High Pool Hashrate!"
      message: "Current: {{ trigger.to_state.state | float(0) / 1e9 | round(2) }} GH/s"
```

### Pool Offline Alert

```yaml
alias: Pool Coordinator - Offline
trigger:
  - platform: state
    entity_id: sensor.pool_coordinator_pool_pool_hashrate_1m
    to: "unavailable"
    for:
      minutes: 5
action:
  - service: notify.mobile_app_your_phone
    data:
      title: "❌ Pool Offline!"
      message: "No pool data for 5 minutes"
```

## ⚡ Pro Tips

### Total Pool Efficiency

Track efficiency across all metrics:

```yaml
template:
  - sensor:
      - name: "Pool Hashrate GH/s"
        unique_id: pool_hashrate_gh
        unit_of_measurement: "GH/s"
        state: >
          {{ (states('sensor.pool_coordinator_pool_pool_hashrate_1h') | float(0) / 1e9) | round(3) }}
```

### Worker Health Check

Monitor worker status:

```yaml
template:
  - binary_sensor:
      - name: "Pool Workers Offline"
        unique_id: pool_workers_down
        device_class: problem
        state: >
          {{ (states('sensor.pool_coordinator_pool_pool_disconnected') | int(0)) > 5 }}
```

## 🆘 Quick Troubleshooting

### API not responding?

```bash
# Test ckstats endpoint
curl http://localhost:5000/api/pool/current

# Should return JSON with pool stats
```

### Port blocked?

```bash
# Check if port is accessible
netstat -tlnp | grep 5000

# Open firewall if needed
sudo ufw allow 5000
```

### Sensors say "unavailable"?

- Wait 30 seconds for first refresh
- Verify ckpool is running
- Check Home Assistant logs: Settings → System → Logs
- Verify API endpoints return valid JSON

## 📚 Next Steps

1. **Read Full Docs**: See README.md
2. **Create Automations**: Use examples above
3. **Build Dashboard**: Add visualizations
4. **Monitor Workers**: Track individual miners via user stats

## 🎯 Common Setups

### Single Pool Server
```
Config: localhost:5000
Result: 1 device, 27 sensors
Updates: Every 5 minutes
```

### Remote Pool Server
```
Config: pool.example.com:5000
Result: 1 device, 27 sensors
Updates: Every 5 minutes
```

### Multiple Pools (Future)
```
Add multiple Pool Coordinator instances
One per pool server
Result: Full multi-pool visibility!
```

## ✨ Integration Highlights

| Feature | Pool Coordinator |
|---------|------------------|
| **Update Rate** | 🔄 Every 5 minutes |
| **Sensor Count** | 📊 27 sensors |
| **Setup Complexity** | 🟢 Simple |
| **Network Overhead** | 📡 Minimal |
| **Data Freshness** | ⏱️ 5m delays acceptable |
| **Primary Use** | Pool + User metrics |

---

**Monitor your pool in seconds!** 🚀⛏️
