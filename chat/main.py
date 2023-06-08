import logging
import sys
from PyQt5.QtCore import QThread
from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import QApplication
from forms import main_form
from client import ChatWatch
from utils import *
from resp import *
from config import *

logger = logging.getLogger('chat')


class ChatApp:
    def __init__(self, host, port, db_path):
        self.chat = ChatWatch(self, host, port, db_path)
        self.thread1 = QThread()
        self.chat.moveToThread(self.thread1)
        self.thread1.started.connect(self.chat.start)
        self.chat.gotData.connect(self.new_message)
        self.chat.start()
        self.chat.watcher()

        self.app = QApplication(sys.argv)
        self.window = main_form.MainWindow()
        self.login = ""
        self.active_chat = ""
        self.window.show()
        self.events()
        self.login_on_server()
        title = self.window.windowTitle()
        self.window.setWindowTitle(f'{title} [{self.login}@{host}:{port}]')
        self.renew_contact_list()
        sys.exit(self.app.exec_())


    def new_message(self):
        while len(self.chat.chat.messages) > 0:
            msg = ObjDict(self.chat.chat.messages.pop(0))
            self.chat.mess_len -= 1
            from_login = msg.login
            to_login = msg.contact_login
            time = datetime.fromtimestamp(msg.time)
            text = msg.message
            text = self.chat.chat.db.add_message(from_login, to_login, text, time)
            if from_login == self.active_chat:
                self.window.ui.txt_chat.append(text)

    def login_on_server(self):
        profile = self.chat.chat.db.get_my_profile()
        try:
            self.login = profile.login
        except AttributeError:
            self.login = self.window.open_login_dialog()
        if self.login == '' or self.login is None:
            sys.exit()
        #abc = self.chat.chat.refresh_keys()
        prof = self.chat.chat.send_login(self.login)
        try:
            prof = prof.client
            self.chat.chat.db.renew_profile(prof['login'], prof['name'], prof['surname'],
                                       str2date(prof['birthday_date']), prof['status'])
        except AttributeError:
            logger.info('Авторизация, нет связи')

    def renew_contact_list(self):
        try:
            contacts = self.chat.chat.send_get_contacts(self.login).alert
        except Exception:
            logger.info('Обновление контактов, нет связи')
        else:
            for contact in contacts:
                item = QStandardItem(contact)
                self.window.ui.model.appendRow(item)
            self.chat.chat.db.renew_contacts(contacts)

    def btn_add_clicked(self):
        contact_login = self.window.ui.txt_search.text()
        if contact_login:
            resp = self.chat.chat.send_add_contact(self.login, contact_login)
            logger.info(resp)
            if resp.response != NOT_FOUND_404:
                item = QStandardItem(contact_login)
                self.window.ui.model.appendRow(item)
                self.window.ui.txt_search.setText("")
            else:
                self.window.show_ok_dialog("Пользователь не найден")
        else:
            self.window.show_ok_dialog("Введите login")

    def btn_remove_clicked(self):
        try:
            index = self.window.ui.lst_contacts.selectedIndexes()[0]
        except Exception:
            self.window.show_ok_dialog("Пользователь не выбран")
        else:
            contact_login = self.window.ui.model.itemFromIndex(index).text()
            answer = self.window.show_yes_no_dialog(f"Вы уверены что хотите удалить контакт {contact_login}")
            if answer:
                resp = self.chat.chat.send_remove_contact(self.login, contact_login)
                answer = self.window.show_yes_no_dialog(f"Удалить историю сообщений?")
                if answer:
                    self.chat.chat.db.clear_history(contact_login, self.login)
                if resp.response == CONFIRMATION_202:
                    self.window.ui.model.removeRow(index.row())
                    self.window.ui.txt_search.setText(contact_login)
                    self.window.ui.txt_chat.setText("")
                else:
                    self.window.show_ok_dialog("Пользователь не найден")

    def item_selected(self):
        try:
            index = self.window.ui.lst_contacts.selectedIndexes()[0]
        except Exception:
            self.window.show_ok_dialog("Пользователь не выбран")
        else:
            self.active_chat = self.window.ui.model.itemFromIndex(index).text()
            self.renew_chat()

    def send_btn_click(self):
        text = self.window.ui.txt_send.text()
        if text:
            resp = self.chat.chat.send_message(self.login, self.active_chat, text)
            if resp.status == CONFIRMATION_202:
                if self.login != self.active_chat:
                    res = self.chat.chat.db.add_message(self.login, self.active_chat, text)
                    self.window.ui.txt_chat.append(res)
                self.window.ui.txt_send.setText('')
            else:
                if resp.status == OFFLINE_410:
                    self.window.show_ok_dialog("Пользователь оффлайн")
                else:
                    self.window.show_ok_dialog("Пользователь не найден")
        else:
            self.window.show_ok_dialog("Введите текст сообщения")

    def renew_chat(self):
        self.window.ui.txt_chat.setText('')
        history = self.chat.chat.db.get_chat_history(self.active_chat, self.login)
        for msg in history:
            self.window.ui.txt_chat.append(msg)


    def events(self):
        self.window.ui.btn_add.clicked.connect(self.btn_add_clicked)
        self.window.ui.btn_remove.clicked.connect(self.btn_remove_clicked)
        self.window.ui.lst_contacts.doubleClicked.connect(self.item_selected)
        self.window.ui.btn_send.clicked.connect(self.send_btn_click)


if __name__ == '__main__':
    args = sys.argv
    try:
        db_path = args[1]
    except IndexError:
        db_path = DB_DEF_NAME
    settings = load_server_config(SRV_CFG_FILE_NAME)
    host = settings['host']
    port = int(settings['port'])
    chat_app = ChatApp(host, port, db_path)
