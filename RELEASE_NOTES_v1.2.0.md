# 🚀 KM Layout Tables Studio — Sürüm v1.2.0 (İlk Resmi Yayın)

<p align="center">
  <b>Rusya GOST Standartlarında Çelik Konstrüksiyon (КМ) CAD Tablo ve Pafta Stüdyosu</b><br>
  <i>AutoCAD gerektirmeyen bağımsız 1:1 DXF üretimi ve canlı 2D vektörel CAD tuvali.</i>
</p>

---

## 🌟 Öne Çıkan Özellikler ve Standartlar

### 📐 1. Rusya GOST Standartlarına %100 Kesin Uyum
- **ГОСТ 21.502-2007 — Eleman Listesi (Ведомость элементов):**
  - Standart 7 sütun: Marka (`Марка`), Kesit Eskizi (`Эскиз`), Profil/Bileşen (`Сечение / Состав`), Eksenel Kuvvet (`N, кН` / `A, кН`), Eğilme Momenti (`M, кН·м`), Çelik Kalitesi (`Сталь`), Notlar (`Примечание`).
  - Dahili profil eskiz geometrileri (I-Profil, Kutu Profil, Yuvarlak Boru, Şveller, Levha vb.).
- **ГОСТ Р 21.101-2020 Form 3 — Ana Başlık Bloğu (Title Block / Form 3 Antet):**
  - $185 \times 55\text{ mm}$ Form 3 ana antet; pafta boyutu ve yönü ne olursa olsun **daima sağ alt köşeye kilitlenir**.
  - Kurumsal şirket logosu (PNG, JPG, BMP) ekleme ve antet içinde otomatik ölçekleme desteği.
  - WYSIWYG görsel veri giriş şablonu (Revizyon tablosu, 6 kişilik mühendis imza kadrosu, doküman kodu, proje adı).
- **ГОСТ Р 21.101-2020 Form 2 — Referans ve Ek Dokümanlar Tablosu:**
  - $185\text{ mm}$ genişlikte antet üstüne veya paftaya kilitlenen Form 2 tablosu.
  - **14 temel KM çelik standardı** içeren kalıcı, çok dilli (RU / TR / EN) ve CRUD destekli Standartlar Kütüphanesi.
- **ГОСТ Р 21.101-2020 Form 2 — Ana Çizim Takımları Listesi (Ведомость основных комплектов):**
  - $185\text{ mm}$ genişlikte takım listesi ve düzenleyicisi.
- **ГОСТ Р 21.101-2020 Form 1 — Çalışma Çizimleri Pafta Listesi (Ведомость рабочих чертежей):**
  - $185\text{ mm}$ genişlikte pafta listesi ve düzenleyicisi.
- **ГОСТ 2.104-2006 Sol Cilt Kenarı Ek Tabloları:**
  - $20\text{ mm}$ sol ciltleme kenarında Form 1a/2a İnventar Tablosu (`Инв. № подл.`, `Подп. и дата`, `Взам. инв. №`) ve 90° döndürülmüş onay damgası (`Согласовано`).
- **ГОСТ 2.301-68 Pafta Formatı Alt Etiketi:**
  - Pafta alt çerçevesi dışında yer alan dinamik format göstergesi (`Формат А3А`, `Формат А1А` vb.).

---

### 🖥️ 2. Modern Linear & Notion SaaS Tarzı Masaüstü Arayüzü (UI v2)
- **Obsidian Dark Teması:** Göz yormayan koyu renk paleti, 1px ultra-ince kenarlıklar ve mor vurgular.
- **Gelişmiş Hücre Düzenleyici:** Opak zeminli `SolidItemDelegate` ile metin çakışmalarını engelleyen düzenleme, Excel/Google Sheets uyumlu TSV kopyala-yapıştır (`Ctrl+C`, `Ctrl+V`).
- **Hızlı Komut Paleti:** Klavyeden `Ctrl+K` veya `Ctrl+T` ile anında arama ve hızlı tablo değiştirici (Quick Switcher).
- **Dinamik Çift Dilli Başlıklar:** Üstte standart Rusça GOST terimi, altta seçilen dildeki karşılığı (TR, EN, RU tek tıkla dil değiştirme).
- **Bağımsız Pafta Hafızası:** Her tablo için ayrı sayfa boyutu (A4, A3, A2, A1, A0), yönelim (Yatay / Dikey) ve pafta içi yerleşim (Antet Üstü, Sol Üst, Sağ Üst, Pafta Ortası).

---

### ⚡ 3. Canlı 2D Vektörel CAD Tuvali & Bağımsız 1:1 DXF Motoru
- **AutoCAD Lisansı Gerektirmez:** `ezdxf R2010` çekirdeği ile bağımsız çalışır.
- **Kesin 1:1 Metrik Ölçek:** $1\text{ CAD Birimi} = 1.0\text{ mm}$ (`$INSUNITS = 4`).
- **Katmanlı (Layered) Yapı:** `KM_TABLO_CERCEVE`, `KM_TABLO_IZGARA`, `KM_TABLO_METIN`, `KM_TABLO_ESKIZ`, `KM_TABLO_ANTET`.
- **%100 WYSIWYG Uyum:** Canlı CAD ekranında ne görünüyorsa DXF çıktısında milimetrik olarak birebir aynısı elde edilir. Otomatik kelime sarımı (word-wrap) ve dinamik font ölçekleme ile hücre dışına taşma yaşanmaz.
- **Floating Glass HUD:** Tuval üzerinde yüzen cam araç çubuğu (Ekrana Sığdır, %100 Görünüm, Koordinat Takibi).

---

## 📦 İndirme ve Kurulum (Windows x64)

1. Aşağıdaki **Assets** bölümünden `KM-Layout-Tables-v1.2.0-win64.zip` arşivini indirin.
2. Arşivi bilgisayarınızda istediğiniz bir klasöre çıkartın.
3. `KM-Layout-Tables.exe` dosyasına çift tıklayarak uygulamayı başlatın.
   *(Python veya ek yazılım kurulumu gerektirmez, doğrudan çalışır).*

---

## 🔑 Doğrulama (Checksums)

İndirilen dosyanın bütünlüğünü doğrulamak için `checksums.txt` dosyasındaki SHA-256 değerini kontrol edebilirsiniz.
