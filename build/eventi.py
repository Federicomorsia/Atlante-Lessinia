"""
Archivio eventi 2012–2026 dell'Atlante della Lessinia.
Input : research/all_raw.json (schede raccolte da quattro ricerche documentali parallele, 10/10/2026)
Output: app/data/tema_eventi.geojson          eventi localizzabili (punto al toponimo OSM o al comune)
        app/data/tema_eventi_archivio.json     tutti gli eventi, compresi quelli non localizzabili
Regole: nessuna coordinata inventata; località risolte solo su toponimi OSM verificati (id indicato)
        o sul punto rappresentativo del comune ISTAT; aree vaghe e siti riproduttivi non vanno in mappa.
"""
import json, os, re, unicodedata
from shapely.geometry import shape, Point
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = json.load(open(os.path.join(ROOT, 'research', 'all_raw.json')))
BY = {e['_src']: e for e in RAW}
OUT = os.path.join(ROOT, 'app', 'data')
COM = json.load(open(os.path.join(ROOT, 'dist', 'data', 'confini_comuni.geojson')))['features']
EXT = (10.80, 45.48, 11.34, 45.84)

# ---------------------------------------------------------------- 1. duplicati: gruppi da fondere (il primo è la scheda principale)
MERGE = [
 ['D1', 'A2', 'C0'], ['A0', 'D2'], ['A3', 'C1', 'D6'], ['D8', 'B1'], ['D12', 'A5', 'C3'], ['D11', 'B2', 'C2'], ['C4', 'A6'],
 ['A11', 'D14'], ['D13', 'C5'], ['C8', 'A13'], ['C9', 'A14'], ['A17', 'D16'], ['A15', 'B8'], ['D18', 'A20'], ['C10', 'A26', 'D19'],
 ['D20', 'A21'], ['A22', 'C11'], ['A23', 'C12'], ['A24', 'C13'], ['B15', 'D27', 'A33'], ['C18', 'A34'], ['D29', 'A39', 'C24'],
 ['B20', 'A41'], ['A40', 'C25'], ['C29', 'D31'], ['A50', 'C30', 'D34'], ['B22', 'A43'], ['C26', 'A44'], ['C27', 'A48'],
 ['C33', 'D33'], ['A52', 'C32'], ['D38', 'A59', 'B40', 'C40'], ['B30', 'D35'], ['B32', 'A56', 'D36'], ['B33', 'A57'], ['B34', 'D37'],
 ['C39', 'A58'], ['B36', 'D39'], ['C46', 'A62', 'B39', 'D41'], ['C42', 'A60', 'D40'], ['B37', 'A61'], ['C56', 'A65'],
 ['B45', 'D43'], ['B46', 'D44'], ['B49', 'D46', 'A67', 'C57'], ['B47', 'A66', 'D45'], ['C58', 'A69', 'D47'], ['B51', 'A71'],
 ['C63', 'D51'], ['C64', 'A73'], ['B59', 'A72'],
]
# schede escluse: duplicati concettuali o fuori tema
DROP = {
 'D42': 'pubblicazione della tesi: è una fonte, non un evento territoriale',
 'D30': 'dato nazionale/alpino, già nel pannello Dati',
}

