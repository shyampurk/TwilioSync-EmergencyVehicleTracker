# TwilioSync Emergency Vehicle Tracker

A model application to simulate the control of traffic signal for ensuring priority movement of emergency vehicles


## Introduction
This is the accompanying source code for the Twilio Sync demonstration for controlling a traffic signal for ensuring priority movement of emergency vehicles within the city. In this demo we have used a raspberry pi 3 as the traffic signal and the emergency vehicle movement is simulated through a script. Twilio sync enables the state and information orchestration between the traffic signal and emergency vehicle.

## What You Will Need

To make a working replica of this demo you will need the following

1. Twilio Subscription & access to Twilio IoT service
2. Raspberry Pi3 hardware and hardware accessories to emulate a traffic signal 
3. Microship RN 2483 LoRa module with serial to USB breakout
4. Software program to control traffic signal
5. Software program to simulate emergency vehicle movement

Refer the sections below to setup all the above components.


## Twilio Subscription

If you have a Twilio account then you can request for the Sync IoT service

### Step 1 Note down the account credentials
You need to capture the account SID and AUTH token 

<img src=screenshots/pic-1.jpg>

### Step 2 Create your device fleet

You need to create a device so that a Twilio Sync instance is associated with it. 

<img src=screenshots/pic-2.jpg>

### Step 3 Retrieve the service id and TLS certificate

Follow the link to obtain Device Service SID and TLS certificates,
https://www.twilio.com/docs/quickstart/sync-iot/python-mqtt-quickstart#create-a-sync-document

Note Down the Twilio credentials and download the certificates

In the end you will need these three credential elements from Twilio to be configured in the software later (explained below)
1. Account SID
2. AUTH Token
3. Service SID

## Raspberry Pi 3 Hardware

Raspberry Pi 3 is used to emulate the traffic signal. You will also need three LEDs ( Red, Yellow and Green) and three pull up resistors to connect to the Raspberry Pi and make a functional setup on a traffic signal

<img src=screenshots/pic-3.jpg width=400>

## Microship RN 2483 LoRa module

To enable a backup direct connectivity in the case of internet connection failure, you need to use a LoRa chip. We have used the Microchip RN 2483 module for this project.

<img src=screenshots/pic-4.jpg>

You will have to connect it to a USB to serial converter so that it can be plugged in to Raspberry Pi3 and a computer. You will need two of these, one each for the traffic signal (Raspberry Pi3) and the emergency vehicle (computer).

<img src=screenshots/pic-5.jpg>



## Software program to control traffic signal

The Raspberry Pi3 setup acts as the traffic signal. It will exhibit the usual red, yellow, green cycle just like a real world traffic signal. But it is programmed in a way that it is aware of the emergency vehicle's proximity so that at a certain minimum distance it will set to green till the emergency vehicle clears past that distance.  

All of this is handled by [this python script](trafficController/trafficControl.py)

Here are the steps to configure and run this script. But before that, make sure that the Raspberry Pi3 is setup with teh LEDs..

### Step 0 : DEPENDENCIES - you need to install the following python libraries that the traffic signal script relies upon

      pip install paho-mqtt
      pip install pyserial

### Step 1 : Clone this repo in the Raspberry Pi 3

### Step 2 : Copy the files 

You must copy the certificate and key files (.pem & .key.decrypted) in the same location as the script.  Refer step 3 under "Twilio Subscription" section above. 

### Step 3 : Modify the traffic signal script  

Navigate to the script file [trafficController/trafficControl.py](trafficController/trafficControl.py) and update the key file names in line 15 & 16.

### Step 4 : Connect the RN2483 LoRa Module

Plug in the LoRa module in one of the USB ports of Raspberry Pi3

### Step 5 : Identify the device file for the LoRa Module

Run the command "dmesg" to display a list of device files under /dev. Look for the most recent file which has the following pattern

        /dev/ttyUSBx

### Step 6 : Run the traffic signal script

Run the script by invoking the following command

        sudo python trafficControl.py --port /dev/ttyUSBx
  

If eveything went well, then you can see the traffic signal toggling between the three signal colors. 

## Software program to simulate emergency vehicle movement

As the final task, you need to setup a simulated movement of an emergency vehicle along a pre-defined route. This route intersects the traffic signal and the signal exhibits an all green state when the vehicle is in close proximity to it.

The emergency vehicle movement is simulated by [this python script](emergencyVechileSimulate/emergencyVechileSimulate.py)

Before you can execute this script on a computer, perform the following steps. The steps below are shown for a Windows based PC/laptop with pre installed python 2.7 runtime environment.


### Step 0 : DEPENDENCIES - You need to install the following python libraries that the emergency vehicle script relies upon

      pip install twilio
      pip install pyserial

### Step 1 : Clone this repo in the computer

### Step 2 : Modify the emergency vehicle script

Navigate to the script file [emergencyVechileSimulate/emergencyVechileSimulate.py](emergencyVechileSimulate/emergencyVechileSimulate.py) and update the line 14, 15 & 16 with your Twilio credentials as follows

 Line 14 : ACCOUNT_SID - Update your ACCOUNT_SID obrained from Twilio
 
 Line 15 : AUTH_TOKEN  - Update your AUTH_TOKEN obrained from Twilio
 
 Line 16 : SERVICE_SID  - Update your SERVICE_SID obrained from Twilio
 
 Refer step 3 under "Twilio Subscription" section above to get your Twilio credentials. 

### Step 4 : Connect the RN2483 LoRa Module

Connect the LoRa module to one of the available USB slots on the computer

### Step 5 : Identify the COM port for communicating with the LoRa module

Open the Device Manager under Windows Control Panel and identify the COMx port that is mapped to the newly attached USN to serial converter for the LoRa module. 

### Step 6 : Run the emergency vehicle simulation

Run the script from command prompt ( assuming that you are in the correct sub directory)

      python emergencyVechileSimulate.py --port COMx
      
This will start the simulation and the GPS location of emergency vehicle along the route will be published at frequent intervals.


