_loops = []
_is_quit = False

def loop_add(loop):
    "传入的loop是协程，不是生成器"
    _loops.append(loop())

def loop_exec():
    i = 0
    while (not _is_quit):
        _loops[i].__next__()
        i = (i + 1) % len(_loops)

def loop_quit():
    global _is_quit
    _is_quit = True
