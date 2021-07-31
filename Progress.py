import re
import subprocess
import math
import platform
from shutil import which
import os
import time


class ProgressFFmpeg(object):
    def __init__(self, file):
        self.callback = None
        self.precent = 0
        self.re_duration = re.compile('Duration: (\d{2}):(\d{2}):(\d{2}).(\d{2})[^\d]*', re.I)
        self.re_position = re.compile('time=(\d{2}):(\d{2}):(\d{2})\.(\d{2})\d*', re.U | re.I)
        self.total = None
        self.time = None
        self.is_allowed = True if which("ffmpeg") else False
        self.total = None
        self.time = None
        self.file = file
        
    def export(self, output, cmd=None):
        if not self.is_allowed:
            self.callback.on_error("ffmpeg not found in your Systeam did you want to download it?", do="confirm")
            return
        cmd = cmd if cmd else 'ffmpeg -i "{file}" -vn -acodec pcm_s16le -ar 44100 -ac 2 "{output}'.format(file=self.file, output=output)
        pipe = subprocess.Popen(cmd, shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines = True)
        while True:
            line = pipe.stdout.readline().strip()
            if line == '' and pipe.poll() is not None:
                break
            if line.count("Conversion failed"):
                self.callback.on_error("Conversion failed!", do="show")
                return
                break

            if self.total is None:
                self.total = self.get_duration(line)
            self.time = self.get_time(line)
            if self.time is None:
                continue
            percent, current, total = self.get_perecent(self.total, self.time)
            self.callback.on_progress(percent, current, total)
        self.callback.on_finish()
        pipe.kill()

    def set_callback(self, callback: classmethod):
        self.callback = callback

    def get_duration(self, string):
        result = None
        if string.count("Duration"):
            result = self.re_duration.match(string)
            result = str(result.group(0)).split()
            result = result[1].replace(",", "")
        return result
    
    def get_time(self, string):
        result = None
        if string.count("time="):
            result = self.re_position.search(string)
            result = str(result.group(0)).replace("time=", "")
        return result

    def get_perecent(self, a, b):
        a = a.split(":")
        b = b.split(":")
        a1, a2, a3 = self.get_int(a)
        b1, b2, b3 = self.get_int(b)
        a_total = a1 * 3600 + a2 * 60 + a3
        b_total = b1 * 3600 + b2 * 60 + b3
        res = self.get_result(b_total, a_total)
        return res, b_total, a_total

    def get_int(self, _list: list):
        f = "("
        for x in _list:
            if len(x) <= 2:
                f += str(int(x))+","
            else:
                f += str(int(float(x)))+","
        f = f[:-1]
        f += ")"
        return eval(f)

    def get_result(self, how, total):
        return int(how / total * 100)

class Callback:
    def on_error(self, msg, do=None):
        print(msg, do)

    def on_progress(self, percent, current, total):
        print(percent, current, total)

    def on_finish(self):
        print("Cover finish!!")
        
#cover = ProgressFFmpeg("P:/streaming/videos/Red Dead Redemption 2/Red Dead Redemption 2 2021.07.30 - 05.38.56.03.mp4")
#cover.set_callback(Callback())
#cover.export("P:/streaming/videos/Red Dead Redemption 2/red_dead_redem_output.wav")
