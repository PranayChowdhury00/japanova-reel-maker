# Japanova Reel Maker V4.0 — AI Presenter Studio

**V4.0 (preview release)** adds an optional 2.5D illustrated presenter to the existing local Windows reel editor. This is deliberately **not** a rigged 3D human or true phoneme-based lip-sync model.

### Features
- Select **Formal Boy**, **Formal Girl**, or **Off (Classic Text Reel)**.
- Presenter position: left, center, or right.
- Eyes blink automatically during previews and final MP4 output.
- During exports with AI voice narration, mouth-open intervals are estimated from speech amplitude (RMS), not from consonants/vowels. This is approximate audio-reactive speaking animation.
- 30-second H.264 MP4 retains optional Bengali/English voice, background music, subtitles, images/video, and previous brand styling.
- No new paid API or heavy 3D graphics engine. Presenter SVG portraits render in the browser and are exported as PNG poses; FFmpeg composites them into video.
- The previous 3.4 text-only workflow remains available by setting Presenter = Off.

### Update on Windows
Stop the running app, then open PowerShell:

```powershell
cd C:\Users\USER\japanova-reel-maker
git pull origin main
.\START.bat
```
Refresh the browser with **Ctrl+Shift+R**.

### Recommended first test
1. Choose **Formal Boy**, **HD 720p**, subtitle **On**, and a short Bengali script.
2. Click **Generate & Listen Voice**, then **Live Preview**.
3. Click **Export 30s MP4**. Rendering will be CPU-intensive, especially at 1080p. Close other heavy apps.
4. Check the downloaded video for mouth movement, blink, narration and subtitles. Send back any error from the terminal or interface.

### Limits and safeguards
- **Beta:** The synthetic FFmpeg overlay technique was tested, but the complete Windows end-to-end flow has not been verified remotely.
- Speech-energy mouth activity is an approximation; it is **not** word-perfect lip sync.
- This is a stylized 2.5D presenter, **not full 3D**. It has a static upper body, blinking, mouth poses; no hand animation.
- Avatar is SVG/Canvas-based and needs no additional model downloads or paid GPU API. It can take longer to render than V3.4.
- Edge TTS and backup gTTS require internet. Edge is an unofficial Microsoft client. Check commercial licensing terms before publishing reels.
- All video composition is local. Text is sent to online TTS providers only when AI voice is enabled.
- The default server binds only to 127.0.0.1; do not expose it publicly.
