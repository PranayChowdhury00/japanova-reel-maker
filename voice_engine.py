"""Optional online TTS for short Bengali/English social reels."""
import asyncio, base64, pathlib, shutil, subprocess, tempfile

VOICES={'bn-BD-PradeepNeural','bn-BD-NabanitaNeural','en-US-AndrewNeural','en-US-AriaNeural'}

def probe_seconds(path):
    ffprobe=shutil.which('ffprobe')
    if not ffprobe: raise RuntimeError('FFprobe missing. Install FFmpeg.')
    result=subprocess.run([ffprobe,'-v','error','-show_entries','format=duration','-of','default=nokey=1:noprint_wrappers=1',str(path)],capture_output=True,text=True,timeout=15,check=True)
    return float(result.stdout.strip())

async def synthesize(scenes,voice,speed,folder):
    try: import edge_tts
    except ImportError as e: raise RuntimeError('Missing voice package. Run: py -3 -m pip install edge-tts') from e
    paths=[]
    for i,caption in enumerate(scenes):
        path=folder/f'voice-{i}.mp3'
        rate=f'{round((speed-1)*100):+d}%'
        await edge_tts.Communicate(caption,voice=voice,rate=rate).save(str(path))
        if not path.exists() or path.stat().st_size<300: raise RuntimeError(f'Voice generation failed in scene {i+1}')
        paths.append(path)
    return paths

def make_voice(scenes,voice,speed):
    if voice not in VOICES: raise ValueError('Unsupported voice')
    if not isinstance(speed,(int,float)) or not .75<=speed<=1.4: raise ValueError('Voice speed must be 0.75–1.40x')
    if not 1<=len(scenes)<=20 or any(not isinstance(s,str) or not s.strip() or len(s)>400 for s in scenes): raise ValueError('Provide 1–20 nonempty scenes, each <=400 chars')
    if sum(map(len,scenes))>2500: raise ValueError('Script too long for 30-second reel')
    ff=shutil.which('ffmpeg')
    if not ff: raise RuntimeError('FFmpeg missing')
    with tempfile.TemporaryDirectory() as temp:
        folder=pathlib.Path(temp)
        paths=asyncio.run(synthesize(scenes,voice,speed,folder))
        lengths=[probe_seconds(p) for p in paths]
        reserved=sum(lengths)+.13*len(lengths)
        if reserved>29.6: raise ValueError(f'Voice needs {reserved:.1f}s. Shorten the script or increase speed to fit 30s.')
        spare=30-reserved
        weights=[max(1,len(s)) for s in scenes]; weight_total=sum(weights)
        durations=[length+.13+spare*weight/weight_total for length,weight in zip(lengths,weights)]
        durations[-1]+=30-sum(durations)
        starts=[]; cursor=0.
        for d in durations: starts.append(cursor);cursor+=d
        command=[ff,'-hide_banner','-loglevel','error','-y']
        for path in paths: command+=['-i',str(path)]
        filters=[]
        for i,start in enumerate(starts):
            delay=round(start*1000)
            filters.append(f'[{i}:a]aresample=44100,aformat=channel_layouts=stereo,adelay={delay}|{delay}[a{i}]')
        filters.append(''.join(f'[a{i}]' for i in range(len(paths)))+f'amix=inputs={len(paths)}:duration=longest:normalize=0,apad=whole_dur=30,atrim=0:30[out]')
        output=folder/'voice.mp3'
        command+=['-filter_complex',';'.join(filters),'-map','[out]','-c:a','libmp3lame','-b:a','160k',str(output)]
        result=subprocess.run(command,capture_output=True,timeout=120)
        if result.returncode: raise RuntimeError('FFmpeg voice processing failed: '+result.stderr.decode(errors='replace')[-500:])
        return {'audio_base64':base64.b64encode(output.read_bytes()).decode('ascii'),'durations':[round(d,5) for d in durations],'voice':voice,'spoken_seconds':round(sum(lengths),2)}
