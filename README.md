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
