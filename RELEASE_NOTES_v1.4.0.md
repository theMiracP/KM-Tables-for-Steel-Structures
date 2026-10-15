# 🚀 KM Layout Tables Studio — Sürüm v1.4.0

<p align="center">
  <b>Rusya GOST Standartlarında Çelik Konstrüksiyon (КМ) CAD Tablo ve Pafta Stüdyosu</b><br>
  <i>AutoCAD gerektirmeyen bağımsız 1:1 DXF ve PDF üretimi, ГОСТ Profil Sortament Kütüphanesi, Form 9 / Form 12 modülleri, Word (.docx) aktarımı ve proje yönetimi (.kmproj).</i>
</p>

---

## 🌟 Sürüm v1.4.0 ile Gelen Yenilikler ve Geliştirmeler

Bu sürüm, KM Layout Tables Studio için bugüne kadar yayınlanan en kapsamlı güncellemedir. Rus çelik profil kütüphanesi entegrasyonu, 1:1 vektörel PDF motoru, resmi ГОСТ Form 9 ve Form 12 modülleri, Microsoft Word aktarımı, proje kayıt formatı (.kmproj), geri al/ileri al sistemi ve çok sayıda mimari iyileştirme stüdyoya kazandırılmıştır.

---

### 📚 1. ГОСТ Rus Çelik Sortament / Profil Seçici Kütüphanesi (GostProfileDatabase)
- **Kapsamlı Profil Kataloğu:**
  - СТО АСЧМ 20-93 ve ГОСТ 26020-83 (I-Kirişler / Двутавры: Б, Ш, К serileri),
  - ГОСТ 8240-97 (U-Profiller / Швеллеры: П ve У serileri),
  - ГОСТ 30245-2003 (Kare ve Dikdörtgen Kutu Profiller / Гнутосварные профили),
  - ГОСТ 10704-91 (Yuvarlak Borular / Электросварные трубы),
  - ГОСТ 8509-93 & ГОСТ 8510-86 (Eşit ve Çeşitkenar Köşebentler / Уголки).
- **Gelişmiş Profil Seçici Diyaloğu (`ProfilePickerDialog`):**
  - Kategoriye göre filtreleme, anlık dinamik arama, temizleme butonu ve metrik özellikler (ağırlık, boyutlar, standart çelik kalitesi).
- **Kullanıcı Tanımlı Özel Profil Ekleme:**
  - Standart dışı veya özel profilleri JSON formatında (`custom_profiles.json`) kalıcı olarak tanımlama imkanı.
- **Dinamik Kaynaklı Kesit Düzenleyicisi (`WeldedSectionDialog`):**
  - Kaynaklı I-kirişler, kutu profiller ve haç kesitler için başlık/gövde et kalınlıkları ile parametrik kesit oluşturma.
- **Otomatik Kesit - Eskiz Eşlemesi:**
  - Profil seçildiğinde Eleman Listesi tablosundaki eskiz geometrisi (`I`, `[`, `Гн. □`, `○`, `L`) ve DXF/CAD sembolleri anında otomatik güncellenir.

---

### 📄 2. 1:1 Vektörel PDF Dışa Aktarma Motoru (`PdfExporter`)
- **Yüksek Çözünürlüklü Vektörel Çıktı:**
  - 300 DPI çözünürlükte, AutoCAD hassasiyetinde 1:1 ölçekli ($1\text{ CAD Birimi} = 1\text{ mm}$) vektörel PDF üretimi (`QPdfWriter`).
- **Tekli ve Çoklu Pafta Desteği:**
  - Tekli tablolardan Form 3 antetli paftalar veya çok sayfalı (Multi-Sheet) çizim takımları için sayfa sayfa kusursuz PDF üretimi.
- **Kiril Metin & Geometri Desteği:**
  - Aranabilir UTF-8 Kiril metinler, GOST çizgi kalınlıkları ve katman renkleri korunarak aktarılır.
- **Üst Gezinme Çubuğu Entegrasyonu:**
  - Üst barda yer alan "PDF Dışa Aktar" butonu ile tek tıkla doğrudan PDF üretimi.

---

### 📑 3. ГОСТ Р 21.101-2020 Form 9 Değişiklik İzni Modülü (Разрешение на изменения)
- **Resmi Mühendislik Değişiklik Formu:**
  - ГОСТ Р 21.101-2020 standartlarına tam uyumlu Form 9 tablosu ve veri editörü.
- **Değişiklik Neden Kodları (Таблица Л.1):**
  - Standart neden kodları (1 - Hata, 2 - Sipariş değişikliği, 3 - İyileştirme vb.) için çok dilli açılır menü ve hızlı atama butonları.
- **Sorumlu İmzacı Kadrosu:**
  - Değişikliği hazırlayan, kontrol eden, norm kontrolü yapan ve onaylayan yetkililer için çok dilli rol seçimi ve tarih alanları.

