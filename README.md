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

Note Down the Service SID and download the certificates

In the end you will need these three credential emelents from Twilio to be configured in the software
1. Account SID
2. AUTH Token
3. Service SID
