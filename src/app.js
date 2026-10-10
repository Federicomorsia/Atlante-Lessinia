/* Atlante della Lessinia — logica dell'interfaccia.
   I dati stanno in data/ e sono descritti da data/catalogo.json: per aggiungere un dataset
   si aggiunge il file e una voce al catalogo. Qui non ci sono coordinate né numeri tematici. */
(async function () {
'use strict';
const $ = (s, el = document) => el.querySelector(s);
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const fmt = n => n == null ? '—' : Number(n).toLocaleString('it-IT');
const getJSON = u => fetch(u).then(r => { if (!r.ok) throw new Error(u + ' ' + r.status); return r.json(); });

if (!window.maplibregl) {               // CDN non raggiungibile: copia locale
  await new Promise((ok, ko) => { const s = document.createElement('script'); s.src = 'vendor/maplibre-gl.js'; s.onload = ok; s.onerror = ko; document.head.appendChild(s); });
}

const [CAT, FONTI] = await Promise.all([getJSON('data/catalogo.json'), getJSON('data/fonti.json')]);
const FON = Object.fromEntries(FONTI.map(f => [f.id, f]));
const LYR = Object.fromEntries(CAT.livelli.map(l => [l.id, l]));
const STATE = { yr0: 2012, yr1: 2025, vis: {}, catFilter: 'tutti' };
CAT.livelli.forEach(l => STATE.vis[l.id] = !!l.visibile);
try { const v = JSON.parse(localStorage.getItem('atlante-lessinia-vis') || 'null'); if (v) Object.assign(STATE.vis, v); } catch (e) {}

const C = { ink:'#1D2226', ink2:'#4B5359', ink3:'#7C858B', paper:'#F3F4F0', sheet:'#FBFBF8', conflict:'#B4432C', wolf:'#54479A', park:'#2C7A57', cai:'#C23B22', water:'#5C8DAF', contour:'#A8957C' };
const F_REG = ['noto-regular'], F_MED = ['noto-medium'], F_IT = ['noto-italic'];

// ---------------------------------------------------------------- map
// glyphs: PBF ranges shipped in one JSON (data/glyphs_noto.json), served to MapLibre through a custom protocol
const GLY = await getJSON('data/glyphs_noto.json');
const EMPTY = new ArrayBuffer(0);
maplibregl.addProtocol('glyph', async (params) => {
  const k = decodeURIComponent(params.url.replace('glyph://', '')).replace(/\.pbf$/, '');
  const b = GLY[k]; if (!b) return { data: EMPTY };
  const bin = atob(b), u = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i);
  return { data: u.buffer };
});
const glyphs = 'glyph://{fontstack}/{range}.pbf';
const map = new maplibregl.Map({
  container: 'map',
  style: { version: 8, glyphs, sources: {}, layers: [{ id: 'bg', type: 'background', paint: { 'background-color': C.paper } }] },
  bounds: CAT.vista_iniziale, fitBoundsOptions: { padding: 20 },
  maxBounds: [[CAT.estensione[0] - .25, CAT.estensione[1] - .15], [CAT.estensione[2] + .25, CAT.estensione[3] + .15]],
  minZoom: 9, maxZoom: 17, dragRotate: false, pitchWithRotate: false, touchPitch: false,
  attributionControl: false, preserveDrawingBuffer: true, canvasContextAttributes: { preserveDrawingBuffer: true }
});
map.touchZoomRotate.disableRotation();
map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right');
map.addControl(new maplibregl.ScaleControl({ maxWidth: 140, unit: 'metric' }), 'bottom-left');
map.addControl(new maplibregl.AttributionControl({ compact: false, customAttribution:
  'Confini © ISTAT 2026 · Aree protette © EEA 2024 · DTM TINITALY 1.1 © INGV (CC BY 4.0) · © OpenStreetMap contributors (ODbL)' }), 'bottom-right');
await new Promise(r => map.once('load', r));

// hatch patterns for Natura 2000
function hatch(id, color, dir) {
  const s = 12, c = document.createElement('canvas'); c.width = c.height = s;
  const x = c.getContext('2d'); x.strokeStyle = color; x.lineWidth = 1.1; x.globalAlpha = .85;
  x.beginPath();
  if (dir > 0) { x.moveTo(0, s); x.lineTo(s, 0); x.moveTo(-s/2, s/2); x.lineTo(s/2, -s/2); x.moveTo(s/2, s*1.5); x.lineTo(s*1.5, s/2); }
  else { x.moveTo(0, 0); x.lineTo(s, s); x.moveTo(-s/2, s/2); x.lineTo(s/2, s*1.5); x.moveTo(s/2, -s/2); x.lineTo(s*1.5, s/2); }
  x.stroke(); map.addImage(id, x.getImageData(0, 0, s, s));
}
hatch('h-zsc', '#7A8F2E', 1); hatch('h-zps', '#9A7A2A', -1);
function icon(id, size, draw) {
  const r = 2, c = document.createElement('canvas'); c.width = c.height = size * r;
  const x = c.getContext('2d'); x.scale(r, r); draw(x, size); map.addImage(id, x.getImageData(0, 0, size * r, size * r), { pixelRatio: r });
}
icon('i-malga', 9, (x, s) => { x.fillStyle = '#FBFBF8'; x.fillRect(0, 0, s, s); x.fillStyle = '#1D2226'; x.fillRect(1, 1, s - 2, s - 2); });
icon('i-malga-t', 9, (x, s) => { x.fillStyle = '#FBFBF8'; x.fillRect(0, 0, s, s); x.strokeStyle = '#1D2226'; x.lineWidth = 1.2; x.strokeRect(1.6, 1.6, s - 3.2, s - 3.2); });
icon('i-wolf', 15, (x, s) => { x.beginPath(); x.moveTo(s / 2, .8); x.lineTo(s - .8, s / 2); x.lineTo(s / 2, s - .8); x.lineTo(.8, s / 2); x.closePath(); x.fillStyle = '#54479A'; x.strokeStyle = '#FBFBF8'; x.lineWidth = 1.4; x.fill(); x.stroke(); });
icon('i-peak', 9, (x, s) => { x.beginPath(); x.moveTo(s / 2, 1); x.lineTo(s - 1, s - 1.5); x.lineTo(1, s - 1.5); x.closePath(); x.fillStyle = '#5A4E40'; x.fill(); });
icon('i-pass', 11, (x, s) => { x.strokeStyle = '#5A4E40'; x.lineWidth = 1.3; x.beginPath(); x.moveTo(2, 1.5); x.quadraticCurveTo(s / 2, s / 2 + 1, 2, s - 1.5); x.moveTo(s - 2, 1.5); x.quadraticCurveTo(s / 2, s / 2 + 1, s - 2, s - 1.5); x.stroke(); });

const DATA = {};
async function src(file) {
  if (!DATA[file]) DATA[file] = getJSON(file);
  return DATA[file];
}
function addGeo(id, data) { if (!map.getSource(id)) map.addSource(id, { type: 'geojson', data, tolerance: 0.25 }); }
const ORDER = [];               // [mapLayerId, catalogId]
function L(cat, spec) { spec.layout = Object.assign({ visibility: STATE.vis[cat] ? 'visible' : 'none' }, spec.layout || {}); map.addLayer(spec); ORDER.push([spec.id, cat]); }
const inter = (cat, id) => { (INTER[cat] = INTER[cat] || []).push(id); };
const INTER = {};

// ---- 01 rilievo
const dem = await getJSON('data/dem_meta.json');
map.addSource('rilievo', { type: 'image', url: 'data/dem_hillshade_3857.jpg', coordinates: dem.coordinates });
L('rilievo', { id: 'rilievo', type: 'raster', source: 'rilievo', paint: { 'raster-opacity': 1, 'raster-fade-duration': 0, 'raster-resampling': 'linear' } });

// ---- 01 coperture
addGeo('aperto', await src('data/osm_copertura_aperta.geojson'));
L('aperto', { id: 'aperto', type: 'fill', source: 'aperto', paint: { 'fill-color': ['match', ['get', 'classe'],
  'prateria / prato-pascolo', '#EEE7C8', 'arbusteto / brughiera', '#DDE2C6', 'roccia / ghiaione', '#E3E1DC', 'coltivo', '#EFEADF', 'abitato', '#E2DEDA', 'cava', '#E2DEDA', '#EEE'], 'fill-opacity': .62 } });
inter('aperto', 'aperto');
addGeo('boschi', await src('data/osm_boschi.geojson'));
L('boschi', { id: 'boschi', type: 'fill', source: 'boschi', paint: { 'fill-color': '#B9CDAE', 'fill-opacity': .5 } });

// ---- 02 aree di tutela (fills under lines)
addGeo('natda', await src('data/aree_protette_natda.geojson'));
addGeo('n2000', await src('data/natura2000.geojson'));
L('n2000_zsc', { id: 'n2000_zsc', type: 'fill', source: 'n2000', filter: LYR.n2000_zsc.filtro, paint: { 'fill-pattern': 'h-zsc', 'fill-opacity': .55 } });
L('n2000_zsc', { id: 'n2000_zsc_l', type: 'line', source: 'n2000', filter: LYR.n2000_zsc.filtro, paint: { 'line-color': '#7A8F2E', 'line-width': 1 } });
L('n2000_zps', { id: 'n2000_zps', type: 'fill', source: 'n2000', filter: LYR.n2000_zps.filtro, paint: { 'fill-pattern': 'h-zps', 'fill-opacity': .5 } });
L('n2000_zps', { id: 'n2000_zps_l', type: 'line', source: 'n2000', filter: LYR.n2000_zps.filtro, paint: { 'line-color': '#9A7A2A', 'line-width': 1, 'line-dasharray': [4, 2] } });
inter('n2000_zsc', 'n2000_zsc'); inter('n2000_zps', 'n2000_zps');

// ---- 04/05 choropleths by comune
const comuni = await src('data/confini_comuni.geojson');
const branchi = await src('data/tema_lupo_branchi_comuni_2022.json');
const aggr = await src('data/tema_predazioni_aggregate.json');
const norm = s => String(s).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
const comuniB = { type: 'FeatureCollection', features: comuni.features.map(f => {
  const names = branchi.branchi.filter(b => b.comuni.some(c => norm(c) === norm(f.properties.comune))).map(b => b.nome);
  const pr = aggr.righe.find(r => r.istat && r.istat === f.properties.istat && r.periodo === '2022');
  return { type: 'Feature', geometry: f.geometry, properties: { ...f.properties, n_branchi: names.length, branchi: names.join(' · '), pred_2022: pr ? pr.eventi : null } };
}) };
addGeo('comuni', comuniB);
L('lupo_branchi', { id: 'lupo_branchi', type: 'fill', source: 'comuni', filter: ['>', ['get', 'n_branchi'], 0],
  paint: { 'fill-color': ['step', ['get', 'n_branchi'], '#E4E0F0', 2, '#C7BFE2', 3, '#A397CF'], 'fill-opacity': .62 } });
inter('lupo_branchi', 'lupo_branchi');
L('pred_comuni', { id: 'pred_comuni', type: 'fill', source: 'comuni', filter: ['!=', ['get', 'pred_2022'], null],
  paint: { 'fill-color': ['step', ['get', 'pred_2022'], '#F2D9CF', 25, '#E3A994', 40, '#C9644A'], 'fill-opacity': .6 } });
inter('pred_comuni', 'pred_comuni');

// ---- 01 idrografia + curve
addGeo('idro_aree', await src('data/osm_idrografia_aree.geojson'));
L('idro_aree', { id: 'idro_aree', type: 'fill', source: 'idro_aree', paint: { 'fill-color': '#A9C7DC', 'fill-outline-color': C.water } });
inter('idro_aree', 'idro_aree');
addGeo('curve', await src('data/dem_curve_livello_50m.geojson'));
L('curve', { id: 'curve', type: 'line', source: 'curve', filter: ['!', ['get', 'direttrice']], minzoom: 10.5,
  paint: { 'line-color': C.contour, 'line-width': ['interpolate', ['linear'], ['zoom'], 11, .4, 15, 1], 'line-opacity': .85 } });
L('curve', { id: 'curve_d', type: 'line', source: 'curve', filter: ['get', 'direttrice'],
  paint: { 'line-color': C.contour, 'line-width': ['interpolate', ['linear'], ['zoom'], 10, .6, 15, 1.4], 'line-opacity': .9 } });
L('curve', { id: 'curve_lab', type: 'symbol', source: 'curve', filter: ['get', 'direttrice'], minzoom: 12,
  layout: { 'symbol-placement': 'line', 'text-field': ['to-string', ['get', 'quota']], 'text-font': F_REG, 'text-size': 9.5, 'symbol-spacing': 420, 'text-max-angle': 25 },
  paint: { 'text-color': '#8C7A62', 'text-halo-color': C.paper, 'text-halo-width': 1.6 } });
addGeo('idro', await src('data/osm_idrografia_linee.geojson'));
const IWIDTH = ['interpolate', ['linear'], ['zoom'], 10, ['match', ['get', 'tipo'], 'river', 1.4, .45], 14, ['match', ['get', 'tipo'], 'river', 2.4, 1.1]];
L('idro', { id: 'idro', type: 'line', source: 'idro', filter: ['!=', ['get', 'intermittente'], 'yes'], paint: { 'line-color': C.water, 'line-width': IWIDTH, 'line-opacity': .9 } });
L('idro', { id: 'idro_int', type: 'line', source: 'idro', filter: ['==', ['get', 'intermittente'], 'yes'], paint: { 'line-color': C.water, 'line-width': IWIDTH, 'line-dasharray': [3, 2], 'line-opacity': .9 } });
L('idro', { id: 'idro_lab', type: 'symbol', source: 'idro', minzoom: 12, filter: ['has', 'nome'],
  layout: { 'symbol-placement': 'line', 'text-field': ['get', 'nome'], 'text-font': F_IT, 'text-size': 10.5, 'symbol-spacing': 380 },
  paint: { 'text-color': '#3F6E8F', 'text-halo-color': C.paper, 'text-halo-width': 1.5 } });
inter('idro', 'idro'); inter('idro', 'idro_int');
addGeo('sorgenti', await src('data/osm_sorgenti.geojson'));
L('sorgenti', { id: 'sorgenti', type: 'circle', source: 'sorgenti', paint: { 'circle-radius': 2.6, 'circle-color': C.sheet, 'circle-stroke-color': C.water, 'circle-stroke-width': 1.3 } });
inter('sorgenti', 'sorgenti');

// ---- 06 viabilità e sentieri
addGeo('strade', await src('data/osm_viabilita.geojson'));
const MAJOR = ['motorway', 'trunk', 'primary', 'secondary'];
addGeo('piste', await src('data/osm_piste_sentieri.geojson'));
L('piste', { id: 'piste_track', type: 'line', source: 'piste', minzoom: 12, filter: ['==', ['get', 'tipo'], 'track'],
  paint: { 'line-color': '#9A938C', 'line-width': ['interpolate', ['linear'], ['zoom'], 12, .5, 16, 1.3], 'line-dasharray': [3, 1.5], 'line-opacity': .85 } });
L('piste', { id: 'piste_path', type: 'line', source: 'piste', minzoom: 12.5, filter: ['!=', ['get', 'tipo'], 'track'],
  paint: { 'line-color': '#9A938C', 'line-width': ['interpolate', ['linear'], ['zoom'], 12, .35, 16, .9], 'line-dasharray': [1, 1.5], 'line-opacity': .85 } });
inter('piste', 'piste_track'); inter('piste', 'piste_path');
L('strade', { id: 'strade_loc_c', type: 'line', source: 'strade', minzoom: 11, filter: ['in', ['get', 'tipo'], ['literal', ['tertiary', 'unclassified', 'residential']]],
  paint: { 'line-color': '#9A938C', 'line-width': ['interpolate', ['linear'], ['zoom'], 11, 1.2, 16, 4.5] } });
L('strade', { id: 'strade_loc', type: 'line', source: 'strade', minzoom: 11, filter: ['in', ['get', 'tipo'], ['literal', ['tertiary', 'unclassified', 'residential']]],
  paint: { 'line-color': '#FFFFFF', 'line-width': ['interpolate', ['linear'], ['zoom'], 11, .4, 16, 3] } });
L('strade', { id: 'strade_mag_c', type: 'line', source: 'strade', filter: ['in', ['get', 'tipo'], ['literal', MAJOR]],
  paint: { 'line-color': '#8C7F73', 'line-width': ['interpolate', ['linear'], ['zoom'], 9, 1.4, 16, 7] } });
L('strade', { id: 'strade_mag', type: 'line', source: 'strade', filter: ['in', ['get', 'tipo'], ['literal', MAJOR]],
  paint: { 'line-color': '#F7F1E6', 'line-width': ['interpolate', ['linear'], ['zoom'], 9, .6, 16, 5] } });
L('strade', { id: 'strade_lab', type: 'symbol', source: 'strade', minzoom: 12.5, filter: ['any', ['has', 'ref'], ['in', ['get', 'tipo'], ['literal', MAJOR]]],
  layout: { 'symbol-placement': 'line', 'text-field': ['coalesce', ['get', 'ref'], ['get', 'nome']], 'text-font': F_REG, 'text-size': 9.5, 'symbol-spacing': 500 },
  paint: { 'text-color': C.ink2, 'text-halo-color': '#fff', 'text-halo-width': 1.6 } });
inter('strade', 'strade_mag_c'); inter('strade', 'strade_loc_c');

addGeo('sentieri', await src('data/osm_sentieri.geojson'));
const IS250 = ['==', ['get', 'ref'], '250'];
L('sentieri', { id: 'sentieri', type: 'line', source: 'sentieri', minzoom: 10.5, filter: ['!', IS250],
  paint: { 'line-color': '#B0603F', 'line-width': ['interpolate', ['linear'], ['zoom'], 11, .5, 15, 1.4], 'line-dasharray': [2, 2], 'line-opacity': .7 } });
L('sentieri', { id: 'sentieri_250_h', type: 'line', source: 'sentieri', filter: IS250,
  paint: { 'line-color': '#FFFFFF', 'line-width': ['interpolate', ['linear'], ['zoom'], 10, 3, 15, 6], 'line-opacity': .9 } });
L('sentieri', { id: 'sentieri_250', type: 'line', source: 'sentieri', filter: IS250,
  paint: { 'line-color': C.cai, 'line-width': ['interpolate', ['linear'], ['zoom'], 10, 1.4, 15, 3], 'line-dasharray': [3, 1.2] } });
L('sentieri', { id: 'sentieri_lab', type: 'symbol', source: 'sentieri', minzoom: 13, filter: ['has', 'ref'],
  layout: { 'symbol-placement': 'line', 'text-field': ['get', 'ref'], 'text-font': F_MED, 'text-size': 9.5, 'symbol-spacing': 300 },
  paint: { 'text-color': '#9C3A22', 'text-halo-color': '#fff', 'text-halo-width': 2 } });
inter('sentieri', 'sentieri'); inter('sentieri', 'sentieri_250');

// ---- 02 confini (above fills)
L('comuni', { id: 'comuni', type: 'line', source: 'comuni', paint: { 'line-color': '#6E7479', 'line-width': ['interpolate', ['linear'], ['zoom'], 9, .5, 14, 1.1], 'line-dasharray': [3, 2] } });
L('comuni', { id: 'comuni_lab', type: 'symbol', source: 'comuni', minzoom: 10, maxzoom: 13,
  layout: { 'text-field': ['upcase', ['get', 'comune']], 'text-font': F_REG, 'text-size': 9.5, 'text-letter-spacing': .18, 'text-max-width': 8 },
  paint: { 'text-color': '#7C858B', 'text-halo-color': C.paper, 'text-halo-width': 1.4 } });
addGeo('province', await src('data/confini_province.geojson'));
L('province', { id: 'province', type: 'line', source: 'province', paint: { 'line-color': '#3B4045', 'line-width': 1.2, 'line-dasharray': [6, 2, 1, 2] } });
addGeo('parco', (await src('data/aree_protette_natda.geojson')));
L('riserve', { id: 'riserve', type: 'line', source: 'natda', filter: LYR.riserve.filtro, paint: { 'line-color': '#5E8F74', 'line-width': 1.2, 'line-dasharray': [2, 2] } });
L('riserve', { id: 'riserve_f', type: 'fill', source: 'natda', filter: LYR.riserve.filtro, paint: { 'fill-color': '#5E8F74', 'fill-opacity': .07 } });
inter('riserve', 'riserve_f');
L('parco', { id: 'parco_halo', type: 'line', source: 'natda', filter: LYR.parco.filtro, paint: { 'line-color': C.park, 'line-width': ['interpolate', ['linear'], ['zoom'], 9, 3, 14, 9], 'line-opacity': .16, 'line-offset': ['interpolate', ['linear'], ['zoom'], 9, 1.5, 14, 4.5] } });
L('parco', { id: 'parco', type: 'line', source: 'natda', filter: LYR.parco.filtro, paint: { 'line-color': C.park, 'line-width': 1.6 } });
L('parco', { id: 'parco_hit', type: 'fill', source: 'natda', filter: LYR.parco.filtro, paint: { 'fill-color': C.park, 'fill-opacity': 0.01 } });
inter('parco', 'parco_hit');
addGeo('regioni', await src('data/confine_veneto_trentino.geojson'));
L('regioni', { id: 'regioni_h', type: 'line', source: 'regioni', paint: { 'line-color': '#FFFFFF', 'line-width': 5, 'line-opacity': .7 } });
L('regioni', { id: 'regioni', type: 'line', source: 'regioni', paint: { 'line-color': C.ink, 'line-width': 2.2, 'line-dasharray': [5, 1.5, 1, 1.5, 1, 1.5] } });
L('regioni', { id: 'regioni_lab', type: 'symbol', source: 'regioni', minzoom: 11,
  layout: { 'symbol-placement': 'line', 'text-field': 'VENETO   ·   TRENTINO-ALTO ADIGE', 'text-font': F_MED, 'text-size': 9.5, 'text-letter-spacing': .2, 'symbol-spacing': 700, 'text-offset': [0, -1] },
  paint: { 'text-color': C.ink, 'text-halo-color': C.paper, 'text-halo-width': 1.6 } });
inter('regioni', 'regioni');
inter('comuni', 'comuni_hit');
map.addLayer({ id: 'comuni_hit', type: 'fill', source: 'comuni', paint: { 'fill-color': '#000', 'fill-opacity': 0 }, layout: { visibility: STATE.vis.comuni ? 'visible' : 'none' } }, 'aperto');
ORDER.push(['comuni_hit', 'comuni']);

// ---- 06 toponimi
const topo = await src('data/osm_toponimi_punti.geojson');
addGeo('topo', topo);
const isPlace = ['in', ['get', 'place'], ['literal', ['town', 'village']]];
const isHamlet = ['in', ['get', 'place'], ['literal', ['hamlet']]];
const isPeak = ['==', ['get', 'natural'], 'peak'];
const isPass = ['any', ['==', ['get', 'natural'], 'saddle'], ['==', ['get', 'mountain_pass'], 'yes']];
const isHut = ['==', ['get', 'tourism'], 'alpine_hut'];
L('toponimi', { id: 'topo_peak', type: 'symbol', source: 'topo', minzoom: 11.5, filter: ['all', isPeak, ['has', 'name']],
  layout: { 'icon-image': 'i-peak', 'text-field': ['format', ['get', 'name'], {}, ['case', ['has', 'ele'], ['concat', '\n', ['get', 'ele']], ''], { 'font-scale': .85 }],
    'text-font': F_IT, 'text-size': 10, 'text-anchor': 'top', 'text-offset': [0, .55], 'text-max-width': 8, 'symbol-sort-key': ['-', 0, ['to-number', ['get', 'ele'], 0]] },
  paint: { 'text-color': '#5A4E40', 'text-halo-color': C.paper, 'text-halo-width': 1.5 } });
L('toponimi', { id: 'topo_pass', type: 'symbol', source: 'topo', minzoom: 11.5, filter: ['all', isPass, ['has', 'name']],
  layout: { 'icon-image': 'i-pass', 'text-field': ['get', 'name'], 'text-font': F_IT, 'text-size': 10, 'text-anchor': 'left', 'text-offset': [.75, 0], 'text-max-width': 9 },
  paint: { 'text-color': '#5A4E40', 'text-halo-color': C.paper, 'text-halo-width': 1.5 } });
L('toponimi', { id: 'topo_hamlet', type: 'symbol', source: 'topo', minzoom: 12, filter: ['all', isHamlet, ['has', 'name']],
  layout: { 'text-field': ['get', 'name'], 'text-font': F_REG, 'text-size': 10.5, 'text-max-width': 8 },
  paint: { 'text-color': C.ink2, 'text-halo-color': C.paper, 'text-halo-width': 1.6 } });
L('toponimi', { id: 'topo_place', type: 'symbol', source: 'topo', filter: ['all', isPlace, ['has', 'name']],
  layout: { 'text-field': ['get', 'name'], 'text-font': F_MED, 'text-size': ['interpolate', ['linear'], ['zoom'], 9, 10.5, 14, 14], 'text-max-width': 8 },
  paint: { 'text-color': C.ink, 'text-halo-color': C.paper, 'text-halo-width': 1.8 } });
inter('toponimi', 'topo_peak'); inter('toponimi', 'topo_pass'); inter('toponimi', 'topo_place'); inter('toponimi', 'topo_hamlet');

// ---- 03 malghe
addGeo('malghe', await src('data/osm_malghe.geojson'));
L('malghe', { id: 'malghe', type: 'symbol', source: 'malghe', minzoom: 10.5,
  layout: { 'icon-image': ['case', ['==', ['get', 'tipo_oggetto'], 'edificio'], 'i-malga', 'i-malga-t'], 'icon-size': ['interpolate', ['linear'], ['zoom'], 10.5, .7, 15, 1.2], 'icon-allow-overlap': true, 'icon-ignore-placement': true } });
L('malghe', { id: 'malghe_lab', type: 'symbol', source: 'malghe', minzoom: 13, filter: ['==', ['get', 'tipo_oggetto'], 'edificio'],
  layout: { 'text-field': ['get', 'nome'], 'text-font': F_REG, 'text-size': 10, 'text-anchor': 'left', 'text-offset': [.7, 0], 'text-max-width': 9, 'text-optional': true },
  paint: { 'text-color': C.ink2, 'text-halo-color': C.paper, 'text-halo-width': 1.5 } });
inter('malghe', 'malghe');

// ---- 05 conflitti (proportional, time-aware)
const conf = await src('data/tema_conflitti_malghe.geojson');
addGeo('conflitti', confData());
function confData() {
  return { type: 'FeatureCollection', features: conf.features.map(f => {
    let n = 0; for (const [y, v] of Object.entries(f.properties.serie)) if (+y >= STATE.yr0 && +y <= STATE.yr1) n += v;
    return { ...f, properties: { ...f.properties, n_int: n } };
  }) };
}
const R = ['*', 3, ['sqrt', ['get', 'n_int']]];   // area ∝ eventi
L('conflitti', { id: 'conflitti', type: 'circle', source: 'conflitti', filter: ['>', ['get', 'n_int'], 0],
  paint: { 'circle-radius': ['interpolate', ['linear'], ['zoom'], 10, ['*', .55, R], 14, ['*', 1.4, R]], 'circle-color': C.conflict, 'circle-opacity': .28, 'circle-stroke-color': C.conflict, 'circle-stroke-width': 1.3 } });
L('conflitti', { id: 'conflitti_lab', type: 'symbol', source: 'conflitti', minzoom: 12, filter: ['>', ['get', 'n_int'], 0],
  layout: { 'text-field': ['to-string', ['get', 'n_int']], 'text-font': F_MED, 'text-size': 10, 'text-allow-overlap': true },
  paint: { 'text-color': '#7E2A18', 'text-halo-color': C.sheet, 'text-halo-width': 1.2 } });
inter('conflitti', 'conflitti');

// ---- 04 lupo eventi
addGeo('lupo_eventi', await src('data/tema_lupo_eventi_storici.geojson'));
L('lupo_eventi', { id: 'lupo_eventi', type: 'symbol', source: 'lupo_eventi',
  layout: { 'icon-image': 'i-wolf', 'icon-allow-overlap': true, 'icon-ignore-placement': true, 'icon-offset': ['case', ['==', ['get', 'data'], '2012-12-04'], ['literal', [11, 0]], ['literal', [0, 0]]] } });
inter('lupo_eventi', 'lupo_eventi');

// ---- luoghi A–H
const luoghi = await src('data/tema_luoghi_interesse.geojson');
addGeo('luoghi', luoghi);
// letter markers sit up-left of the exact point (small dot) so they never hide the data underneath
const OFF = [-15, -15];
icon('i-leader', 32, (x) => { x.strokeStyle = '#1D2226'; x.lineWidth = 1; x.beginPath(); x.moveTo(16, 16); x.lineTo(7, 7); x.stroke(); x.beginPath(); x.arc(16, 16, 2.4, 0, 7); x.fillStyle = '#1D2226'; x.fill(); });
L('luoghi', { id: 'luoghi_pt', type: 'symbol', source: 'luoghi', layout: { 'icon-image': 'i-leader', 'icon-allow-overlap': true, 'icon-ignore-placement': true } });
L('luoghi', { id: 'luoghi_box', type: 'circle', source: 'luoghi', paint: { 'circle-radius': 10, 'circle-color': C.sheet, 'circle-stroke-color': C.ink, 'circle-stroke-width': 1.6, 'circle-translate': OFF } });
L('luoghi', { id: 'luoghi', type: 'symbol', source: 'luoghi',
  layout: { 'text-field': ['get', 'lettera'], 'text-font': F_MED, 'text-size': 10.5, 'text-allow-overlap': true, 'text-ignore-placement': true },
  paint: { 'text-color': C.ink, 'text-translate': OFF } });
L('luoghi', { id: 'luoghi_lab', type: 'symbol', source: 'luoghi', minzoom: 11.5,
  layout: { 'text-field': ['get', 'nome'], 'text-font': F_MED, 'text-size': 11, 'text-anchor': 'left', 'text-offset': [-0.1, -1.36], 'text-max-width': 11, 'text-optional': true },
  paint: { 'text-color': C.ink, 'text-halo-color': C.sheet, 'text-halo-width': 2, 'text-translate': [12, 0] } });
inter('luoghi', 'luoghi_box');
map.addSource('sel', { type: 'geojson', data: { type: 'FeatureCollection', features: [] } });
map.addLayer({ id: 'sel', type: 'circle', source: 'sel', paint: { 'circle-radius': 16, 'circle-color': 'rgba(0,0,0,0)', 'circle-stroke-color': C.ui = '#264A6B', 'circle-stroke-width': 2 } });
$('#loading').hidden = true;

// ---------------------------------------------------------------- visibility & time
function setVis(cat, on) {
  STATE.vis[cat] = on;
  ORDER.filter(([, c]) => c === cat).forEach(([id]) => map.setLayoutProperty(id, 'visibility', on ? 'visible' : 'none'));
  try { localStorage.setItem('atlante-lessinia-vis', JSON.stringify(STATE.vis)); } catch (e) {}
  renderLegend(); applyTime();
}
function inRange(y) { return y >= STATE.yr0 && y <= STATE.yr1; }
function applyTime() {
  map.getSource('conflitti').setData(confData());
  map.setFilter('lupo_eventi', ['all', ['>=', ['get', 'anno'], STATE.yr0], ['<=', ['get', 'anno'], STATE.yr1]]);
  for (const id of ['lupo_branchi', 'pred_comuni']) {
    const ok = inRange(LYR[id].anno);
    map.setLayoutProperty(id, 'visibility', STATE.vis[id] && ok ? 'visible' : 'none');
  }
  const cov = [];
  const ce = Math.max(STATE.yr0, 2013), cs = Math.min(STATE.yr1, 2022);
  cov.push(ce <= cs ? `Predazioni per malga: dati ${ce}–${cs} (serie disponibile 2013–2022).` : 'Predazioni per malga: nessun dato nell\'intervallo (serie 2013–2022).');
  cov.push(inRange(2012) ? 'Osservazioni storiche del lupo: 2012.' : 'Osservazioni storiche del lupo (2012) escluse.');
  if (!inRange(2022)) cov.push('Livelli 2022 (branchi, predazioni per comune) nascosti.');
  $('#yrCov').textContent = cov.join(' ');
  $('#yrOut').textContent = STATE.yr0 === STATE.yr1 ? String(STATE.yr0) : `${STATE.yr0} – ${STATE.yr1}`;
  const a = (STATE.yr0 - 2012) / 13 * 100, b = (STATE.yr1 - 2012) / 13 * 100;
  $('#yrFill').style.left = a + '%'; $('#yrFill').style.width = (b - a) + '%';
}
$('#yr0').addEventListener('input', e => { STATE.yr0 = Math.min(+e.target.value, STATE.yr1); e.target.value = STATE.yr0; applyTime(); });
$('#yr1').addEventListener('input', e => { STATE.yr1 = Math.max(+e.target.value, STATE.yr0); e.target.value = STATE.yr1; applyTime(); });

// ---------------------------------------------------------------- side panes
function badge(stato) {
  const k = /secondaria/.test(stato) ? 'secondaria' : stato;
  const t = { verificato: 'Dato verificato', osservazione: 'Osservazione scientifica', interpretazione: 'Interpretazione', ipotesi: 'Ipotesi progettuale', secondaria: 'Fonte secondaria' }[k] || stato;
  return `<span class="badge ${esc(k)}">${esc(t)}</span>`;
}
function swatch(lg) {
  const c = lg.colore || C.ink;
  const s = { linea: `<svg class="sw" viewBox="0 0 26 14"><line x1="1" y1="7" x2="25" y2="7" stroke="${c}" stroke-width="${lg.spessore || 1.2}" stroke-dasharray="${lg.tratteggio || ''}"/></svg>`,
    area: `<svg class="sw" viewBox="0 0 26 14"><rect x="1" y="2" width="24" height="10" fill="${c}" stroke="rgba(0,0,0,.12)"/></svg>`,
    bordo: `<svg class="sw" viewBox="0 0 26 14"><rect x="2" y="2" width="22" height="10" fill="${c}" fill-opacity=".08" stroke="${c}" stroke-width="1.6" stroke-dasharray="${lg.tratteggio || ''}"/></svg>`,
    tratteggio: `<svg class="sw" viewBox="0 0 26 14"><defs><pattern id="p1" width="5" height="5" patternUnits="userSpaceOnUse"><path d="M0 5L5 0" stroke="${c}"/></pattern></defs><rect x="1" y="2" width="24" height="10" fill="url(#p1)" stroke="${c}"/></svg>`,
    tratteggio2: `<svg class="sw" viewBox="0 0 26 14"><defs><pattern id="p2" width="5" height="5" patternUnits="userSpaceOnUse"><path d="M0 0L5 5" stroke="${c}"/></pattern></defs><rect x="1" y="2" width="24" height="10" fill="url(#p2)" stroke="${c}" stroke-dasharray="3 1.5"/></svg>`,
    punto: `<svg class="sw" viewBox="0 0 26 14"><circle cx="13" cy="7" r="3" fill="#fff" stroke="${c}" stroke-width="1.4"/></svg>`,
    quadrato: `<svg class="sw" viewBox="0 0 26 14"><rect x="5" y="3.5" width="7" height="7" fill="${c}"/><rect x="15" y="3.5" width="7" height="7" fill="none" stroke="${c}"/></svg>`,
    rombo: `<svg class="sw" viewBox="0 0 26 14"><path d="M13 1.5L18.5 7L13 12.5L7.5 7Z" fill="${c}"/></svg>`,
    cerchi: `<svg class="sw" viewBox="0 0 26 14"><circle cx="8" cy="9" r="4" fill="${c}" fill-opacity=".28" stroke="${c}"/><circle cx="19" cy="7" r="6.3" fill="${c}" fill-opacity=".28" stroke="${c}"/></svg>`,
    lettera: `<svg class="sw" viewBox="0 0 26 14"><circle cx="13" cy="7" r="6" fill="#fff" stroke="${C.ink}" stroke-width="1.4"/><text x="13" y="9.6" font-size="7.5" text-anchor="middle" font-family="Archivo" font-weight="600" fill="${C.ink}">A</text></svg>`,
    raster: `<svg class="sw" viewBox="0 0 26 14"><defs><linearGradient id="hs" x1="0" x2="1"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#9aa0a4"/></linearGradient></defs><rect x="1" y="2" width="24" height="10" fill="url(#hs)"/></svg>`,
    testo: `<svg class="sw" viewBox="0 0 26 14"><text x="13" y="10.5" font-size="9" text-anchor="middle" font-family="Archivo" font-style="italic" fill="#5A4E40">▲ab</text></svg>` };
  if (lg.forma === 'categorie' || lg.forma === 'categorie_linea') {
    const v = lg.voci[0];
    return lg.forma === 'categorie' ? `<svg class="sw" viewBox="0 0 26 14">${lg.voci.slice(0, 3).map((x, i) => `<rect x="${1 + i * 8.3}" y="2" width="8" height="10" fill="${x[1]}"/>`).join('')}</svg>`
      : `<svg class="sw" viewBox="0 0 26 14"><line x1="1" y1="7" x2="25" y2="7" stroke="${v[1]}" stroke-width="${v[2]}" stroke-dasharray="3 1.2"/></svg>`;
  }
  return s[lg.forma] || '';
}
function renderLayers() {
  const pane = $('#pane-livelli');
  let h = '';
  for (const g of CAT.gruppi) {
    h += `<div class="sect"><h2><span class="n">${g.id}</span>${esc(g.titolo)}</h2>`;
    for (const l of CAT.livelli.filter(l => l.gruppo === g.id)) {
      if (l.tipo === 'alias') { h += `<p class="note">${esc(l.titolo)}: ${esc(l.nota)}</p>`; continue; }
      h += `<div class="lyr"><input type="checkbox" id="v-${l.id}" ${STATE.vis[l.id] ? 'checked' : ''}><span>${swatch(l.legenda)}</span><label for="v-${l.id}">${esc(l.titolo)}</label><span class="meta">${esc(l.periodo)}</span>`
        + (l.nota ? `<span class="sub">${esc(l.nota)}</span>` : '') + `</div>`;
    }
    if (g.id === '04') h += `<p class="note">Non sono rappresentati territori dei branchi, corridoi, spostamenti o siti riproduttivi: non esistono dati pubblici verificabili e le localizzazioni sensibili sono escluse per tutela della specie.</p>`;
    if (g.id === '05') h += `<p class="note">Le coordinate dei singoli eventi non sono pubbliche: i cerchi stanno sull'edificio della malga a cui la fonte attribuisce gli eventi; il resto è aggregato per comune o per area.</p>`;
    h += `</div>`;
  }
  h += `<div class="sect"><h2><span class="n">L</span>Luoghi del progetto</h2><div class="lyr"><input type="checkbox" id="v-luoghi" ${STATE.vis.luoghi ? 'checked' : ''}><span>${swatch(LYR.luoghi.legenda)}</span><label for="v-luoghi">Luoghi di interesse A–H</label><span class="meta">vari</span></div></div>`;
  pane.innerHTML = h;
  pane.querySelectorAll('input[type=checkbox]').forEach(cb => cb.addEventListener('change', e => setVis(e.target.id.slice(2), e.target.checked)));
}
function renderLegend() {
  let h = '';
  for (const g of [...CAT.gruppi, { id: 'L', titolo: 'Luoghi del progetto' }]) {
    const ls = CAT.livelli.filter(l => l.gruppo === g.id && l.tipo !== 'alias' && STATE.vis[l.id]);
    if (!ls.length) continue;
    h += `<div class="g">${g.id} · ${esc(g.titolo)}</div>`;
    for (const l of ls) {
      const lg = l.legenda;
      if (lg.forma === 'categorie' || lg.forma === 'categorie_linea') {
        h += `<div class="it"><span></span><span><b style="font-weight:600">${esc(l.titolo)}</b>${lg.testo ? `<small>${esc(lg.testo)}</small>` : ''}</span></div>`;
        for (const v of lg.voci) h += `<div class="it">${lg.forma === 'categorie' ? `<svg class="sw" viewBox="0 0 26 14"><rect x="1" y="2" width="24" height="10" fill="${v[1]}" stroke="rgba(0,0,0,.12)"/></svg>` : `<svg class="sw" viewBox="0 0 26 14"><line x1="1" y1="7" x2="25" y2="7" stroke="${v[1]}" stroke-width="${v[2]}" stroke-dasharray="${/250/.test(v[0]) ? '3 1.2' : (/Pista/.test(v[0]) ? '3 1.5' : (/^Sentiero$/.test(v[0]) ? '1 1.5' : (/itinerari/.test(v[0]) ? '2 2' : '')))}"/></svg>`}<span>${esc(v[0])}</span></div>`;
      } else {
        h += `<div class="it">${swatch(lg)}<span>${esc(l.titolo)}${lg.testo ? `<small>${esc(lg.testo)}</small>` : ''}</span></div>`;
      }
    }
  }
  $('#legBody').innerHTML = h || '<p class="note">Nessun livello attivo.</p>';
}
$('#legToggle').addEventListener('click', e => { const m = $('#legend').classList.toggle('min'); e.target.textContent = m ? 'espandi' : 'riduci'; });

const CATS = { tutti: 'Tutti', conflitto: 'Conflitto', lupo: 'Lupo', confine: 'Confini', ambiente: 'Ambiente', istituzione: 'Istituzioni', territorio: 'Territorio' };
const malghe = await src('data/osm_malghe.geojson');
function renderPlaces() {
  const pane = $('#pane-luoghi');
  const list = luoghi.features.filter(f => STATE.catFilter === 'tutti' || f.properties.categoria === STATE.catFilter);
  pane.innerHTML = `<div class="sect"><h2>Luoghi di interesse</h2>
    <div class="chips" role="group" aria-label="Filtra per categoria">${Object.entries(CATS).map(([k, v]) => `<button class="chip" type="button" data-cat="${k}" aria-pressed="${STATE.catFilter === k}">${v}</button>`).join('')}</div>
    ${list.map(f => { const p = f.properties; return `<button class="place" type="button" data-id="${p.id}"><span class="lt">${p.lettera}</span><span><div class="pn">${esc(p.nome)}</div><div class="pm">${esc(p.comune)} (${esc(p.provincia)}) · ${esc(p.tipologia)} · ${esc(p.periodo)}</div></span></button>`; }).join('')}
  </div>
  <div class="sect"><h2>Malghe e casere · ${malghe.features.length} in OSM</h2>
    <p class="note">Elenco dei toponimi contenenti "Malga", "Casara" o "Baito" mappati in OpenStreetMap nell'estensione dell'atlante. Non è un censimento ufficiale.</p>
    <input class="search" id="mSearch" type="search" placeholder="Cerca una malga" aria-label="Cerca una malga">
    <ul class="mlist" id="mList"></ul></div>`;
  pane.querySelectorAll('.chip').forEach(b => b.addEventListener('click', () => { STATE.catFilter = b.dataset.cat; renderPlaces(); }));
  pane.querySelectorAll('.place').forEach(b => b.addEventListener('click', () => {
    const f = luoghi.features.find(x => x.properties.id === b.dataset.id); focus(f, 14); showCard('luoghi', f);
  }));
  const fill = q => {
    const items = malghe.features.filter(f => !q || norm(f.properties.nome).includes(norm(q))).sort((a, b) => a.properties.nome.localeCompare(b.properties.nome, 'it')).slice(0, 400);
    $('#mList').innerHTML = items.map((f, i) => `<li><button type="button" data-i="${malghe.features.indexOf(f)}"><span>${esc(f.properties.nome)}</span><span class="q">${f.properties.quota_m ? f.properties.quota_m + ' m' : ''} ${esc(f.properties.comune || '')}</span></button></li>`).join('');
    $('#mList').querySelectorAll('button').forEach(b => b.addEventListener('click', () => { const f = malghe.features[+b.dataset.i]; if (!STATE.vis.malghe) { setVis('malghe', true); $('#v-malghe').checked = true; } focus(f, 15); showCard('malghe', f); }));
  };
  fill(''); $('#mSearch').addEventListener('input', e => fill(e.target.value));
}
const cron = await src('data/tema_lupo_cronologia.json');
function cubsChart() {
  const e = Object.entries(cron.cuccioli_minimi), W = 320, H = 120, pl = 22, pb = 18, pt = 12, max = 8;
  const bw = (W - pl) / e.length;
  let s = `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="Cuccioli minimi accertati per anno, branco Slavc e Giulietta">`;
  for (const t of [0, 2, 4, 6, 8]) { const y = H - pb - (H - pb - pt) * t / max; s += `<line x1="${pl}" x2="${W}" y1="${y}" y2="${y}" stroke="#E7E9E3"/><text x="${pl - 5}" y="${y + 3}" font-size="9" text-anchor="end" fill="#7C858B" font-family="IBM Plex Mono">${t}</text>`; }
  e.forEach(([y, v], i) => { const h = (H - pb - pt) * v / max, x = pl + i * bw + 3; s += `<rect x="${x}" y="${H - pb - h}" width="${bw - 6}" height="${h}" fill="#54479A"/><text x="${x + (bw - 6) / 2}" y="${H - pb - h - 3}" font-size="9" text-anchor="middle" fill="#1D2226" font-family="IBM Plex Mono">${v}</text><text x="${x + (bw - 6) / 2}" y="${H - 5}" font-size="9" text-anchor="middle" fill="#7C858B" font-family="IBM Plex Mono">${y.slice(2)}</text>`; });
  return s + '</svg>';
}
function renderData() {
  const rows = aggr.righe;
  $('#pane-dati').innerHTML = `<div class="sect"><h2><span class="n">05</span>Predazioni: statistiche per area</h2>
    <p class="note">${esc(aggr.nota)} "Eventi" = attacchi documentati; "capi" = animali coinvolti (vedi colonna note per uccisi/compromessi).</p>
    <div style="overflow-x:auto"><table class="t"><thead><tr><th>Area</th><th>Periodo</th><th class="num">Eventi</th><th class="num">Capi</th></tr></thead><tbody>
    ${rows.map(r => `<tr><td>${esc(r.area)}<div class="note" style="margin:2px 0 0">${esc(r.dettaglio)} ${r.fonti.map(id => `<a href="${esc(FON[id]?.url)}" target="_blank" rel="noopener">[${esc(id)}]</a>`).join(' ')} ${/secondaria/.test(r.stato) ? badge(r.stato) : ''}</div></td><td style="white-space:nowrap">${esc(r.periodo)}</td><td class="num">${fmt(r.eventi)}</td><td class="num">${fmt(r.capi)}</td></tr>`).join('')}
    </tbody></table></div></div>
    <div class="sect"><h2><span class="n">05</span>Malghe di Ala a impatto cronico</h2><p class="note">Eventi di predazione per anno, 2013–2022 (MUSE–PAT 2023, Tab. 5).</p>
    <div style="overflow-x:auto"><table class="t"><thead><tr><th>Malga</th>${[13,14,15,16,17,18,19,20,21,22].map(y => `<th class="num">'${y}</th>`).join('')}<th class="num">Tot.</th></tr></thead><tbody>
    ${conf.features.map(f => `<tr><td>${esc(f.properties.nome.replace('Malga ', ''))}</td>${Object.values(f.properties.serie).map(v => `<td class="num">${v || '·'}</td>`).join('')}<td class="num"><b>${f.properties.eventi_tot}</b></td></tr>`).join('')}
    </tbody></table></div></div>
    <div class="sect"><h2><span class="n">04</span>Ritorno del lupo: cronologia</h2><ol class="tl">${cron.cronologia.map(c => `<li><time>${esc(c.data)}</time><span>${esc(c.evento)} <span class="note">[${c.fonti.join(', ')}]</span></span></li>`).join('')}</ol></div>
    <div class="sect"><h2><span class="n">04</span>Cuccioli minimi accertati, branco Slavc–Giulietta</h2>${cubsChart()}<p class="note">Valori minimi, non stime di popolazione. Fonte: ${esc(FON.PAT2022.autore)} (${FON.PAT2022.anno}), Tab. 1.</p></div>
    <div class="sect"><h2><span class="n">04</span>Branchi nella Lessinia veronese, 2022</h2><table class="t"><thead><tr><th>Branco</th><th class="num">Ind.</th><th>Comuni indicati</th></tr></thead><tbody>${branchi.branchi.map(b => `<tr><td>${esc(b.nome)}<div class="note" style="margin:0">${esc(b.dettaglio)}</div></td><td class="num">${b.individui}</td><td>${esc(b.comuni.join(', '))}</td></tr>`).join('')}</tbody></table><p class="note">${esc(branchi.nota)}</p></div>`;
}
const AVAIL = await src('data/registro_dataset.json');
function renderSources() {
  $('#pane-fonti').innerHTML = `<div class="sect"><h2>Gradi di verifica</h2>
    <div class="statusline">${badge('verificato')}${badge('osservazione')}${badge('interpretazione')}${badge('ipotesi')}${badge('fonte secondaria')}</div>
    <p class="note">Dato verificato: geometria o valore tratto da una fonte ufficiale o scientifica identificata. Osservazione scientifica: evento datato registrato da monitoraggio o studio. Interpretazione e ipotesi progettuale: in questa versione non sono rappresentate come dati geografici.</p></div>
    <div class="sect"><h2>Registro dei dataset</h2><div style="overflow-x:auto"><table class="t avail"><thead><tr><th>Dataset</th><th>Stato</th><th>Formato / anno</th></tr></thead><tbody>
    ${AVAIL.map(d => `<tr><td>${esc(d.dataset)}<div class="note" style="margin:2px 0 0">${esc(d.note)}</div></td><td><span class="${d.stato === 'integrato' ? 'st-ok' : d.stato === 'parziale' ? 'st-part' : 'st-no'}">${esc(d.stato.toUpperCase())}</span></td><td>${esc(d.formato)}<div class="note" style="margin:0">${esc(d.anno)}</div></td></tr>`).join('')}
    </tbody></table></div></div>
    <div class="sect"><h2>Fonti citate · consultazione 10/10/2026</h2>${FONTI.map(f => `<div class="src"><div class="id">${esc(f.id)}</div><b>${esc(f.titolo)}</b><div>${esc(f.autore)}${f.anno ? ', ' + f.anno : ''} · ${esc(f.tipo)}</div><div class="lic">Licenza: ${esc(f.licenza)} · <a href="${esc(f.url)}" target="_blank" rel="noopener">apri la fonte</a></div><div class="note" style="margin:3px 0 0">${esc(f.note)}</div></div>`).join('')}</div>`;
}

// ---------------------------------------------------------------- card
function srcList(ids) { return `<ol class="fonti">${[...new Set(ids)].map(id => { const f = FON[id]; return f ? `<li>${esc(f.autore)}${f.anno ? ' (' + f.anno + ')' : ''}, <i>${esc(f.titolo)}</i>. <a href="${esc(f.url)}" target="_blank" rel="noopener">Fonte</a></li>` : `<li>${esc(id)}</li>`; }).join('')}</ol>`; }
function coord(f) { const c = f.geometry.type === 'Point' ? f.geometry.coordinates : null; return c ? `${c[1].toFixed(5)} N, ${c[0].toFixed(5)} E` : null; }
function osmLink(id) { return id ? `<a href="https://www.openstreetmap.org/${esc(id)}" target="_blank" rel="noopener">${esc(id)}</a>` : '—'; }
function dl(pairs) { return '<dl>' + pairs.filter(p => p[1] != null && p[1] !== '').map(([k, v]) => `<dt>${esc(k)}</dt><dd>${v}</dd>`).join('') + '</dl>'; }
function showCard(cat, f) {
  const p = f.properties, l = LYR[cat] || {};
  let kick = `${l.gruppo && l.gruppo !== 'L' ? l.gruppo + ' · ' : ''}${esc(l.titolo || '')}`, title = p.nome || p.name || p.comune || p.SITENAME || '—', body = '', st = l.stato || 'verificato', fon = l.fonti || [];
  if (cat === 'luoghi') {
    kick = `Luogo ${p.lettera} · ${esc(p.tipologia)}`; st = p.stato; fon = p.fonti;
    body = dl([['Comune', esc(p.comune) + ' (' + esc(p.provincia) + ')'], ['Coordinate', coord(f) + ' <span class="note">WGS84</span>'], ['Quota', p.quota_m ? p.quota_m + ' m' : null], ['Precisione', esc(p.precisione)], ['Oggetto OSM', osmLink(p.osm)], ['Periodo dati', esc(p.periodo)]])
      + `<p>${esc(p.descrizione)}</p><div class="h">Rilevanza per il progetto</div><p>${esc(p.rilevanza)}</p>`;
    const c = conf.features.find(x => x.properties.osm === p.osm) || (p.id === 'scortigara' ? 'multi' : null);
    if (c === 'multi') { const sc = conf.features.filter(x => /Scortigara/.test(x.properties.nome)); body += `<div class="h">Eventi di predazione 2013–2022</div><p>${sc.map(x => x.properties.nome.replace('Malga Scortigara ', '') + ' ' + x.properties.eventi_tot).join(' · ')} eventi, tutti su bovini (MUSE–PAT 2023). Le serie annuali sono nelle schede dei cerchi rossi.</p>`; }
    else if (c) body += `<div class="h">Eventi di predazione 2013–2022</div><p><b>${c.properties.eventi_tot}</b> eventi, ${c.properties.capi_uccisi} capi uccisi (MUSE–PAT 2023). Serie annuale e aggiornamenti nella scheda del cerchio rosso.</p>`;
  } else if (cat === 'conflitti') {
    title = p.nome; kick = `05 · Conflitto documentato · ${esc(p.comune)} (${esc(p.provincia)})`; st = p.stato; fon = p.fonti.concat((p.aggiornamenti || []).flatMap(a => a.fonti));
    const ys = Object.entries(p.serie), mx = Math.max(...ys.map(v => v[1]), 1);
    body = `<div class="bars">${ys.map(([y, v]) => `<div class="${inRange(+y) ? '' : 'off'}" style="height:${v / mx * 100}%">${v ? `<span>${v}</span>` : ''}</div>`).join('')}</div><div class="bars-x">${ys.map(([y]) => `<span>'${y.slice(2)}</span>`).join('')}</div>
      <p class="note">Eventi di predazione per anno; grigio = fuori dall'intervallo selezionato.</p>`
      + dl([['Eventi', `<b>${p.eventi_tot}</b> (2013–2022)`], ['Capi compromessi', p.capi_compromessi], ['Capi uccisi', p.capi_uccisi], ['Specie', esc(p.specie)], ['Impatto', esc(p.impatto)], ['Prevenzione 2021', esc(p.prevenzione_2021)], ['Coordinate', coord(f) + ' · edificio ' + osmLink(p.osm)]])
      + `<p class="note">${esc(p.nota)}${p.nota_fonte ? ' ' + esc(p.nota_fonte) : ''}</p>`
      + (p.aggiornamenti ? `<div class="h">Dopo il 2022 · fonti secondarie</div>` + p.aggiornamenti.map(a => `<div class="upd"><b>${esc(a.periodo)}</b> — ${esc(a.testo)}</div>`).join('') : '');
  } else if (cat === 'lupo_eventi') {
    title = `${p.nome}, ${new Date(p.data).toLocaleDateString('it-IT', { day: 'numeric', month: 'long', year: 'numeric' })}`; st = p.stato; fon = p.fonti;
    body = `<p>${esc(p.evento)}</p>` + dl([['Comune', esc(p.comune) + ' (' + esc(p.provincia) + ')'], ['Localizzazione', esc(p.precisione)], ['Coordinate', coord(f)]])
      + `<p class="note">Evento storico datato. Non indica una presenza attuale o costante del lupo in questo luogo.</p>`;
  } else if (cat === 'malghe') {
    body = dl([['Tipo oggetto', p.tipo_oggetto === 'edificio' ? 'Edificio mappato' : 'Solo toponimo / località'], ['Comune', esc(p.comune || '—')], ['Quota', p.quota_m ? p.quota_m + ' m (OSM)' : '—'], ['Coordinate', coord(f)], ['Oggetto OSM', osmLink(p.osm_id)]])
      + `<p class="note">Posizione dell'edificio o del toponimo. La superficie di pascolo della malga non è disponibile e non viene disegnata.</p>`;
    const c = conf.features.find(x => x.properties.osm === p.osm_id);
    if (c) body += `<div class="h">Conflitti documentati</div><p>${c.properties.eventi_tot} eventi di predazione 2013–2022 (MUSE–PAT 2023).</p>`;
  } else if (cat === 'comuni' || cat === 'lupo_branchi' || cat === 'pred_comuni') {
    title = p.comune; kick = `Comune · ISTAT ${esc(p.istat)}`;
    body = dl([['Provincia', esc(p.provincia) + ' (' + esc(p.sigla) + ')'], ['Regione', esc(p.regione)], ['Parco Lessinia', null]]);
    const b = p.n_branchi ? `<div class="h">Lupo · 2022</div><p>Comune indicato nel territorio di: ${esc(p.branchi)}.</p>` : '';
    const pr = p.pred_2022 != null ? `<div class="h">Predazioni · 2022</div><p><b>${p.pred_2022}</b> eventi di predazione (fonte: Parco della Lessinia).</p>` : '';
    body += b + pr; fon = ['ISTAT2026'].concat(p.n_branchi || p.pred_2022 != null ? ['PARCO2023'] : []);
  } else if (cat === 'parco' || cat === 'riserve') {
    title = p.nome; body = dl([['Tipo', esc(p.tipo)], ['Codice EUAP', esc(p.codice_euap)], ['Istituzione', esc(p.anno_istituzione)], ['Superficie', p.area_ha ? fmt(p.area_ha) + ' ha (dichiarati)' : null], ['IUCN', esc(p.iucn)]]);
    if (p.codice_euap === 'EUAP0241') body += `<p>Il perimetro del Parco copre la parte alta e centrale dell'altopiano veronese. La Lessinia geografica è più ampia e comprende il versante trentino (Ala, Avio) e le valli meridionali.</p><p class="note">Fonte geometrica: EEA NatDA v24 (comunicato dall'Italia). Da confrontare con la perimetrazione ufficiale della Regione del Veneto, non scaricabile in questa sessione.</p>`;
  } else if (cat === 'n2000_zsc' || cat === 'n2000_zps') {
    title = p.SITENAME; kick = `Natura 2000 · ${esc(p.SITECODE)}`;
    body = dl([['Tipo', esc(p.tipo)], ['Regione', esc(p.regione)], ['Versione', 'EEA ' + esc(p.release)]]) + `<p><a href="https://natura2000.eea.europa.eu/Natura2000/SDF.aspx?site=${esc(p.SITECODE)}" target="_blank" rel="noopener">Formulario standard del sito</a></p>`;
  } else if (cat === 'regioni') {
    title = 'Confine Veneto / Trentino-Alto Adige'; body = `<p>Limite regionale ISTAT 2026. Sulla dorsale Fittanze – Castelberto ricalca in larga parte la linea veneto-austriaca fissata dal Trattato di Rovereto (1753), segnata da cippi dal 1754.</p>`; fon = ['ISTAT2026', 'VENETO_CONFINE'];
  } else if (cat === 'sentieri') {
    title = (p.ref ? 'CAI ' + p.ref + ' · ' : '') + (p.nome || 'Itinerario'); body = dl([['Rete', esc(p.network)], ['Gestione', esc(p.operator)], ['Da / a', [p.da, p.a].filter(Boolean).map(esc).join(' → ')], ['Difficoltà', esc(p.cai_scale)], ['Relazione OSM', osmLink(p.osm_id)]]);
    if (p.ref === '250') body += `<p>Dorsale Alta della Lessinia, Giazza – Fosse/Peri, circa 40 km. Percorre il crinale Podestaria – Castelberto – Revoltel – Sega di Ala – Passo Fittanze.</p>`;
  } else if (cat === 'aperto') {
    title = p.classe; body = `<p>Copertura del suolo OSM. Le praterie d'altopiano sono in gran parte pascoli d'alpeggio, ma il poligono non corrisponde alla superficie assegnata a una specifica malga.</p>`;
  } else {
    title = p.nome || p.name || p.tipo || l.titolo;
    body = dl([['Tipo', esc(p.tipo || p.place || p.natural || p.tourism || '')], ['Quota', p.ele ? esc(p.ele) + ' m' : null], ['Coordinate', coord(f)], ['Oggetto OSM', osmLink(p.osm_id)]]);
  }
  const card = $('#card');
  card.innerHTML = `<header><div class="kicker">${kick}</div><h4>${esc(title)}</h4><button class="close" type="button" aria-label="Chiudi scheda">×</button></header>
    <div class="body"><div class="statusline">${badge(st)}<span class="badge" style="color:var(--ink-3)">${esc(p.periodo || l.periodo || '')}</span></div>${body}<div class="h">Fonti</div>${srcList(fon.length ? fon : (l.fonti || []))}</div>`;
  card.hidden = false;
  $('.close', card).addEventListener('click', () => { card.hidden = true; map.getSource('sel').setData({ type: 'FeatureCollection', features: [] }); });
  if (f.geometry.type === 'Point') map.getSource('sel').setData({ type: 'FeatureCollection', features: [{ type: 'Feature', geometry: f.geometry, properties: {} }] });
}
function focus(f, z) { if (f.geometry.type === 'Point') map.flyTo({ center: f.geometry.coordinates, zoom: Math.max(map.getZoom(), z), duration: matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 900 }); }

