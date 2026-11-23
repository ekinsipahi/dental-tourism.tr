# İlçe budaması, 17 dil ve çalışma saati temizliği — dağıtım raporu (22.11.2026, gece)

Hekimin 22.11.2026 kararlarıyla üç sitede yapılan her değişikliğin sayfa sayfa kaydı. Hepsi geri alınabilir;
geri alma yolları §8'de. Etki ölçümü §9'da. Ekler: ekA (drdevrim silinen 2.233 adres), ekB (drdevrim eklenen 2.145 adres).

## 1. Özet

| Site | Sitemap önce | Sitemap sonra | Silinen | Eklenen | Düzeltilen |
|---|---|---|---|---|---|
| drdevrim.com | 4.431 | **4.343** (canlıda doğrulandı) | 2.233 pSEO sayfası (410 Gone) | 2.145 pSEO sayfası (11 yeni dil) | 51 dosya → tüm sayfalarda saat 05:00–00:00, gece/acil/7-24 ifadeleri yok |
| devrimbirikensipahi.com.tr | 153 | **128** (canlıda doğrulandı) | 13 blog yazısı (301) + 12 hesap sayfası sitemap'ten | — | 44 blog yazısının içeriği (acil/7-24/gece cümleleri, anahtar kelime listeleri, 13 yazıya giden linkler); ana sayfa 5 ilçe etiketi |
| dentaltourism.tr | 1.284 | 1.284 | — | — | yalnızca salt-okunur ölçüm komutu `pseo_etki` |

Dağıtım: drdevrim `afd0331 → 3c971d3` (Netlify, canlıda 22.11 saat 22:30), devrimbirikensipahi `1674922 → 6ab4d25 → ef04031` (Render devrim-web).
Blog içerik temizliği (44 yazı, veritabanı): **uygulandı — Render açılış kancası göç 0003'ü dağıtımda çalıştırdı; canlıda 44/44 yazı doğrulandı (22.11.2026 23:05)**.
Ek dağıtım 23.11.2026 22:02: drdevrim'de "acil" niyeti ve "24 saat" ifadeleri de kaldırıldı (§11).

Not: dağıtım Google core update sürerken yapıldı (hekim kararı, 22.11 gece: "siktir et, alalım"). Sıralama dalgalanması ilk haftalarda update etkisiyle karışacaktır; §9'daki ölçüm bunu ayırmaz, yalnızca kendi ziyaretçi verimizi gösterir.

## 2. drdevrim.com — silinen sayfalar (2.233 adres, hepsi 410 Gone)

21 ilçe ve 182 mahallesi, 11 sayfa ailesinden birden çıkarıldı. Her ilçe için 11 ilçe sayfası + mahalle sayısı × 11 mahalle sayfası.
Aileler: `/disci/`, `/haftasonu/`, `/en-iyi-disci/`, `/uzman-dis-hekimi/`, `/prof-dis-hekimi/`, `/estetik-dis-klinigi/`, `/en/dentist/`, `/ru/stomatolog/`, `/uk/stomatolog/`, `/bg/zabolekar/`, `/de/zahnarzt/`.
Aile başına silinen: disci 203, haftasonu 203, en-iyi-disci 203, uzman-dis-hekimi 203, prof-dis-hekimi 203, estetik-dis-klinigi 203, en/dentist 203, ru/stomatolog 203, uk/stomatolog 203, bg/zabolekar 203, de/zahnarzt 203 (her ailede 21 ilçe + 182 mahalle = 203).

| # | İlçe | Mahalle sayısı | Silinen sayfa | Mahalleler (slug) |
|---|---|---|---|---|
| 1 | Sultangazi (`sultangazi`) | 8 | 99 | cebeci, gazi, habibler, ismetpasa, malkoceoglu, sultanciftligi, sultangazi-merkez, ugur-mumcu |
| 2 | Ümraniye (`umraniye`) | 12 | 143 | altunizade, atakent, cakmak, camlik, dudullu, esenevler, hekimbasi, istiklal, kucukbakkalkoy, mimar-sinan, namik-kemal, site |
| 3 | Beykoz (`beykoz`) | 10 | 121 | anadoluhisari, beykoz-merkez, cubuklu, goztepe, kanlica, ortacesme, pasabahce, poyrazkoy, riva, yalikoy |
| 4 | Ataşehir (`atasehir`) | 10 | 121 | ataturk, barbaros, esatpasa, fetih, icerenkoy, kucukbakkalkoy, mevlana, mustafa-kemal, yenisahra, yukari-dudullu |
| 5 | Başakşehir (`basaksehir`) | 7 | 88 | altinsehir, bahcesehir-1, bahcesehir-2, basak, kayabasi, olimpiyatkoy, ziya-gokalp |
| 6 | Çekmeköy (`cekmekoy`) | 6 | 77 | cekmekoy-merkez, eksioglu, hamidiye, nisantepe, resadiye, tasdelen |
| 7 | Küçükçekmece (`kucukcekmece`) | 11 | 132 | atakent, ataturk, fatih, gultepe, halkali, inonu, kanarya, kartaltepe, kucukcekmece-merkez, tevfikbey, yarimburgaz |
| 8 | Maltepe (`maltepe`) | 11 | 132 | altay, altintepe, baglarbasi, basibuyuk, cevizli, findikli, gulsuyu, idealtepe, kucukyali, maltepe-merkez, zumrutevler |
| 9 | Sancaktepe (`sancaktepe`) | 9 | 110 | akpinar, emek, eyup-sultan, ismetpasa, kaynarca, meclis, mimar-sinan, sancaktepe-merkez, sarigazi |
| 10 | Avcılar (`avcilar`) | 10 | 121 | ambarli, cihangir, denizkoskler, firuzkoy, gumuspala, merkez, mustafa-kemal, tahtakale, universite, yesilkent |
| 11 | Arnavutköy (`arnavutkoy`) | 8 | 99 | arnavutkoy-merkez, bolluca, dursunkoy, hadimkoy, haracci, imrahor, nenehatun, tasoluk |
| 12 | Adalar (`adalar`) | 4 | 55 | buyukada, burgazada, heybeliada, kinalıada |
| 13 | Kartal (`kartal`) | 11 | 132 | ankara, atalar, cevizli, esentepe, gumuspinar, hurriyet, kartal-merkez, orhantepe, soganlik, ugur-mumcu, yakacik |
| 14 | Esenyurt (`esenyurt`) | 10 | 121 | akevler, ardicsli, esenyurt-merkez, fatih, guzelyurt, kaptanpasa, mehtap, pinar, saadetdere, sultanmurat |
| 15 | Pendik (`pendik`) | 10 | 121 | arslanbey, bati, camlik, dogu, guzelyali, kurtkoy, pendik-merkez, suluntepe, velibaba, yenisehir |
| 16 | Beylikdüzü (`beylikduzu`) | 8 | 99 | baris, beylikduzu-merkez, buyuksehir, cumhuriyet, dereagzi, gurpinar, kavakli, marmara |
| 17 | Büyükçekmece (`buyukcekmece`) | 7 | 88 | akcatepe, buyukcekmece-merkez, canta, karaagac, kumburgaz, mimaroba, tepecik |
| 18 | Tuzla (`tuzla`) | 8 | 99 | aydinli, cinarli, evliya-celebi, icmeler, mimar-sinan, orhangazi, postane, tuzla-merkez |
| 19 | Çatalca (`catalca`) | 8 | 99 | catalca-merkez, ciftlikkoy, ferhatpasa, gumuspinar, kabakca, karacakoy, muratbey, ormanli |
| 20 | Şile (`sile`) | 6 | 77 | agva, balikli, cayirbasi, kalem, komurlu, sile-merkez |
| 21 | Silivri (`silivri`) | 8 | 99 | alipasa, buyuksinekli, canta, fener, gumusyaka, kavakli, selimpasa, silivri-merkez |

Her ilçe için silinen ilçe sayfaları (mahalle sayfaları aynı kalıpla `/<aile>/<ilçe>/<mahalle>/`):

