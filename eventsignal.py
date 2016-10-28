
class Signal():
    def __init__(self):
        self._callback = list()

    def bind(self, callback):
        self._callback.append(callback)

    def emit(self, *args, **kwargs):
        for callback in self._callback:
            callback(*args, **kwargs)



