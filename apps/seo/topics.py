"""
Konu (topic) sayfaları — kullanıcının keyword listelerinden üretilen programatik SEO sayfaları.
URL: /<dil>/<guide segmenti>/<dile özel slug>/  (EN: /guide/<slug>/)   — 16 dil, hepsi sitemap'te, FİYAT RAKAMI YOK.

İçerik kaynağı:
  * EN (kaynak)          → bu dosyadaki "en" sözlüğü
  * Diğer 15 dil         → apps/seo/topic_content/<dil>.json
  * Veritabanına yükleme → python manage.py seed_topics   (sonra her şey admin'den düzenlenebilir: SEO konu sayfaları)

Keyword → sayfa haritası ayrıca docs/programmatic-seo-keywords.md içinde.

Liste 1 grupları                          Liste 2 grupları
  G1 dental turizm/klinik → dental-care-turkey      L2-G1 dental tourism (3.6K) → dental-tourism (pillar)
  G2 genel fiyat          → /prices/                L2-G2 best clinic istanbul  → best-dental-clinic-istanbul
  G3 tedavi fiyatı        → /prices/<tedavi>/       L2-G3 best implant/veneer…  → /packages/<tedavi>/ (+ tedavi sayfası)
  G4 tedavi / best for    → /packages/<tedavi>/     L2-G4 best country          → best-country-dental-tourism
  G5 lokasyon             → istanbul/antalya/ege/ankara    L2-G5 agency/insurance → dental-tourism-agency / teeth-done
  G6 + G8 güven/yorumlar  → best-dental-clinic-turkey      L2-G6 izmir/kuşadası   → dental-clinic-aegean
  G7 bilgi                → teeth-done-in-turkey           L2-G7 areas to avoid   → istanbul-guide
  G10 garanti/aftercare   → dental-guarantee-aftercare
  G10 önce-sonra / renk   → smile-gallery
  HEDEFLENMEYEN: rakip markalar (G9, L2-G8), DCT marka sorguları, başka ülkelerin klinik aramaları, saç/estetik/hastane.
"""

