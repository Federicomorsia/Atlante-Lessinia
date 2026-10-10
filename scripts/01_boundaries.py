"""Confini amministrativi (ISTAT 2026) e aree protette (EEA Natura 2000 2024, EEA NatDA v24)."""
import geopandas as gpd, pandas as pd, zipfile, json, os
from shapely.geometry import box
R='raw'; O='data'
BB=box(10.80,45.48,11.34,45.84)
def save(g,name,prec=6):
    g=g.to_crs(4326)
    import shapely
    g=g.copy(); g['geometry']=shapely.set_precision(g.geometry.values, 10**-prec)
    open(f'{O}/{name}.geojson','w').write(g.to_json(na='drop',drop_id=True,ensure_ascii=False))
    print(name,len(g),os.path.getsize(f'{O}/{name}.geojson'))
z='zip://'+R+'/istat_limiti_01012026.zip!'
bb32=gpd.GeoSeries([BB],crs=4326).to_crs(32632).iloc[0]
com=gpd.read_file(z+'Com01012026/Com01012026_WGS84.shp',bbox=bb32.bounds,encoding='utf-8')
com=com[com.intersects(bb32)]
print(com.columns.tolist())
prov=gpd.read_file(z+'ProvCM01012026/ProvCM01012026_WGS84.shp')
reg=gpd.read_file(z+'Reg01012026/Reg01012026_WGS84.shp')
pmap=dict(zip(prov.COD_PROV if 'COD_PROV' in prov else prov.COD_UTS, prov.DEN_UTS if 'DEN_UTS' in prov else prov.DEN_PROV))
smap=dict(zip(prov.COD_UTS, prov.SIGLA)) if 'SIGLA' in prov else {}
rmap=dict(zip(reg.COD_REG,reg.DEN_REG))
com['comune']=com.COMUNE; com['istat']=com.PRO_COM_T
com['provincia']=com.COD_UTS.map(pmap) if 'COD_UTS' in com else com.COD_PROV.map(pmap)
com['sigla']=com.COD_UTS.map(smap) if smap else ''
com['regione']=com.COD_REG.map(rmap)
com['geometry']=com.geometry.simplify(2)
save(com[['comune','istat','provincia','sigla','regione','geometry']],'confini_comuni')
# regioni/province clip
for g,n,col in [(reg,'confini_regioni','DEN_REG'),(prov,'confini_province','DEN_UTS')]:
    g=g[g.intersects(bb32)].copy(); g['nome']=g[col]; g['geometry']=g.geometry.intersection(bb32.buffer(4000)).simplify(2)
    save(g[['nome','geometry']],n)
# linea Veneto / Trentino-Alto Adige
v=reg[reg.DEN_REG=='Veneto'].geometry.iloc[0]; t=reg[reg.DEN_REG.str.startswith('Trentino')].geometry.iloc[0]
line=v.boundary.intersection(t.buffer(5)).intersection(bb32.buffer(3000))
gl=gpd.GeoDataFrame({'nome':['Confine regionale Veneto / Trentino-Alto Adige'],'fonte':['ISTAT 2026']},geometry=[line.simplify(2)],crs=32632)
save(gl,'confine_veneto_trentino')
# Natura 2000
sci=gpd.read_file(R+'/eea_n2000_sci_habitats.geojson'); spa=gpd.read_file(R+'/eea_n2000_spa_birds.geojson')
print(sci.columns.tolist())
n2=pd.concat([sci.assign(direttiva='Habitat (SIC/ZSC)'),spa.assign(direttiva='Uccelli (ZPS)')])
keep=[c for c in ['SITECODE','SITENAME','SITETYPE','MS','RELEASE_DATE'] if c in n2.columns]
n2=n2[keep+['direttiva','geometry']]
n2=n2[n2.intersects(BB)]
TYPES={'A':'ZPS (Direttiva Uccelli)','B':'SIC/ZSC (Direttiva Habitat)','C':'SIC/ZSC e ZPS coincidenti'}
n2=n2.sort_values('direttiva').drop_duplicates('SITECODE')
n2['tipo']=n2.SITETYPE.map(TYPES)
import datetime
n2['release']=pd.to_datetime(n2.RELEASE_DATE,unit='ms').dt.strftime('%Y-%m-%d')
n2['regione']=n2.SITECODE.str[:4].map({'IT31':'Trentino-Alto Adige','IT32':'Veneto'})
n2=n2[['SITECODE','SITENAME','SITETYPE','tipo','regione','release','geometry']]
n2['geometry']=n2.to_crs(32632).geometry.simplify(2).to_crs(4326)
save(n2,'natura2000')
nd=gpd.read_file(R+'/eea_natda_v24_large.geojson'); print(nd.columns.tolist())
nd=nd[nd.intersects(BB)]
def fix(x):
    for _ in range(3):
        try: x=x.encode('latin1').decode('utf8')
        except Exception: break
    return x
nd['nome']=nd.siteName.map(fix).str.replace('PalÃƒÂ¹','Palù')
nd['tipo']=nd.designationTypeCode.map({'IT04':'Parco naturale regionale','IT05':'Riserva naturale statale','IT30':'Riserva naturale provinciale'}).fillna(nd.designationTypeCode)
nd=nd.rename(columns={'legalFoundationDate':'anno_istituzione','nationalId':'codice_euap','siteArea':'area_ha','iucncat':'iucn'})
nd=nd[['nome','tipo','anno_istituzione','codice_euap','area_ha','iucn','geometry']]
nd['geometry']=nd.to_crs(32632).geometry.simplify(2).to_crs(4326)
save(nd,'aree_protette_natda')
