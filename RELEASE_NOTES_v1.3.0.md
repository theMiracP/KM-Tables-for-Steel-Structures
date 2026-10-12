# 🚀 KM Layout Tables Studio — Sürüm v1.3.0

<p align="center">
  <b>Rusya GOST Standartlarında Çelik Konstrüksiyon (КМ) CAD Tablo ve Pafta Stüdyosu</b><br>
  <i>AutoCAD gerektirmeyen bağımsız 1:1 DXF üretimi, çoklu pafta dağıtımı ve canlı 2D vektörel CAD tuvali.</i>
</p>

---

## 🌟 Sürüm v1.3.0 ile Gelen Yenilikler ve Geliştirmeler

Bu sürümde; çoklu pafta dağıtımı, gelişmiş AutoCAD DXF katman ve renk ayarları, tablo önayar (şablon) yönetimi, akıllı profil algılama ve kullanıcı arayüzü modernizasyonları entegre edilmiştir.

---

### 📑 1. Çoklu Pafta Dağıtımı & Gelişmiş DXF Motoru (Multi-Sheet Layout)
- **Sağdan Sola Sütun Paketleme (Right-to-Left Dynamic Packing):**
  - Çizim paftasında tablolar Form 3 ana antetin üzerinden başlayarak ve sola doğru yeni sütunlar açılarak GOST standartlarına tam uyumlu biçimde yerleştirilir.
- **Kesin Çakışmasızlık Garantisi (Zero Overlap):**
  - 197 mm genişliğindeki Eleman Listesi tablosu ile 185 mm genişliğindeki Form 3 antet ve sol komşu sütunlar arasındaki 4 mm fiziksel çakışma tamamen giderildi (Geometrik Sınırlayıcı Kutu / Bounding Box ayrıklığı).
- **Otomatik Çoklu Pafta Üretimi & Sayfa Numaralandırması:**
  - Tek bir paftaya sığmayan tablolar için otomatik olarak ek paftalar (`Лист 1`, `Лист 2`...) oluşturulur.
  - Form 3 antet içerisindeki pafta numaraları ve toplam pafta sayısı (`Лист N / Листов Total`) dinamik olarak güncellenir.
- **Export Sonrası Klasörü Açma:**
  - DXF dışa aktarımı başarıyla tamamlandığında oluşturulan dosyayı dosya yöneticisinde (Windows Explorer) seçili olarak açma seçeneği eklendi.

---

### 🎨 2. AutoCAD DXF Ayarları & 255 ACI Renk Paleti
- **Gelişmiş DXF Ayarlar Paneli (`LinearSettingsDialog`):**
  - Üst gezinme çubuğundan erişilebilen modern ayarlar paneli ile tüm AutoCAD katman adları özelleştirilebilir.
- **255 Renk AutoCAD Renk İndeksi (ACI):**
  - Standart 1-9 ACI renkleri, 10-249 renk matrisi ve 250-255 gri tonlarını içeren tam kapsamlı AutoCAD Renk Seçici iletişim kutusu (`AciColorPickerDialog`).
  - Açılır menülerde renk örneklerini gösteren canlı renk kutuları (swatches).
- **Özel Milimetrik Çizgi Kalınlıkları:**
  - Önceden tanımlı standart kalınlıklara ek olarak dilediğiniz milimetrik çizgi kalınlığını girebileceğiniz `Özel Kalınlık...` desteği.

---

### 💾 3. Tablo Önayar (Preset / Şablon) Yönetim Sistemi
- **Bağımsız JSON Önayar Dosyaları:**
  - Her tablo için bağımsız şablonları JSON formatında dışa aktarma ve içe aktarma imkanı (`PresetManager`).
- **Görsel Önayar Diyalogları:**
  - Şablon Kaydet (`SavePresetDialog`) ve Şablon Yükle (`LoadPresetDialog`) pencereleri ile tek tıkla şablon yönetimi.
  - Editör başlığının sağ tarafında konumlandırılan hızlı erişim butonları.

---

