#!/usr/bin/env python3
"""Perspective bivalve plates. Python 3 standard library only.

X is the straight, immovable hinge; +Y is the front, +Z is up. The
commissure is Z=0. Both valves use the SAME scalloped margin. The upper
valve is one rigid body, rotated around X, never a rescaled drawing.
A thick shell has an outward ribbed face, a smooth inward offset and a
connecting rim. Visibility and shadow tests use this geometry. The finish
samples smooth lighting fields on a separate fine grid, traces their level
regions and fits cubic wash and ink contours without emitting mesh edges. --check-sheets writes temporary
colour-resolved SVGs/PNGs for rsvg-convert; it is not needed for generation.
"""
from pathlib import Path
from collections import defaultdict
import argparse
import json
import math
import random
import subprocess
from functools import lru_cache

OUT = Path(__file__).resolve().parents[1] / 'assets/art'
VIEW = '0 0 120 110'
POSES = dict(shut=(0, 2), barely=(10, 1), half=(28, 2),
             rest=(56, 3), wide=(70, 2), settle=(48, 2))
NS, NP = 14, 60
BANDS = [.18, .29, .43, .58, .74, .88]
THICK = .075

def add(a,b): return tuple(x+y for x,y in zip(a,b))
def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def mul(a,s): return tuple(x*s for x in a)
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def unit(a): return mul(a,1/(math.sqrt(dot(a,a)) or 1))
def mean(ps): return mul(tuple(map(sum,zip(*ps))),1/len(ps))
def rotate(p,t):
    c,s=math.cos(math.radians(t)),math.sin(math.radians(t))
    return p[0], p[1]*c-p[2]*s, p[1]*s+p[2]*c

# Close camera gives visibly larger near scallops. All poses share this camera.
ELEV, YAW, DIST, FOCAL = 31, 20, 6.3, 184
TARGET = (0,.72,.12)
E = math.radians(ELEV); A = math.radians(YAW)
TOWARD = (math.sin(A)*math.cos(E),math.cos(A)*math.cos(E),math.sin(E))
CAM = add(TARGET,mul(TOWARD,DIST))
RIGHT = (math.cos(A),-math.sin(A),0)
UP = cross(RIGHT,TOWARD)
LIGHT = unit((-.7,.45,1.5))

def project(p):
    q=sub(p,CAM); depth=-dot(q,TOWARD)
    return (60+FOCAL*dot(q,RIGHT)/depth, 66-FOCAL*dot(q,UP)/depth, depth)

def exterior(s,phi,sign,smooth=False):
    # Ovate fan, wider than long; posterior ends lie ON the hinge axis.
    # The small left/right difference is an outline asymmetry, not a pose warp.
    scallop=1+.018*math.cos(30*phi)
    x=-.12*(1-s)+s*1.9*math.cos(phi)*(.32+.82*math.sin(phi))**.45*scallop*(1+.045*math.cos(phi))
    y=1.64*s*math.sin(phi)**.82*scallop
    profile=(s**.72*(1-s)**1.3)/(.356**.72*(1-.356)**1.3) if 0<s<1 else 0
    dome=.72*profile*math.sin(phi)**.65
    ribs=.042*s**.8*math.sin(math.pi*s)*math.cos(30*phi)*math.sin(phi)
    # Irregular stepped growth on the exterior only; zero at the commissure.
    growth=sum(.009 for b in BANDS if s>b)*math.sin(math.pi*s)*math.sin(phi)
    return (x,y,sign*(dome+(0 if smooth else ribs+growth)))

def point(s,phi,sign,inside=False):
    p=exterior(s,phi,sign)
    if not inside: return p
    p=exterior(s,phi,sign,True)
    # Offset the smoothed envelope inward; exterior ribs add local thickness. Thickness tapers
    # at the umbo and hinge ends so the two beaks almost meet the ligament.
    h=.0001
    ds=sub(exterior(min(1,s+h),phi,sign,True),exterior(max(0,s-h),phi,sign,True))
    dp=sub(exterior(s,min(math.pi,phi+h),sign,True),exterior(s,max(0,phi-h),sign,True))
    n=unit(cross(ds,dp))
    if n[2]*sign<0: n=mul(n,-1)
    thickness=THICK*min(1,s*8)*math.sin(phi)**.35
    p= sub(p,mul(n,thickness))
    return p

# Sphere rests against the lowest inner point. Its location never depends on theta.
DEEP=min((point(i/300,math.pi/2,-1,True) for i in range(1,300)),key=lambda p:p[2])
RADIUS=.55
# Lift only enough to satisfy sphere/cup contact, once at modelling time.
# The sphere settles to minimum gravitational potential inside the cup, rather
# than balancing on a steep rear wall. This is a numeric sphere/surface contact
# solve; no artist-authored screen coordinate or pose-dependent lift is used.
INNER=[point(i/180,j*math.pi/100,-1,True) for i in range(1,180) for j in range(1,100)]
def support(y):
    candidates=[]
    for p in INNER:
        r2=(p[0]-DEEP[0])**2+(p[1]-y)**2
        if r2<RADIUS**2: candidates.append((p[2]+math.sqrt(RADIUS**2-r2),p))
    return max(candidates)
