# Japanova Reel Maker V4.2 — Minimal Cinematic Focus

V4.2 improves the V4.1 motion graphics so that visual aids help explain key moments without making a 30-second education reel busy or childish.

## What's new
- **Auto Presenter Shrink:** during a focus moment, the 2.5D boy/girl presenter smoothly shrinks to 75% and moves to the opposite side of the featured object; smoothly returns afterward.
- **Context-aware selection (heuristic, no additional AI API):** select high-priority COE, financial proof, passport, visa, university and language contexts. The generic word *Japan/জাপান* no longer creates an airplane unless the phrase actually involves travel.
- **No duplicate object topic:** one complete focus card per topic across the reel.
- **Limited visual moments:** up to 3 focus moments in a 30-second reel, with at least about 3.8 seconds between their start times.
- **Professional icon artwork:** locally drawn vector-inspired document, passport, financial proof, graduation, book, and travel icons replace OS-specific emoji cards.
- **Softer motion default:** Soft Fade & Zoom (default), Gentle Slide, or Subtle Float. No flashing / spinning / repeated bounce by default.
- **Preview AND exported MP4** include the same general focus layout. FFmpeg uses per-frame avatar scale with focus-in and focus-out transitions.
- Existing AI voices, scene subtitles, branding, videos/music, HD & Full HD MP4, and Presenter Off remain available.

## Windows update
Stop the previous START.bat console, open PowerShell:

```powershell
cd C:\Users\USER\japanova-reel-maker
git pull origin main
.\START.bat
```

In the browser press **Ctrl+Shift+R**, then select **Smart Objects: On — Smart Focus (max 3)** and **Soft Fade & Zoom**. For your first test choose **HD 720p** (not 1080p), then generate voice, preview and export.

### Example script
`জাপানে পড়াশোনা করতে চান? COE প্রস্তুত রাখতে হবে। পাসপোর্ট ও ভিসার তথ্য মিলিয়ে নিন। ব্যাংক স্টেটমেন্ট ঠিক রাখুন। জাপানে গিয়ে ভাষা শেখা চালিয়ে যান।`

Expected: COE or financial proof and other distinct relevant objects may be shown, no generic airplane just because Japan is mentioned, no category repeated.

## Important limitations
- **This is a heuristic, not a general-purpose AI vision or semantic model.** Context detection uses Bengali/English phrase patterns and ranked priorities; some matches will be imperfect.
- **Timing is still scene-level**, not exactly at the time the presenter says each word. Precise alignment would require word timestamp data.
- The presenter remains a stylized **2.5D**, not a rigged 3D person. Mouth animation is energy-driven, not phoneme-correct.
- Focus resizing is approximately smooth in preview and rendered FFmpeg; minor timing/opacity differences may remain. Render cost grows with the number of overlay layers.
- Tested: JavaScript parses, six keyword patterns match, dynamic FFmpeg avatar scale and object opacity render a synthetic H.264/AAC MP4. **Full end-to-end Windows UI export has not yet been tested here.**
- No paid animation API. AI voice optionally sends script text online via unofficial Edge TTS, or backup gTTS. Internet availability, reliability and commercial licensing are not guaranteed.
- Keep the local server bound to localhost (127.0.0.1), not public Internet.

## Research-based design rationale
- Nielsen Norman Group: purposeful restrained motion is more useful than excessive animation: https://www.nngroup.com/articles/animation-purpose-ux/
- University of West Florida: avoid rapid flashing or unnecessary motion in social media videos: https://uwf.edu/brand/social-media/social-media-videos-best-practices/
- Clemson: stick to consistent motion types and gentle fade/slide/zoom styles: https://www.clemson.edu/brand/imagery/videography.html
