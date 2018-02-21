# Download the Python helper library from twilio.com/docs/python/install
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

def internet_on():
    try:
        urllib2.urlopen('http://google.com', timeout=1)
        return True
    except urllib2.URLError as err: 
        return False

client = Client(account_sid, auth_token)

new_data = {
    'date_updated': str(datetime.now()),
    'lat': "12.5656",
    'lon': "73.5050"
}

# 200 mts, 100 mts, 50 mts, 0 mts, -300 mts
#ambulance_list = [(37.754660, -122.399898),(37.754505, -122.402470),(37.754503, -122.402528),(37.754277, -122.406388),(37.754277, -122.406388),(37.754277, -122.406388),(37.754277, -122.406388)]
ambulance_list = [(37.754512, -122.402560),(37.753925, -122.399577),(37.754228, -122.399612),(37.754660, -122.399898),(37.754579, -122.401350),(37.754541, -122.402021),(37.754512, -122.402560),(37.754485, -122.402862),(37.754430, -122.403747),(37.754277, -122.406388),(37.754586, -122.406395)]
# create parser
descStr = "Add description here"
parser = argparse.ArgumentParser(description=descStr)
# add expected arguments
#parser.add_argument('--file', dest='imgFile', required=True)
#parser.add_argument('--morelevels',dest='moreLevels',action='store_true')
# parse args
parser.add_argument('--port', dest='serial_port', required=True)
args = parser.parse_args()
#print(args)

print("starting gateway...\n")

if args.serial_port:
    port = args.serial_port

# create LoRa module
loraM = MCLoRa(port)
success = loraM.testOK()
if success:
    print('connected: ')
    print(success)
    print(loraM.getUniqueID())
else:
    print('unable to connect!')
loraM.pause()
while True:
	try:		
		for i in range(len(ambulance_list)):
			new_data["lat"] = ambulance_list[i][0]
			new_data["lon"] = ambulance_list[i][1]
			if internet_on():		
				try:
					document = client.sync \
					    .services(deviceID) \
					    .documents("gpsData") \
					    .update(data=new_data)
					print(document.data)
				except Exception as error:
					print "Send LoRa"
					print loraM.send()
			        time.sleep(10)
			else:
				print "Send Through LoRa"
				print loraM.send()
	        	time.sleep(10)
			time.sleep(3)
		time.sleep(5)
	except KeyboardInterrupt:
		sys.exit(0)

	