- **Sultangazi:** /disci/sultangazi/ · /haftasonu/sultangazi/ · /en-iyi-disci/sultangazi/ · /uzman-dis-hekimi/sultangazi/ · /prof-dis-hekimi/sultangazi/ · /estetik-dis-klinigi/sultangazi/ · /en/dentist/sultangazi/ · /ru/stomatolog/sultangazi/ · /uk/stomatolog/sultangazi/ · /bg/zabolekar/sultangazi/ · /de/zahnarzt/sultangazi/
- **Ümraniye:** /disci/umraniye/ · /haftasonu/umraniye/ · /en-iyi-disci/umraniye/ · /uzman-dis-hekimi/umraniye/ · /prof-dis-hekimi/umraniye/ · /estetik-dis-klinigi/umraniye/ · /en/dentist/umraniye/ · /ru/stomatolog/umraniye/ · /uk/stomatolog/umraniye/ · /bg/zabolekar/umraniye/ · /de/zahnarzt/umraniye/
- **Beykoz:** /disci/beykoz/ · /haftasonu/beykoz/ · /en-iyi-disci/beykoz/ · /uzman-dis-hekimi/beykoz/ · /prof-dis-hekimi/beykoz/ · /estetik-dis-klinigi/beykoz/ · /en/dentist/beykoz/ · /ru/stomatolog/beykoz/ · /uk/stomatolog/beykoz/ · /bg/zabolekar/beykoz/ · /de/zahnarzt/beykoz/
- **Ataşehir:** /disci/atasehir/ · /haftasonu/atasehir/ · /en-iyi-disci/atasehir/ · /uzman-dis-hekimi/atasehir/ · /prof-dis-hekimi/atasehir/ · /estetik-dis-klinigi/atasehir/ · /en/dentist/atasehir/ · /ru/stomatolog/atasehir/ · /uk/stomatolog/atasehir/ · /bg/zabolekar/atasehir/ · /de/zahnarzt/atasehir/
- **Başakşehir:** /disci/basaksehir/ · /haftasonu/basaksehir/ · /en-iyi-disci/basaksehir/ · /uzman-dis-hekimi/basaksehir/ · /prof-dis-hekimi/basaksehir/ · /estetik-dis-klinigi/basaksehir/ · /en/dentist/basaksehir/ · /ru/stomatolog/basaksehir/ · /uk/stomatolog/basaksehir/ · /bg/zabolekar/basaksehir/ · /de/zahnarzt/basaksehir/
- **Çekmeköy:** /disci/cekmekoy/ · /haftasonu/cekmekoy/ · /en-iyi-disci/cekmekoy/ · /uzman-dis-hekimi/cekmekoy/ · /prof-dis-hekimi/cekmekoy/ · /estetik-dis-klinigi/cekmekoy/ · /en/dentist/cekmekoy/ · /ru/stomatolog/cekmekoy/ · /uk/stomatolog/cekmekoy/ · /bg/zabolekar/cekmekoy/ · /de/zahnarzt/cekmekoy/
- **Küçükçekmece:** /disci/kucukcekmece/ · /haftasonu/kucukcekmece/ · /en-iyi-disci/kucukcekmece/ · /uzman-dis-hekimi/kucukcekmece/ · /prof-dis-hekimi/kucukcekmece/ · /estetik-dis-klinigi/kucukcekmece/ · /en/dentist/kucukcekmece/ · /ru/stomatolog/kucukcekmece/ · /uk/stomatolog/kucukcekmece/ · /bg/zabolekar/kucukcekmece/ · /de/zahnarzt/kucukcekmece/
- **Maltepe:** /disci/maltepe/ · /haftasonu/maltepe/ · /en-iyi-disci/maltepe/ · /uzman-dis-hekimi/maltepe/ · /prof-dis-hekimi/maltepe/ · /estetik-dis-klinigi/maltepe/ · /en/dentist/maltepe/ · /ru/stomatolog/maltepe/ · /uk/stomatolog/maltepe/ · /bg/zabolekar/maltepe/ · /de/zahnarzt/maltepe/
- **Sancaktepe:** /disci/sancaktepe/ · /haftasonu/sancaktepe/ · /en-iyi-disci/sancaktepe/ · /uzman-dis-hekimi/sancaktepe/ · /prof-dis-hekimi/sancaktepe/ · /estetik-dis-klinigi/sancaktepe/ · /en/dentist/sancaktepe/ · /ru/stomatolog/sancaktepe/ · /uk/stomatolog/sancaktepe/ · /bg/zabolekar/sancaktepe/ · /de/zahnarzt/sancaktepe/
- **Avcılar:** /disci/avcilar/ · /haftasonu/avcilar/ · /en-iyi-disci/avcilar/ · /uzman-dis-hekimi/avcilar/ · /prof-dis-hekimi/avcilar/ · /estetik-dis-klinigi/avcilar/ · /en/dentist/avcilar/ · /ru/stomatolog/avcilar/ · /uk/stomatolog/avcilar/ · /bg/zabolekar/avcilar/ · /de/zahnarzt/avcilar/
- **Arnavutköy:** /disci/arnavutkoy/ · /haftasonu/arnavutkoy/ · /en-iyi-disci/arnavutkoy/ · /uzman-dis-hekimi/arnavutkoy/ · /prof-dis-hekimi/arnavutkoy/ · /estetik-dis-klinigi/arnavutkoy/ · /en/dentist/arnavutkoy/ · /ru/stomatolog/arnavutkoy/ · /uk/stomatolog/arnavutkoy/ · /bg/zabolekar/arnavutkoy/ · /de/zahnarzt/arnavutkoy/
- **Adalar:** /disci/adalar/ · /haftasonu/adalar/ · /en-iyi-disci/adalar/ · /uzman-dis-hekimi/adalar/ · /prof-dis-hekimi/adalar/ · /estetik-dis-klinigi/adalar/ · /en/dentist/adalar/ · /ru/stomatolog/adalar/ · /uk/stomatolog/adalar/ · /bg/zabolekar/adalar/ · /de/zahnarzt/adalar/
- **Kartal:** /disci/kartal/ · /haftasonu/kartal/ · /en-iyi-disci/kartal/ · /uzman-dis-hekimi/kartal/ · /prof-dis-hekimi/kartal/ · /estetik-dis-klinigi/kartal/ · /en/dentist/kartal/ · /ru/stomatolog/kartal/ · /uk/stomatolog/kartal/ · /bg/zabolekar/kartal/ · /de/zahnarzt/kartal/
- **Esenyurt:** /disci/esenyurt/ · /haftasonu/esenyurt/ · /en-iyi-disci/esenyurt/ · /uzman-dis-hekimi/esenyurt/ · /prof-dis-hekimi/esenyurt/ · /estetik-dis-klinigi/esenyurt/ · /en/dentist/esenyurt/ · /ru/stomatolog/esenyurt/ · /uk/stomatolog/esenyurt/ · /bg/zabolekar/esenyurt/ · /de/zahnarzt/esenyurt/
- **Pendik:** /disci/pendik/ · /haftasonu/pendik/ · /en-iyi-disci/pendik/ · /uzman-dis-hekimi/pendik/ · /prof-dis-hekimi/pendik/ · /estetik-dis-klinigi/pendik/ · /en/dentist/pendik/ · /ru/stomatolog/pendik/ · /uk/stomatolog/pendik/ · /bg/zabolekar/pendik/ · /de/zahnarzt/pendik/
- **Beylikdüzü:** /disci/beylikduzu/ · /haftasonu/beylikduzu/ · /en-iyi-disci/beylikduzu/ · /uzman-dis-hekimi/beylikduzu/ · /prof-dis-hekimi/beylikduzu/ · /estetik-dis-klinigi/beylikduzu/ · /en/dentist/beylikduzu/ · /ru/stomatolog/beylikduzu/ · /uk/stomatolog/beylikduzu/ · /bg/zabolekar/beylikduzu/ · /de/zahnarzt/beylikduzu/
- **Büyükçekmece:** /disci/buyukcekmece/ · /haftasonu/buyukcekmece/ · /en-iyi-disci/buyukcekmece/ · /uzman-dis-hekimi/buyukcekmece/ · /prof-dis-hekimi/buyukcekmece/ · /estetik-dis-klinigi/buyukcekmece/ · /en/dentist/buyukcekmece/ · /ru/stomatolog/buyukcekmece/ · /uk/stomatolog/buyukcekmece/ · /bg/zabolekar/buyukcekmece/ · /de/zahnarzt/buyukcekmece/
- **Tuzla:** /disci/tuzla/ · /haftasonu/tuzla/ · /en-iyi-disci/tuzla/ · /uzman-dis-hekimi/tuzla/ · /prof-dis-hekimi/tuzla/ · /estetik-dis-klinigi/tuzla/ · /en/dentist/tuzla/ · /ru/stomatolog/tuzla/ · /uk/stomatolog/tuzla/ · /bg/zabolekar/tuzla/ · /de/zahnarzt/tuzla/
- **Çatalca:** /disci/catalca/ · /haftasonu/catalca/ · /en-iyi-disci/catalca/ · /uzman-dis-hekimi/catalca/ · /prof-dis-hekimi/catalca/ · /estetik-dis-klinigi/catalca/ · /en/dentist/catalca/ · /ru/stomatolog/catalca/ · /uk/stomatolog/catalca/ · /bg/zabolekar/catalca/ · /de/zahnarzt/catalca/
- **Şile:** /disci/sile/ · /haftasonu/sile/ · /en-iyi-disci/sile/ · /uzman-dis-hekimi/sile/ · /prof-dis-hekimi/sile/ · /estetik-dis-klinigi/sile/ · /en/dentist/sile/ · /ru/stomatolog/sile/ · /uk/stomatolog/sile/ · /bg/zabolekar/sile/ · /de/zahnarzt/sile/
- **Silivri:** /disci/silivri/ · /haftasonu/silivri/ · /en-iyi-disci/silivri/ · /uzman-dis-hekimi/silivri/ · /prof-dis-hekimi/silivri/ · /estetik-dis-klinigi/silivri/ · /en/dentist/silivri/ · /ru/stomatolog/silivri/ · /uk/stomatolog/silivri/ · /bg/zabolekar/silivri/ · /de/zahnarzt/silivri/