// click priority: point layers first
const PRI = ['luoghi', 'conflitti', 'lupo_eventi', 'malghe', 'sorgenti', 'toponimi', 'sentieri', 'regioni', 'strade', 'piste', 'idro', 'idro_aree', 'pred_comuni', 'lupo_branchi', 'n2000_zps', 'n2000_zsc', 'parco', 'riserve', 'aperto', 'comuni'];
function hit(pt) {
  for (const cat of PRI) {
    if (!STATE.vis[cat] || !INTER[cat]) continue;
    const ids = INTER[cat].filter(id => map.getLayer(id) && map.getLayoutProperty(id, 'visibility') !== 'none');
    if (!ids.length) continue;
    const bb = [[pt.x - 5, pt.y - 5], [pt.x + 5, pt.y + 5]];
    const fs = map.queryRenderedFeatures(bb, { layers: ids });
    if (fs.length) return [cat, fs[0]];
  }
  return null;
}
map.on('click', e => {
  const h = hit(e.point); if (!h) return;
  let [cat, f] = h;
  // recover full geometry/properties from source data for points
  const full = { type: 'Feature', geometry: f.geometry, properties: { ...f.properties } };
  ['serie'].forEach(k => { if (typeof full.properties[k] === 'string') try { full.properties[k] = JSON.parse(full.properties[k]); } catch (x) {} });
  if (cat === 'conflitti') { const o = conf.features.find(x => x.properties.osm === f.properties.osm); if (o) Object.assign(full.properties, o.properties); }
  if (cat === 'luoghi') { const o = luoghi.features.find(x => x.properties.id === f.properties.id); if (o) Object.assign(full, o); }
  if (cat === 'lupo_eventi') { full.properties.fonti = JSON.parse(f.properties.fonti || '[]'); }
  showCard(cat, full);
});
map.on('mousemove', e => { map.getCanvas().style.cursor = hit(e.point) ? 'pointer' : ''; readout(e.lngLat); });

