from anki.hooks import wrap
from anki.notes import Note
from aqt import gui_hooks, qconnect
from aqt.browser.browser import Browser
from aqt.reviewer import Reviewer
from aqt.qt import QWidget, QMenu

from .utils import get_fields_from_note_type
from .bulk_sentences import generate_sentences
from .choose_example_sentence import choose_example_sentence

_ADD_EXAMPLE_SENTENCE_LABEL = 'Add/change Example Sentence'
_ADD_EXAMPLE_SENTENCE_KEY = 'Ctrl+Shift+E'

_BULK_ADD_SENTENCE_LABEL = "Bulk-add Example Sentences (1 each)"

def add_example_sentence(parent: QWidget, note: Note):
    fields = get_fields_from_note_type(note)
    choose_example_sentence(parent, note, fields['word'], fields['sentence'])

# Shortcut keys while reviewing
def shortcut_keys_wrapped(self, _old):
    shortcuts = _old(self)
    shortcuts.append((_ADD_EXAMPLE_SENTENCE_KEY, lambda: add_example_sentence(\
        self.mw,\
        self.mw.col.get_note(self.card.nid)\
    )))

    return shortcuts

# Shows up when you click on the 'More' button while reviewing
def context_menu_wrapped(self, _old):
    opts = _old(self)

    opts.append(None) # Separator
    opts.append([_ADD_EXAMPLE_SENTENCE_LABEL, _ADD_EXAMPLE_SENTENCE_KEY, lambda: add_example_sentence(\
        self.mw,\
        self.mw.col.get_note(self.card.nid)\
    )])

    return opts

# Browser table context menu
def add_browser_context_menu_items(browser: Browser, menu: QMenu):
    menu.addSeparator()

    bulk_add_sentence_action = menu.addAction(_BULK_ADD_SENTENCE_LABEL)
    qconnect(bulk_add_sentence_action.triggered, lambda: generate_sentences(\
        browser.selected_notes(), browser\
    ))

    add_example_sentence_action = menu.addAction(_ADD_EXAMPLE_SENTENCE_LABEL)
    qconnect(add_example_sentence_action.triggered, lambda: add_example_sentence(\
        browser, browser.mw.col.get_note(browser.card.nid)\
    ))

def init():
    Reviewer._shortcutKeys = wrap(Reviewer._shortcutKeys, shortcut_keys_wrapped, 'around')
    Reviewer._contextMenu = wrap(Reviewer._contextMenu, context_menu_wrapped, 'around')

    gui_hooks.browser_will_show_context_menu.append(add_browser_context_menu_items)