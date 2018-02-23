#Import the Modules Required
from threading import Thread
import paho.mqtt.client as mqtt
import time
import json
from geopy.distance import vincenty
import sys
import argparse
from mclora import MCLoRa
import RPi.GPIO as GPIO

#
# Use the actual location of your downloaded certificate and key.
#
pem_location = 'CYc9531991ff3c4f3db6e35993fa80066d.pem'
key_location = 'CYc9531991ff3c4f3db6e35993fa80066d.key.decrypted'

#Traffic Signal Location
TRAFFIC_SIGNAL = (37.754512, -122.402560)

#LED Pins
YELLOW = 38
RED = 36
GREEN = 40

#Traffic State Related 
NORMAL = 0
CRITICAL = 1

#Traffic Light Related
LIGHT_RED = 0
LIGHT_YELLOW = 1
LIGHT_GREEN = 2

#System States and COnsts
emergencyVehicleState = dict();
gpsLocation = [0]*2;

trafficLightNormalCurrState = LIGHT_RED
trafficLightNormalCycle = [ LIGHT_RED , LIGHT_YELLOW , LIGHT_GREEN]
trafficLightNormalCycleTime = [2, 1, 3]

#System Variables
port = " "
loraM = " "

'''****************************************************************************************
Function Name 		:	obtain_port
Description			:	Obtain the Serial Port from argument 
Parameters 			:	none
****************************************************************************************'''
def obtain_port():
	global port
	#obtain the Port from the Argument 
	descStr = "Traffic Controller: Enter the LoRa Port"
	parser = argparse.ArgumentParser(description=descStr)
	parser.add_argument('--port', dest='serial_port', required=True)
	args = parser.parse_args()
	if args.serial_port:
		port = args.serial_port

'''****************************************************************************************
Function Name 		:	gpio_init
Description			:	Initiazie the GPIO Pins for the Traffic Control
Parameters 			:	none
****************************************************************************************'''
def gpio_init():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(YELLOW, GPIO.OUT)
    GPIO.setup(RED, GPIO.OUT)
    GPIO.setup(GREEN, GPIO.OUT)
    set_red()

'''****************************************************************************************
Function Name 		:	set_red
Description			:	Switch to Red Signal
Parameters 			:	none
****************************************************************************************'''
def set_red():
    GPIO.output(YELLOW, GPIO.LOW)
    GPIO.output(RED, GPIO.HIGH)
    GPIO.output(GREEN, GPIO.LOW)

'''****************************************************************************************
Function Name 		:	set_green
Description			:	Switch to Green Signal
Parameters 			:	none
****************************************************************************************'''
def set_green():
    GPIO.output(YELLOW, GPIO.LOW)
    GPIO.output(RED, GPIO.LOW)
    GPIO.output(GREEN, GPIO.HIGH)

'''****************************************************************************************
Function Name 		:	set_yellow
Description			:	Swtich to Yellow Signal 
Parameters 			:	none
****************************************************************************************'''
def set_yellow():
    GPIO.output(YELLOW, GPIO.HIGH)
    GPIO.output(RED, GPIO.LOW)
    GPIO.output(GREEN, GPIO.LOW)

'''****************************************************************************************
Function Name 		:	handleEmergencyMessage
Description			:	Subscribed to Twilio Channel
Parameters 			:	client 		- Twilio Client
						userdata 	- userdata related to device
						msg 		- Payload received

****************************************************************************************'''
def handleEmergencyMessage(client, userdata, msg):
	print(msg.topic + ' ' + str(msg.payload))
	dataReceived = json.loads(msg.payload)
	gpsLocation[0] = dataReceived["lat"]
	gpsLocation[1] = dataReceived["lon"]
	gps_tuple = tuple(gpsLocation)
	distanceCalculated = int(vincenty(TRAFFIC_SIGNAL, gps_tuple).meters)
	print ("Emergency Vehicle Location: ", distanceCalculated)
	if distanceCalculated >= 150:
		emergencyVehicleState["state"] = 0
		trafficLightNormalCurrState = LIGHT_RED
	else:
		emergencyVehicleState["state"] = 1

'''****************************************************************************************
Function Name 		:	updateTrafficSignal
Description			:	Updates the Signal Status
Parameters 			:	none
****************************************************************************************'''
def updateTrafficSignal():
	global trafficLightNormalCurrState
	state = emergencyVehicleState["state"]
	if state == NORMAL:

		if (LIGHT_RED == trafficLightNormalCurrState):
			print "Switching to RED\n"	
			set_red()
		elif (LIGHT_YELLOW == trafficLightNormalCurrState):
			print "Switching to YELLOW\n"	
			set_yellow()
		elif (LIGHT_GREEN == trafficLightNormalCurrState):
			print "Switching to GREEN\n"	
			set_green()

		time.sleep(trafficLightNormalCycleTime[trafficLightNormalCurrState])

		trafficLightNormalCurrState = trafficLightNormalCycle[ (trafficLightNormalCurrState + 1) % 3]

	elif state == CRITICAL:
		set_green()
		print "Detected Critical Distance from Emergency Vehicle\n"

		print "Switching to GREEN and Hold\n"
		time.sleep(3)

'''****************************************************************************************
Function Name 		:	loraReceive
Description			:	Receives the LoRa Data
Parameters 			:	none
****************************************************************************************'''
def loraReceive():
	global loraM
	count  = 0
	while True:
		print "LoRa Packet Receive Start"
		try:
			data = str(loraM.recv())
			if data == "01": #Code 01 indicates primary communication failure
				print "Received LoRa Signal from Emergeny Vehicle"
				emergencyVehicleState["state"] = 1
				count = 0
			else:
				count = count + 1
				if count == 20:
					count  = 0
					emergencyVehicleState["state"] = 0
		except Exception as error:
			print error 

'''****************************************************************************************
Function Name 		:	systemInit
Description			:	Initiazie the LoRa and Twilio Client 
Parameters 			:	None
****************************************************************************************'''
def systemInit():
	global port, loraM, client
	obtain_port()
	gpio_init()
	emergencyVehicleState.setdefault("state",0)
	
	#loraM handles all the loraEvents 
	loraM = MCLoRa(port)
	success = loraM.testOK()
	if success:
		print "Traffic Controller Gateway Init Success"
		print (success)
	else:
		print("Traffic Controller Gateway Init FAILURE")
	loraM.pause()

	#Twilio Client 	
	client = mqtt.Client(client_id="rpi", clean_session=False)
	client.tls_set(None, pem_location, key_location)
	client.on_message = handleEmergencyMessage
    
    #
    # Use qos=1 to get your device caught up right away.
    #
	client.connect('mqtt-sync.us1.twilio.com', 8883, 60)
	client.subscribe('sync/docs/gpsData', qos=1)
	client.loop_start()

if __name__ == "__main__":
    systemInit()
    loraThread = Thread(target = loraReceive)
    loraThread.setDaemon(True)
    loraThread.start()

    print("Traffic Controller Started\n")

    while True:
        try:
            updateTrafficSignal()
        except KeyboardInterrupt:
            sys.exit(0)


#End of the Script 
##*****************************************************************************************************##
