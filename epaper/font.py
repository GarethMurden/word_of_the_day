import os
from fontTools.ttLib import TTFont
from fontTools.unicode import Unicode

dirname, scriptname = os.path.split(os.path.abspath(__file__))
THIS_DIRECTORY = f'{dirname}{os.sep}'

def get_fonts(language_code, phrase):
    font_file = f'{THIS_DIRECTORY}fonts{os.sep}NotoSans.ttf' # default font

    # language-specific fonts
    font_files = list_files(f'{THIS_DIRECTORY}fonts{os.sep}', ['ttf', 'otf'])
    for filename in font_files:
        if language_code in filename.split(os.sep)[-1]:
            font_file = filename
            break

    # fallback
    print(f'\nLanguage:               "{language_code}"')
    if not render_succesfull(phrase, font_file):
        print(f'Failed to render with:  "{font_file.split(os.sep)[-1]}"')
        font_file = f'{THIS_DIRECTORY}fonts{os.sep}unifont.ttf'       
    print(f'Using font:             "{font_file.split(os.sep)[-1]}"\n')
    
    return font_file

def list_files(folder, extensions=None):
    file_list = []
    all_files = os.listdir(folder)
    for name in all_files:
        if extensions is not None:
            for ext in extensions:
                if name.endswith(ext):
                    file_list.append(f'{folder}{os.sep}{name}')
        else:
            file_list.append(f'{folder}{os.sep}{name}')
    return file_list

def render_succesfull(input_string, font_file):
    font = TTFont(font_file)
    for glyph in input_string:
        for table in font['cmap'].tables:
            if not ord(glyph) in table.cmap.keys():
                return False
    return True

if __name__ == '__main__':
    print(get_fonts('VI', 'xin chào'))