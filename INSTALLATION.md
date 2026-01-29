# Pool Coordinator - Installation Guide

## Prerequisites

- Home Assistant 2024.1.0 or newer
- ckpool mining pool with ckstats API enabled
- Network access from Home Assistant to pool server
- SSH access to Home Assistant (for manual installation)

## Installation Methods

### Method 1: Manual Installation

**Step 1: Connect to Home Assistant**

```bash
# Via SSH
ssh -i your_key.pem root@homeassistant.local
# Or: ssh username@homeassistant.local

# Navigate to config
cd ~/.homeassistant
```

**Step 2: Create Directory**

```bash
mkdir -p custom_components/pool_coordinator
cd custom_components/pool_coordinator
```

**Step 3: Copy Files**

Option A: Using Git
```bash
git clone https://github.com/TechnicallyBob202/HA-pool-coordinator.git
cp HA-pool-coordinator/custom_components/pool_coordinator/* ./
```

Option B: Using SCP (from your computer)
```bash
scp -r custom_components/pool_coordinator/* \
  user@homeassistant.local:~/.homeassistant/custom_components/pool_coordinator/
```

**Step 4: Verify Installation**

```bash
ls -la ~/.homeassistant/custom_components/pool_coordinator/

# Should show:
# __init__.py
# config_flow.py
# const.py
# coordinator_pool.py
# manifest.json
# sensor.py
# strings.json
```

**Step 5: Restart Home Assistant**

- Settings → System → Restart Home Assistant
- Or via command: `systemctl restart homeassistant`

**Step 6: Add Integration**

- Settings → Devices & Services
- Click "+ Add Integration"
- Search for "Pool Coordinator"
- Enter your pool server details
- Click Submit

### Method 2: Docker Installation

**If using Docker with volume mount:**

```bash
# In docker-compose.yml or docker run command:
volumes:
  - ./config:/config

# Copy integration
cp -r custom_components/pool_coordinator ./config/custom_components/

# Restart container
docker restart homeassistant
```

**Docker Compose Example:**

```yaml
version: '3'
services:
  homeassistant:
    container_name: homeassistant
    image: homeassistant/home-assistant:latest
    volumes:
      - ./config:/config
      - /etc/localtime:/etc/localtime:ro
    restart: unless-stopped
```

### Method 3: Home Assistant OS (with Terminal Add-on)

**Step 1: Install Terminal & SSH Add-on**

1. Settings → Add-ons → Add-on Store
2. Search "Terminal & SSH"
3. Install and start

**Step 2: Connect via SSH**

```bash
ssh root@homeassistant.local
```

**Step 3: Download and Install**

```bash
cd /config
mkdir -p custom_components/pool_coordinator
cd custom_components/pool_coordinator

# Option A: Clone repo
git clone https://github.com/TechnicallyBob202/HA-pool-coordinator.git
cp HA-pool-coordinator/custom_components/pool_coordinator/* ./

# Option B: Download via curl (if git not available)
curl -o __init__.py https://raw.githubusercontent.com/TechnicallyBob202/HA-pool-coordinator/main/custom_components/pool_coordinator/__init__.py
# ... repeat for all files
```

**Step 4: Restart**

- In Home Assistant: Settings → System → Restart

## Network Configuration

### Pool API Access

**Verify ckstats API is accessible:**

```bash
# From HA host - test pool API
curl http://pool-server-ip:5000/api/health

# Should return HTTP 200 if healthy
```

**Allow Network Access:**

```bash
# UFW firewall (from pool server if needed)
sudo ufw allow from home-assistant-ip to any port 5000

# firewalld (from pool server if needed)
sudo firewall-cmd --add-rich-rule='rule family="ipv4" source address="ha-ip" port protocol="tcp" port="5000" accept' --permanent
```

### Localhost vs Remote

**Localhost (same server):**
```
Pool Host: localhost
Pool Port: 5000
```

**Remote Server:**
```
Pool Host: 192.168.1.50 (or hostname)
Pool Port: 5000
Verify network path is open
```

## Verification

### Check Files Are Installed

```bash
# Via SSH
ls -lah /config/custom_components/pool_coordinator/

# Should list all Python files and manifest.json
```

### Check Home Assistant Logs

```bash
# In Home Assistant:
Settings → System → Logs

# Or via SSH:
tail -f /config/home-assistant.log | grep -i pool
```

### Watch for Startup Message

```
[custom_components.pool_coordinator] Setting up Pool Coordinator integration
[custom_components.pool_coordinator] Pool API connection established: localhost:5000
```

