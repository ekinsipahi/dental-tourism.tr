"""
Thompson Sampling — segment bazlı Beta-Bernoulli bandit.

Her kol (arm) bir persona varyantıdır, 'unknown' = varsayılan (kişiselleştirilmemiş) sayfa.
Böylece sistem kişiselleştirmenin varsayılandan GERÇEKTEN daha iyi dönüştürüp
dönüştürmediğini de öğrenir.

Hiyerarşik backoff: segmentte az veri varsa, global oran sahte-gözlem (pseudo-count)
olarak eklenir → yeni segmentler sıfırdan başlamaz.
"""
import random

from django.core.cache import cache
from django.db.models import F, Sum

from .models import PERSONA_UNKNOWN, PERSONAS, PersonaArmStat

ARMS = [PERSONA_UNKNOWN] + PERSONAS
GLOBAL = "__global__"
PRIOR_STRENGTH = 20       # global orandan kaç sahte gözlem
PRIOR_FLOOR = 0.15         # inference olasılığı 0 olan kola da şans tanı
PRIOR_POWER = 2.0          # soğuk başlangıçta inference'ın ağırlığı
PRIOR_HALF_LIFE = 1000     # persona seviyesinde bu kadar gösterimden sonra inference etkisi yarıya iner
STATS_CACHE_TTL = 60


def _levels(segment):
    from .features import backoff_key

    return [segment, backoff_key(segment), GLOBAL]


def _load_stats(segment):
    key = f"bandit:stats:{segment}"
    stats = cache.get(key)
    if stats is None:
        rows = PersonaArmStat.objects.filter(segment__in=_levels(segment))
        stats = {(r.segment, r.persona): (r.impressions, r.conversions) for r in rows}
        cache.set(key, stats, STATS_CACHE_TTL)
    return stats


def arm_params(segment):
    """Hiyerarşik Beta öncülü: global → persona seviyesi → segment."""
    stats = _load_stats(segment)
    seg, mid, top = _levels(segment)
    params = {}
    for arm in ARMS:
        g_imp, g_conv = stats.get((top, arm), (0, 0))
        g_rate = (g_conv + 1) / (g_imp + 30)
        m_imp, m_conv = stats.get((mid, arm), (0, 0))
        m_rate = (m_conv + PRIOR_STRENGTH * g_rate) / (m_imp + PRIOR_STRENGTH)
        s_imp, s_conv = stats.get((seg, arm), (0, 0))
        alpha = 1 + s_conv + PRIOR_STRENGTH * m_rate
        beta = 1 + (s_imp - s_conv) + PRIOR_STRENGTH * (1 - m_rate)
        params[arm] = (alpha, beta)
    return params


def _prior_power(segment):
    """Veri arttıkça inference (kural/niyet) etkisi azalır, öğrenilen dönüşüm oranları belirleyici olur."""
    from .features import backoff_key

    stats = _load_stats(segment)
    mid = backoff_key(segment)
    n = max(sum(imp for (seg, _), (imp, _c) in stats.items() if seg == level) for level in (segment, mid))
    return PRIOR_POWER * PRIOR_HALF_LIFE / (PRIOR_HALF_LIFE + n)


def _score(arm, theta, probs, power):
    return theta * (PRIOR_FLOOR + probs.get(arm, 0.0)) ** power


def choose(segment, probs, simulations=200, epsilon=None):
    """Döner: (seçilen arm, propensity tahmini).

    Thompson Sampling × inference öncülü (veri arttıkça zayıflar) + epsilon kadar
    tamamen rastgele keşif (ML modeli ve IPS değerlendirmesi için gerekli çeşitlilik).
    """
    from django.conf import settings

    eps = settings.PERSONA_EXPLORATION_RATE if epsilon is None else epsilon
    params = arm_params(segment)
    power = _prior_power(segment)

    def draw():
        return max(ARMS, key=lambda a: _score(a, random.betavariate(*params[a]), probs, power))

    pick = random.choice(ARMS) if random.random() < eps else draw()
    # Propensity — Monte Carlo ile bu kolun seçilme olasılığı (offline değerlendirme için)
    wins = sum(draw() == pick for _ in range(simulations))
    propensity = (1 - eps) * wins / simulations + eps / len(ARMS)
    return pick, max(propensity, 1 / (simulations * 2))


def record_impression(segment, arm):
    for seg in _levels(segment):
        obj, _ = PersonaArmStat.objects.get_or_create(segment=seg, persona=arm)
        PersonaArmStat.objects.filter(pk=obj.pk).update(impressions=F("impressions") + 1)
    cache.delete(f"bandit:stats:{segment}")


def undo_impression(segment, arm):
    PersonaArmStat.objects.filter(segment__in=_levels(segment), persona=arm, impressions__gt=0) \
        .update(impressions=F("impressions") - 1)
    cache.delete(f"bandit:stats:{segment}")


def record_conversion(segment, arm):
    for seg in _levels(segment):
        PersonaArmStat.objects.filter(segment=seg, persona=arm).update(conversions=F("conversions") + 1)
    cache.delete(f"bandit:stats:{segment}")


def summary():
    """Dashboard için: global kol performansı + kazanma olasılığı."""
    params = arm_params(GLOBAL)
    rows = {r.persona: r for r in PersonaArmStat.objects.filter(segment=GLOBAL)}
    wins = {a: 0 for a in ARMS}
    for _ in range(2000):
        draws = {a: random.betavariate(1 + (rows[a].conversions if a in rows else 0),
                                       1 + ((rows[a].impressions - rows[a].conversions) if a in rows else 0))
                 for a in ARMS}
        wins[max(draws, key=draws.get)] += 1
    total_imp = PersonaArmStat.objects.filter(segment=GLOBAL).aggregate(s=Sum("impressions"))["s"] or 0
    return [{
        "persona": a,
        "impressions": rows[a].impressions if a in rows else 0,
        "conversions": rows[a].conversions if a in rows else 0,
        "rate": round(rows[a].rate * 100, 2) if a in rows else 0.0,
        "p_best": round(wins[a] / 2000 * 100, 1),
        "share": round((rows[a].impressions / total_imp * 100) if a in rows and total_imp else 0, 1),
        "alpha_beta": params[a],
    } for a in ARMS]