# ---------------------------------------------------------------- 2. toponimi verificati su OpenStreetMap (estrazione Overpass 10/10/2026)
L = {  # chiave: (lon, lat, oggetto OSM, etichetta di precisione)
 'branchetto': (11.07019, 45.67905, 'node/471966828', 'toponimo (Passo del Branchetto)'),
 'malera': (11.09565, 45.67779, 'node/4336780532', 'toponimo (Rifugio Malga Malera)'),
 'potteghe': (11.10313, 45.66198, 'node/8234132562', 'toponimo (Monte Potteghe)'),
 'valbella': (10.99421, 45.68343, 'way/293146632', 'edificio della malga'),
 'fosse': (10.93663, 45.64497, 'node/1165500605', 'centro abitato (Fosse)'),
 'podestaria': (11.04703, 45.70093, 'way/143205782', 'edificio (rifugio Podestaria)'),
 'revoltel': (10.99727, 45.71148, 'way/152088705', 'edificio della malga'),
 'sega': (10.97504, 45.69475, 'node/2477526670', 'località (Sega di Ala)'),
 'vallina_sopra': (11.00783, 45.68361, 'node/5983354619', 'toponimo della malga'),
 'riondera': (10.96557, 45.72625, 'way/373933665', 'edificio della malga'),
 'tecchie': (11.10652, 45.6235, 'node/2319810960', 'contrada (Tecchie)'),
 'san_rocco_piegara': (11.08572, 45.55316, 'node/2314421913', 'frazione (San Rocco di Piegara)'),
 'stander': (11.08671, 45.61988, 'node/2318713332', 'contrada (Stander)'),
 'mama_avio': (10.92163, 45.70517, 'node/303626845', "frazione (Mama d'Avio)"),
 'gabbiola': (10.85388, 45.64878, 'way/1553719225', 'località (Gabbiola)'),
 'raossi': (11.11868, 45.78268, 'node/317401114', 'frazione (Raossi)'),
 'boldera': (10.97467, 45.68641, 'way/140264909', 'edificio della malga'),
 'posta': (11.11845, 45.72163, 'way/448545381', 'edificio (ex Malga Posta)'),
 'serravalle': (11.01352, 45.81246, 'node/2621355085', "centro abitato (Serravalle all'Adige)"),
 'barozze': (10.94949, 45.64407, 'node/2379813028', 'contrada (Barozze)'),
 'speccheri': (11.12974, 45.76585, 'node/301582126', 'frazione (Speccheri)'),
 'squaranto': (11.04405, 45.59947, 'node/2319554894', 'contrada (Squaranto, basso vajo)'),
 'borghetto_avio': (10.92693, 45.69858, 'node/303626554', "frazione (Borghetto all'Adige)"),
 'derocchetto': (11.00068, 45.67029, 'node/5983354614', 'toponimo della malga'),
 'campoleva_sopra': (11.06991, 45.68736, 'node/10034101794', 'località (Campolevà di Sopra)'),
 'lugo': (10.99182, 45.57563, 'node/1185166082', 'centro abitato (Lugo)'),
 'cime': (10.96022, 45.7037, 'way/140264940', 'edificio (Malga delle Cime)'),
 'san_valentino_ala': (10.98099, 45.72448, 'node/4450717110', 'località (San Valentino)'),
 'perobia': (11.06617, 45.75498, 'way/216614237', 'edificio della malga'),
 'chizzola': (11.00874, 45.81113, 'node/2621354992', 'centro abitato (Chizzola)'),
 'staffor': (10.98469, 45.63551, 'node/2388972302', 'contrada (Staffor)'),
 'vo_sinistro': (10.95789, 45.73417, 'node/4017868485', "frazione (Vò Sinistro)"),
 'rambalda': (10.97984, 45.67137, 'way/216674573', 'edificio della malga'),
 'lavacchio': (10.90158, 45.73002, 'way/94356024', 'edificio della malga'),
 'masi_avio': (10.93795, 45.71179, 'node/4005744879', "frazione (Masi d'Avio)"),
 'laorno': (11.05584, 45.64788, 'node/2822729651', 'località (Laorno)'),
 'campodalbero': (11.18187, 45.65817, 'node/6106827156', 'frazione (Campodalbero)'),
 'erbezzo': (11.00158, 45.64002, 'node/64778977', 'centro abitato (Erbezzo)'),
 'bosco': (11.02952, 45.6221, 'node/64778814', 'centro abitato (Bosco Chiesanuova)'),
 'ala': (11.00182, 45.7579, 'node/4464079806', 'centro abitato (Ala)'),
}
# ---------------------------------------------------------------- 3. localizzazione e territorio per scheda principale
# loc: chiave di L | 'comune' (punto del comune ISTAT) | None (non in mappa)
# terr: 'Lessinia' | 'limitrofo' (fondovalle, Vallarsa, Baldo, città: connesso ma distinto)
LOC = {
 'D0': ('branchetto', 'Lessinia'), 'A1': ('branchetto', 'Lessinia'), 'C0': ('branchetto', 'Lessinia'),
 'A0': ('malera', 'Lessinia'), 'D3': ('potteghe', 'Lessinia'), 'D4': ('valbella', 'Lessinia'), 'D5': ('comune', 'Lessinia'),
 'A3': ('fosse', 'Lessinia'), 'D7': ('podestaria', 'Lessinia'), 'D8': ('revoltel', 'Lessinia'), 'D9': ('revoltel', 'Lessinia'),
 'B0': ('comune', 'Lessinia'), 'B3': ('comune', 'Lessinia'), 'A7': ('vallina_sopra', 'Lessinia'),
 'A12': ('comune', 'Lessinia'), 'B5': ('riondera', 'Lessinia'), 'B6': ('sega', 'Lessinia'), 'A15': ('comune', 'Lessinia'),
 'B9': ('ala', 'limitrofo'), 'A22': ('comune', 'Lessinia'), 'A23': ('tecchie', 'Lessinia'), 'A24': ('erbezzo', 'Lessinia'),
 'C16': ('comune', 'Lessinia'), 'B12': ('comune', 'Lessinia'), 'B13': ('raossi', 'limitrofo'), 'B14': ('sega', 'Lessinia'),
 'B15': ('boldera', 'Lessinia'), 'C18': ('san_rocco_piegara', 'Lessinia'), 'A37': ('stander', 'Lessinia'),
 'B16': ('mama_avio', 'limitrofo'), 'C20': ('gabbiola', 'Lessinia'), 'B17': ('comune', 'Lessinia'),
 'B21': ('posta', 'limitrofo'), 'C22': ('comune', 'Lessinia'), 'B20': ('serravalle', 'limitrofo'), 'A40': ('barozze', 'Lessinia'),
 'B19': ('speccheri', 'limitrofo'), 'A49': ('squaranto', 'Lessinia'), 'B22': ('comune', 'Lessinia'), 'C27': ('derocchetto', 'Lessinia'),
 'C26': ('comune', 'limitrofo'), 'A46': ('campoleva_sopra', 'Lessinia'), 'B23': ('borghetto_avio', 'limitrofo'),
 'C34': ('podestaria', 'Lessinia'), 'B24': ('serravalle', 'limitrofo'), 'C31': ('lugo', 'Lessinia'), 'B25': ('comune', 'Lessinia'),
 'B26': ('speccheri', 'limitrofo'), 'A55': ('cime', 'Lessinia'), 'B27': ('san_valentino_ala', 'Lessinia'), 'B28': ('perobia', 'limitrofo'),
 'B29': ('chizzola', 'limitrofo'), 'B30': ('boldera', 'Lessinia'), 'B31': ('boldera', 'Lessinia'), 'B32': ('boldera', 'Lessinia'),
 'B33': ('boldera', 'Lessinia'), 'B34': ('boldera', 'Lessinia'), 'B35': ('boldera', 'Lessinia'), 'C41': ('comune', 'Lessinia'),
 'B36': ('boldera', 'Lessinia'), 'C42': ('fosse', 'Lessinia'), 'C43': ('staffor', 'Lessinia'), 'B37': ('boldera', 'Lessinia'),
 'B38': ('comune', 'Lessinia'), 'C44': ('comune', 'Lessinia'), 'B41': ('borghetto_avio', 'limitrofo'), 'C50': ('comune', 'Lessinia'),
 'B42': ('vo_sinistro', 'limitrofo'), 'B43': ('comune', 'limitrofo'), 'B44': ('comune', 'Lessinia'), 'C55': ('comune', 'Lessinia'),
 'B45': ('boldera', 'Lessinia'), 'C56': ('bosco', 'Lessinia'), 'B46': ('boldera', 'Lessinia'), 'B47': ('boldera', 'Lessinia'),
 'B48': ('boldera', 'Lessinia'), 'B49': ('boldera', 'Lessinia'), 'C58': ('rambalda', 'Lessinia'), 'C59': ('rambalda', 'Lessinia'),
 'A70': ('boldera', 'Lessinia'), 'B50': ('boldera', 'Lessinia'), 'B51': ('boldera', 'Lessinia'), 'B52': ('lavacchio', 'limitrofo'),
 'B53': ('boldera', 'Lessinia'), 'D48': ('boldera', 'Lessinia'), 'B54': ('comune', 'limitrofo'), 'C60': ('comune', 'limitrofo'),
 'B56': ('masi_avio', 'limitrofo'), 'B57': ('comune', 'limitrofo'), 'C64': ('comune', 'Lessinia'), 'B59': ('boldera', 'Lessinia'),
 'C66': ('comune', 'Lessinia'), 'C67': ('laorno', 'Lessinia'), 'C68': ('campodalbero', 'Lessinia'), 'C7': ('bosco', 'Lessinia'),
 'A68': (None, 'Lessinia'),
}
# eventi fuori estensione o lontani: solo archivio, con territorio dichiarato
TERR_ONLY = {'A18': 'esterno (Valsugana)', 'A19': 'esterno (Val di Fassa)', 'A28': 'esterno (Col Visentin)', 'D25': 'esterno (Grappa)',
             'D26': 'esterno (Dolomiti Bellunesi)', 'C36': 'limitrofo (Verona, Montorio)', 'C37': 'Lessinia', 'C38': 'esterno (pianura, A22 Vigasio)',
             'C19': 'limitrofo (Monte Baldo)', 'B18': 'limitrofo (Pasubio)', 'B58': 'limitrofo (Rovereto)', 'C6': 'limitrofo (Verona)',
             'C8': 'limitrofo (Verona)', 'C9': 'limitrofo (Verona)'}

