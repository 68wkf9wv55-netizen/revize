# CoolScape AI · Proje Spec (tek kaynak)

Bu dosya önceki spec sürümlerinin yerine geçer. Çakışmada bu dosya geçerlidir. Son güncelleme: 20.10.2026 (v6.1).

## 1. Bağlantılar

| Ne | Adres |
|---|---|
| GitHub deposu | https://github.com/68wkf9wv55-netizen/cop31so |
| Canlı uygulama (güncel, 20.10.2026) | https://revize-nbbmv2gz99wbroa7qgcwni.streamlit.app/ |
| Canlı uygulama (önceki) | https://cop31so-bjfwfgycfoqz7ltvuqiz5f.streamlit.app/ |
| Geçersiz eski uygulama linki | `hpwfojfuks6ctcccqjwgxz.streamlit.app` (kullanma) |
| Streamlit ana dosya | `coolscape_app.py` |

## 2. Proje

- **Ne:** Sıcak hava dalgası gününde kısıtlı soğutma suyunu 08:00-20:00 arasında saat saat park sulama, sisleme ve yol ıslatmaya dağıtan karar destek prototipi (MILP).
- **Pilot:** Antalya Muratpaşa-Kepez.
- **Yarışma:** Siemens Türkiye Climathon; COP31 sergisi (Antalya, 9-20 Kasım 2026).
- **Ekip:** Sıla Hayranse Önal (İTÜ Meteoroloji, proje sahibi); Tulga destek. Danışman: Cihan Hoca.
- **Task 3 son teslim:** 21 Ekim 2026, 23:59 (PDF ayrı sohbette).
- **Sunum çerçevesi:** "öğrenci karar destek prototipi". "Kenti serinletiyoruz" iddiası yok.

## 3. Çalışma kuralları

- Yalnızca Türkçe; sade, işlevsel, minimal. Emoji yok. Dolgu cümlesi yok.
- Uydurma veri yasak. Her değer gerçek / vekil / temsili olarak etiketlenir.
- Emin olunmayan bilgi: "BİLGİ YETERSİZ".
- Sentetik havayla üretilen yüzdeler sunulmaz (sentetik hava yalnızca `tests/` içinde).
- Kullanıcı e-postası hiçbir yere gönderilmez.
- Teslimden önce `pytest tests` (AppTest dahil) ve görsel doğrulama. Değişen dosya tam verilir.
- Sandbox Open-Meteo, Overpass, WorldPop, Copernicus, harita karoları, Leaflet/deck.gl CDN'i ve Streamlit sitesine erişemez; testlerde ağ taklit edilir, harita iframe'i sandbox'ta boş görünür.

## 4. Veri

