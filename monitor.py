import eventsignal
import loop
import player as playerbackend

# TODO: backend的API还没有标准化
class Monitor:
    """监视播放器的状态"""

    player_backend = (playerbackend.AudaciousPlayer(), )

    def __init__(self):
        self._player_open_signal = eventsignal.Signal()
        self._player_close_signal = eventsignal.Signal()
        self._song_change_signal = eventsignal.Signal()
        self._song_time_change_signal = eventsignal.Signal()

        loop.loop_add(self.loop)

    @property
    def player_open_signal(self):
        return self._player_open_signal

    @property
    def player_close_signal(self):
        return self._player_close_signal

    @property
    def song_change_signal(self):
        return self._song_change_signal

    @property
    def song_time_change_signal(self):
        return self._song_time_change_signal

    def _current_running_player(self):
        for backend in self.player_backend:
            if backend.is_run():
                return backend
        return None

    def loop(self):
        last_player = None
        last_song_path = None
        last_time = None

        while True:
            # 注意先通知播放器改变再通知歌曲改变再通知时间改变
            player = self._current_running_player()
            if (last_player != player):
                if last_player is None:
                    player_name =  ""
                else:
                    player_name = last_player.name
                self.player_close_signal.emit(player_name)
                self.player_open_signal.emit(player_name)
                last_player = player

            if player is not None:
                song_path = player.get_current_path()
                if song_path != last_song_path:
                    self.song_change_signal.emit(song_path)
                    last_song_path = song_path

                time_ = player.get_current_ms()
                if time_ != last_time:
                    self.song_time_change_signal.emit(time_ + 0.02)
                    last_time = time_
            yield


