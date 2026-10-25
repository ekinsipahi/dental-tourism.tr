"""'Aramadan dönüş' olayı: telefon / WhatsApp / harita tıklamasından sonra sekmeye geri gelen ziyaretçi
(static/js/tracker.js → contact_return) iletişim listesinde tıklamanın yanında saklanır."""
import json

from .base import SeededTestCase


class ContactReturnTests(SeededTestCase):
    def _event(self, event_type, data):
        return self.client.post("/api/tracking/event/", data=json.dumps({"event_type": event_type, "data": data}),
                                content_type="application/json")

    def test_contact_return_is_stored_next_to_the_click(self):
        from apps.tracking.models import ContactClick, TrackingEvent

        self.client.get("/")
        self._event("phone_click", {"position": "hero", "label": "Call now"})
        self._event("contact_return", {"kind": "phone", "away_seconds": 42, "likely_contacted": True,
                                       "position": "hero", "label": "Call now"})
        ret = TrackingEvent.objects.get(event_type="contact_return")
        self.assertEqual(ret.data.get("away_seconds"), 42)
        self.assertTrue(ret.data.get("likely_contacted"))
        self.assertEqual(ContactClick.objects.filter(event_type="contact_return").count(), 1)
        self.assertEqual(ContactClick.objects.count(), 2)  # tıklama + dönüş, aynı listede


class SegmentedTimeOnPageTests(SeededTestCase):
    def test_tab_switch_segments_do_not_inflate_page_views(self):
        from apps.persona.models import VisitorSession

        self.client.get("/")
        for seg, secs in ((0, 30), (1, 20), (2, 10)):  # aynı sayfa: ilk görüntüleme + iki geri dönüş
            self.client.post("/api/tracking/event/", data=json.dumps({
                "event_type": "time_on_page", "data": {"seconds": secs, "segment": seg}, "page_url": "/",
            }), content_type="application/json")
        s = VisitorSession.objects.get()
        self.assertEqual(s.total_page_views, 1)      # segmentler sayfa görüntüleme sayılmaz
        self.assertEqual(s.total_time_spent_sec, 60)  # ama aktif süre toplanır
