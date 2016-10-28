#! /usr/bin/python3

import subprocess
import shlex

def exist(name):
    return subprocess.call(('which', name), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

def call(args, encoding='utf8'):
    if isinstance(args, str):
        args = shlex.split(args)

    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    return p.returncode, stdout.decode(encoding), stderr.decode(encoding)

def output(args, encoding='utf8'):
    _, stdout, _ = call(args, encoding)
    return stdout
