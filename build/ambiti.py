"""
AMBITI DIPLOMATICI — ipotesi progettuali della Diplomazia Multispecie della Lessinia.
Non sono confini ecologici: ogni ambito deriva da eventi dell'archivio (tema_eventi_archivio.json) e usa geometrie reali:
  comuni ISTAT 2026, perimetro del Parco (EEA NatDA), poligoni di prateria OSM attorno alle malghe coinvolte.
Output: app/data/tema_ambiti_diplomatici.geojson (+ ambiti senza geometria in properties 'cartografato': false)
"""
import json, os
from shapely.geometry import shape, mapping, Point
from shapely.ops import unary_union, transform
from pyproj import Transformer
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'dist', 'data'); A = os.path.join(ROOT, 'app', 'data')
arch = json.load(open(os.path.join(A, 'tema_eventi_archivio.json')))['eventi']
SRC = {s: r for r in arch for s in r['rif_ricerca']}
com = {f['properties']['comune']: shape(f['geometry']) for f in json.load(open(os.path.join(D, 'confini_comuni.geojson')))['features']}
parco = [shape(f['geometry']) for f in json.load(open(os.path.join(D, 'aree_protette_natda.geojson')))['features'] if f['properties']['codice_euap'] == 'EUAP0241'][0]
prat = [shape(f['geometry']) for f in json.load(open(os.path.join(D, 'osm_copertura_aperta.geojson')))['features'] if f['properties']['classe'].startswith('prateria')]
to32 = Transformer.from_crs(4326, 32632, always_xy=True).transform; to4 = Transformer.from_crs(32632, 4326, always_xy=True).transform
prat32 = [transform(to32, g) for g in prat]
def pascoli(pts, r):
    """Praterie OSM entro r metri dalle malghe indicate (geometria reale di copertura, non il perimetro della malga)."""
    buf = unary_union([Point(transform(to32, Point(p))).buffer(r) for p in pts])
    sel = [g.intersection(buf) for g in prat32 if g.intersects(buf)]
    return transform(to4, unary_union(sel).simplify(4))
def comuni(*names): return unary_union([com[n] for n in names]).simplify(0.0001)

M = {'boldera': (10.97467, 45.68641), 'sc_fondo': (11.02534, 45.71246), 'sc_mezzo': (11.03211, 45.71291), 'sc_cima': (11.04520, 45.71306),
     'podesteria': (11.04703, 45.70093), 'lago_boaro': (11.02207, 45.69408), 'costeggioli': (11.02795, 45.69932), 'camporotondo': (11.03444, 45.67388),
     'pealda': (10.96255, 45.67787), 'rambalda': (10.97984, 45.67137), 'valbella': (10.99421, 45.68343), 'derocchetto': (11.00068, 45.67029)}
