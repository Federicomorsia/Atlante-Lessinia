"""
Dati tematici dell'Atlante della Lessinia, compilati a mano da fonti verificate.
Ogni feature porta:
  - stato: 'verificato' | 'osservazione' | 'interpretazione' | 'ipotesi'
  - fonti: lista di id del registro fonti (fonti.json)
  - precisione: come è stata ottenuta la coordinata
Le coordinate provengono da OpenStreetMap (id dell'oggetto indicato) estratte via Overpass il 10/10/2026.
"""
import json, os
OUT = os.path.join(os.path.dirname(__file__), '..', 'app', 'data')
os.makedirs(OUT, exist_ok=True)
CONSULT = '2026-10-10'

FONTI = [
 dict(id='ISTAT2026', titolo='Confini delle unità amministrative a fini statistici al 1° gennaio 2026 (versione non generalizzata)', autore='ISTAT', anno=2026, tipo='Dataset ufficiale', url='https://www.istat.it/notizia/confini-delle-unita-amministrative-a-fini-statistici-al-1-gennaio-2018-2/', licenza='CC BY 3.0 IT', note='Shapefile EPSG:32632. Geometrie semplificate a 2 m per il web (tolleranza Douglas-Peucker).'),
 dict(id='EEA_N2000', titolo='Natura 2000 – End 2024 (servizio ArcGIS ProtectedSites/Natura2000Sites)', autore='European Environment Agency', anno=2024, tipo='Dataset ufficiale', url='https://bio.discomap.eea.europa.eu/arcgis/rest/services/ProtectedSites/Natura2000Sites/MapServer', licenza='Riutilizzo EEA (attribuzione)', note='Perimetri trasmessi dagli Stati membri. Semplificati a 2 m.'),
 dict(id='EEA_NATDA', titolo='Nationally designated areas (NatDA/CDDA) v24, layer large scale', autore='European Environment Agency (dati comunicati da MASE, Elenco Ufficiale Aree Protette)', anno=2024, tipo='Dataset ufficiale', url='https://bio.discomap.eea.europa.eu/arcgis/rest/services/ProtectedSites/NatDAv24_Dyna_WM/MapServer', licenza='Riutilizzo EEA (attribuzione)', note='Fonte del perimetro del Parco Naturale Regionale della Lessinia (EUAP0241, 10.333 ha dichiarati). Non è il file di perimetrazione regionale: da confrontare con la cartografia della Regione Veneto.'),
 dict(id='TINITALY', titolo='TINITALY, a digital elevation model of Italy with a 10 meters cell size (Version 1.1)', autore='Tarquini S., Isola I., Favalli M., Battistini A., Dotta G. – INGV', anno=2023, tipo='Modello digitale del terreno', url='https://doi.org/10.13127/tinitaly/1.1', licenza='CC BY 4.0', note='DTM 10 m. Curve di livello ricavate su griglia 20 m con lieve smoothing gaussiano: adatte alla lettura del rilievo, non a misure topografiche.'),
 dict(id='OSM', titolo='OpenStreetMap, estrazione Overpass API', autore='OpenStreetMap contributors', anno=2026, tipo='Base dati collaborativa', url='https://www.openstreetmap.org/copyright', licenza='ODbL 1.0', note='Idrografia, boschi, praterie, viabilità, sentieri, toponimi, edifici delle malghe. Completezza e accuratezza variabili.'),
 dict(id='MUSE2023', titolo='Predazioni da lupo sul bestiame domestico in provincia di Trento: analisi delle dinamiche e delle strategie di prevenzione', autore='Bombieri G., Roseo F., Bragalanti N., Zanghellini P., Zeni M., Groff C., Pedrini P. (MUSE – PAT)', anno=2023, tipo='Relazione tecnica', url='https://www.muse.it/contrib/uploads/2023/08/lupo_danni_09_08_2023-1.pdf', licenza='—', note='Tabelle 4 e 5: eventi di predazione e capi per malga, 2013–2022. Malga "a impatto cronico" = almeno 5 eventi nel periodo.'),
 dict(id='PAT2022', titolo='Lo status del lupo in provincia di Trento (2020-2021)', autore='Bombieri G., Ferraro E., Oberosler V., Pedrini P., Pedrotti L.', anno=2022, tipo='Relazione tecnica (in Marucco et al. 2022, LIFE WolfAlps EU / ISPRA)', url='https://www.lifewolfalps.eu/wp-content/uploads/2022/07/Report-Lupo_PAT_2020_21.pdf', licenza='—', note='Box 1 p. 6: campioni genetici in loc. Revoltel (30/10/2012) e prima foto della coppia (04/12/2012). Tab. 1: cuccioli minimi accertati 2013–2021.'),
 dict(id='RAZEN2016', titolo='Long-distance dispersal connects Dinaric-Balkan and Alpine grey wolf (Canis lupus) populations', autore='Ražen N., Brugnoli A., Castagna C., Groff C., Kaczensky P., Kljun F. et al.', anno=2016, tipo='Articolo scientifico (Eur J Wildl Res 62:137–142)', url='https://doi.org/10.1007/s10344-015-0971-z', licenza='—', note='Dispersione di Slavc: 98 giorni, 1.176 km; insediamento nelle Alpi italiane a marzo 2012; prima cucciolata 2013.'),
 dict(id='MENINI2015', titolo='Il ripopolamento naturale del lupo in Lessinia', autore='Menini G. (Università di Padova, rel. A. Zanella)', anno=2015, tipo='Tesi di laurea', url='https://thesis.unipd.it/retrieve/b5dc3770-816f-440b-b971-54dfab6e31a0/Menini_Giacomo.pdf', licenza='—', note='Cronologia 2011–2014 (fototrappole, avvistamenti, rilascio del collare a Podestaria).'),
 dict(id='PARCO2023', titolo='Comunicato stampa: monitoraggio lupi 2022 nella Lessinia veronese', autore='Parco Naturale Regionale della Lessinia', anno=2023, tipo='Comunicato istituzionale', url='https://lessiniapark.it/wp-content/uploads/2023/01/COMUNICATO-STAMPA-MONITORAGGIO-LUPI-2022-LESSINIA-VERONESE-25.01.2022.pdf', licenza='—', note='Tre branchi, 31 lupi; 134 eventi di predazione e 185 capi nella Lessinia veronese nel 2022; ripartizione per comune parziale.'),
 dict(id='TABARELLI2024', titolo='Malghe e lupi in Lessinia: mappatura del territorio e conflitti tra conservazione faunistica e allevamento', autore='Tabarelli de Fatis K. (Università di Padova, rel. A. A. Pilastro)', anno=2024, tipo='Tesi di laurea triennale', url='https://thesis.unipd.it/handle/20.500.12608/89085', licenza='—', note='Dataset di eventi di predazione confermati 2012–2024. Testo integrale non consultato: dati non integrati.'),
 dict(id='ILDOLOMITI2025', titolo='Lupi, Fugatti firma il decreto per l\'abbattimento di due esemplari in Lessinia. Ispra: il prelievo non assicura l\'azzeramento del rischio', autore='il Dolomiti', anno=2025, tipo='Stampa (riporta parere ISPRA)', url='https://www.ildolomiti.it/cronaca/2025/lupi-fugatti-firma-il-decreto-per-labbattimento-di-due-esemplari-in-lessinia-ispra-il-prelievo-non-assicura-lazzeramento-del-rischio-di-ulteriori-predazioni', licenza='—', note='Fonte secondaria. Lessinia trentina 2013–2025: 136 eventi, 143 capi uccisi; Malga Boldera 2015–2025: 21 eventi, 27 capi uccisi.'),
 dict(id='ILDOLOMITI2023', titolo='Dopo gli orsi Fugatti dà l\'ok anche all\'abbattimento dei lupi', autore='il Dolomiti', anno=2023, tipo='Stampa', url='https://www.ildolomiti.it/cronaca/2023/dopo-gli-orsi-fugatti-da-lok-anche-allabbattimento-dei-lupi-firmato-il-decreto-che-condanna-a-morte-due-esemplari', licenza='—', note='Fonte secondaria. Malga Boldera: proprietà del Comune di Ala, gestione Società allevatori di Ala; attacchi del 29/6 e 22/7/2023.'),
 dict(id='CDS2026', titolo='Lupo abbattuto in Lessinia, il Consiglio di Stato dà ragione alla Provincia', autore='il Dolomiti', anno=2026, tipo='Stampa', url='https://www.ildolomiti.it/cronaca/2026/lupo-abbattuto-in-lessinia-il-consiglio-di-stato-da-ragione-alla-provincia-decreto-legittimo', licenza='—', note='Fonte secondaria. Abbattimento di un lupo a Malga Boldera nella notte 19–20/9/2025.'),
 dict(id='VISITLESSINIA250', titolo='Itinerario n. 250 CAI – Dorsale Alta della Lessinia', autore='Visit Lessinia', anno=None, tipo='Scheda itinerario', url='https://www.visitlessinia.eu/en/itinerario-n-250-cai-dorsale-alta-della-lessinia-820', licenza='—', note='Giazza – Fosse/Peri, circa 40 km. In OSM: superroute 9333024.'),
 dict(id='VENETO_CONFINE', titolo='Cippi di confine del 1753 (Trattato di Rovereto)', autore='Regione del Veneto – Veneto Around Me', anno=None, tipo='Scheda istituzionale turistica', url='https://venetoaroundme.regione.veneto.it/en/node/104739', licenza='—', note='Congresso di Rovereto 1750, trattato 1753, cippi posati dal 1754.'),
 dict(id='DEBIASI', titolo='Malghe di Ala e Avio', autore='Debiasi B., associazione Quei de Fopiano', anno=None, tipo='Ricerca storica locale', url='https://www.fondazionemcr.it/UploadDocs/23074_Malghe_di_Ala_e_Avio_di_Barbara_Debiasi_associazione_Quei_de_Fopiam.pdf', licenza='—', note='Quote e storia delle malghe di Ala.'),
 dict(id='VENETO_PARCO', titolo='Parco Naturale Regionale della Lessinia (L.R. 30 gennaio 1990, n. 12)', autore='Regione del Veneto', anno=1990, tipo='Norma / scheda istituzionale', url='https://www.regione.veneto.it/parco-lessinia', licenza='—', note='Sede: Piazza Borgo 52, Bosco Chiesanuova.'),
 dict(id='VENETO2020', titolo='Comunicato n. 475 del 30/03/2020: lupi in Veneto, dati 2018–2019', autore='Regione del Veneto', anno=2020, tipo='Comunicato istituzionale', url='https://www.regione.veneto.it/article-detail?articleId=4433056', licenza='—', note='Veneto 2019: 198 eventi, 425 capi uccisi.'),
]