settled=[]
for i in range(81):
    y=.5+i*.008
    height,contact=support(y)
    settled.append((height,y,contact))
_HEIGHT,_Y,CONTACT=min(settled)
PEARL=(DEEP[0],_Y,_HEIGHT)
PC=project(PEARL)
# Exact apparent radius of a sphere measured perpendicular to its sight line.
DIAM=2*FOCAL*RADIUS/math.sqrt(PC[2]**2-RADIUS**2)


def mesh(theta, ns=NS, np=NP):
    cells=[]; vertices={}
    for sign in [-1,1]:
        for inside in [False,True]:
            label=(sign,inside)
            for i in range(ns+1):
                for j in range(np+1):
                    p=point(i/ns,j*math.pi/np,sign,inside)
                    vertices[(sign,inside,i,j)] = rotate(p,theta) if sign==1 else p
            for i in range(ns):
                for j in range(np):
                    ids=[(*label,i,j),(*label,i+1,j),(*label,i+1,j+1),(*label,i,j+1)]
                    ps=[vertices[k] for k in ids]
                    n=unit(cross(sub(ps[1],ps[0]),sub(ps[3],ps[0])))
                    # Parametric normal points up; reverse for lower exterior/upper interior.
                    if (sign==-1) != inside: n=mul(n,-1)
                    cells.append(dict(ids=ids,ps=ps,n=n,c=mean(ps),sign=sign,inside=inside,s=(i+.5)/NS,phi=(j+.5)*math.pi/np,rim=False))
        for j in range(np):
            ids=[(sign,False,ns,j),(sign,False,ns,j+1),(sign,True,ns,j+1),(sign,True,ns,j)]
            ps=[vertices[k] for k in ids]
            n=unit(cross(sub(ps[1],ps[0]),sub(ps[3],ps[0])))
            if sign==1: n=mul(n,-1)
            cells.append(dict(ids=ids,ps=ps,n=n,c=mean(ps),sign=sign,inside=False,s=1,phi=(j+.5)*math.pi/np,rim=True))
    return vertices,cells


def bary(p,a,b,c):
    v0=(b[0]-a[0],b[1]-a[1]); v1=(c[0]-a[0],c[1]-a[1]); v2=(p[0]-a[0],p[1]-a[1])
    d=v0[0]*v1[1]-v1[0]*v0[1]
    if abs(d)<1e-9: return None
    u=(v2[0]*v1[1]-v1[0]*v2[1])/d; v=(v0[0]*v2[1]-v2[0]*v0[1])/d
    return (1-u-v,u,v) if u>=-1e-6 and v>=-1e-6 and u+v<=1.000001 else None

class Screen:
    """Spatially indexed perspective triangles; depth is reciprocal interpolated."""
    def __init__(self,cells,projection=project):
        self.bins=defaultdict(list)
        for idx,c in enumerate(cells):
            q=[projection(p) for p in c['ps']]
            for ks in [(0,1,2),(0,2,3)]:
                tri=[q[k] for k in ks]
                for x in range(math.floor(min(p[0] for p in tri)/8),math.floor(max(p[0] for p in tri)/8)+1):
                    for y in range(math.floor(min(p[1] for p in tri)/8),math.floor(max(p[1] for p in tri)/8)+1):
                        self.bins[x,y].append((idx,tri))
    def hit(self,p):
        best=1e9; who=-1
        for idx,t in self.bins.get((math.floor(p[0]/8),math.floor(p[1]/8)),[]):
            b=bary(p,*t)
            if b:
                d=1/sum(w/q[2] for w,q in zip(b,t))
                if d<best: best,who=d,idx
        return best,who

# Orthogonal light-space triangle tests for shadows (not a painted dark patch).
LR=unit(cross(LIGHT,(0,0,1))); LU=cross(LIGHT,LR)
def light_project(p): return (dot(p,LR)*30,dot(p,LU)*30,10-dot(p,LIGHT))

def simplify(ps,tol=.25):
    if len(ps)<4: return ps
    a,b=ps[0],ps[-1]
    dx,dy=b[0]-a[0],b[1]-a[1]; length=math.hypot(dx,dy)
    distances=[abs(dy*(p[0]-a[0])-dx*(p[1]-a[1]))/length if length else math.hypot(p[0]-a[0],p[1]-a[1]) for p in ps]
    k=max(range(len(ps)),key=lambda i:distances[i])
    if distances[k]<=tol: return [a,b]
    return simplify(ps[:k+1],tol)[:-1]+simplify(ps[k:],tol)

