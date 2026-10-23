"""Kit di generazione della Mappa Agenti Mosnel, cifrato nel repository (kit.enc).
  python3 tools/kit.py apri    -> estrae kit/ (dati e script) usando la password in MAPPA_PW
  python3 tools/kit.py chiudi  -> ricifra kit/ in kit.enc (esclude index.html generato)
Richiede: pip install cryptography"""
import base64, io, json, os, sys, tarfile
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENC, KIT, IT = os.path.join(ROOT, "kit.enc"), os.path.join(ROOT, "kit"), 600_000
def key(pw, salt): return PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=IT).derive(pw.encode())
pw = os.environ.get("MAPPA_PW") or sys.exit("Imposta MAPPA_PW con la password della mappa")
cmd = (sys.argv[1:] or [""])[0]
if cmd == "chiudi":
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as t:
        t.add(KIT, arcname="kit", filter=lambda m: None if m.name in ("kit/index.html",) or "__pycache__" in m.name else m)
    salt, iv = os.urandom(16), os.urandom(12)
    ct = AESGCM(key(pw, salt)).encrypt(iv, buf.getvalue(), None)
    b = lambda x: base64.b64encode(x).decode()
    json.dump({"salt": b(salt), "iv": b(iv), "it": IT, "ct": b(ct)}, open(ENC, "w"))
    print("kit.enc aggiornato")
elif cmd == "apri":
    d = json.load(open(ENC)); u = base64.b64decode
    data = AESGCM(key(pw, u(d["salt"]))).decrypt(u(d["iv"]), u(d["ct"]), None)
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as t: t.extractall(ROOT, filter="data")
    print("kit/ estratto in", KIT)
else:
    sys.exit(__doc__)
