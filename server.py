"""Local-only Reel Maker API with FFmpeg transitions."""
import http.server, json, pathlib, shutil, subprocess, tempfile, threading, webbrowser, zipfile, io, base64, os, hmac, binascii
from urllib.parse import urlsplit,parse_qs
from voice_engine import make_voice
from avatar_engine import presenter_svg, mouth_intervals, open_expression
from email.parser import BytesParser
from email.policy import default

ROOT = pathlib.Path(__file__).resolve().parent
CLOUD_LITE = os.environ.get('CLOUD_LITE','0') == '1'
APP_PASSWORD = os.environ.get('APP_PASSWORD','')
PUBLIC_HOST = os.environ.get('HOST','0.0.0.0' if CLOUD_LITE else '127.0.0.1')
PUBLIC_PORT = int(os.environ.get('PORT','8765'))
WORK_SEMAPHORE = threading.BoundedSemaphore(1)
QUALITY = {'lite':(540,960,15),'hd':(720,1280,24),'full':(1080,1920,30)}
TRANSITIONS = {'fade','slide-up','slide-left'}
PROJECT_FILE_LIMIT = 80 * 1024 * 1024
PROJECT_TOTAL_LIMIT = 170 * 1024 * 1024
PROJECT_MIME = 'application/octet-stream'
def parse_form(headers, payload):
    kind=headers.get('Content-Type','')
    if not kind.startswith('multipart/form-data;'):
        raise ValueError('Expected multipart form')
    head=('Content-Type: '+kind+'\r\nMIME-Version: 1.0\r\n\r\n').encode()
    msg=BytesParser(policy=default).parsebytes(head+payload)
    return {part.get_param('name',header='content-disposition'):part for part in msg.iter_parts()}

def project_json(data):
    project=json.loads(data)
    if not isinstance(project,dict) or project.get('format')!='japanova-reel-project' or project.get('version')!=1:
        raise ValueError('Not a supported Japanova project')
    if not isinstance(project.get('script'),str) or len(project['script'])>3000:
        raise ValueError('Project script invalid')
    scenes=project.get('scenes',[])
    if not isinstance(scenes,list) or not 1<=len(scenes)<=20 or any(
        not isinstance(s,dict) or not isinstance(s.get('text'),str) or len(s['text'])>400
        for s in scenes
    ):raise ValueError('Invalid project scenes')
    settings=project.get('settings',{})
    if not isinstance(settings,dict) or len(settings)>50 or any(
        not isinstance(k,str) or not isinstance(v,(str,int,float,bool))
        for k,v in settings.items()
    ):raise ValueError('Invalid project settings')
    durations=project.get('durations',[])
    if not isinstance(durations,list) or len(durations)!=len(scenes) or any(
        not isinstance(d,(float,int)) or isinstance(d,bool) or not .04<=d<=30 for d in durations
    ) or not .5<=sum(durations)<=30.05:raise ValueError('Invalid project durations')
    return project


