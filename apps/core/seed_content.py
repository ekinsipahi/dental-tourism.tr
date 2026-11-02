"""seed_data komutu için başlangıç içeriği (İngilizce kaynak). Değerleri admin'den güncelleyebilirsiniz."""

TREATMENTS = [
    {
        "key": "dental-implants", "category": "implant", "icon": "🦷", "order": 9,
        "price": (500, 700), "unit": "per implant", "stay": "5-7", "visits": 2, "duration": "1-2 hours per implant",
        "name": "Dental Implants",
        "short": "A titanium root and a natural-looking crown that permanently replace a missing tooth. "
                 "At our clinic an implant is the last resort — we try to save your own tooth first.",
        "meta_title": "Dental Implants Istanbul 2026 — 3D-Planned, ★{rating} on Google",
        "meta_description": "Dental implants in Istanbul with CE-certified brands, 3D planning and a fixed written quote. Two short visits, 35+ years' experience. Free WhatsApp assessment.",
        "kw": "dental implants turkey",
        "body": """## What is a dental implant?
A dental implant is a small titanium (or zirconia) screw placed in the jawbone where a tooth is missing. After it has fused with the bone, a crown is fixed on top. The result looks, feels and functions like a natural tooth.

## Who is it for?
Implants suit adults who have lost one or more teeth and have enough healthy bone — or can receive a bone graft. Before recommending an implant we always check whether your own tooth can still be saved with a root canal treatment or a crown.

## The process in Istanbul
1. **Visit 1 (5–7 days):** examination, 3D scan, implant placement and a temporary solution.
2. **Healing (3–6 months at home):** the implant integrates with the bone.
3. **Visit 2 (5–7 days):** the final crown is made and fitted.

## Risks and aftercare
As with any surgery there can be swelling, bruising or — rarely — infection or implant failure. Smokers and patients with uncontrolled diabetes have a higher risk. Good oral hygiene and regular check-ups are essential for the implant to last for many years.""",
        "faq": [
            {"question": "Do dental implants hurt?", "answer": "The procedure is done under local anaesthesia, so you feel pressure but no pain. Mild soreness for a few days afterwards is normal and is controlled with standard painkillers."},
            {"question": "How long do I need to stay in Istanbul for implants?", "answer": "Usually two trips: about 5–7 days for placement and 5–7 days for the final crowns, 3–6 months apart."},
            {"question": "Which implant brands do you use?", "answer": "We use CE-certified implant systems and tell you the exact brand, with documentation, before treatment."},
        ],
    },
    {
        "key": "porcelain-veneers", "category": "cosmetic", "icon": "✨", "order": 7,
        "price": (180, None), "unit": "per tooth", "stay": "5-7", "visits": 1, "duration": "2 appointments",
        "name": "Porcelain Veneers",
        "short": "Thin porcelain shells bonded to the front of the teeth to correct colour, shape and small gaps — "
                 "with only as much tooth reduction as is truly necessary.",
        "meta_title": "Porcelain Veneers Istanbul — Natural Look, Minimal Prep (2026)",
        "meta_description": "Porcelain veneers in Istanbul designed for your face: minimal preparation, natural shade, ready in about a week. ★ {rating} on Google. Free smile assessment.",
        "kw": "veneers turkey",
        "body": """## What are porcelain veneers?
Veneers are thin, custom-made ceramic shells bonded to the front surface of the teeth. They change the colour, shape and length of teeth and close small gaps.

## Are they right for you?
Veneers suit healthy teeth with cosmetic problems: discolouration that does not respond to whitening, chipped edges, uneven shapes. They are not a fix for crooked bites or gum disease — those need to be treated first.

## The process
Day 1: consultation, photos, digital smile design. Day 2: minimal preparation and temporary veneers. Days 5–7: try-in, adjustments and final bonding.

## How long do they last?
Well-made porcelain veneers can last 10–15 years with good hygiene, a night guard if you grind your teeth, and regular check-ups.""",
        "faq": [
            {"question": "Will my teeth be ground down?", "answer": "A thin layer of enamel is usually removed so the veneer does not look bulky. We remove only what is necessary and discuss non-prep options when suitable."},
            {"question": "How many veneers do I need?", "answer": "That depends on your smile line. Many patients need 6–10 upper teeth; we decide together after the digital smile design."},
            {"question": "Porcelain or composite veneers?", "answer": "Porcelain lasts longer and keeps its colour; composite is cheaper, done in one session and needs no tooth reduction, and with a good material and proper care it also keeps its colour for years."},
        ],
    },
    {
        "key": "zirconia-crowns", "category": "restorative", "icon": "👑", "order": 6,
        "price": (150, None), "unit": "per crown", "stay": "5-7", "visits": 1, "duration": "2-3 appointments",
        "name": "Zirconia Crowns",
        "short": "Strong, metal-free crowns that protect weakened teeth and look natural — the most durable "
                 "crown option available.",
        "meta_title": "Zirconia Crowns Istanbul — Metal-Free, Ready in About a Week",
        "meta_description": "Metal-free zirconia crowns in Istanbul: natural-looking, strong and planned to keep as much of your tooth as possible. About one week in Istanbul. Free assessment.",
        "kw": "zirconia crowns turkey",
        "body": """## What is a zirconia crown?
A crown covers the whole visible part of a tooth to protect it and restore its shape. Zirconia is a very strong, biocompatible ceramic without a metal core, so there is no grey line at the gum.

## When is a crown needed?
After a root canal treatment, for heavily filled or cracked teeth, or on top of an implant. For purely cosmetic changes on healthy teeth, veneers are often the more conservative option.

## The process
The tooth is prepared and scanned, a temporary crown is fitted, and the final zirconia crown is cemented after a try-in — usually within 5–7 days.""",
        "faq": [
            {"question": "How long do zirconia crowns last?", "answer": "With good care zirconia crowns often last 15 years or more. Regular check-ups help detect problems early."},
            {"question": "Is zirconia better than porcelain-fused-to-metal?", "answer": "Zirconia has no metal, so it looks more natural at the gum line and is suitable for patients with metal sensitivity."},
        ],
    },
    {
        "key": "all-on-4", "category": "implant", "icon": "💎", "order": 10,
        "price": (4500, None), "unit": "per arch", "stay": "5-7", "visits": 2, "duration": "1 day surgery",
        "name": "All-on-4 Implants",
        "short": "A complete fixed set of teeth on four (or six) implants per jaw — for patients who have lost "
                 "most of their teeth or wear dentures.",
        "meta_title": "All-on-4 Implants Istanbul — Fixed Teeth Instead of Dentures",
        "meta_description": "All-on-4 and All-on-6 in Istanbul: fixed full-arch teeth instead of dentures, a temporary bridge within days and 3D planning. Free treatment plan on WhatsApp.",
        "kw": "all on 4 turkey",
        "body": """## What is All-on-4?
All-on-4 replaces a full arch of teeth with a fixed bridge supported by four implants (All-on-6 uses six). The back implants are angled to make the most of the available bone, which often avoids bone grafting.

## Who is a candidate?
Patients with many failing or missing teeth, or who struggle with removable dentures. A 3D scan shows whether there is enough bone.

## The process
Visit 1: extractions if needed, implant placement and a fixed temporary bridge within a few days. After 3–6 months of healing, visit 2: the final bridge (zirconia or acrylic-titanium) is fitted.""",
        "faq": [
            {"question": "Will I leave with teeth?", "answer": "In most cases you leave the first visit with a fixed temporary bridge, so you are never without teeth."},
            {"question": "All-on-4 or All-on-6?", "answer": "It depends on your bone volume and bite. Six implants spread the load more; four can avoid grafting. We decide after the 3D scan."},
        ],
    },
    {
        "key": "root-canal", "category": "general", "icon": "🔬", "order": 1,
        "price": (None, None), "unit": "per tooth", "stay": "1-3", "visits": 1, "duration": "1-2 appointments",
        "name": "Root Canal Treatment",
        "short": "Saves an infected or badly inflamed tooth instead of extracting it. Most teeth can be saved — "
                 "and should be.",
        "meta_title": "Root Canal Treatment Istanbul — Save Your Tooth in 1–2 Visits",
        "meta_description": "Save your natural tooth instead of extracting it: precise, comfortable root canal treatment in Istanbul in 1–2 appointments. Open 7 days. Free assessment.",
        "kw": "root canal treatment istanbul",
        "body": """## Why a root canal?
When the nerve inside a tooth becomes infected, the infection can spread to the bone. A root canal treatment cleans, disinfects and seals the canals so the tooth can stay in your mouth.

## Saving the tooth comes first
An extraction followed by an implant is more invasive and more expensive. Our ethical principle is simple: if the tooth can be saved, we save it.

## After treatment
A treated back tooth usually needs a crown to protect it from breaking.""",
        "faq": [
            {"question": "Is a root canal painful?", "answer": "With modern local anaesthesia the treatment itself feels similar to a filling. Mild sensitivity for a few days is normal."},
        ],
    },
    {
        "key": "composite-veneers", "category": "cosmetic", "icon": "😁", "order": 4,
        "price": (None, None), "unit": "per tooth", "stay": "1-3", "visits": 1, "duration": "1 session",
        "name": "Composite Veneers",
        "short": "Smile makeover with tooth-coloured composite, sculpted directly on the teeth — usually without "
                 "grinding and in a single session.",
        "meta_title": "Composite Veneers Istanbul — No Grinding, Often in One Session",
        "meta_description": "Composite veneers in Istanbul: reshape and brighten your teeth without grinding, often in a single session. ★ {rating} on Google. Free smile assessment on WhatsApp.",
        "kw": "composite veneers turkey",
        "body": """## What are composite veneers?
Composite veneers are made from tooth-coloured resin applied and shaped directly on your teeth. In most cases no enamel needs to be removed.

## Pros and cons
They are faster and more affordable than porcelain and fully reversible. With a good composite material and sensible eating habits they keep their colour for years — often no yellowing even after 5–6 or 10 years — and we have patients who have worn their composite veneers for 20 years. They need no separate maintenance schedule: the small polishing touches are simply part of your routine scaling visits.""",
        "faq": [
            {"question": "How long do composite veneers last?", "answer": "With a good composite material and proper care, many years — we have patients who have worn theirs for 20 years. There is no fixed polishing or replacement interval; minor polishing is done during routine scaling visits."},
        ],
    },
    {
        "key": "teeth-cleaning", "category": "general", "icon": "🪥", "order": 3,
        "price": (None, None), "unit": "per session", "stay": "1", "visits": 1, "duration": "30-45 minutes",
        "name": "Teeth Cleaning",
        "short": "Professional scaling and polishing that removes tartar and stains — the basis of healthy gums.",
        "meta_title": "Teeth Cleaning Istanbul — Scaling & Polishing, Open 7 Days",
        "meta_description": "Professional teeth cleaning in Istanbul: ultrasonic scaling and polishing for healthy gums and a fresher smile, with a dentist's check-up. Open 7 days a week.",
        "kw": "teeth cleaning istanbul",
        "body": """## Why professional cleaning?
Tartar cannot be removed with a toothbrush. Left in place it causes gum inflammation, bad breath and eventually bone loss. Ultrasonic scaling removes it gently, followed by polishing.""",
        "faq": [],
    },
    {
        "key": "tooth-filling", "category": "general", "icon": "🦴", "order": 2,
        "price": (None, None), "unit": "per tooth", "stay": "1", "visits": 1, "duration": "30-60 minutes",
        "name": "Tooth Fillings",
        "short": "Aesthetic composite fillings that restore decayed teeth. Done correctly, they last for many years.",
        "meta_title": "Tooth Fillings Istanbul — Tooth-Coloured, Done by a Dentist",
        "meta_description": "Tooth-coloured composite fillings in Istanbul: careful, painless treatment that keeps as much natural tooth as possible. Open 7 days. Free assessment.",
        "kw": "white fillings istanbul",
        "body": """## Composite fillings
Decay is removed and the tooth is rebuilt with tooth-coloured composite that bonds to the enamel, so less healthy tooth structure needs to be removed than with old amalgam fillings.""",
        "faq": [],
    },
    {
        "key": "teeth-whitening", "category": "cosmetic", "icon": "💡", "order": 5,
        "price": (None, None), "unit": "per session", "stay": "1", "visits": 1, "duration": "60-90 minutes",
        "name": "Teeth Whitening",
        "short": "In-office whitening that lightens natural teeth by several shades in a single visit.",
        "meta_title": "Teeth Whitening Istanbul — Several Shades Lighter in One Visit",
        "meta_description": "Professional in-office teeth whitening in Istanbul, supervised by a dentist: several shades lighter in one session, safely. Free assessment on WhatsApp.",
        "kw": "teeth whitening istanbul",
        "body": """## How whitening works
A professional whitening gel is applied to the teeth while the gums are protected. Results depend on your natural tooth colour; crowns and fillings do not change colour.""",
        "faq": [],
    },
    {
        "key": "hollywood-smile", "category": "cosmetic", "icon": "🌟", "order": 8,
        "price": (None, None), "unit": "per smile", "stay": "5-7", "visits": 1, "duration": "about 1 week",
        "name": "Hollywood Smile",
        "short": "A complete smile makeover planned digitally — with veneers or crowns designed to suit your "
                 "face, not a one-size-fits-all bright white.",
        "meta_title": "Hollywood Smile Istanbul — Natural, Not Over-White (2026)",
        "meta_description": "A Hollywood smile designed for your face, not a template: digital smile design, veneers or crowns, natural shade. About one week in Istanbul. ★ {rating} on Google.",
        "kw": "hollywood smile turkey",
        "body": """## A smile designed for you
"Hollywood smile" usually means a full makeover of the visible teeth with veneers or crowns. We start with a digital smile design so you can see and approve the result before any tooth is touched.

## Natural, not artificial
Too white, too large and too uniform teeth look fake. We choose a shade and shape that fit your face, age and skin tone — and we only prepare teeth as much as necessary.""",
        "faq": [
            {"question": "How many teeth are included in a Hollywood smile?", "answer": "Usually 16–20 teeth (the teeth visible when you smile in both jaws), but this depends on your smile line."},
        ],
    },
]