---

### 📘 4. ГОСТ Р 21.101-2020 Form 12 Başlık Sayfası (Титульный лист) & Word (.docx) Aktarımı
- **Resmi Başlık Sayfası Modülü:**
  - Form 12 / Приложение С standartlarında A4 dikey başlık sayfası oluşturucu.
- **Microsoft Word (.docx) Motoru (`DocxExporter`):**
  - Başlık sayfasını kenar boşlukları (Sol 20 mm, Üst/Sağ/Alt 5 mm), resmi onay grifi (`УТВЕРЖДАЮ / СОГЛАСОВАНО`), proje künyesi ve sorumlu imza tablosuyla tam uyumlu Word belgesi olarak dışa aktarma.
- **Ergonomik Editör:**
  - `QScrollArea` tabanlı kart mimarisi, logo yükleme, onay kutuları ve imzacı yönetim araçları.

---

### 💾 5. Yerel Proje Dosya Formatı (.kmproj) & Proje Yönetimi (`ProjectManager`)
- **Tüm Çalışmayı Tek Dosyada Saklama:**
  - Aktif tüm tabloların verilerini, Form 3 antet bilgilerini, pafta boyutlarını ve AutoCAD ayarlarını içeren tek bir `.kmproj` proje dosyası formatı.
- **Proje Açma ve Farklı Kaydetme:**
  - Üst bar üzerinden "Projeyi Aç", "Projeyi Kaydet" ve "Farklı Kaydet" aksiyonları.

---

### ↩️ 6. Geri Al / İleri Al Sistemi (`UndoManager`)
- **Geri Alma ve İleri Alma:**
  - Tablo veri girişlerinde yapılan değişiklikleri hafızada tutarak `Ctrl+Z` (Geri Al) ve `Ctrl+Y` (İleri Al) kısayolları ile geri alma imkanı.

---

### 🔄 7. Çoklu Pafta ve Tekli Pafta İki Yönlü Geçiş
- **HUD Çoklu Pafta Toggle:**
  - Canlı CAD tuvali üzerindeki Floating Glass HUD barında tekli ve çoklu pafta modları arasında anında geçiş.
  - Pafta modları arası geçişte veri senkronizasyonu ve görünümün korunması.

---

### 🎯 8. Ortak Antet (Form 3) Verilerinin Tam Senkronizasyonu
- **Merkezi Antet Havuzu:**
  - Form 3 antetinde girilen proje adı, pafta adı, kuruluş adı ve yetkili isimleri tüm çizim tabloları ve paftalar arasında otomatik olarak paylaşılır ve eşzamanlanır.

---

### 🛡️ 9. Hücre İçi Düzenlemede Çift Metin (Ghosting) Engellemesi (`SolidItemDelegate`)
- Tablolarda hücre düzenlenirken alttaki metnin görünmesini %100 engelleyen opak arka plan ve otomatik gizleme mekanizması.

---

### 🌐 10. Çok Dilli (i18n) Geliştirmeleri
- Türkçe, Rusça ve İngilizce dilleri arasında tam metin uyumu.
- Form 9 değişiklik kodları ve sorumlu imzacı rolleri için dinamik üç dilli çeviri sistemi.

---

## 📦 İndirme Seçenekleri (Windows x64)

İhtiyacınıza göre iki farklı dağıtım seçeneğinden birini tercih edebilirsiniz:

- **🚀 1. Tek Parça EXE (`KM-Layout-Tables-v1.4.0-Standalone.exe`):**  
  Arşiv açma veya kurulum gerektirmez. Tek bir `.exe` dosyasıdır, doğrudan çift tıklayarak çalışır. Masaüstünde veya USB bellekte taşımak için son derece uygundur.

- **⚡ 2. Taşınabilir Klasör / ZIP (`KM-Layout-Tables-v1.4.0-win64.zip`):**  
  Arşivi bir klasöre çıkartın ve içindeki `KM-Layout-Tables.exe`'ye tıklayın. Önceden ayıklanmış kütüphaneleri sayesinde anında (0.3 saniyede) açılır.

*(Her iki sürüm de Python veya AutoCAD kurulumu gerektirmez, bağımsız çalışır).*

---

## 🔑 Doğrulama (Checksums SHA-256)

| Dosya Adı | Boyut | SHA-256 Özeti |
| :--- | :---: | :--- |
| `KM-Layout-Tables-v1.4.0-Standalone.exe` | 78.13 MB | `9066c3b7cb75238f60404e935e32e58e7f666632e58f91b6978ad8b62b33ea21` |
| `KM-Layout-Tables-v1.4.0-win64.zip` | 78.02 MB | `a294a324b179f6debcf4bb660467c28381c12dd0fe6c912487014713c188de37` |
