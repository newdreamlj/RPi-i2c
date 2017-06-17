#!/usr/bin/env python
#
# 2017-4-19 by NewDream
#
# i2c interaction with SHT30


import smbus
import time
import paho.mqtt.client as mqtt

bus = smbus.SMBus(1)
SHT_ADDR = 0x44

def on_disconnect(client, obj, rc):
    client.reconnect()

def sht_read():
    bus.write_i2c_block_data(SHT_ADDR, 0x24, [0x00])
    time.sleep(0.1)
    data = bus.read_i2c_block_data(SHT_ADDR, 0,6)
    temp = ((( data[0] * 256.0 + data[1]) * 175 ) / 65535.0) - 45
    humid = ((( data[3] * 256.0 + data[4]) * 100 ) / 65535.0)
    print "T = %6.2f   RH = %6.2f %%" % (temp,humid)
    return temp,humid

if __name__ == "__main__":
    client = mqtt.Client()
    client.on_disconnect = on_disconnect
    client.connect("www.newdream.xyz", 1883)

    while 1:
        t,h = sht_read()
        client.publish("td/room615/temp/1", "%.2f" % t)
	client.publish("td/room615/humid/1", "%.2f" % h)
        time.sleep(60)


