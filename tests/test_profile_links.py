"""Footer / pSEO'daki hekim-sitesi linkleri ziyaretçinin dilindeki sayfaya gider (drdevrim.com /lang/<dil>/,
devrimbirikensipahi.com.tr /<dil>/); site o dili yayınlamıyorsa İngilizce, Türkçede kök."""
from django.test import override_settings

from apps.seo.common import profile_site_url

from .base import SeededTestCase

SITES = [("https://drdevrim.com", "langpath", None), ("https://devrimbirikensipahi.com.tr", "lang", None)]


class ProfileSiteLinkTests(SeededTestCase):
    def test_url_follows_each_sites_scheme_and_language_list(self):
        self.assertEqual(profile_site_url("https://drdevrim.com", "langpath", None, "de"), ("https://drdevrim.com/lang/de/", "de"))
        self.assertEqual(profile_site_url("https://drdevrim.com", "lang", None, "de"), ("https://drdevrim.com/lang/de/", "de"))  # eski mod düzeltilir
        self.assertEqual(profile_site_url("https://drdevrim.com", "langpath", None, "sv"), ("https://drdevrim.com/lang/en/", "en"))  # İsveççe yok
        self.assertEqual(profile_site_url("https://drdevrim.com", "langpath", None, "tr"), ("https://drdevrim.com/", "tr"))
        self.assertEqual(profile_site_url("https://drdevrim.com", "root", None, "fr"), ("https://drdevrim.com/lang/fr/", "fr"))  # mod verilmese de
        self.assertEqual(profile_site_url("https://devrimbirikensipahi.com.tr", "lang", None, "sv"),
                         ("https://devrimbirikensipahi.com.tr/sv/", "sv"))
        self.assertEqual(profile_site_url("https://example.org", "lang", frozenset({"de", "en"}), "fr"), ("https://example.org/en/", "en"))
        self.assertEqual(profile_site_url("https://example.org", "lang", frozenset({"de"}), "fr"), ("https://example.org/", "tr"))  # İngilizce de yok → kök
        self.assertEqual(profile_site_url("https://example.org", "root", None, "fr"), ("https://example.org/", "tr"))

    def test_env_value_parsing(self):
        from dental_tourism.settings import _profile_site

        self.assertEqual(_profile_site("https://drdevrim.com|lang"), ("https://drdevrim.com", "lang", None))
        self.assertEqual(_profile_site("https://x.org/"), ("https://x.org", "root", None))
        self.assertEqual(_profile_site(" https://x.org | langpath | de+en "), ("https://x.org", "langpath", frozenset({"de", "en"})))

    @override_settings(PROFILE_SITES=SITES)
    def test_footer_links_match_the_page_language(self):
        de = self.client.get("/de/").content.decode()
        self.assertIn('href="https://drdevrim.com/lang/de/" hreflang="de"', de)
        self.assertIn('href="https://devrimbirikensipahi.com.tr/de/" hreflang="de"', de)
        sv = self.client.get("/sv/").content.decode()
        self.assertIn('href="https://drdevrim.com/lang/en/" hreflang="en"', sv)
        self.assertIn('href="https://devrimbirikensipahi.com.tr/sv/" hreflang="sv"', sv)
        tr = self.client.get("/tr/").content.decode()
        self.assertIn('href="https://drdevrim.com/" hreflang="tr"', tr)
        self.assertIn("Dr. Devrim Biriken Sipahi", tr)