# correzioni puntuali emerse dal confronto tra fonti
PATCH = {
 'C26': {'localita': 'SS12 tra Dolcè e Peri', 'note_extra': 'Il toponimo "Val Vergnana" indicato nell\'elenco di partenza non compare in nessuna fonte consultata: non è usato.'},
 'A50': {'categoria': 'osservazione', 'sottotipo': 'mancato rilevamento', 'note_extra': 'Classificato come osservazione (mancato rilevamento): la morte di Giulietta non è accertata.'},
 'C39': {'categoria': 'interazione', 'sottotipo': 'sospetto avvelenamento (esche)', 'note_extra': 'Nessun lupo rinvenuto morto in questo episodio. Nessuna fonte consultata collega l\'episodio a Malga Rambalda: l\'associazione con Rambalda nell\'elenco di partenza resta non verificata.'},
 'A0': {'note_extra': 'Menini (2015) colloca le tracce appaiate presso Tracchi / Bocca di Selva; Lessinia Bolf indica Malera. Punto posto a Malera, con incertezza.'},
}

# ---------------------------------------------------------------- 4. eventi aggiunti da lettura diretta di fonti (non dalle ricerche automatiche)
EXTRA = [
 dict(_src='X1', titolo='Tesi Tabarelli: le 13 malghe con almeno 10 eventi di predazione su bovini (2012–2024)', categoria='predazione', sottotipo='predazione bovini',
      descrizione='Analisi del dataset MUSE–PAT–Parco–Regione Veneto: 94 malghe interessate da predazioni nel 2012–2024 (82 in provincia di Verona, 12 di Trento). Le cinque con più eventi sono Podesteria, Scortigara di Fondo, Lago Boaro, Scortigara di Cima e Scortigara di Mezzo. Le serie annuali per malga sono nel livello "Eventi di predazione per malga".',
      data_evento='2012', data_fine='2024', localita=None, comune=None, provincia=None, precisione='area', specie_coinvolte=['lupo', 'bovini'],
      tipo_evidenza='tesi di laurea (dataset istituzionale)', stato='accertato',
      fonti=[dict(titolo='Malghe e lupi in Lessinia: mappatura del territorio e conflitti tra conservazione faunistica e allevamento', editore='Università di Padova (Tabarelli de Fatis K., rel. A. A. Pilastro)', url='https://thesis.unipd.it/handle/20.500.12608/89085', data_pubblicazione='2025-07-22')],
      note='Valori annuali letti dai grafici A1–A13 della tesi (pp. 34–40). Le serie differiscono in alcuni anni da quelle del rapporto MUSE–PAT 2023 per le malghe trentine.'),
]

