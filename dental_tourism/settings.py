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
            "CONN_HEALTH_CHECKS": True,
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
            "CONN_HEALTH_CHECKS": True,
            "OPTIONS": {"sslmode": config("DB_SSLMODE", default="prefer")},
        }
    }
else:
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── Cache / Session ──────────────────────────────────────────────────────────
# Redis YOK: veritabanı cache'i (tüm gunicorn işçileri arasında paylaşılır).
# Kurulumda bir kez: python manage.py createcachetable
CACHES = {"default": {"BACKEND": "django.core.cache.backends.db.DatabaseCache", "LOCATION": "django_cache",
                      "OPTIONS": {"MAX_ENTRIES": 20000}}}
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_COOKIE_AGE = 60 * 60 * 24 * 90  # 90 gün

# ── i18n — 16 dil ────────────────────────────────────────────────────────────
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

# ── Security (production) ────────────────────────────────────────────────────
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
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
PERSONA_EXPLORATION_RATE = config("PERSONA_EXPLORATION_RATE", default=0.1, cast=float)
PERSONA_MODEL_DIR = BASE_DIR / "ml_models"

# ── Email ────────────────────────────────────────────────────────────────────
EMAIL_BACKEND = (
    "django.core.mail.backends.console.EmailBackend" if DEBUG
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