Tam liste (2.233 satır): `docs/ilce-budama-2026-11-22-ekA-drdevrim-silinen-2233.txt` ve drdevrim deposunda `docs/kaldirilan-sayfalar-2026-11-22.txt`.
Veri silinmedi: `app/data/istanbul-data-kaldirilan.ts`. 410 kuralı: `server/middleware/kaldirilan-ilceler.ts` (X-Robots-Tag: noindex, gövdede /disci/sisli/ linki).

## 3. drdevrim.com — eklenen sayfalar (2.145 adres, 11 yeni dil)

Kalan 17 ilçe + 178 mahalle = 195 konum × 11 dil. Tek dinamik şablon çifti üretir: `app/pages/[lang]/[segment]/[ilce]/index.vue` ve `.../[mahalle]/index.vue`; metinler `app/data/pseo-i18n.ts`, dil→segment eşlemesi `app/data/pseo-segments.ts`.

| Dil | Segment | İlçe sayfası | Mahalle sayfası | Toplam | Örnek |
|---|---|---|---|---|---|
| Hollandaca | `/nl/tandarts/` | 17 | 178 | 195 | /nl/tandarts/sisli/ · /nl/tandarts/sisli/nisantasi/ |
| Fransızca | `/fr/dentiste/` | 17 | 178 | 195 | /fr/dentiste/sisli/ · /fr/dentiste/sisli/nisantasi/ |
| İtalyanca | `/it/dentista/` | 17 | 178 | 195 | /it/dentista/sisli/ · /it/dentista/sisli/nisantasi/ |
| İspanyolca | `/es/dentista/` | 17 | 178 | 195 | /es/dentista/sisli/ · /es/dentista/sisli/nisantasi/ |
| Lehçe | `/pl/dentysta/` | 17 | 178 | 195 | /pl/dentysta/sisli/ · /pl/dentysta/sisli/nisantasi/ |
| Arapça | `/ar/tabib-asnan/` | 17 | 178 | 195 | /ar/tabib-asnan/sisli/ · /ar/tabib-asnan/sisli/nisantasi/ |
| İsveççe | `/sv/tandlakare/` | 17 | 178 | 195 | /sv/tandlakare/sisli/ · /sv/tandlakare/sisli/nisantasi/ |
| Danca | `/da/tandlaege/` | 17 | 178 | 195 | /da/tandlaege/sisli/ · /da/tandlaege/sisli/nisantasi/ |
| Norveççe | `/no/tannlege/` | 17 | 178 | 195 | /no/tannlege/sisli/ · /no/tannlege/sisli/nisantasi/ |
| Romence | `/ro/dentist/` | 17 | 178 | 195 | /ro/dentist/sisli/ · /ro/dentist/sisli/nisantasi/ |
| Azerbaycanca | `/az/dis-hekimi/` | 17 | 178 | 195 | /az/dis-hekimi/sisli/ · /az/dis-hekimi/sisli/nisantasi/ |

Kalan 17 ilçe (kliniğe yakından uzağa; "diğer ilçeler" listeleri bu sırayla, Şişli ilk):

| # | İlçe | Mahalle | Sayfa / dil | Mahalleler |
|---|---|---|---|---|
| 1 | Şişli (`sisli`) | 16 | 17 | bozkurt, cumhuriyet, caglayan, elmadagi, ergenekon, ferikoy, fulya, halaskargazi, harbiye, kustepe, mecidiyekoy, mesrutiyet, nisantasi, osmanbey, pinartepe, tesvikiye |
| 2 | Kağıthane (`kagithane`) | 11 | 12 | caglayan, gultepe, hamidiye, hurriyet, islambey, mehmet-akif, merkez, nurtepe, seyrantepe, talatpasa, yahya-kemal |
| 3 | Beyoğlu (`beyoglu`) | 12 | 13 | asmalimescit, bulbul, cihangir, haciahmet, halicioglu, huseyinaga, ornektepe, sururi, tarlabasi, tomtom, tophane, yahyakemal |
| 4 | Beşiktaş (`besiktas`) | 16 | 17 | abbasaga, akatlar, arnavutkoy, balmumcu, bebek, etiler, gayrettepe, kurucesme, levent, levazim, nisbetiye, ortakoy, sinanpasa, turkali, ulus, yildiz |
| 5 | Eyüpsultan (`eyupsultan`) | 9 | 10 | alibeykoy, dugmeciler, eyup-merkez, gokturk, ihsaniye, kemerburgaz, niscanci, rami-cuma, rami-yeni |
| 6 | Üsküdar (`uskudar`) | 15 | 16 | acibadem, ahmediye, altunizade, aziz-mahmut-hudayi, baglarbasi, bulgurlu, burhaniye, cengelkoy, ferah, kandilli, kisikli, kucuk-camlica, sultantepe, unalan, validebag |
| 7 | Gaziosmanpaşa (`gaziosmanpasa`) | 7 | 8 | baglarbasi, fevzi-cakmak, gazi, gaziosmanpasa-merkez, karadeniz, karlitepe, mevlana |
| 8 | Bayrampaşa (`bayrampasa`) | 8 | 9 | altintepsi, cevatpasa, kartaltepe, kocatepe, muratpasa, orta-mahalle, vatan, yildirim |
| 9 | Fatih (`fatih`) | 14 | 15 | aksaray, atikali, beyazit, carsamba, davutpasa, haseki, karagumruk, kumkapi, mevlanakapi, samatya, suleymaniye, sultanahmet, yedikule, zeyrek |
| 10 | Esenler (`esenler`) | 8 | 9 | birlik, cifte-havuzlar, fatih, havaalani, menderes, nene-hatun, oruc-reis, turgut-reis |
| 11 | Kadıköy (`kadikoy`) | 12 | 13 | acibadem, bostanci, caferaga, erenkoy, fenerbahce, fikirtepe, goztepe, kosuyolu, moda, osmanaga, suadiye, zuhtupasa |
| 12 | Güngören (`gungoren`) | 6 | 7 | gungoren-merkez, gursel, haznedar, mehmet-akif, merkez, ressam |
| 13 | Zeytinburnu (`zeytinburnu`) | 10 | 11 | gokalp, gundogdu, kazlicesme, merkezefendi, nuripasa, seyitnizam, sumer, telsiz, veliefendi, yenidogan |
| 14 | Bağcılar (`bagcilar`) | 10 | 11 | baglar, demirkapi, evren, gunesli, hurriyet, kemalpasa, kirazli, merkez, yenimahalle, yildiztepe |
| 15 | Bahçelievler (`bahcelievler`) | 7 | 8 | bahcelievler-merkez, cumhuriyet, cobancesme, kocasinan, soganli, sirinevler, yenibosna |
| 16 | Sarıyer (`sariyer`) | 10 | 11 | bahcekoy, baltalimanı, buyukdere, derbent, emirgan, kirecburnu, maslak, sariyer-merkez, tarabya, yenikoy |
| 17 | Bakırköy (`bakirkoy`) | 7 | 8 | atakoy, bakirkoy-merkez, florya, kartaltepe, sakizagaci, yenimahalle, zeytinlik |

Her yeni sayfada: başlık ve meta (dil + ilçe/mahalle), kliniğe kuş uçuşu mesafe, 35+ yıl / aile kliniği / Şişli adresi, çalışma saati 05:00–00:00 ve 7 gün (bayram dahil), WhatsApp ile ücretsiz ön değerlendirme, tedavi listesi, o dilde SSS, Dentist + FAQPage şeması, 17 dil + x-default hreflang, kardeş mahalle ve diğer ilçe linkleri. Fiyat, garanti, otel/transfer, sedasyon, mikroskop yok. Arapça sayfalarda ilçe adları Arapça, sağdan sola düzen.
Hub adresleri (ör. `/fr/dentiste`) 301 ile `/lang/fr/` sayfasına gider; sv/da/no hub'ları `/lang/en/`'e (bu dillerde ana sayfa yok).
Tam liste (2.145 satır): `docs/ilce-budama-2026-11-22-ekB-drdevrim-eklenen-2145.txt`.

## 4. drdevrim.com — düzeltilen sayfalar (saat ve gece/acil ifadeleri; commit 3c971d3, 51 dosya)

Kural: klinik gece çalışmaz; yayınlanan saat **05:00–00:00, haftanın 7 günü, bayramlarda açık**. Yapılanlar:

- Tüm "07:00–23:00" / "07–23" ifadeleri → "05:00–00:00" / "05–00" (şema `opens`/`closes` dahil).
- "7/24 telefon hattı", "24/7", "7-24", "nöbetçi dişçi", "gece açık", "acil dişçi" cümleleri çıkarıldı; yerine "Telefon ve WhatsApp: 05:00–00:00 … ekibimiz aynı gün muayene için yönlendirme yapar".
- EN "Emergency Dentist in {ilçe}" kartları → "Same-Day Appointments"; DE "Notfallzahnarzt" → "Termine am selben Tag"; RU/UK/BG "24/7" → "приём в тот же день" / "прийом того ж дня" / "преглед в същия ден".
- Ana sayfa 18 dil (`home-i18n/*.ts`): `cta247Badge` → "7 gün" karşılıkları, `line247` → "… 05:00–00:00", `hoursTime` → 05:00–00:00 (TheContact şeması buradan okur).
- Açılış sayfaları (`landing-i18n.ts`, 17 dil) ve hizmet verisi (`services-data.ts`): acil/7-24 hizmet maddeleri çıktı, saat düzeltildi. /hizmetler/acil-dis/ sayfası duruyor, saati düzeltildi (hekim kararı bekliyor).

