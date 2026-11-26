# Japanova Reel Maker

A local-first, 30-second Bengali/English vertical reel generator for Japanova Edu.

## Features
- Smart sentence detection (Bengali danda, punctuation and line breaks)
- Dynamic scene durations normalized to 30 seconds
- Edit scene captions and timing before exporting
- Automatic text wrapping and responsive font sizing
- Fade-in/fade-out captions and live browser preview
- Background image/video and licensed music uploads
- CPU-based FFmpeg export to H.264/AAC MP4
- Lite (540×960), HD (720×1280), Full HD (1080×1920) modes

## Setup (Windows)
1. Download or clone this repository.
2. Install Python 3 and FFmpeg, and make sure both are available in PATH. Alternatively, run `setup.bat` to attempt installation via Windows Package Manager.
3. Double-click `START.bat` (or run `py -3 server.py`).
4. Open `http://127.0.0.1:8765` if it does not open automatically.
5. Paste your script, select a quality option, review/edit scenes, then click **Generate & Export 30s Reel**.

### Security and privacy
- Runs locally on `127.0.0.1`. Scripts/media are processed on your computer.
- No OpenAI API key or paid service is required.
- Use only music and footage you have rights to use.
- The development server is intended for personal desktop use, **not** for public hosting.

## Known limitations
- Browser preview animations may not perfectly match the exported MP4.
- Actual rendering requires a compatible local FFmpeg installation.
- Full HD export is resource intensive; start with HD mode.
- Built for 30-second reels only; excessively long captions may be difficult to read.
- No automatic stock footage retrieval or AI voiceover.

## Project files
- `index.html` — user interface, preview, and scene controls
- `server.py` — local HTTP server and FFmpeg rendering
- `START.bat` — Windows launcher
- `setup.bat` — optional dependency installer

## Version
v3.1 (Smart Scene Edition). Source is provided as-is; verify MP4 output on your machine before production use.