def make_command(p, settings, media, music, still=False, has_voice=False):
    w,h,fps=QUALITY[settings['quality']]
    durations=settings['durations']; count=int(settings['count'])
    transitions=settings['transitions']
    if not 1<=count<=20 or len(durations)!=count or len(transitions)!=count: raise ValueError('Invalid scenes')
    total_seconds=sum(durations)
    if any(not isinstance(d,(float,int)) or d<=0 or d>30 for d in durations) or not .5<=total_seconds<=30.02: raise ValueError('Invalid scene durations')
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
    subtitle_mode=settings.get('subtitle_mode','scene' if settings.get('subtitles',False) else 'off')
    if subtitle_mode not in ('off','scene','short'):raise ValueError('Invalid subtitle mode')
    subtitle_count=count if subtitle_mode!='off' else 0
    sprite_rows=settings.get('subtitle_rows',[])
    if subtitle_mode=='short':
        if not isinstance(sprite_rows,list) or len(sprite_rows)!=count:raise ValueError('Subtitle timing count mismatch')
        if sum(len(x) for x in sprite_rows if isinstance(x,list))>140:raise ValueError('Too many highlighted words (140 max)')
        cursor=0.
        for scene,d in enumerate(durations):
            rows=sprite_rows[scene]
            if not isinstance(rows,list) or not 1<=len(rows)<=50:raise ValueError('Too many subtitle rows in scene')
            if any(not isinstance(x,(int,float)) or not cursor-.04<=x<=cursor+d+.04 for x in rows):
                raise ValueError('Subtitle word time outside its scene')
            if any(rows[k+1]<rows[k] for k in range(len(rows)-1)):raise ValueError('Subtitle timestamps unsorted')
            cursor+=d

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
    motion_items=settings.get('motion_items',[])
    if not isinstance(motion_items,list) or len(motion_items)>3:raise ValueError('Too many focus moments')
    motion_style=settings.get('motion_style','bounce')
    if motion_style not in ('fade','slide','float'):raise ValueError('Invalid motion style')
    motion_position=settings.get('motion_position','right')
    if motion_position not in ('left','right','top'):raise ValueError('Invalid motion position')
    size=settings.get('motion_size',100)
    if not isinstance(size,(int,float)) or not 65<=size<=120:raise ValueError('Invalid motion size')
    allowed={'coe','passport','visa','bank','university','language','japan'}
    used=set();used_categories=set()
    scene_starts=[];cursor=0.
    for d in durations:scene_starts.append(cursor);cursor+=d
    for item in motion_items:
        if not isinstance(item,dict):raise ValueError('Invalid motion item')
        scene=item.get('scene');ident=item.get('id')
        if not isinstance(scene,int) or not 0<=scene<count or scene in used or ident not in allowed or ident in used_categories:raise ValueError('Invalid or repeated focus topic')
        used.add(scene);used_categories.add(ident)
        start=float(item.get('start',-1));length=float(item.get('duration',-1))
        if not (scene_starts[scene]-.05<=start<=scene_starts[scene]+durations[scene] and .05<=length<=2.6 and start+length<=scene_starts[scene]+durations[scene]+.05):
            raise ValueError('Motion timing must fit its scene')
        path=p/f'motion{scene}.png'
        if not path.is_file():raise ValueError('Missing motion image')
        cmd+=['-loop','1','-framerate',str(fps),'-i',str(path)]
    motion_index=avatar_index+avatar_count
    audio=motion_index+len(motion_items)
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
        # Animate the presenter from 100% to 75% size during important
        # object moments. The FFmpeg scale filter evaluates every frame.
        aw=max(2,round(w*600/1080/2)*2)
        ah=max(2,round(h*850/1920/2)*2)
        ax={'left':round(w*.01),'center':round((w-aw)/2),'right':round(w-aw-w*.01)}[position]
        ay=round(h*420/1920)
        target_x=round(w*(.55 if motion_position=='left' else .074))
        target_y=round(h*540/1920)
        def ff_focus(clock):
            fragments=[]
            for item in motion_items:
                st=float(item['start']);en=st+float(item['duration'])
                fragments.append(
                    f'min(1,min(max(0,({clock}-{st-.4:.5f})/.4),'
                    f'max(0,({en+.4:.5f}-{clock})/.4)))'
                )
            if not fragments:return '0'
            result=fragments[0]
            for frag in fragments[1:]:result=f'max({result},{frag})'
            return result
        def escaped(expr):
            return expr.replace(',',r'\,')
        frame_focus=escaped(ff_focus(f'n/{fps}'))
        time_focus=escaped(ff_focus('t'))
        for j,pose in enumerate(('closed','open','blink')):
            avatar_stream=avatar_index+j
            avatar_w=f'trunc({aw}*(1-0.25*({frame_focus}))/2)*2'
            avatar_h=f'trunc({ah}*(1-0.25*({frame_focus}))/2)*2'
            filters.append(f'[{avatar_stream}:v]scale=w={avatar_w}:h={avatar_h}:eval=frame,format=rgba[avatar{j}]')
        # Existing position and mouth/blink streams remain synchronous.
        xpos=f'{ax}+({target_x-ax})*({time_focus})'
        ypos=f'{ay}+({target_y-ay})*({time_focus})'
        filters.append(f'[{previous}][avatar0]overlay=x={xpos}:y={ypos}:shortest=0:eof_action=pass[body]')
        previous='body'
        intervals=mouth_intervals(p/'voice.mp3' if has_voice else None)
        if intervals:
            expression=open_expression(intervals)
            filters.append(f'[{previous}][avatar1]overlay=x={xpos}:y={ypos}:shortest=0:eof_action=pass:enable={expression}[speaking]')
            previous='speaking'
        blink='+'.join(f'between(t\\,{float(v):.2f}\\,{float(v)+.12:.2f})' for v in (2.8,6.9,11.4,16.1,20.9,26.3))
        filters.append(f'[{previous}][avatar2]overlay=x={xpos}:y={ypos}:shortest=0:eof_action=pass:enable={blink}[blinking]')
        previous='blinking'
    if motion_items:
        motion_width=max(2,round(w*(350/1080)*(size/100)/2)*2)
        motion_height=max(2,round(h*(350/1920)*(size/100)/2)*2)
        mx={'left':round(w*65/1080),'right':round(w*(1-65/1080)-motion_width),'top':round(w*(1-65/1080)-motion_width)}[motion_position]
        my=round(h*(385 if motion_position=='top' else 720)/1920)
        for j,item in enumerate(motion_items):
            start=float(item['start']);finish=start+float(item['duration'])
            position_x=str(mx);position_y=str(my)
            if motion_style=='slide':
                distance=-round(w*.06) if motion_position=='left' else round(w*.06)
                position_x=f'if(lt(t\\,{start+.4:.5f})\\,{mx}+{distance}*(1-(t-{start:.5f})/.4)\\,{mx})'
            elif motion_style=='float':
                position_y=f'{my}+{max(2,round(h*.004))}*sin(2.5*(t-{start:.5f}))'
            label=f'motionout{j}'
            fade_d=min(.4,float(item['duration'])/3)
            filters.append(f'[{motion_index+j}:v]scale={motion_width}:{motion_height},format=rgba,'
                           f'fade=t=in:st={start:.5f}:d={fade_d:.4f}:alpha=1,'
                           f'fade=t=out:st={finish-fade_d:.5f}:d={fade_d:.4f}:alpha=1[motionasset{j}]')
            filters.append(f'[{previous}][motionasset{j}]overlay=x={position_x}:y={position_y}:'
                           f'shortest=0:eof_action=pass:enable=between(t\\,{start:.5f}\\,{finish:.5f})[{label}]')
            previous=label
    if subtitle_count:
        start=0.
        for i,duration in enumerate(durations):
            end=start+duration
            label=f'caption{i}'
            input_index=first+count+i
            if subtitle_mode=='short':
                # Each scene supplies ONE vertical PNG sprite, with a caption
                # for each word. Dynamic crop selects rows without hundreds
                # of independent FFmpeg input streams.
                rows=sprite_rows[i]
                # FFmpeg crop y is evaluated once per frame (expression 't').
                # Starts are absolute timeline timestamps.
                row_expr='0'
                for j,word_start in enumerate(rows[1:],1):
                    row_expr+=f'+gte(t\\,{float(word_start):.5f})'
                source=f'wordcrop{i}'
                filters.append(
                    f'[{input_index}:v]crop=w=900:h=190:x=0:y=190*({row_expr}),'
                    f'scale={round(w*900/1080)}:{round(h*190/1920)},format=rgba[{source}]'
                )
                position='middle' if settings.get('subtitle_position')=='middle' else 'lower'
                cy=1200 if position=='middle' else 1360
                oy=round(cy*h/1920)
                ox=round((w-round(w*900/1080))/2)
                filters.append(
                    f'[{previous}][{source}]overlay=x={ox}:y={oy}:shortest=0:'
                    f'eof_action=pass:enable=between(t\\,{start:.5f}\\,{end:.5f})[{label}]'
                )
            else:
                filters.append(
                    f'[{previous}][{input_index}:v]overlay=x=0:y=0:'
                    f'shortest=0:eof_action=pass:enable=between(t\\,{start:.6f}\\,{end:.6f})[{label}]'
                )
            previous=label
            start=end
    if has_voice:
        filters.append(f'[{voice_index}:a]aresample=44100,volume=1.0,asplit=2[voiceSide][voiceMain]' if music else f'[{voice_index}:a]aresample=44100,volume=1.0[voiceMain]')
        if music:
            filters.append(f'[{audio}:a]aresample=44100,volume=0.20[music]')
            filters.append('[music][voiceSide]sidechaincompress=threshold=0.015:ratio=8:attack=40:release=350[ducked]')
            filters.append(f'[ducked][voiceMain]amix=inputs=2:duration=first:normalize=0,apad=whole_dur={total_seconds:.6f},atrim=0:{total_seconds:.6f}[aout]')
        else:
            filters.append(f'[voiceMain]apad=whole_dur={total_seconds:.6f},atrim=0:{total_seconds:.6f}[aout]')
    else:
        filters.append(f'[{audio}:a]volume=0.35,atrim=0:{total_seconds:.6f}[aout]')
    cmd+=['-filter_complex_threads','2','-filter_complex',';'.join(filters),'-map',f'[{previous}]','-map','[aout]','-t',f'{total_seconds:.6f}','-r',str(fps),'-c:v','libx264','-threads','2','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-movflags','+faststart',str(p/'reel.mp4')]
    return cmd

