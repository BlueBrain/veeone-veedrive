import asyncio.subprocess
import datetime
import math

import cv2

from .. import config


async def get_video_thumbnail(path, box_width, box_height, scaling_mode):
    video = cv2.VideoCapture(path)
    video_height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
    video_width = video.get(cv2.CAP_PROP_FRAME_WIDTH)

    # seek until 1% of video's duration
    video_duration = await _get_video_length(path)
    seek_time = str(datetime.timedelta(seconds=int(math.floor(video_duration / 100))))

    # fit the output to the specified box
    requested_size = calculate_size(
        scaling_mode, box_width, box_height, video_width, video_height
    )

    ffargs = compile_ffmpeg_args(
        seek_time, path, requested_size, scaling_mode, box_width, box_height
    )

    process = await asyncio.subprocess.create_subprocess_exec(
        *ffargs, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return stdout


def calculate_size(scaling_mode, box_width, box_height, video_width, video_height):
    if scaling_mode == config.FIT_TRANSFORM_IMAGE:
        requested_aspect = box_width / box_height
        video_aspect = video_width / video_height

        requested_size = (
            f"-1:{box_height}" if requested_aspect > video_aspect else f"{box_width}:-1"
        )

    # fill the specified box with the output (cropping possible)
    if scaling_mode == config.FILL_TRANSFORM_IMAGE:
        ratio = max(box_width / video_width, box_height / video_height)
        width = int(math.ceil(video_width * ratio))
        # height = int(math.ceil(vidHeight * ratio))

        requested_size = f"{width}:-1"
    return requested_size


def compile_ffmpeg_args(
    seek_time, path, requested_size, scaling_mode, box_width, box_height
):
    extra_ffmpeg_params = ""
    if scaling_mode == config.FILL_TRANSFORM_IMAGE:
        crop_area = f"{box_width}:{box_height}"
        extra_ffmpeg_params = f",crop={crop_area}"

    return [
        "ffmpeg",
        "-ss",
        seek_time,
        "-t",
        "3",
        "-y",
        "-i",
        path,
        "-f",
        "gif",
        "-vf",
        f"fps=10,scale={requested_size}:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse\
            {extra_ffmpeg_params}",
        "pipe:1",
    ]


async def _get_video_length(file):
    ffprobe_args = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        file,
    ]

    proc = await asyncio.subprocess.create_subprocess_exec(
        *ffprobe_args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    return float(stdout)
