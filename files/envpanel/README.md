# Environment Panel

Environment Panel is a simple web application to present health status information on your Raspberry PI and display information of environmental sensors which are attached to the I2C bus of the RaspPi. 

The supported devices are:
- An BME280 environmental sensor, reading temperature, pressure and relative humidity.
- An INA260 reading voltage, current and power.


# Installation

First check that the 

Env Panel is based on [Python Flask](http://flask.pocoo.org/) micro-framework. It has a built-in webserver and by default listens on port 8627. Install the pre-requisites:

```
$sudo pip3 install -r requirements.txt 
```

Copy the **envpanel** folder to  **DIRECTORY** (eg. /var/www/)

# Usage

The Env Panel can be run as a standalone server. It can be started manually by invoking python:

```
$ python3 DIRECTORY/envpanel/envpanel.py
```

Then using your favorite web browser, go to http://your_ip_address:8627

# Auto Start

To enable the Env Panel to automatically start after a system reboot, a systemd service file is provided for your convenience:

```
[Unit]
Description=Env Panel
After=multi-user.target

[Service]
Type=idle
User=nobody
ExecStart=/usr/bin/python3 DIRECTORY/envpanel/envpanel.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

The above service files assumes you copied the envpanel directory to **DIRECTORY** - replace **DIRECTORY** with real path to envpanel on your system.

Copy the envpanel.service file to **/etc/systemd/system**:

```
sudo cp envpanel.service /etc/systemd/system/
sudo chmod 644 /etc/systemd/system/envpanel.service
```

Now configure systemd to load the service file during boot:

```
sudo systemctl daemon-reload
sudo systemctl enable envpanel.service
sudo systenctl start envpanel.service
```

After startup, check the status of the Env Panel service:

```
sudo systemctl status envpanel.service
```

If all appears OK, you can start using Env Panel using any browser.