# ---------------------------------------------------------------- build
RANK = {'accertato': 3, 'documentato': 2, 'segnalato': 1, 'smentito': 0}
def norm(s): return unicodedata.normalize('NFD', s or '').encode('ascii', 'ignore').decode().lower()
merged = {}
absorbed = set()
for g in MERGE:
    p = dict(BY[g[0]]); fonti = list(p.get('fonti', [])); notes = [p.get('note') or '']; sp = set(p.get('specie_coinvolte') or [])
    for o in g[1:]:
        e = BY[o]; absorbed.add(o)
        for f in e.get('fonti', []):
            if f.get('url') not in [x.get('url') for x in fonti]: fonti.append(f)
        if e.get('note') and e['note'] not in notes: notes.append(e['note'])
        sp |= set(e.get('specie_coinvolte') or [])
        if RANK.get(e.get('stato'), 0) > RANK.get(p.get('stato'), 0) and e.get('tipo_evidenza') not in ('dichiarazione di parte',):
            p['stato'] = e['stato']; p['tipo_evidenza'] = e.get('tipo_evidenza')
        for k in ('localita', 'comune', 'provincia'):
            if not p.get(k) and e.get(k): p[k] = e[k]
    p['fonti'] = fonti; p['note'] = ' | '.join(n for n in notes if n); p['specie_coinvolte'] = sorted(sp); p['_merged'] = g
    merged[g[0]] = p
