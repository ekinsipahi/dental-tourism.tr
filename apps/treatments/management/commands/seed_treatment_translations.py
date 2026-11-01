"""
Tedavi çevirilerini apps/treatments/treatment_content/<dil>.json dosyalarından yükler (API anahtarı gerekmez).

  python manage.py seed_treatment_translations             # eksik / başarısız / pending dilleri doldurur
  python manage.py seed_treatment_translations --overwrite # dosyadakini yeniden yazar (yayındaki slug korunur)

Dosya formatı: {"<EN slug>": {"name", "slug", "short_description", "body", "faq": [[soru, cevap]...],
                              "meta_title", "meta_description", "focus_keyword",
                              "price_factors", "program", "refusals"   # hekimin notları (isteğe bağlı)}}
en.json yalnızca hekim notlarını taşır (kaynak dil metni Treatment'a yazılır). Canlı çevirilere yalnızca EKSİK
notlar eklenir; notlar kaynak hash'ine girdiği için, notlar dışında değişmemiş çevirilerin hash'i tazelenir
(OUTDATED → AI ile yeniden çeviri tetiklenmesin).
FİYAT RAKAMI YAZILMAZ.
"""
import hashlib
import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from dental_tourism.languages import LANGUAGE_META

from apps.localization.models import TranslationStatus
from apps.treatments.models import Treatment, TreatmentTranslation

CONTENT_DIR = Path(__file__).resolve().parents[2] / "treatment_content"
NOTE_FIELDS = ("price_factors", "program", "refusals")


def _hash_of(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()


def _file_key(t):
    """Dosyalardaki anahtar İngilizce slug'dır: kaynak dil İngilizce değilse İngilizce çeviri satırının slug'ı kullanılır."""
    if t.source_language == "en":
        return t.slug
    en = t.translations.filter(language_code="en").first()
    return en.slug if en else t.slug


def _known_hashes(t, before):
    """Çevirinin 'güncel' sayılacağı eski kaynak hash'leri: not alanları yokken (ilk deploy) ve bu çalıştırmadan önceki
    not değerleriyle (sonraki deploy'larda yeni not eklendiğinde) hesaplanan hash'ler."""
    payload = t.source_payload()
    return {_hash_of({f: v for f, v in payload.items() if f not in NOTE_FIELDS}),
            _hash_of({**payload, **before.get(t.pk, {})})}


class Command(BaseCommand):
    help = "Tedavi çevirilerini JSON dosyalarından yükler"

    def add_arguments(self, parser):
        parser.add_argument("--overwrite", action="store_true")

    def handle(self, overwrite=False, **o):
        n = notes_written = 0
        matched = set()
        before = {}  # treatment.pk → bu çalıştırmada değişen not alanlarının ÖNCEKİ değerleri (hash tazeleme için)
        treatments = list(Treatment.objects.all())
        with transaction.atomic():
            # kaynak dil önce: hekim notları önce Treatment'a yazılır, çevirilerin hash'i ondan sonra hesaplanır
            for lang in sorted(LANGUAGE_META, key=lambda code: not any(code == t.source_language for t in treatments)):
                f = CONTENT_DIR / f"{lang}.json"
                if not f.exists():
                    continue
                data = json.loads(f.read_text(encoding="utf-8"))
                for t in treatments:
                    d = data.get(_file_key(t))
                    if d is None:
                        continue
                    matched.add(t.key)
                    if lang == t.source_language:  # kaynak dil dosyası: yalnızca hekim notları, boş olanlar dolar
                        upd = [k for k in NOTE_FIELDS if d.get(k) and (overwrite or not getattr(t, k))]
                        if upd:
                            before[t.pk] = {k: getattr(t, k) for k in upd}
                            for k in upd:
                                setattr(t, k, d[k])
                            t.save(update_fields=upd + ["updated_at"])
                            n += 1
                            notes_written += len(upd)
                        continue
                    tr = TreatmentTranslation.objects.filter(treatment=t, language_code=lang).first()
                    live = tr and tr.status in (TranslationStatus.MACHINE, TranslationStatus.REVIEWED)
                    if live and not overwrite:
                        upd = [k for k in NOTE_FIELDS if d.get(k) and not getattr(tr, k)]
                        for k in upd:
                            setattr(tr, k, d[k])
                        full = t.compute_source_hash()
                        if tr.source_hash != full and tr.source_hash in _known_hashes(t, before):
                            tr.source_hash = full  # yalnızca not alanları eklendi → çeviri güncel sayılır (AI yeniden çeviri yok)
                            upd.append("source_hash")
                        if upd:
                            tr.save(update_fields=upd + ["updated_at"])
                            n += 1
                            notes_written += len([k for k in upd if k in NOTE_FIELDS])
                        continue
                    if tr is None and "slug" not in d:  # yalnızca not taşıyan dosya (en.json) yeni satır açamaz
                        continue
                    tr = tr or TreatmentTranslation(treatment=t, language_code=lang)
                    if not (tr.pk and tr.slug and live):
                        tr.slug = d["slug"]
                    tr.name = d["name"]
                    tr.short_description = d["short_description"]
                    tr.body = d["body"]
                    tr.faq = [{"question": q, "answer": a} for q, a in d["faq"]]
                    tr.meta_title = d["meta_title"][:70]
                    tr.meta_description = d["meta_description"][:170]
                    tr.focus_keyword = d.get("focus_keyword", "")
                    for k in NOTE_FIELDS:
                        setattr(tr, k, d.get(k, ""))
                    tr.status = TranslationStatus.REVIEWED
                    tr.source_hash = t.compute_source_hash()
                    tr.model_used = "seed_treatment_translations"
                    tr.translated_at = timezone.now()
                    tr.error = ""
                    tr.save()
                    n += 1
        self.stdout.write(self.style.SUCCESS(
            f"✓ {n} tedavi çevirisi yazıldı (hekim notu alanı: {notes_written}; dosyayla eşleşen tedavi: "
            f"{len(matched)}/{len(treatments)}; eşleşmeyen: {sorted(t.key for t in treatments if t.key not in matched) or '-'})"))