class Handler(http.server.BaseHTTPRequestHandler):
    def require_access(self):
        if not CLOUD_LITE:return False
        header=self.headers.get('Authorization','')
        try:
            scheme,data=header.split(' ',1)
            if scheme.lower()!='basic':raise ValueError('Auth scheme')
            decoded=base64.b64decode(data,validate=True).decode('utf8')
            _,password=decoded.split(':',1)
            valid=hmac.compare_digest(password,APP_PASSWORD)
        except (ValueError,UnicodeError,binascii.Error):
            valid=False
        if valid:return False
        self.send_response(401)
        self.send_header('WWW-Authenticate','Basic realm="Japanova Edu", charset="UTF-8"')
        self.send_header('Cache-Control','no-store')
        self.send_header('Content-Length','0')
        self.end_headers()
        return True

    def do_GET(self):
        path=urlsplit(self.path)
        if path.path=='/health':
            data=b'OK'
            self.send_response(200)
            self.send_header('Content-Type','text/plain')
            self.send_header('Content-Length',str(len(data)))
            self.end_headers();self.wfile.write(data);return
        if self.require_access():return
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
        if self.require_access():return
        if self.path not in ('/render','/voice','/project/save','/project/load'):self.send_error(404);return
        if not WORK_SEMAPHORE.acquire(blocking=False):
            self.send_error(429,'Another task is running. Try again in a moment.');return
        try:
            if self.path in ('/project/save','/project/load'):
                n=int(self.headers.get('Content-Length','0'))
                if not 0<n<(24*1024*1024 if CLOUD_LITE else PROJECT_TOTAL_LIMIT):raise ValueError('Project request too large')
                parts=parse_form(self.headers,self.rfile.read(n))
                if self.path=='/project/save':
                    if 'project' not in parts:raise ValueError('Missing project settings')
                    data=parts['project'].get_payload(decode=True)
                    project=project_json(data)
                    archive=io.BytesIO()
                    manifest={}
                    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=3,allowZip64=False) as z:
                        for key,filename in [('media','assets/media'),('music','assets/music'),('voice','assets/voice.mp3')]:
                            if key not in parts:continue
                            content=parts[key].get_payload(decode=True)
                            if len(content)>(10*1024*1024 if CLOUD_LITE else PROJECT_FILE_LIMIT):raise ValueError(f'{key} too large for cloud project (10 MB max)')
                            z.writestr(filename,content)
                            manifest[key]={'name':parts[key].get_filename() or key,'type':parts[key].get_content_type(),'size':len(content)}
                        project['assets']=manifest
                        z.writestr('project.json',json.dumps(project,ensure_ascii=False))
                    content=archive.getvalue()
                    self.send_response(200)
                    self.send_header('Content-Type','application/octet-stream')
                    self.send_header('Content-Disposition','attachment; filename="japanova-project.jrm"')
                    self.send_header('Content-Length',str(len(content)))
                    self.end_headers();self.wfile.write(content);return
                if 'projectFile' not in parts:raise ValueError('Choose a .jrm project')
                payload=parts['projectFile'].get_payload(decode=True)
                if len(payload)>(24*1024*1024 if CLOUD_LITE else PROJECT_TOTAL_LIMIT):raise ValueError('Project too large for cloud')
                with zipfile.ZipFile(io.BytesIO(payload)) as z:
                    members=z.namelist()
                    if len(members)>5 or not set(members).issubset({'project.json','assets/media','assets/music','assets/voice.mp3'}):
                        raise ValueError('Unknown files in project archive')
                    if 'project.json' not in members or z.getinfo('project.json').file_size>100000:
                        raise ValueError('Invalid project manifest')
                    for name in members:
                        if z.getinfo(name).file_size>PROJECT_FILE_LIMIT:raise ValueError('Asset too large in project')
                    if sum(z.getinfo(name).file_size for name in members)>PROJECT_TOTAL_LIMIT:
                        raise ValueError('Project uncompressed size too large')
                    project=project_json(z.read('project.json'))
                    assets={}
                    for key,filename in [('media','assets/media'),('music','assets/music'),('voice','assets/voice.mp3')]:
                        if filename not in members:continue
                        meta=project.get('assets',{}).get(key,{})
                        content=z.read(filename)
                        assets[key]={'name':str(meta.get('name',key))[:160], 'type':str(meta.get('type','application/octet-stream'))[:120],
                                     'data':base64.b64encode(content).decode('ascii')}
                    project['loaded_assets']=assets
                encoded=json.dumps(project,ensure_ascii=False).encode('utf8')
                self.send_response(200);self.send_header('Content-Type','application/json; charset=utf-8')
                self.send_header('Content-Length',str(len(encoded)))
                self.end_headers();self.wfile.write(encoded);return
            if self.path=='/voice':
                size=int(self.headers.get('Content-Length','0'))
                if not 0<size<32000:raise ValueError('Invalid voice request size')
                request=json.loads(self.rfile.read(size))
                result=make_voice(request['scenes'],request['voice'],float(request['speed']),request.get('duration_mode','auto'))
                payload=json.dumps(result).encode('utf8')
                self.send_response(200)
                self.send_header('Content-Type','application/json; charset=utf-8')
                self.send_header('Content-Length',str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return
            n=int(self.headers.get('Content-Length','0'))
            if not 0<n<(24*1024*1024 if CLOUD_LITE else 500000000):raise ValueError('Upload too large for free cloud server (24 MB max)')
            head=('Content-Type: '+self.headers['Content-Type']+'\r\nMIME-Version: 1.0\r\n\r\n').encode()
            msg=BytesParser(policy=default).parsebytes(head+self.rfile.read(n))
            with tempfile.TemporaryDirectory() as d:
                p=pathlib.Path(d);settings=None;media=music=still=has_voice=False
                for part in msg.iter_parts():
                    key=part.get_param('name',header='content-disposition')
                    data=part.get_payload(decode=True)
                    if key=='settings':settings=json.loads(data)
                    elif key in ('base','media','music','voice') or (key and (key.startswith('scene') and key[5:].isdigit() or key.startswith('subtitle') and key[8:].isdigit() or key in ('avatar_closed','avatar_open','avatar_blink') or key.startswith('motion') and key[6:].isdigit())):
                        name='base.png' if key=='base' else 'voice.mp3' if key=='voice' else f'avatar-{key[7:]}.png' if key.startswith('avatar_') else f'{key}.png' if key.startswith(('scene','subtitle','motion')) else key
                        (p/name).write_bytes(data)
                        if key=='media':media=True;still=part.get_content_type().startswith('image/')
                        if key=='music':music=True
                        if key=='voice':has_voice=True
                if settings is None or not (p/'base.png').is_file():raise ValueError('Missing project settings')
                if any(not (p/f'scene{i}.png').is_file() for i in range(int(settings['count']))):raise ValueError('Missing scene image')
                if settings.get('avatar','off')!='off' and any(not (p/f'avatar-{pose}.png').is_file() for pose in ('closed','open','blink')):raise ValueError('Missing presenter images; refresh the page and retry')
                if CLOUD_LITE and settings.get('quality')!='lite':raise ValueError('Free cloud supports Lite 540p only. Choose Lite quality.')
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
        except ValueError as e:self.send_error(400,str(e).replace('\n',' ')[:600])
        except Exception as e:self.send_error(500,str(e).replace('\n',' ')[:1200])
        finally:WORK_SEMAPHORE.release()

if __name__=='__main__':
    if CLOUD_LITE and len(APP_PASSWORD)<12:
        raise RuntimeError('Set APP_PASSWORD in cloud environment (at least 12 characters)')
    s=http.server.ThreadingHTTPServer((PUBLIC_HOST,PUBLIC_PORT),Handler)
    if not CLOUD_LITE:
        threading.Timer(.5,lambda:webbrowser.open(f'http://127.0.0.1:{PUBLIC_PORT}')).start()
    print(f'Japanova Reel Maker serving on {PUBLIC_HOST}:{PUBLIC_PORT}; cloud_lite={CLOUD_LITE}')
    s.serve_forever()
