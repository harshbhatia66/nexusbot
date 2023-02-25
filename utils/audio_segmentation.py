import wave
import contextlib
from pydub import AudioSegment
import os

class Segmenter:
    def __init__(self, audio_filepath, transcript_filepath, output_folder):
        self.audio_filepath = audio_filepath
        self.transcript_filepath = transcript_filepath
        self.output_folder = output_folder

    def get_audio_duration(self):
        with contextlib.closing(wave.open(self.audio_filepath,'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
            return duration

    def srt_to_timecodes(self):
        timecodes = []
        with open(self.transcript_filepath, "r") as f:
            lines = f.readlines()
            for i in range(0, len(lines), 4):
                start_time = lines[i+1].split(" --> ")[0].strip()
                end_time = lines[i+1].split(" --> ")[1].strip()
                sentence = lines[i+2].strip()
                timecodes.append([start_time, end_time, sentence])
        return timecodes

    def create_segments(self):
        audio = AudioSegment.from_file(self.audio_filepath)

        timecodes = self.srt_to_timecodes()
        video_name = os.path.splitext(os.path.basename(self.audio_filepath))[0]
        for i, tc in enumerate(timecodes):
            start_time = tc[0].split(":")
            end_time = tc[1].split(":")
            start_ms = int((int(start_time[0]) * 3600 + int(start_time[1]) * 60 + int(start_time[2].split(",")[0])) * 1000 + int(start_time[2].split(",")[1]))
            end_ms = int((int(end_time[0]) * 3600 + int(end_time[1]) * 60 + int(end_time[2].split(",")[0])) * 1000 + int(end_time[2].split(",")[1]))
            segment = audio[start_ms:end_ms]
            segment_file = f"{self.output_folder}/{video_name}_segment{i+1}.wav"
            transcript_file = f"{self.output_folder}/{video_name}_segment{i+1}.txt"
            segment.export(segment_file, format="wav")
            with open(transcript_file, "w") as f:
                f.write(tc[2])


