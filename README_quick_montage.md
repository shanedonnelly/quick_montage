# quick_montage

This is a **small personal project** built as an experiment to learn scripting in both **Python** and **Bash**.  
Its goal is to **quickly assemble video files** found in the current folder into a single video, optionally with audio added or mixed in.


## What It Does

- Scans the current folder for video files (`.mp4`, `.mkv`, `.avi`, `.flv`, etc.).
- Remuxes videos into a common format (`.mp4`) without re-encoding.
- Optionally downloads audio from YouTube using `yt-dlp`.
- Allows simple audio mixing via a balance parameter.
- Outputs a final `output.mp4` file.
- Automatically opens the result in VLC (if available).


## Dependencies

- `ffmpeg`
- `yt-dlp` (optional, only if you use the YouTube audio option)
- `vlc` (optional, for playback)


##  How to Use

### Python version:
```bash
python3 quick_montage.py [-y YOUTUBE_URL] [-b BALANCE]
```

- `-y`: Download audio from a YouTube video to use as background music.
- `-b`: Set audio balance (0.0 = only video audio, 1.0 = only external audio). Defaults to 0.2 if flag is passed without a value.

### Bash version:
Same for bash 

- Simpler version, uses local audio if present. No YouTube download or audio mixing.

