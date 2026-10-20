# CoolScape AI

Kentsel serinlik ve su tahsis motoru: sıcak hava dalgası gününde kısıtlı soğutma suyunu 08:00–20:00 arasında saat saat park sulama, sisleme ve yol ıslatmaya dağıtan karar destek prototipi (MILP). Pilot: Antalya Muratpaşa–Kepez. Siemens Türkiye Climathon / COP31.

Öğrenci karar destek prototipidir; etki eğrileri Antalya'da sahada doğrulanmamıştır (2027 pilotu).

Canlı uygulama: https://cop31so-bjfwfgycfoqz7ltvuqiz5f.streamlit.app/

## Çalıştırma

```bash
pip install -r requirements.txt
python -m streamlit run coolscape_app.py
```

## Testler

```bash
pip install pytest
python -m pytest -q tests
```
Testlerde ağ çağrıları taklit edilir; sentetik hava yalnızca test içindir ve sonuç olarak raporlanmaz.

## Dosyalar

| Dosya | İçerik |
|---|---|
| `coolscape_app.py` | Streamlit uygulaması (v6) |
| `isi_yuzeyi_h3.csv` | Landsat 9 yüzey sıcaklığı (25.07.2025) ve Sentinel-2 NDVI (24.07.2025, kısmi), H3 res 9 |
| `nufus_h3.csv` | WorldPop 2025 toplam nüfus ve 65+ (ilçe oranıyla), H3 res 9 |
| `tesisler_osm.json` | OpenStreetMap okul/kreş, sağlık, içme suyu (Overpass dışa aktarımı) |
| `hava/openmeteo_*.json` | Kayıtlı günlerin ham Open-Meteo yanıtı; varsa API yerine okunur (429 sınırına karşı). Bkz. `hava/BENIOKU.md` |
| `parklar_osm.json` | İsteğe bağlı: OpenStreetMap park poligonları; yoksa canlı Overpass |
| `nufus_hazirla.py` | WorldPop → `nufus_h3.csv` |
| `ndvi_hazirla.py` | Sentinel-2 → `isi_yuzeyi_h3.csv` NDVI sütunu |
| `uyanik_tut.py`, `.github/workflows/uyanik_tut.yml` | Uygulamayı 3 saatte bir uyandırır |
| `CoolScape_ATIKSU_RAPORU.md` | Mevzuat, altyapı/finansman ve ekonomik etki analizi |

## Veri kaynakları ve atıf

- Hava: Open-Meteo (ERA5 arşivi ve tahmin), CC BY 4.0
- Yüzey sıcaklığı: USGS Landsat 9 Collection 2 Level-2
- NDVI: Copernicus Sentinel-2 (ESA)
- Nüfus: WorldPop (www.worldpop.org), Global2 R2025A, CC BY 4.0
- Tesisler ve parklar: © OpenStreetMap katkıcıları, ODbL
- Altlık: Esri World Imagery; OpenStreetMap