Örnek değişiklikler (silinen → eklenen):

- `app/pages/disci/[ilce]/index.vue`: `Sabah 07:00'den gece 23:00'e kadar açık kliniğimize telefonla <strong>7/24 ulaşabilirsiniz</strong> —` → `Sabah 05:00'ten 00:00'a kadar açık kliniğimize telefon ve WhatsApp ile <strong>05:00–00:00 arası ulaşabilirsiniz</strong> —`
- `app/pages/disci/[ilce]/index.vue`: `İstanbul · {{ ilce?.name }} · Her Gün 07:00–23:00 Açık` → `İstanbul · {{ ilce?.name }} · Her Gün 05:00–00:00 Açık`
- `app/pages/en/dentist/[ilce]/index.vue`: `<strong>aesthetic dentistry</strong>, emergency treatment or a routine check-up —` → `<strong>aesthetic dentistry</strong>, a same-day appointment or a routine check-up —`
- `app/pages/de/zahnarzt/[ilce]/index.vue`: `<em>Zahnklinik · Notfallzahnarzt · 35 Jahre Erfahrung.</em>` → `<em>Zahnklinik · Termine am selben Tag · 35 Jahre Erfahrung.</em>`
- `app/pages/ru/stomatolog/[ilce]/index.vue`: `могут связаться с нами 24/7 по телефону или WhatsApp.` → `могут связаться с нами по телефону или WhatsApp с 05:00 до 00:00.`
- `app/data/home-i18n/tr.ts`: `cta247Badge: '7/24',` → `cta247Badge: '7 gün',`

Dosya başına değişiklik (silinen/eklenen satır, dokunulan ifade grupları). Her şablon dosyası o ailenin tüm canlı sayfalarını değiştirir:

| Dosya | Etkilenen canlı sayfalar | Satır (−/+) | İfade grupları |
|---|---|---|---|
| `app/components/HeroSection.vue` | ana sayfa hero | 1/1 | 7/24 · 24/7 |
| `app/components/TheContact.vue` | iletişim bloğu + şema (tüm sayfalar) | 1/1 | saat 07:00/23:00→05:00/00:00 |
| `app/data/home-i18n/ar.ts` | ana sayfa metinleri (o dil) | 7/7 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7 |
| `app/data/home-i18n/az.ts` | ana sayfa metinleri (o dil) | 8/8 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7 |
| `app/data/home-i18n/bg.ts` | ana sayfa metinleri (o dil) | 6/6 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7 |
| `app/data/home-i18n/de.ts` | ana sayfa metinleri (o dil) | 7/7 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7, acil / emergency / Notfall |
| `app/data/home-i18n/el.ts` | ana sayfa metinleri (o dil) | 8/8 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7 |
| `app/data/home-i18n/en.ts` | ana sayfa metinleri (o dil) | 7/7 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7, acil / emergency / Notfall |
| `app/data/home-i18n/es.ts` | ana sayfa metinleri (o dil) | 8/8 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7 |
| `app/data/home-i18n/fa.ts` | ana sayfa metinleri (o dil) | 8/8 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7 |
| `app/data/home-i18n/fr.ts` | ana sayfa metinleri (o dil) | 6/6 | saat 07:00/23:00→05:00/00:00, acil / emergency / Notfall |
| `app/data/home-i18n/he.ts` | ana sayfa metinleri (o dil) | 8/8 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7 |
| `app/data/home-i18n/it.ts` | ana sayfa metinleri (o dil) | 6/6 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7 |
| `app/data/home-i18n/nl.ts` | ana sayfa metinleri (o dil) | 6/6 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7 |
| `app/data/home-i18n/pl.ts` | ana sayfa metinleri (o dil) | 7/7 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7 |
| `app/data/home-i18n/ro.ts` | ana sayfa metinleri (o dil) | 8/8 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7 |
| `app/data/home-i18n/ru.ts` | ana sayfa metinleri (o dil) | 8/8 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7, acil / emergency / Notfall |
| `app/data/home-i18n/sq.ts` | ana sayfa metinleri (o dil) | 6/6 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7 |
| `app/data/home-i18n/tr.ts` | ana sayfa metinleri (o dil) | 6/6 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7 |
| `app/data/home-i18n/uk.ts` | ana sayfa metinleri (o dil) | 8/8 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7, acil / emergency / Notfall |
| `app/data/landing-i18n.ts` | 17 dil açılış sayfası | 49/49 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7, acil / emergency / Notfall |
| `app/data/services-data.ts` | hizmet kartları ve sayfaları | 7/7 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7, acil / emergency / Notfall |
| `app/pages/bg/zabolekar/[ilce]/[mahalle]/index.vue` | /bg/zabolekar/ ailesi — 178 mahalle sayfası | 12/12 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7, acil / emergency / Notfall |
| `app/pages/bg/zabolekar/[ilce]/index.vue` | /bg/zabolekar/ ailesi — 17 ilçe sayfası | 15/15 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7, acil / emergency / Notfall |
| `app/pages/de/zahnarzt/[ilce]/[mahalle]/index.vue` | /de/zahnarzt/ ailesi — 178 mahalle sayfası | 16/16 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7, acil / emergency / Notfall |
| `app/pages/de/zahnarzt/[ilce]/index.vue` | /de/zahnarzt/ ailesi — 17 ilçe sayfası | 23/23 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7, acil / emergency / Notfall |
| `app/pages/disci/[ilce]/[mahalle]/index.vue` | /disci/ ailesi — 178 mahalle sayfası | 25/24 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7, nöbetçi, gece, acil / emergency / Notfall |
| `app/pages/disci/[ilce]/index.vue` | /disci/ ailesi — 17 ilçe sayfası | 25/25 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7, nöbetçi, gece, acil / emergency / Notfall |
| `app/pages/doktorlar/index.vue` | /doktorlar/ | 1/1 | saat 07:00/23:00→05:00/00:00 |
| `app/pages/en-iyi-disci/[ilce]/[mahalle]/index.vue` | /en-iyi-disci/ ailesi — 178 mahalle sayfası | 3/3 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7 |
| `app/pages/en-iyi-disci/[ilce]/index.vue` | /en-iyi-disci/ ailesi — 17 ilçe sayfası | 6/6 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7 |
| `app/pages/en/dentist/[ilce]/[mahalle]/index.vue` | /en/dentist/ ailesi — 178 mahalle sayfası | 15/13 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7, acil / emergency / Notfall |
| `app/pages/en/dentist/[ilce]/index.vue` | /en/dentist/ ailesi — 17 ilçe sayfası | 17/14 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7, acil / emergency / Notfall |
| `app/pages/estetik-dis-klinigi/[ilce]/[mahalle]/index.vue` | /estetik-dis-klinigi/ ailesi — 178 mahalle sayfası | 2/2 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7 |
| `app/pages/estetik-dis-klinigi/[ilce]/index.vue` | /estetik-dis-klinigi/ ailesi — 17 ilçe sayfası | 2/2 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7 |
| `app/pages/haftasonu/[ilce]/[mahalle]/index.vue` | /haftasonu/ ailesi — 178 mahalle sayfası | 42/42 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7, gece |
| `app/pages/haftasonu/[ilce]/index.vue` | /haftasonu/ ailesi — 17 ilçe sayfası | 42/42 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7, gece |
| `app/pages/hizmetler/[slug].vue` | 31 hizmet sayfası | 1/1 | saat 07:00/23:00→05:00/00:00 |
| `app/pages/hizmetler/index.vue` | /hizmetler/ | 1/1 | saat 07:00/23:00→05:00/00:00 |
| `app/pages/iletisim/index.vue` | /iletisim/ | 7/7 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7, acil / emergency / Notfall |
| `app/pages/index.vue` | ana sayfa / | 2/2 | saat 07:00/23:00→05:00/00:00 |
| `app/pages/lang/[code].vue` | 17 dil ana sayfası /lang/xx/ | 2/2 | saat 07:00/23:00→05:00/00:00 |
| `app/pages/prof-dis-hekimi/[ilce]/[mahalle]/index.vue` | /prof-dis-hekimi/ ailesi — 178 mahalle sayfası | 2/2 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7 |
| `app/pages/prof-dis-hekimi/[ilce]/index.vue` | /prof-dis-hekimi/ ailesi — 17 ilçe sayfası | 2/2 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7 |
| `app/pages/ru/stomatolog/[ilce]/[mahalle]/index.vue` | /ru/stomatolog/ ailesi — 178 mahalle sayfası | 12/12 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7, acil / emergency / Notfall |
| `app/pages/ru/stomatolog/[ilce]/index.vue` | /ru/stomatolog/ ailesi — 17 ilçe sayfası | 16/16 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7, acil / emergency / Notfall |
| `app/pages/uk/stomatolog/[ilce]/[mahalle]/index.vue` | /uk/stomatolog/ ailesi — 178 mahalle sayfası | 12/12 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7, acil / emergency / Notfall |
| `app/pages/uk/stomatolog/[ilce]/index.vue` | /uk/stomatolog/ ailesi — 17 ilçe sayfası | 16/16 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7, acil / emergency / Notfall |
| `app/pages/uzman-dis-hekimi/[ilce]/[mahalle]/index.vue` | /uzman-dis-hekimi/ ailesi — 178 mahalle sayfası | 2/2 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7 |
| `app/pages/uzman-dis-hekimi/[ilce]/index.vue` | /uzman-dis-hekimi/ ailesi — 17 ilçe sayfası | 2/2 | saat 07:00/23:00→05:00/00:00, 7/24 · 24/7 |
| `nuxt.config.ts` | site geneli şema/meta | 2/2 | saat 07:00/23:00→05:00/00:00 |

