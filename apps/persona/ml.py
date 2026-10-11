"""
Supervised conversion modeli.

Soru: "Bu bağlamdaki ziyaretçiye X persona varyantını gösterirsem dönüşüm olasılığı nedir?"
  P(convert | bağlam özellikleri, gösterilen persona)

Eğitim verisi: PersonaExposure (bandit'in topladığı randomize deneyler — bu sayede
model nedensel etkiyi öğrenebilir; sadece kural etiketlerini ezberlemez).

Model: DictVectorizer + (LogisticRegression | GradientBoosting) — 5-fold CV ROC-AUC ile seçilir.
Ayrıca IPS (inverse propensity scoring) ile yeni policy'nin offline değeri tahmin edilir:
model, loglanan bandit policy'sinden daha iyi değilse AKTİF EDİLMEZ.
"""
import logging
import time
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from .features import with_arm
from .models import MLModelVersion, PersonaExposure

logger = logging.getLogger(__name__)

CONVERSION_WINDOW = timedelta(hours=24)


def build_dataset():
    cutoff = timezone.now() - CONVERSION_WINDOW
    qs = PersonaExposure.objects.exclude(policy="forced").filter(Q(created_at__lt=cutoff) | Q(converted=True))
    rows, y, props, arms = [], [], [], []
    for e in qs.iterator():
        if not e.features:
            continue
        rows.append(with_arm(e.features, e.persona))
        y.append(1 if e.converted else 0)
        props.append(max(e.propensity or 0.0, 0.01))
        arms.append(e.persona)
    return rows, y, props, arms


def _candidates():
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.feature_extraction import DictVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler

    return {
        "logreg": Pipeline([
            ("vec", DictVectorizer(sparse=False)),
            ("scale", StandardScaler()),
            ("clf", LogisticRegression(max_iter=3000, C=0.5)),
        ]),
        "gbm": Pipeline([
            ("vec", DictVectorizer(sparse=False)),
            ("clf", GradientBoostingClassifier(n_estimators=150, max_depth=3, learning_rate=0.05,
                                               subsample=0.8, random_state=42)),
        ]),
    }


def _snips_value(model, rows, y, props, arms):
    """Self-normalized IPS: yeni policy'nin offline dönüşüm oranı tahmini (IPS'ten daha az varyanslı).
    Döner: (tahmini oran, eşleşen örnek sayısı)."""
    from .bandit import ARMS

    num = den = 0.0
    matched = 0
    for row, r, p, logged_arm in zip(rows, y, props, arms):
        base = {k: v for k, v in row.items() if not k.startswith("arm")}
        scores = model.predict_proba([with_arm(base, a) for a in ARMS])[:, 1]
        if ARMS[int(scores.argmax())] == logged_arm:
            w = 1.0 / max(p, 0.02)
            num += w * r
            den += w
            matched += 1
    return (num / den if den else 0.0), matched


def train(force=False) -> dict:
    import joblib
    from sklearn.model_selection import StratifiedKFold, cross_val_score

    rows, y, props, arms = build_dataset()
    n, pos = len(rows), sum(y)
    if not force and (n < settings.PERSONA_ML_MIN_EXPOSURES or pos < settings.PERSONA_ML_MIN_CONVERSIONS):
        msg = (f"Yetersiz veri: {n} exposure / {pos} dönüşüm "
               f"(gerekli {settings.PERSONA_ML_MIN_EXPOSURES} / {settings.PERSONA_ML_MIN_CONVERSIONS}). "
               "Bandit öğrenmeye devam ediyor.")
        logger.info(msg)
        return {"trained": False, "reason": msg, "samples": n, "positives": pos}
    if pos < 5 or pos == n:
        return {"trained": False, "reason": "Tek sınıflı veri.", "samples": n, "positives": pos}

    from sklearn.model_selection import train_test_split

    cv = StratifiedKFold(n_splits=min(5, pos), shuffle=True, random_state=42)
    results = {}
    for name, pipe in _candidates().items():
        auc = cross_val_score(pipe, rows, y, cv=cv, scoring="roc_auc").mean()
        results[name] = auc
    best_name = max(results, key=results.get)

    # Policy değerlendirmesi modelin GÖRMEDİĞİ veride yapılır (aksi halde aşırı iyimser olur)
    idx = list(range(n))
    tr, te = train_test_split(idx, test_size=0.3, random_state=42, stratify=y)
    holdout_model = _candidates()[best_name].fit([rows[i] for i in tr], [y[i] for i in tr])
    te_rows, te_y = [rows[i] for i in te], [y[i] for i in te]
    logged_value = sum(te_y) / len(te_y)
    ips_value, matched = _snips_value(holdout_model, te_rows, te_y, [props[i] for i in te], [arms[i] for i in te])
    model = _candidates()[best_name].fit(rows, y)
    activate = results[best_name] >= 0.6 and matched >= 50 and ips_value >= logged_value * 1.05

    version = timezone.now().strftime("%Y%m%d_%H%M%S")
    model_dir = Path(settings.PERSONA_MODEL_DIR)
    model_dir.mkdir(parents=True, exist_ok=True)
    path = model_dir / f"persona_conversion_{version}.joblib"
    joblib.dump(model, path)

    if activate:
        MLModelVersion.objects.filter(is_active=True).update(is_active=False)
    mv = MLModelVersion.objects.create(
        version=version, kind="conversion", training_samples=n, positives=pos,
        accuracy=results[best_name], model_path=str(path), is_active=activate,
        feature_names=list(model.named_steps["vec"].feature_names_),
        class_names=[0, 1],
        metrics={"cv_auc": results, "chosen": best_name, "holdout_logged_rate": round(logged_value, 4),
                 "holdout_snips_model_rate": round(ips_value, 4), "holdout_matched": matched},
    )
    _cache["loaded_at"] = 0  # yeniden yüklensin
    logger.info("persona ML v%s AUC=%.3f SNIPS=%.4f vs logged=%.4f active=%s",
                version, results[best_name], ips_value, logged_value, activate)
    return {"trained": True, "version": mv.version, "active": activate, "metrics": mv.metrics,
            "samples": n, "positives": pos}


# ── Çalışma zamanı ────────────────────────────────────────────────────────────
_cache = {"loaded_at": 0, "model": None, "version": None}
RELOAD_SECONDS = 600


def active_model():
    """Aktif modeli (varsa) döner; 10 dakikada bir DB'den kontrol eder."""
    if time.time() - _cache["loaded_at"] < RELOAD_SECONDS:
        return _cache["model"], _cache["version"]
    _cache["loaded_at"] = time.time()
    mv = MLModelVersion.objects.filter(is_active=True, kind="conversion").first()
    if mv is None:
        _cache.update(model=None, version=None)
    elif mv.version != _cache["version"]:
        try:
            import joblib

            _cache.update(model=joblib.load(mv.model_path), version=mv.version)
        except Exception:  # noqa: BLE001
            logger.exception("ML model yüklenemedi: %s", mv.model_path)
            _cache.update(model=None, version=None)
    return _cache["model"], _cache["version"]


def predict_arms(model, features, arms):
    batch = [with_arm(features, a) for a in arms]
    probs = model.predict_proba(batch)[:, 1]
    return dict(zip(arms, (float(p) for p in probs)))