def F(lon, lat, **p):
    return {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [lon, lat]}, 'properties': p}

# ------------------------------------------------------------------ LUOGHI DI INTERESSE
luoghi = [
 F(10.97467, 45.68641, id='boldera', nome='Malga Boldera', comune='Ala', provincia='TN', tipologia='Malga (alpeggio bovino)', quota_m=1402,
   descrizione='Malga di proprietà del Comune di Ala, gestita dalla Società allevatori di Ala, a nord del Passo delle Fittanze. Alpeggio di bovini, in prevalenza manze e vitelli.',
   rilevanza='Una delle quattro malghe di Ala classificate "a impatto cronico" (≥5 eventi 2013–2022). Recinzione elettrificata multifilo dal 2018; abbattimento di un lupo nel settembre 2025 su decreto provinciale.',
   periodo='2015–2025', stato='verificato', categoria='conflitto', osm='way/140264909',
   precisione='Edificio principale (OSM)', fonti=['MUSE2023','ILDOLOMITI2023','ILDOLOMITI2025','CDS2026','OSM']),
 F(11.03211, 45.71291, id='scortigara', nome='Malghe Scortigara (Fondo, Mezzo, Cima)', comune='Ala', provincia='TN', tipologia='Sistema di tre malghe', quota_m=1572,
   descrizione='Tre alpeggi bovini in sequenza altimetrica lungo il versante trentino, tra 1.520 e 1.590 m, immediatamente a nord del confine regionale. Il punto indica Scortigara di Mezzo.',
   rilevanza='Concentrano 77 dei 576 eventi di predazione registrati in provincia di Trento nel 2013–2022 (13%). Nessuna misura di prevenzione registrata nel 2021.',
   periodo='2013–2022', stato='verificato', categoria='conflitto', osm='way/121203030',
   precisione='Edificio di Scortigara di Mezzo (OSM)', fonti=['MUSE2023','OSM']),
 F(10.99727, 45.71148, id='revoltel', nome='Malga Revoltel', comune='Ala', provincia='TN', tipologia='Malga · luogo di osservazione storica', quota_m=1550,
   descrizione='Malga sulla dorsale tra Sega di Ala e Castelberto, attraversata dal sentiero CAI 250. Sul colle sono presenti trincee della Prima guerra mondiale.',
   rilevanza='Il 30 ottobre 2012 vi furono raccolti i campioni organici che diedero la prima conferma genetica della coppia Slavc–Giulietta; il 4 dicembre 2012 la prima fotografia della coppia (fototrappola). È un episodio datato: non indica una presenza stabile del lupo in questo punto.',
   periodo='Ottobre–dicembre 2012', stato='osservazione', categoria='lupo', osm='way/152088705',
   precisione='Edificio della malga (OSM); la località è citata come "loc. Revoltel"', fonti=['PAT2022','OSM']),
 F(10.97912, 45.68389, id='fittanze', nome='Passo delle Fittanze della Sega', comune='Erbezzo', provincia='VR', tipologia='Valico', quota_m=1399,
   descrizione='Valico stradale tra la Sega di Ala e l\'altopiano veronese. Secondo i confini ISTAT il punto del valico ricade in comune di Erbezzo, circa 180 m a sud del confine regionale. Da qui la dorsale sale verso Castelberto.',
   rilevanza='Punto in cui il confine amministrativo attuale, il confine storico veneto-austriaco (1753) e la continuità fisica dei pascoli d\'altopiano si sovrappongono.',
   periodo='Attuale', stato='verificato', categoria='confine', osm='node/1536873702',
   precisione='Nodo "saddle" OSM', fonti=['OSM','ISTAT2026','VENETO_CONFINE']),
 F(11.01696, 45.71894, id='castelberto', nome='Monte Castelberto', comune='Erbezzo', provincia='VR', tipologia='Vetta', quota_m=1765,
   descrizione='Culmine della dorsale nord-occidentale dell\'altopiano. La vetta OSM dista circa 30 m dal confine regionale ISTAT, sul lato veronese. Il sentiero CAI 250 ne percorre la cresta.',
   rilevanza='Lungo la cresta il confine regionale ricalca la linea fissata dal Trattato di Rovereto (1753) con cippi posati dal 1754; il pascolo prosegue senza interruzione su entrambi i versanti.',
   periodo='Attuale; confine storico dal 1753', stato='verificato', categoria='confine', osm='node/2411534673',
   precisione='Nodo "peak" OSM', fonti=['OSM','ISTAT2026','VENETO_CONFINE']),
 F(11.04703, 45.70093, id='podestaria', nome='Podestaria (rifugio e malga)', comune='Bosco Chiesanuova', provincia='VR', tipologia='Rifugio / malga', quota_m=1655,
   descrizione='Rifugio sulla dorsale alta, all\'interno del Parco, punto di passaggio del sentiero CAI 250.',
   rilevanza='Il 27 agosto 2012 il radiocollare GPS di Slavc si sganciò nei pressi di Podestaria dopo 407 giorni di tracciamento.',
   periodo='Agosto 2012', stato='osservazione', categoria='lupo', osm='way/143205782',
   precisione='Edificio del rifugio (OSM); la fonte indica "nei pressi"', fonti=['MENINI2015','OSM']),
 F(11.03, 45.672, id='folignani', nome='Foresta dei Folignani', comune='Bosco Chiesanuova / Erbezzo', provincia='VR', tipologia='Area forestale',
   descrizione='Formazione di conifere di origine antropica (rimboschimento) sull\'altopiano centrale, tra le malghe Folignano e il Branchetto. In OSM è mappata come multipoligono (relation 3253604).',
   rilevanza='Area forestale di interesse ambientale. Le fonti consultate non documentano un ruolo specifico per il lupo: la mappa non gliene attribuisce.',
   periodo='Attuale (copertura OSM)', stato='verificato', categoria='ambiente', osm='relation/3253604',
   precisione='Punto interno al poligono forestale OSM', fonti=['OSM']),
 F(11.02952, 45.6221, id='bosco', nome='Bosco Chiesanuova', comune='Bosco Chiesanuova', provincia='VR', tipologia='Centro abitato · sede del Parco',
   descrizione='Capoluogo della Lessinia centrale. In Piazza Borgo 52 ha sede l\'Ente Parco Naturale Regionale della Lessinia, istituito con L.R. Veneto 12/1990.',
   rilevanza='Riferimento istituzionale del progetto: sede dell\'ente che gestisce il Parco e coordina il monitoraggio del lupo nella Lessinia veronese.',
   periodo='Attuale', stato='verificato', categoria='istituzione', osm='node/64778814',
   precisione='Nodo del centro abitato (OSM); la sede non è geocodificata separatamente', fonti=['VENETO_PARCO','OSM']),
 F(10.97504, 45.69475, id='sega', nome='Sega di Ala', comune='Ala', provincia='TN', tipologia='Località', quota_m=1224,
   descrizione='Località d\'alpeggio sul versante trentino, accesso da Ala lungo la SP 211.',
   rilevanza='Porta trentina della dorsale; tappa del sentiero CAI 250.',
   periodo='Attuale', stato='verificato', categoria='territorio', osm='node/2477526670',
   precisione='Nodo "hamlet" OSM', fonti=['OSM','VISITLESSINIA250']),
]