events = []
for e in RAW + EXTRA:
    s = e['_src']
    if s in absorbed or s in DROP: continue
    events.append(merged.get(s, dict(e)))

def comune_point(name):
    for f in COM:
        if norm(f['properties']['comune']) == norm(name):
            g = shape(f['geometry']); p = g.representative_point()
            return round(p.x, 5), round(p.y, 5), f['properties']['sigla']
    return None
CAT_OK = {'osservazione', 'riproduzione', 'mortalita', 'predazione', 'interazione', 'prevenzione', 'decisione'}
feats, archive = [], []
events.sort(key=lambda e: (str(e.get('data_evento')), e['_src']))
for i, e in enumerate(events, 1):
    s = e['_src']; e = dict(e)
    if s in PATCH:
        pt = PATCH[s]; e.update({k: v for k, v in pt.items() if k != 'note_extra'})
        if 'note_extra' in pt: e['note'] = ((e.get('note') or '') + ' | ' + pt['note_extra']).strip(' |')
    assert e['categoria'] in CAT_OK, (s, e['categoria'])
    d = str(e.get('data_evento') or '')
    anno = int(d[:4]); anno_fine = int(str(e.get('data_fine') or d)[:4])
    rec = {
        'id': f'EV{i:03d}', 'titolo': e['titolo'], 'categoria': e['categoria'], 'sottotipo': e.get('sottotipo'),
        'descrizione': e.get('descrizione'), 'data_evento': d, 'data_fine': e.get('data_fine'), 'anno': anno, 'anno_fine': max(anno, anno_fine),
        'localita': e.get('localita'), 'comune': e.get('comune'), 'provincia': e.get('provincia'),
        'specie': e.get('specie_coinvolte') or [], 'tipo_evidenza': e.get('tipo_evidenza'), 'stato': e.get('stato'),
        'fonti': [{'titolo': f.get('titolo'), 'editore': f.get('editore'), 'url': f.get('url'), 'data': f.get('data_pubblicazione')} for f in e.get('fonti', [])],
        'note': e.get('note') or None, 'rif_ricerca': [s] + e.get('_merged', [s])[1:],
    }
    loc, terr = LOC.get(s, (None, 'Lessinia'))
    if s in TERR_ONLY: loc, terr = None, TERR_ONLY[s]
    rec['territorio'] = terr
    geom = None
    if loc in L:
        lon, lat, osm, lab = L[loc]; rec['precisione'] = 'località'; rec['precisione_nota'] = lab; rec['osm'] = osm; geom = [lon, lat]
    elif loc == 'comune' and e.get('comune'):
        cp = comune_point(e['comune'].split(';')[0].split('/')[0].strip())
        if cp:
            rec['precisione'] = 'comune'; rec['precisione_nota'] = f"punto rappresentativo del comune di {e['comune']} (ISTAT): la fonte non indica un luogo più preciso"
            geom = [cp[0], cp[1]]
    if geom and not (EXT[0] < geom[0] < EXT[2] and EXT[1] < geom[1] < EXT[3]): geom = None
    if not geom:
        rec['precisione'] = 'non localizzata'
        rec['precisione_nota'] = {'area': 'la fonte indica solo un\'area (es. Lessinia orientale) o un dato aggregato', 'non localizzabile': 'nessun luogo indicato'}.get(e.get('precisione'), 'luogo non localizzabile con sicurezza o fuori dall\'estensione dell\'atlante')
        if e['categoria'] == 'riproduzione': rec['precisione_nota'] += '; i siti riproduttivi non sono mai mappati'
    rec['in_mappa'] = bool(geom)
    archive.append(rec)
    if geom: feats.append({'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': geom}, 'properties': rec})

