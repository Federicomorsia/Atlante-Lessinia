"""OpenStreetMap (Overpass API) -> layer GeoJSON tematici, ritagliati sull'estensione dell'atlante."""
import json, subprocess, os, glob, sys
import geopandas as gpd, pandas as pd, shapely
from shapely.geometry import box
from shapely.ops import unary_union
BB=box(10.80,45.48,11.34,45.84); O='data'
OTG=os.path.expanduser('~/tools/node_modules/.bin/osmtogeojson')
def load(pattern):
    gs=[]
    for f in sorted(glob.glob('raw/'+pattern)):
        out=subprocess.run([OTG,'-m',f],capture_output=True,text=True,check=True).stdout
        g=gpd.GeoDataFrame.from_features(json.loads(out)['features'],crs=4326)
        if len(g): gs.append(g)
    g=pd.concat(gs,ignore_index=True) if gs else gpd.GeoDataFrame(geometry=[],crs=4326)
    if 'id' in g: g=g.drop_duplicates('id')
    return g
def col(g,c): return g[c] if c in g else pd.Series([None]*len(g),index=g.index)
def save(g,name,prec=5,simp=None):
    g=g.copy()
    g['geometry']=g.geometry.intersection(BB)
    g=g[~g.geometry.is_empty]
    if simp: g['geometry']=g.to_crs(32632).geometry.simplify(simp).to_crs(4326)
    g['geometry']=shapely.set_precision(g.geometry.values,10**-prec)
    g=g[~g.geometry.is_empty]
    open(f'{O}/{name}.geojson','w').write(g.to_json(na='drop',drop_id=True,ensure_ascii=False))
    print(name,len(g),os.path.getsize(f'{O}/{name}.geojson'))
which=sys.argv[1:] or ['water','routes','pois','roads','wood','open']
if 'water' in which:
    w=load('osm_water.json')
    ln=w[w.geom_type.isin(['LineString','MultiLineString']) & col(w,'waterway').notna()]
    ln=gpd.GeoDataFrame({'osm_id':ln['id'],'nome':col(ln,'name'),'tipo':col(ln,'waterway'),'intermittente':col(ln,'intermittent')},geometry=ln.geometry,crs=4326)
    save(ln,'osm_idrografia_linee',simp=3)
    ar=w[w.geom_type.isin(['Polygon','MultiPolygon']) & (col(w,'natural')=='water')]
    ar=gpd.GeoDataFrame({'osm_id':ar['id'],'nome':col(ar,'name'),'tipo':col(ar,'water')},geometry=ar.geometry,crs=4326)
    save(ar,'osm_idrografia_aree',simp=1)
    sp=w[(col(w,'natural')=='spring')]
    sp=gpd.GeoDataFrame({'osm_id':sp['id'],'nome':col(sp,'name')},geometry=sp.geometry.centroid,crs=4326)
    save(sp,'osm_sorgenti')
if 'routes' in which:
    r=load('osm_routes.json')
    r=r[r['id'].astype(str).str.startswith('relation')]
    r=gpd.GeoDataFrame({'osm_id':r['id'],'ref':col(r,'ref'),'nome':col(r,'name'),'network':col(r,'network'),'operator':col(r,'operator'),'osmc':col(r,'osmc:symbol'),'da':col(r,'from'),'a':col(r,'to'),'cai_scale':col(r,'cai_scale')},geometry=r.geometry,crs=4326)
    r=r[r.geom_type.isin(['LineString','MultiLineString'])]
    save(r,'osm_sentieri',simp=4)
if 'pois' in which:
    p=load('osm_pois.json')
    p['geometry']=p.geometry.representative_point()
    keep=['name','tourism','amenity','place','natural','mountain_pass','ele','building','landuse','operator','alt_name','wikidata','wikipedia','seasonal','description','access','shelter_type']
    p=gpd.GeoDataFrame({**{'osm_id':p['id']},**{k:col(p,k) for k in keep}},geometry=p.geometry,crs=4326)
    save(p,'osm_toponimi_punti')
if 'roads' in which:
    r=load('osm_roads*.json'); t=load('osm_track_*.json')
    r=pd.concat([r,t],ignore_index=True).drop_duplicates('id')
    r=r[r.geom_type.isin(['LineString','MultiLineString'])]
    r=gpd.GeoDataFrame({'osm_id':r['id'],'tipo':col(r,'highway'),'nome':col(r,'name'),'ref':col(r,'ref'),'tracktype':col(r,'tracktype'),'superficie':col(r,'surface')},geometry=r.geometry,crs=4326)
    r=r[r.tipo.isin(['motorway','trunk','primary','secondary','tertiary','unclassified','track','path','bridleway'])]
    # piste e sentieri non segnati solo sopra la pianura (lat > 45.56): fuori tema nelle aree urbane
    minor=r.tipo.isin(['track','path','bridleway'])
    r=r[~minor | (r.geometry.centroid.y>45.56)]
    from shapely.ops import linemerge
    main=r[~r.tipo.isin(['track','path','bridleway'])]
    save(main,'osm_viabilita',simp=4)
    mn=r[r.tipo.isin(['track','path','bridleway'])].to_crs(32632)
    mn['nome']=mn.nome.fillna('')
    parts=[]
    for (t,n),g in mn.groupby(['tipo','nome']):
        u=unary_union(g.geometry.values); m=linemerge(u) if u.geom_type=="MultiLineString" else u
        parts.append(gpd.GeoDataFrame({'tipo':[t],'nome':[n or None]},geometry=[m.simplify(5)],crs=32632))
    mn=pd.concat(parts).explode(index_parts=False).to_crs(4326)
    save(mn,'osm_piste_sentieri')
def landcover(pattern,name,classify):
    g=load(pattern); g=g[g.geom_type.isin(['Polygon','MultiPolygon'])]
    g['classe']=g.apply(classify,axis=1); g=g[g.classe.notna()]
    g=g.to_crs(32632); g['geometry']=g.geometry.buffer(0)
    parts=[]
    for c,sub in g.groupby('classe'):
        u=unary_union(sub.geometry.values)
        parts.append(gpd.GeoDataFrame({'classe':[c]},geometry=[u],crs=32632))
    d=pd.concat(parts).explode(index_parts=False)
    d['geometry']=d.geometry.simplify(9).buffer(0)
    d=d[d.area>2500].to_crs(4326)
    save(d,name,simp=None)
if 'wood' in which:
    landcover('osm_wood_*.json','osm_boschi',lambda x:'bosco')
if 'open' in which:
    def cl(x):
        n=x.get('natural'); l=x.get('landuse')
        if l=='meadow' or n=='grassland' or l=='grass': return 'prateria / prato-pascolo'
        if n in ('scrub','heath'): return 'arbusteto / brughiera'
        if n in ('bare_rock','scree'): return 'roccia / ghiaione'
        if l in ('farmland','orchard','vineyard'): return None  # escluso: coltivi di pianura, fuori tema
        if l=='residential': return 'abitato'
        if l=='quarry': return 'cava'
    landcover('osm_open_*.json','osm_copertura_aperta',cl)
