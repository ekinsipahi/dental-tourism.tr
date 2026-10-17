"""
Tarayıcı saat dilimi → ülke. IP proxy/VPN'den geçtiğinde (Zscaler, iCloud Private Relay, kurumsal ağ …)
ipinfo proxy'nin ülkesini döner; tarayıcının saat dilimi (Intl API) ise cihazın gerçek konumunu gösterir.
"""
from functools import lru_cache


@lru_cache(maxsize=1)
def _tz_map():
    import pytz

    return {tz: cc for cc, zones in pytz.country_timezones.items() for tz in zones}


def tz_country(tz: str) -> str:
    return _tz_map().get(tz or "", "")


def is_valid_tz(tz) -> bool:
    return isinstance(tz, str) and tz in _tz_map()
