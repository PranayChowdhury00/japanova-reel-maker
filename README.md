# Japanova Reel Maker V4.1 — Smart Motion Graphics Studio

A local-first Windows app for Bengali/English 30-second social media reels.

## V4.1: Keyword-based animated objects
Select **Smart Objects: On — Auto Detect** to add an illustrated emoji card when a scene contains a matching topic:

| Script keywords (examples) | Animated card |
| --- | --- |
| COE, সিওই | 📑 COE documents |
| Passport, পাসপোর্ট | 🛂 PASSPORT |
| Visa, ভিসা | 🛃 VISA |
| Bank, ব্যাংক, ব্যালেন্স, Statement | 💳 BANK |
| University, বিশ্ববিদ্যালয়, স্কুল | 🎓 UNIVERSITY |
| Japan, জাপান | ✈️ JAPAN |

Choose one of **Pop & Bounce**, **Slide In/Out**, or **Floating**, adjust **Left / Right / Top** position, and set card size to 65–120%. Preview and final FFmpeg MP4 both include animation. There is no extra paid API or asset download.

**Timing limitations:** keyword matching is textual, not AI semantic understanding. One card is shown for each matching scene, up to six cards per reel. The object begins early in its scene, not exactly at the spoken word, because the voice engine has scene-level rather than word-level timestamps. For clarity, the card is placed above the subtitle safe area. Cards are rendered from browser canvas graphics and OS emoji fonts, so appearance may vary by Windows version.

## Existing features
- Optional 2.5D Boy / Girl Presenter (or Off), mouth energy animation, blinking.
- Bengali Male / Female AI narration, optional English voices; free online Edge TTS with Google TTS fallback.
- Automatic subtitles (scene-level sync), styling, transitions, branded backgrounds, background video/music.
- Local FFmpeg CPU export to Lite 540p, HD 720p and Full HD 1080p 30-second MP4.

## Update on Windows
Stop the running app first. Open PowerShell:

```powershell
cd C:\Users\USER\japanova-reel-maker
git pull origin main
.\START.bat
```

Hard-refresh browser with Ctrl+Shift+R. In the app set **Smart Objects** to On, paste a short sample:
`জাপানে যাওয়ার আগে COE প্রস্তুত রাখুন। পাসপোর্ট ও ভিসার কাগজ যাচাই করুন। ব্যাংক স্টেটমেন্ট ঠিক রাখুন।`
Click **Auto Split Sentences**, then **Generate & Listen Voice** and **Live Preview** before **Export 30s MP4**.

## Stability and privacy
- This is an early V4.1 build. JavaScript syntax and separate FFmpeg animation expressions were tested. Full Windows end-to-end export on the user's PC remains unverified.
- Export rendering can be slower with a presenter, subtitles and six graphic overlays at once; start with HD 720p.
- The CPU-first design avoids a heavy 3D graphics model. Characters are *2.5D stylized*, and mouth movement is not phoneme-accurate.
- No extra service is required for keyword graphics. AI voice still sends entered script to online services (Edge TTS / backup gTTS), whose availability and commercial terms are not guaranteed.
- The app binds to 127.0.0.1. Never expose the local server on a public address.
