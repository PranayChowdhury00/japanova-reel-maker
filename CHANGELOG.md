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

## V4.2 — Minimal Cinematic Focus (2026-11-26)
- Replaced repeated emoji pop-ups with consistent illustrated objects and restrained motion.
- Presenter smoothly shrinks to 75% and shifts aside during focus moments, then returns.
- Added context-sensitive topic selection, max three focus moments, one display per unique topic, and 3.8-second spacing.
- Default motion changed to soft fade and zoom; gentle slide and float remain optional.
- Generic Japan keyword no longer automatically produces airplane; travel context required.
- Integrated FFmpeg dynamic scaling/positioning and alpha fade with animated focus objects.
- Smoke-tested FFmpeg dynamic scaling and combined H.264/AAC 5-second synthetic render. Full Windows end-to-end remains unverified.

## V4.3 — Professional Subtitle & Stability (2026-11-26)
- Added default 3–4-word grouped subtitles with highlighted current word; classic full-scene subtitles and Off remain available.
- Captured Edge TTS WordBoundary timestamp metadata; estimates timing when metadata mismatches or backup Google TTS is used.
- Added one vertical PNG subtitle sprite per scene and per-frame FFmpeg crop selection to limit stream count.
- Added export preflight checks for empty/long scenes, total script words, missing presenter assets, and large background files.
- Synthetic FFmpeg test confirmed correct row selection and playable H.264/AAC output.
- Full online voice + Windows UI end-to-end test remains unverified.

## V4.3.1 — Auto Reel Duration Hotfix (2026-11-26)
- Voice clips now assemble to their natural total duration plus short scene/end padding rather than always padding to 30 seconds.
- Added Auto (default) vs Fixed 30s selection.
- FFmpeg audio and video trimming use the selected total duration; browser preview/progress/timeline and word timestamps align to it.
- Voice Off mode uses estimated text-length playback; maximum 30 seconds remains enforced.
- Short text no longer forces an extra ~20 seconds of dead air in Auto mode.
- Full Windows voice-generation and MP4-export workflow awaits local verification.

## V4.4 — Save & Resume Projects (2026-11-26)
- Added portable **Save Project (.jrm)** and **Open Project (.jrm)** controls.
- Archive includes the scene editor state, settings, scene durations and optional embedded original background, music, and previously generated AI narration audio.
- Reuses cached voice only when settings and script exactly match the saved voice signature.
- ZIP handling uses Python stdlib with explicit member allowlist, per-file byte limits and project schema validation.
- Existing animated preview and MP4 export are untouched; full Windows end-to-end tests are still required.

## V4.5 — Compact Responsive Studio UI (2026-11-26)
- Replaced one long editor with Script, Presenter, Captions, Design and Scenes tabs.
- Compact mobile preview and sticky Preview/Export footer; sticky right-side preview on desktop.
- Collapsed verbose guidance into seven optional Help accordions.
- Preserved IDs, rendering logic, project Save/Open, auto-duration and voice pipelines.
- JavaScript syntax, markup structure and functional ID uniqueness checked; Windows/mobile browser tests pending.
