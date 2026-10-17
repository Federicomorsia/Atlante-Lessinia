"""Assembla src/ in app/index.html, usando la copia locale di MapLibre.
Eseguire: python3 build/make.py. Non modifica i dati in app/data/.
app/ è la directory servita localmente e configurata per Vercel.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
html = (ROOT / 'src/index.html').read_text()
js = (ROOT / 'src/app.js').read_text()
css = (ROOT / 'app/vendor/maplibre-gl.css').read_text()
assert html.count('/*__MAPLIBRE_CSS__*/') == 1
assert html.count('/*__APP_JS__*/') == 1
frag = html.replace('/*__MAPLIBRE_CSS__*/', css).replace('/*__APP_JS__*/', js)
head_end = frag.index('</style>') + len('</style>')
full = ('<!doctype html>\n<html lang="it">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        + frag[:head_end] + '\n</head>\n<body>\n' + frag[head_end:] + '\n</body>\n</html>\n')
(ROOT / 'app/index.html').write_text(full)
print('app/index.html aggiornato da src/ (dati e vendor conservati)')
