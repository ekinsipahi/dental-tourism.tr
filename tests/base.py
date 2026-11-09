from django.core.management import call_command
from django.test import TestCase, override_settings

def visit(client, url="/", referrer=""):
    """Gerçek tarayıcı gibi: sayfa GET'i + pageview beacon'ı (oturum ve persona kaydı beacon'da açılır)."""
    import json

    r = client.get(url, HTTP_REFERER=referrer) if referrer else client.get(url)
    client.post("/api/tracking/pageview/", data=json.dumps({"url": "http://testserver" + url, "referrer": referrer}),
                content_type="application/json")
    return r


BROWSER_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


@override_settings(AUTO_TRANSLATE_ON_PUBLISH=False, ANTHROPIC_API_KEY="", PERSONA_EXPLORATION_RATE=0.0)
class SeededTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_data", "--keywords", verbosity=0, stdout=open("/dev/null", "w"))

    def setUp(self):
        from django.core.cache import cache, caches

        cache.clear()
        caches["local"].clear()  # sitemap / bot sayfa önbelleği testler arasında sızmasın
        self.client.defaults["HTTP_USER_AGENT"] = BROWSER_UA


def fake_translation(spec, lang):
    """LLM yerine deterministik çeviri üretir."""
    out = {}
    for f in spec.fields:
        if f.kind == "faq":
            out[f.name] = [{"question": f"Q-{lang}", "answer": f"A-{lang}"}]
        elif f.kind == "slug":
            out[f.name] = f"slug {lang} test"
        else:
            out[f.name] = f"[{lang}] text"
    return out
