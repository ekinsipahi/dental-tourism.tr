"""
locale/_source/<dil>.txt dosyalarındaki elle yazılmış arayüz çevirilerini .po dosyalarına işler.

Dosya formatı: her satır  `<msgid_index>|<çeviri>` ; çoğul formlar `‖` ile ayrılır.
Index sırası `makemessages` çıktısındaki msgid sırasıdır; eşleşme için `locale/_source/msgids.json`
(msgid listesi) kullanılır, böylece .po yeniden üretilse bile çeviriler doğru msgid'e gider.

    python manage.py apply_ui_translations            # tüm diller + compilemessages
    python manage.py apply_ui_translations --dump     # msgids.json'u mevcut .po'dan yeniden üret
"""
import json
import re
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

PH = re.compile(r"%\(\w+\)s|%%|\{\{.*?\}\}")

PLURAL_FORMS = {
    "fr": "nplurals=2; plural=(n > 1);",
    "pl": "nplurals=3; plural=(n==1 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2);",
    "ru": "nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2);",
    "uk": "nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2);",
    "ar": "nplurals=6; plural=(n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 : n%100>=11 ? 4 : 5);",
    "ro": "nplurals=3; plural=(n==1 ? 0 : (n==0 || (n%100>0 && n%100<20)) ? 1 : 2);",
}
DEFAULT_PLURAL = "nplurals=2; plural=(n != 1);"


def fix_header(po, lang):
    po.metadata["Plural-Forms"] = PLURAL_FORMS.get(lang, DEFAULT_PLURAL)
    po.metadata["Language"] = lang
    po.metadata["Content-Type"] = "text/plain; charset=UTF-8"
    po.metadata["Project-Id-Version"] = "dentaltourism.tr"
    po.metadata_is_fuzzy = False


class Command(BaseCommand):
    help = "locale/_source/*.txt çevirilerini .po dosyalarına yazar ve derler"

    def add_arguments(self, parser):
        parser.add_argument("--dump", action="store_true")
        parser.add_argument("--lang", default="")

    def handle(self, dump=False, lang="", **o):
        import polib

        base = Path(settings.LOCALE_PATHS[0])
        src = base / "_source"
        ids_path = src / "msgids.json"
        if dump or not ids_path.exists():
            po = polib.pofile(str(base / "de" / "LC_MESSAGES" / "django.po"))
            ids = [e.msgid for e in po if not e.obsolete]
            ids_path.write_text(json.dumps(ids, ensure_ascii=False, indent=0), encoding="utf-8")
            self.stdout.write(f"msgids.json: {len(ids)} metin")
            if dump:
                return
        ids = json.loads(ids_path.read_text(encoding="utf-8"))

        # Tüm .po başlıklarını düzelt (makemessages şablon başlık bırakıyor → derleme hatası)
        for po_file in base.glob("*/LC_MESSAGES/django.po"):
            lg_code = po_file.parent.parent.name
            p = polib.pofile(str(po_file))
            fix_header(p, lg_code)
            p.save()

        files = sorted(src.glob("*.txt"))
        if lang:
            files = [f for f in files if f.stem in lang.split(",")]
        errors = 0
        for f in files:
            lg = f.stem
            po_path = base / lg / "LC_MESSAGES" / "django.po"
            if not po_path.exists():
                raise CommandError(f"{po_path} yok — önce makemessages -l {lg}")
            po = polib.pofile(str(po_path))
            entries = {e.msgid: e for e in po if not e.obsolete}
            nplurals = int(re.search(r"nplurals=(\d+)", po.metadata.get("Plural-Forms", "nplurals=2")).group(1))
            done = 0
            for line in f.read_text(encoding="utf-8").splitlines():
                if not line.strip() or line.startswith("#"):
                    continue
                idx, _, text = line.partition("|")
                msgid = ids[int(idx)]
                e = entries.get(msgid)
                if e is None:
                    continue
                forms = text.split("‖")
                src_ph = sorted(PH.findall(msgid + (e.msgid_plural or "")))
                for form in forms:
                    if sorted(set(PH.findall(form))) != sorted(set(src_ph)):
                        self.stderr.write(f"[{lg}] #{idx} yer tutucu uyuşmuyor: {msgid!r} → {form!r}")
                        errors += 1
                if msgid.endswith("/") and not re.fullmatch(r"[a-z0-9\-/]+/", forms[0]):
                    self.stderr.write(f"[{lg}] #{idx} URL segmenti ASCII slug olmalı: {forms[0]!r}")
                    errors += 1
                if e.msgid_plural:
                    forms = (forms + [forms[-1]] * nplurals)[:nplurals]
                    e.msgstr_plural = {i: v for i, v in enumerate(forms)}
                else:
                    e.msgstr = forms[0]
                if "fuzzy" in e.flags:
                    e.flags.remove("fuzzy")
                # "%70 indirim" gibi düz yüzde işaretleri python-format sanılıyor → msgfmt hatası
                if "python-format" in e.flags and not re.search(r"%\(\w+\)s|%s|%d", msgid):
                    e.flags.remove("python-format")
                done += 1
            po.save()
            missing = [e.msgid for e in po if not e.obsolete and not e.translated()]
            self.stdout.write(f"[{lg}] {done} çeviri işlendi, eksik: {len(missing)}")
        if errors:
            raise CommandError(f"{errors} doğrulama hatası")
        call_command("compilemessages", ignore=["venv", ".venv", "_source"], verbosity=0)
        self.stdout.write(self.style.SUCCESS("✓ compilemessages"))
