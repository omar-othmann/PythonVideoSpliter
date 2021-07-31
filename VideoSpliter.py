import subprocess
from Progress import ProgressFFmpeg


class VideoSpliter:
    def __init__(self, path: str, filename: str, number: int):
        self.path = path
        self.filename = filename
        self.number = number
        self.full = "{path}/{filename}".format(path=self.path, filename=self.filename)

    class Progress:
        def on_error(self, msg, do=None):
            print(msg, do)

        def on_progress(self, a, b, c):
            print(a)

        def on_finish(self):
            print("Video split successfully!!!")

    def __get_length(self, path):
        result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                 "format=duration", "-of",
                                 "default=noprint_wrappers=1:nokey=1", path],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)

        return float(result.stdout)


    def get_length(self):
        length = self.__get_length(self.full)
        return length
        
    def length_to_time(self, length, hours=False):
        minutes, seconds = divmod(length, 60)
        hours, minutes = divmod(minutes, 60)
        sec = round(seconds)
        result = []
        if length >= 3600:
            result.append(str(hours))
        if length >= 60:
            result.append(str(int(minutes)))
        if sec > 0:
            result.append(str(sec))

        if result:
            return ":".join(result)
        if hours:
            return "00:00:00"
        else:
            return "00:00"

    def do_math(self):
        def_length = self.get_length()
        c = self.length_to_time(def_length)
        hours = len(c.split(":")) >= 3
        length = def_length / self.number
        must = float(length)
        rep = dict()
        last = 0
        count = 0
        for i in range(0, self.number):
            start = self.length_to_time(last, hours=hours)
            end = self.length_to_time(must, hours=hours)
            rep[i] = [start, end]
            last += must
            if self.number - i <= 2:
                must = def_length - last

        return rep

    def split(self):
        rep = self.do_math()
        for index in rep:
            start, end = rep[index]
            out = self.path + "/{index}_{filename}".format(filename=self.filename, index=index)
            if len(start.split(":")) >=3:
                cmd = 'ffmpeg -ss "{start}" -i "{full}" -t "{end}" -c:v copy -c:a copy  "{out}"'.format(full=self.full, start=start, end=end, out=out)
            else:
                cmd = cmd = 'ffmpeg -ss "00:{start}" -i "{full}" -t "00:{end}" -c:v copy -c:a copy  "{out}"'.format(full=self.full, start=start, end=end, out=out)

            print(cmd)

            pro = ProgressFFmpeg(None)
            pro.set_callback(self.Progress())
            pro.export(None, cmd=cmd)
    
        

    

video = VideoSpliter("P:/streaming/videos/Squad", "example.mp4", 3)
video.split()
