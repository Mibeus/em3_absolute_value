# Shelly EM3 Absolute Values - Domoticz Plugin

Domoticz plugin for Shelly EM3 3-phase energy meter that reads absolute kWh values via MQTT.

## Features
- Reads total energy consumption from each phase (L1, L2, L3)
- Calculates and displays total consumption (L1+L2+L3)
- Shows absolute values from EM3 device (not daily deltas)
- Auto-creates kWh counter devices in Domoticz

## Requirements
- Domoticz with Python plugin support enabled
- paho-mqtt Python library: `pip3 install paho-mqtt`
- Shelly EM3 with MQTT enabled

## Installation

1. Clone into Domoticz plugins directory:
```bash
cd /path/to/domoticz/userdata/plugins
git clone https://github.com/Mibeus/em3_absolute_value shellyem3_absolute
pip3 install paho-mqtt
```

2. Restart Domoticz

3. Go to **Setup → Hardware → Add** and select `Shelly EM3 Absolute Values`

## Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| MQTT Server | IP address of your MQTT broker | localhost |
| MQTT Port | MQTT broker port | 1883 |
| MQTT Username | Optional username | |
| MQTT Password | Optional password | |
| Device ID | Shelly EM3 device ID | shellyem3-485519D782ED |

## Created Devices

The plugin automatically creates 4 devices in Domoticz:
- **EM3 L1 Absolute** - Phase 1 total energy (kWh)
- **EM3 L2 Absolute** - Phase 2 total energy (kWh)
- **EM3 L3 Absolute** - Phase 3 total energy (kWh)
- **EM3 Total Absolute** - Total energy all phases (kWh)

## Docker installation

If running Domoticz in Docker:
```bash
cd /path/to/domoticz/userdata/plugins
git clone https://github.com/Mibeus/em3_absolute_value shellyem3_absolute
docker exec domoticz pip3 install paho-mqtt --break-system-packages
docker restart domoticz
```
