"""
<plugin key="ShellyEM3Absolute" name="Shelly EM3 Absolute Values" author="Mibeus" version="1.0.0" wikilink="https://github.com/Mibeus/em3_absolute_value">
    <description>
        <h2>Shelly EM3 Absolute Energy Values Plugin</h2><br/>
        This plugin reads absolute energy counter values directly from Shelly EM3 MQTT topics.<br/>
        <br/>
        <h3>Features</h3>
        <ul style="list-style-type:square">
            <li>Reads total energy consumption from each phase (L1, L2, L3)</li>
            <li>Calculates and displays total consumption (L1+L2+L3)</li>
            <li>Shows absolute values from EM3 device (not daily deltas)</li>
            <li>Auto-creates kWh counter devices</li>
        </ul>
        <h3>Configuration</h3>
        <ul style="list-style-type:square">
            <li>MQTT Server: IP address or hostname of your MQTT broker</li>
            <li>MQTT Port: Usually 1883</li>
            <li>Device ID: Your Shelly EM3 device ID (e.g., shellyem3-485519D782ED)</li>
        </ul>
    </description>
    <params>
        <param field="Address" label="MQTT Server" width="200px" required="true" default="localhost"/>
        <param field="Port" label="MQTT Port" width="100px" required="true" default="1883"/>
        <param field="Username" label="MQTT Username" width="200px" required="false" default=""/>
        <param field="Password" label="MQTT Password" width="200px" required="false" default="" password="true"/>
        <param field="Mode1" label="Device ID" width="300px" required="true" default="shellyem3-485519D782ED"/>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal" default="true"/>
            </options>
        </param>
    </params>
</plugin>
"""
# Author: Mibeus

import Domoticz
import json
import time

try:
    import paho.mqtt.client as mqtt
except ImportError:
    Domoticz.Error("paho-mqtt library not found. Install it with: pip3 install paho-mqtt")