// ---------------------------------------------------------------- elevation readout (TINITALY, terrarium-encoded PNG)
let Z = null;
(async () => {
  const img = new Image(); img.src = 'data/dem_quote_terrarium_3857.png'; await img.decode();
  const c = document.createElement('canvas'); c.width = img.width; c.height = img.height;
  const x = c.getContext('2d', { willReadFrequently: true }); x.drawImage(img, 0, 0);
  Z = { d: x.getImageData(0, 0, c.width, c.height).data, w: c.width, h: c.height };
})();
const mx = lon => (lon + 180) / 360, my = lat => { const s = Math.sin(lat * Math.PI / 180); return .5 - Math.log((1 + s) / (1 - s)) / (4 * Math.PI); };
const [W0, S0, E0, N0] = dem.bounds_lonlat;
function readout(ll) {
  let q = '';
  if (Z && ll.lng > W0 && ll.lng < E0 && ll.lat > S0 && ll.lat < N0) {
    const px = Math.floor((mx(ll.lng) - mx(W0)) / (mx(E0) - mx(W0)) * Z.w), py = Math.floor((my(ll.lat) - my(N0)) / (my(S0) - my(N0)) * Z.h);
    const i = (py * Z.w + px) * 4; const v = Z.d[i] * 256 + Z.d[i + 1] - 32768; if (v > 0) q = ` · ${v} m s.l.m.`;
  }
  $('#readout').textContent = `${ll.lat.toFixed(5)} N  ${ll.lng.toFixed(5)} E${q}`;
}

