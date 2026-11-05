#!/usr/bin/env python3
"""Original clam pencil-test plates. Python 3 stdlib; no SVG strokes or transforms.

The six keys below are drawing coordinates, not deformations of a master fan.
Each ink mark is an authored cubic, expanded into a pressure-shaped filled ribbon.
Retraces perturb its four controls and pressure independently, before expansion.
Run from any directory to reproduce the committed sprite and exposure sheet.
"""
from pathlib import Path
import json
import math
import random
import re

OUT = Path(__file__).resolve().parents[1] / 'assets' / 'art'
VIEW = '0 0 120 110'

def points(s):
    n = [float(v) for v in s.split()]
    return list(zip(n[::2], n[1::2]))

def fmt(n):
    return f'{n:.1f}'

def coords(ps):
    return ' '.join(f'{fmt(x)} {fmt(y)}' for x, y in ps)

def blob(d, colour='wash', opacity=None):
    d = re.sub(r'-?\d+(?:\.\d+)?', lambda m: fmt(float(m[0])), d)
    return f'<path fill="var(--clam-{colour})"' + (f' opacity="{opacity}"' if opacity else '') + f' d="{d}"/>'

def pen(s, width=1.4, rng=None, colour='ink'):
    """Cubic ribbon: pointed ends, unequal shoulders, independently varied pressure.
    Offset control handles keep the two sides truly curved, without SVG strokes.
    """
    p = points(s) if isinstance(s, str) else s
    if rng:
        p = [(x + rng.uniform(-.55, .55), y + rng.uniform(-.55, .55)) for x, y in p]
        width *= rng.uniform(.8, 1.2)
    normals = []
    for i in range(4):
        a, b = p[max(0, i-1)], p[min(3, i+1)]
        dx, dy = b[0]-a[0], b[1]-a[1]
        length = math.hypot(dx, dy) or 1
        pressure = [0, .72, 1.12, .025][i]
        normals.append((-dy/length*width*pressure, dx/length*width*pressure))
    left = [(x+nx, y+ny) for (x,y),(nx,ny) in zip(p,normals)]
    right = [(x-nx, y-ny) for (x,y),(nx,ny) in zip(p,normals)]
    return blob(f'M{coords(left[:1])} C{coords(left[1:])} L{coords(right[3:])} C{coords(right[2::-1])} Z', colour)

