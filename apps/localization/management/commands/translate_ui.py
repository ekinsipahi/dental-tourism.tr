"""
Arayüz metinlerini (.po) Claude ile çevirir ve derler.

  python manage.py makemessages -a --ignore=venv --ignore=.venv
  python manage.py translate_ui              # tüm dillerde boş msgstr'leri doldurur
  python manage.py translate_ui --lang de --fuzzy
"""
import json
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from dental_tourism.languages import LANGUAGE_META

from apps.localization import llm

BATCH = 80
SYSTEM = ("You translate user-interface strings of a dental tourism website (Istanbul, Turkey) for international "
          "patients. Translate naturally and concisely as a native UI copywriter would, keeping a warm, trustworthy, "
          "professional tone. Keep placeholders like %(name)s, %s, {name}, HTML tags, emojis and brand names "
          "(WhatsApp, Dr. Devrim Sipahi, Istanbul names as given) unchanged. URL path segments ending in '/' must "
          "be translated as lowercase ASCII slug words ending with '/' (e.g. 'treatments/' → 'behandlungen/').")


class Command(BaseCommand):
    help = "locale/*/LC_MESSAGES/django.po dosyalarındaki eksik çevirileri AI ile doldurur"

    def add_arguments(self, parser):
        parser.add_argument("--lang", default="")
        parser.add_argument("--fuzzy", action="store_true", help="fuzzy işaretlileri de yeniden çevir")
        parser.add_argument("--no-compile", action="store_true")

    def handle(self, lang="", fuzzy=False, no_compile=False, **o):
        import polib

        if not llm.is_configured():
            raise CommandError("ANTHROPIC_API_KEY .env içinde tanımlı değil.")
        langs = [x.strip() for x in lang.split(",") if x.strip()] or [c for c in LANGUAGE_META if c != "en"]
        for lg in langs:
            path = Path(settings.LOCALE_PATHS[0]) / lg / "LC_MESSAGES" / "django.po"
            if not path.exists():
                self.stdout.write(self.style.WARNING(f"[{lg}] {path} yok — önce makemessages -l {lg}"))
                continue
            po = polib.pofile(str(path))
            todo = [e for e in po if not e.obsolete and (not e.translated() or (fuzzy and "fuzzy" in e.flags))]
            self.stdout.write(f"[{lg}] {len(todo)} metin çevrilecek")
            for i in range(0, len(todo), BATCH):
                self._translate_batch(lg, todo[i:i + BATCH])
                po.save()
        if not no_compile:
            call_command("compilemessages", ignore=["venv", ".venv"], verbosity=0)
            self.stdout.write(self.style.SUCCESS("✓ compilemessages"))

    def _translate_batch(self, lg, entries):
        meta = LANGUAGE_META[lg]
        items = [{"id": i, "text": e.msgid, **({"plural": e.msgid_plural} if e.msgid_plural else {}),
                  **({"context": e.msgctxt} if e.msgctxt else {})} for i, e in enumerate(entries)]
        schema = {"type": "object", "properties": {"items": {"type": "array", "items": {
            "type": "object", "properties": {"id": {"type": "integer"}, "text": {"type": "string"},
                                             "plural": {"type": "string"}},
            "required": ["id", "text", "plural"], "additionalProperties": False}}},
            "required": ["items"], "additionalProperties": False}
        data = llm.generate_json(
            system=SYSTEM,
            blocks=[{"text": f"Target language: {meta['name']} ({meta['native']}). Turkey='{meta['turkey']}', "
                             f"Istanbul='{meta['istanbul']}'. For entries with 'plural', return the singular "
                             "in 'text' and plural in 'plural' (else empty string).\n\n"
                             + json.dumps(items, ensure_ascii=False)}],
            schema=schema, effort="low", max_tokens=16000)
        by_id = {it["id"]: it for it in data["items"]}
        for i, e in enumerate(entries):
            it = by_id.get(i)
            if not it or not it["text"]:
                continue
            if e.msgid_plural:
                e.msgstr_plural = {0: it["text"], 1: it.get("plural") or it["text"]}
            else:
                e.msgstr = it["text"]
            if "fuzzy" in e.flags:
                e.flags.remove("fuzzy")