REVIEWS = [
    ("Melih E.", "TR", "tr", "Kanal tedavim acısız ve başarılı geçti ellerine sağlık"),
    ("Ece Y.", "TR", "tr", "38 yaşındayım, korkumu yenmeme neden bir doktordur. Eli hafif, güler yüzlü. Aynı anda 3 dolgu yaptık, hiç ağrım olmadı."),
    ("Cem T.", "TR", "tr", "Ufacık dişten dolgu ile diş yaptı. 3 doktor çekilmesi gerektiği söylemesine rağmen Devrim hanım kurtardı. Güvenle gidebilirsiniz."),
    ("Buse Y.", "TR", "tr", "Devrim hocam yıllardır güvendiğim, işini özenle yapan bir hekim. Yaptırdığım dolgular hep çok iyi sonuç verdi."),
    ("Ceren S.", "TR", "tr", "Devrim hoca ile 2020'de tanıştık. Yirmilik dişimi çektirmiştim, ön dişlerimi kaplama yaptırdım, yıllardır sorunsuz kullanıyorum."),
    ("Özlem H.", "TR", "tr", "Yıllardır hekimliğine güvendiğim, temizlik konusunda hiç şüphe duymadığım işinin ehli bir diş doktorudur."),
]

VIDEOS = [
    ("Doruk O.", "TR", "pArVqGBhSm4", "dental-implants"),
    ("Nika", "RU", "rnLVclfU0Tc", "root-canal"),
    ("Hazan", "TR", "yEGBHXrapMM", "root-canal"),
    ("Işık", "TR", "HlCQeyD0Zu4", "porcelain-veneers"),
    ("Marissa G.", "NL", "iVhUafgUj10", "composite-veneers"),
]

BLOG_CATEGORIES = [
    ("Treatment Guides", "treatment-guides", "awareness", "What each dental treatment involves, who it is for and what to expect."),
    ("Costs & Comparisons", "costs-comparisons", "consideration", "Honest price comparisons and what is included in dental treatment abroad."),
    ("Planning Your Trip", "planning-your-trip", "decision", "Step-by-step guidance for travelling to Istanbul for dental treatment."),
    ("Dental Health", "dental-health", "awareness", "Prevention, aftercare and keeping your teeth healthy for life."),
]

# Mevcut site metnindeki İngiltere fiyatları (tek değer). EUR karşılığı ~1.17 kurla.
# KAYNAĞI DOĞRULAYIP admin'den güncelleyin (verified=False olarak eklenir).
MARKET_PRICES = {
    "dental-implants": [("GB", "GBP", 2500, 2500, 2925, 2925)],
    "porcelain-veneers": [("GB", "GBP", 800, 800, 936, 936)],
    "zirconia-crowns": [("GB", "GBP", 900, 900, 1053, 1053)],
    "all-on-4": [("GB", "GBP", 15000, 15000, 17550, 17550)],
}