Canlı doğrulama (22.11 22:40, 14 sayfa: TR ilçe/mahalle, haftasonu, EN, DE, RU, UK, BG, FR, NL, AR, IT, iletişim, acil-dis): "7/24", "24/7", "nöbetçi", "07:00", "23:00", "Notfallzahnarzt", "Emergency Dentist", "круглосуточно", "gece açık", "acil dişçi" **hiçbirinde yok**; şema opens 05:00 / closes 00:00.

Bilerek dokunulmayanlar (hekim kararı gerekir): Nobel/Straumann marka cümleleri; Invisalign/ortodonti hizmet sayfaları (soru 25); "10 yıl garanti", "doğal ton garantisi", "Etik tedavi garantisi" ifadeleri (TheNav); "124 yorum" sayıları; /hizmetler/acil-dis/ sayfasının kendisi; eski 11 ailenin hreflang listesinde yeni 11 dil yok.

## 5. devrimbirikensipahi.com.tr — yayından kalkan sayfalar

13 blog yazısı yayından kaldı (veritabanında duruyor, `blog/removed.py` listesi); eski adres 301 ile kalıcı sayfaya gider. Canlıda 13/13 doğrulandı (22.11 22:40).

| # | Yazı | 301 hedefi | Gerekçe |
|---|---|---|---|
| 1 | /blog/en-iyi-disci/pendik-acik-disci/ | /sisli-dis-klinigi/ | uzak ilçe |
| 2 | /blog/en-iyi-disci/kartal-acik-disci/ | /sisli-dis-klinigi/ | uzak ilçe |
| 3 | /blog/en-iyi-disci/maltepe-acik-disci/ | /sisli-dis-klinigi/ | uzak ilçe |
| 4 | /blog/en-iyi-disci/buyukcekmece-acik-disci/ | /sisli-dis-klinigi/ | uzak ilçe |
| 5 | /blog/en-iyi-disci/avcilar-acik-disci/ | /sisli-dis-klinigi/ | uzak ilçe |
| 6 | /blog/en-iyi-disci/atasehir-acik-disci/ | /sisli-dis-klinigi/ | uzak ilçe |
| 7 | /blog/en-iyi-disci/basaksehir-acik-disci/ | /sisli-dis-klinigi/ | uzak ilçe |
| 8 | /blog/en-iyi-disci/kucukcekmece-acik-disci/ | /sisli-dis-klinigi/ | uzak ilçe |
| 9 | /blog/en-iyi-disci/umraniye-acik-disci/ | /sisli-dis-klinigi/ | uzak ilçe |
| 10 | /blog/en-iyi-disci/beykoz-acik-disci/ | /sisli-dis-klinigi/ | uzak ilçe |
| 11 | /blog/en-iyi-disci/anadolu-yakasi-acik-disci/ | /sisli-dis-klinigi/ | uzak bölge |
| 12 | /blog/en-iyi-disci/acil-disci-istanbul/ | /acil-dis-hekimi/ | baştan sona gece/nöbetçi/7-24 niyeti |
| 13 | /blog/en-iyi-disci/ramazanda-acik-disci/ | /sisli-dis-klinigi/ | "gece açık diş hekimi", sahur–iftar gece anlatımı |

Sitemap'ten çıkan 12 hesap sayfası (sayfalar çalışıyor, yalnızca listelenmiyor): /accounts/kvkk/, /accounts/giris/, /accounts/login/, /accounts/cikis/, /accounts/logout/, /accounts/benim-sorularim/, /accounts/my-questions/, /accounts/sifre-sifirla/, /accounts/password-reset/, /accounts/privacy/, /accounts/kayit/, /accounts/register/.
Ana sayfa (`clinic/templates/clinic/index.html`): Beylikdüzü, Ataşehir, Maltepe, Kartal, Pendik etiketleri silindi (canlıda doğrulandı).
Dokunulmayan: ana sayfadaki "İstanbul'un her ilçesinden… Kadıköy'den Bakırköy'e" paragrafı (16 dilde .po; hekim kararı).

## 6. devrimbirikensipahi.com.tr — içeriği temizlenen 44 blog yazısı

Durum: **uygulandı — Render açılış kancası göç 0003'ü dağıtımda çalıştırdı; canlıda 44/44 yazı doğrulandı (22.11.2026 23:05)**. Mekanizma: `blog/management/commands/icerik_duzelt.py` (prova / --apply / --geri-al), metinler `blog/fixtures/icerik_duzelt_2026-11-22/before|after/<slug>.json`;
göç `blog/migrations/0003_icerik_duzelt_2026_11_22.py` komutu dağıtımda **bir kez** çalıştırır, Render açılış kancası `blog/boot.py` bunu garanti eder (yerelde çalışmaz).
Kalan: "açık dişçi" / "pazar açık dişçi" niyeti, saat 05:00–00:00, hafta sonu ve bayram açık ifadeleri. Çıkan: acil / nöbetçi / 7-24 / gece cümleleri ve blokları, sondaki anahtar kelime yığınları, kaldırılan 13 yazıya giden linkler, şemadaki 24 saat/acil alanları.
Toplam: 250 blok, 309 cümle, 39 anahtar kelime öğesi, 242 link, 147 JSON-LD düzenlemesi.
Canlı tarama (22.11 23:05, 44 yazının tamamı çekildi): 44/44 → 200; "7/24", "24/7", "7-24", "nöbetçi", "gece açık", "ŞU AN AÇIĞIZ", "24 saat", "emergency dentist" ifadeleri ve 13 kaldırılan yazıya link 42 yazıda yok. 2 zararsız kalıntı: `pazar-acik-disci` içinde görünmez bir bölüm kimliği `id="nobetci-disci"` (metin "Pazar Günü Planlanmış Tedaviler"), `sisli-dis-hekimi` içinde "24 saat içinde geri dönüş" (yanıt süresi, açık olma iddiası değil).

