#!/usr/bin/python3

import os
import subprocess
import random
from time import sleep, time
import datetime

from gpiozero import DistanceSensor
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

""" Database setup """
engine = create_engine(os.getenv("DATABASE_URL"),echo=True)
db = scoped_session(sessionmaker(bind=engine))

""" For Video PLayer """
# Path to video file to be played
video_path = '/home/pi/tube/Videos/Dotonbori.mp4'

# Crops center part of video in order to accomodate in a 4:3 screen
crop_area = '240,0,1680,1080'

# Turns video 180 degrees for better internal layout in the actual tube
degrees = 180

""" For Sound Effects """
# Sound file to play when ultrasonic sensor is activated
soundTube = '/home/pi/tube/Sounds/warp.wav'
soundPowerUp = '/home/pi/tube/Sounds/powerup.wav'

# Ultrasonic sensor configuration, max range is set to 3 meters
sensor = DistanceSensor(echo=17, trigger=18, max_distance=3)

# Below this distance in centimeters, ultrasonic sensor will not activate
minDistance = 30

# Above this distance in centimeters, ultrasonic sensor will not activate
maxDistance = 200

# Time when tube sound was last played
start = 0

# Time when tube sound activation parameters were met
end = 0

# Time when power up sound was last played
startPowerUp = 0

# Time when power up sound activation parameters were met
endPowerUp = 0

def main():
    # Starts Omxplayer program and plays video
    video_open = subprocess.Popen(['omxplayer', '--loop', '--no-osd','--orientation', str(degrees), '--crop', str(crop_area), str(video_path)], stdin=subprocess.PIPE)
    while True:
        check_distance_random()

def check_distance_random():
	global start
	global end
	global counter
	global startPowerUp
	global endPowerUp
	distance = sensor.distance * 100
	if distance > maxDistance:
		print(distance)
	elif minDistance < distance:
		print(distance)
		end = time()
		# If there is a 15 seconds difference from the time the sound was played, sound will play again
		if (end - start > 15):
			subprocess.Popen(['omxplayer', '--no-keys', '--no-osd', soundTube, '&'], stdin=subprocess.PIPE)
			start = time()
	else:
		print(distance)
		endPowerUp = time()
		if (endPowerUp - startPowerUp > 10):
			subprocess.Popen(['omxplayer', '--no-keys', '--no-osd', soundPowerUp, '&'], stdin=subprocess.PIPE)
			db.execute("INSERT INTO sensor_data (counter) VALUES (1)")
			db.commit()
			startPowerUp = time()
			sensor.wait_for_out_of_range(100)

	sleep(0.5)


if __name__ == "__main__":
    main()
