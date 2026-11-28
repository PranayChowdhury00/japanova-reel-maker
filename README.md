# Japanova Reel Maker V4.5.1 — Minimal Japanova Edu Header

V4.5 redesigns V4.4 into a compact mobile-friendly dashboard while keeping original video and project APIs.

## New editor layout

- Five tabs: **Script, Presenter, Captions, Design, Scenes**.
- Script: project Save/Open, narration, media, quality, duration.
- Presenter: formal Boy/Girl + Smart Focus motion.
- Captions: Short Word Highlight / Classic / Off and color/size/position.
- Design: typography, transitions and color presets.
- Scenes: Auto Split, scene text, duration weights, per-scene styling.
- Desktop: sticky right-side preview, edit pane on left.
- Phones (up to 700px): compact preview above the editor, scrollable tabs, sticky Preview/Export actions.
- Long instructions are collapsed in expandable help accordions.
- Keyboard tabs: ArrowLeft/ArrowRight, Home, End. Screen-reader tab and panel semantics are provided.

## Update on Windows

Stop the existing application, then run in PowerShell:

    cd C:\Users\USER\japanova-reel-maker
    git pull origin main
    .\START.bat

Press Ctrl+Shift+R to hard-refresh the browser.

## Quick regression check

1. Edit a script on Script.
2. Select Presenter settings, and Captions/Design in other tabs without losing scene text.
3. Visit Scenes, Auto Split, and edit scene-specific colors and duration.
4. Preview/Export and confirm original functions remain working.
5. Save a .jrm project, reopen it and verify your settings and media.

## Notes

- Tab switching does not destroy controls or remove selected files.
- Original FFmpeg, TTS, Save/Open project code remains untouched.
- No new paid APIs or third-party packages.
- HTML structure, script syntax, unique functional IDs were checked, but **full interactive Windows/mobile end-to-end testing remains to be done locally**.

## V4.5.1 header polish

- Company-first white header with **JAPANOVA EDU** and restrained Open/Save project actions.
- Removed version number, technical feature names, and redundant 'Local Studio' display from the header.
- On mobile, the five editing tabs become a compact fixed **bottom navigation bar**. Header project actions remain available as icon buttons.
- Replaced decorative preview status with the actual reel length and scene count.
- Normal success messages are hidden; only errors/warnings and in-progress voice/render notices appear, so the interface stays quiet. Browser download remains the confirmation for Save/Export.
- No changes to the actual reel generation or audio/video pipeline.
- Static validation: JavaScript syntax, unique IDs, all five tabs and mobile CSS passed. Full Windows/mobile browser tests are pending.

## Cloud Lite Edition — Free public shareable link (experimental)

This repository now includes a Dockerfile and Render Blueprint (render.yaml) to run the complete Python app, FFmpeg and Bengali fonts in a cloud container. **Cloud Lite is opt-in**; the Windows localhost version continues to use the existing START.bat and HD/Full HD settings.

### Deploy on Render

1. Sign up at https://dashboard.render.com/ and connect GitHub.
2. Choose **New → Blueprint**, select `PranayChowdhury00/japanova-reel-maker`, and allow the `render.yaml` configuration.
3. Select the **Free** plan. Render will build its Dockerfile, including FFmpeg.
4. **Set APP_PASSWORD** in the Render Blueprint prompt (minimum 12 characters). Never commit this password to GitHub or publicly post it.
5. Once deployment succeeds, open the HTTPS `*.onrender.com` URL provided by Render. The browser asks for a username and password. Use any nonempty username, and the APP_PASSWORD you configured. Share the link and password only with people you trust.

**Security/privacy:** This is simple HTTP Basic Authentication via HTTPS, suitable for a small trusted pilot, not a polished public user-account system. Anyone with the shared password can upload material and run a render, so do not post the password publicly. For an unrestricted public launch, implement individual sign-in, per-user rate limiting/quotas, abuse controls and media retention policy first. No student personal documents should be uploaded without necessary consent and safeguards.

### Free cloud limits

- Free Render memory is only 512 MB. Cloud Lite defaults to **540p / 15fps**; 720p and 1080p remain exclusive to local Windows.
- One server-side task at a time; another concurrent request may return HTTP 429.
- Raw render / save or load requests limited to about **24 MB**. UI rejects images/video larger than 8 MB and music larger than 5 MB; choose lightweight media.
- ZIP Save/Load has tighter cloud asset limits (10 MB each).
- The free service sleeps after 15 minutes of inactivity and can take a while to wake. Render has bandwidth and free-instance-hour limits and may restart free instances.
- Cloud voice still depends on external Edge TTS and gTTS services. The free service is **not guaranteed to successfully render every MP4** and is not a high-traffic production host.
- A project is saved by downloading a .jrm file to the user's device. No persistent project database is provided.
- Initial deployment needs to be completed and tested in your own Render account. **No public live URL exists until Render reports a successful deployment**.

Render docs: https://render.com/docs/free · https://render.com/docs/blueprint-spec


## Auto Duration up to 60 seconds — Voice fix (2026-11-28)

Previously, scripts requiring over 29.6 seconds of TTS triggered HTTP 400 even when **Auto Duration** was selected. The video editor and voice engine now support a natural-length **Auto Duration of up to 60 seconds**, with short pauses between scenes and a small final hold. Audio is never silently truncated to 30 seconds.

