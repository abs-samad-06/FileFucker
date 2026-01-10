# bot/services/metadata.py

import os
import subprocess
import shutil
from typing import Optional

from mutagen.easyid3 import EasyID3
from mutagen.mp4 import MP4, MP4Cover


TEMP_DIR = "temp_metadata"


def _ensure_dir():
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)


# ─── AUDIO METADATA (MP3 / M4A) ───────────────────────────────────────
def edit_audio_metadata(
    input_path: str,
    *,
    title: Optional[str] = None,
    artist: Optional[str] = None,
    album: Optional[str] = None,
    year: Optional[str] = None,
    cover_path: Optional[str] = None
) -> str:
    """
    Edits audio metadata without re-encoding.
    Returns output file path.
    """
    _ensure_dir()
    output_path = os.path.join(TEMP_DIR, os.path.basename(input_path))

    shutil.copy(input_path, output_path)

    if output_path.lower().endswith(".mp3"):
        audio = EasyID3(output_path)
        if title:
            audio["title"] = title
        if artist:
            audio["artist"] = artist
        if album:
            audio["album"] = album
        if year:
            audio["date"] = year
        audio.save()

    elif output_path.lower().endswith((".m4a", ".mp4")):
        audio = MP4(output_path)
        if title:
            audio["\xa9nam"] = title
        if artist:
            audio["\xa9ART"] = artist
        if album:
            audio["\xa9alb"] = album
        if year:
            audio["\xa9day"] = year

        if cover_path and os.path.exists(cover_path):
            with open(cover_path, "rb") as img:
                audio["covr"] = [
                    MP4Cover(img.read(), imageformat=MP4Cover.FORMAT_JPEG)
                ]
        audio.save()

    return output_path


# ─── VIDEO METADATA (MP4 / MKV) ────────────────────────────────────────
def edit_video_metadata(
    input_path: str,
    *,
    title: Optional[str] = None,
    year: Optional[str] = None,
    comment: Optional[str] = None
) -> str:
    """
    Uses ffmpeg to update metadata without re-encoding.
    """
    _ensure_dir()
    output_path = os.path.join(TEMP_DIR, os.path.basename(input_path))

    cmd = ["ffmpeg", "-y", "-i", input_path]

    if title:
        cmd += ["-metadata", f"title={title}"]
    if year:
        cmd += ["-metadata", f"year={year}"]
    if comment:
        cmd += ["-metadata", f"comment={comment}"]

    cmd += ["-c", "copy", output_path]

    subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True
    )

    return output_path


# ─── CLEANUP ──────────────────────────────────────────────────────────
def cleanup_temp():
    """
    Clears temp metadata directory.
    """
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
