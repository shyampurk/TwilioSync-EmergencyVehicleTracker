from threading import Thread
import paho.mqtt.client as mqtt
import time
import json
from geopy.distance import vincenty
import sys
import argparse
from mclora import MCLoRa
import RPi.GPIO as GPIO

BLUE = 38
RED = 36
GREEN = 40

#
# Use the actual location of your downloaded certificate and key.
#
pem_location = 'CYc9531991ff3c4f3db6e35993fa80066d.pem'
key_location = 'CYc9531991ff3c4f3db6e35993fa80066d.key.decrypted'

TRAFFIC_SIGNAL = (37.754512, -122.402560)

#Traffic Related 
NORMAL = 0
CRITICAL = 1

ambulaceState = dict();
gpsLocation = [0]*2;
port = " "
loraM = " "

def obtain_port():
	global port
	#obtain the Port from the Argument 
	descStr = "Traffic Controller: Enter the LoRa Port"
	parser = argparse.ArgumentParser(description=descStr)
	parser.add_argument('--port', dest='serial_port', required=True)
	args = parser.parse_args()
	if args.serial_port:
		port = args.serial_port

def gpio_init():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(BLUE, GPIO.OUT)
    GPIO.setup(RED, GPIO.OUT)
    GPIO.setup(GREEN, GPIO.OUT)
    set_red()

def set_red():
    GPIO.output(BLUE, GPIO.LOW)
    GPIO.output(RED, GPIO.HIGH)
    GPIO.output(GREEN, GPIO.LOW)

def set_green():
    GPIO.output(BLUE, GPIO.LOW)
    GPIO.output(RED, GPIO.LOW)
    GPIO.output(GREEN, GPIO.HIGH)

def set_yellow():
    GPIO.output(BLUE, GPIO.HIGH)
    GPIO.output(RED, GPIO.LOW)
    GPIO.output(GREEN, GPIO.LOW)

def on_message(client, userdata, msg):
	print(msg.topic + ' ' + str(msg.payload))
	dataReceived = json.loads(msg.payload)
	gpsLocation[0] = dataReceived["lat"]
	gpsLocation[1] = dataReceived["lon"]
	gps_tuple = tuple(gpsLocation)
	distanceCalculated = int(vincenty(TRAFFIC_SIGNAL, gps_tuple).meters)
	print ("Ambulace Location: ", distanceCalculated)
	if distanceCalculated >= 150:
		ambulaceState["state"] = 0
	else:
		ambulaceState["state"] = 1

def updateTrafficSignal():
    state = ambulaceState["state"]
    if state == NORMAL:
        print "RED"
        set_red()
        time.sleep(1)
        print "YELLOW"
        set_yellow()
        time.sleep(1)
        print "GREEN"
        set_green()
        time.sleep(3)
    elif state == CRITICAL:
        set_green()
        print "GREEN"
        time.sleep(3)

def signalUpdate():
    while True:
        updateTrafficSignal()

def loraReceive():
	global loraM
	count  = 0
	try:
		data = loraM.recv()
		if data == "01":
			ambulaceState["state"] = 1
			count = 0
		else:
			count = count + 1
			if count == 20:
				count  = 0
				ambulaceState["state"] = 0
	except Exception as error:
		print error 

def systemInit():
	global port, loraM, client
	obtain_port()
	gpio_init()
	ambulaceState.setdefault("state",0)
	#loraM handles all the loraEvents 
	loraM = MCLoRa(port)
	success = loraM.testOK()
	if success:
		print "Gateway Init Success"
		print (success)
	else:
		print("Unable to connect to LoRa")
	loraM.pause()

	#Twilio Client 	
	client = mqtt.Client(client_id="rpi", clean_session=False)
	client.tls_set(None, pem_location, key_location)
	client.on_message = on_message
    
    #
    # Use qos=1 to get your device caught up right away.
    #
	client.connect('mqtt-sync.us1.twilio.com', 8883, 60)
	client.subscribe('sync/docs/gpsData', qos=1)
	client.loop_start()

if __name__ == "__main__":
    systemInit()
    t1 = Thread(target = signalUpdate)
    t2 = Thread(target = loraReceive)
    t1.setDaemon(True)
    t2.setDaemon(True)
    t1.start()
    t2.start()
    while True:
        try:
            pass
        except KeyboardInterrupt:
            t1.stop()
            t2.stop()
            sys.exit(0)
