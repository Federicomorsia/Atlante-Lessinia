"""Assembla l'atlante: dist/ contiene index.html (pagina completa per uso locale), artifact.html (frammento per la pubblicazione),
data/, glyphs/, vendor/. Le sorgenti sono app/src (interfaccia) e app/data (dati)."""
import os, shutil, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, 'app'); DIST = os.path.join(ROOT, 'dist')
UP = '/mnt/user-data/uploads/Desktop/Atlante-Lessinia/data'
os.makedirs(DIST, exist_ok=True)
for d in ['data', 'vendor']: os.makedirs(os.path.join(DIST, d), exist_ok=True)
# data: processed base layers (from the user's machine) + thematic files authored here
for f in glob.glob(UP + '/*'): shutil.copy(f, os.path.join(DIST, 'data'))
for f in glob.glob(APP + '/data/*'): shutil.copy(f, os.path.join(DIST, 'data'))
# glyph PBF -> un unico JSON base64 (gli artifact non servono .pbf); l'app li legge con un protocollo personalizzato
import base64, json
G = {}
for f in sorted(glob.glob(os.path.join(APP, 'glyphs', '*', '*.pbf'))):
    G[os.path.basename(os.path.dirname(f)) + '/' + os.path.basename(f)[:-4]] = base64.b64encode(open(f, 'rb').read()).decode()
json.dump(G, open(os.path.join(DIST, 'data', 'glyphs_noto.json'), 'w'))
shutil.rmtree(os.path.join(DIST, 'glyphs'), ignore_errors=True)
NM = os.path.join(ROOT, 'node_modules', 'maplibre-gl', 'dist')
shutil.copy(os.path.join(NM, 'maplibre-gl.js'), os.path.join(DIST, 'vendor'))
css = open(os.path.join(NM, 'maplibre-gl.css')).read()
html = open(os.path.join(APP, 'src', 'index.html')).read()
js = open(os.path.join(APP, 'src', 'app.js')).read()
frag = html.replace('/*__MAPLIBRE_CSS__*/', css).replace('/*__APP_JS__*/', js)
open(os.path.join(DIST, 'artifact.html'), 'w').write(frag)
head_end = frag.index('</style>') + len('</style>')
full = ('<!doctype html>\n<html lang="it">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        + frag[:head_end] + '\n</head>\n<body>\n' + frag[head_end:] + '\n</body>\n</html>\n')
open(os.path.join(DIST, 'index.html'), 'w').write(full)
tot = sum(os.path.getsize(p) for p in glob.glob(DIST + '/**/*', recursive=True) if os.path.isfile(p))
print('dist ok', round(tot / 1e6, 1), 'MB')
