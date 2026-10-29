from pathlib import Path
import re,json,textwrap,subprocess,html
root=Path(__file__).resolve().parents[1]
assets=root/'assets'; temp=Path(__import__('tempfile').mkdtemp(prefix='shoal-trailer-'))
scenes=json.loads((root/'media/trailer-scenes.json').read_text())
total_duration=sum(scene['duration'] for scene in scenes)

text=(root/'index.html').read_text();icons=re.findall(r'<svg class="icon".*?</svg>',text,re.S)
for name,svg in zip(['swordfish','blobfish','clownfish','pufferfish','anglerfish','shoal'],icons):
    svg=svg.replace('<svg class="icon"','<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512"')
    svg=svg.replace('class="cookie"','fill="#174744"').replace('class="fish"','fill="#a0edc9"').replace('class="ink"','fill="#092729"')
    (temp/f'{name}.svg').write_text(svg)
poster='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720"><rect width="1280" height="720" fill="#092729"/><circle cx="1040" cy="130" r="300" fill="#16443f"/><circle cx="200" cy="700" r="240" fill="#123a36"/><text x="90" y="160" fill="#a0edc9" font-family="sans-serif" font-size="24" letter-spacing="5">MEET SHOAL</text><text x="90" y="320" fill="#f1fff7" font-family="sans-serif" font-size="86" font-weight="700">A fresh current.</text><text x="90" y="420" fill="#a0edc9" font-family="sans-serif" font-size="58">Your kind of apps.</text><circle cx="1070" cy="510" r="70" fill="#a0edc9"/><path d="M1050 475L1106 510L1050 545Z" fill="#092729"/><text x="90" y="600" fill="#c1dbd0" font-family="sans-serif" font-size="24">Six apps · One design language · {duration_label}</text></svg>'''
duration_label=f'{int(total_duration)//60}:{int(total_duration)%60:02d}'
poster=poster.replace('{duration_label}',duration_label)
(assets/'trailer-poster.svg').write_text(poster)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'; bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

for phase in range(3):
    colour=['#986d72','#7d7ab5','#a0edc9'][phase]
    panel=['#352a2b','#302d43','#194d45'][phase]
    labels=[('Video app','ADVERTISEMENT','Upgrade to download'),('Patched YouTube','Your chosen patches','Morphe - independent project'),('Swordfish','Your videos, your colours','A separate Shoal app')][phase]
    interface=f'''<svg xmlns="http://www.w3.org/2000/svg" width="300" height="580" viewBox="0 0 300 580"><rect x="2" y="2" width="296" height="576" rx="42" fill="{panel}" stroke="{colour}" stroke-width="4"/><rect x="120" y="16" width="60" height="7" rx="4" fill="{colour}"/><text x="22" y="66" fill="white" font-family="sans-serif" font-size="21">{labels[0]}</text><rect x="20" y="88" width="260" height="155" rx="{12+phase*7}" fill="{colour}"/><path d="M133 135L175 164L133 191Z" fill="{panel}"/><rect x="20" y="262" width="200" height="9" rx="5" fill="{colour}"/><rect x="20" y="284" width="140" height="7" rx="4" fill="{colour}" opacity=".4"/><rect x="20" y="320" width="260" height="65" rx="18" fill="{colour}" opacity=".2"/><text x="30" y="350" fill="white" font-family="sans-serif" font-size="14">{labels[1]}</text><text x="30" y="372" fill="white" font-family="sans-serif" font-size="12">{labels[2]}</text><rect x="20" y="405" width="260" height="100" rx="22" fill="{colour}" opacity=".35"/><circle cx="85" cy="546" r="10" fill="{colour}"/><circle cx="150" cy="546" r="10" fill="{colour}"/><circle cx="215" cy="546" r="10" fill="{colour}"/></svg>'''
    (temp/f'evolution-{phase}.svg').write_text(interface)

segments=[];vtt=['WEBVTT',''];transcript=[]
def stamp(sec):
    ms=round(sec*1000);return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d}.{ms%1000:03d}'
