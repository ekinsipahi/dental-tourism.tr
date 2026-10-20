"""Kişisel marka: metinlerde "Dr. Devrim", tam ad navbar ve hekim kartlarında."""
from django.test import SimpleTestCase

from apps.clinics.branding import brandify

from .base import SeededTestCase


class BrandifyTests(SimpleTestCase):
    def test_keeps_local_honorific_and_clinic_name(self):
        self.assertEqual(brandify("Dr. Dt. Devrim Biriken Sipahi examines you"), "Dr. Devrim examines you")
        self.assertEqual(brandify("La Dra. Dt. Devrim Biriken Sipahi y su hijo"), "La Dra. Devrim y su hijo")
        self.assertEqual(brandify("Dr. Sipahi'nin bilgisi"), "Dr. Devrim'in bilgisi")
        self.assertEqual(brandify("la clinique Devrim Sipahi"), "la clinique Devrim Sipahi")
        self.assertEqual(brandify("Dt. Ekin Sipahi"), "Dt. Ekin Sipahi")

    def test_first_mention_keeps_full_name_and_is_idempotent(self):
        once = brandify("**Dr. Dt. Devrim Biriken Sipahi** is a dentist.", keep_full_first=True)
        self.assertEqual(once, "**Dr. Devrim** (Dr. Dt. Devrim Biriken Sipahi) is a dentist.")
        self.assertEqual(brandify(once, keep_full_first=True), once)


class BrandingPageTests(SeededTestCase):
    def test_navbar_shows_full_name_and_logo_video_with_image_fallback(self):
        html = self.client.get("/").content.decode()
        self.assertIn('class="logo-name"', html)
        self.assertIn("Dr. Dt. Devrim", html)
        self.assertIn('class="logo-video"', html)
        self.assertIn('class="logo-img"', html)  # video oynamazsa görünen logo
        self.assertIn('class="ig-float"', html)