def fill(d,c,opacity=None):
    return f'<path fill="var(--clam-{c})"'+(f' opacity="{opacity}"' if opacity else '')+f' d="{d}"/>'

def brush(ps,width,rng,colour='ink',jitter=.1):
    """Filled tapered ribbon, never a mesh stroke. Endpoints stay attached."""
    if len(ps)<2: return ''
    ps=simplify(ps,.32)
    ps=[(p[0]+(rng.uniform(-jitter,jitter) if 0<i<len(ps)-1 else 0),p[1]+(rng.uniform(-jitter,jitter) if 0<i<len(ps)-1 else 0)) for i,p in enumerate(ps)]
    left=[]; right=[]
    width*=rng.uniform(.86,1.14)
    phase=rng.uniform(0,math.tau)
    for i,p in enumerate(ps):
        a,b=ps[max(i-1,0)],ps[min(i+1,len(ps)-1)]
        dx,dy=b[0]-a[0],b[1]-a[1]; l=math.hypot(dx,dy) or 1
        w=width*(.15+.85*max(0,math.sin(math.pi*i/(len(ps)-1)))**.5)*(.94+.06*math.sin(i/max(1,len(ps)-1)*math.tau*1.5+phase))/2
        left.append((p[0]-dy/l*w,p[1]+dx/l*w)); right.append((p[0]+dy/l*w,p[1]-dx/l*w))
    return fill(curve(left+right[::-1],0,.22),colour)

# Rendering resolution is independent of the anatomical/control mesh. Neither
# sample count changes the parametric surface, camera, pose or resting sphere.
SCALE = 3
RW, RH = 120*SCALE, 110*SCALE


def chaikin(ps, rounds=2):
    ps=[p[:2] for p in ps]
    if ps and ps[0]==ps[-1]: ps=ps[:-1]
    for _ in range(rounds):
        ps=[q for a,b in zip(ps,ps[1:]+ps[:1])
            for q in [(a[0]*.75+b[0]*.25,a[1]*.75+b[1]*.25),
                      (a[0]*.25+b[0]*.75,a[1]*.25+b[1]*.75)]]
    return ps


def curve(ps, smooth=0, tolerance=.22):
    """Closed, smooth cubic contour; no polygon corners survive in the SVG."""
    ps=chaikin(ps,smooth)
    if len(ps)<3: return ''
    ps=simplify(ps+[ps[0]],tolerance)[:-1]
    if len(ps)<3: return ''
    # Consecutive Catmull-Rom spans have reflected handles: SVG's smooth
    # relative command preserves the cubic while avoiding redundant controls.
    def num(v):
        v=round(v,1)
        return f'{v:.1f}'.rstrip('0').rstrip('.') if v else '0'
    def pair(p): return num(p[0])+','+num(p[1])
    rounded=lambda p:(round(p[0],1),round(p[1],1))
    d='M'+pair(ps[0])
    for i,b in enumerate(ps):
        a=ps[i-1]; c=ps[(i+1)%len(ps)]; e=ps[(i+2)%len(ps)]
        q=(b[0]+(c[0]-a[0])/7,b[1]+(c[1]-a[1])/7)
        r=(c[0]-(e[0]-b[0])/7,c[1]-(e[1]-b[1])/7)
        origin=rounded(b)
        relative=lambda p:sub(rounded(p),origin)
        if i==0: d+='c'+pair(relative(q))+' '+pair(relative(r))+' '+pair(relative(c))
        else: d+='s'+pair(relative(r))+' '+pair(relative(c))
    return d+'Z'


def field_contours(mask):
    """Trace subpixel field regions, smooth the lattice, then fit cubic curves.

    The pixel lattice is only an internal sampling device. Its edges are never
    emitted as wash edges, silhouette strokes, or rim divisions.
    """
    edges=defaultdict(list)
    for y in range(RH):
        off=y*RW
        for x in range(RW):
            k=off+x
            if not mask[k]: continue
            if y==0 or not mask[k-RW]: edges[(x,y)].append((x+1,y))
            if x==RW-1 or not mask[k+1]: edges[(x+1,y)].append((x+1,y+1))
            if y==RH-1 or not mask[k+RW]: edges[(x+1,y+1)].append((x,y+1))
            if x==0 or not mask[k-1]: edges[(x,y+1)].append((x,y))
    loops=[]
    while edges:
        start=next(iter(edges)); at=start; loop=[at]
        while at in edges:
            nxt=edges[at].pop()
            if not edges[at]: del edges[at]
            loop.append(nxt); at=nxt
            if at==start: break
        if len(loop)<5: continue
        area=abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(loop,loop[1:])))/2/SCALE**2
        if area<.3: continue
        loops.append([(x/SCALE,y/SCALE) for x,y in loop])
    return loops


def field_path(mask):
    return ''.join(curve(loop,2,.42) for loop in field_contours(mask))


