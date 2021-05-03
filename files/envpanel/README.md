# Environment Panel

Environment Panel is a simple web application to present health status information on your Raspberry PI and display information of environmental sensors which are attached to the I2C bus of the RaspPi. 

The supported devices are:
- An BME280 environmental sensor, reading temperature, pressure and relative humidity.
- An INA260 reading voltage, current and power.


# Installation

First you need to install the following packages in Raspian:

```
$sudo apt install rrdtool librrd-dev python-rrdtool
```

Env Panel is based on [Python Flask](http://flask.pocoo.org/) micro-framework. It has a built-in webserver and by default listens on port 8627. Install the python pre-requisites:

```
$sudo pip3 install -r requirements.txt 
```

Copy the **envpanel** folder to  **DIRECTORY** (eg. /var/www/)

# Usage

First set-up the collector process and run it:

```
$ sudo mkdir /var/local/astroberry
$ sudo chown astroberry /var/local/astroberry
$ python3 DIRECTORY/envpanel/envpanelcollect.py
```

The Env Panel itself can be run as a standalone server. It can be started manually by invoking python:

```
$ python3 DIRECTORY/envpanel/envpanel.py
```

Then using your favorite web browser, go to http://your_ip_address:8627

# Auto Start

To enable the collector and Env Panel to automatically start after a system reboot, a systemd service file is provided for your convenience:

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
(Note: for the collector it looks rather similar, up to astroberry as user and a different path.)

The above service files assumes you copied the envpanel directory to **DIRECTORY** - replace **DIRECTORY** with real path to envpanel on your system.

Copy the envpanel.service and envpanelcollect.service files to **/etc/systemd/system**:

```
sudo cp envpanel.service /etc/systemd/system/
sudo cp envpanelcollect.service /etc/systemd/system/
sudo chmod 644 /etc/systemd/system/envpanel.service
sudo chmod 644 /etc/systemd/system/envpanelcollect.service
```

Now configure systemd to load the service file during boot:

```
sudo systemctl daemon-reload
sudo systemctl enable envpanelcollect.service
sudo systemctl start envpanelcollect.service
sudo systemctl enable envpanel.service
sudo systemctl start envpanel.service
```

After startup, check the status of the Env Panel service:

```
sudo systemctl status envpanel.service
```

If all appears OK, you can start using Env Panel using any browser.
