"""
MIT License

Copyright (c) 2020 Kevin Hermann

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ChapterTimestamp:
    "Wrapper class to represent a timestamp"
    track_id: int
    title: str
    start: str
    end: str


def obtain_chapter_information(filepath):
    "run ffprobe command to obtain the chapter timestamps"
    command = [
        "ffprobe",
        "-i",
        filepath,
        "-print_format",
        "json",
        "-show_chapters",
        "-sexagesimal",
    ]
    result = subprocess.run(command, check=True, stdout=subprocess.PIPE)
    json_data = json.loads(result.stdout)
    chapters = json_data["chapters"]
    chapter_timestamps = []
    # iterat eover ffprobe output
    for chapter in chapters:
        start_time = chapter["start_time"]
        end_time = chapter["end_time"]
        track_id = int(chapter["id"])
        title = chapter["tags"]["title"]
        cht = ChapterTimestamp(track_id, title, start_time, end_time)
        chapter_timestamps.append(cht)
    return chapter_timestamps


def slice_chapter(filepath, chapter):
    "Obtains chapter from audiofile"
    # file output path
    Path("./output").mkdir(exist_ok=True)
    p = Path(filepath)
    new_p = f"{chapter.track_id:03d}_{p.name}"
    new_p = Path("./output").joinpath(new_p)
    # shell command
    command = [
        "ffmpeg",
        "-i",
        filepath,
        "-ss",
        chapter.start,
        "-to",
        chapter.end,
        "-c",
        "copy",
        new_p,
    ]
    subprocess.run(command, check=True)


def convert_audiofile(filepath):
    "Convert audiofile  mp3"
    new_p = Path(filepath).with_suffix(".mp3")
    new_name = new_p.name
    commmand = [
        "ffmpeg",
        "-i",
        filepath,
        "-acodec",
        "libmp3lame",
        "-ar",
        "22050",
        "-metadata",
        f"title={new_name}",
        new_p,
    ]
    subprocess.run(commmand, check=True)


def process_audiobook(filepath):
    "Splits .m4b audiobook into chapters and converts to mp3"
    # get chapter information
    chapter_info = obtain_chapter_information(filepath)
    # split into chapters
    for c in chapter_info:
        slice_chapter(filepath, c)
    # convert to .mp3
    for _, _, files in os.walk("./output"):
        for f in files:
            if not f.endswith("m4b"):
                continue
            p = Path("./output").joinpath(f)
            convert_audiofile(p)


if __name__ == "__main__":
    filename = sys.argv[1]
    print(filename)
