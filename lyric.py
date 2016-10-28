#! /usr/bin/env python3

import os.path
import re
import zlib
import logging


def new_lyric_object(song_path, type_="krc", try_all=False):
    if try_all:
        if type_ == "lrc":
            queue = ["lrc", "krc"]
        if type_ == "krc":
            queue = ["krc", "lrc"]
    else:
        queue = [type_]

    type_to_class = {"lrc": LrcLyric, "krc": KugouLyric}

    for type_ in queue:
        path = songpath_to_lycpath(song_path, type_)
        if os.path.exists(path):
            return type_to_class[type_](path)
    return None





def songpath_to_lycpath(song_path, type_="krc"):
    noext_path, _ = os.path.splitext(song_path)
    return noext_path + "." + type_

def locate_in_sorted(sorted_list, search):
    "从一组排序的数字里，找到自己的位置。位置编号类似切片"
    if len(sorted_list) == 0 or search < sorted_list[0]:
        return 0

    for i in range(1, len(sorted_list)):
        prev = sorted_list[i - 1]
        this_ = sorted_list[i]
        if prev <= search < this_:
            return i
    return len(sorted_list)

# ==============================================================================

class LrcLyric():
    """ 该类表示歌词。可从文件路径建立歌词对象。可从播放进度更新当前唱的句子 """

    def __init__(self, path):
        with open(path, "r") as f:
            self._sentences = self._parse(f)


    def is_end(self, lineno):
        return lineno > len(self._sentences)

    def locate_position(self, current_time):
        return locate_in_sorted([time_ for time_, sentence in self._sentences], current_time)


    def get_position(self, lineno):
        if (lineno <= 0) or self.is_end(lineno):
            return ""
        return self._sentences[lineno][1]

    def get_offset(self, current_time):
        """
        得到当前唱到该句歌词的那个字了（对于lrc歌词，进度显然是按比例计算的）
        """
        lineno = self.locate_position(current_time)
        time_, sentence = self._sentences[lineno]
        # 最后一句歌词，没有办法。。。
        if self.is_end(lineno):
            return len(sentence)

        next_time, _ = self._sentences[lineno + 1]

        total = next_time - time_
        crrnt = current_time - time_

        assert(crrnt <= total)

        return round(crrnt / total * len(sentence))

    def _parse(self, f):
        sentences = list()
        for line in f.readlines():
            times = list()
            while True:
                m = re.match(r"\s*\[([0-9.:]+)\](.*)", line)
                if m == None:
                    break
                times.append(m.group(1))
                line = m.group(2)

            for time in times:
                time = time.split(":")
                time = int(time[0]) * 60 + float(time[1])
                sentences.append((time, line))

        sentences.sort(key=lambda t:t[0])
        return sentences

# ==============================================================================

class KugouLyric():
    def __init__(self, path):
        with open(path, "rb") as f:
            self._sentences = self.__parse(self.krc_decode(f.read()).decode())

    def is_end(self, lineno):
        return lineno > len(self._sentences)

    def get_sentence(self, lineno):
        if (lineno <= 0) or self.is_end(lineno):
            return ""
        line = self._sentences[lineno - 1]

        sentence = ""
        for _, s in line:
            sentence += s
        return sentence


    def locate_position(self, current_time):
        return locate_in_sorted([line[0][0] for line in self._sentences], current_time)


    def get_offset(self, current_time):
        "返回将要唱到的那个字块在本行的offset"
        line = self._sentences[self.locate_position(current_time) - 1]
        index = locate_in_sorted([time_ for time_, _ in line], current_time)
        offset = 0
        for time_, s in line[0:index]:
            offset += len(s)
        return offset


    def __parse(self, s):
        sentences = list()
        for line in s.split("\r\n"):
            m = re.match(r"\s*\[(\d+),(\d+)\](.*)\s*", line)
            if m == None: continue
            line_start_time = int(m.group(1)) / 1000
            line = m.group(3) + "<"

            sentence = list()
            while True:
                m = re.match(r"<(\d+),\d+,\d+>(.*?)(<.*)", line)
                if m == None: break
                relative_time = float(m.group(1))
                text = m.group(2)
                sentence.append((line_start_time + relative_time / 1000,text))

                line = m.group(3)

            sentences.append(sentence)

        sentences.sort(key=lambda t:t[0][0])
        return sentences

    def krc_decode(self, s):
        head = s[0:4]
        if head.decode() != "krc1":
            raise ValueError("貌似不是krc歌词文件！(krc歌词文件头四字节是krc1)")

        # python的byte类型不能直接对单个字节赋值，要转为bytearray
        key =  [64, 71, 97, 119, 94, 50, 116, 71, 81, 54, 49, 45, 206, 210, 110, 105]
        s = bytearray(s[4:])

        for i in range(len(s)):
            s[i] = s[i] ^ key[i % len(key)]
        res = zlib.decompress(s)
        return res



# ==============================================================================


if __name__ == "__main__":

    print(KugouLyric("/media/removable/SD Card/music/少司命/少司命 - 宿命.krc")._sentences)

