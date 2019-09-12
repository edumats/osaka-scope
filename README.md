# Osaka Scope

Interactive video installation housed in a Mario Tube. Using Raspbery Pi that plays a HD video, produces sounds based on readings of an ultrasonic sensor, logs views into a Postgresql database. Includes an administrator website to check status of the views.

## Getting Started

Please use video_local.py located in /raspberry in your Raspberry Pi. All the other files will be used on a Heroku server or local server.

### Prerequisites

See requirements.txt
For the Raspberry Pi, it is necessary to install GPIO Zero, sqlalchemy and run Python 3

### Installing

Please git clone the contents of this repository and, using Git, deploy the app to Heroku.
If you use your local server instead, it is necessary to set the environment variables to: 
```
FLASK_APP=application.py
```
and

```
DATABASE_URL=(URI address in your Heroku Postgres)
```

Please set DATABASE_URL also in your Raspberry Pi.

Also, it is necessary to create in your database server an users table with the following fields:

```
  Column  |  Type   | Collation | Nullable |              Default
----------+---------+-----------+----------+-----------------------------------
 id       | integer |           | not null | nextval('users_id_seq'::regclass)
 username | text    |           | not null |
 hash     | text    |           | not null |
```

and also a sensor data table:

```
 Column  |           Type           | Collation | Nullable |                 Default
---------+--------------------------+-----------+----------+-----------------------------------------
 id      | integer                  |           | not null | nextval('sensor_data_id_seq'::regclass)
 counter | integer                  |           | not null |
 date    | timestamp with time zone |           | not null | now()
```

As a last step, please edit the video_local.py file variables:

```
* video_path
Path to the video that will be played by the Raspberry Pi

* crop_area
Used to crop part of video because of the diamaters of the actual tube. Please edit if you don't need video cropping

* minDistance
Distance measured by ultrasonic sensor. Readings that are less than this distance will be counted as a "view"

* maxDistance
Distance measured by ultrasonic sensor. When sensor registers a distance between minDistance and maxDistance, will play a sound that is refered by soundTube variable. Distances greater than maxDistances will not play any sound.

* soundTube
Plays a sound when ultrasonic sensor detects a distance less than maxDistance and greater than min Distance. Used to invite visitors to see the video.

* soundPowerUp
Plays a sound to indicate that a view was recorded for distances that are less than minDistance.

* degrees
Turn the video upside down because of the physical restrictions of the actual tube. Set to 360 to turn to normal view.
```

## Authors

* **Eduardo Matsuoka**