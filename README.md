# Atlante della Lessinia — versione 0.2 (10 ottobre 2026)

Prototipo di atlante cartografico per il progetto *Diplomazia Multispecie della Lessinia* (Communication Design, Politecnico di Milano).

## Come aprirlo sul tuo computer

1. Doppio clic su `avvia_atlante.command` (la prima volta: tasto destro → Apri, per l'avviso di sicurezza di macOS).
2. Si apre il browser su `http://localhost:8765`. Per chiudere, chiudi la finestra del Terminale.

In alternativa, da Terminale: `cd app && python3 -m http.server 8765`.
Il file `app/index.html` non funziona con doppio clic diretto: i browser bloccano la lettura dei file di dati da `file://`.

La versione locale esporta la vista in PNG (pulsante *Esporta PNG*) con scala grafica, nord, estensione e attribuzioni.

## Struttura

```
Atlante-Lessinia/
├── app/                  atlante pronto all'uso (interfaccia + dati)
│   ├── index.html        interfaccia (MapLibre GL JS 4.7.1, nessuna API key)
│   ├── data/             tutti i livelli: GeoJSON, raster, catalogo, fonti
│   └── vendor/           copia locale di MapLibre
├── data/                 livelli di base elaborati (output degli script)
├── raw/                  dati originali scaricati (ISTAT, EEA, TINITALY, OSM)
├── scripts/              elaborazione dei dati di base (Python)
├── build/                dati tematici (thematic.py) e assemblaggio (make.py)
└── src/                  sorgenti dell'interfaccia (index.html, app.js)
```

## Aggiungere un dataset

1. Metti il file GeoJSON (WGS84) in `app/data/`.
2. Aggiungi una voce in `app/data/catalogo.json` (gruppo, titolo, file, fonti, stato, periodo, legenda).
3. Se la fonte è nuova, aggiungila a `app/data/fonti.json`.
4. Per uno stile cartografico specifico aggiungi il layer MapLibre in `src/app.js` e riassembla con `build/make.py`.

I dati non sono mai scritti dentro l'interfaccia: coordinate e numeri stanno solo nei file di `data/`.

## Novità della versione 0.2

- **Archivio eventi 2012–2026** (`app/data/tema_eventi_archivio.json`, `tema_eventi.geojson`): 186 eventi in sette categorie (osservazioni, riproduzione, mortalità, predazioni, interazioni, prevenzione, decisioni istituzionali), 93 localizzati in mappa al toponimo OSM o al comune. Ogni evento ha data del fatto, luogo, precisione, tipo di evidenza, stato di verifica e fonti con URL.
- **Stati di verifica degli eventi**: accertato, documentato, segnalato, smentito.
- **Predazioni per malga 2012–2024**: 12 malghe localizzate (più Castilverio, non localizzabile) dalla tesi Tabarelli de Fatis (2025), con la serie MUSE–PAT 2013–2022 come confronto per le malghe di Ala.
- **Relazioni tra eventi** (`tema_relazioni.json`): cinque relazioni tematiche e undici collegamenti documentati (storici, geografici, istituzionali). Non rappresentano percorsi di animali.
- **Ambiti diplomatici** (`tema_ambiti_diplomatici.geojson`): dodici ipotesi progettuali (osservazione, rappresentanza, mediazione, negoziazione) costruite sugli eventi e su geometrie reali.
- **Tempo**: modalità Intervallo, Anno singolo e Cumulativo, fino al 2026.
- **Pannello Eventi**: archivio completo con ricerca, anche per gli eventi non localizzabili.
- `research/`: le schede grezze delle quattro ricerche documentali; `build/eventi.py` e `build/ambiti.py` le trasformano nei file dell'atlante.

## Gradi di verifica

Ogni elemento ha un campo `stato`:

- **verificato**: geometria o valore da fonte ufficiale o scientifica identificata;
- **osservazione**: evento datato registrato da monitoraggio o studio;
- **fonte secondaria**: dato riportato dalla stampa (es. parere ISPRA citato);
- **interpretazione** e **ipotesi progettuale**: previsti nel modello dati, non usati come geometrie in questa versione.

## Dataset

| Livello | Fonte | Formato | Anno | Licenza | Limiti |
|---|---|---|---|---|---|
| Confini comunali, provinciali, regionali | ISTAT, confini non generalizzati | Shapefile | 1/1/2026 | CC BY 3.0 IT | Semplificati a 2 m |
| Parco Naturale Regionale della Lessinia | EEA NatDA v24 (dati MASE, EUAP0241) | ArcGIS REST | 2024 | EEA | Da confrontare con la perimetrazione regionale |
| Natura 2000 | EEA Natura 2000 End 2024 | ArcGIS REST | 2024 | EEA | — |
| DTM, curve di livello, ombreggiatura | TINITALY 1.1, INGV (doi:10.13127/tinitaly/1.1) | GeoTIFF 10 m | 2023 | CC BY 4.0 | Curve da griglia 20 m con smoothing |
| Boschi, praterie, idrografia, viabilità, sentieri, toponimi, malghe | OpenStreetMap via Overpass API | JSON | 10/10/2026 | ODbL | Completezza variabile |
| Predazioni per malga (Ala) | MUSE–PAT 2023, Tab. 4–5 | PDF | 2013–2022 | — | Solo malghe trentine a impatto cronico |
| Predazioni per area / comune | Parco Lessinia 2023; MUSE–PAT 2023; Regione Veneto 2020; stampa | PDF / web | 2019–2025 | — | Ripartizione per comune parziale |
| Osservazioni storiche del lupo | Menini 2015; Bombieri et al. 2022 | PDF | 2012 | — | Localizzate al toponimo |
| Branchi per comune | Parco Lessinia 2023 | PDF | 2022 | — | Non sono perimetri di territorio |

Consultazione di tutte le fonti: 10 ottobre 2026. L'elenco completo con URL è in `app/data/fonti.json` e nel pannello *Fonti* dell'atlante.

## Dati non reperiti

- Perimetri delle superfici di pascolo delle singole malghe (Piano malghe PAT; Regione Veneto / Comuni).
- Coordinate dei singoli eventi di predazione (non pubbliche).
- Serie annuale delle predazioni per comune nella Lessinia veronese (disponibile solo il 2022, parziale).
- Testo integrale della tesi Tabarelli de Fatis (UniPD 2024), che contiene la mappatura 2012–2024 per malga.
- Perimetrazione ufficiale del Parco dal geoportale della Regione Veneto (download dietro login).
- Territori dei branchi, corridoi, spostamenti: non pubblicati, non rappresentati.
- Tane e siti riproduttivi: esclusi per tutela della specie.

## Verifiche da fare prima di un uso pubblico

- Confrontare il perimetro del Parco EEA con la cartografia della L.R. 12/1990 e successive modifiche (2016).
- Controllare in QGIS le geometrie OSM dei boschi e delle praterie nell'Alta Lessinia.
- Chiedere a MUSE/PAT e al Parco i dati 2023–2025 per malga e per comune.