| # | Yazı | Dil | Başlık | Meta başlık | Meta açıklama | Blok | Cümle | Anahtar | Link | JSON-LD | Karakter önce→sonra |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | /blog/en-iyi-disci/avrupa-yakasi-acik-disci/ | tr | degisti | degisti | ayni | 6 | 9 | 1 | 11 | 4 | 32765→28420 |
| 2 | /blog/en-iyi-disci/bahcelievler-acik-disci/ | tr | degisti | degisti | ayni | 7 | 9 | 1 | 11 | 4 | 32526→27805 |
| 3 | /blog/en-iyi-disci/bakirkoy-acik-disci/ | tr | degisti | degisti | ayni | 7 | 9 | 1 | 11 | 4 | 32362→27666 |
| 4 | /blog/en-iyi-disci/bayramda-acik-disci/ | tr | degisti | ayni | ayni | 9 | 15 | 1 | 0 | 7 | 37013→32784 |
| 5 | /blog/en-iyi-disci/bayrampasa-acik-disci/ | tr | degisti | degisti | ayni | 7 | 9 | 1 | 11 | 4 | 32442→27734 |
| 6 | /blog/en-iyi-disci/besiktas-acik-disci/ | tr | degisti | degisti | ayni | 7 | 9 | 1 | 11 | 4 | 32360→27665 |
| 7 | /blog/en-iyi-disci/besiktas-disci/ | tr | degisti | degisti | ayni | 3 | 2 | 0 | 0 | 1 | 24986→24214 |
| 8 | /blog/en-iyi-disci/beyoglu-acik-disci/ | tr | degisti | degisti | ayni | 7 | 9 | 1 | 11 | 4 | 32309→27623 |
| 9 | /blog/en-iyi-disci/beyoglu-disci/ | tr | degisti | degisti | ayni | 3 | 2 | 0 | 0 | 1 | 25103→24166 |
| 10 | /blog/en-iyi-disci/cihangir-disci/ | tr | degisti | degisti | ayni | 3 | 2 | 0 | 0 | 1 | 25288→24346 |
| 11 | /blog/en-iyi-disci/cumartesi-acik-disci-pazar-acik-disci/ | tr | degisti | degisti | degisti | 10 | 22 | 3 | 0 | 6 | 23079→18250 |
| 12 | /blog/english/dental-tourism-turkey-istanbul/ | en | ayni | ayni | ayni | 3 | 4 | 0 | 0 | 4 | 63534→61990 |
| 13 | /blog/english/dentist-istanbul/ | en | ayni | ayni | ayni | 10 | 4 | 1 | 0 | 4 | 55822→52836 |
| 14 | /blog/en-iyi-disci/devrim-biriken-sipahi/ | tr | degisti | ayni | ayni | 3 | 4 | 0 | 0 | 1 | 24083→22652 |
| 15 | /blog/en-iyi-disci/eminonu-acik-disci/ | tr | degisti | degisti | ayni | 7 | 9 | 1 | 11 | 4 | 32321→27633 |
| 16 | /blog/en-iyi-disci/esenler-acik-disci/ | tr | degisti | degisti | ayni | 7 | 9 | 1 | 11 | 4 | 32314→27623 |
| 17 | /blog/en-iyi-disci/etiler-acik-disci/ | tr | degisti | degisti | ayni | 7 | 9 | 1 | 11 | 4 | 32274→27589 |
| 18 | /blog/en-iyi-disci/eyup-acik-disci/ | tr | degisti | degisti | ayni | 7 | 9 | 1 | 11 | 4 | 32200→27526 |
| 19 | /blog/en-iyi-disci/fatih-acik-disci/ | tr | degisti | degisti | ayni | 7 | 9 | 1 | 11 | 4 | 32228→27550 |
| 20 | /blog/en-iyi-disci/gaziosmanpasa-acik-disci/ | tr | degisti | degisti | ayni | 7 | 9 | 1 | 11 | 4 | 32566→27843 |
| 21 | /blog/en-iyi-disci/gungoren-acik-disci/ | tr | degisti | degisti | ayni | 7 | 9 | 1 | 11 | 4 | 32369→27668 |
| 22 | /blog/en-iyi-disci/istanbul-acik-disci/ | tr | degisti | degisti | ayni | 7 | 8 | 5 | 11 | 4 | 32067→25999 |
| 23 | /blog/en-iyi-disci/kadikoy-acik-disci/ | tr | degisti | degisti | ayni | 7 | 9 | 1 | 11 | 4 | 32326→27636 |
| 24 | /blog/en-iyi-disci/kagithane-acik-disci/ | tr | degisti | degisti | ayni | 6 | 9 | 1 | 11 | 4 | 32572→28264 |
| 25 | /blog/en-iyi-disci/levent-disci/ | tr | degisti | degisti | ayni | 3 | 2 | 0 | 0 | 0 | 24403→23486 |
| 26 | /blog/en-iyi-disci/nisantasi-acik-disci/ | tr | degisti | degisti | ayni | 7 | 9 | 1 | 11 | 4 | 32861→28210 |
| 27 | /blog/english/nisantasi-dentist/ | en | ayni | ayni | ayni | 3 | 0 | 0 | 0 | 3 | 54074→52967 |
| 28 | /blog/en-iyi-disci/nisantasi-disci-osmanbey-disci/ | tr | degisti | degisti | degisti | 5 | 5 | 2 | 0 | 6 | 32782→28581 |
| 29 | /blog/en-iyi-disci/ortakoy-disci/ | tr | degisti | ayni | ayni | 3 | 1 | 0 | 0 | 0 | 24380→23667 |
| 30 | /blog/en-iyi-disci/pazar-acik-disci-kagithane/ | tr | degisti | degisti | degisti | 5 | 5 | 0 | 0 | 1 | 26384→24600 |
| 31 | /blog/en-iyi-disci/pazar-acik-disci-nisantasi/ | tr | degisti | degisti | degisti | 5 | 4 | 0 | 0 | 3 | 28228→26055 |
| 32 | /blog/en-iyi-disci/pazar-acik-disci-osmanbey/ | tr | degisti | degisti | degisti | 6 | 4 | 0 | 0 | 3 | 28366→25815 |
| 33 | /blog/en-iyi-disci/pazar-acik-disci-sisli/ | tr | degisti | degisti | degisti | 6 | 5 | 0 | 0 | 4 | 25986→23482 |
| 34 | /blog/en-iyi-disci/pazar-acik-disci/ | tr | degisti | degisti | degisti | 7 | 18 | 4 | 0 | 6 | 26949→23001 |
| 35 | /blog/en-iyi-disci/sariyer-acik-disci/ | tr | degisti | degisti | ayni | 6 | 9 | 1 | 11 | 4 | 32483→28169 |
| 36 | /blog/en-iyi-disci/sirinevler-acik-disci/ | tr | degisti | degisti | ayni | 6 | 9 | 1 | 11 | 4 | 32612→28265 |
| 37 | /blog/en-iyi-disci/sisli-acik-disci/ | tr | degisti | degisti | ayni | 6 | 9 | 1 | 11 | 4 | 32444→28143 |
| 38 | /blog/en-iyi-disci/sisli-dis-hekimi/ | tr | degisti | ayni | ayni | 0 | 0 | 0 | 0 | 0 | 34285→34181 |
| 39 | /blog/en-iyi-disci/sisli-disci-mecidiyekoy-disci/ | tr | degisti | degisti | degisti | 5 | 5 | 2 | 0 | 6 | 32702→28353 |
| 40 | /blog/en-iyi-disci/sisli-disci/ | tr | degisti | degisti | ayni | 3 | 2 | 0 | 0 | 0 | 24440→23508 |
| 41 | /blog/en-iyi-disci/sisli-en-iyi-disci/ | tr | ayni | ayni | ayni | 5 | 4 | 0 | 0 | 2 | 60741→59401 |
| 42 | /blog/en-iyi-disci/taksim-disci/ | tr | degisti | degisti | ayni | 3 | 2 | 0 | 0 | 0 | 22956→22153 |
| 43 | /blog/en-iyi-disci/uskudar-acik-disci/ | tr | degisti | degisti | ayni | 6 | 9 | 1 | 11 | 4 | 32284→28006 |
| 44 | /blog/en-iyi-disci/zeytinburnu-acik-disci/ | tr | degisti | degisti | ayni | 6 | 9 | 1 | 11 | 4 | 32481→28174 |

Başlık değişiklikleri (önce → sonra):