def shading_normal(s,phi,sign,inside,theta):
    # The physical growth steps remain in the model. In the wash they are
    # represented by ink arcs, not discontinuities in a faceted normal field.
    def envelope(u,v):
        p=exterior(u,v,sign,True)
        if not inside:
            ridge=.042*u**.8*math.sin(math.pi*u)*math.cos(30*v)*math.sin(v)
            p=add(p,(0,0,sign*ridge))
        return p
    h=.0002
    ds=sub(envelope(min(1,s+h),phi),envelope(max(0,s-h),phi))
    dp=sub(envelope(s,min(math.pi,phi+h)),envelope(s,max(0,phi-h)))
    n=unit(cross(ds,dp))
    if (sign==-1)!=inside: n=mul(n,-1)
    return rotate(n,theta) if sign==1 else n


@lru_cache(maxsize=6)
def paint(theta):
    # A fine numeric tessellation samples the unchanged surface. Smooth normals
    # and continuous scalar washes are interpolated BEFORE tone quantisation.
    verts,cells=mesh(theta,48,240)
    oldverts,oldcells=mesh(theta)
    light=Screen([c for c in oldcells if c['sign']==1 and not c['inside']],light_project)
    def shadow(p):
        q=light_project(add(p,mul(LIGHT,.012)))
        return float(light.hit(q)[0]<q[2]-.025)
    projected={k:project(p) for k,p in verts.items()}
    values={}
    for k,p in verts.items():
        sign,inside,i,j=k; u=i/48; v=j*math.pi/240
        n=shading_normal(u,v,sign,inside,theta)
        lam=max(0,dot(n,LIGHT))
        # Fade corrugated lighting into the beak, rather than ending stripes
        # with rectangular highlight patches near the umbo.
        if not inside:
            smoothn=shading_normal(u,v,sign,True,theta)
            smoothlam=max(0,dot(mul(smoothn,-1),LIGHT))
            fade=min(1,max(0,(u-.13)/.45))
            lam=smoothlam*(1-fade)+lam*fade
        ao=(.22*(1-u)+.12*(1-p[1]/1.7)) if inside else 0
        values[k]=.2+.8*lam-ao-(.28*shadow(p) if inside else 0)
    z=[1e9]*(RW*RH); kinds=[None]*(RW*RH); field=[0.]*(RW*RH)
    for c in cells:
        if dot(c['n'],sub(CAM,c['c']))<=0: continue
        ids=c['ids']; q=[projected[k] for k in ids]
        for ks in [(0,1,2),(0,2,3)]:
            t=[q[k] for k in ks]
            xmin=max(0,math.floor(min(p[0] for p in t)*SCALE)); xmax=min(RW-1,math.ceil(max(p[0] for p in t)*SCALE))
            ymin=max(0,math.floor(min(p[1] for p in t)*SCALE)); ymax=min(RH-1,math.ceil(max(p[1] for p in t)*SCALE))
            for y in range(ymin,ymax+1):
                for x in range(xmin,xmax+1):
                    b=bary(((x+.5)/SCALE,(y+.5)/SCALE),*t)
                    if b is None: continue
                    inv=sum(w/p[2] for w,p in zip(b,t)); depth=1/inv; idx=y*RW+x
                    if depth>=z[idx]: continue
                    z[idx]=depth
                    kinds[idx]=(int(depth<PC[2]),c['sign'],2 if c['rim'] else int(c['inside']))
                    field[idx]=sum(w*values[ids[k]]/p[2] for w,p,k in zip(b,t,ks))/inv
    # A small surface-aware low pass removes sampling noise without smearing
    # a valve over its rim or mixing the upper and lower valves.
    for _ in range(3):
        blurred=field[:]
        for y in range(1,RH-1):
            for x in range(1,RW-1):
                k=y*RW+x
                if kinds[k] is None: continue
                ns=[i for i in (k-1,k+1,k-RW,k+RW) if kinds[i]==kinds[k]]
                blurred[k]=(field[k]*2+sum(field[i] for i in ns))/(2+len(ns))
        field=blurred
    # Nacre has broad washes, not the exterior's narrowly corrugated light.
    # Smooth its continuous field at a two-unit footprint before taking level
    # sets. This removes angular cast-shadow transitions without blurring ribs.
    for _ in range(2):
        for vertical in [False,True]:
            blurred=field[:]
            for y in range(RH):
                for x in range(RW):
                    k=y*RW+x; label=kinds[k]
                    if label is None or label[2]!=1: continue
                    total=0.; weight=0
                    for d in range(-7,8):
                        xx=x if vertical else x+d; yy=y+d if vertical else y
                        if not (0<=xx<RW and 0<=yy<RH): continue
                        i=yy*RW+xx; other=kinds[i]
                        if other is not None and other[1:]==label[1:]:
                            total+=field[i]; weight+=1
                    if weight: blurred[k]=total/weight
            field=blurred
    layers=['','']; outlines=[]
    groups=set(k for k in kinds if k is not None)
    for kind in sorted(groups,key=lambda kind:sum(z[i] for i,k in enumerate(kinds) if k==kind)/kinds.count(kind),reverse=True):
        layer,sign,inside=kind
        # BACK may include the same material behind its FRONT continuation.
        # The continuation is painted again over the avatar. This overlap
        # prevents fitted curves on opposite sides of the virtual pearl-depth
        # plane from leaving a hairline that could resemble a nacre crack.
        mask=[k==kind if layer else k is not None and k[1:]==kind[1:] for k in kinds]
        # A continuous pale rim, never individual mesh bricks. Only the long
        # contours on its two borders are inked below; no transverse edges.
        if inside==2:
            rimd=field_path(mask)
            layers[layer]+=fill(rimd,'edge')+f'<path fill="url(#clam-rim)" d="{rimd}"/>'
            continue
        prefix='nacre-' if inside else 'tone-'
        for tone,threshold in [(1,-100),(2,.27),(3,.54),(4,.81)]:
            d=field_path([m and v>=threshold for m,v in zip(mask,field)])
            if d: layers[layer]+=fill(d,prefix+str(tone)).replace('<path ','<path fill-rule="evenodd" ')
    # Per-valve silhouettes, including true occlusion edges, not the boundaries
    # of cell visibility or the virtual BACK/FRONT split through the pearl.
    for sign in [-1,1]:
        loops=field_contours([k is not None and k[1]==sign for k in kinds])
        for loop in loops:
            signed=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(loop,loop[1:]))
            if signed<=0: continue
            ps=chaikin(loop,2); ps=simplify(ps+[ps[0]],.19)
            runs=[]; run=[]; oldlayer=None
            for p in ps:
                x=min(RW-1,max(0,int(p[0]*SCALE))); y=min(RH-1,max(0,int(p[1]*SCALE)))
                candidates=[y*RW+x]+[yy*RW+xx for yy in range(max(0,y-2),min(RH,y+3)) for xx in range(max(0,x-2),min(RW,x+3))]
                near=next((i for i in candidates if kinds[i] is not None and kinds[i][1]==sign),None)
                if near is None: continue
                layer=kinds[near][0]
                if run and layer!=oldlayer: runs.append((oldlayer,run)); run=[]
                run.append(p); oldlayer=layer
            if run: runs.append((oldlayer,run))
            outlines.extend((layer,ps,True) for layer,ps in runs if len(ps)>2)
    # True scalloped margin borders, sampled densely enough to round each lobe.
    def visible(p,sign,inside=None):
        q=project(p); x=int(q[0]*SCALE); y=int(q[1]*SCALE)
        if not (0<=x<RW and 0<=y<RH): return None
        k=y*RW+x; label=kinds[k]
        if label is None or label[1]!=sign: return None
        if inside is not None and label[2]!=inside: return None
        return label[0] if q[2]<=z[k]+.045 else None
    details=[]
    def trace(sign,samples,inside,width,colour='ink',opacity=None):
        runs=[]; run=[]; oldlayer=None
        for u,v in samples:
            p=point(u,v,sign,inside); p=rotate(p,theta) if sign==1 else p
            layer=visible(p,sign,int(inside))
            if layer is not None:
                if run and layer!=oldlayer: runs.append((oldlayer,run)); run=[]
                run.append(project(p)); oldlayer=layer
            elif run: runs.append((oldlayer,run)); run=[]
        if run: runs.append((oldlayer,run))
        details.extend((layer,ps,width,colour,opacity) for layer,ps in runs if len(ps)>3)
    for sign in [-1,1]:
        for inside in [False,True]:
            # Rim classification is allowed at a margin sample; it is one
            # continuous border, not strokes across each sampled segment.
            run=[]; oldlayer=None
            for j in range(241):
                p=point(1,j*math.pi/240,sign,inside); p=rotate(p,theta) if sign==1 else p
                layer=visible(p,sign)
                if layer is not None:
                    if run and layer!=oldlayer:
                        if len(run)>3: outlines.append((oldlayer,run,False))
                        run=[]
                    run.append(project(p)); oldlayer=layer
                elif run:
                    if len(run)>3: outlines.append((oldlayer,run,False))
                    run=[]
            if len(run)>3: outlines.append((oldlayer,run,False))
        # Exterior details require the visible surface to be EXTERIOR. This
        # prevents the old rib tuft shining through the thin beak's interior.
        for j in [2,4,7,10,13]:
            phi=j*math.pi/15
            trace(sign,[(u/40,phi) for u in range(12,38)],False,.22,'ink','.35')
        for band in [.29,.58,.88]:
            for lo,hi in [(.16,.75),(.92,1.8),(2.02,2.9)]:
                trace(sign,[(band,lo+(hi-lo)*j/30) for j in range(31)],False,.17,'shade','.5')
        for j in range(2,6):
            trace(sign,[(u/40,j*math.pi/15+.035) for u in range(24,34)],False,.28,'ink','.6')
        # Deliberately no nacre veins: a smooth cup and quiet hinge shadow.
    # Small ligament, geometrically at the immovable hinge, never a rib fan.
    lig=[(-.42,0,0),(.24,0,0),(.18,.085,.025),(-.32,.085,.025)]
    q=project(mean(lig)); x=int(q[0]*SCALE); y=int(q[1]*SCALE)
    if 0<=x<RW and 0<=y<RH and q[2]<=z[y*RW+x]+.1:
        layers[int(q[2]<PC[2])]+=fill(curve([project(p) for p in lig]),'ink')
    # Light-projected ground silhouette, with a gently rounded envelope.
    ground=-.61; pts=[]
    for p in oldverts.values():
        t=max(0,(p[2]-ground)/LIGHT[2]); q=project(sub(p,mul(LIGHT,t)))
        pts.append(q[:2])
    pts=sorted(set(pts))
    def half(seq):
        out=[]
        for p in seq:
            while len(out)>1 and ((out[-1][0]-out[-2][0])*(p[1]-out[-2][1])-(out[-1][1]-out[-2][1])*(p[0]-out[-2][0]))<=0: out.pop()
            out.append(p)
        return out
    hull=half(pts)[:-1]+half(pts[::-1])[:-1]
    groundshadow=fill(curve(hull,2,.15),'shadow','.22').replace('<path ','<path filter="url(#clam-soft)" ')
    layers[0]=groundshadow+layers[0]
    # A soft contact pool on the lower cup; no pale sand strip in front.
    contact=[project((CONTACT[0]+.24*math.cos(i*math.tau/32),CONTACT[1]+.12*math.sin(i*math.tau/32),CONTACT[2]+.008)) for i in range(32)]
    layers[0]+=fill(curve(contact),'shadow','.35').replace('<path ','<path filter="url(#clam-soft)" ')
    # Sphere shadow sampled as a fine, continuous screen-space field, reduced
    # to one smooth contour and softly feathered inside the projected sphere.
    mask=[False]*(RW*RH)
    count=clear=0
    for y in range(max(0,int((PC[1]-DIAM/2)*SCALE)),min(RH,int((PC[1]+DIAM/2)*SCALE)+1)):
        for x in range(max(0,int((PC[0]-DIAM/2)*SCALE)),min(RW,int((PC[0]+DIAM/2)*SCALE)+1)):
            q=((x+.5)/SCALE,(y+.5)/SCALE)
            ray=unit(add(mul(TOWARD,-1),add(mul(RIGHT,(q[0]-60)/FOCAL),mul(UP,(66-q[1])/FOCAL))))
            oc=sub(CAM,PEARL); b=dot(oc,ray); disc=b*b-dot(oc,oc)+RADIUS**2
            if disc<0: continue
            p=add(CAM,mul(ray,-b-math.sqrt(disc))); depth=project(p)[2]; k=y*RW+x
            count+=1
            clear+=z[k]>=depth-.015 and (kinds[k] is None or kinds[k][0]==0)
            mask[k]=bool(shadow(p))
    contours=field_contours(mask)
    if contours:
        # Tiny detached islands from coarse light testing are not ink marks.
        loop=max(contours,key=len)
        d=curve(loop,3,.25)
        layers[1]=fill(d,'shadow','.12').replace('<path ','<path filter="url(#clam-soft)" clip-path="url(#clam-pearl-clip)" ')+layers[1]
    return layers,outlines,details,clear/count


