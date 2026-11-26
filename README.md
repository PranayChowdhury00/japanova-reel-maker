# Japanova Reel Maker V3.2

Local-first 30-second vertical reel generator for Bengali and English content.

## Features
- Smart sentence splitting, no text loss, dynamic 30-second scene durations
- Scene editor for changing caption, duration, individual color and transition
- Text Design Studio: white, gold, cyan, pink and gradient color presets
- Semi Bold, Bold and Extra Bold; font size controls and automatic wrapping
- Soft Shadow, Bold Outline, Neon Glow and Highlight Box
- MP4 transitions: Fade, Slide Up and Slide Left (CPU FFmpeg)
- Live preview; background image/video; licensed background music
- Lite, HD 720p and Full HD 1080p; H.264 video with AAC audio
- No API key or remote service

## Windows installation
1. `git clone https://github.com/PranayChowdhury00/japanova-reel-maker.git`
2. Install Python 3 and FFmpeg if needed (run `setup.bat`).
3. Run `START.bat` or `py -3 server.py` in PowerShell.
4. Open http://127.0.0.1:8765
5. Paste script, split scenes, choose styles, preview and export MP4.

If updating an existing clone, run `git pull origin main` and use `Ctrl+Shift+R` in the browser.

## Notes
- Local desktop app: keep the terminal open while exporting.
- Uploaded media/scripts are processed on your own machine.
- Only use media for which you have usage rights.
- Browser preview approximates animation movement; MP4 is rendered by FFmpeg on CPU.
- A synthetic 30-second H.264 + AAC render was verified, but full browser-to-Windows export was not verified in this environment.
- If Full HD is slow, use HD.

## Files
- `index.html`: UI, styling, preview and transparent caption PNGs
- `server.py`: local HTTP + FFmpeg CPU renderer
- `START.bat` / `setup.bat`: Windows setup/launcher
- `CHANGELOG.md`: version history
