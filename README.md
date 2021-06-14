# DIY-Project inspired by QLOCKTWO
## privat usage only! I built this project for a birthday present (see (/img). Deployed on a raspberry pi Zero W.

# Installation:
- For correct cabling look up /img
- install https://github.com/rpi-ws281x/rpi-ws281x-python (controlling led's)
- For starting, run 'sudo python clock_controller.py' on your pi. RPi_ws281x needs sudo
- Start the script after boot: 
    - on the pi: 'sudo nano /etc/rc.local
    - paste in 'sudo python clock_controller.py' before the last line and save

# Parts
- Raspberry Pi Zero W (W = Wifi important for auto-updating clock via internet)
- 16x16 LED matrix like this one: https://www.amazon.de/ALITOVE-Arduino-WS2812B-Rainbow-flexible/dp/B01JYLZWPI/ref=dp_prsubs_1?pd_rd_i=B01JYLZWPI&psc=1
- Breadboard & cables
- converter-thing: https://www.amazon.de/gp/product/B016MTW0YG/ref=ppx_yo_dt_b_asin_title_o05_s01?ie=UTF8&psc=1
- Housing made with a 3d-printer
- other parts: laser-cutted wooden plates

