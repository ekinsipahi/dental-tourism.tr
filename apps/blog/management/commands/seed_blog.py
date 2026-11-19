"""
Blog yazılarını DOSYADAN (Markdown + YAML ön bilgi) veritabanına yükler — API anahtarı gerekmez.
build.sh ve günlük cron (seed_translations) içinden çalışır: repoya eklenen yazı deploy ile canlıya çıkar,
yayınlandığı anda sitemap'e ve hreflang'a girer.

Dizin: apps/blog/content/
  categories.yaml                 kategoriler + 17 dilde ad/slug/açıklama (yalnızca EKSİK çeviriler yazılır)
  posts/<yazi-slug>/en.md         kaynak dil (ön bilgideki `lang`; varsayılan en)
  posts/<yazi-slug>/<dil>.md      çeviriler — insan onaylı sayılır (status=reviewed), AI çevirisi ezmez

DOSYA ESASTIR: yazı ve çevirileri dosyadan farklıysa DB güncellenir (admin'den yapılan düzenleme bir sonraki
deploy'da dosyadaki hâle döner). Değişiklik yoksa hiçbir kayıt yazılmaz (dateModified oynamaz).

  python manage.py seed_blog                   # tüm yazılar + kategoriler
  python manage.py seed_blog --dir <yol>       # başka içerik dizini (test)
  python manage.py seed_blog --export <slug>   # DB'deki canlı çevirileri posts/<slug>/<dil>.md olarak yazar
                                               # (translate_content ile üretilen makine çevirisini dosyaya almak için)

Ön bilgi (en.md):
---
title: Is it safe to get dental implants in Turkey?
slug: is-it-safe-to-get-dental-implants-in-turkey     # URL; boşsa dizin adı
category: safety-and-quality                           # categories.yaml anahtarı
excerpt: ...
meta_title: ...
meta_description: ...
focus_keyword: ...
featured_image: img/blog/implant-safety/hero.jpg       # static/ altındaki yol → kalıcı statik URL
featured_image_alt: ...
author: devrim-biriken-sipahi                          # hekim slug → yazar kutusu + schema author
reviewed_by: ekin-sipahi                               # isteğe bağlı ikinci hekim
treatment: dental-implants                             # tedavi anahtarı (yazı sonunda tedavi kutusu)
schema_type: MedicalWebPage                            # BlogPosting | Article | MedicalWebPage | HowTo
funnel_stage: consideration                            # awareness | consideration | decision
guides: [dental-care-turkey, teeth-done-in-turkey]     # rehber anahtarları (SeoTopic.key): o rehberlerde iç link bloğu
status: published                                      # draft | review | published
published: 2026-12-05                                  # yayın tarihi; gelecekse o gün görünür
auto_translate: false                                  # true → yayınlanınca AI 16 dile çevirir (API anahtarı gerekir)
faq:
  - q: ...
    a: ...
---
Gövde: Markdown, H1 yok (## ile başlar). Fotoğraf: ![alt]({static:img/blog/implant-safety/foto.jpg})

Çeviri dosyası (<dil>.md) ön bilgisi: title, slug, excerpt, meta_title, meta_description, focus_keyword,
featured_image_alt, faq — gövde çevrilmiş Markdown.
"""
import re
from datetime import date, datetime, time
from pathlib import Path

import yaml
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.templatetags.static import static
from django.utils import timezone
from slugify import slugify

from dental_tourism.languages import LANGUAGE_META

from apps.blog.models import BlogCategory, BlogCategoryTranslation, BlogPost, BlogPostTranslation
from apps.localization.models import LIVE_STATUSES, TranslationStatus

CONTENT_DIR = Path(__file__).resolve().parents[2] / "content"
FRONT = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.S)
STATIC_TOKEN = re.compile(r"\{static:([^}\s]+)\}")
TRANSLATED = ("title", "slug", "excerpt", "content", "faq", "featured_image_alt", "meta_title", "meta_description",
              "focus_keyword")
