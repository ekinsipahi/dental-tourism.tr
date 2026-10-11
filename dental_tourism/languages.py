"""
Dil konfigürasyonu — tek kaynak.

Türkiye'ye diş turizmi için gelen ana pazarlar baz alınarak 16 dil seçildi.
Yeni dil eklemek için:
  1. Aşağıya bir satır ekleyin
  2. python manage.py makemessages -l <kod> && python manage.py translate_ui --lang <kod>
  3. python manage.py translate_content --missing --lang <kod>

Alanlar:
  native          Dilin kendi dilindeki adı (dil seçicide gösterilir)
  flag            Bayrak emojisi
  dir             ltr / rtl
  hreflang        hreflang değeri
  markets         Bu dili konuşan hedef ülkeler (ISO-3166) — fiyat karşılaştırma sayfaları
  currency/symbol Karşılaştırma fiyatlarında kullanılan yerel para birimi
  compare_country Fiyat karşılaştırmasında "evdeki" ülke adı (o dilde)
  turkey/istanbul Anahtar kelime üretiminde kullanılan yer isimleri (o dilde)
"""

LANGUAGE_META = {
    "en": {"name": "English", "native": "English", "flag": "🇬🇧", "dir": "ltr", "hreflang": "en",
           "markets": ["GB", "IE", "US", "CA", "AU", "NZ"], "currency": "GBP", "symbol": "£",
           "compare_country": "the UK", "turkey": "Turkey", "istanbul": "Istanbul"},
    "de": {"name": "German", "native": "Deutsch", "flag": "🇩🇪", "dir": "ltr", "hreflang": "de",
           "markets": ["DE", "AT", "CH"], "currency": "EUR", "symbol": "€",
           "compare_country": "Deutschland", "turkey": "Türkei", "istanbul": "Istanbul"},
    "nl": {"name": "Dutch", "native": "Nederlands", "flag": "🇳🇱", "dir": "ltr", "hreflang": "nl",
           "markets": ["NL", "BE"], "currency": "EUR", "symbol": "€",
           "compare_country": "Nederland", "turkey": "Turkije", "istanbul": "Istanbul"},
    "fr": {"name": "French", "native": "Français", "flag": "🇫🇷", "dir": "ltr", "hreflang": "fr",
           "markets": ["FR", "BE", "CH"], "currency": "EUR", "symbol": "€",
           "compare_country": "France", "turkey": "Turquie", "istanbul": "Istanbul"},
    "it": {"name": "Italian", "native": "Italiano", "flag": "🇮🇹", "dir": "ltr", "hreflang": "it",
           "markets": ["IT", "CH"], "currency": "EUR", "symbol": "€",
           "compare_country": "Italia", "turkey": "Turchia", "istanbul": "Istanbul"},
    "es": {"name": "Spanish", "native": "Español", "flag": "🇪🇸", "dir": "ltr", "hreflang": "es",
           "markets": ["ES"], "currency": "EUR", "symbol": "€",
           "compare_country": "España", "turkey": "Turquía", "istanbul": "Estambul"},
    "pl": {"name": "Polish", "native": "Polski", "flag": "🇵🇱", "dir": "ltr", "hreflang": "pl",
           "markets": ["PL"], "currency": "PLN", "symbol": "zł",
           "compare_country": "Polska", "turkey": "Turcja", "istanbul": "Stambuł"},
    "ru": {"name": "Russian", "native": "Русский", "flag": "🇷🇺", "dir": "ltr", "hreflang": "ru",
           "markets": ["RU", "KZ", "BY"], "currency": "EUR", "symbol": "€",
           "compare_country": "Европа", "turkey": "Турция", "istanbul": "Стамбул"},
    "uk": {"name": "Ukrainian", "native": "Українська", "flag": "🇺🇦", "dir": "ltr", "hreflang": "uk",
           "markets": ["UA"], "currency": "EUR", "symbol": "€",
           "compare_country": "Європа", "turkey": "Туреччина", "istanbul": "Стамбул"},
    "ar": {"name": "Arabic", "native": "العربية", "flag": "🇸🇦", "dir": "rtl", "hreflang": "ar",
           "markets": ["SA", "AE", "IQ", "KW", "QA", "BH", "OM"], "currency": "USD", "symbol": "$",
           "compare_country": "دول الخليج", "turkey": "تركيا", "istanbul": "إسطنبول"},
    "sv": {"name": "Swedish", "native": "Svenska", "flag": "🇸🇪", "dir": "ltr", "hreflang": "sv",
           "markets": ["SE"], "currency": "SEK", "symbol": "kr",
           "compare_country": "Sverige", "turkey": "Turkiet", "istanbul": "Istanbul"},
    "da": {"name": "Danish", "native": "Dansk", "flag": "🇩🇰", "dir": "ltr", "hreflang": "da",
           "markets": ["DK"], "currency": "DKK", "symbol": "kr",
           "compare_country": "Danmark", "turkey": "Tyrkiet", "istanbul": "Istanbul"},
    "no": {"name": "Norwegian", "native": "Norsk", "flag": "🇳🇴", "dir": "ltr", "hreflang": "no",
           "markets": ["NO"], "currency": "NOK", "symbol": "kr",
           "compare_country": "Norge", "turkey": "Tyrkia", "istanbul": "Istanbul"},
    "ro": {"name": "Romanian", "native": "Română", "flag": "🇷🇴", "dir": "ltr", "hreflang": "ro",
           "markets": ["RO", "MD"], "currency": "EUR", "symbol": "€",
           "compare_country": "România", "turkey": "Turcia", "istanbul": "Istanbul"},
    "az": {"name": "Azerbaijani", "native": "Azərbaycanca", "flag": "🇦🇿", "dir": "ltr", "hreflang": "az",
           "markets": ["AZ"], "currency": "AZN", "symbol": "₼",
           "compare_country": "Azərbaycan", "turkey": "Türkiyə", "istanbul": "İstanbul"},
    "tr": {"name": "Turkish", "native": "Türkçe", "flag": "🇹🇷", "dir": "ltr", "hreflang": "tr",
           "markets": ["TR", "DE", "NL"], "currency": "EUR", "symbol": "€",
           "compare_country": "Avrupa", "turkey": "Türkiye", "istanbul": "İstanbul"},
}

LANGUAGES = [(code, meta["native"]) for code, meta in LANGUAGE_META.items()]
LANGUAGE_CODES = list(LANGUAGE_META)