TOPICS = {
    # ── L2-G1 pillar ──────────────────────────────────────────────────────
    "dental-tourism": {
        "group": "L2-G1", "kind": "pillar", "order": 1,
        "slugs": {"en": "dental-tourism", "de": "zahntourismus", "nl": "tandheelkundig-toerisme",
                  "fr": "tourisme-dentaire", "it": "turismo-dentale", "es": "turismo-dental",
                  "pl": "turystyka-dentystyczna", "ru": "stomatologicheskiy-turizm", "uk": "stomatologichnyy-turyzm",
                  "ar": "al-siyaha-al-ilajiya-lil-asnan", "sv": "tandturism", "da": "tandturisme", "no": "tannturisme",
                  "ro": "turism-dentar", "az": "dis-turizmi", "tr": "dis-turizmi-rehberi"},
        "en": {
            "h1": "Dental tourism: the honest guide for 2026",
            "lead": "Dental tourism means travelling abroad for dental treatment. Done well, it gives you an experienced "
                    "dentist, modern care and very affordable treatment. Done badly, it costs you healthy teeth. Here is "
                    "how to get it right.",
            "meta_title": "Dental Tourism 2026: Honest Guide from a Dentist in Istanbul",
            "meta_description": "What is dental tourism, where is the best place for it and how to choose a dentist abroad. "
                                "An honest guide from a dental clinic in Istanbul, Turkey.",
            "body": """## What is dental tourism?

Dental tourism (also called dental medical tourism or dental health tourism) means combining a trip abroad with dental treatment. Patients travel because treatment at home is expensive, waiting lists are long, or they want a dentist with more time for them.

## Dental work is more than a Hollywood smile

Many "dental holidays" sell the same set of veneers or crowns to everyone. A real treatment starts with an examination, X-rays and an honest conversation. Sometimes the best treatment is a filling, a root canal or professional whitening — not twenty crowns.

## Best place for dental tourism

The best place for dental medical tourism is where three things come together:

- **An experienced dentist** who examines you personally and is responsible for the whole plan
- **Transparency**: a written plan, named materials and a fixed quote before you travel
- **Easy travel and aftercare**: short flights and a dentist you can reach on WhatsApp after you go home

Turkey — and Istanbul in particular — offers all three, which is why it is one of the most popular destinations for dental tourism in Europe.

## How dental tourism with us works

1. Send photos or an X-ray on WhatsApp
2. Receive a personal plan and a fixed written quote — prices are very affordable, and we tell you openly what is and isn't included
3. Book your flights; we plan the appointments around them
4. Treatment in our clinic in Şişli, Istanbul — open 7 days a week
5. Aftercare on WhatsApp when you are back home""",
            "faq": [
                ["Is dental tourism safe?", "Yes, if you choose a licensed clinic and a qualified dentist, check real "
                 "reviews and get a written treatment plan before you travel."],
                ["What is the best medical tourism destination for dental work?", "Turkey, Hungary, Mexico and Thailand are "
                 "the best known. For patients from Europe, the UK and the Middle East, Istanbul combines short flights, "
                 "experienced dentists and very affordable treatment."],
                ["How much does dental tourism cost?", "It depends entirely on your teeth. Call us or send photos on "
                 "WhatsApp and you will receive a personal, fixed quote — no surprises later."],
            ],
        },
        "keywords": {
            "en": ["dental tourism", "dental tourism turkey", "dental health tourism", "best dental tourism",
                   "best medical tourism for dental", "best medical tourism for dental work",
                   "best place for dental medical tourism", "what is dental tourism", "dental tourism websites"],
            "de": ["zahntourismus", "zahntourismus türkei", "was ist zahntourismus", "zahnbehandlung im ausland"],
            "nl": ["tandheelkundig toerisme", "tandarts buitenland", "tandartstoerisme turkije"],
            "fr": ["tourisme dentaire", "tourisme dentaire turquie", "soins dentaires à l'étranger"],
            "it": ["turismo dentale", "turismo dentale turchia", "dentista all'estero"],
            "es": ["turismo dental", "turismo dental turquía", "dentista en el extranjero"],
            "pl": ["turystyka dentystyczna", "leczenie zębów za granicą"],
            "ru": ["стоматологический туризм", "лечение зубов за границей"],
            "uk": ["стоматологічний туризм", "лікування зубів за кордоном"],
            "ar": ["السياحة العلاجية للأسنان", "علاج الأسنان في الخارج"],
            "sv": ["tandturism", "tandvård utomlands"], "da": ["tandturisme", "tandlæge i udlandet"],
            "no": ["tannturisme", "tannlege i utlandet"], "ro": ["turism dentar", "dentist in strainatate"],
            "az": ["diş turizmi", "xaricdə diş müalicəsi"], "tr": ["diş turizmi", "sağlık turizmi diş"],
        },
    },
    # ── G1 ────────────────────────────────────────────────────────────────
    "dental-care-turkey": {
        "group": "G1", "kind": "general", "order": 2,
        "slugs": {"en": "dental-care-turkey", "de": "zahnbehandlung-tuerkei", "nl": "tandarts-turkije",
                  "fr": "soins-dentaires-turquie", "it": "cure-dentali-turchia", "es": "tratamiento-dental-turquia",
                  "pl": "leczenie-zebow-turcja", "ru": "lechenie-zubov-v-turcii", "uk": "likuvannya-zubiv-turechchyna",
                  "ar": "ilaj-al-asnan-fi-turkiya", "sv": "tandvard-turkiet", "da": "tandbehandling-tyrkiet",
                  "no": "tannbehandling-tyrkia", "ro": "tratament-dentar-turcia", "az": "turkiyede-dis-mualicesi",
                  "tr": "turkiye-dis-klinigi"},
        "en": {
            "h1": "Dental care in Turkey — a dental clinic chosen for quality",
            "lead": "Dental tourism in Turkey is more than a cheap smile. At our dental clinic in Istanbul you get an "
                    "experienced dentist, a real diagnosis and a treatment plan made only for you.",
            "meta_title": "Dental Care in Turkey — Dental Clinic in Istanbul",
            "meta_description": "Dental care in Turkey with an experienced dentist in Istanbul: real diagnosis, written "
                                "plan, very affordable treatment. Call or WhatsApp for your personal quote.",
            "body": """## Why patients choose a dental clinic in Turkey

Turkey combines experienced dentists, modern clinics and very affordable treatment. Many of our patients come from the UK, Germany and the Netherlands and fly home after about a week.

- Experienced dentists and modern 3D diagnostics
- Very affordable compared with Western Europe — without cutting corners on materials
- Short flights and easy travel to Istanbul
- Direct WhatsApp contact with your dentist

## Dental clinic, dental office or dental hospital?

In Turkey you will find small dental offices, private dental practices, large dental care centres and dental departments of hospitals. What matters is not the size of the building but who treats you: one experienced dentist who is responsible for your whole plan.

## What makes our dental care different

We save natural teeth first, explain every option openly and give you a fixed written quote before treatment. Implants, veneers and crowns are recommended only when you truly need them — dental work is more than a Hollywood smile.""",
            "faq": [
                ["Is dental care in Turkey safe?", "Yes, in licensed clinics inspected by the Ministry of Health. Ask for "
                 "the dentist's qualifications, the brands of materials and a written treatment plan before you travel."],
                ["Why is dental care in Turkey so affordable?", "Lower operating costs and the exchange rate make "
                 "treatment much more affordable — the materials and techniques are the same as in Western Europe."],
                ["Do you treat patients from the UK?", "Yes. Many of our patients travel from the UK and Ireland; we "
                 "communicate in English and plan your appointments around your flights."],
            ],
        },
        "keywords": {
            "en": ["dental care in turkey", "dental clinic turkey", "dentist clinic turkey", "dental tourism turkey",
                   "dental tourism in turkey", "dental tourism to turkey", "best dental tourism turkey",
                   "dental travel to turkey", "dental medical tourism turkey", "teeth clinic in turkey",
                   "dental care center turkey", "dental office in turkey", "dental practice in turkey",
                   "dental hospital in turkey", "dental clinic turkish hospital", "dental clinics turkey facebook",
                   "turkey dental clinic uk", "dental care turkey"],
            "de": ["zahnbehandlung türkei", "zahnklinik türkei", "zahnarzt türkei", "zahnarztpraxis türkei"],
            "nl": ["tandarts turkije", "tandartskliniek turkije", "tandheelkundige zorg turkije"],
            "fr": ["soins dentaires turquie", "clinique dentaire turquie", "dentiste turquie"],
            "it": ["cure dentali turchia", "clinica dentale turchia", "dentista turchia"],
            "es": ["tratamiento dental turquía", "clínica dental turquía", "dentista turquía"],
            "pl": ["leczenie zębów turcja", "klinika stomatologiczna turcja", "dentysta turcja"],
            "ru": ["лечение зубов в турции", "стоматология в турции", "стоматологическая клиника турция"],
            "uk": ["лікування зубів у туреччині", "стоматологія туреччина"],
            "ar": ["علاج الأسنان في تركيا", "عيادة أسنان في تركيا", "طبيب أسنان في تركيا"],
            "sv": ["tandvård turkiet", "tandklinik turkiet"], "da": ["tandbehandling tyrkiet", "tandklinik tyrkiet"],
            "no": ["tannbehandling tyrkia", "tannklinikk tyrkia"], "ro": ["tratament dentar turcia", "clinica dentara turcia"],
            "az": ["türkiyədə diş müalicəsi", "türkiyədə diş klinikası"],
            "tr": ["türkiye diş kliniği", "yabancı hastalar için diş kliniği", "diş turizmi türkiye"],
        },
    },
    # ── L2-G2 ─────────────────────────────────────────────────────────────
    "best-dental-clinic-istanbul": {
        "group": "L2-G2", "kind": "trust", "order": 3, "show_cases": True,
        "slugs": {"en": "best-dental-clinic-in-istanbul", "de": "beste-zahnklinik-istanbul",
                  "nl": "beste-tandarts-istanbul", "fr": "meilleure-clinique-dentaire-istanbul",
                  "it": "migliore-clinica-dentale-istanbul", "es": "mejor-clinica-dental-estambul",
                  "pl": "najlepsza-klinika-stomatologiczna-stambul", "ru": "luchshaya-stomatologiya-stambula",
                  "uk": "krashcha-stomatologiya-stambula", "ar": "afdal-iyadat-asnan-fi-istanbul",
                  "sv": "basta-tandklinik-istanbul", "da": "bedste-tandklinik-istanbul", "no": "beste-tannklinikk-istanbul",
                  "ro": "cea-mai-buna-clinica-dentara-istanbul", "az": "istanbulda-en-yaxsi-dis-klinikasi",
                  "tr": "istanbul-en-iyi-dis-klinigi"},
        "en": {
            "h1": "Best dental clinic in Istanbul? Reviews, questions to ask and our approach",
            "lead": "Searching for the best dental clinic in Istanbul, Turkey? Read the reviews — and ask the questions "
                    "that separate a good dentist from a sales team.",
            "meta_title": "Best Dental Clinic in Istanbul 2026 — Reviews & How to Choose",
            "meta_description": "How to find the best dental clinic in Istanbul: real reviews, questions to ask, red "
                                "flags. Dental clinic in Şişli with transparent plans and very affordable treatment.",
            "body": """## What "best" should mean

The best dentist clinic in Istanbul is not the one with the biggest advertising budget. It is the one where an experienced dentist examines you, explains your options and keeps healthy teeth healthy.

## Questions to ask any clinic in Istanbul

- Who will treat me — and can I see the dentist's qualifications?
- Can I get a written treatment plan with the brands of implants, crowns and veneers?
- Is the quote fixed? What exactly is included?
- How will aftercare work when I am back home?

## Reviews: Google, Trustpilot and Reddit

Read reviews on several platforms, including critical ones on Reddit. Look for detailed reviews written months after treatment, and look at how the clinic replies to criticism. Our reviews are collected on Google and on this site, and every review shows where it comes from.

## Why patients choose us

- Treatment by Dr. Dt. Devrim Biriken Sipahi personally — Ankara University Faculty of Dentistry, oral and maxillofacial radiology at Marmara University
- Natural teeth first: no unnecessary crowns or veneers
- Very affordable, with a fixed written quote — call or message us on WhatsApp
- Central Şişli, near Taksim, open 7 days a week""",
            "faq": [
                ["Which is the best clinic in Istanbul for teeth?", "The best clinic is the one that fits your case: "
                 "an experienced dentist, a written plan and honest reviews. Compare several and ask the questions above."],
                ["Do you have reviews on Google?", "Yes — you can read them on our Google Business Profile and on this "
                 "page. Every review is linked to its source."],
            ],
        },
        "keywords": {
            "en": ["best dental clinic in istanbul turkey reviews", "best dental clinic in istanbul",
                   "best dental clinic istanbul turkey", "best dental clinic istanbul reviews",
                   "best dental clinic istanbul reddit", "best dental clinic in istanbul 2026",
                   "best dentist clinic in istanbul", "best clinic in istanbul for teeth"],
            "de": ["beste zahnklinik istanbul", "bester zahnarzt istanbul", "zahnklinik istanbul erfahrungen"],
            "nl": ["beste tandarts istanbul", "tandarts istanbul ervaringen"],
            "fr": ["meilleure clinique dentaire istanbul", "meilleur dentiste istanbul avis"],
            "it": ["migliore clinica dentale istanbul", "miglior dentista istanbul recensioni"],
            "es": ["mejor clínica dental estambul", "mejor dentista estambul opiniones"],
            "pl": ["najlepsza klinika stomatologiczna stambuł", "dentysta stambuł opinie"],
            "ru": ["лучшая стоматология стамбула", "лучший стоматолог стамбул отзывы"],
            "uk": ["краща стоматологія стамбула"], "ar": ["أفضل عيادة أسنان في إسطنبول", "أفضل طبيب أسنان في إسطنبول"],
            "sv": ["bästa tandklinik istanbul"], "da": ["bedste tandklinik istanbul"], "no": ["beste tannklinikk istanbul"],
            "ro": ["cea mai buna clinica dentara istanbul"], "az": ["istanbulda ən yaxşı diş klinikası"],
            "tr": ["istanbul en iyi diş kliniği", "şişli en iyi diş hekimi", "istanbul diş kliniği yorumlar"],
        },
    },
    # ── G6 + G8 ───────────────────────────────────────────────────────────
    "best-dental-clinic-turkey": {
        "group": "G6+G8", "kind": "trust", "order": 4, "show_cases": True,
        "slugs": {"en": "best-dental-clinic-turkey-reviews", "de": "beste-zahnklinik-tuerkei-erfahrungen",
                  "nl": "beste-tandarts-turkije-ervaringen", "fr": "meilleure-clinique-dentaire-turquie-avis",
                  "it": "migliore-clinica-dentale-turchia-recensioni", "es": "mejor-clinica-dental-turquia-opiniones",
                  "pl": "najlepsza-klinika-stomatologiczna-turcja-opinie", "ru": "luchshaya-stomatologiya-turcii-otzyvy",
                  "uk": "krashcha-stomatologiya-turechchyny-vidguky", "ar": "afdal-iyadat-asnan-turkiya-taqyimat",
                  "sv": "basta-tandklinik-turkiet-omdomen", "da": "bedste-tandklinik-tyrkiet-anmeldelser",
                  "no": "beste-tannklinikk-tyrkia-omtaler", "ro": "cea-mai-buna-clinica-dentara-turcia-pareri",
                  "az": "turkiyede-en-yaxsi-dis-klinikasi-reyler", "tr": "turkiye-en-iyi-dis-klinigi-yorumlar"},
        "en": {
            "h1": "Best dental clinic in Turkey 2026? How to choose — and real patient reviews",
            "lead": "Top, luxury, VIP — every clinic says it is the best. Here is how to judge a dental clinic in Turkey "
                    "yourself, the red flags of the worst ones, and what our patients really say.",
            "meta_title": "Best Dental Clinic in Turkey 2026 — Reviews & Red Flags",
            "meta_description": "Top, luxury or VIP dental clinic in Turkey? How to judge quality, red flags of the worst "
                                "clinics, and real reviews from Google and Trustpilot.",
            "body": """## How to recognise a good dental clinic in Turkey

- A named dentist who examines you and is responsible for the whole plan
- A written treatment plan before you travel — with the material brands
- Real reviews on Google and Trustpilot, not only on the clinic's own website
- Aftercare when you are back home

## Red flags of the worst dental clinics

- A fixed number of veneers or crowns sold before anyone has seen your teeth
- Healthy teeth ground down for a "Hollywood smile"
- No dentist's name — only a sales coordinator
- Pressure to decide immediately

## Luxury and VIP dental clinics

A luxury waiting room does not make a better dentist. What you should expect from a premium clinic is time: a careful diagnosis, a dentist who explains, and results that last. Quality does not have to be expensive — our treatment is very affordable, and you receive a fixed quote by phone or WhatsApp.""",
            "faq": [
                ["Where can I read reviews of dental clinics in Turkey?", "Google Maps, Trustpilot and Reddit are good "
                 "places — look for detailed reviews with photos and for how the clinic replies to criticism."],
                ["Are your reviews real?", "Our reviews come from Google and from patients treated here; every review "
                 "on our site is checked and shows its source."],
            ],
        },
        "keywords": {
            "en": ["best dental clinic turkey trustpilot", "best dental clinic in turkey 2026", "top dental clinic turkey",
                   "good dental clinic turkey", "luxury dental clinic turkey", "luxury dental clinic turkey reviews",
                   "vip dental clinic turkey", "worst dental clinic turkey", "dental care turkey reviews",
                   "dental care turkey trustpilot", "dental care turkey reddit", "dental surgery turkey reviews"],
            "de": ["beste zahnklinik türkei", "zahnklinik türkei erfahrungen", "zahnarzt türkei bewertungen"],
            "nl": ["beste tandarts turkije", "tandarts turkije ervaringen", "tandarts turkije reviews"],
            "fr": ["meilleure clinique dentaire turquie", "clinique dentaire turquie avis"],
            "it": ["migliore clinica dentale turchia", "clinica dentale turchia recensioni"],
            "es": ["mejor clínica dental turquía", "clínica dental turquía opiniones"],
            "pl": ["najlepsza klinika stomatologiczna turcja", "dentysta turcja opinie"],
            "ru": ["лучшая стоматология в турции", "стоматология турция отзывы"],
            "uk": ["краща стоматологія туреччини", "стоматологія туреччина відгуки"],
            "ar": ["أفضل عيادة أسنان في تركيا", "تقييمات عيادات الأسنان في تركيا"],
            "sv": ["bästa tandklinik turkiet", "tandläkare turkiet omdömen"],
            "da": ["bedste tandklinik tyrkiet", "tandlæge tyrkiet anmeldelser"],
            "no": ["beste tannklinikk tyrkia", "tannlege tyrkia omtaler"],
            "ro": ["cea mai buna clinica dentara turcia", "dentist turcia pareri"],
            "az": ["türkiyədə ən yaxşı diş klinikası", "diş klinikası rəylər"],
            "tr": ["dental clinic turkey yorumlar", "aesthetic dental turkey clinic yorumlar",
                   "en iyi diş kliniği yorumlar", "şişli diş hekimi yorumlar"],
        },
    },
    # ── G5 ────────────────────────────────────────────────────────────────
    "dental-clinic-istanbul": {
        "group": "G5", "kind": "location", "order": 5,
        "slugs": {"en": "dental-clinic-istanbul", "de": "zahnklinik-istanbul", "nl": "tandartskliniek-istanbul",
                  "fr": "clinique-dentaire-istanbul", "it": "clinica-dentale-istanbul", "es": "clinica-dental-estambul",
                  "pl": "klinika-stomatologiczna-stambul", "ru": "stomatologiya-stambul", "uk": "stomatologiya-v-stambuli",
                  "ar": "iyadat-asnan-istanbul", "sv": "tandklinik-istanbul", "da": "tandklinik-istanbul",
                  "no": "tannklinikk-istanbul", "ro": "clinica-dentara-istanbul", "az": "istanbul-dis-klinikasi",
                  "tr": "istanbul-dis-klinigi-sisli"},
        "en": {
            "h1": "Dental clinic in Istanbul, Turkey — Şişli, near Taksim",
            "lead": "Our dental clinic is in central Şişli (Osmanbey), one metro stop from Taksim. Easy to reach from "
                    "every district of Istanbul — and open 7 days a week.",
            "meta_title": "Dental Clinic in Istanbul — Şişli, near Taksim, Open 7 Days",
            "meta_description": "Dental clinic in Istanbul, Turkey: Şişli/Osmanbey, one metro stop from Taksim, open 7 days "
                                "a week. Experienced dentist, very affordable treatment, WhatsApp consultation.",
            "body": """## How to reach us in Istanbul

Osmanbey metro station (M2) is a few minutes' walk away. From Taksim it is one stop; from Zeytinburnu, Beşiktaş or Kadıköy you can reach us by metro, tram or ferry.

- Taksim → Osmanbey: one metro stop
- Nişantaşı and Mecidiyeköy: walking distance
- Istanbul Airport: about 45–60 minutes by car or metro

## Dental tourism in Istanbul

Istanbul has direct flights to more destinations than almost any other city. Patients combine treatment with a few days in the city — appointments are planned around your flights.

## A dentist, not a factory

We are a dentist-led clinic: Dr. Dt. Devrim Biriken Sipahi examines and treats you personally. Prices are very affordable and always fixed in writing before treatment — ask by phone or on WhatsApp.""",
            "faq": [
                ["Where is the clinic in Istanbul?", "Abide-i Hürriyet Caddesi No:148, Floor 4, Flat 11, Şişli — near "
                 "Osmanbey metro."],
                ["Are you open at weekends?", "Yes, we are open 7 days a week, including Saturday and Sunday."],
                ["Is the clinic near Taksim?", "Yes — Osmanbey is one metro stop from Taksim."],
            ],
        },
        "keywords": {
            "en": ["dental clinic in turkey istanbul", "dental tourism istanbul turkey", "dental clinic taksim",
                   "turkey dental clinic zeytinburnu", "istanbul dental clinic turkey trustpilot", "dentist istanbul"],
            "de": ["zahnklinik istanbul", "zahnarzt istanbul", "zahnarzt istanbul taksim"],
            "nl": ["tandarts istanbul", "tandartskliniek istanbul"], "fr": ["clinique dentaire istanbul", "dentiste istanbul"],
            "it": ["clinica dentale istanbul", "dentista istanbul"], "es": ["clínica dental estambul", "dentista estambul"],
            "pl": ["klinika stomatologiczna stambuł", "dentysta stambuł"], "ru": ["стоматология стамбул", "стоматолог стамбул"],
            "uk": ["стоматологія стамбул"], "ar": ["عيادة أسنان في إسطنبول", "عيادة أسنان تقسيم"],
            "sv": ["tandklinik istanbul"], "da": ["tandklinik istanbul"], "no": ["tannklinikk istanbul"],
            "ro": ["clinica dentara istanbul"], "az": ["istanbul diş klinikası"],
            "tr": ["şişli diş kliniği", "taksim diş kliniği", "osmanbey diş hekimi", "zeytinburnu diş kliniği",
                   "hafta sonu açık diş hekimi şişli"],
        },
    },
    "dental-care-antalya": {
        "group": "G5", "kind": "location", "order": 6,
        "slugs": {"en": "dental-care-antalya-side-alanya", "de": "zahnarzt-antalya-side-alanya",
                  "nl": "tandarts-antalya-side-alanya", "fr": "dentiste-antalya-side-alanya",
                  "it": "dentista-antalya-side-alanya", "es": "dentista-antalya-side-alanya",
                  "pl": "dentysta-antalya-side-alanya", "ru": "stomatologiya-antalya-sajd-alanya",
                  "uk": "stomatologiya-antaliya-alaniya", "ar": "tabib-asnan-antalya",
                  "sv": "tandlakare-antalya-side-alanya", "da": "tandlaege-antalya-side-alanya",
                  "no": "tannlege-antalya-side-alanya", "ro": "dentist-antalya-side-alanya",
                  "az": "antalya-dis-mualicesi", "tr": "antalya-tatilinde-dis-tedavisi"},
        "en": {
            "h1": "Dental care in Antalya, Side, Belek or Alanya? A short flight to Istanbul",
            "lead": "Holidaying on the Turkish Riviera? Our clinic is in Istanbul — about 1 hour 15 minutes by plane from "
                    "Antalya. Many patients combine a beach holiday with a few days of treatment in Istanbul.",
            "meta_title": "Dental Care Antalya, Side, Alanya — or Istanbul?",
            "meta_description": "Dental clinic in Antalya, Side, Belek or Alanya? Combine your holiday with treatment by "
                                "an experienced dentist in Istanbul — 75 minutes by plane.",
            "body": """## Honest note: our clinic is in Istanbul

We do not have a branch in Antalya, Side, Belek or Alanya. If you prefer to be treated where you stay, choose a licensed clinic and check the dentist's qualifications. If you want an experienced dentist with a transparent plan, a domestic flight to Istanbul is quick and inexpensive.

## How to combine your holiday with treatment

- Send photos or an X-ray on WhatsApp before your holiday
- We plan the appointments for the start or the end of your trip
- Flights between Antalya and Istanbul run many times a day

## Implants and dental surgery

Dental implants and other surgery need a careful 3D plan and a follow-up check. We plan every step so that it fits around your stay in Turkey — and the price is very affordable and fixed in writing.""",
            "faq": [
                ["How far is Istanbul from Antalya?", "About 1 hour 15 minutes by plane, with many daily flights."],
                ["Can I start treatment during my holiday?", "Yes — examination and planning can be done in one visit, "
                 "and treatment scheduled around your stay."],
            ],
        },
        "keywords": {
            "en": ["dental care turkey antalya", "dental clinic in turkey antalya", "dental tourism antalya turkey",
                   "dental surgery turkey antalya", "dental clinic side turkey", "dental care side turkey",
                   "dental clinic belek turkey", "dental clinic alanya turkey", "dental implants turkey antalya price",
                   "full mouth dental implants turkey antalya"],
            "de": ["zahnarzt antalya", "zahnarzt side türkei", "zahnarzt alanya", "zahnklinik belek"],
            "nl": ["tandarts antalya", "tandarts side turkije", "tandarts alanya"],
            "fr": ["dentiste antalya", "dentiste side turquie", "dentiste alanya"],
            "it": ["dentista antalya", "dentista alanya"], "es": ["dentista antalya", "dentista alanya"],
            "pl": ["dentysta antalya", "dentysta alanya"], "ru": ["стоматология анталия", "стоматолог алания", "стоматология сиде"],
            "uk": ["стоматологія анталія"], "ar": ["طبيب أسنان في أنطاليا"], "sv": ["tandläkare antalya"],
            "da": ["tandlæge antalya"], "no": ["tannlege antalya"], "ro": ["dentist antalya"], "az": ["antalya diş klinikası"],
            "tr": ["antalya diş kliniği", "alanya diş hekimi", "side diş kliniği"],
        },
    },
    "dental-clinic-aegean": {
        "group": "G5+L2-G6", "kind": "location", "order": 7,
        "slugs": {"en": "dental-clinic-bodrum-marmaris-izmir-kusadasi", "de": "zahnarzt-bodrum-marmaris-izmir",
                  "nl": "tandarts-bodrum-marmaris-izmir", "fr": "dentiste-bodrum-marmaris-izmir",
                  "it": "dentista-bodrum-marmaris-izmir", "es": "dentista-bodrum-marmaris-esmirna",
                  "pl": "dentysta-bodrum-marmaris-izmir", "ru": "stomatologiya-bodrum-marmaris-izmir",
                  "uk": "stomatologiya-bodrum-marmarys-izmir", "ar": "tabib-asnan-bodrum-marmaris-izmir",
                  "sv": "tandlakare-bodrum-marmaris-izmir", "da": "tandlaege-bodrum-marmaris-izmir",
                  "no": "tannlege-bodrum-marmaris-izmir", "ro": "dentist-bodrum-marmaris-izmir",
                  "az": "bodrum-marmaris-izmir-dis-mualicesi", "tr": "bodrum-marmaris-izmir-kusadasi-dis-tedavisi"},
        "en": {
            "h1": "Dental clinic in Bodrum, Marmaris, Izmir or Kuşadası? Combine your holiday with Istanbul",
            "lead": "Bodrum, Dalaman and Izmir airports have frequent flights to Istanbul — about 1 hour 10 minutes. Plan "
                    "your treatment with an experienced Istanbul dentist before or after your Aegean holiday.",
            "meta_title": "Dental Clinic Bodrum, Marmaris, Izmir, Kuşadası — or Istanbul?",
            "meta_description": "Looking for the best dental clinic in Izmir, Kuşadası, Bodrum or Marmaris? Combine your "
                                "Aegean holiday with treatment in Istanbul — about 70 minutes by plane.",
            "body": """## Honest note: our clinic is in Istanbul

We do not have a branch in Bodrum, Marmaris, Izmir or Kuşadası. We help you plan treatment in Istanbul so that it fits around your holiday, with aftercare on WhatsApp when you are back home.

## How it works

- Fly from Bodrum (BJV), Dalaman (DLM) or Izmir (ADB) to Istanbul in about 70 minutes
- Examination and 3D scan on day one, treatment over the following days
- A fixed written quote before treatment — very affordable, no surprises

## Choosing a dentist on the Aegean coast

If you decide to be treated locally, use the same checklist: a named dentist, a written plan, material brands and real reviews.""",
            "faq": [
                ["How do I get from Bodrum or Marmaris to Istanbul?", "Fly from Bodrum (BJV) or Dalaman (DLM) to "
                 "Istanbul — about 1 hour 10 minutes."],
                ["And from Izmir or Kuşadası?", "Fly from Izmir Adnan Menderes (ADB); Kuşadası is about an hour's drive "
                 "from the airport."],
            ],
        },
        "keywords": {
            "en": ["dental clinic marmaris turkey", "dental clinic bodrum turkey", "best dental clinics in izmir",
                   "best dental clinic in kusadasi"],
            "de": ["zahnarzt marmaris", "zahnarzt bodrum", "zahnarzt izmir", "zahnarzt kusadasi"],
            "nl": ["tandarts marmaris", "tandarts bodrum", "tandarts kusadasi"], "fr": ["dentiste marmaris", "dentiste bodrum"],
            "it": ["dentista bodrum"], "es": ["dentista bodrum"], "pl": ["dentysta marmaris", "dentysta bodrum"],
            "ru": ["стоматология мармарис", "стоматология бодрум", "стоматология измир"], "uk": ["стоматологія мармарис"],
            "ar": ["طبيب أسنان بودروم", "طبيب أسنان إزمير"], "sv": ["tandläkare marmaris"], "da": ["tandlæge marmaris"],
            "no": ["tannlege marmaris"], "ro": ["dentist bodrum"], "az": ["izmir diş klinikası"],
            "tr": ["marmaris diş kliniği", "bodrum diş kliniği", "izmir en iyi diş kliniği", "kuşadası diş kliniği"],
        },
    },
    "dental-clinic-ankara": {
        "group": "G5", "kind": "location", "order": 8,
        "slugs": {"en": "dental-clinic-ankara-or-istanbul", "de": "zahnarzt-ankara-oder-istanbul",
                  "nl": "tandarts-ankara-of-istanbul", "fr": "dentiste-ankara-ou-istanbul", "it": "dentista-ankara-o-istanbul",
                  "es": "dentista-ankara-o-estambul", "pl": "dentysta-ankara-czy-stambul", "ru": "stomatologiya-ankara-ili-stambul",
                  "uk": "stomatologiya-ankara-chy-stambul", "ar": "tabib-asnan-ankara", "sv": "tandlakare-ankara-eller-istanbul",
                  "da": "tandlaege-ankara-eller-istanbul", "no": "tannlege-ankara-eller-istanbul",
                  "ro": "dentist-ankara-sau-istanbul", "az": "ankara-ve-istanbul-dis-mualicesi",
                  "tr": "ankaradan-istanbula-dis-tedavisi"},
        "en": {
            "h1": "Dental clinic in Ankara or Istanbul? What to consider",
            "lead": "From Ankara, Istanbul is about 1 hour by plane or 4–5 hours by high-speed train. Our dentist graduated "
                    "from Ankara University Faculty of Dentistry and practises in Istanbul.",
            "meta_title": "Dental Clinic in Ankara or Istanbul? What to Consider",
            "meta_description": "Choosing a dental clinic in Ankara or Istanbul: travel times, how to plan treatment and "
                                "why patients from Ankara choose our dentist in Şişli, Istanbul.",
            "body": """## Honest note: our clinic is in Istanbul

We do not have a clinic in Ankara. Patients from Ankara choose us for our ethical, tooth-saving approach and transparent planning.

## Planning treatment from Ankara

- Send photos or an X-ray on WhatsApp for a first assessment
- Combine treatment with a weekend — we are open 7 days a week
- Receive a fixed written quote; our prices are very affordable""",
            "faq": [
                ["How do I travel from Ankara to Istanbul?", "By plane (about 1 hour) or by high-speed train (about "
                 "4–5 hours)."],
            ],
        },
        "keywords": {
            "en": ["dental clinic in ankara"], "de": ["zahnarzt ankara"], "nl": ["tandarts ankara"], "fr": ["dentiste ankara"],
            "it": ["dentista ankara"], "es": ["dentista ankara"], "pl": ["dentysta ankara"], "ru": ["стоматология анкара"],
            "uk": ["стоматологія анкара"], "ar": ["طبيب أسنان أنقرة"], "sv": ["tandläkare ankara"], "da": ["tandlæge ankara"],
            "no": ["tannlege ankara"], "ro": ["dentist ankara"], "az": ["ankara diş klinikası"],
            "tr": ["ankara diş kliniği", "ankaradan istanbula diş tedavisi"],
        },
    },
    # ── L2-G4 + paket karşılaştırma ───────────────────────────────────────
    "best-country-dental-tourism": {
        "group": "L2-G4+PKG", "kind": "compare", "order": 9,
        "slugs": {"en": "best-country-for-dental-tourism", "de": "bestes-land-fuer-zahntourismus",
                  "nl": "beste-land-voor-tandheelkundig-toerisme", "fr": "meilleur-pays-tourisme-dentaire",
                  "it": "miglior-paese-turismo-dentale", "es": "mejor-pais-turismo-dental",
                  "pl": "najlepszy-kraj-turystyka-dentystyczna", "ru": "luchshaya-strana-dlya-lecheniya-zubov",
                  "uk": "krashcha-krayina-dlya-likuvannya-zubiv", "ar": "afdal-dawla-lil-siyaha-al-ilajiya-lil-asnan",
                  "sv": "basta-landet-for-tandturism", "da": "bedste-land-til-tandturisme", "no": "beste-land-for-tannturisme",
                  "ro": "cea-mai-buna-tara-turism-dentar", "az": "dis-turizmi-ucun-en-yaxsi-olke",
                  "tr": "dis-turizmi-icin-en-iyi-ulke"},
        "en": {
            "h1": "Best country for dental tourism in 2026: Turkey vs Mexico, Thailand, Hungary and more",
            "lead": "Mexico, Thailand, Vietnam, Bali, Hungary, Croatia, Albania, India, Costa Rica, the Philippines or "
                    "Turkey? An honest comparison of the top dental tourism destinations — and why the dentist matters more "
                    "than the country.",
            "meta_title": "Best Country for Dental Tourism 2026 — Top 10 Destinations",
            "meta_description": "Best country for dental tourism in Europe, from the US or Australia: Turkey, Hungary, "
                                "Mexico, Thailand, Vietnam, Bali and more compared honestly.",
            "body": """## Top 10 dental tourism destinations

- **Turkey (Istanbul, Antalya)** — short flights from Europe, the UK and the Middle East; experienced dentists; very affordable
- **Hungary and Croatia** — popular in Europe, but usually more expensive than Turkey
- **Albania** — growing, with fewer specialised clinics
- **Mexico (Cancún, Tijuana, Los Algodones)** — the classic choice from the US and Canada
- **Costa Rica** — popular with North Americans for longer stays
- **Thailand, Vietnam, Bali (Indonesia)** — popular "dental holiday packages" from Australia and New Zealand
- **India and the Philippines** — very low costs, long travel times from Europe

## Best country for dental tourism in Europe

For European patients, Turkey and Hungary are the main choices. Istanbul has more direct flights, open-all-week clinics and a wider choice of experienced dentists.

## From the US, Australia or New Zealand

Distance matters: implants usually need two visits. From the US, Mexico is closer; from Australia, Thailand, Vietnam and Bali are. Patients who choose Istanbul from far away plan treatment carefully so that the number of trips stays small.

## Best city for dental tourism

Within Turkey, Istanbul is the best city for most dental tourists: the most flights, the most choice of dentists and plenty to do between appointments.

## What Reddit gets right

Discussions about the best dental tourism countries on Reddit agree on one thing: the individual dentist matters more than the country. Choose transparency, real reviews and a written plan — wherever you go.""",
            "faq": [
                ["Which country is best for dental tourism?", "For patients from Europe, the UK and the Middle East, Turkey "
                 "offers the best combination of short flights, experienced dentists and very affordable treatment."],
                ["Are all-inclusive dental packages in Mexico or Thailand a good idea?", "Only if the plan is based on a "
                 "real examination. Fixed all-inclusive packages often include treatment you don't need."],
            ],
        },
        "keywords": {
            "en": ["best country for dental tourism", "dental tourism countries", "top 10 dental tourism destinations",
                   "best country for dental tourism in europe", "best country for dental tourism from us",
                   "best country for dental medical tourism", "best city for dental tourism",
                   "best country for dental tourism reddit", "best dental tourism countries reddit",
                   "best dental tourism reddit", "best place for dental tourism reddit",
                   "mexico dental tourism packages all inclusive", "dental vacation packages mexico",
                   "cancun dental vacation packages all inclusive", "thailand dental tourism packages all inclusive",
                   "thailand dental holiday packages from australia", "vietnam dental tourism packages",
                   "vietnam dental holiday packages from australia", "vietnam dental holiday packages from nz",
                   "bali dental holiday packages all inclusive", "bali dental holiday packages from nz",
                   "dental holiday packages hungary", "dental holiday packages croatia", "dental tourism albania packages",
                   "dental tourism packages in india", "dental tourism packages costa rica",
                   "dental holiday packages philippines"],
            "de": ["bestes land für zahnbehandlung", "zahnurlaub ungarn oder türkei", "zahnbehandlung kroatien oder türkei"],
            "nl": ["beste land voor tandarts", "tandarts hongarije of turkije"],
            "fr": ["meilleur pays tourisme dentaire", "soins dentaires hongrie ou turquie"],
            "it": ["miglior paese turismo dentale", "dentista ungheria o turchia"],
            "es": ["mejor país turismo dental", "turismo dental méxico o turquía"],
            "pl": ["najlepszy kraj turystyka dentystyczna", "leczenie zębów węgry czy turcja"],
            "ru": ["лучшая страна для лечения зубов", "лечение зубов в турции или венгрии"],
            "uk": ["краща країна для лікування зубів"], "ar": ["أفضل دولة للسياحة العلاجية للأسنان", "علاج الأسنان في تركيا أم المجر"],
            "sv": ["bästa landet för tandvård", "tandvård ungern eller turkiet"],
            "da": ["bedste land til tandbehandling", "tandlæge ungarn eller tyrkiet"],
            "no": ["beste land for tannbehandling", "tannlege ungarn eller tyrkia"],
            "ro": ["cea mai bună țară pentru turism dentar", "dentist ungaria sau turcia"],
            "az": ["diş turizmi üçün ən yaxşı ölkə"], "tr": ["diş turizmi için en iyi ülke", "türkiye macaristan diş karşılaştırma"],
        },
    },
    # ── G7 + L2-G5 sigorta ────────────────────────────────────────────────
    "teeth-done-in-turkey": {
        "group": "G7+L2-G5", "kind": "guide", "order": 10,
        "slugs": {"en": "getting-teeth-done-in-turkey", "de": "zaehne-machen-lassen-tuerkei",
                  "nl": "tanden-laten-doen-in-turkije", "fr": "se-faire-soigner-les-dents-en-turquie",
                  "it": "rifarsi-i-denti-in-turchia", "es": "arreglarse-los-dientes-en-turquia",
                  "pl": "leczenie-zebow-w-turcji-poradnik", "ru": "sdelat-zuby-v-turcii", "uk": "zrobyty-zuby-v-turechchyni",
                  "ar": "tarkib-al-asnan-fi-turkiya", "sv": "fixa-tanderna-i-turkiet", "da": "faa-lavet-taender-i-tyrkiet",
                  "no": "fikse-tennene-i-tyrkia", "ro": "sa-iti-faci-dintii-in-turcia", "az": "turkiyede-dis-etdirmek",
                  "tr": "turkiyede-dis-yaptirmak-rehber"},
        "en": {
            "h1": "Getting your teeth done in Turkey — an honest guide",
            "lead": "Should you get your teeth done in Turkey, and where? The questions to ask, how the process works, "
                    "insurance and payment — explained by a dentist.",
            "meta_title": "Getting Teeth Done in Turkey: Where, How & Should You?",
            "meta_description": "Where to get teeth done in Turkey, how the process works, dental travel insurance and "
                                "payment options — an honest guide from a dentist in Istanbul.",
            "body": """## Should I get my teeth done in Turkey?

It is a good choice if you pick an experienced dentist, accept a treatment plan based on a real diagnosis and allow enough time. It is a bad choice if you buy a fixed "teeth package" before anyone has seen your teeth. Dental work is more than a Hollywood smile.

## Where to get teeth done in Turkey

Istanbul and Antalya are the main centres. More important than the city is the dentist: experience, transparency and real reviews.

## How do I get my teeth done in Turkey? Step by step

1. Send photos or an X-ray on WhatsApp
2. Receive a personal plan and a fixed written quote
3. Book flights — we plan appointments around them
4. Examination and 3D scan on day one, then treatment
5. Aftercare on WhatsApp when you are home

## Dental travel insurance and finance

Standard travel insurance usually does not cover planned dental treatment; ask your insurer about optional complication cover — this is what "dental tourism insurance" policies offer. We accept cash and credit card; ask us about paying in instalments for larger treatment plans. Our prices are very affordable — call us for your personal quote.""",
            "faq": [
                ["Where is the best place to get teeth done in Turkey?", "Istanbul and Antalya are the main centres. "
                 "Choose the dentist first: experience, transparency and real reviews."],
                ["Do I need travel insurance for dental treatment in Turkey?", "Travel insurance is recommended for the "
                 "trip itself; planned dental work is usually excluded, so ask about cover for complications."],
            ],
        },
        "keywords": {
            "en": ["where to get teeth done in turkey", "how do i get my teeth done in turkey",
                   "should i get my teeth done in turkey", "dental travel insurance turkey", "dental care turkey finance",
                   "best dental tourism insurance"],
            "de": ["zähne machen lassen türkei", "zahnbehandlung türkei versicherung", "zahnbehandlung türkei ablauf"],
            "nl": ["tanden laten doen turkije", "tandarts turkije verzekering"],
            "fr": ["se faire refaire les dents en turquie", "soins dentaires turquie assurance"],
            "it": ["rifarsi i denti in turchia"], "es": ["hacerse los dientes en turquía", "seguro dental turquía"],
            "pl": ["zrobić zęby w turcji"], "ru": ["сделать зубы в турции", "лечение зубов в турции страховка"],
            "uk": ["зробити зуби в туреччині"], "ar": ["تركيب الأسنان في تركيا", "أين أعمل أسناني في تركيا"],
            "sv": ["fixa tänderna i turkiet"], "da": ["få lavet tænder i tyrkiet"], "no": ["fikse tennene i tyrkia"],
            "ro": ["sa-ti faci dintii in turcia"], "az": ["türkiyədə diş etdirmək"],
            "tr": ["türkiyede diş yaptırmak", "yurt dışından türkiyeye diş tedavisi"],
        },
    },
    # ── G3/G4 cerrahi ─────────────────────────────────────────────────────
    "dental-surgery-turkey": {
        "group": "G3+G4", "kind": "service", "order": 11,
        "slugs": {"en": "dental-surgery-turkey", "de": "zahnchirurgie-tuerkei", "nl": "kaakchirurgie-turkije",
                  "fr": "chirurgie-dentaire-turquie", "it": "chirurgia-dentale-turchia", "es": "cirugia-dental-turquia",
                  "pl": "chirurgia-stomatologiczna-turcja", "ru": "hirurgicheskaya-stomatologiya-turciya",
                  "uk": "khirurgichna-stomatologiya-turechchyna", "ar": "jirahat-al-asnan-fi-turkiya",
                  "sv": "tandkirurgi-turkiet", "da": "tandkirurgi-tyrkiet", "no": "tannkirurgi-tyrkia",
                  "ro": "chirurgie-dentara-turcia", "az": "turkiyede-dis-cerrahiyyesi", "tr": "agiz-dis-cerrahisi-istanbul"},
        "en": {
            "h1": "Dental surgery in Turkey — implants, extractions and wisdom teeth",
            "lead": "Implant placement, extractions and wisdom tooth removal are minor surgical procedures done under local "
                    "anaesthesia. We plan every operation with 3D imaging (CBCT) — and an implant is always the last resort.",
            "meta_title": "Dental Surgery in Turkey — Implants & Extractions, Istanbul",
            "meta_description": "Dental surgery in Turkey: implant placement, extractions and wisdom teeth with 3D "
                                "planning in Istanbul. Very affordable — call or WhatsApp for your quote.",
            "body": """## Which dental surgery do we perform?

- Dental implant placement with 3D planning
- Tooth and wisdom tooth extraction
- Implant placement right after extraction, when suitable

## 3D planning comes first

Our dentist trained in oral and maxillofacial radiology. Every surgical step is planned on a 3D scan, which makes the procedure shorter, more precise and more comfortable.

## Dental surgery in Turkey: cost

Dental surgery in Turkey is very affordable compared with Western Europe. The cost depends on the procedure, the implant brand and whether bone grafting is needed — call us or message us on WhatsApp for your personal, fixed quote.""",
            "faq": [
                ["Is dental surgery painful?", "No. It is done under local anaesthesia; mild swelling for a few days is normal."],
                ["How long should I stay after surgery?", "Usually 2–3 days for the first check-up before you fly home."],
            ],
        },
        "keywords": {
            "en": ["dental surgery in turkey", "dental surgery in turkey cost", "dental surgery turkey cost",
                   "dental surgery turkey reviews", "wisdom tooth extraction turkey"],
            "de": ["zahnchirurgie türkei", "weisheitszahn op türkei"], "nl": ["kaakchirurg turkije"],
            "fr": ["chirurgie dentaire turquie"], "it": ["chirurgia dentale turchia"], "es": ["cirugía dental turquía"],
            "pl": ["chirurgia stomatologiczna turcja"], "ru": ["хирургическая стоматология турция"],
            "uk": ["хірургічна стоматологія туреччина"], "ar": ["جراحة الأسنان في تركيا"], "sv": ["tandkirurgi turkiet"],
            "da": ["tandkirurgi tyrkiet"], "no": ["tannkirurgi tyrkia"], "ro": ["chirurgie dentara turcia"],
            "az": ["türkiyədə diş cərrahiyyəsi"], "tr": ["ağız diş cerrahisi istanbul", "yirmilik diş çekimi şişli"],
        },
    },
    # ── G10 ───────────────────────────────────────────────────────────────
    "dental-guarantee-aftercare": {
        "group": "G10", "kind": "trust", "order": 12,
        "slugs": {"en": "dental-guarantee-aftercare-turkey", "de": "garantie-nachsorge-zahnbehandlung-tuerkei",
                  "nl": "garantie-nazorg-tandarts-turkije", "fr": "garantie-suivi-soins-dentaires-turquie",
                  "it": "garanzia-assistenza-dentista-turchia", "es": "garantia-seguimiento-dental-turquia",
                  "pl": "gwarancja-opieka-leczenie-zebow-turcja", "ru": "garantiya-lechenie-zubov-turciya",
                  "uk": "garantiya-likuvannya-zubiv-turechchyna", "ar": "daman-wa-mutabaat-ilaj-al-asnan",
                  "sv": "garanti-eftervard-tandvard-turkiet", "da": "garanti-efterbehandling-tyrkiet",
                  "no": "garanti-oppfolging-tannbehandling-tyrkia", "ro": "garantie-tratament-dentar-turcia",
                  "az": "dis-mualicesi-zemanet", "tr": "dis-tedavisi-garanti-takip"},
        "en": {
            "h1": "Guarantee, aftercare and payment for dental treatment in Turkey",
            "lead": "What happens after you fly home matters as much as the treatment. Here is how our written guarantee, "
                    "aftercare and payment work.",
            "meta_title": "Dental Treatment Turkey: Guarantee, Aftercare & Payment",
            "meta_description": "Written guarantee, aftercare at home and payment options for dental treatment in Istanbul. "
                                "Fixed quotes, no hidden costs.",
            "body": """## Written guarantee

You receive a written treatment plan and the guarantee information for your treatment before it starts. If there is a technical problem with our work, we fix it.

## Aftercare when you are back home

Follow-up continues on WhatsApp and email. If needed, we coordinate with a local dentist in your country and guide you by video call.

## Payment options

We accept cash and credit card. Your quote is fixed — the price agreed at the start is the price you pay. Ask us about paying in instalments for larger plans.""",
            "faq": [
                ["What if something goes wrong after I return home?", "Message us on WhatsApp with photos. We assess the "
                 "situation, coordinate with a local dentist if needed and plan any correction with you."],
            ],
        },
        "keywords": {
            "en": ["dental treatment turkey guarantee", "dental work turkey warranty", "dental aftercare turkey",
                   "dental treatment turkey payment plan", "dental treatment turkey finance"],
            "de": ["zahnbehandlung türkei garantie", "zahnbehandlung türkei nachsorge"],
            "nl": ["tandarts turkije garantie", "tandarts turkije nazorg"], "fr": ["soins dentaires turquie garantie"],
            "it": ["dentista turchia garanzia"], "es": ["tratamiento dental turquía garantía"],
            "pl": ["leczenie zębów turcja gwarancja"], "ru": ["лечение зубов турция гарантия"],
            "uk": ["лікування зубів туреччина гарантія"], "ar": ["ضمان علاج الأسنان في تركيا"],
            "sv": ["tandvård turkiet garanti"], "da": ["tandbehandling tyrkiet garanti"], "no": ["tannbehandling tyrkia garanti"],
            "ro": ["tratament dentar turcia garantie"], "az": ["diş müalicəsi zəmanət"], "tr": ["diş tedavisi garanti", "implant garantisi"],
        },
    },
    "smile-gallery": {
        "group": "G10", "kind": "gallery", "order": 13, "show_cases": True,
        "slugs": {"en": "before-and-after-smile-gallery", "de": "vorher-nachher-zaehne", "nl": "voor-en-na-tanden",
                  "fr": "avant-apres-sourire", "it": "prima-e-dopo-denti", "es": "antes-y-despues-dientes",
                  "pl": "przed-i-po-zeby", "ru": "do-i-posle-zuby", "uk": "do-i-pislya-zuby", "ar": "qabl-wa-bad-al-asnan",
                  "sv": "fore-och-efter-tander", "da": "foer-og-efter-taender", "no": "for-og-etter-tenner",
                  "ro": "inainte-si-dupa-dinti", "az": "evvel-ve-sonra-disler", "tr": "once-sonra-gulus-galerisi"},
        "en": {
            "h1": "Before and after — smile gallery and teeth shade guide",
            "lead": "Real results from our clinic, published with patient consent — and how we choose a natural tooth shade "
                    "instead of a one-size-fits-all bright white.",
            "meta_title": "Before and After Smile Gallery — Teeth Shade Guide",
            "meta_description": "Real before-and-after results from our dental clinic in Istanbul, and how to choose a "
                                "natural tooth shade with the VITA shade guide.",
            "body": """## Teeth shades: choosing a natural colour

We match the shade using the VITA shade guide: A (reddish-brown), B (reddish-yellow), C (grey) and D (reddish-grey), from light (1) to dark (4), plus extra-bright bleach shades. A natural smile usually sits close to your own eyes and skin tone — not at the brightest shade on the chart.

## Real cases, not stock photos

Every photo on this page shows a real patient of our clinic, published with consent. Results differ from person to person — your plan starts with an examination.""",
            "faq": [
                ["Can I choose my own tooth colour?", "Yes. We show you the shade guide and a digital preview, and "
                 "recommend a shade that looks natural for your face."],
            ],
        },
        "keywords": {
            "en": ["dental before and after turkey", "smile gallery turkey", "teeth before and after turkey",
                   "teeth shades colour chart", "veneers before and after turkey"],
            "de": ["zähne vorher nachher türkei", "zahnfarbe farbskala"], "nl": ["tanden voor en na turkije"],
            "fr": ["dents avant après turquie"], "it": ["denti prima e dopo turchia"], "es": ["dientes antes y después turquía"],
            "pl": ["zęby przed i po turcja"], "ru": ["зубы до и после турция"], "uk": ["зуби до і після туреччина"],
            "ar": ["الأسنان قبل وبعد تركيا"], "sv": ["tänder före och efter turkiet"], "da": ["tænder før og efter tyrkiet"],
            "no": ["tenner før og etter tyrkia"], "ro": ["dinti inainte si dupa turcia"], "az": ["dişlər əvvəl və sonra"],
            "tr": ["diş önce sonra", "gülüş tasarımı önce sonra", "diş renk skalası"],
        },
    },
    # ── L2-G5 ajans ───────────────────────────────────────────────────────
    "dental-tourism-agency": {
        "group": "L2-G5", "kind": "b2b", "order": 14,
        "slugs": {"en": "dental-tourism-agency-partnership", "de": "zahntourismus-agentur-partner",
                  "nl": "tandheelkundig-toerisme-bureau-partner", "fr": "agence-tourisme-dentaire-partenaire",
                  "it": "agenzia-turismo-dentale-partner", "es": "agencia-turismo-dental-socio",
                  "pl": "agencja-turystyki-dentystycznej-partner", "ru": "agentstvo-stomatologicheskogo-turizma",
                  "uk": "agentstvo-stomatologichnogo-turyzmu", "ar": "wakala-al-siyaha-al-ilajiya-lil-asnan",
                  "sv": "tandturism-byra-partner", "da": "tandturisme-bureau-partner", "no": "tannturisme-byra-partner",
                  "ro": "agentie-turism-dentar-partener", "az": "dis-turizmi-agentliyi", "tr": "dis-turizmi-acentesi-is-birligi"},
        "en": {
            "h1": "Dental tourism agency in Turkey? Work directly with our clinic",
            "lead": "Agencies and facilitators: partner with a dentist-led clinic in Istanbul that values honest treatment "
                    "plans over volume. Patients: you can also contact us directly — no agency needed.",
            "meta_title": "Dental Tourism Agency Turkey — Partner with Our Clinic",
            "meta_description": "Dental tourism agencies and facilitators: partner with a transparent, dentist-led clinic "
                                "in Istanbul. Patients can also contact us directly.",
            "body": """## For agencies and facilitators

- Every patient is examined and treated by the dentist personally
- Written plans and fixed quotes your clients can trust
- Appointments planned around your clients' travel dates
- Multilingual communication and aftercare via WhatsApp

## For patients: do you need a dental tourism agency?

No. You can contact our clinic directly on WhatsApp or by phone. You receive the same personal plan and the same very affordable, fixed price. An agency can help with travel, but the medical decisions should always be made with the dentist.

## Get in touch

Call us or message us on WhatsApp — tell us whether you are a patient or an agency.""",
            "faq": [
                ["Do I need an agency to get dental treatment in Turkey?", "No. You can contact the clinic directly — "
                 "that is often simpler and more transparent."],
            ],
        },
        "keywords": {
            "en": ["dental tourism agency", "dental tourism agency turkey", "dental tourism facilitator turkey"],
            "de": ["zahntourismus agentur", "zahnreise türkei agentur"], "nl": ["tandartsreis bureau turkije"],
            "fr": ["agence tourisme dentaire turquie"], "it": ["agenzia turismo dentale turchia"],
            "es": ["agencia turismo dental turquía"], "pl": ["agencja turystyki dentystycznej"],
            "ru": ["агентство стоматологического туризма"], "uk": ["агентство стоматологічного туризму"],
            "ar": ["وكالة السياحة العلاجية للأسنان في تركيا"], "sv": ["tandturism byrå"], "da": ["tandturisme bureau"],
            "no": ["tannturisme byrå"], "ro": ["agenție turism dentar"], "az": ["diş turizmi agentliyi"],
            "tr": ["diş turizmi acentesi", "sağlık turizmi acentesi iş birliği"],
        },
    },
    # ── L2-G7 ─────────────────────────────────────────────────────────────
    "istanbul-guide": {
        "group": "L2-G7", "kind": "guide", "order": 15,
        "slugs": {"en": "istanbul-guide-for-dental-patients", "de": "istanbul-reisefuehrer-fuer-zahnpatienten",
                  "nl": "istanbul-gids-voor-tandartspatienten", "fr": "guide-istanbul-patients-dentaires",
                  "it": "guida-istanbul-pazienti-dentali", "es": "guia-estambul-pacientes-dentales",
                  "pl": "przewodnik-stambul-dla-pacjentow", "ru": "putevoditel-stambul-dlya-patsientov",
                  "uk": "putivnyk-stambul-dlya-patsiyentiv", "ar": "dalil-istanbul-li-mardaa-al-asnan",
                  "sv": "istanbul-guide-for-tandpatienter", "da": "istanbul-guide-til-tandpatienter",
                  "no": "istanbul-guide-for-tannpasienter", "ro": "ghid-istanbul-pacienti-dentari",
                  "az": "dis-xestereri-ucun-istanbul-beledcisi", "tr": "dis-hastalari-icin-istanbul-rehberi"},
        "en": {
            "h1": "Istanbul guide for dental patients: where to stay and areas to avoid",
            "lead": "Coming to Istanbul for dental treatment? Where to stay near the clinic, how to get around, and which "
                    "areas to avoid at night.",
            "meta_title": "Istanbul for Dental Patients: Where to Stay, Areas to Avoid",
            "meta_description": "Where to stay in Istanbul during dental treatment, how to get around and Istanbul areas to "
                                "avoid at night — practical tips from our clinic in Şişli.",
            "body": """## Where to stay

Stay close to the clinic so that appointments are easy: Şişli, Osmanbey, Nişantaşı, Pangaltı and Harbiye are safe, central and within walking distance or one metro stop. Taksim and Beşiktaş are also well connected.

## Getting around

- Metro M2 (Taksim – Osmanbey – Şişli) is the easiest way to reach us
- Use licensed taxis or ride-hailing apps; agree on the meter
- From Istanbul Airport: the M11 metro, a taxi or a ride-hailing app

## Istanbul areas to avoid

Istanbul is generally safe for visitors, but like any big city it has areas where you should be careful, especially at night:

- Side streets of Tarlabaşı, behind İstiklal Avenue
- Parts of Aksaray and Laleli late at night
- Crowded spots such as İstiklal Avenue and the Grand Bazaar: watch out for pickpockets
- Avoid unofficial "guides" and bars that invite you in on the street

## After treatment

After implants or surgery, plan a quiet day: avoid alcohol, hot baths and intense sightseeing for 24–48 hours.""",
            "faq": [
                ["Is Şişli a safe area to stay?", "Yes. Şişli, Osmanbey and Nişantaşı are central, busy and safe "
                 "residential and shopping districts."],
            ],
        },
        "keywords": {
            "en": ["istanbul areas to avoid", "where to stay in istanbul for dental treatment", "is istanbul safe"],
            "de": ["istanbul gefährliche viertel", "wo übernachten istanbul"], "nl": ["istanbul wijken vermijden"],
            "fr": ["quartiers à éviter istanbul"], "it": ["zone da evitare istanbul"], "es": ["zonas a evitar en estambul"],
            "pl": ["stambuł niebezpieczne dzielnice"], "ru": ["опасные районы стамбула"], "uk": ["небезпечні райони стамбула"],
            "ar": ["مناطق يجب تجنبها في إسطنبول"], "sv": ["istanbul områden att undvika"], "da": ["istanbul områder at undgå"],
            "no": ["istanbul områder å unngå"], "ro": ["zone de evitat istanbul"], "az": ["istanbulda təhlükəli rayonlar"],
            "tr": ["istanbul'da kalınacak yerler diş tedavisi"],
        },
    },
}

