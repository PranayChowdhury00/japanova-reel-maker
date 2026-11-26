# Japanova Reel Maker V3.4 — AI Voice Studio

A **local Windows reel editor** for 30-second Bengali/English videos. It combines HTML canvas typography and transitions with a Python + FFmpeg CPU renderer. New in V3.3: optional online AI voiceover and synced captions.

## What's new
- Bengali voices: **Pradeep** (male) and **Nabanita** (female)
- English voices: Andrew (male), Aria (female)
- Speech speed control (0.75–1.40x), Generate & Listen Voice, Stop Voice
- Voice synchronization per complete scene, with 30-second maximum and no forced speech truncation
- Music ducking (automatic music reduction when voice is speaking)
- Voice preview, auto-generation on MP4 export, optional music-only export

All V3.2 features remain: colorful bold text, shadows, gradients, transitions, scene editing, backgrounds, HD/Full HD MP4 export.

## Install & run on Windows

1. Clone: `git clone https://github.com/PranayChowdhury00/japanova-reel-maker.git`
2. Open the folder and run `setup.bat` (Python, FFmpeg, and `edge-tts` dependency). If Python and FFmpeg are installed, `py -3 -m pip install -r requirements.txt` is sufficient.
3. Start `START.bat`. Open http://127.0.0.1:8765 if not opened automatically.
4. Paste a short script, split scenes, choose a voice, click **Generate & Listen Voice**, then **Export 30s MP4**.
5. If the voice exceeds 30 seconds, shorten the script or increase speed. It will never silently cut off the spoken text.

## Privacy / service notes

- Text, videos and rendered MP4 are processed locally **except** for optional AI voice synthesis.
- `edge-tts` sends text over the Internet to a Microsoft speech service. It is an unofficial client and the free route may stop working or be rate-limited.
- No paid API key is required for this experimental option, but it is **not** a guaranteed free commercial TTS service. Check service/licensing terms before publishing commercial content; use an appropriately licensed TTS provider where necessary.
- A backup music-only workflow is available by choosing *No Voiceover*.
- Do not expose the local development server to the public Internet.

## Testing

- Python syntax checks and local synthetic audio rendering test completed in this environment.
- Full remote Edge TTS playback requires an online Windows test because this environment does not have access to the Microsoft speech endpoint.
- Voice-to-scene timings are derived from each rendered speech clip, but FFmpeg frame rounding can create minor timing differences.
## Troubleshooting: `No audio was received` (v3.3.1)

Edge TTS sometimes returns no audio even with valid text. The app now retries Edge TTS up to three times and automatically tries the Google Translate TTS fallback if Edge fails. Both providers need an internet connection and can be unavailable.

1. Close the app and run `git pull origin main`.
2. Run `py -3 -m pip install --upgrade -r requirements.txt`.
3. Restart with `.\\START.bat`, then refresh with `Ctrl+Shift+R`.
4. Try a short Bengali sentence, e.g. `জাপানে আপনাকে স্বাগতম।` using Bengali Male or Female.
5. Check the status: it states which provider produced audio. Backup TTS does not preserve male/female voice choice.
6. If **both** providers fail, check connection/firewall and retry later. Voice Off still allows silent/music-only MP4 export.

This fallback is not an official Microsoft/Google commercial API or uptime guarantee. Check provider usage terms before commercial publishing. Do not bypass service blocks or quotas.

## V3.4 Auto Subtitle Studio
- Enable or disable burned-in subtitles for 30-second reels.
- Choose Yellow + Outline, White + Shadow, or Cyan + Dark Box.
- Adjust subtitle size and lower-third position (safe margins).
- Subtitles are generated from each edited scene's text; no new API or payment is needed.
- With AI narration, caption changes follow scene-level voice durations. These are **not** word-by-word timestamps or speech recognition.
- Exported H.264 MP4 has subtitle text burned into frames (viewers cannot turn it off after export).
- If you edit scene text, regenerate AI voice before export to update synchronization.