# Outer wash and the ink fragments are deliberately separately drawn.
# Ribs finish at different points around the rear-left hinge, not one radial pole.
KEYS = {
 'shut': dict(
 wash='M13 78 C11 73 18 70 23 71 C25 65 33 66 38 67 C47 61 55 65 59 67 C68 63 76 65 80 69 C89 68 97 72 102 76 C112 78 110 83 103 87 C79 96 37 96 17 87 Q10 84 13 78Z',
 edge=['12 80 11 74 18 70 24 71','25 70 27 64 34 65 40 67','40 67 48 62 54 64 60 67','61 67 70 63 77 66 81 69','82 69 93 69 100 73 105 78','108 79 114 88 85 91 68 91','65 92 43 94 18 88 11 81'],
 ribs=['24 73 27 78 32 82 42 85','40 69 40 74 43 80 48 85','59 69 57 76 56 80 55 85','79 71 75 77 68 83 63 86','99 77 89 81 78 85 70 87'],
 growth=['21 80 43 88 77 89 100 82','29 75 49 82 76 82 88 78'],
 mouth='M16 83 C43 88 82 90 107 81 Q101 96 58 95 Q29 94 16 83Z',
 front='M13 84 C39 93 80 94 109 82 C105 92 91 100 70 101 C44 103 23 98 13 84Z',
 lip=['12 83 38 92 75 94 109 82','109 84 100 98 81 101 65 100','62 101 40 103 20 96 13 85'],
 fribs=['26 90 30 94 36 96 40 97','46 93 47 96 49 98 52 99','72 94 71 97 69 99 68 100','94 90 91 95 87 97 83 98'], pearl=[62,82,45], window=[79,89], visible=False),
 'barely': dict(
 wash='M13 71 C12 64 18 60 24 62 C26 54 34 55 39 57 C44 48 53 50 60 55 C67 49 76 53 80 59 C89 55 96 62 98 66 C107 66 110 74 105 79 C88 89 38 90 18 81Z',
 edge=['13 74 11 65 18 60 24 61','25 61 26 53 34 54 40 56','40 56 45 48 54 49 61 54','62 55 68 49 77 53 81 59','82 59 92 55 97 61 99 66','100 66 109 66 112 75 106 79','104 80 81 90 41 89 15 78'],
 ribs=['25 63 26 70 32 78 40 81','40 58 39 66 43 75 47 82','60 57 57 66 56 75 54 82','79 61 75 70 66 78 62 83','99 69 91 77 78 82 69 84'],
 growth=['22 72 43 82 78 84 102 75','29 65 47 74 79 76 91 69'],
 mouth='M14 77 C43 83 85 84 108 75 Q113 91 69 97 Q29 95 14 77Z',
 front='M12 83 C37 91 79 92 110 80 C106 91 90 100 69 101 C44 102 22 96 12 83Z',
 lip=['12 82 38 91 77 91 109 80','109 82 103 94 84 100 67 100','64 101 40 102 20 94 12 83'],
 fribs=['24 88 29 93 33 94 40 97','46 92 47 95 48 97 51 99','74 92 72 96 71 98 68 100','96 88 94 93 88 97 83 98'], pearl=[62,99,45], window=[0,88], visible=True),
 'half': dict(
 wash='M12 65 C10 57 17 49 23 51 C21 41 31 39 37 41 C40 31 49 31 57 37 C63 28 74 33 78 41 C88 37 96 45 95 51 C105 52 110 61 105 69 C83 84 41 87 17 76Z',
 edge=['12 68 9 57 16 49 23 50','23 50 21 41 30 38 37 40','38 40 39 31 49 30 57 36','58 36 64 28 74 32 79 40','79 41 89 36 97 45 96 51','96 52 107 52 112 61 106 69','104 71 81 86 37 86 14 73'],
 ribs=['24 53 25 62 30 71 39 77','38 43 37 55 41 68 46 78','58 39 54 51 54 67 53 78','78 43 73 55 65 71 60 79','97 55 87 66 77 77 67 81'],
 growth=['20 64 39 77 76 81 102 66','28 56 48 65 78 69 90 59'],
 mouth='M14 70 C41 79 84 77 108 66 C114 81 96 94 69 97 C38 99 20 87 14 70Z',
 front='M12 81 C34 90 78 93 110 77 C108 89 94 99 73 101 C45 104 23 96 12 81Z',
 lip=['11 80 36 90 79 91 110 77','110 79 105 92 89 100 71 101','67 102 39 103 19 93 12 81'],
 fribs=['25 88 29 92 34 95 40 97','46 92 46 95 49 99 51 100','75 92 74 96 71 99 68 101','98 86 94 93 90 96 84 98'], pearl=[62,82,45], window=[0,89], visible=True),
 'rest': dict(
 wash='M13 61 C8 51 14 43 21 44 C17 32 26 27 34 30 C34 17 45 16 54 24 C58 12 71 17 76 28 C85 23 97 32 95 41 C107 42 112 53 107 64 C87 80 40 86 17 73Z',
 edge=['13 64 8 53 13 43 21 43','21 42 17 31 26 26 34 29','35 29 33 17 44 15 54 23','55 23 59 12 71 16 77 28','77 29 87 23 98 32 96 41','97 41 108 41 114 53 108 64','106 66 84 82 39 84 14 70'],
 ribs=['22 46 23 58 29 68 38 75','35 32 35 48 39 65 45 76','55 27 51 42 52 61 52 76','76 31 70 47 64 66 60 77','97 45 88 59 78 72 68 78'],
 growth=['19 59 37 73 74 78 104 61','27 48 47 59 80 65 92 51','42 37 54 45 66 48 75 47'],
 mouth='M14 68 C43 76 88 72 109 61 C117 79 99 95 70 98 C38 100 19 87 14 68Z',
 front='M12 80 C36 91 79 91 111 75 C110 87 97 99 75 101 C47 105 23 97 12 80Z',
 lip=['11 79 35 90 78 91 111 75','111 77 108 90 91 100 73 101','69 102 41 105 20 94 12 81'],
 fribs=['25 87 30 93 34 94 40 98','46 92 47 96 49 98 52 101','76 91 75 96 72 99 69 101','99 84 97 91 90 96 85 98'], pearl=[62,65,46], window=[38,89], visible=True),
 'wide': dict(
 wash='M14 57 C8 46 12 35 20 36 C15 24 24 17 32 21 C30 8 43 5 52 14 C56 1 69 5 75 19 C86 13 98 23 95 32 C110 32 115 46 109 59 C87 77 39 83 17 69Z',
 edge=['14 60 7 47 11 35 20 35','20 34 14 23 23 17 32 20','32 20 30 8 43 4 52 13','53 13 57 1 69 5 76 18','77 19 87 13 99 22 96 32','97 33 111 32 117 46 110 59','108 61 83 80 39 80 14 66'],
 ribs=['21 39 21 53 28 65 37 72','33 23 33 40 38 61 44 73','54 17 49 35 51 58 51 73','75 22 70 41 63 61 59 74','98 36 89 54 78 68 67 75'],
 growth=['18 54 37 69 76 74 106 55','26 39 45 54 79 59 93 42','39 27 53 35 67 40 78 37'],
 mouth='M13 64 C45 71 88 67 111 56 C119 75 102 95 72 99 C37 101 18 84 13 64Z',
 front='M11 78 C35 90 81 89 112 72 C114 87 98 100 76 102 C47 107 22 95 11 78Z',
 lip=['10 77 34 89 80 89 112 72','112 74 114 90 93 101 75 102','71 103 41 106 19 93 11 79'],
 fribs=['24 85 29 90 34 94 40 98','46 91 46 96 50 100 53 102','77 90 77 95 73 100 70 102','101 81 99 89 92 95 86 98'], pearl=[62,59,47], window=[30,89], visible=True),
 'settle': dict(
 wash='M12 63 C9 53 16 45 22 47 C19 35 28 31 36 34 C37 22 48 21 56 28 C62 18 73 23 78 33 C89 28 98 37 97 45 C108 47 112 57 106 66 C84 83 40 85 16 75Z',
 edge=['12 66 9 55 15 45 22 46','22 45 19 35 28 30 36 33','37 33 36 22 48 20 56 27','57 27 63 18 73 22 79 33','80 33 90 28 99 37 98 45','98 46 110 46 114 57 107 66','105 68 84 83 38 85 13 72'],
 ribs=['23 49 24 60 30 70 39 76','37 36 36 51 40 66 46 77','57 31 53 46 53 63 53 77','78 36 73 51 65 68 61 78','99 49 89 62 79 74 69 80'],
 growth=['19 62 38 75 76 79 103 64','28 52 47 62 79 67 92 55'],
 mouth='M13 70 C44 77 87 74 109 63 C116 80 98 94 70 98 C37 100 18 87 13 70Z',
 front='M12 82 C36 92 79 92 110 77 C109 90 94 100 73 102 C46 104 22 97 12 82Z',
 lip=['11 81 36 91 78 92 110 77','110 79 107 93 88 101 72 102','68 103 40 104 20 95 12 83'],
 fribs=['25 89 30 94 35 96 41 99','47 93 48 97 50 99 53 102','75 93 74 97 71 100 68 102','98 86 96 93 89 97 84 99'], pearl=[62,67,46], window=[40,90], visible=True),
}