for i,scene in enumerate(scenes):
    eyebrow,title,body,fish,shot=(scene[k] for k in ['eyebrow','title','body','fish','shot'])
    start=scene['start'];duration=scene['duration']
    vtt += [f'{stamp(start)} --> {stamp(start+duration)}',textwrap.fill(scene['narration'],88),'']
    transcript.append('<p><strong>'+html.escape(title.replace('\n',' '))+'</strong> '+html.escape(scene['narration'])+'</p>')
    for key,value in [('eye',eyebrow.upper()),('title',title),('body',body)]: (temp/f'{i}-{key}.txt').write_text(value)
    video=temp/f'{i:02d}.mp4';segments.append(video)
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','lavfi','-i',f'color=c=0x092729:s=1280x720:r=24:d={duration}','-loop','1','-i',str(temp/f'{fish}.svg')]
    if i in (1,2,3): cmd += ['-loop','1','-i',str(temp/f'evolution-{i-1}.svg')]
    elif shot: cmd += ['-loop','1','-i',str(root/shot)]
    filters=["[0:v]drawbox=x=790:y=0:w=490:h=720:c=0x103d38:t=fill[bg]", "[1:v]scale=360:360,format=rgba[fish]"]
    if i in (1,2,3):
        filters += ["[2:v]scale=270:522,format=rgba,fade=t=in:st=3:d=1:alpha=1[phone]", "[bg][phone]overlay=x=910:y=85[habitat]", "[fish]scale=w='360-160*min(t/4,1)':h='360-160*min(t/4,1)':eval=frame,fade=t=out:st=3.4:d=1:alpha=1[adapting]", "[habitat][adapting]overlay=x='1280-380*min(t/3,1)':y='190+40*sin(t*2)'[scene]"]
    elif shot:
        filters += ["[2:v]scale=250:556,format=rgba[phone]", "[bg][phone]overlay=x=900:y='70+8*sin(t*.6)'[art]", "[art][fish]overlay=x=740:y='365+10*sin(t)'[scene]"]
    else: filters += ["[bg][fish]overlay=x='835+15*sin(t*.7)':y='170+15*sin(t)'[scene]"]
    chain=f"[scene]drawtext=fontfile={font}:textfile={temp}/{i}-eye.txt:x=70:y=95:fontsize=18:fontcolor=0xa0edc9,drawtext=fontfile={bold}:textfile={temp}/{i}-title.txt:x=65:y=210:fontsize={48 if len(title.split(chr(10))[0])>24 else 57}:fontcolor=0xf1fff7:line_spacing=12,drawtext=fontfile={font}:textfile={temp}/{i}-body.txt:x=70:y=410:fontsize=23:fontcolor=0xd2e7dc:line_spacing=14,drawtext=fontfile={font}:text='SHOAL  /  {i+1:02d}':x=70:y=650:fontsize=15:fontcolor=0x8ccbb7,fade=t=in:d=0.25,fade=t=out:st={duration-.25}:d=0.25,format=yuv420p[out]"
    filters.append(chain)
    cmd += ['-filter_complex',';'.join(filters),'-map','[out]','-t',str(duration),'-an','-c:v','libx264','-preset','veryfast','-crf','23','-threads','2',str(video)]
    subprocess.run(cmd,check=True)
    print(f'Scene {i+1}/14 rendered',flush=True)
(assets/'trailer-en.vtt').write_text('\n'.join(vtt))
text=re.sub(r'<div id="trailer-transcript">.*?</div>', '<div id="trailer-transcript">'+''.join(transcript)+'</div>', text, count=1, flags=re.S)
(root/'index.html').write_text(text)
(temp/'concat.txt').write_text(''.join("file '"+str(v)+"'\n" for v in segments))
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(temp/'concat.txt'),'-c','copy','-movflags','+faststart',str(temp/'silent.mp4')],check=True)
# A deterministic, original sound bed: gentle water, bubbles and soft transition swishes.
import numpy as np,wave
rate=22050;size=round(total_duration*rate);rng=np.random.default_rng(20261029);t=np.arange(size)/rate
water=np.convolve(rng.normal(0,1,size),np.ones(45)/45,mode='same')*.018*(.65+.35*np.sin(t*.55))
sfx=water
for scene in scenes:
    start=round(scene['start']*rate);length=min(round(.8*rate),size-start);u=np.arange(length)/rate
    whoosh=rng.normal(0,1,length)*np.sin(np.pi*np.minimum(u/.8,1))**2*.012
    bubble=np.sin(2*np.pi*(650*u+300*u*u))*np.exp(-u*7)*.022
    sfx[start:start+length]+=whoosh+bubble
sfx*=np.minimum(t/1,1)*np.minimum((total_duration-t)/1,1)
with wave.open(str(temp/'water.wav'),'wb') as output:
    output.setnchannels(1);output.setsampwidth(2);output.setframerate(rate);output.writeframes((np.clip(sfx,-.95,.95)*32767).astype('<i2').tobytes())
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(temp/'silent.mp4'),'-i',str(root/'media/trailer-narration.flac'),'-i',str(temp/'water.wav'),'-filter_complex','[1:a][2:a]amix=inputs=2:duration=longest:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[a]','-map','0:v:0','-map','[a]','-c:v','copy','-c:a','aac','-b:a','128k','-t',str(total_duration),'-movflags','+faststart',str(assets/'shoal-trailer.mp4')],check=True)
# Keep page duration, captions and transcript in step with the actual voiceover.
text=re.sub(r'Animated film · .*? · Silent, with on-screen text',f'Animated film · {duration_label} · British English voiceover, sound effects and captions',text)
text=text.replace('srclang="en" label="English"','srclang="en-GB" label="English (UK)"')
(root/'index.html').write_text(text)
print(f'Trailer complete: {total_duration} seconds, British English narration and original sound effects',flush=True)
