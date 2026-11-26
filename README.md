# Japanova Reel Maker V4.3.1 — Auto Reel Duration Fix

V4.3.1 fixes reels that remained 30 seconds long even when the narration was only 8–10 seconds.

## Fixed: Video Duration follows narration

**Video Duration** now has two modes:

- **Auto — Ends with speech (default):** use actual generated voice clip lengths, ~0.22 seconds of space after each scene and a ~0.65-second final hold. A short script can export a short reel, rather than a 30-second video filled with silence.
- **Fixed 30 Seconds (optional):** retain the former 30-second behaviour for a planned campaign where a full 30-second clip is required.

The duration is shared consistently by:
- AI voice assembly and audio padding
- Scene timings and word-highlight subtitle timestamps
- Live preview playback and progress bar
- Presenter/Smart Focus timelines
- FFmpeg video output and audio trimming

With **Voice Off**, the app uses an approximate speaking-rate estimate based on word count (about 2.35 words/second), a short scene pause and final hold. This estimate is not speech analysis.

**Maximum reel length remains 30 seconds.** If speech is too long, the generator asks you to shorten the script or adjust the voice speed; it does not silently truncate the words.

## Update on Windows

1. Close the running Japanova app/START.bat console.
2. From PowerShell:

```powershell
cd C:\Users\USER\japanova-reel-maker
git pull origin main
.\START.bat
```

3. In Chrome, press **Ctrl + Shift + R**.
4. Select **Video Duration → Auto — Ends with speech**.
5. Generate AI Voice again (old cached voice timings may still reflect 30 seconds), listen to it, then Export MP4.

### Recommended regression script

`জাপানে পড়াশোনা করতে চাইলে আগে COE প্রস্তুত করুন। পাসপোর্ট আর ব্যাংক স্টেটমেন্ট ঠিক রাখুন।`

The video should now be near the spoken narration length plus ~1 second of small scene gaps/end hold. Its exact seconds depend on the selected TTS voice and speed. It must **not** stretch to 30 seconds in Auto mode.

## Other features retained
V4.3 Short Captions + Word Highlight, Edge WordBoundary (estimated when unavailable), Classic Subtitles, 2.5D presenter, Smart Focus, minimal animation, background media, music, export checks, and HD/Full HD MP4.

## Testing notes
- Checked relevant client-side JavaScript syntax and presence of per-mode duration handling in voice generation, preview, and MP4 export.
- A full remote Windows FFmpeg + Edge TTS end-to-end test is **not possible here**; please check the output locally and send the error text if your test fails.
- Edge TTS and Google backup involve online speech services; commercial use is subject to provider terms.
