# Osaka Scope

Interactive video instalation housed in a Mario Tube. Using Raspbery Pi that plays a HD video, produces sounds based on readings of a ultrasonic sensor, logs views into a Postgresql database. Includes an administrator website to check status of the views.

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

## Authors

* **Eduardo Matsuoka**