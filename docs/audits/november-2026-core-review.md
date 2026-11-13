# dentaltourism.tr — 12 Kasım 2026 core update incelemesi

## Sonuç

Sitenin tamamına “thin content” veya “spam” demek eldeki kanıtı aşar. Canlı implant fiyat ve paket sayfalarında tedaviye özgü, isimli hekim notları var. Bununla birlikte bazı fiyat/paket, ülke, semt ve şehir rehberi sayfaları arama niyetini karşılamak için yetersiz farklılık gösteriyor. Bunlar algoritmik görünürlük kaybı açısından inceleme önceliğidir; kesin ceza tahmini veya doğrulanmış politika ihlali değildir.

Search Console erişimi olmadan mevcut manuel işlem, gerçek indeks durumu, trafik etkisi veya sıralama kaybının nedeni doğrulanamaz. Kamuya açık HTML ve kaynak kod, Google'ın siteye verdiği değerlendirmeyi göstermez.

## Google'ın Kasım duyurusu ne diyor?

- Resmî duyuru: November 2026 core update, 10 Kasım 2026; küresel ve tüm dillerde; dağıtım iki haftaya kadar sürebilir. İnceleme sırasında tamamlanma bildirimi görünmüyordu.
- Duyuru yeni bir “pSEO cezası”, kelime sınırı veya özel thin-content eşiği açıklamıyor; genel core-update rehberine yönlendiriyor.
- Google'ın people-first rehberi, ana içeriğin amacını yerine getirmesini, özgünlüğünü ve doğruluğunu öne çıkarıyor. Sağlık konularında güven özellikle önem taşıyor. Gerçek deneyim olumlu; her URL'nin arama niyetini karşıladığının tek başına kanıtı değil.
- Spam politikasında scaled content abuse, kullanıcıya değer katmadan sıralamayı etkilemek amacıyla çok sayıda sayfa üretmekle ilgili. Otomasyon veya çeviri tek başına ihlal değil.
- Doorway abuse bakımından benzer coğrafi sorguları hedefleyip aynı hizmete yönlendiren, bağımsız faydası zayıf sayfalar özellikle incelenmeli. Aynı kliniğe yönelmek tek başına ihlal kanıtı değil.

Kaynaklar:

- https://status.search.google.com/incidents/WLxcJyC6jMWMfryxsKMc
- https://developers.google.com/search/docs/appearance/core-updates
- https://developers.google.com/search/docs/fundamentals/creating-helpful-content
- https://developers.google.com/search/docs/essentials/spam-policies#doorway-abuse
- https://developers.google.com/search/docs/essentials/spam-policies#scaled-content

## Kapsam ve yöntem

Canlı `/sitemap.xml` 1.245 URL içeriyor. Sitemap kapsamındaki tüm adresler GET isteğiyle kontrol edildi; HTTP sonucu, yönlendirme hedefi, robots meta, canonical, H1 sayısı ve hekim notu işareti kaydediliyor. Bu envanter taraması, her dilin insan tarafından tıbbi veya dilsel incelemesi değildir. Sitemap dışındaki tüm olası URL ve parametre kombinasyonları tarama kapsamında değildir.

Tarama sonucu: **1.245/1.245 URL HTTP 200** döndürdü; tamamında tek H1, kendisine işaret eden canonical ve indexlenebilir robots meta vardı. Sitemap URL'lerinde yönlendirme veya noindex bulunmadı. Bu sonuç gerçek Google indeks durumu veya içerik kalitesi onayı değildir. URL bazlı kayıt: `november-2026-url-inventory.csv`.

| Sayfa grubu | Canlı sitemap URL sayısı |
|---|---:|
| Tedavi detayları | 170 |
| Fiyat detayları | 170 |
| Paket detayları | 170 |
| Semt detayları | 221 |
| Ülke sayfaları | 38 |
| Rehber detayları | 255 |
| Diğer hub, kurumsal, klinik ve hekim sayfaları | 221 |
| Toplam | 1.245 |

Fiyat sayfalarının 68'inde, paket sayfalarının 51'inde özel `doctor-note` bloğu bulunmadı. Fiyat tarafında dolgu, temizlik, beyazlatma ve kompozit lamina; paket tarafında dolgu, temizlik ve beyazlatmanın 17 dil varyasyonu söz konusu. Bir bloğun olmaması tek başına thin içerik göstergesi değildir; bu sayfaların şablon ağırlığıyla birlikte değerlendirilmiştir. Toplam 119 fiyat/paket URL'si editoryal incelemede önceliklidir; hepsinin otomatik noindex yapılması önerilmez.

Canlı sayfa örnekleri ayrıca ana `<article>` içeriği açısından okundu. Kelime sayıları yalnızca içeriğin nerede yoğunlaştığını göstermek içindir; Google eşiği veya kalite puanı değildir. Fotoğraf, video, SSS ve diğer yararlı bölümler de ana içerik işlevi görebilir.

