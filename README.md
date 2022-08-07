# DIY-Project inspired by QLOCKTWO
## privat usage only! I built this project for a birthday present (see (/img). Deployed on a raspberry pi Zero W.

# Installation:
## Download Qlock Repo
- clone github repo 'qlock'
- sudo pip install rpi_ws281x
- disable audio kernel module:
    create file /etc/modprobe.d/snd-blacklist.conf with 'blacklist snd_bcm2835'
    for further information: https://pypi.org/project/rpi-ws281x/

- Start the script after boot: 
    - on the pi: 'sudo nano /etc/rc.local
    - paste in 'sudo python clock_controller.py' before the last line and save

## Potentiometer installations
- https://howchoo.com/pi/how-to-install-a-potentiometer-on-a-raspberry-pi#install-an-appropriate-python-library
- install Adafruit_Python_ADS1x15
- check if i2c device is found:

- sudo i2cdetect -y 1


# Wiring:
WS281x LED chips are controlled by 5V PWM signal, but RPi only has 3,3V - level shifter needed.
I'm using the SN54AHCT125 with 5 cabels connected to it.

So, 5V and ground are coming directly from the Pi (Pin 2/4 for 5V & 6 for GND), but the GPIO needs to be shifted.

![Alt text](img/level_shifter.png?raw=true "Level shifter")

Shifter's pin 1 and 7 to gnd, 14 to 5V, 2 is input PWM (coming from Pi) and 3 is output (going to led strip).


# Parts
- Raspberry Pi Zero W (W = Wifi important for auto-updating clock via internet)
- 16x16 LED matrix like this one: https://www.amazon.de/ALITOVE-Arduino-WS2812B-Rainbow-flexible/dp/B01JYLZWPI/ref=dp_prsubs_1?pd_rd_i=B01JYLZWPI&psc=1
- Breadboard & cables
- level shifter: https://www.amazon.de/gp/product/B016MTW0YG/ref=ppx_yo_dt_b_asin_title_o05_s01?ie=UTF8&psc=1
- Housing made with a 3d-printer
- other parts: laser-cutted wooden plates

# Additional:
- disable audio: sudo nano /etc/modprobe.d/snd-blacklist.conf add 'blacklist snd_bcm2835'
- in sudo nano /boot/config.txt, comment out 'dtparam=audio=on'
- sudo reboot