def draw(key, variant, seed):
    k = KEYS[key]
    rng = random.Random(seed)
    # A wash retrace has its own controls; it never shares an ink boundary.
    wash = k['wash']
    if variant:
        wash = re.sub(r'-?\d+(?:\.\d+)?', lambda m: fmt(float(m[0])+rng.uniform(-.5,.5)), wash)
    back = blob('M17 95 C30 89 88 90 111 96 C104 104 40 108 17 99Z', 'shade', '.45')
    back += blob(k['mouth'], 'inside') + blob(wash)
    # Uneven brush fragments leave air between scallops and overshoot the corners.
    for s in k['edge']:
        back += pen(s, 1.65, rng)
    for i,s in enumerate(k['ribs']):
        back += pen(s, 1.0 if i%2 else 1.3, rng)
        p = points(s)
        # Short parallel hatch, authored as a fragment of this particular wandering rib.
        back += pen([(p[2][0]+2.2,p[2][1]-5), (p[2][0]+1,p[2][1]-2),
                     (p[3][0]+2,p[3][1]-2), (p[3][0]+3,p[3][1])], .65, rng, 'shade')
    for s in k['growth']:
        back += pen(s, .48, rng, 'shade')
    # A tiny off-centre barnacle, with a broken rim and an inky little cleft.
    p = points(k['ribs'][0])[1]
    x,y = p[0]+3,p[1]-1
    back += blob(f'M{x-2} {y+2} q-2 -4 1 -5 q4 -2 5 2 q0 4 -6 3Z', 'shade')
    back += pen([(x-2,y+1),(x-3,y-4),(x+3,y-5),(x+4,y)], .7, rng)
    back += pen([(x,y+1),(x-.8,y-1),(x+1,y-2),(x+2,y-2)], .65, rng)
    front = blob(k['front'])
    # Low tide wash pooling under the lip; distinct from its outline.
    front += blob('M24 92 C42 99 82 103 102 87 Q92 103 68 102 Q37 102 24 92Z', 'shade', '.5')
    for s in k['lip']:
        front += pen(s, 1.8, rng)
    for s in k['fribs']:
        front += pen(s, .95, rng)
    front += pen('20 86 43 96 78 97 103 83', .6, rng, 'shade')
    front += pen('32 94 52 101 74 100 90 93', .45, rng, 'shade')
    # Two quick lip shadows, and a small chipped edge on the right.
    front += pen('28 88 37 93 42 93 46 94', .9, rng)
    front += pen('79 90 85 89 91 87 96 85', 1, rng)
    front += pen('103 88 101 90 104 92 100 93', .85, rng)
    return back, front

