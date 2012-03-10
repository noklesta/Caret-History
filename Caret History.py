#!/usr/bin/python
import os
import UserList
import sublime
import sublime_plugin


class Prefs():
    def load(self, view):
        Prefs.history_length = view.settings().get('caret_history_length', 10)


class Caret(sublime.Region):
    def __init__(self, view, a, b):
        sublime.Region.__init__(self, a, b)
        self.view = view
        self.file = self.get_file()
        self.line = self.get_line()
        self.coln = self.get_column()
        #print self

    def __getitem__(self):
        return (self.file, self.line, self.coln)

    def __repr__(self):
        return "%s: (%s, %s)" % (self.file, self.line, self.coln)

    def __eq__(self, other):
        if self.file == other.file:
            if self.line == other.line:
                if self.coln == other.coln:
                    return 1
        return 0

    def __ne__(self, other):
        return 0 if self == other else 1

    def get_line(self):
        return self.view.rowcol(self.begin())[0] + 1

    def get_column(self):
        return self.view.rowcol(self.end())[1] + 1

    def get_file(self):
        return self.view.file_name()

    def get_filename(self):
        file = self.get_file()
        if file:
            return file.split(os.path.sep)[-1]


class CaretList(UserList.UserList):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.index = 0

    # Return relative index value

    def current(self):
        return self.index

    def first(self):
        return 0

    def last(self):
        return 0 if not len(self.data) else len(self.data) - 1

    def previous(self):
        index = self.index - 1
        if index < self.first():
            index = self.first()
        return index

    def next(self):
        index = self.index + 1
        if index > self.last():
            index = self.last()
        return index

    # Set index value to...

    def mv_first(self):
        self.index = self.first()

    def mv_last(self):
        self.index = self.last()

    def mv_previous(self):
        self.index = self.previous()

    def mv_next(self):
        self.index = self.next()

    # Return self.data[value]...
    # doesn't modify index value.

    def get_current(self):
        return self.data[self.current()]

    def get_first(self):
        return self.data[self.first()]

    def get_last(self):
        return self.data[self.last()]

    def get_previous(self):
        return self.data[self.previous()]

    def get_next(self):
        return self.data[self.next()]

    # Grabbing a new one

    def truncate(self):
        if len(self.data) > Prefs.history_length:
            self.pop(0)

    def append(self, caret):
        if not len(self.data):
            self.data.append(caret)
        elif caret not in [self.get_current(), self.get_last(), self.get_previous(), self.get_next()]:
            self.data.append(caret)
            self.truncate()
            self.mv_last()


class CaretHistoryListener(sublime_plugin.EventListener):
    def on_selection_modified(self, view):
        Prefs().load(view)
        region = view.sel()[-1]
        caret = Caret(view, region.a, region.b)
        if caret.file:
            CARET_LIST.append(caret)


class CaretHistoryCommand(sublime_plugin.TextCommand):
    def run(self, edit, action):
        method = getattr(self, action)
        if method:
            method()

    def previous(self):
        Prefs().load(self.view)
        CARET_LIST.mv_previous()
        caret = CARET_LIST.get_current()
        self.open_file(caret)

    def next(self):
        Prefs().load(self.view)
        CARET_LIST.mv_next()
        caret = CARET_LIST.get_current()
        self.open_file(caret)

    def open_file(self, caret):
        print caret
        file = "%s:%d:%d" % (caret.file, caret.line, caret.coln)
        if self.view.window():
            self.view.window().open_file(file, sublime.ENCODED_POSITION)


# Main ()
CARET_LIST = CaretList()
