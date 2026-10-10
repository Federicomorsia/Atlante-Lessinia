"""Classifica i file scaricati dal browser (nomi temporanei) e li copia in raw/ con un nome parlante."""
import json, glob, os, shutil, hashlib, sys
DL=os.path.expanduser('~/mnt/Downloads'); RAW='raw'
seen={}
for f in glob.glob(RAW+'/osm_*.json'): seen[os.path.getsize(f)]=f
TILES={'a':(45.50,10.82,45.66,11.07),'b':(45.50,11.07,45.66,11.32),'c':(45.66,10.82,45.82,11.07),'d':(45.66,11.07,45.82,11.32),
       'b1':(45.50,11.07,45.58,11.32),'b2':(45.58,11.07,45.66,11.32),'c1':(45.66,10.82,45.74,11.07),'c2':(45.74,10.82,45.82,11.07)}
for f in glob.glob(DL+'/.*claudefordesktop*'):
    with open(f,'rb') as h: head=h.read(200)
    if b'Overpass API' not in head: continue
    d=json.load(open(f)); e=d['elements']
    if any('center' in x for x in e[:50]): continue
    tags=[x.get('tags',{}) for x in e if x.get('tags')]
    hw=[t.get('highway') for t in tags if 'highway' in t]
    kind=None
    if hw:
        kind='roadsmain' if set(hw)<= {'motorway','trunk','primary','secondary','tertiary','unclassified'} else 'track'
    elif any(t.get('natural')=='wood' or t.get('landuse')=='forest' for t in tags) and not any(t.get('landuse') in ('meadow','farmland') or t.get('natural') in ('grassland','scrub') for t in tags): kind='wood'
    elif any(t.get('landuse') in ('meadow','farmland','grass') or t.get('natural') in ('grassland','scrub','bare_rock') for t in tags): kind='open'
    else: continue
    if kind in ('roadsmain','track','wood','open'):
        # query bbox from osm3s? not present: infer from 'out skel' nodes median
        lats=sorted(x['lat'] for x in e if x['type']=='node'); lons=sorted(x['lon'] for x in e if x['type']=='node')
        if not lats: continue
        # pick the tile whose box contains the most nodes
        bb=(lats[int(len(lats)*.02)],lons[int(len(lons)*.02)],lats[int(len(lats)*.98)],lons[int(len(lons)*.98)])
        def iou(t):
            ix=max(0,min(bb[2],t[2])-max(bb[0],t[0]))*max(0,min(bb[3],t[3])-max(bb[1],t[1]))
            u=(bb[2]-bb[0])*(bb[3]-bb[1])+(t[2]-t[0])*(t[3]-t[1])-ix
            return ix/u if u else 0
        best=max(TILES,key=lambda k: iou(TILES[k]))
        name=f'{RAW}/osm_{kind}_{best}.json'
    out=name
    if os.path.exists(out) and os.path.getsize(out)>=os.path.getsize(f): continue
    shutil.copy(f,out); print('->',out,os.path.getsize(f))