- `avrupa-yakasi-acik-disci`: "AVRUPA YAKASI AÇIK DİŞÇİ · "Avrupa Yakası Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, 7/24 Hizmet"" → "Avrupa Yakası Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, Hafta Sonu Açık"
- `bahcelievler-acik-disci`: "BAHÇELİEVLER AÇIK DİŞÇİ · "Bahçelievler Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, 7/24 Hizmet"" → "Bahçelievler Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, Hafta Sonu Açık"
- `bakirkoy-acik-disci`: "BAKIRKÖY AÇIK DİŞÇİ · "Bakırköy Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, 7/24 Hizmet"" → "Bakırköy Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, Hafta Sonu Açık"
- `bayramda-acik-disci`: "BAYRAMDA AÇIK DİŞÇİ 35+ Yıl Tecrübe · "Bayramda Açık Dişçi İstanbul — Dr. Devrim Biriken Sipahi | Tüm Bayramlarda Açık Diş Hekimi"" → "Bayramda Açık Dişçi İstanbul — Dr. Devrim Biriken Sipahi | Tüm Bayramlarda Açık Diş Hekimi"
- `bayrampasa-acik-disci`: "BAYRAMPAŞA AÇIK DİŞÇİ · "Bayrampaşa Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, 7/24 Hizmet"" → "Bayrampaşa Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, Hafta Sonu Açık"
- `besiktas-acik-disci`: "BEŞİKTAŞ AÇIK DİŞÇİ · "Beşiktaş Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, 7/24 Hizmet"" → "Beşiktaş Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, Hafta Sonu Açık"
- `besiktas-disci`: "BEŞİKTAŞ DİŞÇİ · "Beşiktaş Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, Şişli'ye 10 Dakika"" → "Beşiktaş Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, Şişli'ye 10 Dakika"
- `beyoglu-acik-disci`: "BEYOĞLU AÇIK DİŞÇİ · "Beyoğlu Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, 7/24 Hizmet"" → "Beyoğlu Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, Hafta Sonu Açık"
- `beyoglu-disci`: "BEYOĞLU DİŞÇİ · "Beyoğlu Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, Şişli'ye 10 Dakika"" → "Beyoğlu Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, Şişli'ye 10 Dakika"
- `cihangir-disci`: "CİHANGİR DİŞÇİ · "Cihangir Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, Şişli'ye 8 Dakika"" → "Cihangir Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, Şişli'ye 8 Dakika"
- `cumartesi-acik-disci-pazar-acik-disci`: "ACİL DİŞÇİ · "Şişli Cumartesi Açık Dişçi, Pazar açık Dişçi — 7/24 Hafta Sonu Acil Diş Tedavisi İstanbul"" → "Şişli Cumartesi Açık Dişçi, Pazar açık Dişçi — Hafta Sonu Açık Dişçi İstanbul"
- `devrim-biriken-sipahi`: "EN İYİ DİŞÇİ · "İstanbul'un En İyi Diş Hekimi — Dr. Devrim Biriken Sipahi (Şişli)"" → "İstanbul'un En İyi Diş Hekimi — Dr. Devrim Biriken Sipahi (Şişli)"
- `eminonu-acik-disci`: "EMİNÖNÜ AÇIK DİŞÇİ · "Eminönü Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, 7/24 Hizmet"" → "Eminönü Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, Hafta Sonu Açık"
- `esenler-acik-disci`: "ESENLER AÇIK DİŞÇİ · "Esenler Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, 7/24 Hizmet"" → "Esenler Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, Hafta Sonu Açık"
- `etiler-acik-disci`: "ETİLER AÇIK DİŞÇİ · "Etiler Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, 7/24 Hizmet"" → "Etiler Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, Hafta Sonu Açık"
- `eyup-acik-disci`: "EYÜP AÇIK DİŞÇİ · "Eyüp Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, 7/24 Hizmet"" → "Eyüp Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, Hafta Sonu Açık"
- `fatih-acik-disci`: "FATİH AÇIK DİŞÇİ · "Fatih Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, 7/24 Hizmet"" → "Fatih Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, Hafta Sonu Açık"
- `gaziosmanpasa-acik-disci`: "GAZİOSMANPAŞA AÇIK DİŞÇİ · "Gaziosmanpaşa Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, 7/24 Hizmet"" → "Gaziosmanpaşa Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, Hafta Sonu Açık"
- `gungoren-acik-disci`: "GÜNGÖREN AÇIK DİŞÇİ · "Güngören Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, 7/24 Hizmet"" → "Güngören Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, Hafta Sonu Açık"
- `istanbul-acik-disci`: "İSTANBUL AÇIK DİŞÇİ · "İstanbul Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, Uzman Diş Hekimi, 7/24"" → "İstanbul Açık Dişçi — Dr. Devrim Biriken Sipahi"
- `kadikoy-acik-disci`: "KADIKÖY AÇIK DİŞÇİ · "Kadıköy Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, 7/24 Hizmet"" → "Kadıköy Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, Hafta Sonu Açık"
- `kagithane-acik-disci`: "KAĞITHANE AÇIK DİŞÇİ · "Kağıthane Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, 7/24 Hizmet"" → "Kağıthane Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, Hafta Sonu Açık"
- `levent-disci`: "LEVENT DİŞÇİ · "Levent Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, Şişli'ye 5 Dakika"" → "Levent Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, Şişli'ye 5 Dakika"
- `nisantasi-acik-disci`: "NİŞANTAŞI AÇIK DİŞÇİ · "Nişantaşı Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, 7/24 Hizmet"" → "Nişantaşı Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, Hafta Sonu Açık"
- `nisantasi-disci-osmanbey-disci`: "NİŞANTAŞI DİŞÇİ & OSMANBEY DİŞÇİ · "Nişantaşı & Osmanbey Dişçi — Dr. Devrim Biriken Sipahi (7/24 Acil)"" → "Nişantaşı & Osmanbey Dişçi — Dr. Devrim Biriken Sipahi"
- `ortakoy-disci`: "ORTAKÖY DİŞÇİ · "ORTAKÖY Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, Şişli'ye 10 Dakika"" → "ORTAKÖY Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, Şişli'ye 10 Dakika"
- `pazar-acik-disci-kagithane`: "KAĞITHANE PAZAR AÇIK DİŞÇİ · "Kağıthane Pazar Açık Dişçi — Dr. Devrim Biriken Sipahi | Pazar Günü Açık Diş Kliniği"" → "Kağıthane Pazar Açık Dişçi — Dr. Devrim Biriken Sipahi | Pazar Günü Açık Diş Kliniği"
- `pazar-acik-disci-nisantasi`: "NİŞANTAŞI PAZAR AÇIK DİŞÇİ · "Nişantaşı Pazar Açık Dişçi — Dr. Devrim Biriken Sipahi | Pazar Günü Açık Diş Kliniği"" → "Nişantaşı Pazar Açık Dişçi — Dr. Devrim Biriken Sipahi | Pazar Günü Açık Diş Kliniği"
- `pazar-acik-disci-osmanbey`: "OSMANBEY PAZAR AÇIK DİŞÇİ · "Osmanbey Pazar Açık Dişçi — Dr. Devrim Biriken Sipahi | Pazar Günü Açık Diş Kliniği"" → "Osmanbey Pazar Açık Dişçi — Dr. Devrim Biriken Sipahi | Pazar Günü Açık Diş Kliniği"
- `pazar-acik-disci-sisli`: "ŞİŞLİ PAZAR AÇIK DİŞÇİ · "Şişli Pazar Açık Dişçi — Dr. Devrim Biriken Sipahi | Pazar Günü Açık Diş Kliniği"" → "Şişli Pazar Açık Dişçi — Dr. Devrim Biriken Sipahi | Pazar Günü Açık Diş Kliniği"
- `pazar-acik-disci`: "ACİL DİŞÇİ · "Pazar Açık Dişçi Şişli — Pazar Günü Açık Diş Hekimi İstanbul"" → "Pazar Açık Dişçi Şişli — Pazar Günü Açık Diş Hekimi İstanbul"
- `sariyer-acik-disci`: "SARIYER AÇIK DİŞÇİ · "Sarıyer Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, 7/24 Hizmet"" → "Sarıyer Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, Hafta Sonu Açık"
- `sirinevler-acik-disci`: "ŞİRİNEVLER AÇIK DİŞÇİ · "Şirinevler Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, 7/24 Hizmet"" → "Şirinevler Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, Hafta Sonu Açık"
- `sisli-acik-disci`: "ŞİŞLİ AÇIK DİŞÇİ · "Şişli Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, 7/24 Hizmet"" → "Şişli Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, Hafta Sonu Açık"
- `sisli-dis-hekimi`: "ŞİŞLİ DİŞÇİ · "Şişli Dişçi, Diş Hekimi | Dr. Devrim Biriken Sipahi | Kanal, İmplant, Estetik Diş | Mecidiyeköy"" → "Şişli Dişçi, Diş Hekimi | Dr. Devrim Biriken Sipahi | Kanal, İmplant, Estetik Diş | Mecidiyeköy"
- `sisli-disci-mecidiyekoy-disci`: "ŞİŞLİ DİŞÇİ & MECİDİYEKÖY DİŞÇİ · "Şişli & Mecidiyeköy Dişçi — Dr. Devrim Biriken Sipahi (7/24 Acil)"" → "Şişli & Mecidiyeköy Dişçi — Dr. Devrim Biriken Sipahi"
- `sisli-disci`: "ŞİŞLİ DİŞÇİ · "Şişli Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, Şişli Merkezde"" → "Şişli Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, Şişli Merkezde"
- `taksim-disci`: "TAKSİM DİŞÇİ · "Taksim Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, Şişli'ye 5 Dakika"" → "Taksim Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, Şişli'ye 5 Dakika"
- `uskudar-acik-disci`: "ÜSKÜDAR AÇIK DİŞÇİ · "Üsküdar Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, 7/24 Hizmet"" → "Üsküdar Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, Hafta Sonu Açık"
- `zeytinburnu-acik-disci`: "ZEYTİNBURNU AÇIK DİŞÇİ · "Zeytinburnu Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, 7/24 Hizmet"" → "Zeytinburnu Açık Dişçi — Dr. Devrim Biriken Sipahi | 35+ Yıl Tecrübe, Hafta Sonu Açık"

## 7. Bitenler ve kalanlar

**Bitti ve canlıda:** uzak ilçe budaması (drdevrim 2.233 sayfa 410, dbs 13 yazı 301); 11 yeni dil (2.145 sayfa) sitemap'te; drdevrim saat/gece temizliği; dbs sitemap temizliği; ana sayfa etiketleri; iç linkler (drdevrim "diğer ilçeler" Şişli'den başlar, dbs listeler veritabanından otomatik); testler (dbs 34, drdevrim derleme + canlı kontrol); etki ölçüm komutu ve temel ölçüm.

**Hekimin kararını bekleyen:**
- Nobel/Straumann marka cümleleri (drdevrim TR/EN/DE/RU/UK/BG + hizmet verisi; hekim S.I.N. standart dedi).
- Invisalign / ortodonti hizmet sayfaları (soru 25: ortodonti yapılıyor mu?).
- "Garanti" ifadeleri: drdevrim "10 yıl garanti", "doğal ton garantisi", "Etik tedavi garantisi"; dbs "Hollywood smile garantisi", "en net fiyat garantisi".
- Eski yorum sayıları: drdevrim 124, dbs şemada 352.
- /hizmetler/acil-dis/ sayfası kalsın mı (saati düzeltildi).
- Kalan 17 ilçede uzak mahalleler (Göktürk, Kemerburgaz, Bahçeköy, Kireçburnu, Bostancı vb.): ikinci, daha geniş tarama.
- dbs ana sayfa "her ilçesinden… Kadıköy'den Bakırköy'e" paragrafı (16 dil).
- Eski 11 drdevrim ailesinin hreflang listesine yeni 11 dilin eklenmesi (teknik, hekim kararı gerekmez; sıradaki iş).
- Search Console: iki sitemap'i yeniden gönder (drdevrim.com/sitemap.xml, devrimbirikensipahi.com.tr/sitemap.xml); 410'lar "kaldırıldı" olarak düşer.

## 8. Geri alma yolları

- **drdevrim ilçe:** `app/data/istanbul-data-kaldirilan.ts` içindeki ilçe satırını `istanbul-data.ts` → `istanbulIlceleri` dizisine (mesafe sırasında) taşı; rotalar, sitemap, listeler ve 410 kuralı kendiliğinden güncellenir. Push → Netlify.
- **drdevrim diller:** `app/data/pseo-segments.ts` içinden dili sil → sayfalar, sitemap ve hub 301'i düşer.
- **drdevrim saatler:** `git revert 3c971d3` (tek commit).
- **dbs yazılar:** `blog/removed.py` sözlüğünden slug'ı sil → yazı aynı adreste yeniden yayında, 301 kalkar.
- **dbs içerik:** Render Shell: `python manage.py icerik_duzelt --geri-al` (before/ dosyalarından 44 yazıyı eski hâline yazar; göç kaydı durduğu için yeniden uygulanmaz). Tek yazı: `--slug <slug> --geri-al`.
- **dbs açılış kancası:** Render ortam değişkeni `BLOG_GOC_BOOT=0` kapatır.