# ------------------------------------------------------------------ CONFLITTI (malghe con dati per malga)
def conf(lon, lat, nome, osm, quota, anni, eventi, capi_comp, capi_ucc, prev, extra=None):
    p = dict(nome=nome, comune='Ala', provincia='TN', osm=osm, quota_m=quota, specie='Bovini',
             eventi_tot=eventi, capi_compromessi=capi_comp, capi_uccisi=capi_ucc,
             serie=anni, periodo='2013–2022', impatto='cronico (≥5 eventi 2013–2022)',
             prevenzione_2021=prev, stato='verificato', fonti=['MUSE2023'],
             nota='Eventi di predazione e capi coinvolti sono grandezze diverse: un evento può coinvolgere più capi.')
    if extra: p.update(extra)
    return F(lon, lat, **p)
Y = list(range(2013, 2023))
def serie(vals): return {str(y): v for y, v in zip(Y, vals)}
conflitti = [
 conf(10.97467, 45.68641, 'Malga Boldera', 'way/140264909', 1402, serie([0,0,2,2,1,4,0,0,0,2]), 11, 13, 12,
      'Recinzione elettrificata multifilo sull\'intero pascolo (dal 2018); nessun cane da guardiania',
      dict(aggiornamenti=[
        dict(periodo='2023', testo='Attacchi del 29 giugno e 22 luglio; 16 manze e 2 asini in meno di due mesi. Decreto di rimozione di 2 lupi (24/7/2023), non eseguito.', fonti=['ILDOLOMITI2023'], stato='fonte secondaria'),
        dict(periodo='2015–2025', testo='Parere ISPRA citato: 21 eventi su bovine, 27 capi uccisi e 10 feriti; nel 2025 distanza tra i fili 30–35 cm (ottimale 20 cm), installati 3 dissuasori acustici.', fonti=['ILDOLOMITI2025'], stato='fonte secondaria'),
        dict(periodo='Settembre 2025', testo='Un lupo abbattuto nella notte tra il 19 e il 20 settembre su decreto provinciale del 4/9/2025; il Consiglio di Stato ha ritenuto legittimo il decreto (31/7/2026).', fonti=['CDS2026'], stato='fonte secondaria')])),
 conf(11.02534, 45.71246, 'Malga Scortigara di Fondo', 'way/121202994', 1524, serie([0,4,3,7,5,6,0,2,6,6]), 39, 39, 34, 'Nessuna misura registrata'),
 conf(11.03211, 45.71291, 'Malga Scortigara di Mezzo', 'way/121203030', 1572, serie([2,0,1,2,2,1,1,0,6,5]), 20, 26, 24, 'Nessuna misura registrata',
      dict(nota_fonte='Nella Tab. 6 del rapporto (2020–2022) i valori per questa malga non coincidono con la Tab. 5: qui si usa la Tab. 5.')),
 conf(11.04520, 45.71306, 'Malga Scortigara di Cima', 'way/143205815', 1573, serie([0,0,1,1,1,0,1,1,9,4]), 18, 21, 16, 'Nessuna misura registrata'),
]

