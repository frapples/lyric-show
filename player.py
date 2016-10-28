
import sys
import commandcall as call

"""
播放情况获取：
对于audacious播放器：
audtool --help 可得到如何利用audtool工具获取当前播放歌曲的信息
判断播放器是否打开：pgrep命令查看是否有对应的进程
"""

class AudaciousPlayer:
    '与audacious播放器交互，获取信息，控制播放器'
    name = "Audacious"


    @staticmethod
    def is_run():
        '''
        播放器是否在运行
        self参数可以为空，表明该方法可以当作静态方法来使用
        '''

        if not call.exist('audacious'):
            return False

        retcode, _, _ = call.call(["pgrep", "audacious"])
        return retcode == 0




    def get_current_second(self):
        '当前播放歌曲的进度，精确到秒'
        retcode, output,_ = call.call(["audtool", "current-song-output-length-seconds"])
        if (retcode != 0):
            return -1
        return int(output)




    def get_current_ms(self):
        """
        获取当前播放歌曲的进度，精确到毫秒

        思路是获得歌曲总帧数和总秒数，得到一帧大概是多少秒
        之后可以获取当前进行到的帧数，计算得出精确到微秒级的秒数
        """ 
        try:
            totalSecond = float(call.output(["audtool", "current-song-length-seconds"]))
            totalFrames = float(call.output(["audtool", "current-song-length-frames"]))
            currentFrame = float(call.output(["audtool", "current-song-output-length-frames"]))
        except ValueError as e:
            return 0

        return  currentFrame * (totalSecond / totalFrames)




    def get_current_path(self):
        return call.output(["audtool", "current-song-filename"]).strip()