def symbol(id_, body):
    return f'<symbol id="{id_}" viewBox="{VIEW}">{body}</symbol>'

def main():
    symbols, frames, poses = [], {}, {}
    # Twelve plates per layer, with more retraces on the long-held exposures.
    counts = {'shut':2, 'barely':1, 'half':2, 'rest':3, 'wide':2, 'settle':2}
    for pose,count in counts.items():
        poses[pose] = []
        for v in range(count):
            name = f'{pose}-{v}'
            back,front = draw(pose,v,110+list(KEYS).index(pose)*17+v)
            ids = [f'clam-{name}-back', f'clam-{name}-front']
            symbols.extend([symbol(ids[0],back),symbol(ids[1],front)])
            frames[name] = dict(back=ids[0],front=ids[1],pearl=KEYS[pose]['pearl'],
                                window=KEYS[pose]['window'],visible=KEYS[pose]['visible'])
            poses[pose].append(name)
    # The pearl rim is drawn at the same viewBox as the shell plates.
    for v in range(2):
        rng = random.Random(900+v)
        ring = ''.join(pen(s,1.6,rng) for s in [
            '7 53 3 27 28 3 57 4','58 4 89 1 115 25 113 52',
            '113 54 117 84 91 107 62 105','59 106 26 109 4 84 7 56'])
        ring += blob('M27 31 C29 20 40 17 45 20 Q40 25 36 30 Q29 36 27 31Z', 'wash', '.85')
        ring += pen('21 47 20 38 22 34 24 31', .8, rng, 'wash')
        symbols.append(symbol(f'clam-ring-{v}',ring))
    # Three separate bubble drawings; the air pocket climbs in stepped exposures.
    bubbles = [
        ['85 46 80 40 84 32 90 33','91 33 99 35 98 44 93 47','92 47 88 49 85 47 85 46'],
        ['87 31 80 24 85 15 92 17','94 17 102 20 100 29 95 32','94 32 91 34 88 32 87 31'],
        ['88 15 82 10 88 2 94 4','96 4 102 8 100 14 95 16','94 16 91 17 89 16 88 15']]
    for v,strokes in enumerate(bubbles):
        body = ''.join(pen(s,.8,random.Random(950+v+i),'wash') for i,s in enumerate(strokes))
        symbols.append(symbol(f'clam-bubble-{v}',body))
    # Pencil-drawn sand curls disperse sideways, rather than scaling a cloud.
    puffs = [
        ['15 94 7 88 12 81 20 87','99 94 110 85 117 91 111 96','25 99 31 94 37 95 40 98'],
        ['10 90 1 81 7 74 15 80','104 89 112 77 120 83 116 88','20 101 25 94 31 94 35 96','91 101 96 94 103 95 106 98'],
        ['3 79 0 76 4 72 8 74','111 77 114 71 118 73 120 76','12 98 16 92 21 93 23 95','101 99 105 92 110 94 113 95']]
    for v,strokes in enumerate(puffs):
        symbols.append(symbol(f'clam-sand-{v}', ''.join(pen(s,1.15,random.Random(980+v+i),'shade') for i,s in enumerate(strokes))))
    # All output, including handwritten wash paths, is rounded to one decimal.
    svg = '<svg xmlns="http://www.w3.org/2000/svg"><!-- Original Shoal clam exposure plates; generated by scripts/draw-clams.py. -->' + ''.join(symbols) + '</svg>\n'
    OUT.mkdir(exist_ok=True)
    (OUT/'clams.svg').write_text(svg)
    (OUT/'clams.json').write_text(json.dumps(dict(viewBox=VIEW,poses=poses,frames=frames,
        rings=['clam-ring-0','clam-ring-1'], bubbles=[f'clam-bubble-{i}' for i in range(3)],
        sand=[f'clam-sand-{i}' for i in range(3)]),indent=2)+'\n')
    print(f'{len(frames)} drawings per layer; {len(symbols)} symbols; {len(svg.encode())} bytes')

if __name__ == '__main__':
    main()
