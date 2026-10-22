import sys
from pathlib import Path

from decouple import Csv, config

from .languages import LANGUAGE_META, LANGUAGES  # noqa: F401  (LANGUAGES Django ayarı)

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY", default="django-insecure-change-me")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())
CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default="", cast=Csv())
# Render: servisin kendi alan adı (xxx.onrender.com) otomatik eklenir
_render_host = config("RENDER_EXTERNAL_HOSTNAME", default="")
if _render_host:
    ALLOWED_HOSTS = [*ALLOWED_HOSTS, _render_host]
    CSRF_TRUSTED_ORIGINS = [*CSRF_TRUSTED_ORIGINS, f"https://{_render_host}"]

DJANGO_APPS = [
    "apps.core.admin_config.DentalAdminConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.humanize",
]
THIRD_PARTY_APPS = [
    "rest_framework",
]
LOCAL_APPS = [
    "apps.core",
    "apps.localization",
    "apps.clinics",
    "apps.treatments",
    "apps.blog",
    "apps.seo",
    "apps.persona",
    "apps.tracking",
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.core.middleware.BotDetectionMiddleware",
    "apps.core.middleware.BotPageCacheMiddleware",   # botlara (Google, Bing …) sayfayı bellekten ver: 0 DB sorgusu
    "apps.tracking.middleware.TrackingMiddleware",
    "apps.persona.middleware.PersonaMiddleware",
    "apps.seo.middleware.RedirectFallbackMiddleware",
]

ROOT_URLCONF = "dental_tourism.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.site_context",
                "apps.persona.context_processors.persona_context",
            ],
        },
    },
]

WSGI_APPLICATION = "dental_tourism.wsgi.application"

# ── Database ─────────────────────────────────────────────────────────────────
# Öncelik: DATABASE_URL (Render/Supabase) → DB_ENGINE=postgres + DB_* → SQLite
_db_url = config("DATABASE_URL", default="")
if _db_url:
    from urllib.parse import unquote, urlparse

    _u = urlparse(_db_url)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": (_u.path or "/postgres").lstrip("/"),
            "USER": unquote(_u.username or ""),
            "PASSWORD": unquote(_u.password or ""),
            "HOST": _u.hostname,
            "PORT": str(_u.port or 5432),
            "CONN_MAX_AGE": config("DB_CONN_MAX_AGE", default=60, cast=int),
            "CONN_HEALTH_CHECKS": False,  # her istekte uzak DB'ye fazladan "SELECT 1" gitmesin (bağlantı 60 sn'de yenilenir)
            "OPTIONS": {"sslmode": config("DB_SSLMODE", default="require")},
        }
    }
elif config("DB_ENGINE", default="sqlite") == "postgres":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config("DB_NAME"),
            "USER": config("DB_USER"),
            "PASSWORD": config("DB_PASSWORD"),
            "HOST": config("DB_HOST", default="localhost"),
            "PORT": config("DB_PORT", default="5432"),
            "CONN_MAX_AGE": config("DB_CONN_MAX_AGE", default=60, cast=int),
            "CONN_HEALTH_CHECKS": False,
            "OPTIONS": {"sslmode": config("DB_SSLMODE", default="prefer")},
        }
    }
