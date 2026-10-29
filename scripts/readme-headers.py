#!/usr/bin/env python3
"""Discover Android apps and render self-contained README SVGs from their actual launcher icons.
No image host or per-README app list is needed. A .shoal-app.json file can override the name,
icon path and description; Android apps with the standard launcher files are discovered too.
"""
import argparse,json,os,re,urllib.request,urllib.error,xml.etree.ElementTree as ET
from pathlib import Path
from html import escape
A='{http://schemas.android.com/apk/res/android}'
ROOT=Path(__file__).resolve().parents[1]

def request(url):
    headers={'Accept':'application/vnd.github+json','User-Agent':'Shoal-README-headers'}
    if os.getenv('GH_TOKEN'):headers['Authorization']='Bearer '+os.environ['GH_TOKEN']
    with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=30) as r:return r.read()

def discover(org,local=None):
    if local: repos=[{'name':p.name,'default_branch':'main'} for p in local.iterdir() if (p/'app/build.gradle.kts').is_file()]
    else:
        repos=[];page=1
        while True:
            batch=json.loads(request(f'https://api.github.com/orgs/{org}/repos?per_page=100&page={page}'))
            repos.extend(r for r in batch if not r['archived'] and not r['fork'])
            if len(batch)<100:break
            page+=1
    apps=[]
    for repo in repos:
        slug=repo['name']
        def read(path):
            return (local/slug/path).read_bytes() if local else request(f'https://raw.githubusercontent.com/{org}/{slug}/{repo["default_branch"]}/{path}')
        try:
            gradle=read('app/build.gradle.kts').decode()
        except (FileNotFoundError,urllib.error.HTTPError):continue
        try:meta=json.loads(read('.shoal-app.json'))
        except (FileNotFoundError,urllib.error.HTTPError):meta={}
        name=meta.get('name') or (re.search(r'resValue\("string",\s*"app_name",\s*"([^"]+)"',gradle).group(1))
        vector=ET.fromstring(read(meta.get('icon','app/src/main/res/drawable/ic_launcher_foreground.xml')))
        colours={e.attrib['name']:e.text for e in ET.fromstring(read(meta.get('colours','app/src/main/res/values/icon_colors.xml')))}
        paths=[]
        for node in vector.iter('path'):
            fill=node.get(A+'fillColor','#006B5E');fill=colours.get(fill.removeprefix('@color/'),fill)
            if re.fullmatch('#[0-9A-Fa-f]{8}',fill):fill='#'+fill[3:]+fill[1:3]
            if not re.fullmatch('#(?:[0-9A-Fa-f]{6}|[0-9A-Fa-f]{8})',fill):raise ValueError('Unsupported icon colour: '+fill)
            paths.append(f'<path fill="{fill}" fill-rule="{escape(node.get(A+"fillType","nonzero").lower())}" d="{escape(node.get(A+"pathData",""),quote=True)}"/>')
        apps.append({'slug':slug,'name':name,'description':meta.get('description',f'{name}: a Shoal app for Android.'),'paths':''.join(paths)})
    if not apps:raise ValueError('No Android apps found; refusing to replace the catalogue')
    return sorted(apps,key=lambda a:(a['slug']!='shoal',a['name'].casefold()))

def icon(app,x,y,size):return f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="22 22 64 64">{app["paths"]}</svg>'
def render(current,apps):
    others=[a for a in apps if a['slug']!=current['slug']]
    columns=10;rows=max(1,(len(others)+columns-1)//columns);height=320+rows*96
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}" role="img" aria-label="{escape(current["name"],quote=True)} - a Shoal app"><title>{escape(current["name"])} - a Shoal app</title><rect width="1200" height="{height}" rx="36" fill="#0e211f"/>',icon(current,60,40,172),f'<text x="265" y="143" fill="#def5ed" font-family="sans-serif" font-size="70" font-weight="700">{escape(current["name"])}</text>']
    shoal=next(a for a in apps if a['slug']=='shoal')
    out.extend([icon(shoal,268,176,48),'<text x="332" y="211" fill="#9ff2e2" font-family="sans-serif" font-size="29">A Shoal app</text>','<path d="M64 263H1136" stroke="#38534e"/>','<text x="66" y="302" fill="#b6cec6" font-family="sans-serif" font-size="17">SWIM WITH THE REST OF THE SHOAL</text>'])
    for i,app in enumerate(others):
        x=64+(i%columns)*108;y=322+(i//columns)*96
        out.extend([icon(app,x,y,62),f'<text x="{x+31}" y="{y+81}" text-anchor="middle" fill="#c4e0d7" font-family="sans-serif" font-size="12">{escape(app["name"])}</text>'])
    return ''.join(out)+'</svg>\n'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--org',default='ShoalApps');parser.add_argument('--local-root',type=Path);args=parser.parse_args()
    apps=discover(args.org,args.local_root);out=ROOT/'assets/readme';out.mkdir(parents=True,exist_ok=True)
    for app in apps:(out/(app['slug']+'.svg')).write_text(render(app,apps))
    shoal=next(a for a in apps if a['slug']=='shoal')
    (out/'shoalapps.github.io.svg').write_text(render(dict(shoal,slug='shoalapps.github.io',name='Shoal Apps'),apps))
    (ROOT/'apps.json').write_text(json.dumps([{k:v for k,v in a.items() if k!='paths'} for a in apps],indent=2)+'\n')
    print(f'Rendered {len(apps)+1} headers from {len(apps)} discovered apps')
if __name__=='__main__':main()