def draw(theta,variant):
    base,outlines,details,vis=paint(theta)
    layers=base[:]; rng=random.Random(130+variant*97)
    for layer,ps,silhouette in outlines:
        if silhouette: layers[layer]+=brush(ps,1.25,random.Random(7),'edge',0)
        layers[layer]+=brush(ps,.73 if silhouette else .38,rng)
    for layer,ps,width,colour,opacity in details:
        ink=brush(ps,width,rng,colour)
        if opacity: ink=ink.replace('<path ',f'<path opacity="{opacity}" ')
        layers[layer]+=ink
    return layers,vis,None


def symbol(name,body): return f'<symbol id="{name}" viewBox="{VIEW}">{body}</symbol>'

def validate():
    for j in range(NP+1):
        phi=j*math.pi/NP
        assert math.dist(exterior(1,phi,1),exterior(1,phi,-1))<1e-9
    reference,_=mesh(0)
    for theta,_ in POSES.values():
        assert 0<=theta<=70
        posed,_=mesh(theta)
        for k,p in reference.items():
            q=posed[k]
            if k[0]==-1: assert math.dist(p,q)<1e-12, 'lower valve moved'
            else: assert abs(math.hypot(p[1],p[2])-math.hypot(q[1],q[2]))<1e-10
        for x in [-1.6,-.12,1.6]: assert rotate((x,0,0),theta)==(x,0.,0.)
    width=max(project(exterior(1,j*math.pi/NP,-1))[0] for j in range(NP+1))-min(project(exterior(1,j*math.pi/NP,-1))[0] for j in range(NP+1))
    assert DIAM/width>=.36, f'avatar is only {DIAM/width:.1%} of shell width'
    # Sphere touches the inner cup and cannot penetrate any sampled inner point.
    assert abs(math.dist(CONTACT,PEARL)-RADIUS)<1e-10
    for i in range(1,NS):
        for j in range(1,NP): assert math.dist(point(i/NS,j*math.pi/NP,-1,True),PEARL)>=RADIUS-.015


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--check-sheets',type=Path); args=parser.parse_args()
    validate(); symbols=[]; frames={}; poses={}; checks={}
    for pose,(theta,count) in POSES.items():
        poses[pose]=[]
        for v in range(count):
            name=f'{pose}-{v}'; layers,vis,shadow=draw(theta,v)
            checks[name]=vis
            if pose=='rest': assert vis>=.85, f'rest pearl visibility {vis:.1%}'
            ids=[f'clam-{name}-back',f'clam-{name}-front']
            symbols.extend(symbol(k,b) for k,b in zip(ids,layers))
            frames[name]=dict(back=ids[0],front=ids[1],pearl=[round(PC[0],1),round(PC[1],1),round(DIAM,1)],window=[0,110],visible=True)
            poses[pose].append(name)
    # Subtle sphere overlay remains over the avatar. Cast-shadow side is derived
    # by sampling the upper valve in light space, per pose, in the shell plates.
    ring='<ellipse cx="60" cy="55" rx="60" ry="55" fill="url(#clam-sphere)"/><ellipse cx="43" cy="28" rx="10" ry="6" fill="var(--clam-edge)" opacity=".55"/><path d="M27,88 Q60,105 90,84 Q66,98 27,88Z" fill="var(--clam-nacre)" opacity=".32"/>'
    for v in range(2): symbols.append(symbol(f'clam-ring-{v}',ring))
    for v in range(3):
        rng=random.Random(v)
        p=project((1,1.1,.35+v*.42)); x,y=p[:2]; r=2.2+v*.35
        ps=[(x+r*math.cos(i*math.tau/24),y+r*math.sin(i*math.tau/24)) for i in range(25)]
        symbols.append(symbol(f'clam-bubble-{v}',brush(ps,.65,rng,'edge')))
        ps=[(12-v*3,89-v*4),(15-v*3,85-v*5),(20-v*2,87-v*4)]
        symbols.append(symbol(f'clam-sand-{v}',brush(ps,1.1,rng,'shade')+brush([(99+v*2,90-v*4),(105+v*2,85-v*5),(109+v*2,89-v*4)],.9,rng,'shade')))
    defs='<defs><radialGradient id="clam-sphere" cx="35%" cy="28%" r="72%"><stop offset="0" stop-color="#ffffff" stop-opacity=".16"/><stop offset=".5" stop-color="#ffffff" stop-opacity="0"/><stop offset=".72" stop-color="#173734" stop-opacity=".08"/><stop offset="1" stop-color="#102b29" stop-opacity=".62"/></radialGradient></defs>'
    defs=defs[:-7]+'<linearGradient id="clam-rim"><stop stop-color="#102520" stop-opacity="0"/><stop offset=".5" stop-color="#102520" stop-opacity="0"/><stop offset="1" stop-color="#102520" stop-opacity=".22"/></linearGradient></defs>'
    defs=defs[:-7]+f'<filter id="clam-soft" x="-15%" y="-15%" width="130%" height="130%"><feGaussianBlur stdDeviation="0.5"/></filter><clipPath id="clam-pearl-clip"><circle cx="{PC[0]:.1f}" cy="{PC[1]:.1f}" r="{DIAM/2:.1f}"/></clipPath></defs>'
    import re
    from collections import Counter
    body=''.join(symbols)
    pattern=r'<path ([^>]*?)d="([^"]*)"([^>]*)/>'
    repeats=Counter(m[1] for m in re.findall(pattern,body))
    shared=[]; names={}
    for d,n in repeats.items():
        if n>1 and len(d)>120:
            ident=f'clam-p{len(shared)}'; names[d]=ident
            shared.append(f'<path id="{ident}" d="{d}"/>')
    def reference(m):
        before,d,after=m.groups()
        return f'<use {before}{after} href="#{names[d]}"/>' if d in names else m[0]
    body=re.sub(pattern,reference,body)
    defs=defs[:-7]+''.join(shared)+'</defs>'
    svg='<svg xmlns="http://www.w3.org/2000/svg">'+defs+body+'</svg>\n'
    assert len(svg.encode())<300_000, len(svg.encode())
    (OUT/'clams.svg').write_text(svg)
    (OUT/'clams.json').write_text(json.dumps(dict(viewBox=VIEW,poses=poses,frames=frames,rings=['clam-ring-0','clam-ring-1'],bubbles=[f'clam-bubble-{i}' for i in range(3)],sand=[f'clam-sand-{i}' for i in range(3)]),indent=2)+'\n')
    print(f'{len(svg.encode())} bytes; camera elevation {ELEV}, yaw {YAW}, distance {DIST}; pearl {PC}, diameter {DIAM:.1f}')
    print('visible pearl: '+', '.join(f'{k} {v:.1%}' for k,v in checks.items()))
    if args.check_sheets: sheets(args.check_sheets,svg,frames)