# ------------------------------------------------------------------ STATISTICHE AGGREGATE PER AREA (non puntuali)
aggregati = {
 'nota': 'Statistiche per area: non esistono coordinate pubbliche dei singoli eventi. Non sommare righe di aree o periodi diversi.',
 'righe': [
  dict(area='Lessinia veronese', periodo='2022', eventi=134, capi=185, dettaglio='135 bovini, 39 ovini, 6 caprini, 4 asini, 1 alpaca; 59 eventi dentro il Parco', fonti=['PARCO2023'], stato='verificato'),
  dict(area='Bosco Chiesanuova (VR)', periodo='2022', eventi=53, capi=None, dettaglio='Ripartizione per comune parziale: altri comuni non dettagliati', fonti=['PARCO2023'], stato='verificato', istat='023012'),
  dict(area='Sant\'Anna d\'Alfaedo (VR)', periodo='2022', eventi=28, capi=None, dettaglio='', fonti=['PARCO2023'], stato='verificato', istat='023077'),
  dict(area='Erbezzo (VR)', periodo='2022', eventi=17, capi=None, dettaglio='', fonti=['PARCO2023'], stato='verificato', istat='023032'),
  dict(area='Lessinia trentina', periodo='2022', eventi=21, capi=22, dettaglio='22 bovini', fonti=['PARCO2023'], stato='verificato'),
  dict(area='Malghe di Ala a impatto cronico (4)', periodo='2013–2022', eventi=88, capi=86, dettaglio='Capi uccisi; capi compromessi 99. Boldera + Scortigara Fondo, Mezzo, Cima', fonti=['MUSE2023'], stato='verificato'),
  dict(area='Provincia di Trento', periodo='2013–2022', eventi=576, capi=2256, dettaglio='Capi compromessi. Ovicaprini 64% degli eventi, bovini 26%; 81% degli eventi senza prevenzione efficace', fonti=['MUSE2023'], stato='verificato'),
  dict(area='Lessinia trentina', periodo='2013–2025', eventi=136, capi=143, dettaglio='Capi uccisi (132 bovini, 10 equini, 1 ovino) + 31 feriti; 45% dei danni in agosto–settembre', fonti=['ILDOLOMITI2025'], stato='fonte secondaria (parere ISPRA riportato)'),
  dict(area='Veneto', periodo='2019', eventi=198, capi=425, dettaglio='Capi uccisi; 55 feriti, 302 dispersi', fonti=['VENETO2020'], stato='verificato'),
 ]
}

