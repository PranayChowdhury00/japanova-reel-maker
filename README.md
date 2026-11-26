# Japanova Reel Maker V4.4 — Save & Resume Projects

V4.4 adds a **portable Save Project / Open Project workflow** on top of the V4.3.1 reel editor. Your project file can be moved to another Windows computer with Japanova Reel Maker.

## New — Save & Resume

- **Save Project (.jrm)** downloads a ZIP-based project file that contains `project.json` and, when present, background picture/video, music and previously generated voice audio.
- **Open Project (.jrm)** restores the script, individual edited scenes, scene durations, scene color/transition choices, voice settings, presenter, Smart Focus, subtitle settings, branding, quality and Auto/Fixed duration mode.
- **Voice is reusable** when the previously generated MP3 and exact matching narration settings are included; otherwise click Generate & Listen Voice.
- The ZIP uses Python's built-in `zipfile`. No new pip packages or paid API needed for saving/loading.
- Each media/voice asset can be **up to 80MB**. The total project upload is limited to about **170MB**, so compress larger videos first. Files live in your downloaded .jrm project rather than a cloud database.

## How to update on Windows

Close the existing START.bat window, then run:

```powershell
cd C:\Users\USER\japanova-reel-maker
git pull origin main
.\START.bat
```

Refresh Chrome with **Ctrl + Shift + R**.

## How to test

1. Paste a script and edit scene text or colors. Select a presenter, Smart Focus settings, video quality, and optional background/music.
2. Optionally Generate Voice. Click **Save Project (.jrm)**. Keep the downloaded file.
3. Refresh the browser to reset the editor, choose **Open Project (.jrm)**, and select your downloaded file.
4. Verify restored script, edited scenes, chosen settings, background/music and voice.
5. Preview or export MP4. If the voice wasn't included, generate voice after opening.

## Privacy and limitations

- **No cloud storage**: Projects are saved as local files. Protect your .jrm file if it contains private scripts, students' photos, office clips, or other sensitive content.
- Save is **manual**, not automatic. Download the latest project before closing or refreshing.
- Moving the project between computers may yield different fonts/emoji or TTS voice availability.
- Voice matching checks the exact script/voice/speed/duration settings. Changed voice settings invalidate the saved MP3.
- Imported projects are checked against a restricted ZIP member list and scene/settings schema; do not open untrusted files.
- This code has been inspected and the browser JavaScript syntax checked. **Full Windows browser upload/download and 30-second MP4 end-to-end testing still needs local verification**.
- All project ZIP work uses local Python. Voice generation is still performed through online Edge TTS or backup Google TTS and depends on their usage terms.

## Retained capabilities
V4.3.1 Auto reel duration (natural-length or Fixed 30 seconds); V4.3 word-highlight short captions; V4.2 restrained illustrated motion and presenter shrink; optional 2.5D formal boy/girl presenter and music; Lite/HD/Full HD FFmpeg export.