# G2 / G3: /prices/ ve /prices/<tedavi>/ sayfaları — RAKAM YOK, "uygun, telefonla/WhatsApp'tan kişisel fiyat"
PRICE_KEYWORDS = {
    "index": {
        "en": ["dental price turkey", "dental prices turkey", "dental clinic turkey price", "teeth price in turkey",
               "turkey teeth how much", "dental care prices in turkey", "dental care turkey prices",
               "dental care in turkey cost", "dental care turkey cost", "dental work in turkey cost",
               "dental work in turkey price", "dental work prices in turkey", "dental work turkey cost",
               "dental aesthetic turkey price", "turkey teeth packages price", "turkey dental packages price list",
               "cheap dental turkey", "cheap dental work turkey", "cheap dental treatment turkey"],
        "de": ["zahnbehandlung türkei kosten", "zahnarzt türkei preise", "zähne türkei kosten", "zahnarzt türkei günstig"],
        "nl": ["tandarts turkije prijzen", "tanden turkije kosten", "goedkope tandarts turkije"],
        "fr": ["prix dentiste turquie", "soins dentaires turquie prix", "dentiste pas cher turquie"],
        "it": ["prezzi dentista turchia", "costo cure dentali turchia"], "es": ["precios dentista turquía", "dentista barato turquía"],
        "pl": ["ceny dentysta turcja", "leczenie zębów turcja koszt"], "ru": ["цены на стоматологию в турции", "сколько стоят зубы в турции"],
        "uk": ["ціни стоматологія туреччина"], "ar": ["أسعار علاج الأسنان في تركيا", "كم تكلفة الأسنان في تركيا"],
        "sv": ["tandläkare turkiet priser"], "da": ["tandlæge tyrkiet priser"], "no": ["tannlege tyrkia priser"],
        "ro": ["preturi dentist turcia"], "az": ["türkiyədə diş qiymətləri"], "tr": ["diş tedavisi fiyatları istanbul", "şişli diş fiyatları"],
    },
    # tedavi slug'ı (EN) → İngilizce keyword'ler; diğer dillerde "treatment_pattern"
    "treatment": {
        "dental-implants": ["price of dental implants in turkey", "price dental implants turkey",
                            "dental implants price list turkey", "dental implants turkey price list",
                            "full dental implants price turkey", "full mouth dental implants turkey price reddit",
                            "dental implant cost turkey reddit", "dental implants turkey antalya price"],
        "porcelain-veneers": ["dental veneers price in turkey"],
        "zirconia-crowns": ["dental crown price in turkey", "dental bridge price in turkey"],
        "composite-veneers": ["dental bonding price turkey"],
        "all-on-4-implants": ["full mouth dental implants turkey price list", "full mouth dental implants turkey price"],
        "hollywood-smile": ["dental aesthetic turkey price", "turkey teeth price"],
    },
    "treatment_pattern": {
        "en": "{t} price turkey", "de": "{t} türkei kosten", "nl": "{t} turkije prijs", "fr": "{t} turquie prix",
        "it": "{t} turchia prezzo", "es": "{t} turquía precio", "pl": "{t} turcja cena", "ru": "{t} в турции цена",
        "uk": "{t} туреччина ціна", "ar": "سعر {t} في تركيا", "sv": "{t} turkiet pris", "da": "{t} tyrkiet pris",
        "no": "{t} tyrkia pris", "ro": "{t} turcia pret", "az": "{t} türkiyə qiymət", "tr": "{t} fiyatları istanbul",
    },
}