def sheets(dest,svg,frames):
    """Disposable review render: same BACK / avatar / FRONT composition as CSS."""
    dest.mkdir(parents=True,exist_ok=True)
    import re
    def mix(a,b,t):
        aa=[int(a[i:i+2],16) for i in (1,3,5)]; bb=[int(b[i:i+2],16) for i in (1,3,5)]
        return '#'+''.join(f'{round(x*t+y*(1-t)):02x}' for x,y in zip(aa,bb))
    for theme in ['light','dark']:
        foam='#e6faf5'; abyss='#112b29'
        secondary='#cae6de' if theme=='light' else '#354e49'
        primary_container='#9ff2e2' if theme=='light' else '#005047'
        sand=mix(abyss,secondary,.76)
        wash=mix(mix(primary_container,foam,.55),foam,.65)
        nacre='#e6e7cf' if theme=='light' else '#dce5ca'
        colours=dict(ink=mix(abyss,'#100f18',.86),wash=wash,shade=mix(wash,abyss,.58),edge='#e6eee0' if theme=='light' else '#ecf5de',nacre=nacre,sand=sand,shadow='#102520')
        colours.update({'tone-1':mix(wash,'#244b40',.35),'tone-2':mix(wash,'#476e59',.65),'tone-3':wash,'tone-4':mix(wash,'#fff0cb',.58)})
        colours.update({'nacre-1':mix(nacre,'#4f8a7a',.5),'nacre-2':mix(nacre,'#7fae9c',.75),'nacre-3':mix(nacre,'#a9c4b0',.9),'nacre-4':nacre})
        resolved=re.sub(r'var\(--clam-([\w-]+)\)',lambda m:colours[m[1]],svg)
        panels=[]
        for n,f in frames.items():
            x,y,d=f['pearl']; r=d/2
            face=f'<circle cx="{x}" cy="{y}" r="{r}" fill="#dbb58f"/><path d="M{x-r*.88},{y-r*.25} Q{x-r*.8},{y-r*1.4} {x+r*.75},{y-r*.6} L{x+r*.9},{y-r*.1} Q{x},{y-r*.65} {x-r*.88},{y-r*.25}" fill="#463b35"/><ellipse cx="{x-r*.3}" cy="{y-r*.05}" rx="1.4" ry="1.9" fill="#23332f"/><ellipse cx="{x+r*.3}" cy="{y-r*.05}" rx="1.4" ry="1.9" fill="#23332f"/><path d="M{x-r*.3},{y+r*.35} Q{x},{y+r*.65} {x+r*.3},{y+r*.35}" fill="none" stroke="#704e43" stroke-width="1"/>'
            body=f'<rect width="120" height="110" fill="{sand}"/><use href="#{f["back"]}"/>'+face+f'<svg x="{x-r}" y="{y-r}" width="{d}" height="{d}" preserveAspectRatio="none" viewBox="0 0 120 110"><use href="#clam-ring-0"/></svg>'+f'<use href="#{f["front"]}"/><text x="4" y="10" fill="#eef5e8" font-size="6">{n}</text>'
            document='<svg xmlns="http://www.w3.org/2000/svg" width="360" height="330" viewBox="0 0 120 110">'+resolved+body+'</svg>'
            src=dest/f'{theme}-{n}.svg'; png=src.with_suffix('.png'); src.write_text(document)
            subprocess.run(['rsvg-convert',str(src),'-o',str(png)],check=True); panels.append(str(png))
        subprocess.run(['montage',*panels,'-tile','4x3','-geometry','360x330+4+4',str(dest/f'{theme}.png')],check=True)
        small=[]
        for panel in panels:
            src=Path(panel).with_suffix('.svg'); target=src.with_name(src.stem+'-120.png')
            subprocess.run(['rsvg-convert','-w','120','-h','110',str(src),'-o',str(target)],check=True)
            small.append(str(target))
        subprocess.run(['montage',*small,'-tile','4x3','-geometry','120x110+4+4',str(dest/f'{theme}-120.png')],check=True)

if __name__=='__main__': main()
