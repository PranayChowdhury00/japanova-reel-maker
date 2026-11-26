"""Online Bengali/English TTS with retries and an optional backup provider.

Edge TTS is an unofficial service and occasionally returns NoAudioReceived.
gTTS provides a separate online fallback; it may also fail during outages.
"""
import asyncio
import base64
import pathlib
import re
import shutil
import subprocess
import tempfile

VOICES = {'bn-BD-PradeepNeural', 'bn-BD-NabanitaNeural',
          'en-US-AndrewNeural', 'en-US-AriaNeural'}

def probe_seconds(path):
    executable = shutil.which('ffprobe')
    if not executable:
        raise RuntimeError('FFprobe not found. Please install FFmpeg.')
    result = subprocess.run(
        [executable, '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'default=nokey=1:noprint_wrappers=1', str(path)],
        capture_output=True, text=True, timeout=15, check=True
    )
    return float(result.stdout.strip())

def clean_speech(text):
    # Remove URL, invisible controls, emoji/symbols that can upset TTS requests.
    text = re.sub(r'https?://\S+', '', text)
    text = ''.join(c for c in text if c.isprintable() or c in '\n\t')
    text = re.sub(r'[\U0001F000-\U0010FFFF]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

async def edge_generate(scenes, voice, speed, folder):
    import edge_tts
    paths = []
    rate = f'{round((speed - 1) * 100):+d}%'
    for i, caption in enumerate(scenes):
        dest = folder / f'voice-{i}.mp3'
        error = None
        for attempt in range(3):
            dest.unlink(missing_ok=True)
            try:
                await asyncio.wait_for(
                    edge_tts.Communicate(caption, voice=voice, rate=rate).save(str(dest)),
                    timeout=35
                )
                if dest.exists() and dest.stat().st_size > 300:
                    error = None
                    break
                raise RuntimeError('No audio data returned')
            except Exception as exc:
                error = exc
                if attempt < 2:
                    await asyncio.sleep(1.5 * (attempt + 1))
        if error is not None:
            raise RuntimeError(f'Edge TTS failed at scene {i+1}: {type(error).__name__}: {str(error)[:170]}')
        paths.append(dest)
    return paths

def google_generate(scenes, voice, speed, folder):
    from gtts import gTTS
    lang = 'bn' if voice.startswith('bn-') else 'en'
    paths = []
    for i, caption in enumerate(scenes):
        dest = folder / f'backup-{i}.mp3'
        error = None
        for attempt in range(2):
            dest.unlink(missing_ok=True)
            try:
                # gTTS has no male/female selector; this is a standard voice.
                gTTS(text=caption, lang=lang, slow=False, timeout=20).save(str(dest))
                if dest.exists() and dest.stat().st_size > 300:
                    error = None
                    break
                raise RuntimeError('Backup TTS returned empty audio')
            except Exception as exc:
                error = exc
        if error is not None:
            raise RuntimeError(f'Backup TTS failed at scene {i+1}: {type(error).__name__}: {str(error)[:170]}')
        paths.append(dest)
    return paths

def _sync_audio(paths, durations, starts, folder, speed_factor=1.):
    ff = shutil.which('ffmpeg')
    if not ff:
        raise RuntimeError('FFmpeg not found')
    command = [ff, '-hide_banner', '-loglevel', 'error', '-y']
    for path in paths:
        command += ['-i', str(path)]
    filters = []
    for i, start in enumerate(starts):
        delay = max(0, round(start * 1000))
        # aresample and channel conversion avoid inconsistent mono/stereo files.
        filters.append(
            f'[{i}:a]aresample=44100,aformat=channel_layouts=stereo,'
            f'adelay={delay}|{delay}[a{i}]'
        )
    filters.append(
        ''.join(f'[a{i}]' for i in range(len(paths)))
        + f'amix=inputs={len(paths)}:duration=longest:normalize=0,'
        'apad=whole_dur=30,atrim=0:30[out]'
    )
    output = folder / 'voice.mp3'
    command += ['-filter_complex', ';'.join(filters), '-map', '[out]',
                '-c:a', 'libmp3lame', '-b:a', '160k', str(output)]
    result = subprocess.run(command, capture_output=True, timeout=120)
    if result.returncode:
        raise RuntimeError('FFmpeg voice processing failed: '
                           + result.stderr.decode(errors='replace')[-500:])
    if not output.exists() or output.stat().st_size <= 300:
        raise RuntimeError('Voice mixing produced no audio')
    return output

def make_voice(scenes, voice, speed):
    if voice not in VOICES:
        raise ValueError('Unsupported voice')
    if not isinstance(speed, (int, float)) or not .75 <= speed <= 1.4:
        raise ValueError('Voice speed must be 0.75–1.40x')
    if not 1 <= len(scenes) <= 20 or any(
        not isinstance(s, str) or not s.strip() or len(s) > 400 for s in scenes
    ):
        raise ValueError('Provide 1–20 nonempty scenes, each <=400 characters')
    if sum(map(len, scenes)) > 2500:
        raise ValueError('Script too long for 30-second reel')
    captions = [clean_speech(text) for text in scenes]
    if any(not caption for caption in captions):
        raise ValueError('One scene contains no speakable text')
    if not shutil.which('ffmpeg'):
        raise RuntimeError('FFmpeg is required for voice generation')

    with tempfile.TemporaryDirectory() as temp:
        folder = pathlib.Path(temp)
        primary_error = ''
        try:
            paths = asyncio.run(edge_generate(captions, voice, speed, folder))
            provider = 'Edge Neural Voice'
        except Exception as exc:
            primary_error = str(exc)
            try:
                paths = google_generate(captions, voice, speed, folder)
                provider = 'Google Translate TTS (backup)'
            except Exception as backup_exc:
                raise RuntimeError(
                    'Both online voice providers failed. '
                    'Check internet access and update dependencies. '
                    f'Edge: {primary_error[:220]}. '
                    f'Backup: {str(backup_exc)[:220]}. '
                    'Try again later or turn Voice Off to export without narration.'
                ) from backup_exc

        lengths = [probe_seconds(path) for path in paths]

        # The backup does not expose a voice speed setting. Time-stretch
        # its individual clips with FFmpeg's atempo filter where requested.
        if provider.startswith('Google') and abs(speed - 1) > .005:
            ff = shutil.which('ffmpeg')
            adjusted = []
            for i, path in enumerate(paths):
                dest = folder / f'adjusted-{i}.mp3'
                command = [ff, '-hide_banner', '-loglevel', 'error', '-y',
                           '-i', str(path), '-filter:a', f'atempo={speed:.3f}',
                           '-c:a', 'libmp3lame', '-b:a', '160k', str(dest)]
                result = subprocess.run(command, capture_output=True, timeout=45)
                if result.returncode:
                    raise RuntimeError('Could not apply voice speed')
                adjusted.append(dest)
            paths = adjusted
            lengths = [probe_seconds(path) for path in paths]

        reserved = sum(lengths) + .13 * len(lengths)
        if reserved > 29.6:
            raise ValueError(
                f'Voice needs {reserved:.1f}s. Shorten script or increase voice speed to fit 30s.'
            )
        spare = 30 - reserved
        weights = [max(1, len(s)) for s in captions]
        total = sum(weights)
        durations = [length + .13 + spare * weight / total
                     for length, weight in zip(lengths, weights)]
        durations[-1] += 30 - sum(durations)
        starts = []
        position = 0.
        for duration in durations:
            starts.append(position)
            position += duration

        output = _sync_audio(paths, durations, starts, folder)
        return {
            'audio_base64': base64.b64encode(output.read_bytes()).decode('ascii'),
            'durations': [round(d, 5) for d in durations],
            'voice': voice,
            'spoken_seconds': round(sum(lengths), 2),
            'provider': provider,
            'notice': ('Backup voice does not support male/female selection.'
                       if provider.startswith('Google') else ''),
        }