# ------------------------------------------------------------------ LUPO: eventi storici documentati (localizzati al toponimo)
lupo = [
 F(11.07019, 45.67905, data='2012-01-24', anno=2012, nome='Branchetto', comune='Bosco Chiesanuova', provincia='VR',
   evento='Fototrappola registra una femmina di linea italiana, poi chiamata Giulietta.', stato='osservazione', fonti=['MENINI2015'],
   precisione='Toponimo (Passo del Branchetto, OSM node/471966828); punto esatto non pubblicato'),
 F(11.10313, 45.66198, data='2012-05-04', anno=2012, nome='Potteghe', comune='Roverè Veronese', provincia='VR',
   evento='Primo avvistamento diretto della coppia Slavc–Giulietta.', stato='osservazione', fonti=['MENINI2015'],
   precisione='Toponimo (Monte Potteghe, OSM node/8234132562)'),
 F(11.04703, 45.70093, data='2012-08-27', anno=2012, nome='Podestaria', comune='Bosco Chiesanuova', provincia='VR',
   evento='Il radiocollare GPS di Slavc si sgancia dopo 407 giorni di tracciamento.', stato='osservazione', fonti=['MENINI2015'],
   precisione='Toponimo (rifugio Podestaria, OSM way/143205782); "nei pressi"'),
 F(10.99727, 45.71148, data='2012-10-30', anno=2012, nome='Revoltel', comune='Ala', provincia='TN',
   evento='Campioni organici: prima conferma genetica della nuova coppia.', stato='osservazione', fonti=['PAT2022'],
   precisione='Località (Malga Revoltel, OSM way/152088705)'),
 F(10.99727, 45.71148, data='2012-12-04', anno=2012, nome='Revoltel', comune='Ala', provincia='TN',
   evento='Prima fotografia della coppia (fototrappola).', stato='osservazione', fonti=['PAT2022'],
   precisione='Località (Malga Revoltel, OSM way/152088705)'),
]
cronologia = [
 dict(data='2011-07-17', evento='Slavc riceve un collare GPS-GSM in Slovenia (Università di Lubiana, progetto SloWolf).', fonti=['MENINI2015']),
 dict(data='2011-12', evento='Slavc lascia la Slovenia. La dispersione dura 98 giorni e 1.176 km.', fonti=['RAZEN2016','MENINI2015']),
 dict(data='2012-03-06', evento='Slavc raggiunge la Lessinia.', fonti=['MENINI2015','RAZEN2016']),
 dict(data='2013-08-07', evento='Video di 2 cuccioli: prima riproduzione documentata. Il luogo non è indicato in mappa.', fonti=['MENINI2015','PAT2022']),
 dict(data='2013–2021', evento='Almeno 42 cuccioli accertati per il branco di Slavc e Giulietta (2, 7, 7, 6, 5, 2, 1, 7, 5).', fonti=['PAT2022']),
 dict(data='2022', evento='Nella Lessinia veronese tre branchi, 31 lupi: Lessinia (11), Lessinia Orientale (11), Foresta di Giazza (9).', fonti=['PARCO2023']),
]
cuccioli = {'2013':2,'2014':7,'2015':7,'2016':6,'2017':5,'2018':2,'2019':1,'2020':7,'2021':5}

