"""Report di visita della Mappa Agenti Mosnel, salvati cifrati in reports.enc (li legge e li scrive anche la web app).
  python3 tools/report.py apri     -> reports.enc  => reports.json (in chiaro, NON committare)
  python3 tools/report.py chiudi   -> controlla reports.json e lo ricifra in reports.enc
Password in MAPPA_PW. Il controllo usa kit/persone.json se il kit è aperto (python3 tools/kit.py apri + python3 kit/make_map.py)."""
import base64, json, os, re, sys, time, random
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENC, PLAIN = os.path.join(ROOT, "reports.enc"), os.path.join(ROOT, "reports.json")
pw = os.environ.get("MAPPA_PW") or sys.exit("Imposta MAPPA_PW con la password della mappa")
salt = base64.b64decode(re.search(r'salt:"([^"]+)"', open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()).group(1))
key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=600_000).derive(pw.encode())
u, b = base64.b64decode, lambda x: base64.b64encode(x).decode()
cmd = (sys.argv[1:] or [""])[0]
if cmd == "apri":
    o = json.load(open(ENC)) if os.path.exists(ENC) else None
    data = json.loads(AESGCM(key).decrypt(u(o["iv"]), u(o["ct"]), None)) if o else []
    json.dump(data, open(PLAIN, "w"), ensure_ascii=False, indent=1)
    print(len(data), "report in", PLAIN)
elif cmd == "chiudi":
    data = json.load(open(PLAIN, encoding="utf-8"))
    pf = os.path.join(ROOT, "kit", "persone.json")
    pers = json.load(open(pf, encoding="utf-8")) if os.path.exists(pf) else None
    for r in data:
        r.setdefault("id", format(int(time.time() * 1000), "x") + format(random.randrange(16**4), "04x"))
        assert r["tipo"] in {"visita", "affiancamento", "telefonata", "riunione", "evento"}, ("tipo non valido", r)
        assert re.fullmatch(r"\d{4}-\d\d-\d\d", r["data"]), ("data non valida", r["data"])
        assert r.get("rating") in (None, 1, 2, 3, 4, 5), ("rating non valido", r.get("rating"))
        if pers is not None:
            assert r["agente"] in pers, ("agenzia sconosciuta", r["agente"])
            p = pers[r["agente"]]
            if not r.get("referente") and len(p) == 1: r["referente"] = p[0]
            if r.get("referente"): assert r["referente"] in p, ("referente non trovato", r["referente"], p)
    iv = os.urandom(12)
    ct = AESGCM(key).encrypt(iv, json.dumps(data, ensure_ascii=False).encode(), None)
    json.dump({"iv": b(iv), "ct": b(ct)}, open(ENC, "w"))
    print(len(data), "report cifrati in reports.enc", "(controllo agenzie: sì)" if pers is not None else "(controllo agenzie: kit non aperto)")
else:
    sys.exit(__doc__)
