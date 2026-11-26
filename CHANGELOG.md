# Changelog

## V3.3 — AI Voice Studio
- Optional Bengali and English online Neural TTS with rate adjustment.
- Audio preview and voice cache invalidation when captions are edited.
- Scene-by-scene speech synthesis and voice-aligned 30-second timing.
- FFmpeg H.264/AAC export with optional music ducking.
- Scripts that run too long show an error instead of losing spoken content.
- Preserve V3.2 text themes, typography, transitions, and scene editor.

## V3.2 — Text Design Studio
- Colored captions, shadow and outline, highlight and glow; slide transitions.

## V3.1 — Smart Scenes
- Sentence detection, editable scene durations, 30-second export.
## v3.4 — Auto Subtitle Studio (2026-11-26)
- Added scene-synchronized Bengali/English subtitles.
- Added subtitle on/off, font size, color presets, and position controls.
- Added subtitle overlays to FFmpeg MP4 encoding, preserving AI voice and existing title animations.
- Validated a synthetic FFmpeg MP4 render with two transparent subtitle overlays.
- Scene-level timing only; exact word-level synchronization is not yet implemented.

## V4.0 — Lightweight Presenter Studio (2026-11-26)

- Formal Boy and Formal Girl 2.5D portrait presets, with left/center/right positioning.
- Blink animation in preview and FFmpeg renders.
- Speech energy (RMS) detection creates approximate mouth-open time intervals in MP4; **not phoneme-level lip synchronization**.
- SVG assets are served locally and rasterized in the browser; no CairoSVG, external avatar downloads, paid avatar API or 3D engine required.
- Preserved V3.4's voice narration, scene subtitles, transitions and MP4 export.
- Export filter behavior checked with synthetic 1-second FFmpeg video and audio; Windows application end-to-end requires user testing.

## V4.1 — Smart Motion Graphics (2026-11-26)
- Added automatic recognition of COE, passport, visa, bank, university and Japan keywords in Bengali and English.
- Added browser Canvas generated emoji motion cards, with position and size controls.
- Added Pop & Bounce, Slide and Floating motion styles to preview and FFmpeg MP4 output.
- Hard-capped motion overlays at one per scene and six per reel to reduce visual clutter and CPU load.
- No paid API needed. Object timing is approximate at scene level, not word-accurate.
- FFmpeg animation expressions passed synthetic 2-second H.264/AAC smoke tests; full Windows flow remains to be verified.