else:
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── Cache / Session ──────────────────────────────────────────────────────────
# Önbellek VERİTABANINDA DEĞİL. (Eskiden DatabaseCache'ti: her cache.get başka bölgedeki Supabase'e bir gidiş-dönüş
# demekti — istek başına 5-6 çağrı → sayfa 5 sn, Supabase egress limiti.)
#   REDIS_URL varsa → Redis (Render Key Value, web ile aynı bölge, tüm gunicorn işçileri paylaşır: admin'de yapılan
#                     değişiklik ve persona/aşama güncellemesi anında her işçide görünür)
#   yoksa          → süreç içi bellek (LocMem). İşçi başına ayrıdır: cache.delete yalnızca o işçide çalışır, diğer
#                     işçi TTL kadar (en çok 5 dk) eski değeri gösterebilir. Doğruluk bozulmaz, gecikir.
#   "local"        → her zaman süreç içi: sitemap gibi büyük bloblar Redis'i (25 MB) doldurmasın.
#   "sessions"     → aynı arka uç, commit öneki YOK: oturum önbelleği deploy'larda yeniden kurulmasın / birikmesin.
# KEY_PREFIX = commit → her deploy temiz önbellekle başlar (sitemap/llms.txt yeni dil ve sayfaları hemen görür).
# Oturumlar cached_db: önbellekte bulunamazsa DB'den okunur, kimse oturumdan düşmez.
_CACHE_PREFIX = config("RENDER_GIT_COMMIT", default="")[:12]
REDIS_URL = config("REDIS_URL", default="")


def _cache(location, prefix=_CACHE_PREFIX, shared=True):
    if shared and REDIS_URL:
        # Redis koparsa sayfa 500 vermesin: hata = önbellekte yok (dental_tourism/cache_backends.py)
        return {"BACKEND": "dental_tourism.cache_backends.ResilientRedisCache", "LOCATION": REDIS_URL, "KEY_PREFIX": prefix}
    return {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": location, "KEY_PREFIX": prefix,
            "OPTIONS": {"MAX_ENTRIES": 20000}}


CACHES = {
    "default": _cache("dental-default"),
    "sessions": _cache("dental-sessions", prefix=""),
    "local": {**_cache("dental-local", shared=False), "OPTIONS": {"MAX_ENTRIES": 4000}},  # sitemap + bot sayfa önbelleği
}
# Oturum: Redis varsa cached_db ("sessions" alias'ı); yoksa doğrudan DB — süreç içi önbellekte oturum tutmak iki işçi
# arasında tutarsızlık (kayıp güncelleme) yaratır. Anonim ziyaretçide oturum zaten yüklenmez (persona önizlemesi imzalı
# çerezde, bkz. apps/persona/engine.py _forced) → DB'ye ek sorgu yok.
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db" if REDIS_URL else "django.contrib.sessions.backends.db"
SESSION_CACHE_ALIAS = "sessions"
SESSION_COOKIE_AGE = 60 * 60 * 24 * 90  # 90 gün

# ── i18n — 17 dil ────────────────────────────────────────────────────────────
LANGUAGE_CODE = config("DEFAULT_LANGUAGE", default="en")
TIME_ZONE = "Europe/Istanbul"
USE_I18N = True
USE_TZ = True
LOCALE_PATHS = [BASE_DIR / "locale"]
LANGUAGE_COOKIE_NAME = "django_language"
LANGUAGE_COOKIE_AGE = 60 * 60 * 24 * 365

# ── Static / Media ───────────────────────────────────────────────────────────
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage" if DEBUG
        else "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.AnonRateThrottle"],
    "DEFAULT_THROTTLE_RATES": {"anon": "200/min"},
}

# Testler .env'deki DEBUG'dan bağımsız: manifest'siz statik, HTTPS yönlendirmesi yok
TESTING = len(sys.argv) > 1 and sys.argv[1] == "test"
if TESTING:
    STORAGES["staticfiles"] = {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}

# ── Security (production) ────────────────────────────────────────────────────
if not DEBUG and not TESTING:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SECURE_REDIRECT_EXEMPT = [r"^healthz$"]  # Render iç sağlık kontrolü düz HTTP ile gelir
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
    SECURE_CONTENT_TYPE_NOSNIFF = True

# ── Site ─────────────────────────────────────────────────────────────────────
SITE_NAME = config("SITE_NAME", default="dentaltourism.tr")
SITE_DOMAIN = config("SITE_DOMAIN", default="dentaltourism.tr")
SITE_URL = config("SITE_URL", default="https://dentaltourism.tr").rstrip("/")
# [(url, mod)] — mod: root (her dilde ana sayfa) · en (tr→kök, diğerleri /en/) · lang (/<dil>/)
PROFILE_SITES = [(u.split("|")[0].strip().rstrip("/"), (u.split("|") + ["root"])[1].strip())
                 for u in config("PROFILE_SITES", default="").split(",") if u.strip()]
