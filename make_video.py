#!/usr/bin/env python3
"""Modern Vision slideshow maker.

Takes the photos in a folder, shows each one for exactly 0.2 seconds in
filename order, plays the whole set 4 times, and saves a TikTok-ready
vertical video (1080x1920, 30 fps, H.264 MP4) into the
"finished modern_vision_ videos" folder.

Usage:
    python3 make_video.py                  # uses the default photo folder
    python3 make_video.py "path/to/photos" # uses a folder you choose
"""

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

PHOTO_FOLDER_NAME = "modern_vision_ photos"
OUTPUT_FOLDER_NAME = "finished modern_vision_ videos"
PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tif", ".tiff"}

WIDTH, HEIGHT = 1080, 1920
FPS = 30
FRAMES_PER_PHOTO = 6  # 6 frames at 30 fps = exactly 0.2 seconds
EXPECTED_PHOTOS = 10
DEFAULT_LOOPS = 4


def find_desktop():
    home = Path.home()
    for candidate in (home / "Desktop", home / "OneDrive" / "Desktop"):
        if candidate.is_dir():
            return candidate
    return home


def find_ffmpeg():
    path = shutil.which("ffmpeg")
    if path:
        return path
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        sys.exit(
            "Couldn't find ffmpeg. Install it by running:\n"
            "    python3 -m pip install imageio-ffmpeg\n"
            "then try again."
        )


def natural_key(path):
    # Sort "photo2" before "photo10", the way a person would.
    return [int(part) if part.isdigit() else part.lower()
            for part in re.split(r"(\d+)", path.name)]


def collect_photos(folder):
    photos = [p for p in folder.iterdir()
              if p.is_file() and p.suffix.lower() in PHOTO_EXTENSIONS
              and not p.name.startswith(".")]
    return sorted(photos, key=natural_key)


def make_video(photos, output_path, loops, ffmpeg):
    fit = (
        f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
        f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=black,"
        f"setsar=1,format=yuv420p"
    )
    clip_seconds = FRAMES_PER_PHOTO / FPS

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        # Turn each photo into one exactly-6-frame vertical clip.
        clips = []
        for i, photo in enumerate(photos):
            clip = tmp / f"clip{i:03d}.mp4"
            subprocess.run(
                [ffmpeg, "-y", "-loglevel", "error",
                 "-loop", "1", "-framerate", str(FPS), "-i", str(photo),
                 "-vf", fit, "-frames:v", str(FRAMES_PER_PHOTO),
                 "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                 "-r", str(FPS), str(clip)],
                check=True,
            )
            clips.append(clip)

        # Play all the clips in order, then repeat the whole set.
        playlist = tmp / "playlist.txt"
        lines = [f"file '{clip.as_posix()}'" for _ in range(loops) for clip in clips]
        playlist.write_text("\n".join(lines) + "\n")

        total_frames = FRAMES_PER_PHOTO * len(photos) * loops
        total_seconds = clip_seconds * len(photos) * loops
        subprocess.run(
            [ffmpeg, "-y", "-loglevel", "error",
             "-f", "concat", "-safe", "0", "-i", str(playlist),
             # Silent soundtrack so TikTok treats it as a normal video.
             "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
             "-map", "0:v", "-map", "1:a",
             "-c:v", "libx264", "-preset", "medium", "-crf", "18",
             "-pix_fmt", "yuv420p", "-r", str(FPS), "-frames:v", str(total_frames),
             "-c:a", "aac", "-b:a", "128k", "-t", f"{total_seconds:.3f}",
             "-movflags", "+faststart", str(output_path)],
            check=True,
        )


def main():
    desktop = find_desktop()
    parser = argparse.ArgumentParser(description="Make a TikTok slideshow from a folder of photos.")
    parser.add_argument("photos", nargs="?", default=str(desktop / PHOTO_FOLDER_NAME),
                        help=f'folder of photos (default: "{PHOTO_FOLDER_NAME}" on your Desktop)')
    parser.add_argument("--output", default=str(desktop / OUTPUT_FOLDER_NAME),
                        help=f'where to save the video (default: "{OUTPUT_FOLDER_NAME}" on your Desktop)')
    parser.add_argument("--loops", type=int, default=DEFAULT_LOOPS,
                        help=f"how many times to play the whole set (default: {DEFAULT_LOOPS})")
    args = parser.parse_args()

    photo_folder = Path(args.photos.strip().strip("'\"")).expanduser()
    if not photo_folder.is_dir():
        photo_folder.mkdir(parents=True, exist_ok=True)
        sys.exit(f'I made the folder "{photo_folder}" for you. Put your photos in it and run me again.')

    photos = collect_photos(photo_folder)
    if not photos:
        sys.exit(f'No photos found in "{photo_folder}". Add some and run me again.')
    if len(photos) != EXPECTED_PHOTOS:
        print(f"Heads up: found {len(photos)} photos (expected {EXPECTED_PHOTOS}). Using all of them.")

    output_folder = Path(args.output).expanduser()
    output_folder.mkdir(parents=True, exist_ok=True)
    output_path = output_folder / f"modern_vision_{datetime.now():%Y-%m-%d_%H-%M-%S}.mp4"

    print("Photo order:")
    for i, photo in enumerate(photos, 1):
        print(f"  {i}. {photo.name}")

    make_video(photos, output_path, args.loops, find_ffmpeg())

    seconds = FRAMES_PER_PHOTO / FPS * len(photos) * args.loops
    print(f"\nDone! {seconds:g} second video saved to:\n  {output_path}")


if __name__ == "__main__":
    main()