### Verify Sensors Created

After adding integration:

1. Settings → Devices & Services
2. Look for "Pool Coordinator" entry
3. Click to expand
4. Should see 27 sensors (20 pool + 7 user)

## Troubleshooting Installation

### Integration Not Showing in Add Integration

```bash
# 1. Check file permissions
chmod -R 755 /config/custom_components/pool_coordinator/

# 2. Clear Home Assistant cache
cd /config
rm -rf __pycache__ .homeassistant_cache

# 3. Restart Home Assistant
# Then clear browser cache (Ctrl+Shift+Delete)
```

### "No module named 'pool_coordinator'"

```bash
# Check file structure
tree /config/custom_components/pool_coordinator/

# Should show __init__.py in pool_coordinator directory
# Not: /custom_components/pool_coordinator/pool_coordinator/__init__.py
```

### Permission Errors

```bash
# Fix permissions (if running as specific user)
sudo chown -R homeassistant:homeassistant /config/custom_components/pool_coordinator/
sudo chmod -R 755 /config/custom_components/pool_coordinator/
```

### "Failed to load custom integration pool_coordinator"

Check logs:
```bash
# View recent errors
grep -i "error" /config/home-assistant.log | tail -20

# Look for syntax errors in Python files
python3 -m py_compile /config/custom_components/pool_coordinator/*.py
```

### "Pool Connection Failed" During Setup

1. Verify ckstats API is running:
   ```bash
   curl http://localhost:5000/api/health
   ```

2. Check port is correct (default 5000)

3. Verify network connectivity:
   ```bash
   # From HA to pool server
   nc -zv pool-host 5000
   ```

4. Check firewall:
   ```bash
   # On pool server
   sudo ufw status
   sudo ufw allow 5000
   ```

## File Locations by Setup Type

| Setup Type | Config Path | Integration Path |
|-----------|-------------|------------------|
| **Home Assistant OS** | `/config` | `/config/custom_components/pool_coordinator/` |
| **Home Assistant Supervised** | `/usr/share/hassio/homeassistant` | Same as above |
| **Docker** | `/config` (volume mount) | `/config/custom_components/pool_coordinator/` |
| **Manual Install** | `~/.homeassistant` | `~/.homeassistant/custom_components/pool_coordinator/` |

## Post-Installation

### Upgrade Integration

```bash
# Download latest version
cd /config/custom_components/pool_coordinator/
git pull  # or download new files

# Restart Home Assistant
# Settings → System → Restart
```

### Uninstall Integration

```bash
# Remove directory
rm -rf /config/custom_components/pool_coordinator/

# Remove from Home Assistant
# Settings → Integrations → Pool Coordinator → Delete

# Restart
# Settings → System → Restart
```

### Check Version

In Home Assistant:
- Settings → Devices & Services
- Find Pool Coordinator
- Click to expand
- Version shown at top

From command line:
```bash
grep '"version"' /config/custom_components/pool_coordinator/manifest.json
```

## Requirements

The integration has minimal dependencies:

- **aiohttp** - Already included in Home Assistant for HTTP requests
- **No additional pip packages needed**

## System Requirements

| Component | Minimum |
|-----------|---------|
| **Memory** | 50 MB for integration |
| **CPU** | Minimal (async operations) |
| **Disk** | 1 MB for integration files |
| **Network** | Access to pool API |
| **Python** | 3.11+ (included with HA) |

## ckpool Setup

Ensure ckpool is configured correctly:

**ckpool config should include:**
```
[pool]
...
ckstats = true
statsport = 5000
...
```

**Verify ckstats is running:**
```bash
# Check if ckstats is listening
netstat -tlnp | grep 5000

# Should show something like:
# tcp 0 0 0.0.0.0:5000 0.0.0.0:* LISTEN pid/ckstats
```

## Getting Help

1. **Check logs**: Settings → System → Logs
2. **Review README**: See README.md in integration
3. **Check QUICKSTART**: See QUICKSTART.md for common issues
4. **Verify API**: Ensure pool API is responding
5. **Open GitHub issue**: Include logs and configuration

## Common Issues

### "Integration not loading"
→ Check file permissions and Python syntax

### "Sensors unavailable"
→ Check pool API is accessible and responding

### "No user sensors"
→ Verify pool has at least one active user

### "High memory usage"
→ Should be minimal; check HA instance overall

---

**Installation complete!** Proceed to [QUICKSTART.md](QUICKSTART.md) to begin monitoring your pool. 🚀