PARTNER_AGENCY_URL = config("PARTNER_AGENCY_URL", default="")
IPINFO_TOKEN = config("IPINFO_TOKEN", default="")  # ipinfo.io — iletişim tıklamalarında ülke/şehir/sağlayıcı
BACKGROUND_WORKERS = config("BACKGROUND_WORKERS", default=2, cast=int)
BACKGROUND_QUEUE_LIMIT = config("BACKGROUND_QUEUE_LIMIT", default=200, cast=int)
PRIMARY_CLINIC_SLUG = config("PRIMARY_CLINIC_SLUG", default="")

# ── Claude content machine ───────────────────────────────────────────────────
ANTHROPIC_API_KEY = config("ANTHROPIC_API_KEY", default="")
CONTENT_MACHINE_MODEL = config("CONTENT_MACHINE_MODEL", default="claude-opus-5-5")
TRANSLATION_EFFORT = config("TRANSLATION_EFFORT", default="medium")
GENERATION_EFFORT = config("GENERATION_EFFORT", default="high")
AUTO_TRANSLATE_ON_PUBLISH = config("AUTO_TRANSLATE_ON_PUBLISH", default=True, cast=bool)

# ── Persona ML ───────────────────────────────────────────────────────────────
PERSONA_ML_MIN_EXPOSURES = config("PERSONA_ML_MIN_EXPOSURES", default=400, cast=int)
PERSONA_ML_MIN_CONVERSIONS = config("PERSONA_ML_MIN_CONVERSIONS", default=25, cast=int)
# False → GÖZLEM MODU: motor sayar / teşhis eder / admin'e yazar ama arayüz (renk, hero, mesaj) DEĞİŞMEZ.
# Önce gerçek konuşmalardan etiket toplanır; sistem kanıtlanınca açılır.
PERSONA_UI_ENABLED = config("PERSONA_UI_ENABLED", default=False, cast=bool)
PERSONA_EXPLORATION_RATE = config("PERSONA_EXPLORATION_RATE", default=0.1, cast=float)
PERSONA_MODEL_DIR = BASE_DIR / "ml_models"

# ── Email ────────────────────────────────────────────────────────────────────
# Başta e-posta YOK: lead formları ve yorumlar yalnızca serverda (admin → Lead'ler / Yorumlar) toplanır.
# Açmak için .env / Render: EMAIL_ENABLED=True + EMAIL_HOST…
EMAIL_ENABLED = config("EMAIL_ENABLED", default=False, cast=bool)
EMAIL_BACKEND = (
    "django.core.mail.backends.dummy.EmailBackend" if not EMAIL_ENABLED
    else "django.core.mail.backends.console.EmailBackend" if DEBUG
    else "django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = config("EMAIL_HOST", default="localhost")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="info@dentaltourism.tr")
SERVER_EMAIL = EMAIL_HOST_USER or DEFAULT_FROM_EMAIL
LEAD_NOTIFY_EMAIL = config("LEAD_NOTIFY_EMAIL", default="")

# ── Ad platforms / analytics ─────────────────────────────────────────────────
META_PIXEL_ID = config("META_PIXEL_ID", default="")
META_API_TOKEN = config("META_API_TOKEN", default="")
GOOGLE_ADS_CUSTOMER_ID = config("GOOGLE_ADS_CUSTOMER_ID", default="")
GOOGLE_GTAG_ID = config("GOOGLE_GTAG_ID", default="")
GOOGLE_ADS_CONVERSION = config("GOOGLE_ADS_CONVERSION", default="")
GOOGLE_SITE_VERIFICATION = config("GOOGLE_SITE_VERIFICATION", default="")
BING_SITE_VERIFICATION = config("BING_SITE_VERIFICATION", default="")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {"apps": {"handlers": ["console"], "level": "INFO"}},
}
