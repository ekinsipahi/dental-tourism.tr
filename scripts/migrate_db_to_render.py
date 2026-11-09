#!/usr/bin/env python
"""
Supabase → Render Postgres taşıma (tek seferlik, yeniden çalıştırılabilir).

Kullanım (proje kökünden, venv aktif):
    .env içine:  RENDER_DATABASE_URL=<Render "External Database URL">   (repoya girmez; .env zaten gitignore'da)
    venv/bin/python scripts/migrate_db_to_render.py            # dump + restore + satır sayısı karşılaştırması
    venv/bin/python scripts/migrate_db_to_render.py --verify   # yalnızca karşılaştırma (taşıma sonrası tekrar kontrol)

Ne yapar:
  1. Kaynak (DATABASE_URL = Supabase) → pg_dump, yalnızca `public` şeması (Supabase'in kendi şemaları/uzantıları alınmaz),
     --no-owner --no-privileges (Render'da farklı kullanıcı), custom format → <scratch>/supabase.dump
  2. Hedef (RENDER_DATABASE_URL) → pg_restore --clean --if-exists (tekrar çalıştırılırsa üstüne yazar)
  3. Her tablo için kaynak/hedef satır sayısını karşılaştırır, sıralı dizileri (sequence) ve ANALYZE'ı tamamlar.
Hiçbir şifre ekrana yazılmaz. Kaynağa yazmaz; hedef boş/yeni veritabanı olmalı.
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

import psycopg2
from decouple import config

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get("MIGRATE_OUT", ROOT / ".migrate_tmp"))


def _host(url):
    return urlparse(url).hostname or "?"


def run(cmd, **kw):
    print("  $", " ".join(a if not a.startswith("postgres") else "<url>" for a in cmd))
    subprocess.run(cmd, check=True, **kw)


def table_counts(url):
    with psycopg2.connect(url, connect_timeout=20) as conn, conn.cursor() as cur:
        cur.execute("""select tablename from pg_tables where schemaname='public' order by 1""")
        tables = [r[0] for r in cur.fetchall()]
        counts = {}
        for t in tables:
            cur.execute(f'select count(*) from public."{t}"')
            counts[t] = cur.fetchone()[0]
    return counts


def verify(src, dst):
    a, b = table_counts(src), table_counts(dst)
    bad = 0
    for t in sorted(set(a) | set(b)):
        ca, cb = a.get(t), b.get(t)
        flag = "" if ca == cb else "   <-- FARK"
        if flag:
            bad += 1
        print(f"  {t:45s} supabase={str(ca):>8} render={str(cb):>8}{flag}")
    print(f"\n{'✓ tüm tablolar eşit' if not bad else f'✗ {bad} tabloda fark var'} ({len(a)} tablo)")
    return bad == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true", help="yalnızca satır sayılarını karşılaştır")
    args = ap.parse_args()

    src = config("DATABASE_URL", default="")
    dst = config("RENDER_DATABASE_URL", default="")
    if not src or not dst:
        sys.exit("DATABASE_URL (kaynak) ve RENDER_DATABASE_URL (hedef) .env'de tanımlı olmalı")
    if "supabase" not in _host(src):
        sys.exit(f"Kaynak Supabase görünmüyor: {_host(src)} — DATABASE_URL hâlâ Supabase'i göstermeli")
    if "render.com" not in _host(dst):
        sys.exit(f"Hedef Render görünmüyor: {_host(dst)} — External Database URL kullanın")
    print(f"kaynak: {_host(src)}  →  hedef: {_host(dst)}")

    if args.verify:
        sys.exit(0 if verify(src, dst) else 1)

    OUT.mkdir(parents=True, exist_ok=True)
    dump = OUT / "supabase.dump"
    print("\n1) pg_dump (yalnızca public şeması)")
    run(["pg_dump", "--format=custom", "--no-owner", "--no-privileges", "--schema=public",
         "--no-comments", f"--file={dump}", src])
    print(f"   dump: {dump} ({dump.stat().st_size // 1024} KB)")

    print("\n2) pg_restore → Render")
    run(["pg_restore", "--no-owner", "--no-privileges", "--clean", "--if-exists", "--exit-on-error",
         "--jobs=4", f"--dbname={dst}", str(dump)])

    print("\n3) ANALYZE + karşılaştırma")
    with psycopg2.connect(dst, connect_timeout=20) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("ANALYZE")
    ok = verify(src, dst)
    print("\nSonraki adım: Render env group 'dental-tourism-shared' → DATABASE_URL = Internal Database URL, "
          "DB_SSLMODE=prefer; web servisi yeniden deploy olunca /healthz ve sayfalar kontrol edilir; "
          "ardından `--verify` ile son karşılaştırma.")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
