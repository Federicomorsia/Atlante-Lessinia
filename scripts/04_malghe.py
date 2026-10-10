"""Malghe e casere da OSM: un punto per malga (edificio se mappato, altrimenti toponimo), con comune ISTAT."""
import geopandas as gpd, pandas as pd, json
p=gpd.read_file('data/osm_toponimi_punti.geojson')
m=p[p.name.fillna('').str.contains(r'(?i)\b(malga|casara|baito)\b')].copy()
m=m[~m.name.str.contains(r'(?i)sentiero|strada|via |pozza|pozzo|vaio|valle|monte |busa|buso|grotta|covolo')]
m['tipo_oggetto']=m.osm_id.str.startswith('node').map({True:'toponimo',False:'edificio'})
m=m.to_crs(32632)
m['key']=m.name.str.lower().str.replace(r'\s+',' ',regex=True).str.strip()
m['rank']=m.tipo_oggetto.map({'edificio':0,'toponimo':1})
m=m.sort_values('rank')
keep=[]
for k,g in m.groupby('key'):
    used=[]
    for i,r in g.iterrows():
        if any(r.geometry.distance(u)<250 for u in used): continue
        used.append(r.geometry); keep.append(i)
m=m.loc[keep]
quota=[]
c=gpd.read_file('data/confini_comuni.geojson').to_crs(32632)
m=gpd.sjoin(m,c[['comune','sigla','geometry']],how='left',predicate='within')
m['comune']=m.comune+' ('+m.sigla+')'
m['quota_m']=pd.to_numeric(m.ele,errors='coerce').round()
out=m[['name','osm_id','tipo_oggetto','comune','quota_m','geometry']].rename(columns={'name':'nome'}).to_crs(4326)
out['quota_m']=out.quota_m.astype('Int64')
open('data/osm_malghe.geojson','w').write(out.to_json(na='drop',drop_id=True,ensure_ascii=False))
print(len(out), out.tipo_oggetto.value_counts().to_dict())
# verifica dei luoghi del progetto
pts={'Fittanze':(10.97912,45.68389),'Castelberto':(11.01696,45.71894),'Folignani':(11.03,45.672),'Revoltel':(10.99727,45.71148),'Podestaria':(11.04703,45.70093),'Scortigara Cima':(11.0452,45.71306)}
g=gpd.GeoDataFrame({'n':list(pts)},geometry=gpd.points_from_xy(*zip(*pts.values())),crs=4326).to_crs(32632)
j=gpd.sjoin(g,c[['comune','geometry']],how='left',predicate='within')
l=gpd.read_file('data/confine_veneto_trentino.geojson').to_crs(32632).geometry.iloc[0]
for _,r in j.iterrows(): print(r.n,'->',r.comune,'| dist confine regionale m:',round(r.geometry.distance(l)))
w=gpd.read_file('data/osm_boschi.geojson').to_crs(32632)
fp=gpd.GeoSeries(gpd.points_from_xy([11.03],[45.672]),crs=4326).to_crs(32632).iloc[0]
print('Folignani point in wood:',w.contains(fp).any())
