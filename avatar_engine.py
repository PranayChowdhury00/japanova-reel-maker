"""Lightweight self-contained stylized presenter SVG and speech-energy animation.

This is a 2.5D character, not a rigged 3D model or phoneme-based lip sync.
"""
import math
import pathlib
import subprocess
import shutil

AVATARS = {'boy','girl'}
POSITIONS = {'left','center','right'}
POSES = {'closed','open','blink'}

def presenter_svg(gender='boy',pose='closed'):
    if gender not in AVATARS or pose not in POSES: raise ValueError('Invalid avatar pose')
    girl=gender=='girl'
    hair='#211b2b' if girl else '#1a2635'
    jacket='#334869' if girl else '#233c62'
    skin='#e9a981' if girl else '#cf946f'
    highlight='#f5c6a2' if girl else '#e6ae88'
    hair_back = ('<path d="M152 250 Q95 130 205 82 Q330 5 427 90 Q505 145 457 495 L415 515 L166 505Z" fill="url(#hair)"/>' if girl else '')
    hair_front = ('<path d="M170 201 Q144 101 226 89 Q321 25 424 117 Q470 170 437 252 Q412 173 361 158 Q276 224 170 201Z" fill="url(#hair)"/>'
       if girl else '<path d="M168 219 Q132 136 188 95 Q236 33 313 66 Q421 28 451 150 L432 220 Q408 152 368 143 Q304 196 251 161 Q222 199 168 219Z" fill="url(#hair)"/>')
    eyes = ('<path d="M231 275 q28 -12 55 0 M330 275 q28 -12 55 0" fill="none" stroke="#422f2d" stroke-width="8" stroke-linecap="round"/>' if pose=='blink'
       else '<ellipse cx="260" cy="279" rx="12" ry="15" fill="#273340"/><ellipse cx="357" cy="279" rx="12" ry="15" fill="#273340"/><circle cx="265" cy="272" r="4" fill="#fff"/><circle cx="361" cy="272" r="4" fill="#fff"/>')
    mouth = ('<ellipse cx="308" cy="376" rx="27" ry="26" fill="#763b48"/><ellipse cx="308" cy="387" rx="18" ry="9" fill="#c97479"/>' if pose=='open'
        else '<path d="M282 369 Q309 389 337 369" fill="none" stroke="#914d4b" stroke-width="7" stroke-linecap="round"/>')
    hair_side = ('<path d="M153 216 Q129 353 164 490 L199 482 L187 212Z M435 221 Q467 348 430 500 L402 487 L420 208Z" fill="url(#hair)"/>' if girl else '')
    tie = ('<path d="M300 495 L318 495 L331 610 L310 648 L289 611Z" fill="#c63b54"/>' if not girl else '<path d="M285 498 Q308 535 332 498" stroke="#fff" stroke-width="16" fill="none"/>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="600" height="850" viewBox="0 0 600 850">
<defs>
 <linearGradient id="skin" x1="0" x2="1" y1="0" y2="1"><stop stop-color="{highlight}"/><stop offset=".8" stop-color="{skin}"/><stop offset="1" stop-color="#b7735b"/></linearGradient>
 <linearGradient id="hair" x1="0" x2=".8" y1="0" y2="1"><stop stop-color="#506078"/><stop offset=".4" stop-color="{hair}"/><stop offset="1" stop-color="#101826"/></linearGradient>
 <linearGradient id="coat" x1="0" x2="1" y1="0" y2="1"><stop stop-color="#617a9e"/><stop offset=".5" stop-color="{jacket}"/><stop offset="1" stop-color="#14263e"/></linearGradient>
 <linearGradient id="shirt" x1="0" x2="0" y1="0" y2="1"><stop stop-color="#fff"/><stop offset="1" stop-color="#b9cede"/></linearGradient>
 <filter id="shade"><feGaussianBlur stdDeviation="13"/></filter>
</defs>
<!-- shoulders and jacket -->
<ellipse cx="307" cy="803" rx="272" ry="37" fill="#061321" opacity=".16" filter="url(#shade)"/>
<path d="M44 850 L56 662 Q62 536 199 505 L273 485 L338 485 L419 505 Q554 537 554 664 L570 850Z" fill="url(#coat)" stroke="#142840" stroke-width="5"/>
<path d="M226 494 L311 562 L389 494 L364 850 L250 850Z" fill="url(#shirt)"/>
<path d="M184 514 L273 581 L249 632 L308 850 L66 850 L56 675 Q65 554 184 514Z" fill="url(#coat)"/>
<path d="M422 514 L344 581 L369 635 L309 850 L547 850 L552 675 Q542 554 422 514Z" fill="url(#coat)"/>
<path d="M184 514 L271 579 L243 627 L304 808 L216 659 L240 598Z" fill="#152f50" stroke="#8093ae" stroke-width="3"/>
<path d="M422 514 L346 580 L372 628 L314 808 L404 659 L376 596Z" fill="#172c48" stroke="#8093ae" stroke-width="3"/>
<path d="M300 495 L318 495 L317 570 L300 570Z" fill="#f0c3a3"/>
{tie}
<circle cx="404" cy="706" r="6" fill="#bbcce2"/>
<!-- neck -->
<path d="M263 430 L263 512 Q309 556 355 512 L355 425Z" fill="url(#skin)" stroke="#b77862" stroke-width="4"/>
{hair_back}
<!-- face -->
<ellipse cx="169" cy="317" rx="24" ry="42" fill="{skin}"/>
<ellipse cx="448" cy="317" rx="24" ry="42" fill="{skin}"/>
<path d="M161 202 Q177 106 299 105 Q433 104 453 205 L439 378 Q421 468 321 483 Q213 471 180 390Z" fill="url(#skin)" stroke="#bd7b64" stroke-width="5"/>
<ellipse cx="210" cy="344" rx="39" ry="24" fill="#e9807a" opacity=".18"/>
<ellipse cx="408" cy="344" rx="39" ry="24" fill="#e9807a" opacity=".18"/>
{hair_side}{hair_front}
<path d="M223 252 Q251 237 281 253 M328 252 Q358 237 385 253" fill="none" stroke="{hair}" stroke-width="9" stroke-linecap="round"/>
{eyes}
<path d="M305 281 L290 336 Q307 345 323 333" fill="none" stroke="#b87864" stroke-width="5" stroke-linecap="round"/>
{mouth}
<path d="M208 395 Q306 504 407 392" stroke="#f5cdb1" opacity=".14" stroke-width="10" fill="none"/>
<!-- blazer details -->
<path d="M109 765 L109 832 M503 765 L503 832" fill="none" stroke="#92a2bc" stroke-width="4" opacity=".3"/>
</svg>"""

def mouth_intervals(voice_file):
    """Approximate mouth activity by RMS energy, NOT phoneme lip synchronization."""
    if voice_file is None or not pathlib.Path(voice_file).exists(): return []
    ff=shutil.which('ffmpeg')
    if not ff:return []
    cmd=[ff,'-hide_banner','-loglevel','error','-i',str(voice_file),'-t','30','-f','s16le','-ac','1','-ar','4000','pipe:1']
    try: raw=subprocess.run(cmd,capture_output=True,timeout=35,check=True).stdout
    except (subprocess.CalledProcessError,subprocess.TimeoutExpired): return []
    n=len(raw)//2
    if not n:return []
    samples=memoryview(raw).cast('h')
    chunk=400 # 100ms / 4000 Hz
    energies=[]
    for i in range(0,n,chunk):
        segment=samples[i:min(n,i+chunk)]
        if not segment:break
        rms=math.sqrt(sum(int(v)*int(v) for v in segment)/len(segment))/32768
        energies.append(rms)
    if not energies:return []
    peak=max(energies)
    if peak<.001:return []
    threshold=max(.009,peak*.13)
    flags=[e>threshold for e in energies]
    # Merge tiny 100ms gaps to reduce jitter.
    for i in range(1,len(flags)-1):
        if flags[i-1] and flags[i+1]:flags[i]=True
    out=[];start=None
    for i,flag in enumerate(flags+[False]):
        if flag and start is None:start=i
        if not flag and start is not None:
            if i-start>=1:out.append((round(start*.1,3),round(i*.1,3)))
            start=None
    return out[:180]

def open_expression(intervals):
    if not intervals:return '0'
    return '+'.join(f'between(t\\,{a:.3f}\\,{b:.3f})' for a,b in intervals)