# G4 + L2-G3: /packages/<tedavi>/ sayfalarındaki "best … clinic in Istanbul" bölümü
TREATMENT_PAGE_KEYWORDS = {
    "dental-implants": ["best dental clinic in turkey for implants", "best dental clinic in istanbul for implants",
                        "best dental implant clinic istanbul", "best dental implant clinic in istanbul turkey",
                        "best dental implant tourism", "best medical tourism for dental implants",
                        "best place for dental tourism implants", "dental tourism implants turkey",
                        "medical tourism dental implants turkey"],
    "porcelain-veneers": ["best dental clinic in turkey for veneers", "best veneers clinic in istanbul"],
    "zirconia-crowns": ["best dental clinic in turkey for crowns"],
    "teeth-whitening": ["best teeth whitening clinic istanbul"],
}

# Bilinçli olarak HEDEFLENMEYENLER
NOT_TARGETED = {
    "Rakip klinik markaları (liste 1 G9)": "rakip klinik marka aramaları — marka hakkı / navigasyonel",
    "Dental Centre Turkey marka sorguları (G10)": "dct trustpilot, dct reviews … — sadece konu fikri olarak kullanıldı",
    "Best Clinic Istanbul markası (liste 2 G8)": "best clinic istanbul (1.9K), avis, reseñas, yorumlar, alger … — marka araması",
    "Diğer markalar (liste 2)": "good look clinic, xclinic cadde, best self clinic, best world hair clinic, best care clinic, best dental istanbul photos",
    "Başka ülkelerdeki klinik aramaları": "dental tourism mexico reviews, san jose del cabo, china, delhi, ahmedabad … (ülke karşılaştırma sayfasında sadece genel bahis)",
    "Dental dışı": "saç ekimi, estetik/cilt, hastane/genel tıp, diş hekimliği fakülteleri, dental tourism crm",
    "Alakasız (G11)": "sargodha, dar es salaam, dental market turkiye, dental clinic 34",
    "Ortodonti": "dental braces price in turkey — klinik ortodonti (tel) yapmıyor",
}


def topic_by_slug(slug, lang):
    for key, t in TOPICS.items():
        if t["slugs"].get(lang) == slug:
            return key, t
    return None, None
