# Mappa Agenti Mosnel

Sito: https://simoneriello.github.io/mappa-agenti/ (pagina cifrata, si apre con password).

- `index.html`: la mappa pubblicata, cifrata (AES-GCM, chiave PBKDF2-SHA256).
- `kit.enc`: dati e script che generano la mappa (agenti, province, report di visita), cifrati con la stessa password.
- `tools/kit.py`: apre e richiude il kit.

## Report di visita (reports.enc)
I report stanno in `reports.enc`, cifrato con la password della mappa. La mappa lo legge all'apertura; dalla pagina Report Simone può scrivere report e spuntare azioni (serve una chiave GitHub fine-grained con Contents read/write su questo repository, salvata solo sul suo dispositivo).

Aggiungere o correggere un report da chat:
```
pip install cryptography
export MAPPA_PW='...'                          # password della mappa, la fornisce Simone
git pull                                       # la web app può aver scritto nel frattempo
python3 tools/kit.py apri && python3 kit/make_map.py   # serve kit/persone.json per il controllo
python3 tools/report.py apri                   # reports.enc -> reports.json
# modificare reports.json
python3 tools/report.py chiudi                 # controlla e ricifra in reports.enc
rm -rf kit reports.json && git add reports.enc && git commit && git push
```
Non serve rigenerare la pagina per i report: basta aggiornare reports.enc.

## Aggiornare la mappa (agenti, province, grafica)
```
export MAPPA_PW='...'
python3 tools/kit.py apri
# modificare kit/make_map.py o kit/prov_data.py
python3 kit/make_map.py
python3 kit/encrypt_page.py kit/index.html index.html
python3 tools/kit.py chiudi
rm -rf kit && git add index.html kit.enc && git commit && git push
```
Le cartelle e i file in chiaro (`kit/`, `reports.json`) non vanno mai committati.

## Formato di un report
```json
{"id": "...", "agente": "Nome agenzia come in mappa", "referente": "Nome della persona",
 "data": "2026-10-11", "tipo": "affiancamento", "motivo": "...", "sintesi": "...", "rating": 4,
 "clienti": [{"nome": "Nome cliente", "esito": "ordine fatto"}],
 "azioni": [{"testo": "...", "entro": "2026-11-15", "stato": "aperta"}]}
```
- `tipo`: visita, affiancamento, telefonata, riunione, evento.
- `referente`: persona dell'agenzia, come nei contatti; per le agenzie di una sola persona si compila da sola.
- `rating`: da 1 a 5 calici, per il referente. Il rating dell'agenzia è la media degli ultimi voti dei referenti.
- `stato` azione: aperta o fatto. `id` viene aggiunto da `tools/report.py` se manca.
