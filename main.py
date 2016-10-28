#! /usr/bin/env python3
import sys, os, os.path
import logging
import json
import curses
# import threading

import player
import lyric
import displayer
import loop
import monitor

logging.basicConfig(level=logging.DEBUG,
        filename="mylog.log",
        filemode="w")

logging.debug("test")

def config_load(path):
    with open(path, "r") as f:
        return json.load(f)

CONFIG_PATH = "config.json"
g_config = config_load(CONFIG_PATH)
# ==============================================================================

def main():
    mon = monitor.Monitor()

    if g_config["method"] == "osd":
        displayer_ = displayer.LyricOsdDisplayer(g_config["osd_displayer"])
    elif g_config["method"] == "cli":
        displayer_ = displayer.LyricCliDisplayer(g_config["cli_displayer"])

    displayer_.set_monitor(mon)

    loop.loop_exec()


# ==============================================================================

try:
    try:
        main()
    # 把所有没处理的异常捕获到，关闭curses，再抛出
    except BaseException as e:
        loop.loop_quit()
        # 不加这个的话，异常信息会被curses挡住看不到，影响开发时定位错误
        if displayer.LyricCliDisplayer.is_curse_open():
            curses.endwin()
        raise e
except KeyboardInterrupt:
    print("\b\b  程序被用户打断。")