# ------------------------------------------------------------------ BRANCHI 2022 per comune (dato aggregato, non territori)
branchi_2022 = {
 'nota': 'Comuni indicati dal Parco come interessati dal territorio di ciascun branco nel 2022. Non è un perimetro di territorio: il dato è aggregato per comune.',
 'fonti': ['PARCO2023'],
 'branchi': [
   dict(nome='Branco Lessinia', individui=11, dettaglio='6 adulti, 5 giovani', comuni=['Bosco Chiesanuova','Erbezzo','Grezzana','Cerro Veronese',"Sant'Anna d'Alfaedo",'Ala','Avio']),
   dict(nome='Branco Lessinia Orientale', individui=11, dettaglio='5 adulti, 6 giovani; formato nel 2020', comuni=['Bosco Chiesanuova','Roverè Veronese','Velo Veronese','Selva di Progno','Badia Calavena']),
   dict(nome='Branco Foresta di Giazza', individui=9, dettaglio='nuovo nel 2022', comuni=['Selva di Progno','Ala','Crespadoro']),
 ]
}

def fc(feats): return {'type': 'FeatureCollection', 'features': feats}
def dump(obj, name):
    with open(os.path.join(OUT, name), 'w') as f: json.dump(obj, f, ensure_ascii=False, indent=1)
dump(FONTI, 'fonti.json')
LETTERE = {'boldera':'A','scortigara':'B','revoltel':'C','fittanze':'D1','castelberto':'D2','folignani':'E','bosco':'F','podestaria':'G','sega':'H'}
for f in luoghi: f['properties']['lettera'] = LETTERE[f['properties']['id']]
luoghi.sort(key=lambda f: f['properties']['lettera'])
dump(fc(luoghi), 'tema_luoghi_interesse.geojson')
dump(fc(conflitti), 'tema_conflitti_malghe.geojson')
dump(aggregati, 'tema_predazioni_aggregate.json')
dump(fc(lupo), 'tema_lupo_eventi_storici.geojson')
dump({'cronologia': cronologia, 'cuccioli_minimi': cuccioli, 'fonte_cuccioli': 'PAT2022'}, 'tema_lupo_cronologia.json')
dump(branchi_2022, 'tema_lupo_branchi_comuni_2022.json')
print('ok')
