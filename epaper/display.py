import os
import json
import csv
import random
from datetime import datetime
import time
from sys import platform
from PIL import Image, ImageDraw, ImageFont
import network
import font

dirname, scriptname = os.path.split(os.path.abspath(__file__))
THIS_DIRECTORY = f'{dirname}{os.sep}'
PARENT_DIRECTORY = f"{os.sep.join(THIS_DIRECTORY.split(os.sep)[:-2])}{os.sep}"

if platform == 'linux':
    if os.path.exists(f'{THIS_DIRECTORY}v2'):
        print('DEBUG : Loading V2 display module')
        from waveshare_epd import epd7in5_V2
        epd = epd7in5_V2.EPD()
    else:
        from waveshare_epd import epd7in5
        epd = epd7in5.EPD()
    epd.init()
    epd.Clear()


SETTINGS = {}
UI_FONT = ImageFont.truetype(f'{THIS_DIRECTORY}fonts{os.sep}NotoSans.ttf', 56)
UI_FONT_MEDIUM = ImageFont.truetype(f'{THIS_DIRECTORY}fonts{os.sep}NotoSans.ttf', 40)
UI_FONT_SMALL = ImageFont.truetype(f'{THIS_DIRECTORY}fonts{os.sep}NotoSans.ttf', 24)
UI_FONT_TINY = ImageFont.truetype(f'{THIS_DIRECTORY}fonts{os.sep}NotoSans.ttf', 18)

def already_displayed(word):
    today = datetime.now().strftime('%Y-%m-%d')
    history_file = f'{THIS_DIRECTORY}history.json'
    if not os.path.exists(history_file):
        history = {
            today:[]
        }
    else:
        history = load_json(history_file)
    return word in history.get(today, [])

def end_screen():
    background = Image.open(f'{THIS_DIRECTORY}templates{os.sep}top_banner.bmp')
    width, height = background.size
    background = background.resize((width, height))
    draw = ImageDraw.Draw(background)

    message = "You've seen all your"
    string_width, string_height = UI_FONT.getsize(message)
    draw.text(
        (
            int(width  / 2) - int(string_width  / 2),  # left
            int(height / 2) - int(string_height / 2) - 20 # top
        ),
        message,          # text
        (0, 0, 0),              # colour
        font=UI_FONT      # font
    )
    message = "words for today"
    string_width, string_height = UI_FONT.getsize(message)
    draw.text(
        (
            int(width  / 2) - int(string_width  / 2),  # left
            int(height / 2) - int(string_height / 2) + string_height - 20# top
        ),
        message,          # text
        (0, 0, 0),              # colour
        font=UI_FONT      # font
    )
    background = background.resize((
        SETTINGS['dislplay']['width'],
        SETTINGS['dislplay']['height']
    ))
    print('DEBUG : updating display')
    if platform == 'linux':
        epd.display(epd.getbuffer(background))
    print(f' {os.sep.join(THIS_DIRECTORY.split(os.sep)[-2:])}on_screen.bmp')
    background.save(f'{THIS_DIRECTORY}on_screen.bmp')


