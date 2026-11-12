# CHAN Ka Ming: virtual device. Potentiometer is synthetic BPM input, not a pulse sensor.
from machine import Pin, ADC
import network
import time
import ujson
from umqtt.simple import MQTTClient

TOPIC = b'pulse-demo/7de953b4-7952-4b45-9fe8-895df7dd90fc/heart-rate'
pot = ADC(Pin(34))
pot.atten(ADC.ATTN_11DB)
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect('Wokwi-GUEST', '')
print('Pulse virtual ESP32: synthetic data only')
while not wifi.isconnected():
    time.sleep_ms(100)
print('WiFi connected; connecting to MQTT...')
client = None
while True:
    try:
        if client is None:
            client = MQTTClient('pulse-esp32-7de953b4', 'broker.hivemq.com', keepalive=30)
            client.connect()
            print('MQTT connected')
        bpm = 50 + (pot.read() * 100 // 4095)
        payload = ujson.dumps({'heart_rate': bpm, 'synthetic': True})
        client.publish(TOPIC, payload, retain=False, qos=0)
        print('PUBLISHED', bpm, 'bpm | synthetic | turn the knob to change BPM')
        time.sleep(2)
    except Exception as err:
        print('MQTT reconnecting:', type(err).__name__)
        try:
            client.disconnect()
        except Exception:
            pass
        client = None
        time.sleep(3)