# relazioni puntuali (catene documentate) e tematiche ------------------------------------------------
idx = {s: r['id'] for r in archive for s in r['rif_ricerca']}
CATENE = [
 dict(id='C-SLAVC', titolo='Slavc e Giulietta: dalla dispersione alla prima cucciolata', tipo='storico', eventi=['D0', 'D1', 'A0', 'D3', 'D7', 'D8', 'D9', 'D11', 'D13']),
 dict(id='C-FONDATORI', titolo='Fine del branco storico', tipo='storico', eventi=['A50', 'A51', 'A52', 'C46']),
 dict(id='C-VENTO', titolo='Il lupo "Vento": recupero, rilascio e morte', tipo='storico', eventi=['C36', 'C37']),
 dict(id='C-BOLDERA23', titolo='Boldera 2023: predazioni, decreto, ricorsi', tipo='istituzionale', eventi=['B30', 'B31', 'B32', 'B33', 'B34', 'B35', 'B36']),
 dict(id='C-BOLDERA25', titolo='Boldera 2025–2026: predazioni, decreto, abbattimento, sentenze', tipo='istituzionale', eventi=['B45', 'B46', 'B47', 'B48', 'B49', 'A70', 'B50', 'B51', 'D48', 'B59', 'B55']),
 dict(id='C-PREV-BOLDERA', titolo='Malga Boldera: recinzione e sua manutenzione', tipo='tematico', eventi=['B15', 'B37', 'B53']),
 dict(id='C-AVIO25', titolo='Avio 2025: episodi attribuiti allo stesso branco dalla Provincia', tipo='geografico', eventi=['B41', 'B42', 'B43', 'B44']),
 dict(id='C-FOSSE', titolo='Fosse: due lupi morti per cause illegali a dodici anni di distanza', tipo='geografico', eventi=['A3', 'C42']),
 dict(id='C-TOSI', titolo='Ordinanza di Verona del 2014 e sospensione del TAR', tipo='istituzionale', eventi=['C6', 'C8', 'C9']),
 dict(id='C-DEROGA-VR', titolo='Richieste di deroga dalla Lessinia veronese', tipo='istituzionale', eventi=['C58', 'C59', 'C62', 'C65']),
 dict(id='C-PROTESTA16', titolo='Settembre 2016: predazione a Velo e proteste con la carcassa', tipo='storico', eventi=['A22', 'A23', 'A24']),
]
for c in CATENE:
    c['eventi'] = [idx[s] for s in c['eventi'] if s in idx]