class BasePlugin:
    enabled = False
    mqttClient = None

    # Device units
    UNIT_L1_TOTAL = 1
    UNIT_L2_TOTAL = 2
    UNIT_L3_TOTAL = 3
    UNIT_TOTAL_ALL = 4

    # MQTT topics
    mqtt_topics = []
    device_id = ""

    # Energy values (in Wh)
    l1_total = 0.0
    l2_total = 0.0
    l3_total = 0.0

    def __init__(self):
        return

    def onStart(self):
        Domoticz.Debug("onStart called")

        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)

        Domoticz.Log("Shelly EM3 Absolute Values Plugin starting...")

        self.device_id = Parameters["Mode1"]
        Domoticz.Log(f"Device ID: {self.device_id}")

        if self.UNIT_L1_TOTAL not in Devices:
            Domoticz.Device(Name="EM3 L1 Absolute", Unit=self.UNIT_L1_TOTAL,
                          Type=243, Subtype=29, Options={'EnergyMeterMode': '0'}, Used=1).Create()
            Domoticz.Log("Created L1 Absolute device (From Device mode)")

        if self.UNIT_L2_TOTAL not in Devices:
            Domoticz.Device(Name="EM3 L2 Absolute", Unit=self.UNIT_L2_TOTAL,
                          Type=243, Subtype=29, Options={'EnergyMeterMode': '0'}, Used=1).Create()
            Domoticz.Log("Created L2 Absolute device (From Device mode)")

        if self.UNIT_L3_TOTAL not in Devices:
            Domoticz.Device(Name="EM3 L3 Absolute", Unit=self.UNIT_L3_TOTAL,
                          Type=243, Subtype=29, Options={'EnergyMeterMode': '0'}, Used=1).Create()
            Domoticz.Log("Created L3 Absolute device (From Device mode)")

        if self.UNIT_TOTAL_ALL not in Devices:
            Domoticz.Device(Name="EM3 Total Absolute", Unit=self.UNIT_TOTAL_ALL,
                          Type=243, Subtype=29, Options={'EnergyMeterMode': '0'}, Used=1).Create()
            Domoticz.Log("Created Total Absolute device (From Device mode)")

        self.mqtt_topics = [
            f"shellies/{self.device_id}/emeter/0/total",
            f"shellies/{self.device_id}/emeter/1/total",
            f"shellies/{self.device_id}/emeter/2/total"
        ]

        self.mqttClient = mqtt.Client()

        if Parameters["Username"] != "":
            self.mqttClient.username_pw_set(Parameters["Username"], Parameters["Password"])

        self.mqttClient.on_connect = self.onMQTTConnect
        self.mqttClient.on_message = self.onMQTTMessage
        self.mqttClient.on_disconnect = self.onMQTTDisconnect

        try:
            self.mqttClient.connect(Parameters["Address"], int(Parameters["Port"]), 60)
            self.mqttClient.loop_start()
            Domoticz.Log(f"Connected to MQTT broker at {Parameters['Address']}:{Parameters['Port']}")
        except Exception as e:
            Domoticz.Error(f"Failed to connect to MQTT broker: {str(e)}")

    def onStop(self):
        Domoticz.Debug("onStop called")
        if self.mqttClient:
            self.mqttClient.loop_stop()
            self.mqttClient.disconnect()
        Domoticz.Log("Shelly EM3 Absolute Values Plugin stopped")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug(f"onCommand called for Unit {Unit}: Command '{Command}', Level: {Level}")

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug("onNotification called")

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called")
        if self.mqttClient and not self.mqttClient.is_connected():
            try:
                self.mqttClient.reconnect()
                Domoticz.Log("Reconnected to MQTT broker")
            except Exception as e:
                Domoticz.Error(f"Failed to reconnect to MQTT broker: {str(e)}")

    def onMQTTConnect(self, client, userdata, flags, rc):
        if rc == 0:
            Domoticz.Log("Successfully connected to MQTT broker")
            for topic in self.mqtt_topics:
                client.subscribe(topic)
                Domoticz.Log(f"Subscribed to topic: {topic}")
        else:
            Domoticz.Error(f"Failed to connect to MQTT broker with result code {rc}")

    def onMQTTMessage(self, client, userdata, message):
        try:
            topic = message.topic
            payload = message.payload.decode('utf-8')

            Domoticz.Debug(f"MQTT Message - Topic: {topic}, Payload: {payload}")

            try:
                value_wh = float(payload)
            except ValueError:
                Domoticz.Error(f"Invalid payload value: {payload}")
                return

            if "/emeter/0/total" in topic:
                self.l1_total = value_wh
                self.updateDevice(self.UNIT_L1_TOTAL, value_wh)
                Domoticz.Debug(f"L1 Total: {value_wh} Wh")

            elif "/emeter/1/total" in topic:
                self.l2_total = value_wh
                self.updateDevice(self.UNIT_L2_TOTAL, value_wh)
                Domoticz.Debug(f"L2 Total: {value_wh} Wh")

            elif "/emeter/2/total" in topic:
                self.l3_total = value_wh
                self.updateDevice(self.UNIT_L3_TOTAL, value_wh)
                Domoticz.Debug(f"L3 Total: {value_wh} Wh")

            total_wh = self.l1_total + self.l2_total + self.l3_total
            self.updateDevice(self.UNIT_TOTAL_ALL, total_wh)
            Domoticz.Debug(f"Total All Phases: {total_wh} Wh ({total_wh/1000:.3f} kWh)")

        except Exception as e:
            Domoticz.Error(f"Error processing MQTT message: {str(e)}")

    def onMQTTDisconnect(self, client, userdata, rc):
        if rc != 0:
            Domoticz.Error(f"Unexpected MQTT disconnection (rc={rc}). Will auto-reconnect.")
        else:
            Domoticz.Log("Disconnected from MQTT broker")

    def updateDevice(self, Unit, value_wh):
        if Unit not in Devices:
            Domoticz.Error(f"Device unit {Unit} does not exist")
            return

        value_kwh = value_wh / 1000.0
        sValue = f"0;{int(value_wh)}"
        Devices[Unit].Update(nValue=0, sValue=sValue)
        Domoticz.Debug(f"Updated {Devices[Unit].Name}: {value_kwh:.3f} kWh (raw: {value_wh} Wh)")

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()
