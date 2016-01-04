# -*- coding: utf-8 -*-
import webbrowser
from PyQt4.QtGui import QIcon, QTableWidgetItem
from multiprocess import Pool

import pyforms
from pyforms import BaseWidget
from pyforms.Controls import ControlList
from pyforms.Controls import ControlText
from pyforms.Controls import ControlButton
from pyforms.gui.Controls.ControlCheckBoxList import ControlCheckBoxList

from config import CONFIG, create_bot_from_config
from group_bot import GroupBot


class PopUpGetText(BaseWidget):
    def __init__(self, name, target):
        super(PopUpGetText, self).__init__('Add {}'.format(name))

        self.target = target

        self._text = ControlText('')

        self._add_button = ControlButton('Add')
        self._add_button.value = self.__add_action

        self._cancel_button = ControlButton('Cancel')
        self._cancel_button.value = self.__cancel_action

        self._formset = [('', '_text', ''), ('', '_add_button', '_cancel_button', '')]

    def __add_action(self):
        self.target += self._text.value
        self.close()

    def __cancel_action(self):
        self.close()

class UnicodeControlList(ControlList):
     def __add__(self, other):

        index = self.tableWidget.rowCount()

        self.tableWidget.insertRow(index)
        if self.tableWidget.currentColumn() < len(other):
            self.tableWidget.setColumnCount(len(other))

        for i in range(0, len(other)):
            v = other[i]
            args = [unicode(v)] if not hasattr(v, 'icon') else [QIcon(v.icon), unicode(v)]
            self.tableWidget.setItem(index, i, QTableWidgetItem(*args))

        self.tableWidget.resizeColumnsToContents()
        return self

class GuiList:
    def __init__(self, list, control_list):
        self.list = list
        self.control_list = control_list
        for elem in list:
            control_list += [elem]

    def __add__(self, other):
        self.list += other
        self.control_list += [other]

    def remove(self, index):
        self.list.pop(index)
        self.control_list -= index

class GroupCheckerGui(BaseWidget):

    def __init__(self):
        super(GroupCheckerGui, self).__init__('Group Checker')

        self._group_name = ControlText('Group Name', CONFIG['group_name'])
        self._group_name.enabled = False
        self._allowed_tags = UnicodeControlList('Allowed Tags',
                                               plusFunction=self.__add_tag_action,
                                               minusFunction=self.__remove_tag_action)
        self.allowed_tags = GuiList(CONFIG['white_filters']['SubstringFilter']['substrings'],
                                    self._allowed_tags)

        self._allowed_ids = ControlList('Allowed Ids',
                                        plusFunction=self.__add_id_action,
                                        minusFunction=self.__remove_id_action)
        self.allowed_ids = GuiList(CONFIG['white_filters']['SignerFilter']['ids'], self._allowed_ids)

        self._bad_posts = ControlCheckBoxList('Bad posts')
        self._bad_posts._form.listWidget.itemDoubleClicked.connect(self.__show_link_action)

        self._remove_button = ControlButton('Remove')
        self._remove_button.value = self.__remove_action

        self._show_button = ControlButton('Show bad posts')
        self._show_button.value = self.__show_bad_post_action

        self.pool = Pool(processes=1)
        self.bad_posts = []

        self._formset = [('', '_group_name', ''),
                         ('', '_allowed_tags', '_allowed_ids', ''),
                         '',
                         ('', '_bad_posts', ''),
                         ('', '_remove_button', '_show_button', ''),
                         '']

    def __add_tag_action(self):
        win = PopUpGetText('tag', self.allowed_tags)
        win.show()

    def __remove_tag_action(self):
        self.allowed_tags.remove(self._allowed_tags.mouseSelectedRowIndex)

    def __add_id_action(self):
        win = PopUpGetText('id', self.allowed_ids)
        win.show()

    def __remove_id_action(self):
        self.allowed_ids.remove(self._allowed_ids.mouseSelectedRowIndex)

    def __show_bad_post_action(self):
        def callback(posts):
            self.bad_posts = posts
            self._bad_posts.value = [(GroupBot.get_link_from_post(post, CONFIG['group_name']), True) for post in posts]
            self._show_button.enabled = True

        def run_bot():
            bot = create_bot_from_config()
            return bot.get_bad_posts()

        self._show_button.enabled = False
        self.pool.apply_async(run_bot, callback=callback)

    def __show_link_action(self, link):
        webbrowser.open(link.text())

    def __remove_action(self):
        checked_posts = [self.bad_posts[idx] for idx in self._bad_posts.checkedIndexes]
        bot = create_bot_from_config()
        bot.remove_posts(checked_posts)

if __name__ == "__main__":
    pyforms.startApp(GroupCheckerGui)