Kaynak kod ve yerel SQLite salt okunur incelendi. Yerel veritabanı canlı ortamla birebir aynı değil: örneğin İstanbul rehberinin ulaşım bilgisi canlıda yereldekinden daha güncel. Yerel kayıt sayıları canlı içerik sayısı olarak kullanılmamalı.

## Güçlü taraflar

- `/prices/dental-implants/`: canlı hekim notu kemik grefti, kemik kalitesi, yükleme ve bekleme süresinin teklife etkisini açıklıyor.
- `/packages/dental-implants/`: canlı hekim notu ilk geliş, uygunluk koşulları, geçici diş ve ikinci gelişin neden gerekebileceğini açıklıyor. Fiyat sayfasından farklı bir kullanıcı sorusuna cevap veriyor.
- Hekim adı, profil bağlantısı, klinik görselleri, hasta yorumları ve vaka medyası mevcut. Her birinin doğruluğu, izinleri ve hekim tarafından gerçekten incelendiği bu teknik taramayla bağımsız doğrulanmış değildir.
- Semt sayfaları kliniğin Şişli'de olduğunu ve diğer semtlere yakınlığını açıkça söylüyor; sahte şube iddiası görülmedi.
- Dil fallback'leri için noindex ve bazı landing-page türleri için içerik/teklif kontrolleri mevcut. Ancak bu koruma tüm route'larda aynı uygulanmıyor.

## Öncelikli bulgular

### 1. Bazı küçük tedavilerde üç URL'nin ayrı faydası zayıf — yüksek inceleme önceliği

Canlı örnek: `/treatments/teeth-cleaning/` ana article yaklaşık 38 kelime; bunun bir bölümü şehir linki. Fiyat karşılığı yaklaşık 179, paket karşılığı yaklaşık 256 kelime; bu iki sayfadaki metnin büyük bölümü başka tedavilerde de kullanılan teklifler ve kontrol listeleri. Üç canlı sayfa da indexlenebilir meta etiketi döndürüyor. Bu sayılara SSS, galeri ve diğer dış bölümler dahil değil.

Yerel veri ve şablonlar temizlik, dolgu ve beyazlatmanın fiyat/paket alanlarında hekim notu eksikliğine işaret ediyor. Canlı temizlik örneğinde bu eksiklik doğrulandı. Yerel kaynakta kompozit lamina için de fiyat etkenleri alanı boş; canlı İngilizce kompozit fiyat sayfasında da hekim notu bulunmadığı doğrulandı. Tüm dil varyasyonlarındaki blok varlığı envanterde kayıtlı.

Öneri: Her tedavi için fiyat, paket ve tedavi sayfalarının ayrı bir ihtiyacı karşılayıp karşılamadığını belirleyin. İçerik gerçekten ayrışmıyorsa güçlü tedavi sayfasında birleştirme düşünülebilir. Önce GSC sorgu ve dönüşüm verisini inceleyin; 301 yalnızca uygun karşılık varsa kullanılsın. Toplu ve otomatik noindex önerilmez.

### 2. “Cost” niyeti tam karşılanmıyor — yüksek inceleme önceliği

Fiyat şablonunda “çok uygun” ve “WhatsApp'tan fiyat isteyin” mesajları var; görünür sayısal fiyat aralığı veya hesaplanmış teklif örneği yok. İmplantta fiyatı değiştiren koşullar açıklanması olumlu; kullanıcı bütçe oluşturmak için yine de başka bir sonuca gitmek zorunda kalabilir.

Öneri: Klinik onaylarsa para birimi, tarih, birim, dahil/hariç kalemler ve koşulları açık bir aralık veya gerçek anonim teklif örneği ekleyin. Sabit fiyat verilemiyorsa değişkenleri ve olası ek işlemleri somutlaştırın. Gerçek olmayan fiyat veya vaka üretilmemeli. Sayısal fiyat yayınlamamak tek başına spam ihlali değildir.

### 3. Diğer şehirleri hedefleyen kısa rehberler — yüksek inceleme önceliği

`/guide/dental-clinic-ankara-or-istanbul/` canlıda Ankara'da klinik olmadığını dürüstçe belirtiyor. Ancak özel bölüm esas olarak fotoğraf gönderme, hafta sonu gelme ve teklif alma maddelerinden oluşuyor. Yerel kaynakta özgün rehber gövdesi 71 kelime; canlı article, ortak fiyat CTA'sı dahil yaklaşık 160 kelime. Antalya/Side/Alanya ve Bodrum/Marmaris/İzmir/Kuşadası rehberleri de benzer amaçla kaynak kod/veride bulunuyor.

Öneri: Gerçek ulaşım/konaklama planı, tedavi sonrası dönüş koşulları, yerelde tedaviyle karşılaştırmanın dayanakları veya gerçek hasta süreci gibi bağımsız fayda sağlayın. Bunlar sunulamıyorsa ilgili İstanbul rehberiyle birleştirmeyi değerlendirin. “Şubemiz yok” açıklaması olumlu; sayfanın yararlılığı ayrıca değerlendirilir.

