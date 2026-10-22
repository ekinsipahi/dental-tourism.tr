"""
"İlk gelende belleğe al": herkes için aynı olan okuma sonuçları (slug çözümü, dil slug'ları, ilgili tedaviler,
teklifler, menü listeleri …) süreç içi bellekte tutulur; her istekte Supabase'e sorulmaz.

  memo("key", 300, lambda: pahalı_sorgu(), model=Treatment)

model verilirse anahtar o modelin "sürüm" sayacını içerir: model ya da çevirisi kaydedildiğinde (admin, seed komutu)
sayaç artar ve aynı işçideki eski girişler anında geçersizleşir; diğer işçi TTL (en çok 5 dk) kadar eskisini gösterir.
"""
from django.core.cache import caches

TTL = 300


def _ver(model):
    label = model._meta.label_lower if hasattr(model, "_meta") else str(model)
    return caches["local"].get(f"ver:{label}", 0)


def bump(model):
    """Model (ya da çevirisi) kaydedildi / silindi → bu modele bağlı tüm memo girişleri geçersiz."""
    label = model._meta.label_lower
    cache = caches["local"]
    cache.set(f"ver:{label}", cache.get(f"ver:{label}", 0) + 1, None)


def memo(key, ttl, fn, model=None):
    cache = caches["local"]
    full = f"memo:{_ver(model) if model is not None else 0}:{key}"
    hit = cache.get(full)
    if hit is not None:
        return hit[0]
    value = fn()
    cache.set(full, (value,), ttl)  # tuple sarmalı: None sonucu da ("yok") ezberlenir
    return value
