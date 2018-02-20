import paho.mqtt.client as mqtt
import time
import json
from geopy.distance import vincenty
import sys
import argparse
from mclora import MCLoRa
from threading import Thread

#
# Use the actual location of your downloaded certificate and key.
#
pem_location = 'CYc9531991ff3c4f3db6e35993fa80066d.pem'
key_location = 'CYc9531991ff3c4f3db6e35993fa80066d.key.decrypted'

TRAFFIC_SIGNAL = (37.754512, -122.402560)

client = mqtt.Client(client_id="rpi", clean_session=False)
client.tls_set(None, pem_location, key_location)

#Traffic Related 
NORMAL = 0
CRITICAL = 1

ambulaceState = dict();
gpsLocation = [0]*2;

descStr = "Add Description"
parser = argparse.ArgumentParser(description=descStr)
parser.add_argument('--port', dest='serial_port', required=True)
args = parser.parse_args()

port = " "
if args.serial_port:
	port = args.serial_port

loraM = MCLoRa(port)
# Print out any updates.
#
def print_message(client, userdata, msg):
    print(msg.topic + ' ' + str(msg.payload))
    dataReceived = json.loads(msg.payload)
    gpsLocation[0] = dataReceived["lat"]
    gpsLocation[1] = dataReceived["lon"]
    gps_tuple = tuple(gpsLocation)
    distanceCalculated = int(vincenty(TRAFFIC_SIGNAL, gps_tuple).meters)
    print ("Ambulace Location: ", distanceCalculated)
    if distanceCalculated >= 150:
    	ambulaceState["state"] = 0
	updateTrafficSignal()
    else:
    	ambulaceState["state"] = 1
	updateTrafficSignal()

def updateTrafficSignal():
	state = ambulaceState["state"]
	if state == NORMAL:
		print "RED"
		time.sleep(1)
		print "YELLOW"
		time.sleep(1)
		print "GREEN"
		time.sleep(3)
	elif state == CRITICAL:
		print "GREEN"
		time.sleep(3)

def loraReceive():
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

if __name__ == '__main__':

	ambulaceState.setdefault("state",0)
	success = loraM.testOK()
	if success:
		print "Gateway Init Success"
		print (success)
	else:
		print("Unable to connect to LoRa")

	loraM.pause()

	client.on_message = print_message
	#
	# Use qos=1 to get your device caught up right away.
	#

	client.connect('mqtt-sync.us1.twilio.com', 8883, 60)
	client.subscribe('sync/docs/gpsData', qos=1)
	client.loop_start()

	while(True):
		try:
			loraThread  = Thread(target=loraReceive)
			loraThread.start()
			loraThread.join()
			updateTrafficSignal()
		except KeyboardInterrupt:
			print "Exiting ..."
			sys.exit(0)


