#!/usr/bin/env python3
"""Google Ads API için tek seferlik OAuth: refresh token üretir ve .env'e yazar. Hiçbir gizli değeri ekrana basmaz.

Kullanım:
  python scripts/ads_oauth.py url            # onay adresini yazdırır (tarayıcıda aç, Google hesabıyla onayla)
  python scripts/ads_oauth.py code '<tarayıcının yönlendiği localhost adresi veya code=... değeri>'
                                             # kodu refresh token ile değiştirir, .env'e GOOGLE_ADS_REFRESH_TOKEN yazar
Gerekli .env anahtarları: GOOGLE_ADS_CLIENT_ID, GOOGLE_ADS_CLIENT_KEY (client secret).
OAuth istemcisi "Desktop app" tipinde olmalı; yönlendirme adresi http://localhost:8765/ kullanılır.
"""
import json, re, sys, urllib.parse, urllib.request
from pathlib import Path

ENV = Path(__file__).resolve().parents[1] / ".env"
REDIRECT = "http://localhost:8765/"
SCOPE = "https://www.googleapis.com/auth/adwords"


def env():
    d = {}
    for line in ENV.read_text(encoding="utf8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            d[k.strip()] = v.strip().strip('"').strip("'")
    return d


def main():
    e = env()
    cid, secret = e.get("GOOGLE_ADS_CLIENT_ID"), e.get("GOOGLE_ADS_CLIENT_KEY")
    if not cid or not secret:
        sys.exit(".env'de GOOGLE_ADS_CLIENT_ID / GOOGLE_ADS_CLIENT_KEY yok")
    cmd = sys.argv[1] if len(sys.argv) > 1 else "url"
    if cmd == "url":
        q = {"client_id": cid, "redirect_uri": REDIRECT, "response_type": "code", "scope": SCOPE,
             "access_type": "offline", "prompt": "consent"}
        print("https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(q))
        return
    if cmd == "code":
        raw = sys.argv[2]
        m = re.search(r"[?&]code=([^&\s]+)", raw)
        code = urllib.parse.unquote(m.group(1)) if m else raw.strip()
        data = urllib.parse.urlencode({"code": code, "client_id": cid, "client_secret": secret,
                                       "redirect_uri": REDIRECT, "grant_type": "authorization_code"}).encode()
        req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                tok = json.load(r)
        except urllib.error.HTTPError as ex:
            sys.exit(f"Google hata döndü ({ex.code}): {ex.read().decode()[:300]}")
        rt = tok.get("refresh_token")
        if not rt:
            sys.exit("Cevapta refresh_token yok (daha önce verilmiş olabilir; 'url' adımını prompt=consent ile tekrarla).")
        lines = [l for l in ENV.read_text(encoding="utf8").splitlines() if not l.startswith("GOOGLE_ADS_REFRESH_TOKEN=")]
        lines.append(f"GOOGLE_ADS_REFRESH_TOKEN={rt}")
        ENV.write_text("\n".join(lines) + "\n", encoding="utf8")
        print(f"refresh token .env'e yazıldı (uzunluk {len(rt)}); kapsam: {tok.get('scope')}")
        return
    sys.exit("bilinmeyen komut")


if __name__ == "__main__":
    main()
