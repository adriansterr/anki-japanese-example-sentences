import aqt
import re

from typing import List

from aqt import mw
from anki.notes import Note

ANKI21_VERSION = int(aqt.appVersion.split('.')[-1])
NUMBERS = ['一二三四五六七八九十０１２３４５６７８９']

def get_config():
    return mw.addonManager.getConfig(__name__)

def should_auto_generate_furigana() -> bool:
    return config.get('auto_furigana') is True

def get_furigana_skip_words() -> List[str]:
    words = re.split(r'[, ]+', config.get('furigana_skip_words', ''), flags=re.IGNORECASE)

    if config.get('furigana_skip_numbers') is True:
        words += NUMBERS

    return words

def get_note_type(note: Note) -> dict:
    if hasattr(note, 'note_type'):
        return note.note_type()
    else:
        return note.model()

def get_fields_from_note_type(note: Note) -> dict:
    if not config['fields']:
        return None

    note_type = get_note_type(note)['name']

    for fields in config['fields']:
        if fields['note_type'].lower() in note_type.lower():
            return fields

config = get_config()