| Veri | Kaynak | Durum |
|---|---|---|
| Hava | Open-Meteo (ERA5 arşivi, tahmin), tek nokta (36,89; 30,71) | Gerçek; yalnızca canlıda. Kıyı-iç nem farkı yok |
| Yüzey sıcaklığı | Landsat 9 C2 L2, 25.07.2025, 178/035 + 178/034 | Gerçek. Kara LST min 36,1 / medyan 49,7 / maks 57,8 °C; geçiş ~11:20 |
| NDVI | Sentinel-2, 24.07.2025 | Gerçek ama **kısmi**: 165/1.964 altıgen (kara altıgenlerinin %9,8'i), yalnızca kuzeydoğu köşe (enlem ≥36,935, boylam ≥30,752). Pilot parkların hiçbirinde yok. `ndvi_hazirla.py` ile tüm alan yeniden üretilecek |
| Tesisler | OSM, 318 (230 okul/kreş, 64 sağlık, 24 içme suyu; huzurevi 0) | Gerçek |
| Parklar | 5 pilot (koordinat gerçek, işletme değerleri temsili) + OSM `leisure=park` poligonları (`parklar_osm.json` ya da canlı Overpass) | OSM alanı gerçek; sulanan pay %60, hat 10 m³/saat/ha (≤20), pompa 1,0 temsili |
| Nüfus | WorldPop 2025, 100 m, R2025A; `nufus_hazirla.py` → `nufus_h3.csv` | Gerçek: 1.600 altıgen, ~1.176.469 kişi; kara altıgenlerinin %7,9'unda nüfus kaydı yok (0 sayılır) |
| 65+ | Toplam × ilçe oranı (%6,8 Kepez / %9,8 Konyaaltı / %11,2 Muratpaşa) | Vekil |
| Kırılganlık | OSM okul/sağlık/huzurevi, 400 m | Vekil |
| Su tarifesi | ASAT Haziran 2026, Resmi Daireler ve Belediyeler, 33,31 TL/m³ KDV hariç, kademesiz | Gerçek tarife; parklara uygulandığı doğrulanmadı → uygulamada vekil |

**Seçenek A:** Toplam nüfus kullanılır; 65+ ölçütü "65+ sayısı (ilçe oranıyla)" diye etiketlenir.

## 5. Model sabitleri (v6; değişiklikler 19.10.2026'da onaylandı)

- Öncelik = max(UTCI - 32, 0) x kişi x (1 + w x kırılganlık). MILP Σ öncelik x UTCI düşüşünü en çoklar. (değişmedi)
- Öncelik ağırlıkları: ısı 0,40 / 65+ 0,25 / park uzaklığı 0,20 / tesis 0,15. (değişmedi; park uzaklığı artık tüm parkların kenarına göre)
- **MRT = T + (1 − 0,8 × örtü) × ΔMRT_güneş (SolarCal) + 0,5 × LST farkı × g(saat).** (B1 + B3)
  - örtü = clip((NDVI − 0,2) / 0,4; 0; 1); NDVI yoksa 0. Eşleme ve 0,8 etkinlik temsili.
  - g(saat) = K↓(saat) / K↓(12:00, yani 11–12 ortalaması), [0,3; 1,3] aralığında. Sınırlar temsili.
- Soğutma eğrisi: E = E_REF x min(VPD/2,5; 1) x (1 - e^(-x/x0)); E_REF 1,0 °C (band 0,5-2,0). Sisleme 4,4 °C x VPD faktörü. (değişmedi)
- **Sisleme istasyonu:** 300 m² (3 × 100 m² Vanos birimi), 0,36 m³/saat, erişim 40 kişi/100 m². Yayılım çekirdeği: alan içinde tam etki, dışında 10 m ölçekle azalır, +40 m'de sıfır. (B4; önceki: 100 m², 0,12 m³/saat, noktasal 15/50 m)
- **Yayılım çekirdeği (tüm yöntemler):** yarıçap R = √(alan/π) içinde tam; dışında e^(−(d−R)/ölçek). Ölçek/kesme: park 150/500 m, ıslatma 60/200 m, sisleme 10/40 m. Temsili.
- Kısıtlar: bütçe, hat kapasitesi, min doz, nem kapısı (varsayılan 0,8 kPa, değişmedi), kırılgan pay, park kesme 18:00, günlük 6 mm.
- Yerleşim maskesi ≥50 kişi/altıgen; kıyı karışık piksel maskesi; adaylar 4 sisleme + 3 ıslatma; parka (kenar) uzaklık 600–3.000 m.
- Plana alınan parklar: 5 pilot + 800 m içindeki (nüfus × öncelik) toplamı en yüksek 10 OSM parkı (≥0,5 ha; ayarlanabilir 0–30).
- **v7 (20.10.2026, onaylandı: "hepsini hemen yapalım"):**
  - Kırılganlık eşiği gruba göre: parklar kendi medyanıyla, sisleme/ıslatma adayları kendi medyanıyla (önceden tüm noktaların medyanı; kırılganların hepsi adaydı).
  - Park MRT'sinde yüzey farkı park İÇİ altıgen(ler)den (k_iç = round(yarıçap / altıgen aralığı)); boşsa (kıyı/su maskesi) çevre halkası. Karaalioğlu ve Atatürk Parkı'nda iç altıgen maskeli → çevre kullanılır.
  - Termal atalet 0,5 (temsili): park ve ıslatmada doğrudan etkinin 0,5'i sonraki saate taşınır; MILP amacında segment ağırlığı = öncelik(t) + 0,5 × öncelik(t+1). Sislemede taşınma yok. Arayüzde 0–0,8.
  - Sisleme istasyonu günde en çok 8 saat (temsili; arayüzde 2–13).
  - Değerlendirme: tabanlar (gece = 0, eşit park, aynı yöntemlerle eşit işletim, en sıcak önce, CoolScape yalnız park, CoolScape, bütçe +%50); kazanç ayrışımı zamanlama (yalnız park / eşit park), çeşitlendirme (CoolScape / yalnız park), bütçe (+%50 / CoolScape); tek-seferde-bir duyarlılık (10 parametre, 20 MILP).
- Temsili kalanlar: hat kapasitesi, sulanan alan/pay, pompa, kişi/saat erişim, gölge etkinliği ve NDVI eşlemesi, g(saat) sınırları, sisleme alanı, yayılım ölçekleri, yıllık sulama günü ve mm.

## 6. Uygulama (v7)

- v7 düzeni: başlık → kaynak satırı → **erişim boşluğu (ana mesaj, gerçek veri)** → sekmeler: Özet (zamanlama / çeşitlendirme / bütçe +%50 / kişi·°C·saat temsili; kullanılan su, kırılgan su, toplam; senaryo karşılaştırma tablosu; 2025 yazı sıcak gün sayısı) · Harita ve plan (harita, müdahale noktaları, plan matrisi, operatör listesi) · Ekonomi · Duyarlılık ve karşılaştırma (tornado, bütçe eğrisi, nem kapısı) · Yöntem ve sınırlar (veri güvenilirliği tablosu, Landsat park içi/çevre LST, 2027 pilot tasarımı, Neden?).
- Gelişmiş ayarlara eklenenler: termal atalet, sisleme günlük saat, "OSM parklarını canlı indir (Overpass)" (varsayılan kapalı; `parklar_osm.json` varsa o kullanılır; tekrarlanabilirlik için).
- Yaz klimatolojisi: `hava/openmeteo_yaz_2025.json` (01.06–30.09.2025, gerçek ERA5) varsa her gün 08–20 en yüksek kent UTCI'si; ≥32/38/46 °C gün sayıları. Ekonomide "Yıllık hacim esası": temsili (mm × gün) ya da gerçek sıcak gün sayısı × bugünkü plan (yalnız soğutma suyu). Dosya yoksa BİLGİ YETERSİZ.
- v6 bölümleri (içerik korunuyor): özet metrikler → erişim boşluğu (pilot + tüm OSM parkları) → harita (Uydu/CBS/3B) → müdahale noktaları → plan matrisi → operatör onay listesi → **Su kaynağı ve ekonomi** → **Nem kapısı kontrolü** → bütçe–serinlik eğrisi → Neden?
- Ekonomi bölümü (v6.1, `Atiksu_Geri_Kazanim_Fizibilite_Raporu.md` bölüm 3.2 ile aynı formüller): maliyet esası (ASAT tarifesi 33,31 vekil / ASAT üretim maliyeti 60 vekil, 24.07.2024 / kuyu: kWh/m³ 0,417 vekil × elektrik fiyatı / elle), S1/S2, alan, mm/gün, gün, arıtma tesisi debisi (Lara 150.000 m³/gün), iskonto ve süre (örnek %10, 10 yıl), arıtılmış su maliyeti, pay, yatırım, işletme. Çıktı: yıllık m³, talep/AAT payı, yıllık TL, sıcak gün TL, ikame m³, başa baş fiyat, azami yatırım (üst sınır ve girdiyle; basit ve NBD=0), net tasarruf, geri dönüş, NBD. Sisleme içme suyuyla kalır. v6.2 (20.10.2026): arıtılmış su maliyeti ve yatırım literatür vekiliyle hesaplanır (varsayılan): c_r = (0,14 arıtma işletmesi + 0,05 pompaj) €/m³ × 55,61 TL/€ = 10,57 TL/m³ (Exposito vd. 2024; Pistocchi vd. 2017); yatırım = 0,60 €/(m³/yıl) + 5 €/m³ depo (1 günlük talep), boru hariç. Alternatif: İSKİ 2026 "Geri Dönüşüm Suyu" 7,81 TL/m³. Yeni satır: boru hattı için kalan pay = I_max(NBD=0) − yatırım. Pilot varsayılanında: net tasarruf 1.473.818 TL/yıl, geri dönüş 1,5 yıl (boru hariç), boru için kalan pay 6.793.757 TL (hepsi vekil/temsili girdilerden).
- Nem kapısı bölümü: saatlik VPD, etki çarpanı, kapalı saatler; 0–1,6 kPa eşik duyarlılığı (düğmeyle).
- Tematik (matplotlib) harita kaldırıldı (erişilemeyen koddu).
- Hava (v6.1): kayıtlı günlerde önce `hava/openmeteo_YYYY-AA-GG.json` (ham Open-Meteo yanıtı, gerçek) okunur; yoksa API (429/5xx'te 3 deneme, disk önbelleği). Hata durumunda arşiv bağlantısı gösterilir ve JSON/CSV yüklenebilir. Neden: 20.10.2026'da Streamlit Cloud'da Open-Meteo 429 Too Many Requests.

**Repo ana dizini**
```text
coolscape_app.py
requirements.txt
isi_yuzeyi_h3.csv
tesisler_osm.json
nufus_h3.csv
parklar_osm.json            (isteğe bağlı; yoksa 5 pilot park, canlı Overpass seçeneği)
hava/openmeteo_*.json, hava/openmeteo_yaz_2025.json (gerçek Open-Meteo; kullanıcı indirir)
ndvi_hazirla.py             (yerelde; rasterio, pyproj)
nufus_hazirla.py
tests/test_app.py, tests/parklar_test.json (sentetik fikstür)
Atiksu_Geri_Kazanim_Fizibilite_Raporu.md   (CoolScape_MEVZUAT_EKONOMI.md'nin yerine)
haritalar/harita_1-3.png, .pdf   (v5 modeliyle üretildi)
uyanik_tut.py, .github/workflows/uyanik_tut.yml
README.md
```

**requirements.txt** (v7: test edilen sürümler üst sınır)
```text
# Üst sınırlar test edilen sürümlerdir (Python 3.13, 20.10.2026); test edilmemiş yeni sürüm kurulmaz.
streamlit>=1.40,<=1.66.0
altair>=5,<=6.3.0
pandas>=2.2,<=3.0.5
numpy>=1.26,<=2.5.3
pydeck>=0.9,<=0.9.3
requests>=2.31,<=2.34.2
h3>=4,<=4.5.0
pythermalcomfort>=2.10,<=4.6.2
metpy>=1.6,<=1.7.1
pulp==2.9.0
matplotlib>=3.7,<=3.11.2
folium>=0.17,<=0.20.0
branca>=0.7,<=0.8.2
```

## 7. Sonuçlar

**Gerçek veri (havadan bağımsız; v6'da yeniden üretildi, değişmedi):**
- Yerleşim ~159 km²; 5 pilot parkın 400 m alanı bunun %1,0'ı.
- ~1,15 milyon kişinin %1,2'si bir pilot parka 5 dk yürüme mesafesinde.
- Yüksek + çok yüksek öncelikli 64 km²'nin %100'ü pilot parklara 400 m'den uzak.
- Tüm OSM parklarıyla erişim: canlıda üretilecek (BİLGİ YETERSİZ). Not: canlıda OSM parkları yüklenince öncelik haritası ve aday noktalar değişir.

**Canlı (gerçek Open-Meteo) rakamlar:** v5 rakamları alındı ama spec'e henüz girilmedi. v6 MRT ve sisleme değişikliği nedeniyle geçersiz; v6 yayına girince iki kayıtlı gün için yeniden alınacak.

## 8. Açık durum

- v7 (20.10.2026): 21 test geçti (AppTest dahil); görsel kontrol sentetik TEST havasıyla yapıldı (sandbox Open-Meteo, Overpass, harita karoları ve Streamlit sitesine erişemez; uydu haritası karoları sandboxta yüklenmez). Yayın sonrası canlı rakamlar gerçek Open-Meteo ile yeniden alınmalı.
- Kullanıcıya bağlı: `hava/openmeteo_yaz_2025.json` (bağlantı hava/BENIOKU.md), NDVI karoları, `parklar_osm.json`, belediye verisi (sulama takvimi, kaynak, arazöz maliyeti), canlı rakamlar.
- v6 dosyaları repoya yüklenecek; ardından Reboot app ve canlı rakamlar (iki gün) yeniden alınacak.
- `ndvi_hazirla.py` Sentinel-2 karolarıyla yerelde çalıştırılıp güncel `isi_yuzeyi_h3.csv` repoya yüklenecek.
- İsteğe bağlı: `parklar_osm.json` overpass-turbo'dan dışa aktarılıp repoya konursa park seti sabitlenir (yeniden üretilebilirlik).
- CBS haritaları (QGIS) v5 modeliyle; v6 ile yeniden üretilmeli.
- ASAT/belediyeye sorulacaklar: Atiksu_Geri_Kazanim_Fizibilite_Raporu.md bölüm 4.
- 20.10.2026: repo dosyaları yerelde silindi; tüm paket yeniden üretildi. `uyanik_tut.py`, `.github/workflows/uyanik_tut.yml`, `README.md` yeniden yazıldı (özgünleri yoktu). `haritalar/` (QGIS PNG/PDF) ve `cbs_*.py`, `qgis_harita.py` paket dışında: BİLGİ YETERSİZ; haritalar klasörü yoksa uygulama CBS seçeneğini gizler.

## 9. Sonraki adımlar

| Öncelik | İş |
|---|---|
| 1 | v6 yayını ve canlı rakamlar |
| 2 | NDVI'nin tüm alan için üretimi |
| 3 | ASAT'tan park sulama kaynağı, tarife cetveli ve taban tüketim |
| 4 | Ek-7 7.1 sayısal sınırlarının asıl metinden okunması |
| 4b | v6.3 (20.10.2026) yapıldı: başlık kartı 'Zamanlama ve yer seçimi kazancı (yalnız park)', yöntem çeşitlendirme dahil kazanç alt satırda; kırılgan sayılan noktaların bileşimi gösteriliyor; aday noktalara en yakın adlı OSM tesisi (konum); arazöz sefer sayısı (18 m³ tanker, vekil) ve sefer maliyeti girdisi; arıtılmış su mevcut kaynaktan pahalıysa uyarı; harita kesirli zoom. |
| 4c | v7'de yapıldı (a, b, c). (d) yapılmadı: ikinci Open-Meteo noktası ERA5 0,25° ızgarasında aynı/komşu hücreye düşer, kıyı–iç farkı göstermez; MGM istasyonu gerekir. Önceki öneri metni: (a) kırılganlık eşiği parklar ve adaylar için ayrı hesaplanmalı; şu an kırılgan sayılan noktaların hepsi aday (4 sisleme + 2 ıslatma), hiçbir park kırılgan değil, %40 kırılgan pay kuralı suyu adaylara itiyor; (b) sulamanın 1–2 saatlik termal ataleti; (c) sisleme için saatlik kullanım/kişi varlığı kısıtı (şu an her saat açık); (d) kıyı için ikinci Open-Meteo noktası. |
| 5 | Web portalı (seçenek B, karar 20.10.2026): Task 3 sonrası, 22 Ekim'den itibaren; COP31 sergisine (9 Kasım) hazır. Koyu tam ekran harita, 08–20 saat çizelgesi, imleçle değer okuma, yan paneller (kontroller/tanı), tanıtım turu. Python modeli senaryoları gerçek Open-Meteo verisiyle önceden hesaplar (2 gün × bütçe × öncelik ön ayarı); canlı MILP Streamlit'te kalır. Görsel düzen örnek alınır; başka markanın logo/renk/adı kullanılmaz. Ön koşul: hava/openmeteo_*.json |

## 10. Açık sınırlar

Termal atalet (0,5) ve sisleme saat sınırı (8) temsili; modül bölme (tek dosya → paket) ve portal Task 3 sonrasına ertelendi. Etki eğrisi Antalya'da sahada doğrulanmadı (2027 pilotu); sisleme 4,4 °C kuru Arizona ölçümü; hava tek noktadan, kıyı nemi ayrışmıyor; g(saat) ışınıma bağlı basit ölçek, yüzey enerji dengesi değil; gölge yalnızca NDVI olan yerde ve bina gölgesi yok; yayılım ölçekleri varsayım; +% kazanç kendi tabanımıza göre ve kırılgan; pilot parklarla arıtma tesisi arasındaki bağlantı BİLGİ YETERSİZ.
