"""
Kalıcı ziyaretçi kimliği (dt_vid).

* Sunucu ilk sayfa isteğinde 400 günlük birinci taraf çerez koyar (JS'siz de çalışır).
* tracker.js aynı değeri localStorage'a yedekler; çerez silinirse localStorage'dan geri yükler ve
  her olayla birlikte `vid` olarak gönderir.
* Oturum (sessionid) değişse bile aynı kişi tanınır: persona geçmişi, reklam atfı (gclid/fbclid/utm),
  ziyaret sayısı ve dönüşümler birleşir.
"""
import re
import uuid

COOKIE = "dt_vid"
MAX_AGE = 60 * 60 * 24 * 400
_VALID = re.compile(r"^[a-f0-9]{32}$")


def clean(value):
    value = (value or "").strip().lower()
    return value if _VALID.match(value) else ""


def get_visitor_id(request):
    vid = getattr(request, "_dt_vid", None)
    if vid is None:
        vid = clean(request.COOKIES.get(COOKIE)) or clean(request.headers.get("X-DT-VID"))
        request._dt_vid = vid
    return vid


def ensure_visitor_id(request):
    """Çerez yoksa yeni kimlik üretir (yanıtta çerez olarak yazılır)."""
    vid = get_visitor_id(request)
    if not vid:
        vid = uuid.uuid4().hex
        request._dt_vid = vid
        request._dt_vid_new = True
    return vid


def set_cookie(request, response):
    vid = getattr(request, "_dt_vid", "")
    if vid and (getattr(request, "_dt_vid_new", False) or request.COOKIES.get(COOKIE) != vid):
        response.set_cookie(COOKIE, vid, max_age=MAX_AGE, samesite="Lax", secure=request.is_secure(), httponly=False)
    return response
