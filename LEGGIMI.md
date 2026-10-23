# Mappa Agenti Mosnel

Sito: https://simoneriello.github.io/mappa-agenti/ (pagina cifrata, si apre con password).

- `index.html`: la mappa pubblicata, cifrata (AES-GCM, chiave PBKDF2-SHA256).
- `kit.enc`: dati e script che generano la mappa (agenti, province, report di visita), cifrati con la stessa password.
- `tools/kit.py`: apre e richiude il kit.

## Aggiornare la mappa o aggiungere un report
```
pip install cryptography
export MAPPA_PW='...'              # password della mappa, la fornisce Simone
python3 tools/kit.py apri          # crea la cartella kit/
# modificare kit/reports.json (report) o kit/make_map.py / kit/prov_data.py (agenti, province)
python3 kit/make_map.py            # genera kit/index.html in chiaro
python3 kit/encrypt_page.py kit/index.html index.html   # cifra e sostituisce la pagina pubblicata
python3 tools/kit.py chiudi        # ricifra il kit
rm -rf kit && git add index.html kit.enc && git commit && git push
```
La cartella `kit/` in chiaro non va mai committata.

## Formato di un report (kit/reports.json)
```json
{"agente": "Nome agenzia come in mappa", "data": "2026-10-11", "tipo": "affiancamento",
 "motivo": "...", "sintesi": "...", "rating": 4,
 "clienti": [{"nome": "Nome cliente", "esito": "nuovo"}],
 "azioni": [{"testo": "...", "entro": "2026-11-15", "stato": "aperta"}]}
```
- `agente`: nome esatto dell'agenzia come in mappa.
- `tipo`: visita, affiancamento, telefonata, riunione, evento.
- `rating`: da 1 a 5 calici, deciso da Simone.
- `esito` cliente: nuovo, riordino, da ricontattare, oppure testo libero.
- `stato` azione: aperta o fatto.
