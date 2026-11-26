"""Local-only Reel Maker API with FFmpeg transitions."""
import http.server, json, pathlib, shutil, subprocess, tempfile, threading, webbrowser
from urllib.parse import urlsplit,parse_qs
from voice_engine import make_voice
from avatar_engine import presenter_svg, build_images, mouth_intervals, open_expression
from email.parser import BytesParser
from email.policy import default

ROOT = pathlib.Path(__file__).resolve().parent
QUALITY = {'lite':(540,960,15),'hd':(720,1280,24),'full':(1080,1920,30)}
TRANSITIONS = {'fade','slide-up','slide-left'}

def make_command(p, settings, media, music, still=False, has_voice=False):
    w,h,fps=QUALITY[settings['quality']]
    durations=settings['durations']; count=int(settings['count'])
    transitions=settings['transitions']
    if not 1<=count<=20 or len(durations)!=count or len(transitions)!=count: raise ValueError('Invalid scenes')
    if any(not isinstance(d,(float,int)) or d<=0 or d>30 for d in durations) or abs(sum(durations)-30)>.02: raise ValueError('Invalid scene durations')
    if any(t not in TRANSITIONS for t in transitions): raise ValueError('Invalid transition')
    ff=shutil.which('ffmpeg')
    if not ff: raise RuntimeError('FFmpeg missing; install then restart START.bat')
    cmd=[ff,'-hide_banner','-loglevel','error','-y','-threads','2']
    if media:
        cmd+=['-loop','1','-framerate',str(fps)] if still else ['-stream_loop','-1']
        cmd+=['-i',str(p/'media')]
    base=int(media)
    cmd+=['-loop','1','-framerate',str(fps),'-i',str(p/'base.png')]
    first=base+1
    for i in range(count):cmd+=['-loop','1','-framerate',str(fps),'-i',str(p/f'scene{i}.png')]
    subtitle_count=count if settings.get('subtitles',False) else 0
    if not isinstance(settings.get('subtitles',False),bool): raise ValueError('Invalid subtitle flag')
    for i in range(subtitle_count):
        path=p/f'subtitle{i}.png'
        if not path.is_file(): raise ValueError(f'Missing subtitle image {i}')
        cmd+=['-loop','1','-framerate',str(fps),'-i',str(path)]
    avatar=settings.get('avatar','off')
    if avatar not in ('off','boy','girl'):raise ValueError('Invalid avatar selection')
    position=settings.get('avatar_position','center')
    if position not in ('left','center','right'):raise ValueError('Invalid avatar position')
    avatar_count=3 if avatar!='off' else 0
    for pose in ('closed','open','blink') if avatar_count else ():
        path=p/f'avatar-{pose}.png'
        if not path.is_file():raise ValueError('Missing avatar image')
        cmd+=['-loop','1','-framerate',str(fps),'-i',str(path)]
    avatar_index=first+count+subtitle_count
    audio=avatar_index+avatar_count
    cmd+=['-stream_loop','-1','-i',str(p/'music')] if music else ['-f','lavfi','-i','anullsrc=r=44100:cl=stereo']
    voice_index=None
    if has_voice:
        cmd+=['-i',str(p/'voice.mp3')]
        voice_index=audio+1
    filters=[]
    if media:
        filters.append(f'[0:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,fps={fps},format=yuv420p[bg]')
        filters.append(f'[bg][{base}:v]overlay=shortest=0:eof_action=pass:format=auto[plate]')
    else: filters.append(f'[{base}:v]format=rgba[plate]')
    previous='plate';start=0.
    for i,(duration,transition) in enumerate(zip(durations,transitions)):
        end=start+duration; fade=min(.3,duration/3)
        filters.append(f'[{first+i}:v]format=rgba,trim=duration={duration:.6f},setpts=PTS-STARTPTS+{start:.6f}/TB,fade=t=in:st={start:.6f}:d={fade:.6f}:alpha=1,fade=t=out:st={end-fade:.6f}:d={fade:.6f}:alpha=1[txt{i}]')
        x='0';y='0'
        if transition=='slide-left':
            x=f'if(lt(t\\,{start+.5:.6f})\\,max(0\\,W*(1-(t-{start:.6f})/0.5))\\,0)'
        if transition=='slide-up':
            y=f'if(lt(t\\,{start+.5:.6f})\\,max(0\\,H*(1-(t-{start:.6f})/0.5))\\,0)'
        filters.append(f'[{previous}][txt{i}]overlay=x={x}:y={y}:shortest=0:eof_action=pass:format=auto[compose{i}]')
        previous=f'compose{i}';start=end
    if avatar_count:
        # Relative geometry keeps presenter consistent at Lite / HD / Full HD.
        aw=max(2,round(w*600/1080/2)*2)
        ah=max(2,round(h*850/1920/2)*2)
        ax={'left':round(w*.01),'center':round((w-aw)/2),'right':round(w-aw-w*.01)}[position]
        ay=round(h*420/1920)
        for j,pose in enumerate(('closed','open','blink')):
            filters.append(f'[{avatar_index+j}:v]scale={aw}:{ah},format=rgba[avatar{j}]')
        filters.append(f'[{previous}][avatar0]overlay=x={ax}:y={ay}:shortest=0:eof_action=pass[body]')
        previous='body'
        # Voice-energy-derived mouth activity, sampled from the generated voice track.
        intervals=mouth_intervals(p/'voice.mp3' if has_voice else None)
        if intervals:
            expression=open_expression(intervals)
            filters.append(f'[{previous}][avatar1]overlay=x={ax}:y={ay}:shortest=0:eof_action=pass:enable={expression}[speaking]')
            previous='speaking'
        blink='+'.join(f'between(t\\,{float(v):.2f}\\,{float(v)+.12:.2f})' for v in (2.8,6.9,11.4,16.1,20.9,26.3))
        filters.append(f'[{previous}][avatar2]overlay=x={ax}:y={ay}:shortest=0:eof_action=pass:enable={blink}[blinking]')
        previous='blinking'
    if subtitle_count:
        start=0.
        for i,duration in enumerate(durations):
            end=start+duration
            label=f'caption{i}'
            # Enable each transparent caption only during its scene;
            # overlays are looped so they don't expire mid-video.
            filters.append(
                f'[{previous}][{first+count+i}:v]'
                f'overlay=x=0:y=0:shortest=0:eof_action=pass:'
                f'enable=between(t\\,{start:.6f}\\,{end:.6f})[{label}]'
            )
            previous=label
            start=end
    if has_voice:
        filters.append(f'[{voice_index}:a]aresample=44100,volume=1.0,asplit=2[voiceSide][voiceMain]' if music else f'[{voice_index}:a]aresample=44100,volume=1.0[voiceMain]')
        if music:
            filters.append(f'[{audio}:a]aresample=44100,volume=0.20[music]')
            filters.append('[music][voiceSide]sidechaincompress=threshold=0.015:ratio=8:attack=40:release=350[ducked]')
            filters.append('[ducked][voiceMain]amix=inputs=2:duration=first:normalize=0,apad=whole_dur=30,atrim=0:30[aout]')
        else:
            filters.append('[voiceMain]apad=whole_dur=30,atrim=0:30[aout]')
    else:
        filters.append(f'[{audio}:a]volume=0.35,atrim=0:30[aout]')
    cmd+=['-filter_complex_threads','2','-filter_complex',';'.join(filters),'-map',f'[{previous}]','-map','[aout]','-t','30','-r',str(fps),'-c:v','libx264','-threads','2','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-movflags','+faststart',str(p/'reel.mp4')]
    return cmd

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        path=urlsplit(self.path)
        if path.path=='/avatar':
            q=parse_qs(path.query)
            try:
                gender=q.get('gender',['boy'])[0]
                pose=q.get('pose',['closed'])[0]
                data=presenter_svg(gender,pose).encode('utf8')
            except ValueError:self.send_error(400,'Invalid avatar');return
            self.send_response(200)
            self.send_header('Content-Type','image/svg+xml; charset=utf-8')
            self.send_header('Cache-Control','public, max-age=3600')
            self.send_header('Content-Length',str(len(data)))
            self.end_headers();self.wfile.write(data);return
        if path.path!='/': self.send_error(404);return
        data=(ROOT/'index.html').read_bytes()
        self.send_response(200)
        self.send_header('Content-Type','text/html; charset=utf-8')
        self.send_header('Cache-Control','no-store')
        self.end_headers();self.wfile.write(data)
    def do_POST(self):
        if self.path not in ('/render','/voice'):self.send_error(404);return
        try:
            if self.path=='/voice':
                size=int(self.headers.get('Content-Length','0'))
                if not 0<size<32000:raise ValueError('Invalid voice request size')
                request=json.loads(self.rfile.read(size))
                result=make_voice(request['scenes'],request['voice'],float(request['speed']))
                payload=json.dumps(result).encode('utf8')
                self.send_response(200)
                self.send_header('Content-Type','application/json; charset=utf-8')
                self.send_header('Content-Length',str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return
            n=int(self.headers.get('Content-Length','0'))
            if not 0<n<500000000:raise ValueError('Invalid upload size')
            head=('Content-Type: '+self.headers['Content-Type']+'\r\nMIME-Version: 1.0\r\n\r\n').encode()
            msg=BytesParser(policy=default).parsebytes(head+self.rfile.read(n))
            with tempfile.TemporaryDirectory() as d:
                p=pathlib.Path(d);settings=None;media=music=still=has_voice=False
                for part in msg.iter_parts():
                    key=part.get_param('name',header='content-disposition')
                    data=part.get_payload(decode=True)
                    if key=='settings':settings=json.loads(data)
                    elif key in ('base','media','music','voice') or (key and (key.startswith('scene') and key[5:].isdigit() or key.startswith('subtitle') and key[8:].isdigit())):
                        name='base.png' if key=='base' else 'voice.mp3' if key=='voice' else f'{key}.png' if key.startswith(('scene','subtitle')) else key
                        (p/name).write_bytes(data)
                        if key=='media':media=True;still=part.get_content_type().startswith('image/')
                        if key=='music':music=True
                        if key=='voice':has_voice=True
                if settings is None or not (p/'base.png').is_file():raise ValueError('Missing project settings')
                if any(not (p/f'scene{i}.png').is_file() for i in range(int(settings['count']))):raise ValueError('Missing scene image')
                if settings.get('avatar','off')!='off':build_images(p,settings['avatar'])
                cmd=make_command(p,settings,media,music,still,has_voice)
                r=subprocess.run(cmd,capture_output=True,timeout=900)
                if r.returncode:raise RuntimeError(r.stderr.decode(errors='replace')[-2000:])
                file=p/'reel.mp4'
                self.send_response(200)
                self.send_header('Content-Type','video/mp4')
                self.send_header('Content-Length',str(file.stat().st_size))
                self.end_headers()
                with file.open('rb') as f:shutil.copyfileobj(f,self.wfile)
        except (BrokenPipeError,ConnectionResetError):pass
        except Exception as e:self.send_error(500,str(e).replace('\n',' ')[:1200])

if __name__=='__main__':
    s=http.server.ThreadingHTTPServer(('127.0.0.1',8765),Handler)
    threading.Timer(.5,lambda:webbrowser.open('http://127.0.0.1:8765')).start()
    print('Japanova Reel Maker V4.0: http://127.0.0.1:8765')
    s.serve_forever()