- **Auto — Follows voice (up to 60s):** 46.5 seconds of narration becomes approximately 47–49 seconds of video depending on the number of scenes.
- **Fixed 30 Seconds:** still strictly limited to 30 seconds. If narration is longer, choose Auto, shorten the script or increase speed.
- Video export, saved project durations and editor estimates have been increased to 60 seconds.
- Videos exceeding 60 seconds must still be shortened or split into separate reels; cloud free hosting may struggle with longer render jobs.
- Added a regression test suite at `tests/test_duration.py` (run `python -m unittest discover -s tests -v`). Runtime tests in a real browser and Windows/Cloud FFmpeg environment remain necessary.

Update locally using `git pull origin main`, restart `START.bat`, hard-refresh the page with `Ctrl+Shift+R`, choose Auto Duration and generate voice again.

## V4.7 — Smart Timeline Editor (2026-11-28)

This release adds scene-aware editing controls in the **Scenes** tab:

- **Timeline strips:** proportional scene blocks, click any block to inspect its first frame, or drag the scrubber to a precise moment. Play from Start highlights the currently active scene.
- **Scene duration:** manually adjust when no generated voice is locked. Once voice is generated, its scene durations are locked to prevent audio and word highlights drifting out of sync. Change narration settings and regenerate voice to get fresh durations.
- **Smart Object controls per scene:** Auto Detect (default), No Object, or Choose Object. Manual mode lets you set its category, the number of seconds after the scene begins when it appears, and how long it stays (up to 2.6 seconds).
- **Per-scene captions:** Show/Hide and Caption Delay within that scene.
- **Per-scene presenter:** Show/Hide. Presenter lip and blink overlays follow that visibility in the exported video.
- **Focus moment safeguards:** the reel still uses at most three distinct object categories with starts at least 3.8 seconds apart. Export warns on invalid manual focus timing. Global Smart Objects Off continues to disable all focus moments.
- **Portable project persistence:** new V4.7 timeline controls are saved into existing `.jrm` project format. Older project files remain supported; missing fields default to Auto Object and visible Presenter/Captions.
- **Export parity:** the same per-scene timings and visibility are sent to FFmpeg for rendered MP4, not merely for editor preview.

### How to use

1. Update as usual: `git pull origin main`, then `.\START.bat`. Hard-refresh the browser with `Ctrl+Shift+R`.
2. Open **Scenes** and click a scene block in the timeline. Drag the scrubber to inspect the animation.
3. Scroll to the chosen scene. Select **Object Mode → Choose Object** to override keyword detection, set **Appear after** and **Visible for**.
4. Toggle **Show Presenter** or **Show Captions** and optionally set a **Caption delay**.
5. Preview, Export MP4, and verify the changes are present in the downloaded file.
6. Save a `.jrm` project and reopen it to verify the timeline controls persist.

### Limitations

- This is a **scene timeline with manually adjustable focus moments**, not a full multitrack nonlinear video editor. Custom image placement and freeform keyframes are planned separately.
- Caption delay offsets visibility within the scene; it does not re-time TTS word boundaries. Hiding captions does not delete the voice audio.
- Presenter on/off is scene-level rather than a per-frame entrance animation.
- Script and voice generation remain limited to 60 seconds in Auto mode.
- JavaScript syntax, manual/auto focus selection, invalid timing and duplicate topic checks were exercised; unit regression tests are in `tests/test_timeline.py`. End-to-end FFmpeg export on Windows and mobile is still unverified here.

## V4.8 — Custom Image & Object Library (2026-11-28)

Implemented in the repository. JavaScript syntax and integration points were reviewed; full Windows FFmpeg export requires local end-to-end confirmation.

- Upload up to 8 PNG, JPG or WebP images (12MB maximum per source, auto-resized for projects). Transparent PNGs retain transparency.
- In Scenes, select a scene on the Timeline, then click Use on the chosen library image. One custom image per scene; this is separate from auto-detected Smart Objects.
- Drag the image within Preview, resize using the cyan lower-right handle, or edit its X/Y/Width numerically (1080×1920 logical coordinates).
- Set Appear after and Visible for to place the image in the scene's timeline.
- Reuse an image across multiple scenes; remove a scene image separately from the library.
- The browser attempts to retain the image library locally. Portable .jrm files embed the images; saving the project is the reliable backup. Old projects remain compatible.
- MP4 export composites the same custom transparent PNG images at the same times; selection handles are not exported.

Instructions: run git pull origin main; restart START.bat; hard-refresh with Ctrl+Shift+R. Open Scenes, upload an image, select a scene, tap Use, drag/resize in Preview, adjust the timing, preview and Export MP4. Save and reopen a .jrm to check portability.

Limits: one custom image per scene; eight reusable assets/layers maximum. No rotation, multi-image per scene, freeform keyframes or animated GIF support yet. Images and timings must remain within their scene/frame bounds. Multiple full-frame PNG overlays may use considerable CPU/RAM during rendering; test at Lite 540p first. Browser local storage can be erased, so keep a .jrm file for important projects. Regression tests were added in tests/test_custom_images.py but real Windows FFmpeg encoding has not been run in this session.
