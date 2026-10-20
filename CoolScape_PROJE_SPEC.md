# CoolScape AI · Proje Spec (tek kaynak)

Bu dosya önceki spec sürümlerinin yerine geçer. Çakışmada bu dosya geçerlidir. Son güncelleme: 20.10.2026 (v6.1).

## 1. Bağlantılar

| Ne | Adres |
|---|---|
| GitHub deposu | https://github.com/68wkf9wv55-netizen/cop31so |
| Canlı uygulama | https://cop31so-bjfwfgycfoqz7ltvuqiz5f.streamlit.app/ |
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
- Temsili kalanlar: hat kapasitesi, sulanan alan/pay, pompa, kişi/saat erişim, gölge etkinliği ve NDVI eşlemesi, g(saat) sınırları, sisleme alanı, yayılım ölçekleri, yıllık sulama günü ve mm.

## 6. Uygulama (v6)

- Bölümler: özet metrikler → erişim boşluğu (pilot + tüm OSM parkları) → harita (Uydu/CBS/3B) → müdahale noktaları → plan matrisi → operatör onay listesi → **Su kaynağı ve ekonomi** → **Nem kapısı kontrolü** → bütçe–serinlik eğrisi → Neden?
- Ekonomi bölümü (v6.1, `CoolScape_ATIKSU_RAPORU.md` bölüm 3.2 ile aynı formüller): maliyet esası (ASAT tarifesi 33,31 vekil / ASAT üretim maliyeti 60 vekil, 24.07.2024 / kuyu: kWh/m³ 0,417 vekil × elektrik fiyatı / elle), S1/S2, alan, mm/gün, gün, arıtma tesisi debisi (Lara 150.000 m³/gün), iskonto ve süre (örnek %10, 10 yıl), arıtılmış su maliyeti, pay, yatırım, işletme. Çıktı: yıllık m³, talep/AAT payı, yıllık TL, sıcak gün TL, ikame m³, başa baş fiyat, azami yatırım (üst sınır ve girdiyle; basit ve NBD=0), net tasarruf, geri dönüş, NBD. Sisleme içme suyuyla kalır.
- Nem kapısı bölümü: saatlik VPD, etki çarpanı, kapalı saatler; 0–1,6 kPa eşik duyarlılığı (düğmeyle).
- Tematik (matplotlib) harita kaldırıldı (erişilemeyen koddu).

**Repo ana dizini**
```text
coolscape_app.py
requirements.txt
isi_yuzeyi_h3.csv
tesisler_osm.json
nufus_h3.csv
parklar_osm.json            (isteğe bağlı; yoksa canlı Overpass)
ndvi_hazirla.py             (yerelde; rasterio, pyproj)
nufus_hazirla.py
tests/test_app.py, tests/parklar_test.json (sentetik fikstür)
CoolScape_ATIKSU_RAPORU.md   (CoolScape_MEVZUAT_EKONOMI.md'nin yerine)
haritalar/harita_1-3.png, .pdf   (v5 modeliyle üretildi)
uyanik_tut.py, .github/workflows/uyanik_tut.yml
README.md
```

**requirements.txt** (değişmedi)
```text
streamlit>=1.40
altair
pandas
numpy
pydeck
requests
h3>=4
pythermalcomfort>=2.10
metpy
pulp==2.9.0
matplotlib>=3.7
folium>=0.17
branca>=0.7
```

## 7. Sonuçlar

**Gerçek veri (havadan bağımsız; v6'da yeniden üretildi, değişmedi):**
- Yerleşim ~159 km²; 5 pilot parkın 400 m alanı bunun %1,0'ı.
- ~1,15 milyon kişinin %1,2'si bir pilot parka 5 dk yürüme mesafesinde.
- Yüksek + çok yüksek öncelikli 64 km²'nin %100'ü pilot parklara 400 m'den uzak.
- Tüm OSM parklarıyla erişim: canlıda üretilecek (BİLGİ YETERSİZ). Not: canlıda OSM parkları yüklenince öncelik haritası ve aday noktalar değişir.

**Canlı (gerçek Open-Meteo) rakamlar:** v5 rakamları alındı ama spec'e henüz girilmedi. v6 MRT ve sisleme değişikliği nedeniyle geçersiz; v6 yayına girince iki kayıtlı gün için yeniden alınacak.

## 8. Açık durum

- v6 dosyaları repoya yüklenecek; ardından Reboot app ve canlı rakamlar (iki gün) yeniden alınacak.
- `ndvi_hazirla.py` Sentinel-2 karolarıyla yerelde çalıştırılıp güncel `isi_yuzeyi_h3.csv` repoya yüklenecek.
- İsteğe bağlı: `parklar_osm.json` overpass-turbo'dan dışa aktarılıp repoya konursa park seti sabitlenir (yeniden üretilebilirlik).
- CBS haritaları (QGIS) v5 modeliyle; v6 ile yeniden üretilmeli.
- ASAT/belediyeye sorulacaklar: CoolScape_ATIKSU_RAPORU.md bölüm 4.
- 20.10.2026: repo dosyaları yerelde silindi; tüm paket yeniden üretildi. `uyanik_tut.py`, `.github/workflows/uyanik_tut.yml`, `README.md` yeniden yazıldı (özgünleri yoktu). `haritalar/` (QGIS PNG/PDF) ve `cbs_*.py`, `qgis_harita.py` paket dışında: BİLGİ YETERSİZ; haritalar klasörü yoksa uygulama CBS seçeneğini gizler.

## 9. Sonraki adımlar

| Öncelik | İş |
|---|---|
| 1 | v6 yayını ve canlı rakamlar |
| 2 | NDVI'nin tüm alan için üretimi |
| 3 | ASAT'tan park sulama kaynağı, tarife cetveli ve taban tüketim |
| 4 | Ek-7 7.1 sayısal sınırlarının asıl metinden okunması |

## 10. Açık sınırlar

Etki eğrisi Antalya'da sahada doğrulanmadı (2027 pilotu); sisleme 4,4 °C kuru Arizona ölçümü; hava tek noktadan, kıyı nemi ayrışmıyor; g(saat) ışınıma bağlı basit ölçek, yüzey enerji dengesi değil; gölge yalnızca NDVI olan yerde ve bina gölgesi yok; yayılım ölçekleri varsayım; +% kazanç kendi tabanımıza göre ve kırılgan; pilot parklarla arıtma tesisi arasındaki bağlantı BİLGİ YETERSİZ.
