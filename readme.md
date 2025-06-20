# Words for the Day

Display words and their translation on an eInk display, slowly cycling throughouth the day to help with learning another language's vocabulary.

## Installation


### Dependencies

Ensure a Waveshare ePaper display connected and all it's software installed

Navigate to `/home/pi/` in a terminal window

Clone this git repo

`git clone https://bitbucket.org/pangolinpaw/word-of-the-day.git`

Navigate into the newly created directory

`cd word-of-the-day/`

Install the requirements

`pip3 install -r requirements.txt`


### Configuring for your display

There are several Waveshare ePaper displays and the correct module needs to be imported for this application to work.

By default, `epd7in5` is used, but if you need a different one:

A full list of available imports can be shown with the command

`ls /epaper/waveshare_epd`

Open the `/epaper/display.py` file for editing

`nano /epaper/display.py`

Find the line `from waveshare_epd import epd7in5_V2`

Replace `epd7in5` with the appropriate import for your display

Save your changes by pressing `Ctrl`+`X` and follow the prompts at the bottom of your screen.


## Usage

The application is intended to run each time the Raspberry Pi boots and to ensure the list of displayed words is refreshed each day, it's suggested that the Pi is rebooted at the end of each day. To achieve this edit the crontab with:

`crontab -e`

If your presented with various text editor options, select *nano*. Then add the following lines to the end of the file:

```
@reboot sleep 5; sudo nohup python3 /home/pi/word-of-the-day/web/web_interface.py &  # run web interface
@reboot sleep 5; sudo nohup python3 /home/pi/word-of-the-day/epaper/display.py & # start screen 
0 1 * * * sudo reboot # reboot 1 minute after midnight

```

Press `CTRL`+`x`, then `y` to save and exit


### Web interface

![](https://github.com/GarethMurden/word_of_the_day/blob/master/screenshots/web_homepage.png?raw=true)

Words are saved to the device via a web interface accessible within the local network.

Each boot and if there are no words set to display, a welcome screen will be displayed with a QR code. Scan this code to access the web interface to manage your words and translations.

### eInk display

![](https://github.com/GarethMurden/word_of_the_day/blob/master/screenshots/screen.png?raw=true)

At set intervals, a random word from those set via the web is retrieved and shown on the epaper display.