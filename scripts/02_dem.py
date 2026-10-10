"""DEM TINITALY 1.1 (INGV, 10 m) -> curve di livello, hillshade, raster quote (Web Mercator)."""
import rasterio, numpy as np, json, glob
from rasterio.merge import merge
from rasterio.warp import reproject, Resampling, transform_bounds, calculate_default_transform
from rasterio.transform import from_bounds
from PIL import Image
from skimage import measure
from scipy.ndimage import gaussian_filter
from pyproj import Transformer
W,S,E,N=10.80,45.48,11.34,45.84
srcs=[rasterio.open(f) for f in sorted(glob.glob('raw/w5*/*.tif'))]
b32=transform_bounds(4326,32632,W,S,E,N)
dem,tr=merge(srcs,bounds=b32,res=10,nodata=-9999); dem=dem[0]
print('dem',dem.shape,np.nanmin(np.where(dem<-9000,np.nan,dem)),dem.max())
dem=np.where(dem<-9000,np.nan,dem)
# ---- contours from 20 m grid (smoothed)
d20=dem[::2,::2]; d20s=gaussian_filter(np.nan_to_num(d20,nan=0),1.2)
t=Transformer.from_crs(32632,4326,always_xy=True)
feats=[]
for z in range(100,2300,50):
    for c in measure.find_contours(d20s,z):
        if len(c)<8: continue
        rows,cols=c[:,0],c[:,1]
        x=tr.c+(cols*2+0.5)*10; y=tr.f-(rows*2+0.5)*10
        lon,lat=t.transform(x,y)
        from shapely.geometry import LineString
        ls=LineString(list(zip(x,y))).simplify(6)
        if ls.length<150: continue
        lon,lat=t.transform(*ls.xy)
        coords=[[round(a,5),round(b,5)] for a,b in zip(lon,lat)]
        feats.append({'type':'Feature','properties':{'quota':z,'direttrice':z%250==0},'geometry':{'type':'LineString','coordinates':coords}})
open('data/dem_curve_livello_50m.geojson','w').write(json.dumps({'type':'FeatureCollection','features':feats},separators=(',',':')))
print('contours',len(feats))
# ---- reproject to EPSG:3857
b3857=transform_bounds(4326,3857,W,S,E,N)
px=15.0
w=int((b3857[2]-b3857[0])/px); h=int((b3857[3]-b3857[1])/px)
dst_tr=from_bounds(*b3857,w,h)
d3=np.full((h,w),np.nan,dtype='float32')
reproject(dem.astype('float32'),d3,src_transform=tr,src_crs=32632,dst_transform=dst_tr,dst_crs=3857,src_nodata=np.nan,dst_nodata=np.nan,resampling=Resampling.bilinear)
# ground resolution at lat 45.66 = px*cos(lat)
g=px*np.cos(np.radians(45.66))
dy,dx=np.gradient(np.nan_to_num(d3,nan=np.nanmean(d3)),g)
slope=np.arctan(np.hypot(dx,dy)); aspect=np.arctan2(-dx,dy)
def hs(az,alt):
    az=np.radians(360-az+90); alt=np.radians(alt)
    return np.sin(alt)*np.cos(slope)+np.cos(alt)*np.sin(slope)*np.cos(az-aspect)
shade=0.5*hs(315,45)+0.25*hs(270,45)+0.25*hs(0,45)
shade=np.clip(shade,0,1)
# ombreggiatura "cotta" sul colore carta della mappa (#F3F4F0): JPEG opaco, nessuna trasparenza da quantizzare
paper=np.array([243,244,240],dtype='float32')
flat=np.sin(np.radians(45))
k=np.where(shade<flat, 0.58+0.42*(shade/flat), 1+0.035*(shade-flat)/(1-flat))   # ombre fino a -42%, luci appena più chiare
rgb=np.clip(paper[None,None,:]*k[...,None],0,255)
rgb[np.isnan(d3)]=paper
Image.fromarray(rgb.astype('uint8'),'RGB').save('data/dem_hillshade_3857.jpg',quality=84,optimize=True,progressive=True)
# ---- terrarium-encoded elevation (for readout) at 30 m
d30=d3[::3,::3]; v=np.nan_to_num(d30,nan=0)+32768
enc=np.zeros(d30.shape+(3,),dtype='uint8')
enc[...,0]=(v//256).astype('uint8'); enc[...,1]=(np.floor(v)%256).astype('uint8'); enc[...,2]=0
Image.fromarray(enc,'RGB').save('data/dem_quote_terrarium_3857.png',optimize=True)
json.dump({'bounds_lonlat':[W,S,E,N],'coordinates':[[W,N],[E,N],[E,S],[W,S]],'hillshade_px_m':px,'quote_px_m':px*3,'size_hillshade':[w,h],'size_quote':[d30.shape[1],d30.shape[0]],'source':'TINITALY 1.1 (INGV), DOI 10.13127/tinitaly/1.1, CC BY 4.0'},open('data/dem_meta.json','w'),indent=1)
print('done',w,h)
