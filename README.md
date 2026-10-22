# Modern Vision Video Editor

Turns a folder of photos into a TikTok-ready slideshow video.

**What the video looks like**

- Each photo shows for exactly **0.2 seconds**.
- It uses the **10 newest photos** in the folder, played in the order you added them (oldest first), then the whole set repeats. It plays **4 times** in total.
- With 10 photos that's a **8 second** video.
- Vertical **1080 x 1920** MP4, the size TikTok wants. Photos that aren't vertical get black bars so nothing is cropped off.
- Finished videos are saved in a folder called **`finished modern_vision_ videos`** on your Desktop.

## One-time setup

1. **Install Python** from <https://www.python.org/downloads/> (on Windows, tick "Add Python to PATH" during install). Macs usually already have it.
2. **Download this project**: on the GitHub page click the green **Code** button, then **Download ZIP**, and unzip it somewhere (your Desktop is fine).
3. **Install the video tool** by opening a terminal (Mac: *Terminal* app, Windows: *Command Prompt*) and running:

   ```
   python3 -m pip install imageio-ffmpeg
   ```

   (On Windows, type `python` instead of `python3` in every command.)

## Making a video

1. Make a folder on your Desktop called **`modern_vision_photos`** and drop your photos in. No renaming needed.
   - The tool picks the 10 most recently added photos and plays them in the order you added them.
   - Older photos can stay in the folder; they're just skipped.
   - If the same photo got downloaded twice, the copy is skipped so it never shows twice.
   - JPG, PNG and WEBP all work.
2. In the terminal, type `python3 ` (with a space after it), drag the `make_video.py` file into the terminal window, and press Enter.
3. Your video appears in the **`finished modern_vision_ videos`** folder on your Desktop, ready to upload to TikTok.

Videos are numbered `modern_vision_tiktok1.mp4`, `modern_vision_tiktok2.mp4`, and so on, so old videos are never overwritten. When you want a new video, add 10 new photos and run it again. If you haven't added any photos since the last video, it stops and says "You have not added new photos yet" instead of making a repeat.

### Using a different photo folder

Drag the folder in after the script:

```
python3 make_video.py "/path/to/some other folder"
```

### Using a different number of photos

```
python3 make_video.py --count 15
```

### Changing how many times it repeats

```
python3 make_video.py --loops 6
```