### 4. 221 semt detayı ve 38 ülke URL'si — orta/yüksek inceleme önceliği

Sitemap'te 13 semtin 17 dilde 221 detay URL'si, ayrıca semt hub'ları var. Semt verisi mesafe, ulaşım hattı, çevredeki yerler ve tahmini sürelerle farklılaşıyor; bu gerçek bir fayda. Buna karşılık klinik tanıtımı, fiyat mesajları, hekim kanıtı ve galerinin büyük kısmı ortak.

Ülke sayfalarında kalkış şehirleri, yaklaşık uçuş süresi ve uzun uçuş açıklaması bulunuyor. Canlı Yeni Zelanda örneğinde işlem akışı ve teklif mesajları büyük ölçüde ortak. Ülkeye özgü vaka veya belge/evde takip süreci gibi somut farklılıklar zayıf.

Öneri: URL sayısına kota koymayın. GSC talebi, gerçek hizmet süreci ve özgün faydaya göre ülke/semt bazında karar verin. Boşluğu yalnızca ülke/semt adını değiştiren yeni paragraflarla doldurmayın. Birkaç dilde kontrol yapmak diğer bütün çevirileri doğrulamaz.

### 5. Gerçek deneyim kanıtı çoğunlukla site genelinde ortak — orta öncelik

`apps/seo/common.py` klinik görsellerini offset ile döndürüyor ve ortak yorum/video/vaka paketini getiriyor. `apps/core/templatetags/site_tags.py` içindeki `results_block` klinik vakalarını getiriyor; çağrıda sayfanın tedavisine göre filtre uygulanmıyor. Gerçek bir görselin farklı sayfalarda dönmesi sayfaya özgü yeni deneyim oluşturmaz; tekrar kullanılması da tek başına ihlal değildir.

Öneri: Tedaviye uygun vakayı öne çıkarın; gerçek başlangıç durumu, karar, uygulanan işlem, ziyaret sayısı ve takip sonucunu izinler çerçevesinde açıklayın. Genel galeri kliniği tanıtmak için kalabilir.

### 6. İndeksleme koruması sayfa türleri arasında tutarlı değil — orta öncelik

`apps/seo/views.py:treatment_price` index kararında tedavi çevirisinin fallback olup olmadığını kontrol ediyor; fiyat etkeni veya sayfaya özgü içerik varlığını kontrol etmiyor. `apps/seo/package_views.py:package_treatment` de esas olarak tedavi çevirisinin fallback durumuna bakıyor; bağlı LandingPage.noindex değerini index kararına taşımıyor. Semt ve ülke route'ları varsayılan index kullanıyor. Buna karşılık treatment-city route'u daha sıkı kontroller içeriyor.

Öneri: Her sayfa türü için editörün kontrol edebileceği yayın/indeks kararı oluşturun. Tek başına metin uzunluğu eşiği eklemeyin. Sitemap, robots meta ve hreflang aynı yayın kararını izlesin.

### 7. Garanti, malzeme ve editoryal güven — orta öncelik

Garanti rehberi genel “teknik problem olursa düzeltiriz” ifadesi kullanıyor. Yerel klinik-tedavi kayıtlarında marka ve garanti yılı alanları boş. Yerel çevirilerde `reviewed` durumuyla seed model etiketi birlikte bulunuyor; bu teknik durum insanın metni gerçekten okuduğunu kanıtlamaz.

Öneri: Klinik tarafından doğrulanmış malzeme bilgisi, garanti kapsamı/istisnaları, yol-konaklama masrafının kime ait olduğu ve yurt dışında sorun yaşandığında izlenecek süreci açıklayın. Gerçek hekim incelemesi ve anadil kontrolü yapıldığında tarih/kaynak kaydedin; yalnızca şema tarihini güncellemek inceleme sayılmaz.

## Önerilen uygulama sırası

1. GSC'de manuel işlemleri kontrol edin; 10 Kasım öncesi sorgu/sayfa/ülke/dil verisini sabitleyin. Bu incelemede GSC'ye erişilmedi.
2. Küçük tedavilerin fiyat/paket sayfaları ve diğer şehir rehberleri için URL bazlı güçlendirme/birleştirme kararı hazırlayın.
3. Gelir getiren implant, All-on-4, lamina, zirkonya gibi sayfalarda fiyat niyeti, ziyaret programı ve ilgili gerçek vaka bağlantısını geliştirin.
4. Semt/ülke URL'lerini talep ve bağımsız faydaya göre değerlendirin; ortak galeri veya tekrar eden sloganlarla içerik tamamlanmış sayılmasın.
5. Dil ve yayın durumlarını editoryal kalite kararlarıyla tutarlı hale getirin.

Dağıtım sırasında sırf core update başladı diye güçlü sayfaları silmeyin. Google kesin etki analizi için dağıtım bittikten sonra en az bir hafta bekleyip önceki dönemle karşılaştırmayı öneriyor. Teknik hata ve açık doğruluk sorunları bekletilmeden düzeltilebilir. Bu rapor herhangi bir canlı site değişikliği uygulamaz.