AMBITI = [
 dict(codice='OS-01', tipo='osservazione', nome='Altopiano dei Lessini: i luoghi del ritorno',
      geom=parco, geom_fonte='Perimetro del Parco Naturale Regionale della Lessinia (EEA NatDA v24)',
      localizzazione='Altopiano centrale e settentrionale; la dorsale di Revoltel è appena oltre il confine, versante trentino.',
      eventi=['D0', 'A1', 'A0', 'D3', 'D7', 'D8', 'D9', 'A7', 'A49', 'C31'],
      problematica='Le prime evidenze del ritorno (2012–2014) e le osservazioni successive sono disperse tra tesi, associazioni e rapporti di enti diversi.',
      soggetti='Lupo; Parco della Lessinia; Provincia di Trento; ricercatori; volontari del monitoraggio; escursionisti.',
      questione='Chi custodisce la memoria della presenza del lupo e con quali regole la rende pubblica senza esporre i siti sensibili?',
      attivita='Registro pubblico delle osservazioni con livelli di precisione dichiarati e protocollo condiviso tra Veneto e Trentino.'),
 dict(codice='OS-02', tipo='osservazione', nome='Evoluzione dei branchi (2013–2026)', geom=None,
      geom_fonte='Non cartografato: i siti riproduttivi non vengono pubblicati.',
      localizzazione='Lessinia veronese e trentina (branchi Lessinia, Lessinia Orientale, Foresta di Giazza, centro-meridionale).',
      eventi=['D11', 'D13', 'D15', 'D18', 'D24', 'A32', 'D28', 'D29', 'C29', 'A50', 'A51', 'A52', 'D38', 'C46', 'D49', 'A68'],
      problematica='Dati sui branchi discordanti tra fonti istituzionali e associative dopo il 2022; scomparsa del branco storico non spiegata.',
      soggetti='Lupo (branchi della Lessinia); Parco; Regione Veneto; Provincia di Trento; ISPRA; associazioni.',
      questione='Come rappresentare una popolazione che cambia senza trasformare stime incerte in fatti?',
      attivita='Bollettino annuale congiunto che distingua dati accertati, stime e segnalazioni.'),
 dict(codice='RA-01', tipo='rappresentanza', nome='Corridoio della Val d\'Adige',
      geom=comuni('Ala', 'Avio', 'Dolcè'), geom_fonte='Comuni di Ala, Avio e Dolcè (ISTAT 2026)',
      localizzazione='Fondovalle tra Rovereto e Dolcè: SS12, autostrada A22, ferrovia del Brennero.',
      eventi=['B20', 'B24', 'B29', 'C26', 'B43', 'B56', 'B57', 'B58'],
      problematica='Lupi investiti su strade e ferrovia nel fondovalle che separa Lessinia e Monte Baldo (2020–2026).',
      soggetti='Lupo in dispersione; gestori di strade e ferrovia; Comuni; automobilisti.',
      questione='Rappresentare il bisogno di attraversare il fondovalle in sicurezza presso chi progetta e gestisce le infrastrutture.',
      attivita='Mappatura dei punti di investimento e proposta di misure di mitigazione ai gestori di SS12, A22 e linea ferroviaria.'),
 dict(codice='RA-02', tipo='rappresentanza', nome='Fosse e Sant\'Anna d\'Alfaedo',
      geom=comuni("Sant'Anna d'Alfaedo"), geom_fonte='Comune di Sant\'Anna d\'Alfaedo (ISTAT 2026)',
      localizzazione='Lessinia occidentale: Fosse, Barozze, Semalo.',
      eventi=['A3', 'A40', 'C42', 'C55'],
      problematica='Una lupa avvelenata (2012), una giovane lupa trovata morta (2020), un lupo ucciso con arma da fuoco (2024) e predazioni vicino alle case (2025).',
      soggetti='Lupo; residenti; allevatori; Carabinieri forestali; IZSVe; Procura.',
      questione='Dare voce alla vulnerabilità della specie dove mortalità illegale e conflitto si sovrappongono.',
      attivita='Richiesta di accesso agli esiti delle necroscopie e incontro pubblico con allevatori e forze dell\'ordine.'),
 dict(codice='RA-03', tipo='rappresentanza', nome='Valli meridionali: bracconaggio e veleni',
      geom=comuni('Roverè Veronese', 'Cerro Veronese', 'Grezzana'), geom_fonte='Comuni di Roverè Veronese, Cerro Veronese e Grezzana (ISTAT 2026)',
      localizzazione='San Rocco di Piegara; area tra Cerro Veronese e Romagnano.',
      eventi=['C18', 'C64', 'C39'],
      problematica='Lupo ucciso a fucilate (2018) e lupo trovato morto con sospetto avvelenamento (2026); esche sospette segnalate nel Parco (2023).',
      soggetti='Lupo; altri animali esposti alle esche (corvi imperiali, cani); Carabinieri forestali; nuclei cinofili antiveleno.',
      questione='Le esche avvelenate colpiscono più specie: la tutela del lupo coincide qui con quella di altri animali e dei cani domestici.',
      attivita='Campagna informativa con i Comuni e richiesta di controlli cinofili antiveleno programmati.'),
 dict(codice='ME-01', tipo='mediazione', nome='Pascoli della Lessinia trentina: Scortigara e Boldera',
      geom=pascoli([M['boldera'], M['sc_fondo'], M['sc_mezzo'], M['sc_cima']], 900), geom_fonte='Praterie OSM entro 900 m dalle quattro malghe (copertura del suolo, non perimetro dell\'alpeggio)',
      localizzazione='Comune di Ala, tra Passo delle Fittanze e Monte Castelberto.',
      eventi=['X1', 'D32', 'B14', 'B30', 'B31', 'B45', 'B46'],
      problematica='Quattro malghe a impatto cronico (MUSE–PAT): 103 eventi su bovini 2012–2024 (Tabarelli); nelle Scortigara nessuna misura di prevenzione registrata nel 2021.',
      soggetti='Lupo; bovini (manze, vitelli); allevatori della Società allevatori di Ala; Comune di Ala; Servizio Foreste PAT.',
      questione='Conciliare l\'uso estivo dei pascoli con la presenza stabile di un branco.',
      attivita='Tavolo di malga con allevatori e tecnici: prevenzione sulle Scortigara, ricovero notturno dei vitelli, verifica condivisa delle recinzioni.'),
 dict(codice='ME-02', tipo='mediazione', nome='Pascoli dell\'altopiano centrale',
      geom=pascoli([M['podesteria'], M['lago_boaro'], M['costeggioli'], M['camporotondo']], 900), geom_fonte='Praterie OSM entro 900 m da Podesteria, Lago Boaro, Costeggioli di Sotto e Camporotondo',
      localizzazione='Bosco Chiesanuova, dentro il Parco.',
      eventi=['X1', 'C34'],
      problematica='Podesteria (40) e Lago Boaro (35) sono le malghe veronesi con più eventi su bovini 2012–2024; Lago Boaro cresce dal 2021.',
      soggetti='Lupo; bovini; gestori delle malghe; Parco della Lessinia; Comune di Bosco Chiesanuova.',
      questione='Il conflitto si concentra in poche malghe: la mediazione può essere mirata.',
      attivita='Sperimentazione di prevenzione su due malghe pilota con monitoraggio dei risultati.'),
 dict(codice='ME-03', tipo='mediazione', nome='Contrade e paesi della Lessinia orientale',
      geom=comuni('Velo Veronese', 'Badia Calavena', 'Selva di Progno', 'Crespadoro'), geom_fonte='Comuni di Velo Veronese, Badia Calavena, Selva di Progno e Crespadoro (ISTAT 2026)',
      localizzazione='Tecchie, Stander, Vazzo, centro di Badia Calavena, Campodalbero e Durlo.',
      eventi=['A22', 'A23', 'A37', 'C22', 'C41', 'C44', 'C50', 'C66', 'C68'],
      problematica='Predazioni e lupi osservati a poca distanza dalle case, cani uccisi, proteste pubbliche (2016–2026).',
      soggetti='Lupo; residenti; piccoli allevatori di ovicaprini; cani domestici; Comuni.',
      questione='La paura e il danno vicino alle case chiedono risposte diverse da quelle per i pascoli d\'alta quota.',
      attivita='Sportello di ascolto nelle contrade, sopralluoghi tecnici e kit di prevenzione per piccoli allevamenti.'),
 dict(codice='ME-04', tipo='mediazione', nome='Erbezzo: Pealda, Rambalda, Valbella',
      geom=pascoli([M['pealda'], M['rambalda'], M['valbella']], 900), geom_fonte='Praterie OSM entro 900 m da Pealda Bassa, Rambalda e Valbella',
      localizzazione='Comune di Erbezzo, sotto la dorsale Fittanze–Corno d\'Aquilio.',
      eventi=['D4', 'C43', 'C58', 'C59'],
      problematica='Prime predazioni (2012), 10 eventi a Pealda Bassa nel 2022, cane ucciso a Staffor (2024), richieste di abbattimento per Rambalda (2025).',
      soggetti='Lupo; bovini; allevatori; Comune di Erbezzo; Regione Veneto; associazioni.',
      questione='Le richieste di deroga partono da una malga che, secondo un\'associazione, non aveva recinzioni: il dato va verificato prima di negoziare.',
      attivita='Verifica indipendente delle misure presenti e accompagnamento alla prevenzione prima di ogni richiesta di deroga.'),
 dict(codice='NE-01', tipo='negoziazione', nome='Malga Boldera: deroga e prevenzione',
      geom=pascoli([M['boldera']], 700), geom_fonte='Praterie OSM entro 700 m da Malga Boldera',
      localizzazione='Ala (TN), a nord del Passo delle Fittanze.',
      eventi=['B15', 'B30', 'B32', 'B33', 'B34', 'B36', 'B37', 'B45', 'B46', 'B47', 'B48', 'B49', 'B50', 'B51', 'B53', 'B59'],
      problematica='Predazioni dentro la recinzione elettrificata, due decreti di rimozione (2023, 2025), un lupo abbattuto, contenzioso fino al Consiglio di Stato (2026).',
      soggetti='Lupo; bovini; allevatori; Provincia di Trento; ISPRA; TAR e Consiglio di Stato; LAV, ENPA e altre associazioni.',
      questione='Il primo abbattimento gestionale in Trentino: quali condizioni di prevenzione devono essere dimostrate prima di una deroga?',
      attivita='Protocollo pubblico di verifica delle recinzioni (tensione, distanza tra fili, manutenzione) concordato tra Provincia, allevatori e associazioni.'),
 dict(codice='NE-02', tipo='negoziazione', nome='Tavolo veronese: deroghe e progetto Heimat',
      geom=comuni('Erbezzo', 'Bosco Chiesanuova'), geom_fonte='Comuni di Erbezzo e Bosco Chiesanuova (ISTAT 2026)',
      localizzazione='Bosco Chiesanuova (incontri istituzionali) ed Erbezzo (richieste di deroga).',
      eventi=['C47', 'C51', 'C53', 'C56', 'C58', 'C62', 'C65', 'C67'],
      problematica='Mozione regionale sul contenimento (2025), richieste di deroga respinte (2026), progetto "Heimat, lupo e malghe" finanziato dalla Regione.',
      soggetti='Regione Veneto; Comuni; Coldiretti e altre associazioni agricole; associazioni ambientaliste; Parco.',
      questione='Spostare la discussione dalla deroga alle condizioni di coesistenza finanziabili.',
      attivita='Proposta di tavolo permanente con rappresentanza esplicita degli interessi ecologici del lupo.'),
 dict(codice='NE-03', tipo='negoziazione', nome='Malga Derocchetto: cani da guardiania',
      geom=pascoli([M['derocchetto']], 600), geom_fonte='Praterie OSM entro 600 m da Malga Derocchetto',
      localizzazione='Erbezzo / Bosco Chiesanuova, altopiano centrale.',
      eventi=['C27'],
      problematica='Esperienza documentata di cani da guardiania senza predazioni (2021).',
      soggetti='Lupo; ovicaprini; pastori; cani da guardiania; escursionisti.',
      questione='Una pratica che funziona può diventare oggetto di accordo e di sostegno pubblico?',
      attivita='Scheda di buona pratica e visita di scambio tra allevatori.'),
]
feats, out = [], []
for a in AMBITI:
    evs = [SRC[s] for s in a['eventi'] if s in SRC]
    missing = [s for s in a['eventi'] if s not in SRC]
    if missing: print('manca', a['codice'], missing)
    fonti = []
    for r in evs:
        for f in r['fonti']:
            if f['url'] not in [x['url'] for x in fonti]: fonti.append(f)
    props = {k: v for k, v in a.items() if k not in ('geom', 'eventi')}
    props.update(eventi=[r['id'] for r in evs], n_eventi=len(evs), anni=f"{min(r['anno'] for r in evs)}–{max(r['anno_fine'] for r in evs)}",
                 fonti=fonti[:12], n_fonti=len(fonti), stato='ipotesi progettuale', cartografato=a['geom'] is not None)
    g = a['geom']
    if g is not None:
        big = max(g.geoms, key=lambda x: x.area) if g.geom_type == 'MultiPolygon' else g
        lp = big.representative_point(); props['label_lon'] = round(lp.x, 5); props['label_lat'] = round(lp.y, 5)
    feats.append({'type': 'Feature', 'geometry': mapping(g) if g is not None else None, 'properties': props})
def rnd(o):
    if isinstance(o, float): return round(o, 5)
    if isinstance(o, (list, tuple)): return [rnd(x) for x in o]
    if isinstance(o, dict): return {k: rnd(v) for k, v in o.items()}
    return o
json.dump(rnd({'type': 'FeatureCollection', 'features': feats}), open(os.path.join(A, 'tema_ambiti_diplomatici.geojson'), 'w'), ensure_ascii=False)
print(len(feats), [(f['properties']['codice'], f['properties']['n_eventi'], f['geometry']['type'] if f['geometry'] else None) for f in feats])
print(os.path.getsize(os.path.join(A, 'tema_ambiti_diplomatici.geojson')))
