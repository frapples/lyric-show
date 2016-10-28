import curses
import lyric
import os.path

class LyricOsdDisplayer():
    def __init__(self):
        super().__init__()

    def start(self):
        pass

    def stop(self):
        self.show_space()

    def show_space(self):
        msg = '<message id="lrcdis" osd_fake_translucent_bg="off" hide_timeout="1"></message>'
        subprocess.call(["gnome-osd-client", "-f", msg])

    def __sung_msg(self, s):
        return '<span foreground="%s">%s</span>' % (self._sungColor, s)

    def __other_msg(self, s):
        return '<span foreground="%s">%s</span>' % (self._otherColor, s)

    def flush(self):
        if not self._lyric.currentSentence:
            self.show_space() # 用来解决输出空字符时会将残留上次的一些字符，应该是gnome-osd的软件问题

        nextMsg = ""; previousMsg = ""
        if self._lyric.currentOrd % 2 == 1:
            previousMsg = self.__sung_msg(self._lyric.previousSentence)
        else:
            nextMsg = self.__other_msg(self._lyric.nextSentence)

        currentMsgSung = self.__sung_msg(self._lyric.currentSentence[0:self._progress["char"]])
        currentMsgOther = self.__other_msg(self._lyric.currentSentence[self._progress["char"]:])

        msg = """<message id="lrcdis" osd_fake_translucent_bg="off" animations="off" hide_timeout="10000">%s   %s%s   %s
        </message>"""
        subprocess.call(["gnome-osd-client", "-f", msg % (previousMsg, currentMsgSung, currentMsgOther, nextMsg)])


class LyricCliDisplayer():
    __is_curse_open = False

    @classmethod
    def is_curse_open(cls):
        return cls.__is_curse_open

    @classmethod
    def curse_open(cls):
        if not cls.__is_curse_open:
            curses.initscr()
            cls.__is_curse_open = True


    @classmethod
    def curse_close(cls):
        if cls.__is_curse_open:
            curses.endwin()
            self.__is_curse_open = False

    def get_config(self, key):
        return self._config[key]


    def __init__(self, config):
        self._config = config

        self.start()

    def set_monitor(self, mon):
        def song_time_change(ms):
            self.flush(ms)

        def player_open(player_name):
            self.show_no_player()

        def song_change(song_path):
            self._title = os.path.basename(song_path)
            self._lyric = lyric.new_lyric_object(song_path, "krc", True)

        mon.song_time_change_signal.bind(song_time_change)
        mon.player_open_signal.bind(player_open)
        mon.song_change_signal.bind(song_change)

    def start(self):
        self.curse_open()
        curses.start_color()
        curses.use_default_colors()
        curses.noecho()
        curses.curs_set(False)

        # 注意还有box的上下两行，标题占三行
        height = self.get_config('lines') + 2 + 3
        width = self.get_config('width')
        width = width if width < curses.COLS else curses.COLS

        self.__win = curses.newwin(height, width, 1, curses.COLS // 2 - width // 2) # 在中间显示
        self.__win.box()
        self.__win.refresh()


    def stop(self):
        pass


    def _lyric_not_exist(self):
        self._head()
        self.__add_line("未检测到歌词文件, 敬请欣赏")
        self.__win.refresh()

    def show_no_player(self):
        self.__win.clear()
        self.__win.box()
        self.__add_line("提示：没有检测到运行的播放器 :(")
        self.__win.refresh()



    def flush(self, ms):
        self._head()

        if not self._lyric:
            self._lyric_not_exist()
            return

        up_cnt = (self.get_config('lines') - 1) // 2
        down_cnt = (self.get_config('lines') - 1) - up_cnt

        lineno = self._lyric.locate_position(ms)

        # 唱过的
        for i in range(lineno - up_cnt, lineno):
            self.__add_line(self._lyric.get_sentence(i))

        # 当前唱的
        curses.init_pair(1, curses.COLOR_YELLOW, -1)
        self.__add_line(self._lyric.get_sentence(lineno), curses.color_pair(1), self._lyric.get_offset(ms))

        # 马上要唱的
        for i in range(lineno + 1, lineno + 1 + down_cnt):
            self.__add_line(self._lyric.get_sentence(i))

        self.__win.refresh()


    def _head(self):
        self.__win.clear()
        self.__win.box()

        self.__add_line("========== 歌词显示 ==========", curses.A_BOLD)

        self.__add_line("*** %s ***" % self._title, curses.A_BOLD)
        self.__add_line("")

    def __add_line(self, s, fmt=None, n=None, line=None):
        _, length = self.__win.getmaxyx(); length -= 2
        pre_space = (length - str_width(s)) // 2

        if n is None:
            n = len(s)

        if line is None:
            y, x = self.__win.getyx()
            if y == 0:
                line = 1
            else:
                line = y + 1

        if not fmt:
            self.__win.addstr(line, pre_space + 1, s)
        else:
            self.__win.addstr(line, pre_space + 1, s[0:n], fmt)
            self.__win.addstr(s[n:])


# 汉字占两个宽度，英文字母占一个宽度
def str_width(s):
    return (len(s.encode()) + len(s)) // 2
