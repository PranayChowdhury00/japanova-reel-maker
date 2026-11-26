# Japanova Reel Maker V4.3 — Professional Subtitle & Stability

A local Windows reel maker for 30-second Bengali/English social videos. It retains V4.2's optional 2.5D formal boy/girl presenter, restrained context-aware motion graphics, AI narration, music, background media, and HD/Full HD export.

## New in V4.3

- **Short Captions + Word Highlight (default):** shows groups of up to four words and highlights the current word.
- **Timing-aware:** when Edge TTS returns WordBoundary events, the app uses their positions for word highlighting. If the provider supplies no usable boundaries (including Google Translate TTS backup) or narration is Off, word timing is **estimated**, not speech-recognition-accurate. The voice status reports which timing mode was used.
- **Classic Subtitle Mode:** the prior entire-scene subtitle remains selectable. Subtitles can be turned Off.
- **Local subtitle rendering:** browser Canvas renders caption sprites with matching font and color styles. FFmpeg crops the appropriate sprite row for each word at export, reducing the number of video inputs compared with one PNG per word.
- **Export validation:** checks for empty/oversized scenes, scripts over 2,500 characters, short subtitle projects over 140 words, assets not loaded, and unusually large uploads (200 MB per media file).
- **Backward-compatible V4.2 features:** Full HD/Lite output, boy/girl presenter, scene transitions, Smart Focus animations, optional music, AI voice, and scene subtitles.

## Update on Windows

Stop the old app before updating:

```powershell
cd C:\Users\USER\japanova-reel-maker
git pull origin main
.\START.bat
```

Press **Ctrl + Shift + R** in the browser. Choose **HD 720p** for your first test.

### Test
1. Choose **Short Captions + Word Highlight**, Formal Boy, and Smart Focus On.
2. Use a brief script such as: `জাপানে পড়াশোনা করতে চাইলে আগে COE প্রস্তুত করুন। পাসপোর্ট আর ব্যাংক স্টেটমেন্ট ঠিক রাখুন।`
3. Click **Generate & Listen Voice**. Look at the status message to see if timing is Edge WordBoundary or estimated.
4. Click **Live Preview** and then **Export 30s MP4**. Check word highlight changes in the exported file.
5. If export fails, send the exact error from the status box or PowerShell window.

## Technical notes / limits

- **This is not forced alignment.** Edge word boundaries are associated with the online speech synthesizer, not independently verified against the final MP3 waveform. Audio mixing, frame rounding, punctuation, and provider text tokenization can introduce slight mismatches.
- WordBoundary events may not match whitespace-split Bangla words. In that case timings are estimated and the status is labeled accordingly.
- User-supplied scripts are sent to remote Edge TTS or gTTS services only if AI voice is used. They are unofficial/free integrations with no guarantee of service availability, commercial license or uptime. Check licensing before business posting.
- Short captions are limited to 140 words / 50 words in one scene to reduce large sprite rendering. For longer scripts use **Classic Full-Scene Subtitles**.
- Voice Off uses estimated timing over scene durations; it does not mean the words are being spoken.
- Full Windows application end-to-end export with online TTS could not be tested in this environment. A synthetic FFmpeg smoke test verified dynamic sprite crop changes at word timestamps.
- Everything besides optional AI voice synthesis and supplied background media stays local; the development server binds to 127.0.0.1. Never expose the server on the public internet.