### 🏗️ 4. Eleman Listesi (Ведомость элементов) İyileştirmeleri
- **ГОСТ 21.502-2007 Standart Kuvvet Başlıkları:**
  - Doğru mühendislik sütunları: Kesme Kuvveti (`A, кН`), Eksenel Yük (`N, кН`), Eğilme Momenti (`M, кН·м`).
- **Anında Profil ve Kesit Algılama (`ProfileCellDelegate`):**
  - Kullanıcı profil adını yazarken (`20К1`, `25Ш1`, `30Б2`, `100х100х4`, `L 75х6` vb.) kesit geometrisi gecikmesiz ve gerçek zamanlı algılanır.
  - Profil hücresinde kesit şekli ikonu doğrudan profil adının yanında görüntülenir.
- **Kiril Kısayolları İçin İyileştirilmiş Odaklanma:**
  - Hızlı Kiril karakter ekleme butonlarında imleç konumu ve veri senkronizasyonu optimize edildi.

---

### 🖥️ 5. Modern Linear SaaS Arayüzü (UI v2) İyileştirmeleri
- **Yeniden Boyutlandırılabilir Çalışma Alanı (`QSplitter`):**
  - Tablo veri giriş editörü ile canlı CAD tuvali arasında serbestçe sürüklenebilir ayırıcı.
- **Glassmorphic Floating HUD Araç Çubuğu:**
  - Canlı CAD tuvali üzerinde yüzen, modern cam efekti (glassmorphism), 1px ince ayırıcılar ve dinamik koordinat genişliğine sahip araç çubuğu.
- **Bayraklı Çok Dilli Seçici:**
  - Üst barda ülke bayraklarıyla donatılmış anlık dil değiştirici (🇹🇷 TR, 🇬🇧 EN, 🇷🇺 RU).
- **Jilet Parıltısı Animasyonu:**
  - "DXF Dışa Aktar" butonuna sağdan sola akan dinamik jilet parıltısı efekti (`LinearShimmerButton`).
- **Minimalist Üst Bar:**
  - Yalnızca `📐 KM Studio` logosu ve gerekli kontrollere odaklanan sadeleştirilmiş tasarım.
- **Gelişmiş Form 3 Antet & Logo Görünürlüğü:**
  - Logo gösterim onay kutusu için beyaz vektörel tik işareti ve firma adı girilmediğinde logo dikey ortalaması.

---

## 📦 İndirme Seçenekleri (Windows x64)

İhtiyacınıza göre iki farklı dağıtım seçeneğinden birini tercih edebilirsiniz:

- **🚀 1. Tek Parça EXE (`KM-Layout-Tables-v1.3.0-Standalone.exe`):**  
  Arşiv açma veya kurulum gerektirmez. Tek bir `.exe` dosyasıdır, doğrudan çift tıklayarak çalışır. Masaüstünde veya USB bellekte taşımak için son derece pratiktir.

- **⚡ 2. Taşınabilir Klasör / ZIP (`KM-Layout-Tables-v1.3.0-win64.zip`):**  
  Arşivi bir klasöre çıkartın ve içindeki `KM-Layout-Tables.exe`'ye tıklayın. Önceden ayıklanmış kütüphaneleri sayesinde **0.3 saniyede anında (jet hızında)** açılır.

*(Her iki sürüm de Python veya AutoCAD kurulumu gerektirmez, bağımsız çalışır).*

---

## 🔑 Doğrulama (Checksums SHA-256)

İndirilen dosyaların bütünlüğünü doğrulamak için `checksums.txt` dosyasındaki veya aşağıdaki SHA-256 özetlerini kontrol edebilirsiniz:

| Dosya Adı | Boyut | SHA-256 Özeti |
| :--- | :---: | :--- |
| `KM-Layout-Tables-v1.3.0-Standalone.exe` | 73.65 MB | `bbcbb70b5e6197aeb75d937df9285d284e800a69fe33270d62d0e1fdb49a0aee` |
| `KM-Layout-Tables-v1.3.0-win64.zip` | 73.54 MB | `4e2a15198e80e6c028ee14ca686d805565182278555fe78f8a04620d1cffa74c` |
