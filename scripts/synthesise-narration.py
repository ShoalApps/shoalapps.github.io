"""Generate the trailer's synthetic British English narration locally with Piper."""
import argparse,json,tempfile,wave,subprocess
from pathlib import Path
from piper import PiperVoice,SynthesisConfig
parser=argparse.ArgumentParser();parser.add_argument('--model',required=True);args=parser.parse_args()
root=Path(__file__).resolve().parents[1];temp=Path(tempfile.mkdtemp(prefix='shoal-narration-'))
scenes=json.loads((root/'media/trailer-scenes.json').read_text());voice=PiperVoice.load(args.model)
segments=[];position=0.0
for i,scene in enumerate(scenes):
    path=temp/f'{i:02}.wav'
    with wave.open(str(path),'wb') as output:voice.synthesize_wav(scene['narration'],output,SynthesisConfig(length_scale=1.0,noise_scale=.5,noise_w_scale=.6))
    with wave.open(str(path),'rb') as audio:duration=audio.getnframes()/audio.getframerate()
    scene['duration']=max(7.0,round((duration+1.4)*4)/4);scene['start']=position;position+=scene['duration']
    padded=temp/f'padded-{i:02}.wav'
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(path),'-af','adelay=650,apad','-t',str(scene['duration']),'-ar','22050','-ac','1',str(padded)],check=True)
    segments.append(padded);print(f'Narrated scene {i+1}: {scene["duration"]} seconds',flush=True)
(root/'media/trailer-scenes.json').write_text(json.dumps(scenes,ensure_ascii=False,indent=2)+'\n')
concat=temp/'list.txt';concat.write_text(''.join(f"file '{p}'\n" for p in segments))
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(concat),'-c:a','flac',str(root/'media/trailer-narration.flac')],check=True)
print(f'British English narration ready: {position:.2f} seconds',flush=True)
