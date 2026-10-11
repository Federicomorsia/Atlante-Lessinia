OUTPUT FORMAT (mandatory). End your final answer with ONE fenced ```json block containing an array of event objects:
{
 "titolo": "short Italian title",
 "categoria": one of "osservazione","riproduzione","mortalita","predazione","interazione","prevenzione","decisione",
 "sottotipo": e.g. "fototrappola","avvistamento","tracce","genetica","wolf-howling","dispersione","cucciolata","investimento stradale","investimento ferroviario","bracconaggio arma da fuoco","avvelenamento","abbattimento autorizzato","rinvenimento","recupero ferito","predazione bovini","predazione ovicaprini","cani domestici","cani da caccia","escursionisti","centro abitato","recinzioni","cani da guardiania","finanziamento","provvedimento","sentenza/ricorso","tavolo","iniziativa associazione","manifestazione/conflitto sociale","monitoraggio",
 "descrizione": "1-3 factual sentences in Italian, no speculation",
 "data_evento": "YYYY-MM-DD" or "YYYY-MM" or "YYYY" (date of the FACT),
 "data_fine": optional end date for periods,
 "localita": exact place name as in the source (frazione, malga, contrada, strada) or null,
 "comune": "...", "provincia": "VR"/"TN"/"VI"/...,
 "precisione": "localita" (named place) | "comune" | "area" (e.g. 'Lessinia orientale') | "non localizzabile",
 "specie_coinvolte": ["lupo", "bovini", ...],
 "tipo_evidenza": e.g. "fotografia/fototrappola","analisi genetica","necroscopia/IZSVe","rapporto istituzionale","comunicato istituzionale","atto amministrativo","sentenza","articolo di stampa","dichiarazione di parte","testimonianza",
 "stato": "accertato" (confirmed by institutional/scientific evidence) | "documentato" (reported by an identifiable source, no direct confirmation) | "segnalato" (unconfirmed report) | "smentito" (later excluded),
 "fonti": [{"titolo":"...","editore":"...","url":"https://... (exact URL you actually opened or saw in results)","data_pubblicazione":"YYYY-MM-DD or null"}],
 "note": "caveats, contradictions between sources, what is NOT known"
}
RULES: never invent facts, dates, numbers, places or URLs. Only include URLs you actually saw. If two sources disagree, report both in note. Party statements (allevatori, animalisti, politicians) are 'dichiarazione di parte', not proof. Do NOT report den/rendezvous/pup locations below comune/area level. Distinguish number of attacks (events) vs number of animals. Cover 2012-2026 (today is 10 Oct 2026). Also mention in plain text before the JSON: sources consulted, sources inaccessible.
