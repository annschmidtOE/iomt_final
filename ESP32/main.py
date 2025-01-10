from stepper import Stepper
from machine import Pin
import utime  
import network
from umqtt.simple import MQTTClient

WIFI_SSID = "gruppe7"
WIFI_PASSWORD = "iot3anna"

MQTT_BROKER = "172.20.10.5"
MQTT_TOPIC = "pilledata"
MQTT_CLIENT_ID = "ESP32Client"

in1 = Pin(16, Pin.OUT)
in2 = Pin(17, Pin.OUT)
in3 = Pin(5, Pin.OUT)
in4 = Pin(18, Pin.OUT)
s1 = Stepper.create(in1, in2, in3, in4, delay=1)

mos1 = Pin(22, Pin.OUT)
mos2 = Pin(23, Pin.OUT)
mos3 = Pin(4, Pin.OUT)
mos1.off()
mos2.off()
mos3.off()

led_green = Pin(27, Pin.OUT)
led_red = Pin(26, Pin.OUT)

pille1 = 0
pille2 = 0
pille3 = 0

def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    print("Forbinder til Wi-Fi...")
    while not wlan.isconnected():
        utime.sleep(1)  
    print("Wi-Fi forbundet:", wlan.ifconfig())

def send_mqtt_message(message):
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
        client.connect()
        print(f"Forbundet til MQTT broker: {MQTT_BROKER}")
        client.publish(MQTT_TOPIC, str(message))  
        print(f"Besked sendt: {message}")
        client.disconnect()
    except Exception as e:
        print(f"Fejl ved MQTT: {e}")

try:
    connect_to_wifi()
    while True:
        mos1.on()
        led_green.on()
        print("MOS1 kører")
        pille1 += 1
        print(f"Pille1 tæller: {pille1}")
        s1.step(1000, 1)
        send_mqtt_message(pille1)  
        mos1.off()
        led_green.off()
        led_red.on()
        print("MOS1 stop")
        utime.sleep(0.2)
        led_red.off()

        mos2.on()
        led_green.on()
        print("MOS2 kører")
        pille2 += 1
        print(f"Pille2 tæller: {pille2}")
        s1.step(1000, 1)
        #send_mqtt_message(pille2)  
        mos2.off()
        led_green.off()
        utime.sleep(0.2)
        led_red.on()
        print("MOS2 stop")
        utime.sleep(2)
        led_red.off()
        
        mos3.on()
        led_green.on()
        print("MOS3 kører")
        pille3 += 1
        print(f"Pille3 tæller: {pille2}")
        s1.step(1000, 1)
        #send_mqtt_message(pille3)  
        mos3.off()
        led_green.off()
        led_red.on()
        print("MOS3 stop")
        utime.sleep(2)
        led_red.off()
except Exception as e:
    print(f"Fejl i programmet: {e}")

