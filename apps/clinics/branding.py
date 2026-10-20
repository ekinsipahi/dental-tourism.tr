"""
Kişisel marka: metinlerde hekim "Dr. Devrim" olarak geçer; tam ad (Dr. Dt. Devrim Biriken Sipahi) navbar'da,
hekim kartlarında ve Hakkımızda hikâyesinin ilk cümlesinde parantez içinde görünür.

brandify("Dr. Dt. Devrim Biriken Sipahi examines you")  → "Dr. Devrim examines you"
brandify("Le **Dr Dt. Devrim Biriken Sipahi** est …", keep_full_first=True)
                                                         → "Le **Dr Devrim** (Dr Dt. Devrim Biriken Sipahi) est …"
Her dilin kendi unvanı korunur (Dr / Dra. / Dott.ssa / Д-р / الدكتورة …). Klinik adı ("clinique Devrim Sipahi")
ve unvansız geçen ad DEĞİŞMEZ; meta alanları ve hasta yorumları bu fonksiyona hiç verilmez.
"""
import re

_HON = r"(?:Dr\.|Dr|dr\.|dr|Dra\.|Dott\.ssa|Д-р|д-р|الدكتورة|د\.)"
# Tam ad / ad-soyad: "Dr. Dt. Devrim Biriken Sipahi", "Dr. Devrim Sipahi"
_FULL = re.compile(r"(?<!\()(\*\*)?(" + _HON + r")\s+(?:Dt\.\s+)?Devrim(?:\s+Biriken)?\s+Sipahi(['’](?:nin|yi|ye|den|de|yle))?(?![\w'’])(\*\*)?")
# Yalnızca soyad + iyelik: "Dr. Sipahi's", "dr Sipahis", "Dr. Sipahi'nin", "Dr. Sipahinin"
_SURNAME = re.compile(r"(" + _HON + r")\s+(?:Dt\.\s+)?Sipahi(['’]s|s|['’]nin|nin|['’]yi|['’]ye|['’]den)?(?![\w])")
_SUFFIX = {"'s": "'s", "’s": "’s", "s": "s", "'nin": "'in", "’nin": "’in", "nin": "in", "'yi": "'i", "’yi": "’i",
           "'ye": "'e", "’ye": "’e", "'den": "'den", "’den": "’den", "'de": "'de", "’de": "’de", "'yle": "'le", "’yle": "’le"}


def brandify(text, keep_full_first=False):
    if not text or ("Sipahi" not in text):
        return text
    state = {"first": keep_full_first}

    def full(m):
        b1, hon, suf, b2 = m.group(1) or "", m.group(2), m.group(3) or "", m.group(4) or ""
        out = f"{b1}{hon} Devrim{_SUFFIX.get(suf, suf)}{b2}"
        if state["first"]:
            state["first"] = False
            out = f"{b1}{hon} Devrim{b2} ({m.group(0).strip('*')})"
        return out

    text = _FULL.sub(full, text)
    return _SURNAME.sub(lambda m: f"{m.group(1)} Devrim{_SUFFIX.get(m.group(2) or '', '')}", text)


def brandify_data(value, keep_full_first=False):
    """str / list / dict (SSS listeleri, JSON alanları) içinde özyinelemeli uygular."""
    if isinstance(value, str):
        return brandify(value, keep_full_first)
    if isinstance(value, list):
        return [brandify_data(v) for v in value]
    if isinstance(value, dict):
        return {k: brandify_data(v) for k, v in value.items()}
    return value
