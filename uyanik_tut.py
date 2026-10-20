"""
CoolScape AI – Streamlit Community Cloud uygulamasını uyanık tutar.
Uygulamayı gerçek bir tarayıcıyla açar; uyku ekranı varsa "uyandır" düğmesine basar ve sayfanın yüklenmesini bekler.
GitHub Actions ile 3 saatte bir çalışır (.github/workflows/uyanik_tut.yml).
Not: GitHub, 60 gün etkinlik olmayan depolarda zamanlanmış görevleri durdurabilir.
"""

import sys

from playwright.sync_api import sync_playwright

UYGULAMA_URL = "https://cop31so-bjfwfgycfoqz7ltvuqiz5f.streamlit.app/"
UYANDIR_METINLERI = ["Yes, get this app back up!", "get this app back up"]


def main():
    with sync_playwright() as p:
        tarayici = p.chromium.launch()
        sayfa = tarayici.new_page()
        sayfa.goto(UYGULAMA_URL, timeout=120_000)
        sayfa.wait_for_timeout(8_000)
        for metin in UYANDIR_METINLERI:
            dugme = sayfa.get_by_text(metin, exact=False)
            if dugme.count():
                print("Uyku ekranı bulundu; uyandırılıyor.")
                dugme.first.click()
                sayfa.wait_for_timeout(60_000)
                break
        else:
            print("Uygulama uyanık.")
        tarayici.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
