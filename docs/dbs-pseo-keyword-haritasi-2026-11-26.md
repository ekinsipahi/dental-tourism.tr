# Anahtar kelime haritası — devrimbirikensipahi.com.tr pSEO (26.11.2026)

Hekimin 26.11.2026'da verdiği beş keyword partisinin hangi sayfaya gittiği, hangi varyasyonun nerede kullanıldığı ve
nelerin neden dışarıda kaldığı. Kaynak kod: `/mnt/d/projects/devrim_old/clinic/pseo/` (commit `897ef7c`, Render'da canlı).
Kurallar: fiyat/tutar yok, "garanti" yok, acil / nöbetçi / 7-24 / 24 saat / gece niyeti yok ("acil dişçi değiliz"), metinde
"en iyi" ve unvan iddiası yok (sağlık tanıtım mevzuatı), otel/transfer vaadi yok. Klinik gerçekleri hekimden: her gün
05:00–00:00 (cumartesi, pazar, bayram dahil), ortodonti yapılıyor, SIN implant sistemi, Dt. Ekin Sipahi implantoloji master'ı,
dijital planlama, implant sürecinde hasta dişsiz bırakılmaz.

## 1. Sayfa yapısı ve sayılar

| Aile | Adres kalıbı | Seviye | Sayfa |
|---|---|---|---|
| Diş Kliniği | /dis-klinigi/{ilçe}/ ve /dis-klinigi/{ilçe}/{mahalle}/ | ilçe + mahalle | 262 |
| Pazar Açık Dişçi | /pazar-acik-disci/{ilçe}/[{mahalle}/] | ilçe + mahalle | 262 |
| Açık Dişçi (şu an açık) | /acik-disci/{ilçe}/[{mahalle}/] | ilçe + mahalle | 262 |
| Diş Hekimi Tavsiye | /dis-hekimi-tavsiye/{ilçe}/ | ilçe | 23 |
| Tedavi × ilçe (10 tedavi) | /{tedavi}/{ilçe}/ | ilçe | 230 |
| **Toplam pSEO** | | | **1.039** |

Sitemap: 128 → **1.127** (40 bölge blog yazısı 301 olup düştü, 1.039 pSEO eklendi).

**Konumlar (23 ilçe, 239 mahalle; kliniğe kuş uçuşu):** Şişli 1 km (16 mahalle + Bomonti, Kurtuluş), Kağıthane 2, Beyoğlu 3,5,
Beşiktaş 3,5, Eyüpsultan 4,5, Üsküdar 5,5, Gaziosmanpaşa 5,5, Bayrampaşa 6,5, Fatih 6,5, Esenler 9, Kadıköy 9,5, Güngören 10,
Zeytinburnu 10,5, Sultangazi 10,5, Ümraniye 10,5, Bağcılar 11, Beykoz 11,5, Bahçelievler 12,5, Sarıyer 13, Bakırköy 13,
Küçükçekmece 19, Arnavutköy 24, Esenyurt 26.
**Hekimin kesme listesi (dahil değil):** Ataşehir, Başakşehir, Çekmeköy, Maltepe, Sancaktepe, Avcılar, Adalar, Kartal, Pendik,
Beylikdüzü, Büyükçekmece, Tuzla, Çatalca, Şile, Silivri. (Küçükçekmece, Arnavutköy ve Esenyurt listede olmadığı için içeride.)

**10 tedavi:** implant-tedavisi, zirkonyum-kaplama, dis-beyazlatma, kanal-tedavisi, dis-cekimi, dis-tasi-temizligi, gulus-tasarimi,
cocuk-dis-hekimi, ortodonti, seffaf-plak. Kök sayfası olmayan beşi (zirkonyum, beyazlatma, gülüş tasarımı, ortodonti, şeffaf plak)
kökten Şişli sayfasına 301 gider; diğerlerinin kökü mevcut kategori sayfasıdır.

## 2. Parti 1 — "Acil / şu an açık" + "Şişli lokal" + "Hafta sonu" + "Genel klinik"

| Keyword (hekimin listesi) | Hacim | Nereye gitti | Sayfada nasıl geçiyor |
|---|---|---|---|
| diş kliniği şu anda açık olanlar | 170 | /acik-disci/{ilçe}/[{mahalle}/] | lead: "Diş kliniği şu anda açık olanlar arasında mıyız?"; SSS "{İlçe}'de şu anda açık dişçi var mı?"; JS kutusu "Şu an açığız" |
| açık dişçi şişli, şişli dişçi şu anda açık olanlar | – | /acik-disci/sisli/ | h1 "Şişli Açık Dişçi: Sabah 5'ten Gece 12'ye"; title "Şişli Şu An Açık Dişçi | …" |
| diş kliniği en yakın, en yakın dişçi | – | /acik-disci/… | SSS "{Yer} için en yakın dişçi siz misiniz?" (km ile dürüst cevap) |
| nöbetçi dişçi şişli, şişli dişçi 24 saat, 7 24 dişçi şişli, gece açık dişçi şişli, acil dişçi/diş hekimi şişli, diş ağrısı acil dişçi, gece dişçi, nöbetçi diş hekimi avrupa yakası | 20/10/– | **YOK** | hekim: "acil dişçi değiliz"; bu kelimeler hiçbir sayfada geçmez (test tarar). Diş ağrısı niyeti /dis-agrisi-tedavisi/ sayfasına (eski /acil-dis-hekimi/ 301) |
| diş doktoru şişli | 40 | /dis-klinigi/sisli/ | title "Şişli Diş Kliniği"; "diş doktoru" ifadesi gövdede |
| çocuk diş doktoru şişli | 20 | /cocuk-dis-hekimi/sisli/ | h1 "Şişli Çocuk Diş Hekimi"; SSS "Şişli'de çocuk diş doktoru arıyorum…" |
| dişçi şişli, diş hekimi şişli, istanbul şişli dişçi, dişçi şişli yakınında, dişci şişli, dis doktoru sisli, diş şişli | – | /dis-klinigi/sisli/ | lead "Şişli yakınında dişçi, diş doktoru ya da diş kliniği…"; SSS "İstanbul Şişli'de dişçi randevusu nasıl alırım?" (`84c06c1`) |
| mecidiyeköy dişçi, nişantaşı diş kliniği, osmanbey dişçi, fulya diş kliniği, bomonti dişçi, gayrettepe dişçi, kurtuluş dişçi | – | /dis-klinigi/sisli/{mecidiyekoy,nisantasi,osmanbey,fulya,bomonti,kurtulus}/ ; gayrettepe → /dis-klinigi/besiktas/gayrettepe/ | mahalle sayfaları (Bomonti ve Kurtuluş bu parti için eklendi) |
| implant şişli, zirkonyum kaplama şişli, diş beyazlatma şişli, kanal tedavisi şişli, 20lik diş çekimi şişli, diş taşı temizliği şişli, gülüş tasarımı şişli | – | /implant-tedavisi/sisli/, /zirkonyum-kaplama/sisli/, /dis-beyazlatma/sisli/, /kanal-tedavisi/sisli/, /dis-cekimi/sisli/, /dis-tasi-temizligi/sisli/, /gulus-tasarimi/sisli/ | tedavi × ilçe (aynı kalıp 23 ilçe için) |
| diş teli şişli, şeffaf plak şişli | – | /ortodonti/sisli/, /seffaf-plak/sisli/ | hekim 26.11: ortodonti yapılıyor |
| implant fiyatları şişli, şişli dişçi fiyatları | – | **YOK** (ayrı sayfa açılmaz) | fiyat kuralı; her sayfada SSS "Fiyat bilgisi alabilir miyim?" → yazılı teklif, WhatsApp |
| şişli diş kliniği randevu | – | /dis-klinigi/sisli/ | "Saatler ve randevu" bölümü |
| pazar açık dişçi | 110 | /pazar-acik-disci/{ilçe}/[{mahalle}/] | h1 "{Yer} Pazar Açık Dişçi" |
| hafta sonu dişçiler açık mı | 90 | /pazar-acik-disci/… | lead (soru) + SSS "Hafta sonu dişçiler açık mı?" (`84c06c1`) |
| pazar günü açık diş hekimi | 50 | /pazar-acik-disci/… | lead |
| hafta sonu açık dişçi | 30 | /pazar-acik-disci/… (dbs) — drdevrim'de /haftasonu/ ailesi zaten var | H2 "Hafta sonu açık dişçi: hangi tedaviler yapılır?" |
| özel dişçiler hafta sonu açık mı | 30 | /pazar-acik-disci/… | SSS "Özel dişçiler hafta sonu açık mı?" |
| pazar dişçiler açık mı, diş klinikleri hafta sonu açık mı, pazar dişçi açık mı, pazar açık diş kliniği/hekimi, pazar günü açık dişçi, pazar açık olan dişçiler | 20/20/10/– | /pazar-acik-disci/… | lead + SSS |
| pazar açık dişçi şişli, cumartesi açık dişçi şişli, bayramda açık dişçi | – | /pazar-acik-disci/sisli/ | SSS "Cumartesi açık mısınız?", "Bayramda açık mısınız?" |
| hafta sonu açık dişçi istanbul, pazar günü açık dişçi avrupa yakası | – | /pazar-acik-disci/sisli/ (eski blog yazıları buraya 301) | |
| diş klinikleri istanbul | 110 | /dis-klinigi/{ilçe}/[{mahalle}/] | gövde "Diş klinikleri İstanbul genelinde…" |
| diş polikliniği randevu alma | 20 | /dis-klinigi/… | "Saatler ve randevu" |
| diş kliniği, diş klinik, diş polikliniği, uzman diş hekimi | – | /dis-klinigi/… | gövde; "uzman diş hekimi" SSS "Uzman diş hekimi ile diş hekimi arasındaki fark nedir?" (bilgi sorusu, unvan iddiası yok, `84c06c1`) |
| diş polisaj nedir / fiyatları | 170/90 | /dis-tasi-temizligi/{ilçe}/ | bölüm "Diş polisajı nedir?", SSS "Polisaj ile beyazlatma aynı şey mi?" (fiyat yok) |
| Negatifler (ankara, izmir, hastane, devlet, fakülte, maaş, iş ilanları, açma şartları, polisaj macunu, dış cephe, polis, şikayet…) | – | Ads negatif listesi | pSEO'da bu niyetler için sayfa yok |

## 3. Parti 2 — "Tavsiye / en iyi dişçi" + "Genel İstanbul"

| Keyword | Hacim | Nereye gitti | Nasıl |
|---|---|---|---|
| diş hekimi tavsiye | 30 | /dis-hekimi-tavsiye/{ilçe}/ (23 sayfa) | h1 "{İlçe} Diş Hekimi Tavsiye" |
| diş hekimi tavsiye istanbul, iyi bir dişçi arıyorum, iyi dişçi, iyi bir dişçi | 10/10/– | /dis-hekimi-tavsiye/… | lead "İyi bir diş hekimi arayan hastalar…" |
| en iyi dişçi istanbul avrupa yakası, en iyi dişçi istanbul, en iyi dişçi nerede/hangisi | 10/– | /dis-hekimi-tavsiye/… | hekim 27.11: yalnızca SSS sorusu — "{İlçe}'de en iyi dişçi hangisi?", "İstanbul Avrupa yakasında en iyi dişçi nerede?" (Anadolu: "İstanbul'da en iyi dişçi nerede?"); title/meta/H1/metinde yok (test tarar) |
| şişli diş hekimi tavsiye, şişli dişçi tavsiye, şişli iyi dişçi, güvenilir dişçi şişli, şişli dişçi yorumları | – | /dis-hekimi-tavsiye/sisli/ | SSS "Şişli'de güvenilir diş hekimi nasıl bulurum?", "Hasta yorumlarınızı nerede okuyabilirim?" |
| mecidiyeköy dişçi tavsiye, nişantaşı diş hekimi tavsiye | – | /dis-hekimi-tavsiye/sisli/ (tavsiye ailesi mahalle seviyesine inmez: thin content) | |
| implant için diş hekimi tavsiye istanbul | – | /dis-hekimi-tavsiye/… SSS + /implant-tedavisi/… | SSS "İmplant için diş hekimi tavsiyesi arıyorum…" |
| istanbul diş klinikleri/kliniği, istanbul dişçi, istanbul diş randevu | – | /dis-klinigi/{ilçe}/ ailesi | "istanbul diş randevu" → "Saatler ve randevu" |
| iyi dişçi nasıl bulunur / nasıl anlaşılır | – | /dis-hekimi-tavsiye/… bölüm "İyi bir diş hekimi nasıl seçilir?" | ayrı blog yazısı henüz yok (sıradaki iş) |
| Negatifler (eskişehir… kadıköy*, oda, fakülte, ekşi, kadınlar kulübü) | – | Ads | *Kadıköy pSEO'da ilçe olarak VAR; Ads'te negatif olması hekimin kararı |

## 4. Parti 4 — "Uzman / cerrah / prof"

Klinikte endodontist, çene cerrahı ve profesör unvanı yok → unvan iddiası yapılmaz, hizmet anlatılır.

| Keyword | Hacim | Nereye gitti | Nasıl |
|---|---|---|---|
| kanal tedavisi uzmanı, diş kanal tedavisi uzmanı, endodonti…, kanal tedavisi şişli/istanbul, kanal tedavisi yenileme | 320/20/– | /kanal-tedavisi/{ilçe}/ | SSS "Kanal tedavisi için uzmana mı gitmeliyim?", "Kanal tedavisi uzmanına ne denir?", "…hangi bölümdür?", "Diş kanal tedavisi uzmanı ne yapar?" (cevapta "endodonti (kanal tedavisi) uzmanı"), "İstanbul'da kanal tedavisi için röntgenimi gönderebilir miyim?" (son ikisi `84c06c1`); bölüm "Kanal tedavisi yenileme"; unvan yok |
| mikroskopla kanal tedavisi | – | **YOK** | mikroskop iddiası yasak (hekim kuralı) |
| cerrah diş doktoru, cerrah dişçi, cerrahi diş kliniği, gömülü diş çekimi şişli, yirmilik diş ameliyatı şişli, çene cerrahı şişli | 260/– | /dis-cekimi/{ilçe}/ | SSS "Gömülü diş çekimi için cerrah mı gerekir?", "Cerrah diş doktoru ya da cerrah dişçi aramalı mıyım?" (cevapta "cerrahi diş kliniği"), "Diş hekimi cerrah olabilir mi?", "Gömülü 20'lik diş çekimi fiyatı ve cerrahi diş çekimi fiyatları neye göre değişir?" (tutar yok; son üçü `84c06c1`); "{ilçe}'den gömülü diş çekimi…", "…yirmilik diş ameliyatı…"; çene cerrahı unvan olarak yok ("ağız, diş ve çene cerrahisine yönlendiririz") |
| implant uzmanı, implant cerrahı, implantolog | – | /implant-tedavisi/{ilçe}/ | bölüm "Kim yapıyor, hangi sistem?"; SSS "İmplant cerrahı kim, implantı kim yapıyor?", "İmplantolog ya da implant uzmanı mı aramalıyım?" (`84c06c1`): Dt. Ekin Sipahi implantoloji master'ı, SIN sistemi |
| prof diş doktoru, prof dr diş hekimi (+istanbul/şişli), prof dişçi, doç dr… | 390/20/10 | **YOK** | profesör yok; hekimin talimatı "yoksa açma" |
| kanal tedavisi uzmanına ne denir, hangi bölüm, cerrah dişi nasıl çeker, genel cerrah diş çeker mi… | – | /kanal-tedavisi/{ilçe}/ ve /dis-cekimi/{ilçe}/ SSS'lerinde var ("Kanal tedavisi uzmanına ne denir?", "Cerrah dişi nasıl çeker…", "Diş hekimi cerrah mıdır, genel cerrah diş çeker mi?") | blog yazısı "Hangi diş sorunu için hangi uzmana gidilir?" henüz yazılmadı |
| cerrahpaşa, şehirler, isimle aramalar, profdent, macun/fırça, kanal 7 | – | Ads negatif | |

## 5. Parti 3 — İngilizce (yabancı hasta) → dentaltourism.tr

Bu kelimeler dbs'ye değil dentaltourism.tr'ye aittir (yabancı hasta oraya; 17 dil, tek klinik). Mevcut sayfalarla eşleme:

| Grup | Keyword'ler | dentaltourism.tr sayfası | Durum |
|---|---|---|---|
| İmplant | dental implants istanbul turkey, istanbul dentist implant, best dentist in istanbul for implants, full mouth dental implants turkey, all on 4 istanbul | /treatments/dental-implants/, /treatments/all-on-4-implants/, /packages/dental-implants/ | var |
| Kaplama / veneer | dental veneers istanbul, istanbul dentist veneers, best dentist for crowns, zirconia crowns istanbul, emax veneers istanbul | /treatments/porcelain-veneers/, /treatments/zirconia-crowns/, /packages/… | var |
| Bonding | dental bonding istanbul, composite bonding | /treatments/composite-veneers/ | var (başlıkta "bonding" varyasyonu eklenmeli) |
| Hollywood smile / smile makeover / turkey teeth | | /treatments/hollywood-smile/, /guide/getting-teeth-done-in-turkey/ | var |
| Beyazlatma, root canal, filling, cleaning | | /treatments/teeth-whitening/, root-canal-treatment/, tooth-fillings/, teeth-cleaning/ | var |
| Ortodonti | dental braces istanbul, orthodontist istanbul turkey | **YOK** — dentaltourism'de ortodonti sayfası yok | **açılacak** (hekim 26.11: ortodonti var) |
| Köprü, dental surgery, dental x ray | dental bridge in istanbul, dental surgery istanbul, dental x ray istanbul | /guide/dental-surgery-turkey/ kısmen; köprü sayfası yok | köprü: açılacak |
| Fiyat | istanbul dental clinic prices, dentist price list, veneers istanbul price, how much does dental work cost in turkey, implants turkey cost… | /prices/ ve /prices/{tedavi}/ (10 sayfa) | var; sayfalar tutar vermez, yazılı teklif anlatır (kural) |
| Paket | istanbul dentist package, dental package turkey all inclusive | /packages/ ve /packages/{tedavi}/ | var; otel/transfer vaadi yok |
| Best / reviews / recommended | best dentist istanbul turkey, good dentist istanbul, istanbul dentist reviews, istanbul dental clinic reviews, recommended dentists in turkey | /guide/best-dental-clinic-in-istanbul/, /guide/best-dental-clinic-turkey-reviews/, /clinics/dr-devrim-sipahi/, /dentists/… | var |
| Dental tourism istanbul, dental vacation, dental center, booking dentist istanbul | | /guide/dental-tourism/, /guide/dental-clinic-istanbul/, /dental-holidays-from/{ülke}/ (6) | var |
| Expat (İstanbul'da yaşayan yabancı) | english dentist istanbul, dentist nisantasi/besiktas/levent/taksim/mecidiyekoy/sisli, dental clinic nisantasi | /dental-clinic/{sisli,osmanbey,nisantasi,taksim,mecidiyekoy,gayrettepe,kagithane,besiktas,ortakoy,levent,4-levent,etiler,maslak}/ (13 semt × 17 dil) | var |
| english speaking dentist istanbul, expat dentist istanbul | | **YOK** — ayrı sayfa önerisi | açılacak |
| kids dentist istanbul | | **YOK** | açılacak (çocuk diş hekimliği EN sayfası) |
| emergency dentist istanbul (open now) | | **YOK** | acil niyeti yasak; "same-day appointment" olarak mevcut sayfalarda |
| biological / holistic / sedation | | **YOK** | sunulmuyor; sedasyon iddiası yasak |
| Başka diller (zahnklinik istanbul, dental kliniek istanbul, dental clinic istanbul avis/opinie) | | /de/, /nl/, /fr/, /pl/ sürümleri (tüm sayfalar 17 dilde) | var |
| "dentist near me" + ABD posta kodları, medicaid/nhs/aetna, rakip klinik adları, fuar/eğitim, tedarik, jobs | | Ads negatif | pSEO'da yok |

**dentaltourism'de açılacaklar (hekimden metin/onay gerekir):** EN ortodonti (braces + clear aligners) tedavi sayfası, dental bridge
sayfası, çocuk diş hekimliği EN sayfası, "English-speaking dentist in Istanbul" sayfası; /treatments/composite-veneers/ başlığına
"bonding" varyasyonu. Bunlar 17 dile de yayılır (mevcut çeviri düzeni).

## 6. Eski blog yazıları → yeni sayfalar (301, 40 yazı)

"X açık dişçi" → /acik-disci/X/ (15 ilçe + eyüp→eyupsultan, etiler→besiktas/etiler, şirinevler→bahcelievler/sirinevler,
nişantaşı→sisli/nisantasi, eminönü→fatih, istanbul ve avrupa-yakası→sisli); "pazar açık dişçi …" (7 yazı) → /pazar-acik-disci/…;
"X dişçi" (beşiktaş, beyoğlu, taksim, cihangir, ortaköy, levent, şişli, nişantaşı-osmanbey, mecidiyeköy) → /dis-klinigi/…;
sisli-en-iyi-disci → /dis-hekimi-tavsiye/sisli/; sisli-dis-hekimi → /sisli-dis-hekimi/. Yazılar veritabanında durur
(`blog/removed.py`, geri açmak = satırı silmek). Kalan: devrim-biriken-sipahi ve diğer kategorilerin yazıları.

## 7. Thin content önlemleri

Her sayfada konuma göre değişen bloklar: ulaşım cümlesi (Şişli içi / Avrupa / Anadolu yakası ayrı, km ile), konumlu SSS
(3–4 soru), ilçe sayfasında semt listesi / mahalle sayfasında kardeş semtler, en yakın 6 ilçe (km ile), aynı yer için diğer
aileler, aynı ilçe için 10 tedavi bağlantısı, "şu an açık" kutusu, hekim bloğu, Dentist + FAQPage + BreadcrumbList şeması
(areaServed = konum). Aile başına 3 özgün bölüm (klinik / pazar / açık / tavsiye vurgusu farklı). Test
`pseo/tests.py::test_tum_sayfalar_yasak_kelime_icermez` 1.039 sayfayı yasak kelimeler için tarar.

## 8. Ölçüm

Merkezi takip (site=dbs) `manage.py pseo_etki --days 7` ile haftalık; dbs'nin 18–25.11 taban çizgisi: 60 insan oturumu,
1 iletişim. GSC'ye https://devrimbirikensipahi.com.tr/sitemap.xml yeniden gönderilmeli.

## 9. Denetim — 27.11.2026 (düzeltme)

Bu belgenin 26.11 sürümü bazı ifadeleri "kullanıldı" diye gösteriyordu ama sayfalar render edilip ölçüldüğünde 90 keyword'ün
yalnızca **26'sı** hedef sayfada birebir geçiyordu; 38'inin sadece kelimeleri dağınıktı, 26'sı hiç yoktu (ör. "diş kliniği şu anda
açık olanlar", "diş doktoru şişli", "20lik diş çekimi şişli", "diş klinikleri hafta sonu açık mı", "iyi dişçi nasıl bulunur").

Düzeltme (dbs `3ad5d32`): aile ve tedavi metinleri ifadeleri ara başlık / SSS / cümle olarak **birer kez** içerecek şekilde yeniden
yazıldı. Ölçüm (Türkçe ek ve kelime sırası toleranslı, title/H1/H2/SSS/gövde):

| | Tam geçen | Not |
|---|---|---|
| Şişli sayfaları | 88 / 90 | "sin implant": sayfada "SIN implant" (ölçüm harf dönüşümü); "istanbul şişli dişçi": İstanbul ve "Şişli dişçi" ayrı cümlelerde |
| Kadıköy, Esenyurt sayfaları | 78 / 81 | "Kadıköy diş kliniği randevu" bilerek yok: o semtte klinik varmış gibi okunur |

Kalıcı test: dbs `pseo/tests.py::KeywordKapsamaTests` (16 sayfa, 70 ifade). Bilerek dışarıda (hekim kararı / karar bekliyor):
acil, nöbetçi, 24 saat, 7-24, gece; prof/doç; endodontist ve çene cerrahı unvanı; mikroskop; metinde "en iyi"; fiyat ifadeleri;
"uzman diş hekimi"; "cerrah diş doktoru" (son dördü hekime soruldu).

Aynı denetimde bulunan hata: hekim paragrafında Dt. Ekin Sipahi "kızı" yazıyordu; doğrusu "oğlu" (düzeltildi).

## 10. Eksik keyword'lerin eklenmesi — 27.11.2026

Bu belgede "kullanıldı" yazan keyword'ler 1.049 sayfanın hepsi render edilerek tek tek ölçüldü. Sayfada geçmeyenler dbs
`84c06c1` ile **yeni SSS sorusu** olarak eklendi. Mevcut cümle, title, description, H1, ara başlık ve link değişmedi
(render karşılaştırması: 593 sayfaya 1–3 soru eklendi, başka fark yok).

| Keyword | Sayfalar | Eklendiği yer |
|---|---|---|
| uzman diş hekimi | /dis-klinigi/… (262) | SSS "Uzman diş hekimi ile diş hekimi arasındaki fark nedir?" |
| istanbul şişli dişçi | /dis-klinigi/sisli/ | SSS "İstanbul Şişli'de dişçi randevusu nasıl alırım?" |
| hafta sonu dişçiler açık mı | /pazar-acik-disci/… (262) | SSS "Hafta sonu dişçiler açık mı?" (önceden yalnızca giriş cümlesinde) |
| implantolog, implant uzmanı | /implant-tedavisi/{ilçe}/ (23) | SSS "İmplantolog ya da implant uzmanı mı aramalıyım?" |
| diş kanal tedavisi uzmanı, endodonti kanal tedavisi uzmanı | /kanal-tedavisi/{ilçe}/ (23) | SSS "Diş kanal tedavisi uzmanı ne yapar?" |
| kanal tedavisi istanbul | /kanal-tedavisi/{ilçe}/ (23) | SSS "İstanbul'da kanal tedavisi için röntgenimi gönderebilir miyim?" |
| cerrah diş doktoru, cerrah dişçi, cerrahi diş kliniği | /dis-cekimi/{ilçe}/ (23) | SSS "Cerrah diş doktoru ya da cerrah dişçi aramalı mıyım?" |
| diş hekimi cerrah olabilir mi | /dis-cekimi/{ilçe}/ (23) | SSS "Diş hekimi cerrah olabilir mi?" |
| gömülü 20lik diş çekimi fiyatı, cerrah diş çekimi fiyatları | /dis-cekimi/{ilçe}/ (23) | SSS "Gömülü 20'lik diş çekimi fiyatı ve cerrahi diş çekimi fiyatları neye göre değişir?" (tutar yok) |

Unvan iddiası yok (bilgi soruları, hekim kararı 27.11). Kalıcı test: dbs `pseo/tests.py::KeywordKapsamaTests` (+13 ifade) ve
`test_hafta_sonu_sorusu_sss_te`.

Sayfada zaten olup yazımı farklı olanlar (dokunulmadı): "{yer} açık dişçi" H1'de (title'da "{yer} Şu An Açık Dişçi"); "{yer} diş teli"
SSS ve gövdede; "diş klinik" gövdede ("diş klinikleri"); "en iyi dişçi istanbul" Avrupa yakası sayfalarında "İstanbul Avrupa yakasında
en iyi dişçi nerede?"; mahalle sayfalarında "dişçi {mahalle} yakınında" lead'de "{mahalle}, {ilçe} yakınında dişçi" olarak.

**Geri alınan değişiklik:** aynı gün yapılan `a250bf7` (title'lar, mahalle adları, Güngören birleştirme, Türkçe ekler, ana sayfa
metinleri) hekimin isteğiyle geri alındı (`5736ea5`). İstenen yalnızca eksik keyword'lerin eklenmesiydi. Geri almayla eski hâline
dönenler: ana sayfada "acil randevu", "7/24", "7 gün 24 saat" (16 dil); "Beşiktaş'nin" türü ek hataları; kanal title'larında
"Dişinizi Kurtaralım"; aynı adlı mahallelerde yinelenen title'lar; Güngören'de "Merkez" ve "Güngören Merkez" iki ayrı sayfa.
Bunlara ancak hekim isterse dokunulur. Sayfa sayısı 1.039, sitemap 1.127.

**Hekim kararı (27.11.2026): Şişli'de eski GBP kategori sayfaları ile pSEO Şişli sayfaları ikisi de kalsın.** Aynı başlığı
hedefleyen çiftler: /sisli-dis-klinigi/ ↔ /dis-klinigi/sisli/, /implant-tedavisi/ ↔ /implant-tedavisi/sisli/, /kanal-tedavisi/,
/dis-cekimi/, /dis-tasi-temizligi/, /cocuk-dis-hekimi/ ↔ /…/sisli/.