// ---------------------------------------------------------------- toolbar
$('#btnHome').addEventListener('click', () => map.fitBounds(CAT.vista_iniziale, { padding: 20 }));
$('#btnAll').addEventListener('click', () => map.fitBounds(CAT.estensione, { padding: 10 }));
function toast(t) { const el = $('#toast'); el.textContent = t; el.hidden = false; clearTimeout(toast.t); toast.t = setTimeout(() => el.hidden = true, 3200); }
$('#btnPng').addEventListener('click', async () => {
  map.triggerRepaint(); await new Promise(r => map.once('render', r));
  const mc = map.getCanvas(), dpr = mc.width / mc.clientWidth;
  const out = document.createElement('canvas'); out.width = mc.width; out.height = mc.height + Math.round(64 * dpr);
  const x = out.getContext('2d'); x.fillStyle = '#FBFBF8'; x.fillRect(0, 0, out.width, out.height); x.drawImage(mc, 0, 0);
  x.fillStyle = '#1D2226'; x.font = `600 ${13 * dpr}px Archivo, Arial`; x.fillText('Atlante della Lessinia', 14 * dpr, mc.height + 22 * dpr);
  x.font = `400 ${10 * dpr}px Archivo, Arial`; x.fillStyle = '#4B5359';
  const b = map.getBounds(); const sc = $('.maplibregl-ctrl-scale')?.textContent || '';
  x.fillText(`Estensione ${b.getWest().toFixed(4)}–${b.getEast().toFixed(4)} E, ${b.getSouth().toFixed(4)}–${b.getNorth().toFixed(4)} N · WGS84 / Web Mercator · scala grafica ${sc} · Nord in alto · intervallo dati ${STATE.yr0}–${STATE.yr1}`, 14 * dpr, mc.height + 39 * dpr);
  x.fillText('Confini © ISTAT 2026 · Aree protette © EEA 2024 · DTM TINITALY 1.1 © INGV (CC BY 4.0) · © OpenStreetMap contributors (ODbL) · Predazioni: MUSE–PAT 2023; Parco Lessinia 2023', 14 * dpr, mc.height + 54 * dpr);
  // scale bar
  const y = mc.height - 30 * dpr, mpp = 40075016.686 * Math.cos(map.getCenter().lat * Math.PI / 180) / (512 * 2 ** map.getZoom());
  const nice = [100, 200, 500, 1000, 2000, 5000, 10000].find(m => m / mpp > 70) || 10000, len = nice / mpp * dpr;
  x.fillStyle = 'rgba(251,251,248,.9)'; x.fillRect(10 * dpr, y - 16 * dpr, len + 18 * dpr, 26 * dpr);
  x.strokeStyle = '#1D2226'; x.lineWidth = 1.5 * dpr; x.beginPath(); x.moveTo(18 * dpr, y); x.lineTo(18 * dpr + len, y); x.moveTo(18 * dpr, y - 5 * dpr); x.lineTo(18 * dpr, y + 3 * dpr); x.moveTo(18 * dpr + len, y - 5 * dpr); x.lineTo(18 * dpr + len, y + 3 * dpr); x.stroke();
  x.fillStyle = '#1D2226'; x.font = `500 ${9 * dpr}px "IBM Plex Mono", monospace`; x.fillText(nice >= 1000 ? nice / 1000 + ' km' : nice + ' m', 22 * dpr, y - 5 * dpr);
  // north
  x.beginPath(); x.moveTo(out.width - 30 * dpr, 16 * dpr); x.lineTo(out.width - 24 * dpr, 36 * dpr); x.lineTo(out.width - 30 * dpr, 31 * dpr); x.lineTo(out.width - 36 * dpr, 36 * dpr); x.closePath(); x.fill();
  x.font = `600 ${10 * dpr}px Archivo`; x.fillText('N', out.width - 33.5 * dpr, 48 * dpr);
  const blob = await new Promise(r => out.toBlob(r, 'image/png'));
  const name = `atlante-lessinia_${new Date().toISOString().slice(0, 10)}.png`;
  const dlc = window.claude?.use ? await window.claude.use('downloads').catch(() => null) : null;
  if (dlc) { try { await dlc.save({ filename: name, data: blob }); toast('PNG pronto'); } catch (e) { toast(e?.code === 'declined' ? 'Esportazione annullata' : 'Esportazione non disponibile in questa vista'); } return; }
  const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = name; document.body.appendChild(a); a.click(); a.remove(); toast('PNG salvato: ' + name);
});

// ---------------------------------------------------------------- tabs
document.querySelectorAll('.tabs button').forEach(b => b.addEventListener('click', () => {
  document.querySelectorAll('.tabs button').forEach(x => x.setAttribute('aria-selected', String(x === b)));
  document.querySelectorAll('.pane').forEach(p => p.hidden = p.id !== 'pane-' + b.dataset.tab);
}));

renderLayers(); renderLegend(); renderPlaces(); renderData(); renderSources(); applyTime();
window.__atlante = { map, STATE };
})().catch(err => { console.error(err); const l = document.getElementById('loading'); if (l) { l.hidden = false; l.textContent = 'Errore nel caricamento: ' + err.message; } });