REL = [
 dict(id='R1', titolo='Il ritorno del lupo', tipo='storico', descrizione='Osservazioni e riproduzioni dal 2012 al 2014: arrivo di Slavc, incontro con Giulietta, prime cucciolate.',
      regola=lambda r: r['anno'] <= 2014 and r['categoria'] in ('osservazione', 'riproduzione')),
 dict(id='R2', titolo='La mortalità antropica', tipo='tematico', descrizione='Lupi morti per cause umane: investimenti stradali e ferroviari, bracconaggio, avvelenamento, abbattimenti autorizzati. Le morti per cause naturali (rogna, cimurro) sono distinte.',
      regola=lambda r: r['categoria'] == 'mortalita'),
 dict(id='R3', titolo='Il conflitto pastorale', tipo='tematico', descrizione='Predazioni su bestiame, interazioni con cani e abitati, misure di prevenzione.',
      regola=lambda r: r['categoria'] in ('predazione', 'prevenzione', 'interazione')),
 dict(id='R4', titolo='L\'evoluzione della presenza', tipo='ecologico', descrizione='Dal branco storico ai nuovi gruppi riproduttivi: riproduzioni, monitoraggi, dispersioni documentate geneticamente, scomparse.',
      regola=lambda r: r['categoria'] in ('riproduzione',) or (r['categoria'] == 'osservazione' and r['anno'] >= 2015)),
 dict(id='R5', titolo='La gestione istituzionale', tipo='istituzionale', descrizione='Provvedimenti, sentenze, finanziamenti, tavoli e iniziative delle amministrazioni e delle associazioni.',
      regola=lambda r: r['categoria'] == 'decisione'),
]
for r in archive:
    r['relazioni'] = [x['id'] for x in REL if x['regola'](r)]
    r['catene'] = [c['id'] for c in CATENE if r['id'] in c['eventi']]
for f in feats:  # le feature condividono gli oggetti
    pass
rel_out = {'nota': 'Le relazioni sono collegamenti documentali tra eventi, non percorsi compiuti da animali.',
           'tematiche': [{k: v for k, v in x.items() if k != 'regola'} | {'eventi': [r['id'] for r in archive if x['id'] in r['relazioni']]} for x in REL],
           'catene': CATENE}
# causa di morte (per distinguere nella relazione R2)
def causa(r):
    t = norm((r.get('sottotipo') or '') + ' ' + r['titolo'] + ' ' + (r.get('descrizione') or ''))
    if 'treno' in t or 'ferrov' in t: return 'investimento ferroviario'
    if 'investit' in t or 'stradal' in t or 'camion' in t or 'ambulanza' in t: return 'investimento stradale'
    if 'abbatt' in t and 'autorizz' in t or 'decreto' in t and 'abbattut' in t: return 'abbattimento autorizzato'
    if 'fucil' in t or 'pallettoni' in t or 'arma da fuoco' in t or 'sparat' in t: return 'bracconaggio (arma da fuoco)'
    if 'avvelen' in t: return 'avvelenamento (sospetto o accertato)'
    if 'rogna' in t or 'cimurro' in t: return 'causa naturale (malattia)'
    return 'causa non determinata'
for r in archive:
    if r['categoria'] == 'mortalita': r['causa'] = causa(r)

json.dump({'type': 'FeatureCollection', 'features': feats}, open(os.path.join(OUT, 'tema_eventi.geojson'), 'w'), ensure_ascii=False)
json.dump({'generato': '2026-10-10', 'nota': 'Archivio completo, inclusi eventi non localizzati.', 'eventi': archive}, open(os.path.join(OUT, 'tema_eventi_archivio.json'), 'w'), ensure_ascii=False, indent=0)
json.dump(rel_out, open(os.path.join(OUT, 'tema_relazioni.json'), 'w'), ensure_ascii=False, indent=1)
import collections
print('eventi', len(archive), 'in mappa', len(feats))
print(collections.Counter(r['categoria'] for r in archive)); print(collections.Counter(r['stato'] for r in archive)); print(collections.Counter(r['precisione'] for r in archive))
print(collections.Counter(r.get('causa') for r in archive if r.get('causa')))
print('senza loc ma con localita:', [(r['id'], r['rif_ricerca'][0], r['localita'], r['comune']) for r in archive if not r['in_mappa'] and r['localita']])
