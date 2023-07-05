from .mecab_controller import MecabController
from .utils import *

mecab = MecabController(skip_words=get_furigana_skip_words())

def generate_furigana(expr: str) -> str:
    return mecab.reading(expr)