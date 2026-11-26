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
