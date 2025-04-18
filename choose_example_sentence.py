from aqt import colors
from aqt.browser.browser import Browser
from aqt.operations import QueryOp
from aqt.operations.note import update_note
from aqt.theme import theme_manager
from aqt.qt import *
from PyQt5 import QtCore

from .example_sentences import *
from .utils import *

_ACTION_NAME = 'Choose Example Sentence'

class ChooseExampleSentenceDialog(QDialog):
    sentence = ''

    def __init__(self, word: str, parent: QWidget = None):
        super().__init__(parent)

        self.word = word

        # Window icon
        self.window_icon = QIcon()
        self.window_icon.addPixmap(QPixmap(":/icons/anki.png"), QIcon.Normal, QIcon.Off)

        self.setWindowTitle(_ACTION_NAME)
        self.setWindowIcon(self.window_icon)

        # Layout
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(12, 18, 18, 12)
        self.layout.setSpacing(16)

        # Heading text
        heading_font = QFont()
        heading_font.setPixelSize(18)

        self.heading = QLabel()
        self.heading.setText(_ACTION_NAME)
        self.heading.setFont(heading_font)
        self.heading.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.layout.addWidget(self.heading)

        # List view
        list_font = QFont()
        list_font.setFamily('Yu Gothic')
        list_font.setPixelSize(18)

        self.list_view = QListView()
        self.list_model = self.load_list()
        
        self.list_view.setSpacing(4)
        self.list_view.setFont(list_font)
        self.list_view.setSelectionMode(QListView.SelectionMode.SingleSelection)

        style = '''
            QListView {{
                outline: none;
            }}

            QListView::item {{
                border-bottom: 1px solid grey;
                padding: 8px;
            }}

            QListView::item::selected {{
                background-color: {};
                color: {};
            }}
        '''.format(\
            '#529bc7' if theme_manager.night_mode else 'rgba(150, 150, 150, 50)',\
            theme_manager.color(colors.HIGHLIGHT_FG) if theme_manager.night_mode else 'black'\
        )

        self.list_view.setStyleSheet(style)
        self.list_view.setModel(self.list_model)

        self.layout.addWidget(self.list_view)

        # Button box
        buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.button_box = QDialogButtonBox(buttons)

        qconnect(self.button_box.accepted, self.accept)
        qconnect(self.button_box.rejected, self.reject)

        self.layout.addWidget(self.button_box)

        self.setLayout(self.layout)
        self.resize(720, 480)

    def load_list(self) -> QStandardItemModel:
        model = QStandardItemModel(self.list_view)

        def load_sentences(_):
            soup = get_soup_instance(self.word)
            self.sentences = get_all_sentences_from_page(soup)

        def load_model(_):
            for sentence in self.sentences:
                sentence_item = QStandardItem(sentence)
                sentence_item.setEditable(False)

                model.appendRow(sentence_item)

        QueryOp(parent=self, op=load_sentences, success=load_model).with_progress(_ACTION_NAME).run_in_background()
        return model

    def accept(self):
        selected_indexes = self.list_view.selectedIndexes()

        if len(selected_indexes) == 0:
            QMessageBox.warning(self, _ACTION_NAME, 'Please select an example sentence to add')
            return

        self.sentence = selected_indexes[0].data()
        super().accept()

    def reject(self):
        super().reject()

# Lets the user choose which example sentence they want to add to the note
def choose_example_sentence(parent: QWidget, note: Note, word_field: str, sentence_field: str):
    if not can_fill_note(note, word_field, sentence_field):
        return

    dialog = ChooseExampleSentenceDialog(note[word_field], parent)
    if dialog.exec():
        sentence = dialog.sentence
        if should_auto_generate_furigana():
            sentence = generate_furigana(sentence)

        note[sentence_field] = sentence
        update_note(parent=parent, note=note).run_in_background()

def choose_example_sentence_action(browser: Browser):
    note = browser.mw.col.get_note(browser.card.nid)
    fields = get_fields_from_note_type(note)

    choose_example_sentence(browser, note, fields['word'], fields['sentence'])

def add_menu_items(browser: Browser):
    # Creates a menu item and adds it under the 'Edit' category
    action = QAction('Add/Change Example Sentence', browser)
    qconnect(action.triggered, lambda: choose_example_sentence_action(browser))
    browser.form.menuEdit.addAction(action)

def init():
    if ANKI21_VERSION < 45:
        from anki.hooks import addHook
        addHook('browser.setupMenus', add_menu_items)
    else:
        from aqt import gui_hooks
        gui_hooks.browser_menus_did_init.append(add_menu_items)