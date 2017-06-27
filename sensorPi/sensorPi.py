#!/usr/bin/env python
#
# 2017-4-19 by NewDream
#
# i2c interaction with SHT30


import time
import paho.mqtt.client as mqtt
import threading
import uuid
import os
import sys
import sht30.i2c as SHT30
import adxl345.i2c as adxl
import logging

MQTT_PUBLISH_PERIOD = 0.1
global timer_publish_triggered
timer_publish_triggered = 0

def on_connect(client, userdata, rc):
    result = {
        0: "Connection successful",
        1: "Connection refused - incorrect protocol version",
        2: "Connection refused - invalid client identifier ",
        3: "Connection refused - server unavailable ",
        4: "Connection refused - bad username or password ",
        5: "Connection refused - not authorised "
    }
    if rc == 0:
        logging.info(result[rc])
        # print result[rc]
    else:
        logging.warning(result[rc])

def on_disconnect(client, obj, rc):
    logging.warning("Disconnected...")
    client.reconnect()

def timer_publish_trigger():
    # print "triggered"
    threading.Timer(MQTT_PUBLISH_PERIOD, timer_publish_trigger).start()
    global timer_publish_triggered
    timer_publish_triggered = 1

if __name__ == "__main__":
    logging.basicConfig(filename='mqtt-bridge.log',level=logging.DEBUG,format='%(asctime)s  %(message)s')

    sht30 = SHT30.Sht30()
    sht30.enable_periodic_measurement()
    adxl = adxl.Adxl345()

    mac=uuid.UUID(int = uuid.getnode()).hex[-12:]
    logging.info("MAC:"+ mac)

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    logging.info("Try connecting to server...")
    client.connect("newdream.ren", 1883, 10)
    client.loop_start()

    # if len(sys.argv) > 1:
    #     interface = sys.argv[1]
    # else:
    #     interface = 'wlan0'   
    # wifi_scan_result = [[cell.signal, cell.ssid, cell.address] for cell in Cell.all(interface)] 
    # countdown_1min=2

    timer_publish_trigger()
    COUNT_PER_1S = 10
    count_for_1s = 0
    adxl.flash_fifo()

    while 1:
        if timer_publish_triggered == 1:
            timer_publish_triggered = 0
            count_for_1s = count_for_1s + 1
            # every 1.0 s
            if count_for_1s == COUNT_PER_1S:
                count_for_1s = 0
                # upload sht             
                try:
                    temp,humid,timestamp = sht30.read_periodic()
		    if timestamp !=0:
                        payload = '{"mac":"%s","ts":%d,"c_temp":%.2f,"c_humid":%.2f}' % (mac,timestamp,temp,humid);
                        client.publish("tddt/rpi-001/s_temp_humid",payload)
                except Exception, e:
		    print e
                    logging.error(e)

            # every 0.1s
            try:
                ax,ay,az,timestamp = adxl.read()
		if timestamp != 0:
                    payload = '{"mac":"%s","ts":%d,"c_ax":%d,"c_ay":%d,"c_az":%d}' % (mac,timestamp,ax,ay,az);
                    client.publish("tddt/rpi-001/s_acceleration",payload)
            except Exception, e:
		print e
                logging.error(e)
        else:
            time.sleep(0.001)


