import http.server, pathlib, tempfile, subprocess, shutil, json, webbrowser, threading, urllib.parse
ROOT=pathlib.Path(__file__).parent
class Handler(http.server.BaseHTTPRequestHandler):
 def do_GET(self):
  if self.path=='/':
   data=(ROOT/'index.html').read_bytes(); self.send_response(200); self.send_header('Content-Type','text/html; charset=utf-8'); self.end_headers(); self.wfile.write(data)
  else: self.send_error(404)
 def do_POST(self):
  if self.path!='/render': self.send_error(404); return
  try:
   from email.parser import BytesParser
   from email.policy import default
   n=int(self.headers['Content-Length']); assert n<500_000_000,'Upload too large'
   msg=BytesParser(policy=default).parsebytes(('Content-Type: '+self.headers['Content-Type']+'\r\nMIME-Version: 1.0\r\n\r\n').encode()+self.rfile.read(n))
   with tempfile.TemporaryDirectory() as tmp:
    p=pathlib.Path(tmp); fields={}
    for part in msg.iter_parts():
     key=part.get_param('name',header='content-disposition'); data=part.get_payload(decode=True)
     if key=='settings': fields=json.loads(data)
     elif key in ('media','music','base') or (key.startswith('scene') and key[5:].isdigit()): (p/key).write_bytes(data)
    w,h,f={'lite':(540,960,15),'hd':(720,1280,24),'full':(1080,1920,30)}[fields['quality']]; count=int(fields['count']); assert 1<=count<=20
    durations=fields['durations']; assert len(durations)==count and all(0<d<=30 for d in durations) and abs(sum(durations)-30)<0.01
    ff=shutil.which('ffmpeg'); assert ff,'FFmpeg not found. Run setup.bat and reopen START.bat.'
    cmd=[ff,'-hide_banner','-loglevel','error','-y','-threads','2']; filters=[]; media=(p/'media').exists(); music=(p/'music').exists()
    if media: cmd+=['-stream_loop','-1','-i',str(p/'media')]
    for i in range(count): cmd+=['-loop','1','-framerate',str(f),'-i',str(p/f'scene{i}')]
    cmd+=['-loop','1','-framerate',str(f),'-i',str(p/'base')]
    if music: cmd+=['-stream_loop','-1','-i',str(p/'music')]
    else: cmd+=['-f','lavfi','-i','anullsrc=r=44100:cl=stereo']
    for i,d in enumerate(durations):
     fade=min(.25,d/3)
     filters.append(f'[{i+int(media)}:v]trim=duration={d},setpts=PTS-STARTPTS,format=rgba,fade=t=in:st=0:d={fade}:alpha=1,fade=t=out:st={d-fade}:d={fade}:alpha=1[s{i}]')
    filters.append(''.join(f'[s{i}]' for i in range(count))+f'concat=n={count}:v=1:a=0[slides]')
    base=count+int(media)
    if media: filters += [f'[0:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,fps={f}[bg]',f'[bg][{base}:v]overlay[plate]']
    else: filters.append(f'[{base}:v]null[plate]')
    filters.append('[plate][slides]overlay=shortest=1[v]'); out='[v]'
    cmd+=['-filter_complex_threads','1','-filter_complex',';'.join(filters),'-map',out,'-map',f'{count+int(media)+1}:a:0','-t','30','-r',str(f),'-c:v','libx264','-threads','2','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-af','volume=0.35','-movflags','+faststart',str(p/'reel.mp4')]
    r=subprocess.run(cmd,capture_output=True,timeout=900); assert r.returncode==0,r.stderr.decode(errors='replace')[-2000:]
    self.send_response(200); self.send_header('Content-Type','video/mp4'); self.end_headers(); self.wfile.write((p/'reel.mp4').read_bytes())
  except Exception as e: self.send_error(500,str(e).replace('\n',' ')[:1000])
if __name__=='__main__':
 s=http.server.ThreadingHTTPServer(('127.0.0.1',8765),Handler); threading.Timer(0.5,lambda:webbrowser.open('http://127.0.0.1:8765')).start(); s.serve_forever()
