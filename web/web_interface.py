import os
import json
import csv
from datetime import datetime
from flask import Flask, request, render_template, jsonify, redirect
from slugify import slugify

VERSION = '1.1'

dirname, scriptname = os.path.split(os.path.abspath(__file__))
THIS_DIRECTORY = f'{dirname}{os.sep}'
PARENT_DIRECTORY = f"{os.sep.join(THIS_DIRECTORY.split(os.sep)[:-2])}{os.sep}"

app = Flask(__name__)

# ============================================
#   FRONT-END
# ============================================

@app.route('/', methods=['GET', 'POST'])
def root():
    language = request.args.get('language', None)
    if language is None:
        settings = load_settings()
        language = settings.get('language', '')
        if language == '':
            return redirect('/new_language')

    if request.method == 'POST':
        if 'new_word' in request.form:
            word = request.form.get('new_word', False)
            translation = request.form.get('new_translation', False)
            example = request.form.get('new_example', '')
            if all([word, translation]):
                save_word(word, translation, example, language)
            else:
                return render_template(
                    'notification.html',
                    message_type='Error',
                    message='Please specify both a Word and Translation.',
                    destination=f'/?language={language}'
                )
        if 'delete_id' in request.form:
            slug = request.form.get('delete_id', None)
            if slug is not None:
                delete_word(slug, language)
            else:
                return render_template(
                    'notification.html',
                    message_type='Error',
                    message='Unable to delete word, please try again.',
                    destination=f'/?language={language}'
                )
    words = load_words(language)
    words.reverse()
    return render_template(
        'index.html',
        words = words,
        version = VERSION
    )

@app.route('/language', methods=['GET', 'POST'])
def language():
    available_languages = list_languages()
    settings = load_settings()
    if request.method == 'POST':
        selected_language = request.form.get('display_language')
        settings['language'] = selected_language.lower()
        save_json(f'{PARENT_DIRECTORY}settings.json', settings)
    else:
        try:
            selected_language = settings.get('language', available_languages[0]['code'])
        except IndexError:
            selected_language = ''
    return render_template(
        'language.html',
        available_languages = available_languages,
        selected_language = selected_language.upper(),
        version = VERSION
    )

@app.route('/new_language', methods=['GET', 'POST'])
def new_language():
    language_options = language_codes()
    existing_languages = list_languages()
    for counter, lang in enumerate(language_options):
        if lang[1].strip().upper() in [l['code'] for l in existing_languages]:
            del language_options[counter]

    if request.method == 'POST':
        settings = load_settings()
        new_language = request.form.get('new_language')
        settings['language'] = new_language
        save_json(f'{PARENT_DIRECTORY}{new_language}_words.json', [])
        return redirect('/language')
    return render_template(
        'add_language.html',
        languages = language_options,
        version = VERSION
    )


@app.route('/schedule', methods=['GET', 'POST'])
def refresh():
    settings = load_settings()
    if request.method == 'POST':
        settings['refresh_after'] = int(request.form.get(
            'new_refresh_rate',
            settings['refresh_after']
        ))
        save_json(f'{PARENT_DIRECTORY}settings.json', settings)
    return render_template(
        'schedule.html',
        refresh_rate = settings['refresh_after'],
        version = VERSION
    )

@app.route('/shut_down', methods=['GET', 'POST'])
def shut_down():
    return render_template(
        'shut_down.html',
        version = VERSION
    )

@app.route('/confirm_shut_down', methods=['GET', 'POST'])
def confirm_shut_down():
    print('SHUTTING DOWN')
    os.system('sudo halt')
    return jsonify('System shut down')

# ============================================
#   BACK-END
# ============================================

def language_codes():
    with open(f'{THIS_DIRECTORY}language_list.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        return list(reader)

def delete_word(slug, language):
    words = load_words(language)
    for counter, saved_word in enumerate(words):
        if saved_word['slug'] == slug:
            break
    del words[counter]
    save_json(f'{PARENT_DIRECTORY}{language}_words.json', words)

def list_files(folder, extensions=None):
    file_list = []
    all_files = os.listdir(folder)
    for name in all_files:
        if extensions is not None:
            for ext in extensions:
                if name.endswith(ext):
                    file_list.append(f'{folder}{name}')
        else:
            file_list.append(f'{folder}{os.sep}{name}')
    return file_list

def list_languages():
    language_files = list_files(PARENT_DIRECTORY, ['_words.json'])
    iso_codes = language_codes()
    languages = []
    for filename in language_files:
        code = filename.split(os.sep)[-1].split('_')[0].upper()
        languages.append({
            'name':[l[0] for l in iso_codes if l[1].strip().upper() == code][0],
            'code':code,
            'file':filename
        })
    return languages

def load_settings():
    settings_file = f'{PARENT_DIRECTORY}settings.json'
    if os.path.exists(settings_file):
        settings = load_json(settings_file)
    else:
        settings = {
            "dislplay": {
                "width":640, #800
                "height":384 #480
            },
            "refresh_after":15,
            "language":''
        }
        save_json(settings_file, settings)
    return settings

def load_words(language):
    word_file = f'{PARENT_DIRECTORY}{language}_words.json'.lower()
    if os.path.exists(word_file):
        words = load_json(word_file)
    else:
        words = []
        save_json(word_file, words)
    for word in words:
        word['slug'] = f"{slugify(word['added'])}|{slugify(word['word'])}"
    return words

def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.loads(f.read())
        return data

def save_json(filename, data):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        f.write(json.dumps(data, indent=4))

def save_word(word, translation, example, language):
    words = load_words(language)
    words.append({
        'added':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'word':word,
        'translation':translation,
        'example':example
    })
    save_json(f'{PARENT_DIRECTORY}{language}_words.json'.lower(), words)

if __name__ == '__main__':
    app.run( host='0.0.0.0' )