def language_codes():
    with open(f'{PARENT_DIRECTORY}web{os.sep}language_list.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        return list(reader)

def load_settings():
    global SETTINGS
    settings_file = f'{PARENT_DIRECTORY}settings.json'
    if os.path.exists(settings_file):
        SETTINGS = load_json(settings_file)
    else:
        if os.path.exists(f'{THIS_DIRECTORY}v2'):
            height = 480
            width = 800
        else:
            height = 384
            width = 640
        SETTINGS = {
            "dislplay": {
                "width":width,
                "height":height
            },
            "refresh_after":15,
            "language":""
        }
        save_json(settings_file, SETTINGS)

def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.loads(f.read())
        return data

def record_displayed(word):
    today = datetime.now().strftime('%Y-%m-%d')
    history_file = f'{THIS_DIRECTORY}history.json'
    if not os.path.exists(history_file):
        history = {
            today:[]
        }
    else:
        history = load_json(history_file)
    if today not in history:
        history[today] = []
    history[today].append(word)
    save_json(history_file, history)

def save_json(filename, data):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        f.write(json.dumps(data, indent=4))

def select_word():
    word_file = f'{PARENT_DIRECTORY}{SETTINGS["language"]}_words.json'
    if not os.path.exists(word_file):
        return None
    else:
        wordlist = load_json(word_file)
        wordlist = [word for word in wordlist if not already_displayed(word)]
        if len(wordlist) > 0:
            word = random.choice(wordlist)
            record_displayed(word)
            return word
        else:
            return None

def show(word, words_displayed):
    background = Image.open(f'{THIS_DIRECTORY}templates{os.sep}top_banner.bmp')
    width, height = background.size
    background = background.resize((width, height))
    draw = ImageDraw.Draw(background)

    font_file = font.get_fonts(
        SETTINGS['language'].upper(),
        word['translation']
    )
    translated_fonts = {
        'large': ImageFont.truetype(font_file, 56),
        'small': ImageFont.truetype(font_file, 24)
    }

    translation_width, translation_height = translated_fonts['large'].getsize(word['translation'])
    draw.text(
        (
            int(width / 2) - int(translation_width / 2), # left
            100                 # top
        ),
        word['translation'],    # text
        (0, 0, 0),              # colour
        font=translated_fonts['large']   # font
    )

    word_width,_ = UI_FONT_SMALL.getsize(word['word'])
    draw.text(
        (
            int(width / 2) - int(word_width / 2), # left
            (translation_height) + 110 # top
        ),
        word['word'],           # text
        (0, 0, 0),              # colour
        font=UI_FONT_SMALL    # font
    )

    if word['example'] != '':
        example_width, _ = translated_fonts['small'].getsize(f"\"{word['example']}\"")
        draw.text(
            (
                int(width / 2) - int(example_width / 2), # left
                translation_height + 200        # top
            ),
            f"\"{word['example']}\"", # text
            (0, 0, 0),              # colour
            font=translated_fonts['small']    # font
        )

    update_string = f'word {words_displayed} for today'
    _, data_height = UI_FONT_TINY.getsize(update_string)
    draw.text(
        (
            50, # left
            height - (data_height + 10) # top
        ),
        update_string,     # text
        (0, 0, 0),         # colour
        font=UI_FONT_TINY  # font
    )

    update_string = f'last updated {datetime.now().strftime("%H:%M")}'
    data_width, data_height = UI_FONT_TINY.getsize(update_string)
    draw.text(
        (
            width - (data_width + 50), # left
            height - (data_height + 10) # top
        ),
        update_string,      # text
        (0, 0, 0),          # colour
        font=UI_FONT_TINY   # font
    )

    background = background.resize((
        SETTINGS['dislplay']['width'],
        SETTINGS['dislplay']['height']
    ))
    print('DEBUG : updating display')
    if platform == 'linux':
        epd.display(epd.getbuffer(background))
    print(f' {os.sep.join(THIS_DIRECTORY.split(os.sep)[-2:])}on_screen.bmp')
    background.save(f'{THIS_DIRECTORY}on_screen.bmp')


def welcome_screen():
    background = Image.open(f'{THIS_DIRECTORY}templates{os.sep}top_banner.bmp')
    width, height = background.size
    draw = ImageDraw.Draw(background)

    url, qr_code = network.get_address()
    qr_code = Image.open(qr_code)
    qr_code = qr_code.resize((200, 200))
    qr_width, qr_height = qr_code.size
    background.paste(
        qr_code,
        (
            0,
            (int(height / 2) - (int(qr_height / 2)) + 10)
        )
    )

    message = 'Scan the QR code to'
    _, string_height = UI_FONT_MEDIUM.getsize(message)
    draw.text(
        (
            qr_width - 5,            # left
            int(height / 2) - string_height  # top
        ),
        message,              # text
        (0, 0, 0),            # colour
        font=UI_FONT_MEDIUM # font
    )
    message = 'manage your words'
    _, string_height = UI_FONT_MEDIUM.getsize(message)
    draw.text(
        (
            qr_width -5,              # left
            int(height / 2)  # top
        ),
        message,                   # text
        (0, 0, 0),                 # colour
        font=UI_FONT_MEDIUM      # font
    )

    string_width, string_height = UI_FONT_TINY.getsize(url)
    draw.text(
        (
            int(qr_width / 2) - int(string_width / 2),  # left
            int(height / 2)  + int(qr_height / 2) + int(string_height / 2) # top
        ),
        url,                    # text
        (0, 0, 0),              # colour
        font=UI_FONT_TINY     # font
    )

    background = background.resize((
        SETTINGS['dislplay']['width'],
        SETTINGS['dislplay']['height']
    ))
    print('DEBUG : updating display')
    if platform == 'linux':
        epd.display(epd.getbuffer(background))
    print(f' {os.sep.join(THIS_DIRECTORY.split(os.sep)[-2:])}on_screen.bmp')
    background.save(f'{THIS_DIRECTORY}on_screen.bmp')


def main():
    load_settings()
    welcome_screen()

    word = None
    while word is None:
        time.sleep(5)
        load_settings()
        word = select_word()

    words_displayed = 0
    while word is not None:
        words_displayed += 1
        show(word, words_displayed)
        time.sleep(SETTINGS['refresh_after'] * 60)
        load_settings()
        word = select_word()

    end_screen()

if __name__ == '__main__':
    main()