POST_FIELDS = ("title", "category", "excerpt", "content", "faq", "featured_image_url", "featured_image_alt",
               "meta_title", "meta_description", "focus_keyword", "canonical_url", "noindex", "schema_type",
               "funnel_stage", "target_personas", "related_guides", "status", "published_at", "auto_translate", "doctor_author",
               "reviewed_by", "treatment", "content_source")


def static_url(path):
    """static/ altındaki yol → (varsa manifest hash'li) kalıcı URL. Dosya henüz yoksa düz /static/ yolu."""
    path = path.lstrip("/")
    if path.startswith("static/"):
        path = path[len("static/"):]
    try:
        return static(path)
    except ValueError:
        return settings.STATIC_URL + path


def parse_markdown(text):
    """(ön bilgi dict, gövde) — ön bilgi yoksa ({}, metin)."""
    m = FRONT.match(text)
    if not m:
        return {}, text.strip()
    meta = yaml.safe_load(m.group(1)) or {}
    if not isinstance(meta, dict):
        raise CommandError("Ön bilgi bir YAML eşlemesi olmalı")
    return meta, text[m.end():].strip()


def render_body(body):
    return STATIC_TOKEN.sub(lambda m: static_url(m.group(1)), body)


def norm_faq(items):
    out = []
    for it in items or []:
        if not isinstance(it, dict):
            continue
        q = (it.get("question") or it.get("q") or "").strip()
        a = (it.get("answer") or it.get("a") or "").strip()
        if q and a:
            out.append({"question": q, "answer": a})
    return out


def _aware(value):
    """published: tarih ya da tarih-saat → Europe/Istanbul 09:00 (tarihse)."""
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value if timezone.is_aware(value) else timezone.make_aware(value)
    if isinstance(value, date):
        return timezone.make_aware(datetime.combine(value, time(9, 0)))
    parsed = datetime.fromisoformat(str(value))
    return parsed if timezone.is_aware(parsed) else timezone.make_aware(parsed)


