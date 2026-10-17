# Fototrappole del lupo nella Lessinia

Ricognizione del 17 ottobre 2026, su richiesta di includere tutte le evidenze online reperibili nella Lessinia geografica, compresi i versanti trentino e vicentino. Coordinate esatte solo quando pubbliche e verificabili; altrimenti località o area esplicitamente indicativa. Oggetto: dispositivi con rilevamenti di lupo oppure installati nel monitoraggio dedicato al lupo.

## Risultato e unità di rappresentazione

`app/data/tema_fototrappole.geojson` contiene 13 schede, 16 link video e riferimenti a 24 fonti registrate in `app/data/fonti.json`. Nove schede riguardano località; quattro rappresentano reti o aree non suddivisibili in postazioni. Reti e località possono sovrapporsi: non sommare le quantità. Nessuna coordinata esatta di dispositivo è stata verificata. I punti derivano da toponimi OSM della base dell'atlante o da punti rappresentativi scelti per un'area, con metodo dichiarato in ciascuna scheda. I punti non delimitano copertura, territorio dei branchi o area di ripresa.

Non è possibile garantire di aver reperito ogni dispositivo o contenuto online: mancano registri pubblici completi, alcune fonti non localizzano le riprese e parte degli archivi video non risponde. Le installazioni sono anche mobili. Non si inferisce l'attività odierna da immagini storiche.

## Metodo

- Ricerche incrociate per lupo/lupi, fototrappola/videotrappola/fototrappolaggio, Lessinia/Lessini e località (Ala, Sega, Castelberto, Scortigara, Foppiano, Carega, Ronchi, Squaranto, Crespadoro, Selva, Manar).
- Lettura di archivi PAT Grandi Carnivori, rapporto LIFE WOLFALPS Veneto 2014–2016, rapporto Parco Lessinia 2021, studio MUSE 2023 e tesi Vareschi 2016. Confronto con fonti locali e contenuti associativi.
- Estrazione degli incorporamenti video dalle pagine originali, confronto di titoli e autori con l'endpoint ufficiale YouTube oEmbed. Audit dei metadati in `fototrappole_video_verifica.json`. Non si dichiara verificata la riproduzione integrale.
- Video senza postazione riconoscibile associati alla rete/area della fonte, senza attribuirli a una malga specifica. Ripubblicazioni dello stesso filmato non diventano nuovi dispositivi.
- Per contenuti non più verificabili si conserva il link storico e la pagina fonte, con disponibilità non confermata. Per fotografie o dichiarazioni senza video pubblico si esplicita l'assenza del link.
- Crespadoro/Selva: estratto indicizzato di articolo TViWeb; originale non recuperato. Manar: dichiarazione dell'allevatore alla stampa. Entrambe restano segnalazioni da confermare, separate dai dati accertati.

## Evidenze strutturali

Il rapporto LIFE WOLFALPS Veneto 2014–2016 documenta 10 dispositivi veronesi e 8 trentini nel monitoraggio della Lessinia, senza un elenco completo di coordinate pubbliche. La tesi Vareschi 2016 documenta controlli e installazioni a Scortigara/Scorteghere, Castelberto, Foppiano e Camporetratto: sette dispositivi controllati nel novembre 2015; a gennaio 2016 un'installazione e manutenzione di due dispositivi vicini a Scortigara di Fondo; installazione a Camporetratto; tre controlli complessivi Foppiano–Castelberto nel febbraio 2016. Queste quantità non sono sommabili ai conteggi della rete.

Le fonti originali e i singoli URL sono nelle proprietà `fonti` di ciascuna scheda e nel catalogo delle fonti. La tesi è disponibile nell'archivio pubblico PAT; le evidenze di campo sono nelle pagine stampate 86–87.

## Esclusioni e limiti di attribuzione

Esclusi dispositivi documentati solo per altre specie, aree esterne alla Lessinia, filmati da appostamento e filmati per i quali il metodo non consente di affermare una fototrappola. Fra questi, diverse riprese recenti di Io non ho paura del lupo e il filmato del bagno a Dosso di Pezzo non sono trasformati in nuove postazioni. La raccolta del Parco del 2021 comprende un video da fototrappola e uno da appostamento: la pagina è collegata con questa distinzione, senza creare due dispositivi.

`anni` indica anni delle evidenze/documentazione, non un intervallo continuo di funzionamento. Quando il giorno della ripresa non è noto, la scheda video dichiara l'anno dell'archivio o della pubblicazione. L'interfaccia conserva i video storici nella scheda anche quando il filtro seleziona altri anni; il simbolo è visibile solo se esiste un anno documentato nel filtro.
