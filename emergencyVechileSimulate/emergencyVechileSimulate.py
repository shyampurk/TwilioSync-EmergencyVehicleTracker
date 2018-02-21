# Download the Python helper library from twilio.com/docs/python/install

#Import the Modules Required
from twilio.rest import Client
from datetime import datetime
import time
import urllib2
import sys
import argparse
from mclora import MCLoRa
import serial

# Your Account Sid and Auth Token from twilio.com/user/account
account_sid = "AC18af524b5da6e4429e4c5875e2fdd7cd"
auth_token = "4ee302404ec79b0622eae81ff717e534"
deviceID = "ISd136efcec806480a96570a44a4b942af"

#Variables
loraM = " "
port = " "
client = " "

#Data format to be sent over twilio
gps_Data = {
    'date_updated': str(datetime.now()),
    'lat': "12.5656",
    'lon': "73.5050"
}

#List of the ambulance gps locaiton points 
ambulance_list = [(37.753925, -122.399412),(37.753925, -122.399577),
				  (37.754228, -122.399612),(37.754660, -122.399898),
				  (37.754579, -122.401350),(37.754541, -122.402021),
				  (37.754512, -122.402560),(37.754485, -122.402862),
				  (37.754430, -122.403747),(37.754277, -122.406388),
				  (37.754586, -122.406395)]

'''****************************************************************************************
Function Name 		:	obtain_port
Description			:	Obtain the Serial Port from argument 
Parameters 			:	none
****************************************************************************************'''
def obtain_port():
	global port
	descStr = "Add description here"
	parser = argparse.ArgumentParser(description=descStr)
	# add expected arguments
	parser.add_argument('--port', dest='serial_port', required=True)
	args = parser.parse_args()

	print("starting gateway...\n")

	if args.serial_port:
	    port = args.serial_port

'''****************************************************************************************
Function Name 		:	sys_init
Description			:	Initiazie the LoRa and Twilio Client 
Parameters 			:	None
****************************************************************************************'''
def  sys_init():
	global loraM, client
	obtain_port()

	#Twilio Client Initilize 
	client = Client(account_sid, auth_token)

	# LoRa module Initialze on the given Port
	loraM = MCLoRa(port)
	success = loraM.testOK()
	if success:
	    print('connected: ')
	    print(success)
	    print(loraM.getUniqueID())
	else:
	    print('unable to connect!')
	    sys.exit(0)
	loraM.pause()

if __name__ == '__main__':
	sys_init()
	while True:
		try:		
			for i in range(len(ambulance_list)):
				gps_Data["lat"] = ambulance_list[i][0]
				gps_Data["lon"] = ambulance_list[i][1]
				try:
					document = client.sync \
					    .services(deviceID) \
					    .documents("gpsData") \
					    .update(data=gps_Data)
					print("Location Updated: ", document.data)
				except Exception as error:
					print error
					print "Send LoRa"
					loraM.send()
			        time.sleep(5)
				time.sleep(3)
			time.sleep(5)
		except KeyboardInterrupt:
			print "Exiting ..."
			sys.exit(0)

#End of the Script 
##*****************************************************************************************************##