## 9. Etki ölçümü

Komut (dentaltourism, salt-okunur): `manage.py pseo_etki --days 7` son 7 günü önceki 7 günle karşılaştırır; `--days 28` aylık.

Temel ölçüm, dağıtım ÖNCESİ (15–22.11.2026):

| Site | Oturum | İnsan | İletişim oturumu | Silinen sayfalara iniş |
|---|---|---|---|---|
| drdevrim | 1.103 | 103 | 18 (WhatsApp 10, telefon 19, form 1 tıklama) | 45 / 103 insan inişi (%44) — en çok Eyüpsultan 8, Sultangazi 6, Çekmeköy 5 (3 iletişim), Maltepe 5, Büyükçekmece 5 (3 iletişim) |
| devrimbirikensipahi | 131 | 44 | 3 | 0 |

Beklenti ve ölçütler: ilk 2–4 hafta drdevrim insan trafiği düşer (silinen sayfalardaki 45 iniş gider). Başarı: (1) Şişli ve çevresi 17 ilçe sayfalarına iniş ve iletişim oturumu artışı, (2) kaldırılan sayfalara iniş sıfır, (3) 11 yeni dilden iniş başlaması (GSC'de hreflang/dil sorguları), (4) dbs'de 44 yazının trafiği korunurken "acil/gece" sorgularının kaybolması. Haftalık rapor: 29.11, 6.12, 13.12; toplu değerlendirme 20.12 (`--days 28`).
GSC konum verisini içe aktaramıyoruz; Şişli sayfalarının sorgu konumlarını hekim GSC'den izler.

## 10. Doğrulama kaydı (22.11.2026, 22:30–23:10 TR saati)

- drdevrim: sitemap 4.343 (yerel derleme ile birebir aynı); /disci/pendik/, /disci/pendik/kurtkoy/, /en/dentist/tuzla/, /ru/stomatolog/sile/, /de/zahnarzt/silivri/, /fr/dentiste/adalar/, /haftasonu/umraniye/ → 410; /disci/sisli/, /disci/sisli/nisantasi/, /fr/dentiste/sisli/, /nl/tandarts/kagithane/, /ar/tabib-asnan/besiktas/, /az/dis-hekimi/beyoglu/, /sv/tandlakare/sisli/, /ro/dentist/fatih/ → 200; /fr/dentiste → 301 /lang/fr/; /sv/tandlakare → 301 /lang/en/.
- devrimbirikensipahi: sitemap 128, /accounts/ yok, 13 slug yok; 13 yazı 301 doğru hedefe; /blog/en-iyi-disci/sisli-acik-disci/ 200; ana sayfada Pendik/Kartal/Maltepe/Ataşehir/Beylikdüzü geçmiyor.
- devrimbirikensipahi içerik temizliği: uygulandı — Render açılış kancası göç 0003'ü dağıtımda çalıştırdı; canlıda 44/44 yazı doğrulandı (22.11.2026 23:05).

## 11. Ek — 23.11.2026: drdevrim'de "acil" niyeti ve "24 saat" ifadeleri kaldırıldı

**Tetikleyici:** drdevrim Search Console'da 22–23.11 sorguları: "acil dişçi esenyurt" (14 gösterim), "nöbetçi dişçi esenyurt" (10),
"nöbetçi dişçi" (9), "sultangazi 24 saat açık dişçi", "7 24 açık diş hastanesi kadıköy/kartal/maltepe", "esenyurt dişçi 7 24" vb.
Kaynağı: Google'ın dizinindeki ESKİ sayfa kopyaları ("Nöbetçi dişçi aramadan önce bizi arayın", "7/24 telefon", "07:00–23:00").
Sorgulardaki Esenyurt, Sultangazi, Kartal, Pendik, Küçükçekmece, Maltepe, Sancaktepe, Başakşehir, Beylikdüzü, Tuzla, Arnavutköy,
Büyükçekmece, Ümraniye, Ataşehir sayfaları 22.11 gecesinden beri 410; kalan ilçelerin sayfaları yeni metinle yayında. Gösterimler
Google yeniden taradıkça düşer; site tarafında yapılacak başka şey yok.

**Tarama (kodun tamamı + canlıda 141 sayfa):** "nöbetçi", "7/24", "gece açık" hiçbir yerde yoktu. Kalan iki şey:
1. Ana sayfa 18 dilde "24 saat içinde geri döneriz" (yanıt süresi cümlesi).
2. "Acil" niyeti: /hizmetler/acil-dis/ sayfası ("Acil Diş Hekimi İstanbul Şişli" meta başlığı), pSEO şablonlarında "Acil {mahalle}
   dişçi", "{ilçe} acil diş ağrısında ne yapmalıyım?" SSS'si, şemada "Acil Diş Tedavisi", hizmet kartları, menü, ana sayfa SSS'lerinde
   acil/Notfall/spoed/urgenze, hizmet etiketi "Acil Tedavi", hizmetler ve hasta yorumları meta açıklamaları, yorum etiketleri.
Raporlanan "7 24" eşleşmesi logo SVG'sindeki çizim koordinatıdır, metin değildir.

**Yapılanlar (drdevrim commit `cea8d9b`, 28 dosya, 78 ekleme / 76 silme):**
- /hizmetler/acil-dis/ → **301** → /hizmetler/dis-agrisi/. Hizmet adı "Diş Ağrısı Tedavisi — Haftasonu Dahil, Aynı Gün"; meta başlık
  "Diş Ağrısı Tedavisi İstanbul Şişli | Haftasonu Açık, Aynı Gün Randevu"; metinlerdeki "acil" → "aynı gün" / "diş ağrısı"
  (`app/data/services-data.ts`, `app/components/TheNav.vue`, `nuxt.config.ts`). Sitemap: acil-dis çıktı, dis-agrisi girdi (toplam 4.343).
- `app/pages/disci/[ilce]/index.vue`, `.../[mahalle]/index.vue`, `app/pages/haftasonu/[ilce]/index.vue`, `.../[mahalle]/index.vue`
  (4 aile şablonu = 195 × 2 canlı sayfa): "acil durumlarda beklemenize gerek yok" → "diş ağrısında…"; "Acil {mahalle} dişçi" →
  "{mahalle} dişçi"; SSS "{yer} acil diş ağrısında ne yapmalıyım?" → "{yer} diş ağrısı için aynı gün randevu alabilir miyim?";
  "acil kanal tedavisi" → "kanal tedavisi"; şema "Acil Diş Tedavisi" → "Diş Ağrısı Tedavisi"; "hastane acillerine yönlendirilir" →
  "pazartesiyi beklemek zorunda kalır"; hizmet kartı → "Diş Ağrısı Tedavisi" (/hizmetler/dis-agrisi/); 🚨 → ⏱️.
- `app/data/home-i18n/*.ts` (18 dil): "24 saat içinde geri döneriz" → "kısa sürede geri döneriz" karşılıkları; SSS "acil durumlar /
  Notfällen / spoed / urgenze / спешни / urgjente" → diş ağrısı; etiket "Acil Tedavi / علاج طارئ / Спешно лечение / Urgenza dentale /
  Spoedbehandeling / Nagły przypadek / Trajtim Urgjent" → aynı gün tedavi karşılıkları.
- `app/pages/hizmetler/index.vue`, `app/pages/hasta-yorumlari/index.vue` meta açıklamaları; `app/data/reviews-data.ts` etiketleri
  "Acil Tedavi" → "Aynı Gün Tedavi". Hastaların kendi yorum metinlerine dokunulmadı (bir İngilizce yorumda "emergency" sözcüğü
  hastanın ifadesi olarak duruyor).

**Dağıtım:** Netlify 21:18 (`cea8d9b`) ve 21:45 (`87ee878`, boş) push'larını yayınlamadı; 22:01'deki üçüncü tetikleme (`5c3d9f0`)
yaklaşık 4 dakikada çıktı. Nedeni Netlify panelinden (Deploys) görülmeli.

**Canlı doğrulama (23.11 22:05 TR):** /hizmetler/acil-dis/ 301 → /hizmetler/dis-agrisi/ (200); sitemap 4.343, acil-dis yok;
35 sayfa (ana sayfa, 10 dil sayfası, hizmetler, 4 aile × ilçe/mahalle, 9 yabancı aile) tarandı: "acil / emergency / Notfall / 24 saat /
7-24 / nöbetçi" yok; tek eşleşme hasta yorumundaki "emergency".

**Google tarafı için öneri:** GSC → URL inspection → "Request indexing": /, /haftasonu/sisli/, /disci/sisli/, /hizmetler/dis-agrisi/.
Gösterimlerdeki "nöbetçi / 7 24 / acil" kuyruğu yeniden taramayla haftalar içinde söner; silinen ilçelerinki 410 ile düşer.
