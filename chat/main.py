import logging
import sys

from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import QApplication, QMessageBox
from chat.forms import main_form
from chat.client import ChatClient
from utils import *
from resp import *

logger = logging.getLogger('chat')
app = QApplication(sys.argv)
window = main_form.MainWindow()
login = ""

def load_server_config(file_path):
    setup_dict = {'host': '127.0.0.1', 'port': 7777}
    with open(file_path, 'r') as file:
        for line in file:
            try:
                key, value = line.strip().split('=')
                setup_dict[key.strip()] = value.strip()
            except ValueError:
                pass
    return setup_dict


def renew_contact_list():
    try:
        contacts = chat.send_get_contacts(login).alert
    except Exception:
        pass
    else:
        for contact in contacts:
            item = QStandardItem(contact)
            window.ui.model.appendRow(item)
        chat.db.renew_contacts(contacts)


def btn_add_clicked():
    contact_login = window.ui.txt_search.text()
    resp = chat.send_add_contact(login, contact_login)
    logger.info(resp)
    if resp.response != NOT_FOUND_404:
        item = QStandardItem(contact_login)
        window.ui.model.appendRow(item)
    else:
        window.show_ok_dialog("Пользователь не найден")



def btn_remove_clicked():
    try:
        index = window.ui.lst_contacts.selectedIndexes()[0]
    except Exception:
        window.show_ok_dialog("Пользователь не выбран")
    else:
        contact_login = window.ui.model.itemFromIndex(index).text()
        answer = window.show_yes_no_dialog(f"Вы уверены что хотите удалить контакт {contact_login}")
        if answer:
            resp = chat.send_remove_contact(login, contact_login)
            if resp.response == CONFIRMATION_202:

                if index:
                    window.ui.model.removeRow(index.row())
            else:
                window.show_ok_dialog("Пользователь не найден")



def item_selected(index: QModelIndex):
    selected_item = window.selected_contact_item_text
    window.ui.txt_chat.setText(f'chat({selected_item})')


def events():
    window.ui.btn_add.clicked.connect(btn_add_clicked)
    window.ui.btn_remove.clicked.connect(btn_remove_clicked)
    window.ui.lst_contacts.clicked.connect(item_selected)
    #window.ui.lst_contacts.rig


if __name__ == '__main__':
    args = sys.argv
    try:
        db_path = args[1]
    except IndexError:
        db_path = 'chat.sqlite.db'

    settings = load_server_config('config.ini')
    HOST = settings['host']
    PORT = int(settings['port'])
    chat = ChatClient(HOST, PORT, db_path)
    profile = chat.db.get_my_profile()

    window.show()
    events()
    try:
        login = profile.login
    except AttributeError:
        login = window.open_login_dialog()
    if login == '' or login is None:
        sys.exit()
    title = window.windowTitle()
    window.setWindowTitle(f'{title} [{login}@{HOST}:{PORT}]')
    prof = chat.send_login(login)
    if prof:
        prof = prof.client
        chat.db.renew_profile(prof['login'], prof['name'], prof['surname'], str2date(prof['birthday_date']), prof['status'])
    renew_contact_list()

    sys.exit(app.exec_())