class Command(BaseCommand):
    help = "Blog yazılarını ve kategori çevirilerini dosyadan yükler (dosya esastır; API anahtarı gerekmez)"

    def add_arguments(self, parser):
        parser.add_argument("--dir", default="", help="içerik dizini (varsayılan apps/blog/content)")
        parser.add_argument("--export", default="", help="yazı slug'ı: DB'deki canlı çevirileri <dil>.md olarak yaz")

    def handle(self, dir="", export="", **o):
        settings.AUTO_TRANSLATE_ON_PUBLISH = False  # dosyadan yüklerken AI çevirisi tetiklenmesin
        self.root = Path(dir) if dir else CONTENT_DIR
        if export:
            return self._export(export)
        stats = {"categories": 0, "category_translations": 0, "posts_created": 0, "posts_updated": 0,
                 "translations": 0, "unchanged": 0}
        self._categories(stats)
        posts_dir = self.root / "posts"
        if posts_dir.is_dir():
            for folder in sorted(p for p in posts_dir.iterdir() if p.is_dir()):
                self._post(folder, stats)
        self.stdout.write("✓ seed_blog " + ", ".join(f"{k}={v}" for k, v in stats.items() if v))

    # ── Kategoriler ───────────────────────────────────────────────────────────────────────────────────────
    def _categories(self, stats):
        f = self.root / "categories.yaml"
        if not f.exists():
            return
        data = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        for key, spec in data.items():
            src_lang = spec.get("lang", "en")
            src = spec.get(src_lang) or {}
            cat = BlogCategory.objects.filter(slug=key).first()
            if cat is None:
                cat = BlogCategory.objects.create(
                    slug=key, name=src.get("name") or key.replace("-", " ").title(),
                    description=src.get("description", ""), meta_title=src.get("meta_title", ""),
                    meta_description=src.get("meta_description") or src.get("description", ""),
                    funnel_stage=spec.get("funnel_stage", "awareness"), order=spec.get("order", 0),
                    source_language=src_lang)
                stats["categories"] += 1
            source_hash = cat.compute_source_hash()
            existing = set(cat.translations.values_list("language_code", flat=True))
            for lang in LANGUAGE_META:
                tr = spec.get(lang)
                if lang == cat.source_language or lang in existing or not isinstance(tr, dict) or not tr.get("name"):
                    continue
                slug = self._free_slug(BlogCategoryTranslation, lang, tr.get("slug") or slugify(tr["name"]))
                BlogCategoryTranslation.objects.create(
                    category=cat, language_code=lang, name=tr["name"], slug=slug,
                    description=tr.get("description", ""), meta_title=tr.get("meta_title", "")[:70],
                    meta_description=(tr.get("meta_description") or tr.get("description", ""))[:170],
                    status=TranslationStatus.REVIEWED, source_hash=source_hash, model_used="file",
                    translated_at=timezone.now())
                stats["category_translations"] += 1

    @staticmethod
    def _free_slug(tr_model, lang, base, exclude_pk=None):
        slug, n = base, 2
        while True:
            qs = tr_model.objects.filter(language_code=lang, slug=slug)
            if exclude_pk:
                qs = qs.exclude(pk=exclude_pk)
            if not qs.exists():
                return slug
            slug, n = f"{base}-{n}", n + 1

    # ── Yazılar ───────────────────────────────────────────────────────────────────────────────────────────
    def _post(self, folder, stats):
        files = {p.stem: p for p in folder.glob("*.md")}
        if not files:
            return
        # Kaynak dosya: `lang:` alanı kendisini işaret eden ya da en.md
        source_lang = "en" if "en" in files else next(iter(sorted(files)))
        meta, body = parse_markdown(files[source_lang].read_text(encoding="utf-8"))
        source_lang = meta.get("lang", source_lang)
        if source_lang not in LANGUAGE_META:
            raise CommandError(f"{folder.name}: bilinmeyen kaynak dil {source_lang}")
        slug = meta.get("slug") or folder.name
        if not meta.get("title"):
            raise CommandError(f"{folder.name}/{source_lang}.md: title gerekli")
        cat_key = meta.get("category")
        category = BlogCategory.objects.filter(slug=cat_key).first() if cat_key else None
        if category is None:
            raise CommandError(f"{folder.name}: kategori yok ({cat_key!r}) — categories.yaml'a ekleyin")

        from apps.clinics.models import Doctor
        from apps.treatments.models import Treatment

        def doctor(key):
            if not key:
                return None
            d = Doctor.objects.filter(slug=key).first()
            if d is None:
                self.stderr.write(f"  ! {folder.name}: hekim bulunamadı: {key}")
            return d

        treatment = Treatment.objects.filter(key=meta["treatment"]).first() if meta.get("treatment") else None
        status = meta.get("status", BlogPost.STATUS_DRAFT)
        if status not in dict(BlogPost.STATUS_CHOICES):
            raise CommandError(f"{folder.name}: geçersiz status {status!r}")
        desired = {
            "title": meta["title"][:200], "category": category, "excerpt": (meta.get("excerpt") or "")[:300],
            "content": render_body(body), "faq": norm_faq(meta.get("faq")),
            "featured_image_url": static_url(meta["featured_image"]) if meta.get("featured_image")
            else (meta.get("featured_image_url") or ""),
            "featured_image_alt": (meta.get("featured_image_alt") or "")[:200],
            "meta_title": (meta.get("meta_title") or "")[:70], "meta_description": (meta.get("meta_description") or "")[:170],
            "focus_keyword": (meta.get("focus_keyword") or "")[:120], "canonical_url": meta.get("canonical_url") or "",
            "noindex": bool(meta.get("noindex", False)), "schema_type": meta.get("schema_type", "BlogPosting"),
            "funnel_stage": meta.get("funnel_stage", "awareness"), "target_personas": list(meta.get("target_personas") or []),
            "related_guides": [str(g) for g in (meta.get("guides") or [])],
            "status": status, "published_at": _aware(meta.get("published")),
            "auto_translate": bool(meta.get("auto_translate", False)),
            "doctor_author": doctor(meta.get("author")), "reviewed_by": doctor(meta.get("reviewed_by")),
            "treatment": treatment, "content_source": BlogPost.SOURCE_MANUAL,
        }
        if desired["status"] == BlogPost.STATUS_PUBLISHED and desired["published_at"] is None:
            desired["published_at"] = None  # save() şimdi'yi yazar; sonraki koşularda DB değeri korunur

        with transaction.atomic():
            post = BlogPost.objects.filter(slug=slug).first()
            created = post is None
            if created:
                post = BlogPost(slug=slug, source_language=source_lang)
            changed = created or post.source_language != source_lang
            post.source_language = source_lang
            for f in POST_FIELDS:
                value = desired[f]
                field = BlogPost._meta.get_field(f)
                if field.is_relation:  # FK: nesne yüklemeden id karşılaştır (kategorisiz yeni kayıt hata vermesin)
                    if getattr(post, field.attname) != (value.pk if value is not None else None):
                        setattr(post, f, value)
                        changed = True
                    continue
                if f == "published_at" and value is None and post.published_at is not None:
                    continue  # dosyada tarih yoksa mevcut yayın tarihi korunur
                if getattr(post, f) != value:
                    setattr(post, f, value)
                    changed = True
            if changed:
                post.save()
                stats["posts_created" if created else "posts_updated"] += 1
            else:
                stats["unchanged"] += 1
            self._translations(post, files, stats)

    def _translations(self, post, files, stats):
        source_hash = post.compute_source_hash()
        for lang, path in sorted(files.items()):
            if lang == post.source_language:
                continue
            if lang not in LANGUAGE_META:
                self.stderr.write(f"  ! {post.slug}: bilinmeyen dil dosyası {path.name}")
                continue
            meta, body = parse_markdown(path.read_text(encoding="utf-8"))
            if not meta.get("title"):
                raise CommandError(f"{path}: title gerekli")
            tr = BlogPostTranslation.objects.filter(post=post, language_code=lang).first()
            is_new = tr is None
            if is_new:
                tr = BlogPostTranslation(post=post, language_code=lang)
            base = meta.get("slug") or slugify(meta["title"], max_length=180)
            values = {
                "title": meta["title"][:200],
                "slug": self._free_slug(BlogPostTranslation, lang, base, exclude_pk=tr.pk),
                "excerpt": meta.get("excerpt") or "", "content": render_body(body), "faq": norm_faq(meta.get("faq")),
                "featured_image_alt": (meta.get("featured_image_alt") or "")[:200],
                "meta_title": (meta.get("meta_title") or "")[:70], "meta_description": (meta.get("meta_description") or "")[:170],
                "focus_keyword": (meta.get("focus_keyword") or "")[:120],
                "status": TranslationStatus.REVIEWED, "source_hash": source_hash, "model_used": "file", "error": "",
            }
            changed = is_new
            for k, v in values.items():
                if getattr(tr, k) != v:
                    setattr(tr, k, v)
                    changed = True
            if changed:
                tr.translated_at = timezone.now()
                tr.save()
                stats["translations"] += 1
            else:
                stats["unchanged"] += 1

    # ── Dışa aktarma ──────────────────────────────────────────────────────────────────────────────────────
    def _export(self, slug):
        post = BlogPost.objects.filter(slug=slug).first()
        if post is None:
            raise CommandError(f"Yazı yok: {slug}")
        folder = self.root / "posts" / slug
        folder.mkdir(parents=True, exist_ok=True)
        n = 0
        for tr in post.translations.filter(status__in=LIVE_STATUSES).order_by("language_code"):
            front = {"title": tr.title, "slug": tr.slug, "excerpt": tr.excerpt, "meta_title": tr.meta_title,
                     "meta_description": tr.meta_description, "focus_keyword": tr.focus_keyword,
                     "featured_image_alt": tr.featured_image_alt,
                     "faq": [{"q": f["question"], "a": f["answer"]} for f in (tr.faq or [])]}
            text = "---\n" + yaml.safe_dump(front, allow_unicode=True, sort_keys=False, width=1000) + "---\n\n" \
                   + (tr.content or "").strip() + "\n"
            (folder / f"{tr.language_code}.md").write_text(text, encoding="utf-8")
            n += 1
        self.stdout.write(f"✓ {n} çeviri yazıldı → {folder}")
