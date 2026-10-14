# KM Layout Tables Studio — Görev ve Yol Haritası Takip Belgesi (TODO.md)

**Proje:** KM Tablo Oluşturucu (CAD Layout Tables Studio)  
**Hedef Standartlar:** ГОСТ 21.502-2007 (КМ Çelik Tabloları), ГОСТ Р 21.101-2020 / ГОСТ 2.301 (Pafta & Antet), ГОСТ 2.302-68 (Ölçek)  
**Geçerli Mimari:** Linear / Notion SaaS Dashboard (UI v2)  
**Doküman Sürümü:** 1.7.0 · **Tarih:** 2026-10-14  

---

## 🧭 Yönetici Özeti (Executive Summary)
Bu belge, Rusya GOST standartlarına tam uyumlu KM Çelik Konstrüksiyon çizim tabloları üreten bağımsız masaüstü CAD mühendislik stüdyosunun **aktif olarak yürütülen revizyon görev listesini** ve **tamamlanan mimari işlerin teknik özetlerini** profesyonel ürün yönetimi formatında kayıt altına alır.

---

### 🎯 BÖLÜM 1: Yapılacaklar Listesi (0 Bekleyen / 79 Onay Bekliyor)

> **Kural:** Tüm görevlerin geliştirmesi ve birim/entegrasyon testleri başarıyla tamamlanmıştır. Kullanıcı bizzat inceleyip onay verene kadar görevler Bölüm 1'de `🔍 Onay Bekliyor` durumunda tutulur; Bölüm 3'e taşınmaz.

### 📊 Yapılacaklar Özet Tablosu

| ID | Görev Tanımı | Öncelik | İlgili Dosyalar | Durum |
| :--- | :--- | :---: | :--- | :---: |
| **TASK-01** | **DXF Dışa Aktarma Hatasının Düzeltilmesi (1:1 & Sabit Antet)** | `P0 - Blocker` | `src/ui_v2/window.py`<br>`src/export/dxf_exporter.py` | 🔍 Onay Bekliyor |
| **TASK-02** | **Veri Giriş Tablosu Sütun Hizalaması & 'Q' Sütununun Kaldırılması** | `P0 - Blocker` | `src/tables/elements_schedule/editor.py` | 🔍 Onay Bekliyor |
| **TASK-03** | **Moment ve Malzeme (Çelik Kalitesi) Sütunlarının Ayrılması** | `P0 - Blocker` | `src/tables/elements_schedule/editor.py` | 🔍 Onay Bekliyor |
| **TASK-04** | **Mükerrer Üst Satır Ekle/Sil Araç Çubuğunun Kaldırılması** | `P1 - High` | `src/ui_v2/editor_wrapper.py` | 🔍 Onay Bekliyor |
| **TASK-05** | **"Tablo Editörü" Tekrarları ve İnce Çerçevenin Temizlenmesi** | `P1 - High` | `src/tables/elements_schedule/editor.py` | 🔍 Onay Bekliyor |
| **TASK-06** | **Eleman Ekle/Sil ve Yön Butonlarının Belirginleştirilmesi** | `P1 - High` | `src/tables/elements_schedule/editor.py` | 🔍 Onay Bekliyor |
| **TASK-07** | **Çift Dilli Tablo Başlıkları (Rusça GOST + Türkçe Çeviri)** | `P1 - High` | `src/tables/elements_schedule/editor.py` | 🔍 Onay Bekliyor |
| **TASK-08** | **Hücre Yazı Boyutunun ve Satır Yüksekliğinin Büyütülmesi (13px, 34px)** | `P1 - High` | `src/tables/elements_schedule/editor.py`<br>`src/ui_v2/theme_linear.py` | 🔍 Onay Bekliyor |
| **TASK-09** | **Tablo Altı Kullanım Bilgilendirme Notu (Kısayollar & GOST)** | `P1 - High` | `src/tables/elements_schedule/editor.py` | 🔍 Onay Bekliyor |
| **TASK-10** | **Her Tablo İçin Bağımsız Pafta Boyutu ve Yönelim Hafızası** | `P2 - Medium` | `src/ui_v2/window.py`<br>`src/ui_v2/sidebar.py` | 🔍 Onay Bekliyor |
| **TASK-11** | **QComboBox Açılır Menülerinin Tasarım ve Liste İyileştirmesi** | `P2 - Medium` | `src/ui_v2/theme_linear.py`<br>`src/ui_v2/sidebar.py` | 🔍 Onay Bekliyor |
| **TASK-12** | **Çelik Sarfiyat Modülünün UI'dan Çıkarılması (Registry Korunarak)** | `P2 - Medium` | `src/tables/steel_consumption/module.py`<br>`src/ui_v2/sidebar.py` | 🔍 Onay Bekliyor |
| **TASK-13** | **Eski v1 Kod Artıklarının Temizlenmesi (gemini.md Kuralı)** | `P2 - Medium` | `src/ui/` | 🔍 Onay Bekliyor |
| **TASK-14** | **"Hakkında" (About) Modalı ve Üst Bar Buton Entegrasyonu** | `P2 - Medium` | `src/ui_v2/about_dialog.py`<br>`src/ui_v2/top_bar.py` | 🔍 Onay Bekliyor |
| **TASK-15** | **Dil Seçeneklerinin İlerisi İçin İzolasyonu** | `P3 - Low` | `src/ui_v2/top_bar.py`<br>`src/ui/i18n.py` | 🔍 Onay Bekliyor |
| **TASK-16** | **Dinamik Çift Dilli Başlıklar (Sabit Rusça GOST + Seçilen Dil)** | `P1 - High` | `src/tables/elements_schedule/editor.py`<br>`src/ui/i18n.py` | 🔍 Onay Bekliyor |
| **TASK-17** | **Veri Giriş Tablosuna 'A, кН' (Eksenel Kuvvet) Sütununun Eklenmesi** | `P0 - Blocker` | `src/tables/elements_schedule/editor.py`<br>`src/ui/i18n.py` | 🔍 Onay Bekliyor |
| **TASK-18** | **ГОСТ Р 21.101-2020 Form 3 Başlık Bloğu (Title Block / Antet) Modülü** | `P0 - Blocker` | `src/tables/title_block/*`<br>`src/export/dxf_exporter.py`<br>`src/ui/preview_canvas.py` | 🔍 Onay Bekliyor |
| **TASK-19** | **Veri Giriş Kutucukları İmleç ve Satır Yüksekliği İyileştirmesi** | `P1 - High` | `src/tables/title_block/editor.py`<br>`src/tables/elements_schedule/editor.py` | 🔍 Onay Bekliyor |
| **TASK-20** | **Canlı CAD Tuvalinde Gerçek CAD Fontu & Milimetrik Metin Ölçeklemesi** | `P0 - Blocker` | `src/ui/preview_canvas.py` | 🔍 Onay Bekliyor |
| **TASK-21** | **Canlı CAD Ekranında 2 Antetin Üst Üste Çıkması Hatasının Giderilmesi** | `P0 - Blocker` | `src/ui/preview_canvas.py`<br>`src/export/dxf_exporter.py` | 🔍 Onay Bekliyor |
| **TASK-22** | **Sol Kenar Çubuğundaki Tablo Sayı Rozetlerinin Kaldırılması** | `P2 - Medium` | `src/ui_v2/sidebar.py` | 🔍 Onay Bekliyor |
| **TASK-23** | **Sol Kenar Çubuğu Tablo İsimlerinin Seçilen Dile Göre Dinamik Değişimi** | `P1 - High` | `src/ui_v2/sidebar.py`<br>`src/ui/i18n.py` | 🔍 Onay Bekliyor |
| **TASK-24** | **İlk Tablo İçin Pafta İçi Konumlandırma Seçenekleri (Ortalı, Sol/Sağ Üst)** | `P1 - High` | `src/config/sheet_config.py`<br>`src/models/sheet.py`<br>`src/ui_v2/sidebar.py` | 🔍 Onay Bekliyor |
| **TASK-25** | **Title Block İçin Kurumsal Logo Yükleme Seçeneği (Resim Dosyası)** | `P1 - High` | `src/tables/title_block/*`<br>`src/ui/preview_canvas.py`<br>`src/export/dxf_exporter.py` | 🔍 Onay Bekliyor |
| **TASK-26** | **DXF Dışa Aktarımında Metin Taşmalarının Önlenmesi (Auto Word-Wrap)** | `P0 - Blocker` | `src/export/dxf_exporter.py` | 🔍 Onay Bekliyor |
| **TASK-27** | **Canlı CAD Tuvali ile DXF Çıktısının Birebir Özdeş Hale Getirilmesi (WYSIWYG)** | `P0 - Blocker` | `src/ui/preview_canvas.py`<br>`src/export/dxf_exporter.py` | 🔍 Onay Bekliyor |
| **TASK-28** | **Hücre İçi Düzenlemede Metin Çakışması/Üst Üste Binmesinin Giderilmesi** | `P0 - Blocker` | `src/ui_v2/components.py`<br>`src/tables/title_block/editor.py`<br>`src/tables/elements_schedule/editor.py` | 🔍 Onay Bekliyor |
| **TASK-29** | **Tablo Hücre İçi Düzenlemede İmlecin ve Metin Kutusunun Dikey Sıkışmasının Önlenmesi** | `P1 - High` | `src/ui_v2/components.py`<br>`src/ui_v2/theme_linear.py` | 🔍 Onay Bekliyor |
| **TASK-30** | **Metin Uzunluğuna Göre Otomatik Font Küçültme ve Maksimum Font Tavanı Kuralı** | `P0 - Blocker` | `src/models/text_layout.py`<br>`src/ui/preview_canvas.py`<br>`src/export/dxf_exporter.py` | 🔍 Onay Bekliyor |
| **TASK-31** | **ГОСТ 2.301-68 Pafta Formatı Alt Etiketi (Формат А1А, Формат А3А vb.)** | `P1 - High` | `src/config/sheet_config.py`<br>`src/export/dxf_exporter.py`<br>`src/ui/preview_canvas.py` | 🔍 Onay Bekliyor |
| **TASK-32** | **ГОСТ 2.104 / ГОСТ Р 21.101 Sol Kenar Boşluğu Ek Tabloları (İnventar & Согласовано)** | `P1 - High` | `src/export/dxf_exporter.py`<br>`src/ui/preview_canvas.py` | 🔍 Onay Bekliyor |
| **TASK-33** | **ГОСТ Р 21.101 Form 2 Referans ve Ek Dokümanlar Tablosu & Çok Dilli Standartlar Kütüphanesi** | `P0 - Blocker` | `src/tables/reference_documents/*`<br>`src/config/standards_library.json`<br>`src/ui_v2/sidebar.py` | 🔍 Onay Bekliyor |
| **TASK-34** | **Standart Kodlarının Hücrede Ortalanması & Çok Satırlı İsimlerde Dinamik Font Küçültme** | `P0 - Blocker` | `src/tables/reference_documents/builder.py`<br>`src/models/text_layout.py`<br>`src/ui/preview_canvas.py`<br>`src/export/dxf_exporter.py` | 🔍 Onay Bekliyor |
| **TASK-35** | **ГОСТ Р 21.101 Form 2 'Ведомость основных комплектов рабочих чертежей' Modülü & Manuel Veri Editörü** | `P0 - Blocker` | `src/tables/main_drawings/*`<br>`src/ui_v2/sidebar.py`<br>`src/ui_v2/editor_wrapper.py` | 🔍 Onay Bekliyor |
| **TASK-36** | **ГОСТ Р 21.101 Form 1 'Ведомость рабочих чертежей основного комплекта' Modülü & Manuel Veri Editörü** | `P0 - Blocker` | `src/tables/working_drawings/*`<br>`src/ui_v2/sidebar.py`<br>`src/ui_v2/editor_wrapper.py` | 🔍 Onay Bekliyor |
| **TASK-37** | **Zadax.net Web Sitesi Bağlantısı ve Versiyon Güncelleme Bildirimi (Manuel İndirme)** | `P1 - High` | `src/version.py`<br>`src/services/updater.py`<br>`src/ui_v2/about_dialog.py` | 🔍 Onay Bekliyor |
| **TASK-38** | **QtAwesome Vektörel İkon Altyapısı (Solid fa5s Butonlar & Regular fa5r/fa5 Arayüz)** | `P1 - High` | `src/ui_v2/icons.py`<br>`src/ui_v2/about_dialog.py`<br>`src/ui_v2/top_bar.py`<br>`src/ui_v2/sidebar.py` | 🔍 Onay Bekliyor |
| **TASK-39** | **DXF Dışa Aktar Butonuna Sağdan Sola Jilet Parıltısı Animasyonu** | `P1 - High` | `src/ui_v2/components.py`<br>`src/ui_v2/top_bar.py` | 🔍 Onay Bekliyor |
| **TASK-40** | **CAD Ekranının Açılıp Kapatılabilir (Collapsible/Toggle) Yapılması (Default Açık)** | `P1 - High` | `src/ui_v2/window.py`<br>`src/ui_v2/top_bar.py`<br>`src/ui_v2/cad_panel.py` | 🔍 Onay Bekliyor |
| **TASK-41** | **Hızlı Arama (Ctrl+K) Tablo İsimleri Senkronizasyonu & Kenar Çubuğu Menüsü** | `P1 - High` | `src/ui/quick_switcher.py`<br>`src/ui/i18n.py`<br>`src/ui_v2/sidebar.py` | 🔍 Onay Bekliyor |
| **TASK-42** | **Tablo Temizleme ve Satır Silmede 1'er Boş Satır Korunması** | `P1 - High` | `src/tables/*/editor.py`<br>`src/ui/i18n.py` | 🔍 Onay Bekliyor |
| **TASK-43** | **Örnek Şablon Verilerinin Jenerik/Kurgusal Hale Getirilmesi (Standartlar Tablosu Sabit)** | `P1 - High` | `src/tables/title_block/*`<br>`src/tables/main_drawings/*`<br>`src/tables/working_drawings/*` | 🔍 Onay Bekliyor |
| **TASK-44** | **Çok Dilli Başlık/Üst Bilgi Senkronizasyonu & GOST Form 2 Bölüm (Раздел) Mimarisi** | `P1 - High` | `src/ui/i18n.py`<br>`src/ui_v2/editor_wrapper.py`<br>`src/ui_v2/top_bar.py`<br>`src/tables/reference_documents/editor.py` | 🔍 Onay Bekliyor |
| **TASK-45** | **Form 3 Antet ve Tüm Editör Başlıklarının Dinamik Çok Dilli Senkronizasyonu (TR/EN/RU)** | `P0 - Blocker` | `src/ui/i18n.py`<br>`src/tables/title_block/editor.py`<br>`src/tables/elements_schedule/editor.py`<br>`src/ui_v2/cad_panel.py` | 🔍 Onay Bekliyor |
| **TASK-46** | **Tablo İsimlerinin ГОСТ Standartlarına Tam Uyumlu Hale Getirilmesi (Madde 1)** | `P1 - High` | `src/ui/i18n.py`<br>`src/tables/*/module.py`<br>`src/ui_v2/sidebar.py`<br>`src/ui/quick_switcher.py` | 🔍 Onay Bekliyor |
| **TASK-47** | **Profil Listesinde Profil Şeklinin Profil İsminin Yanında Gösterilmesi (Madde 2)** | `P1 - High` | `src/tables/elements_schedule/editor.py`<br>`src/tables/elements_schedule/sketch_renderer.py` | 🔍 Onay Bekliyor |
| **TASK-48** | **Profil İsmi Silinip Kiril Kısayolu Eklendiğinde Sona Eklenme Hatasının Düzeltilmesi (Madde 3)** | `P1 - High` | `src/tables/elements_schedule/editor.py`<br>`src/ui_v2/components.py` | 🔍 Onay Bekliyor |
| **TASK-49** | **Veri Giriş Alanı ile CAD Tuvali Arasında Boyutlandırma Esnekliği (QSplitter) (Madde 4)** | `P1 - High` | `src/ui_v2/window.py`<br>`src/ui_v2/cad_panel.py` | 🔍 Onay Bekliyor |
| **TASK-50** | **DXF Export Sonrası Dosya Yolunu / Klasörü Açma Onay Diyaloğu (Madde 5)** | `P2 - Medium` | `src/ui_v2/window.py`<br>`src/ui/i18n.py` | 🔍 Onay Bekliyor |
| **TASK-51** | **Title Block Logo Alanında Şirket Yazısı Olmadığında Logonun Kutu İçinde Ortalanması (Madde 6)** | `P1 - High` | `src/tables/title_block/builder.py`<br>`src/ui/preview_canvas.py`<br>`src/export/dxf_exporter.py` | 🔍 Onay Bekliyor |
| **TASK-52** | **Title Block Sorumlular Tablosunda Soyisim Sütunu Konumunun Standarttan Kontrolü (Madde 7)** | `P1 - High` | `src/tables/title_block/builder.py`<br>`src/tables/title_block/editor.py`<br>`src/export/dxf_exporter.py` | 🔍 Onay Bekliyor |
| **TASK-53** | **Title Block Revizyon Sütunları Genişliğinin Standarttan Kontrol Edilip Ayarlanması (Madde 8)** | `P1 - High` | `src/tables/title_block/builder.py`<br>`src/tables/title_block/editor.py` | 🔍 Onay Bekliyor |
| **TASK-54** | **Güncelleme Kontrol Ayarlarının ve Tercihlerinin Yapılandırılması (Madde 9)** | `P2 - Medium` | `src/services/updater.py`<br>`src/ui_v2/about_dialog.py`<br>`src/config/app_config.py` | 🔍 Onay Bekliyor |
| **TASK-55** | **Hakkında (About) Butonlarının Hover Olmadığında da Farklı Renklerle Görünmesi (Madde 10)** | `P2 - Medium` | `src/ui_v2/about_dialog.py`<br>`src/ui_v2/theme_linear.py` | 🔍 Onay Bekliyor |
| **TASK-56** | **Tüm Tabloları Paftalara Otomatik Yerleştiren Dinamik Sistem & Ortak Antet (Madde 11)** | `P0 - Blocker` | `src/models/sheet.py`<br>`src/config/sheet_config.py`<br>`src/export/dxf_exporter.py`<br>`src/ui/preview_canvas.py`<br>`src/ui_v2/window.py` | 🔍 Onay Bekliyor |
| **TASK-57** | **AutoCAD DXF Katman (Layer) İsimleri, Renkleri ve Ayarlar Paneli** | `P1 - High` | `src/config/dxf_config.py`<br>`src/ui_v2/settings_dialog.py`<br>`src/export/dxf_exporter.py` | 🔍 Onay Bekliyor |
| **TASK-58** | **Tablo Şablon / Önayar (Preset) Yönetim Sistemi (Bağımsız Kaydetme & Yükleme)** | `P1 - High` | `src/services/preset_manager.py`<br>`src/ui_v2/preset_dialog.py`<br>`src/tables/*/editor.py` | 🔍 Onay Bekliyor |
| **TASK-59** | **Title Block "Logo Göster" Checkbox Görünürlüğü (Madde 1)** | `P1 - High` | `src/ui_v2/theme_linear.py`<br>`src/ui_v2/assets/checkmark.svg` | 🔍 Onay Bekliyor |
| **TASK-60** | **Tablo İsimlerinin Standart Üçlü Formata Getirilmesi (GOST / Tablo No / İsim) (Madde 2)** | `P1 - High` | `src/ui/i18n.py` | 🔍 Onay Bekliyor |
| **TASK-61** | **Ayarlar Menüsü "Uygulama Açıldığında Güncelle" Checkbox Görünürlüğü (Madde 3)** | `P1 - High` | `src/ui_v2/theme_linear.py`<br>`src/ui_v2/settings_dialog.py` | 🔍 Onay Bekliyor |
| **TASK-62** | **Güncelleme URL Alanının Sabitlenmesi & Resmi Sunucu Kartı (Madde 4)** | `P2 - Medium` | `src/ui_v2/settings_dialog.py` | 🔍 Onay Bekliyor |
| **TASK-63** | **AutoCAD Katman Adı Alanı İmleç ve Satır Yüksekliği İyileştirmesi (Madde 5)** | `P1 - High` | `src/ui_v2/settings_dialog.py` | 🔍 Onay Bekliyor |
| **TASK-64** | **AutoCAD Renk Ayarlarında Renk Kutuları (Swatch) ve 255 ACI Renk Paleti (Madde 6)** | `P1 - High` | `src/ui_v2/settings_dialog.py` | 🔍 Onay Bekliyor |
| **TASK-65** | **AutoCAD Çizgi Kalınlıkları İçin Özel Kalınlık (Custom mm) Desteği (Madde 7)** | `P1 - High` | `src/ui_v2/settings_dialog.py` | 🔍 Onay Bekliyor |
| **TASK-66** | **Kenar Çubuğu Alt Callout Kartının ve Üst Bar GOST Rozetinin Kaldırılması (Madde 8)** | `P2 - Medium` | `src/ui_v2/sidebar.py`<br>`src/ui_v2/top_bar.py` | 🔍 Onay Bekliyor |
| **TASK-67** | **Dil Seçeneklerinin Yanına Ülke Bayrak Simgelerinin Eklenmesi (🇹🇷, 🇬🇧, 🇷🇺) (Madde 9)** | `P2 - Medium` | `src/ui_v2/top_bar.py` | 🔍 Onay Bekliyor |
| **TASK-68** | **Eleman Listesi "Eleman Ekle" Butonundaki Mükerrer '+' İşaretinin Temizlenmesi (Madde 10)** | `P2 - Medium` | `src/ui/i18n.py`<br>`src/tables/elements_schedule/editor.py` | 🔍 Onay Bekliyor |
| **TASK-69** | **Editör Başlık Metni ile Şablon Butonlarının Ayrılması (Çakışma Önleme) (Madde 11)** | `P1 - High` | `src/ui_v2/editor_wrapper.py`<br>`src/ui/i18n.py` | 🔍 Onay Bekliyor |
| **TASK-70** | **Üst Barda Yalnızca Logo ve "KM Studio" İsim Alanının Bırakılması (Madde 12)** | `P2 - Medium` | `src/ui_v2/top_bar.py` | 🔍 Onay Bekliyor |
| **TASK-71** | **Eleman Listesinde Profil İsmi Değişince Anında Algılama & Gecikmesiz Senkronizasyon (Madde 13)** | `P1 - High` | `src/tables/elements_schedule/editor.py` | 🔍 Onay Bekliyor |
| **TASK-72** | **Çoklu Çıktıda Paftalarda Tablo Çakışmasının Kesin Önlenmesi & Dinamik Sütun Paketleme** | `P0 - Blocker` | `src/models/multi_sheet.py`<br>`src/ui_v2/cad_panel.py` | 🔍 Onay Bekliyor |
| **TASK-73** | **Güncelleme Ayarının Kullanıcıdan Gizlenmesi & Resmi Zadax Ürün Sayfası Entegrasyonu** | `P1 - High` | `src/version.py`<br>`src/services/updater.py`<br>`src/services/settings.py`<br>`src/ui_v2/settings_dialog.py` | 🔍 Onay Bekliyor |
| **TASK-74** | **AutoCAD Katman Tablosu Sütun Sıkışmasının Giderilmesi & Dinamik Genişlik** | `P0 - Blocker` | `src/ui_v2/settings_dialog.py`<br>`tests/test_revisions_batch_13.py` | 🔍 Onay Bekliyor |
| **TASK-75** | **GOST Rus Çelik Sortament / Profil Seçici Kütüphanesi (Item 2.1)** | `P0 - Blocker` | `src/config/gost_profiles.json`<br>`src/services/profile_database.py`<br>`src/ui_v2/profile_picker_dialog.py`<br>`src/tables/elements_schedule/editor.py` | 🔍 Onay Bekliyor |
| **TASK-76** | **1:1 Vektörel PDF Dışa Aktarma Motoru (Tekli ve Çoklu Paftalar) (Item 2.3)** | `P0 - Blocker` | `src/export/pdf_exporter.py`<br>`src/ui/preview_canvas.py`<br>`src/ui_v2/window.py`<br>`src/ui_v2/top_bar.py` | 🔍 Onay Bekliyor |
| **TASK-77** | **Ortak Antet (Title Block) Verilerinin Tüm Tablolar ve Paftalarla Eşzamanlanması (Item 3.2)** | `P1 - High` | `src/ui_v2/window.py`<br>`src/models/sheet.py`<br>`src/models/multi_sheet.py` | 🔍 Onay Bekliyor |
| **TASK-78** | **Yerel Proje Formatı (.kmproj) Kaydetme, Yükleme ve Proje Yönetimi (Item 4.1)** | `P0 - Blocker` | `src/services/project_manager.py`<br>`src/ui_v2/window.py`<br>`src/ui_v2/top_bar.py` | 🔍 Onay Bekliyor |
| **TASK-79** | **Geri Al / İleri Al (Undo / Redo) Geri Alma Altyapısı (Item 4.2)** | `P1 - High` | `src/services/undo_manager.py`<br>`src/ui_v2/editor_wrapper.py`<br>`src/ui_v2/window.py` | 🔍 Onay Bekliyor |

---

### 📝 Detaylı Görev Kartları ve Uygulama Özetleri

##### 🔹 [TASK-01] DXF Dışa Aktarma Hatasının Düzeltilmesi (Madde 1) — 🔍 Onay Bekliyor
- **Yapılan İş:**
  1. `src/ui_v2/window.py` içerisindeki dışa aktarma çağrısı `self.dxf_exporter.export(...)` olarak güncellendi.
  2. `src/export/dxf_exporter.py` sınıfına geriye dönük uyumluluk için `export_table = export` takma adı eklendi.
  3. Çıktının 1:1 ölçekli ($INSUNITS=4) ve Form 3 ana antetin daima sağ alt köşeye kilitli üretildiği doğrulandı.

##### 🔹 [TASK-02] Veri Giriş Tablosu Sütun Hizalaması & 'Q' Sütununun Kaldırılması (Madde 6) — 🔍 Onay Bekliyor
- **Yapılan İş:**
  1. `src/tables/elements_schedule/editor.py` içerisinden standart dışı "Q" sütunu tamamen kaldırıldı.
  2. Sütun sayısı 8'den 7'ye indirildi: `Марка`, `Эскиз`, `Сечение / Состав`, `N, кН`, `M, кН·м`, `Сталь`, `Примечание`.
  3. Veri girişi ve model eşlemesi tam uyumlu hale getirildi.

##### 🔹 [TASK-03] Moment ve Malzeme (Çelik Kalitesi) Sütunlarının Ayrılması (Madde 7) — 🔍 Onay Bekliyor
- **Yapılan İş:**
  1. `_load_items_to_table` ve `_sync_and_emit` metodlarındaki sütun indeks kayması giderildi:
     - Sütun 3: `N, кН` -> `item.force_n`
     - Sütun 4: `M, кН·м` -> `item.force_m`
     - Sütun 5: `Сталь` -> `item.steel_grade`
     - Sütun 6: `Примечание` -> `item.note`
  2. Moment hücresine girilen değerler Moment modeline, Çelik hücresine girilen değerler Çelik Kalitesi modeline yazıldı.

##### 🔹 [TASK-04] Mükerrer Üst Satır Ekle/Sil Araç Çubuğunun Kaldırılması (Madde 8) — 🔍 Onay Bekliyor
- **Yapılan İş:**
  1. `src/ui_v2/editor_wrapper.py` üzerindeki mükerrer "＋ Satır Ekle / 🗑 Sil" üst araç çubuğu ve sayaç kaldırıldı.
  2. Grid doğrudan temiz başlık altına bağlandı.

##### 🔹 [TASK-05] "Tablo Editörü" Tekrarları ve İnce Çerçevenin Temizlenmesi (Madde 2 & 3) — 🔍 Onay Bekliyor
- **Yapılan İş:**
  1. `ElementsScheduleWidget` başlığındaki ince çerçeveli `header_card` şeffaf ve çerçevesiz Linear stiline dönüştürüldü.
  2. Mükerrer "TABLO EDİTÖRÜ" rozetleri temizlendi.

##### 🔹 [TASK-06] Eleman Ekle/Sil ve Yön Butonlarının Belirginleştirilmesi (Madde 9) — 🔍 Onay Bekliyor
- **Yapılan İş:**
  1. "＋ Eleman Ekle" butonu zümrüt yeşili vurgulu (`#10B981`, hover `#059669`) stile kavuşturuldu.
  2. "🗑 Sil" butonu koyu kırmızı arka plan ve parlak kırmızı metin (`#EF4444`, hover `#DC2626`) ile belirginleştirildi.
  3. "▲ Yukarı / ▼ Aşağı" taşıma butonları 30px yükseklikte yüksek kontrastlı koyu slate stiliyle yenilendi.

##### 🔹 [TASK-07] Çift Dilli Tablo Başlıkları (Madde 5) — 🔍 Onay Bekliyor
- **Yapılan İş:**
  - Tablo başlıkları standart ГОСТ Rusça terim üstte, Türkçe çevirisi altta olacak şekilde iki satırlı yapıldı:
    `Марка\n(Marka)`, `Эскиз\n(Eskiz)`, `Сечение / Состав\n(Kesit / Profil)`, `N, кН\n(Normal)`, `M, кН·м\n(Moment)`, `Сталь\n(Çelik)`, `Примечание\n(Not)`.

##### 🔹 [TASK-08] Hücre Yazı Boyutunun ve Satır Yüksekliğinin Büyütülmesi (Madde 4) — 🔍 Onay Bekliyor
- **Yapılan İş:**
  1. Grid varsayılan satır yüksekliği 26px'den 34px'e çıkarıldı.
  2. Hücre yazı tipi 10pt (13px) yapıldı, QLineEdit ve ComboBox hücre içi stilleri rahat okunabilir hale getirildi.

##### 🔹 [TASK-09] Tablo Altı Kullanım Bilgilendirme Notu (Madde 13) — 🔍 Onay Bekliyor
- **Yapılan İş:**
  1. Tablonun hemen altına `UsageInfoCard` eklendi.
  2. ГОСТ 21.502 kuralları ve klavye kısayolları (`Tab: Yan Hücre`, `Enter: Alt Hücre`, `F2: Düzenle`, `Ctrl+V: Excel Yapıştır`) kullanıcıya gösterildi.

##### 🔹 [TASK-10] Her Tablo İçin Bağımsız Pafta Boyutu ve Yönelim Hafızası (Madde 10) — 🔍 Onay Bekliyor
- **Yapılan İş:**
  1. `KmLinearMainWindow` sınıfına `module_layout_configs: dict[str, LayoutConfig]` hafızası eklendi.
##### 🔹 [TASK-11] QComboBox Açılır Menülerinin Elden Geçirilmesi (Takılma, Saydamlık ve Ok İyileştirmesi) — 🔍 Onay Bekliyor
- **İstek:** Açılır menülerin (ComboBox) açılırken takılması, arkadaki yazıların saydam şekilde görünmesi ve ok simgesinin bozuk kare görünmesi giderilmeli; akıcı, solid opak zeminli hale getirilmeli.
- **Yapılan İş:**
  1. `src/ui_v2/components.py` altında `LinearComboBox` özel bileşeni geliştirildi:
     - Windows DWM saydamlık hatalarını (`WA_TranslucentBackground = True` sonucu oluşan şeffaflık) gidermek için `showPopup()` içinde container saydamlığı kapatıldı ve `%100 solid opak` (`#17181f`) zemin zorlandı.
     - Açılıştaki işletim sistemi animasyon takılmalarını önlemek için doğrudan optimize `QListView` atandı (`setUniformItemSizes(True)` ile gecikmesiz açılış).
  2. Bozuk beyaz kare simgesi oluşturan CSS border-triangle hilesi kaldırıldı; `src/ui_v2/assets/` altına antialiased `chevron_down.svg` ve `chevron_down_hover.svg` ikonları eklendi.
  3. `theme_linear.py` ve `theme.py` temalarındaki `QComboBox::down-arrow`, `QComboBox QAbstractItemView` ve `QComboBox QListView` stilleri solid ve SVG uyumlu olarak güncellendi.
  4. Hem kenar çubuğundaki pafta parametreleri (`cmb_size`, `cmb_orient`, `cmb_place`) hem de tablo veri editöründeki kesit eskiz seçimi (`cb_sketch`) `LinearComboBox` ile donatıldı.
  5. `tests/test_ui_v2_tasks_verification.py` altındaki testler güncellenerek tüm testlerin (%100) başarıyla geçtiği doğrulandı.

##### 🔹 [TASK-12] Çelik Sarfiyat Modülünün UI'dan Çıkarılması (Madde 12) — 🔍 Onay Bekliyor
- **Yapılan İş:**
  1. `SteelConsumptionModule.is_active = False` olarak işaretlendi.
  2. `LinearSidebar` ve `QuickTableSwitcherDialog` yalnızca aktif modülleri listeleyecek şekilde filtrelendi.
  3. `TableRegistry` altyapısı gelecekte yeni eklenecek tablolar için tam çalışır halde korundu.

##### 🔹 [TASK-13] Eski v1 Kod Artıklarının Temizlenmesi (gemini.md kuralı) — 🔍 Onay Bekliyor
- **Yapılan İş:**
  1. Artık kullanılmayan `src/ui/layout_panel.py`, `src/ui/table_explorer.py` ve `src/ui/input_panel.py` dosyaları silindi.
  2. Ortak CAD bileşenleri (`preview_canvas.py`, `i18n.py`, `quick_switcher.py`, `widgets.py`, `theme.py`) korundu.

##### 🔹 [TASK-14] "Hakkında" (About) Modalı ve Üst Bar Butonu (Madde 14) — 🔍 Onay Bekliyor
- **Yapılan İş:**
  1. `src/ui_v2/about_dialog.py` (`LinearAboutDialog`) modal penceresi geliştirildi (ГОСТ 21.502, ГОСТ Р 21.101, Form 3 antet, ezdxf 1:1 ölçek detayları).
  2. `LinearTopBar` üst gezinme çubuğuna "ℹ️ Hakkında" butonu eklendi ve pencereye bağlandı.

##### 🔹 [TASK-15] Dil Seçeneklerinin İlerisi İçin İzolasyonu (Madde 15) — 🔍 Onay Bekliyor
- **Yapılan İş:**
  1. `i18n.set_language` büyük/küçük harf duyarsız hale getirildi.
  2. Dil değiştirildiğinde arayüzün kararlı çalışması sağlandı.

##### 🔹 [TASK-16] Dinamik Çift Dilli Başlıklar (Sabit Rusça GOST + Seçilen Dil) — 🔍 Onay Bekliyor
- **İstek:** Tablo başlıklarının üst satırı orijinal Rusça GOST standardı olarak daima sabit kalmalı (`Марка`, `Эскиз`, `Сечение / Состав`, `N, кН`, `M, кН·м`, `Сталь`, `Примечание`), alt satır parantez içi ise seçilen aktif dile (TR, EN, RU) göre dinamik olarak güncellenmelidir.
- **Yapılan İş:**
  1. `src/ui/i18n.py` içerisine TR, EN ve RU dilleri için `col_sub_*` çeviri anahtarları eklendi.
  2. `src/tables/elements_schedule/editor.py` sınıfındaki `_apply_table_headers` metodu `f"Марка\n({i18n.t('col_sub_mark')})"` formatında dinamik hale getirildi.
  3. Dil TR seçildiğinde `(Marka)`, `(Eskiz)` vb.; EN seçildiğinde `(Mark)`, `(Sketch)` vb.; RU seçildiğinde `(Марка)`, `(Эскиз)` vb. dinamik alt satır üretildi.
  4. Tüm dillerde üst satırın daima değişmez orijinal Rusça GOST terimi olduğu ve testlerle (`tests/test_ui_v2_tasks_verification.py`) doğrulandığı garanti altına alındı.

##### 🔹 [TASK-17] Veri Giriş Tablosuna 'A, кН' (Eksenel Kuvvet) Sütununun Eklenmesi — 🔍 Onay Bekliyor
- **İstek:** Kullanıcı ekran görüntüsü üzerinden veri giriş tablosunda `A, кН` (Eksenel kuvvet / Осевое усилие) sütununun eksik olduğunu belirtti. Çizim tablosunda ve ГОСТ 21.502 standardında bulunan bu sütunun veri editörüne de eklenmesi talep edildi.
- **Yapılan İş:**
  1. `src/ui/i18n.py` içerisine TR ("Eksenel"), EN ("Axial"), RU ("Осевое") çeviri anahtarları eklendi (`col_sub_force_a`).
  2. `src/tables/elements_schedule/editor.py` tablosu 8 sütuna çıkarıldı:
     - Sütun 0: `Марка` (Marka)
     - Sütun 1: `Эскиз` (Eskiz)
     - Sütun 2: `Сечение / Состав` (Kesit / Profil)
     - Sütun 3: `A, кН` (Eksenel)
     - Sütun 4: `N, кН` (Normal)
     - Sütun 5: `M, кН·м` (Moment)
     - Sütun 6: `Сталь` (Çelik)
     - Sütun 7: `Примечание` (Not)
  3. `_load_items_to_table`, `_sync_and_emit`, `_add_row` ve bilgi kartı metinleri `force_a` alanı ile eksiksiz senkronize edildi.
  4. Örnek veri (Б1) için `force_a="85"` değeri 3. sütuna yüklendi, düzenlemelerin `ScheduleItem.force_a` modeline anında aktarıldığı doğrulandı.
  5. `tests/test_ui_v2_tasks_verification.py` dosyasına `test_task_17_force_a_data_entry` testi eklendi ve tüm 77 test yeşile ulaştırıldı.

##### 🔹 [TASK-18] ГОСТ Р 21.101-2020 Form 3 Başlık Bloğu (Title Block / Antet) Modülü — 🔍 Onay Bekliyor
- **İstek:** Kullanıcı referans görselde işaretlediği değişken sarı alanlar (Doküman kodu, şantiye/proje adı, yapı adı, pafta başlığı, aşama/pafta no, firma adı/logo, 6 kişilik mühendis kadrosu ve 4 satırlık revizyon tablosu) ile Form 3 antet tablosunun sisteme eklenmesini ve veri girişinin klasik form kartları yerine **tıpkı antetin kendisi gibi (WYSIWYG)** görsel bir şablon üzerinde yapılmasını talep etti.
- **Yapılan İş:**
  1. **Veri Modeli (`src/tables/title_block/model.py`):**
     - `SignatoryEntry`: Rol (`Разраб.`, `Проверил`, `Гл. констр.`, `Н. контр.`, `Нач. отд.`, `ГИП`), Soyadı (`Челик`, `Айдын`, `Пехливаноглу`, `Танфенер`, `Олесик`, `Семенов`), İmza/Paraf (`✓`), Tarih (`23.09.26`).
     - `RevisionEntry`: Revizyon tablosu (`Изм.`, `Кол.уч.`, `Лист`, `№док.`, `Подпись`, `Дата`).
     - `TitleBlockDocument`: Kullanıcı görselindeki tüm değişken alanlarla (`РД-2026-Ф2-КМ1-04`, `Москва-Сити` kompleks adresi, `Металлические конструкции секции Ф2...`, `Узлы изменения сечения колонн...`, `Стадия Р`, `Лист 8`, `Листов`, `стадиа инжиниринг` ve logo amblemi) donatıldı.
  2. **Parametrik CAD İnşa Edicisi (`src/tables/title_block/builder.py`):**
     - Tam standart `185 x 55 mm` boyutunda, 10 sütun ve 11 satırdan oluşan milimetrik `Table` modeli geliştirildi.
     - Kalın çizgi sınırları (`border_right_thick`, `border_top_thick`) ile ana bölüntüler (70mm sol sütun ayracı, 40mm kod satırı altı, 135mm orta/sağ ayracı) 0.70mm kalın çizgilerle çizildi.
     - Dinamik font boyutları (`doc_code` 4.5mm bold, proje/yapı 2.5mm, aşama/pafta 3.5mm bold) tanımlandı.
  3. **WYSIWYG Görsel Antet Editörü (`src/tables/title_block/editor.py`):**
     - Kullanıcının doğrudan antetin kendi kutucuklarına tıklayarak veri girebileceği interaktif Form 3 CAD şablonu geliştirildi:
       - **Sol Bölge (70 mm / %38 Genişlik):**
         - Üst: 4 satırlık revizyon kayıt tablosu (`Изм.`, `Кол.уч.`, `Лист`, `№док.`, `Подпись`, `Дата`).
         - Alt: 6 satırlık yetkili mühendis kadrosu ve imza tablosu (`Разраб.`, `Проверил`, `Гл. констр.`, `Н. контр.`, `Нач. отд.`, `ГИП`).
       - **Sağ Bölge (115 mm / %62 Genişlik):**
         - Satır 1 (115x15 mm): Doküman Kodu / Şifresi (`РД-2026-Ф2-КМ1-04`, 14px bold, ortalı).
         - Satır 2 (115x15 mm): Tesis / Kompleks / Şantiye Proje Adı ve Kadastro Adresi (çok satırlı metin).
         - Satır 3: Sol kutu (65 mm) Yapı / Bölüm Adı; Sağ kutu (50 mm) `Стадия`, `Лист`, `Листов` hücreleri.
         - Satır 4: Sol kutu (65 mm) Pafta Başlığı; Sağ kutu (50 mm) Kuruluş Adı ve Logo amblemi kutusu.
       - **Hızlı Araç Çubuğu:** "📋 Örnek KM Doldur" ve "🗑️ Temizle" butonları eklendi.
     - Herhangi bir alana yazıldığı anda `document_changed` sinyaliyle sağdaki CAD tuvali ve DXF verisi eşzamanlı güncellenmektedir.
  4. **Modüler Entegrasyon (`src/tables/title_block/module.py` & `src/tables/__init__.py`):**
     - `TitleBlockModule` sınıfı `TableModule` arayüzünü uyguladı ve `TableRegistry`'ye kaydedildi.
     - Notion Sidebar (`LinearSidebar`) ve Editor Wrapper üzerinde `🏷️` rozeti ile aktifleşti.
  5. **1:1 DXF ve Tuval Entegrasyonu (`src/export/dxf_exporter.py` & `src/ui/preview_canvas.py`):**
     - Tek başına (Standalone) antet çizimi ve dışa aktarımı sağlandı.
     - Sayfa Düzeni (`ABOVE_TITLEBLOCK` vb.) seçildiğinde sağ alt köşedeki Form 3 ana antet artık kullanıcının girdiği tam teşekküllü zengin antet olarak 1:1 CAD katmanlarında ve tuvalde çizilmektedir.
  6. **Kapsamlı Test Süiti (`tests/test_title_block.py`):**
     - 9 test ile model, validator, builder, WYSIWYG görsel editör ve DXF dışa aktarma doğrulandı. Tüm test süiti 86 teste ulaştı (%100 başarılı).

##### 🔹 [TASK-19] Veri Giriş Kutucukları İmleç ve Satır Yüksekliği İyileştirmesi — 🔍 Onay Bekliyor
- **İstek:** Veri girişi kutucukları imleçten küçük kalmış, metin yazarken imleç taşmakta ve hücreler basık kalmaktadır.
- **Yapılan İş:**
  1. `src/tables/title_block/editor.py` içerisindeki tüm metin giriş kutularının yükseklikleri ve fontları büyütüldü:
     - `txt_doc_code`: 38px (13px bold font, 8px padding)
     - `txt_project_name`, `txt_building_name`, `txt_sheet_title`: 66px (12px font, 8px padding)
     - `txt_stage`, `txt_sheet_num`, `txt_total_sheets`: 34px (13px bold font)
     - `txt_company_name`: 32px (12px bold font)
  2. Tablo satır yükseklikleri ferahlatıldı:
     - `tbl_signatories`: 32px satır yüksekliği (toplam 225px)
     - `tbl_revisions`: 29px satır yüksekliği (toplam 152px)
  3. `tests/test_ui_v2_tasks_verification.py` altındaki `test_task_19_title_block_input_sizes_and_row_heights` testiyle doğrulandı.

##### 🔹 [TASK-20] Canlı CAD Tuvalinde Gerçek CAD Fontu & Milimetrik Metin Ölçeklemesi (Resim 1) — 🔍 Onay Bekliyor
- **İstek:** Canlı CAD tuvalinde gerçek teknik CAD fontu görünmüyor, metinler harf ve satır sapmalarına uğruyor ve üst üste biniyor.
- **Yapılan İş:**
  1. `src/ui/preview_canvas.py` içindeki QFont küçültme hatası düzeltildi: 3pt font rasterizasyon çakışmalarını önlemek için 36px referans font oluşturuldu ve sahne koordinatlarında `setScale(font_h / ref_size)` ile milimetrik vektörel ölçekleme yapıldı.
  2. Birincil yazı tipi `ISOCPEUR` (GOST/ISO 3098 CAD standardı), yedek yazı tipi `Segoe UI` olarak tanımlandı.
  3. Metin hizalamaları ve satır aralıkları (`line_spacing = font_h * 1.3`) ile harf/satır sapmaları giderildi.

##### 🔹 [TASK-21] Canlı CAD Ekranında 2 Antetin Üst Üste Çıkması Hatasının Giderilmesi (Resim 2) — 🔍 Onay Bekliyor
- **İstek:** Title block seçildiğinde canlı CAD tuvalinde 2 adet antet üst üste binmektedir.
- **Yapılan İş:**
  1. `src/ui/preview_canvas.py` ve `src/export/dxf_exporter.py` içinde antet tablosu tespiti eklendi (`is_title_block`).
  2. Sayfa düzeninde antet tablosu çizilirken sayfa çerçevesinin çizdiği standart antet bastırıldı (`suppress_title_block=True`), tablo doğrudan sağ alt köşedeki Form 3 konumuna tek bir defa çizildi.
  3. Hem canlı CAD tuvalinde hem DXF çıktısında mükerrer antet oluşumu engellendi.

##### 🔹 [TASK-22] Sol Kenar Çubuğundaki Tablo Sayı Rozetlerinin Kaldırılması (Resim 3) — 🔍 Onay Bekliyor
- **İstek:** Tablolar sol sekmesindeki sayı rozetlerine (7, 6) gerek yoktur.
- **Yapılan İş:**
  1. `src/ui_v2/sidebar.py` içerisindeki `TableNavItem` yapısından sayı rozetleri (`lbl_badge`) kaldırıldı (`setVisible(False)`).
  2. Tablo listesi minimalist, temiz Linear / Notion navigasyon stiline kavuşturuldu.

##### 🔹 [TASK-23] Sol Kenar Çubuğu Tablo İsimlerinin Seçilen Dile Göre Dinamik Değişimi (Resim 3) — 🔍 Onay Bekliyor
- **İstek:** Sol menüdeki tablo isimleri seçilen dile (TR/EN/RU) göre dinamik olarak değişmelidir.
- **Yapılan İş:**
  1. `src/ui/i18n.py` içerisine `module_elements_schedule` ve `module_title_block` çeviri anahtarları TR, EN ve RU dillerinde eklendi.
  2. `LinearSidebar._on_language_changed` sinyaliyle üst barda dil değiştirildiği anda sol kenar çubuğundaki tüm tablo adları, bölüm başlıkları ve pafta parametreleri dinamik olarak güncellendi.

##### 🔹 [TASK-24] İlk Tablo İçin Pafta İçi Konumlandırma Seçenekleri (Ortalı, Sol/Sağ Üst) — 🔍 Onay Bekliyor
- **İstek:** İlk tabloda (Ведомость элементов) pafta içinde konumlandırma ayarı (Ortalı, Sol Üst, Sağ Üst, Antet Üstü) seçilebilmelidir.
- **Yapılan İş:**
  1. `src/config/sheet_config.py` içerisine `TablePlacement.TOP_LEFT` eklendi.
  2. `src/models/sheet.py` (`SheetLayoutCalculator`) içine `TOP_LEFT` milimetrik koordinat hesaplama mantığı eklendi.
  3. `LinearSidebar` pafta yerleşim ComboBox'ına tüm seçenekler (`ABOVE_TITLEBLOCK`, `TOP_RIGHT`, `TOP_LEFT`, `CENTER_SHEET`, `STANDALONE`) dile uygun etiketlerle bağlandı.

##### 🔹 [TASK-25] Title Block İçin Kurumsal Logo Yükleme Seçeneği (Resim Dosyası) — 🔍 Onay Bekliyor
- **İstek:** Title block içerisinde kullanıcının kendi kurumsal şirket logosunu yükleyebilme seçeneği bulunmalıdır.
- **Yapılan İş:**
  1. `TitleBlockDocument` veri modeline `logo_image_path` alanı eklendi (JSON serileştirme desteğiyle).
  2. `TitleBlockEditorWidget` arayüzüne "🖼️ Logo Seç" ve "✕ Kaldır" butonları ile logo dosya bilgisi etiketi eklendi.
  3. `SectionSketch(sketch_type=SketchType.LOGO_EMBLEM, image_path=...)` ile CAD tuvalinde QPixmap pürüzsüz ölçeklemesi ve DXF dışa aktarımında raster image / vektörel amblem entegrasyonu sağlandı.

##### 🔹 [TASK-26] DXF Dışa Aktarımında Metin Taşmalarının Önlenmesi (Auto Word-Wrap) (Resim 4) — 🔍 Onay Bekliyor
- **İstek:** DXF export alındığında uzun metinler (özellikle şantiye proje adı) kutulardan dışarı taşmaktadır.
- **Yapılan İş:**
  1. `src/models/text_layout.py` motoru geliştirildi (`wrap_cell_text` fonksiyonu).
  2. Hücre genişliği ve iç padding dikkate alınarak metinler GOST / ISO 3098 oranlarıyla otomatik kelime sınırlarından (`textwrap`) satırlara bölündü.
  3. Satır sayısı hücre yüksekliğini aştığında font boyutu dinamik olarak optimize edilerek hücre dışına taşma %100 önlendi.

##### 🔹 [TASK-27] Canlı CAD Tuvali ile DXF Çıktısının Birebir Özdeş Hale Getirilmesi (WYSIWYG) — 🔍 Onay Bekliyor
- **İstek:** Canlı CAD ekranında ne görünüyorsa DXF exportunda da birebir aynısı görünmelidir.
- **Yapılan İş:**
  1. Hem `preview_canvas.py` hem de `dxf_exporter.py` aynı `wrap_cell_text` algoritmasını ve aynı padding / line-spacing kurallarını kullanacak şekilde birleştirildi.
  2. Canlı CAD ekranında yapılan her değişiklik (metin, logo, yerleşim) DXF çıktısında milimetrik olarak birebir (%100 WYSIWYG) elde edildi.

##### 🔹 [TASK-28] Hücre İçi Düzenlemede Metin Çakışması/Üst Üste Binmesinin Giderilmesi — 🔍 Onay Bekliyor
- **İstek:** Title block tablosunda hücre içine metin yazarken veya düzenlerken eski metin ile yeni metin şeffaflık yüzünden üst üste binmekte ve harfler çakışmaktadır (kullanıcının ilettiği yeşil daireli ekran görüntüsü).
- **Yapılan İş:**
  1. `src/ui_v2/components.py` içerisine `SolidItemDelegate` geliştirildi:
     - `createEditor()` içinde açılan `QLineEdit` nesnesine solid opak koyu arka plan (`#1e2029`), kontrast beyaz metin, mor vurgulu odak kenarlığı (`#6366f1`) ve uygun padding/font atandı.
     - `initStyleOption()` ve `paint()` metodlarında hücre düzenleme durumundayken (`EditingState`), altındaki statik metin `option.text = ""` yapılarak tamamen gizlendi; böylece düzenleme esnasında alttaki metnin görünmesi imkansız hale getirildi.
  2. `TitleBlockEditorWidget` içerisindeki `tbl_signatories` ve `tbl_revisions` tablolarına `SolidItemDelegate` bağlandı.
  3. `tbl_signatories` sütun 0 ("Должность (Görev)") genişliği 92px'den 110px'e çıkarılarak ilk harfin (`Д`) kesilmesi önlendi.
  4. `ElementsScheduleWidget` içerisindeki `EngineeringTableWidget` tablosuna da `SolidItemDelegate` bağlanarak tüm tablolarda pürüzsüz Excel kalitesinde düzenleme sağlandı.
  5. `tests/test_ui_v2_tasks_verification.py` dosyasına `test_task_28_cell_editor_solid_background_and_no_text_overlap` testi eklendi.

##### 🔹 [TASK-29] Tablo Hücre İçi Düzenlemede İmlecin ve Metin Kutusunun Dikey Sıkışmasının Önlenmesi — 🔍 Onay Bekliyor
- **İstek:** Eleman listesi tablosunda veri girişi yapılırken düzenleme kutucuğu çok dar kalmakta ve imleç kutunun üst-alt kenarlarına yapışarak taşmaktadır ("burada da imlec veri girişne sığmıyor" - kullanıcının ilettiği 20К1 ekran görüntüsü).
- **Yapılan İş:**
  1. Sorunun temel kaynağı tespit edildi: Qt varsayılan `QStyledItemDelegate::updateEditorGeometry` mekanizması, CSS'teki `QTableWidget::item` padding değerini hücre yüksekliğinden düşerek 34px'lik satırdaki editörü 21px'e (içerik alanı 14px) sıkıştırmakta ve 18px imleç ile 13px metin kutuya sığmamaktaydı.
  2. `src/ui_v2/components.py` içindeki `SolidItemDelegate` sınıfına `updateEditorGeometry()` metodu eklendi:
     - `editor.setGeometry(rect.adjusted(1, 1, -1, -1))` formülü ile editörün hücrenin tüm dikey yüksekliğini (31px) kaplaması sağlandı.
     - `padding: 2px 8px; border: 1.5px solid {ACCENT_PRIMARY}; border-radius: 4px;` ile imlece üstten ve alttan rahat nefes payı kazandırıldı.
  3. `src/ui_v2/theme_linear.py` ve `src/tables/title_block/editor.py` içerisindeki `QTableWidget QLineEdit` stilleri tutarlı kılınarak hücre içi düzenleyicilerin yüksekliği 31px'e (Title Block imzalarında 29px) çıkarıldı.
  4. `tests/test_ui_v2_tasks_verification.py` dosyasına `test_task_29_cell_editor_geometry_and_cursor_height` testi eklendi.
  5. Toplam 96 testin tamamı (%100) başarıyla yeşile ulaştırıldı.

##### 🔹 [TASK-30] Metin Uzunluğuna Göre Otomatik Font Küçültme ve Maksimum Font Tavanı Kuralı — 🔍 Onay Bekliyor
- **İstek:** Hem canlı CAD tuvalinde hem de DXF exportunda metinlerin uzunluğuna göre kutucuklara sığacak şekilde ayarlanması gerekmektedir. Karakter boyu metin uzadıkça küçülebilmeli, ancak standartta tanımlı maksimum (tavan) değerinden kesinlikle daha büyük olmamalıdır (kullanıcının ilettiği `media_1791460742782_15109893.png` ekran görüntüsü).
- **Yapılan İş:**
  1. `src/models/text_layout.py` motoru baştan aşağı yenilendi:
     - `estimate_text_width_mm()`: ISO 3098 / ISOCPEUR / ГОСТ 2.304 standartlarına göre geniş Kiril harflerini (`№`, `Ж`, `Ш`, `Щ`, `Ю`, `Ф`, `М` vb.) ve noktalama işaretlerini milimetrik olarak tam hesaplayan oran tablosu geliştirildi (%5 emniyet payı ile).
     - `wrap_paragraph_to_width()`: Paragrafları ve tek başına genişliği aşan kelimeleri milimetrik sınırları asla aşmayacak şekilde satırlara bölen açgözlü (greedy) algoritma kuruldu.
     - `wrap_cell_text()`: Kullanıcının manuel satır sonlarını (`\n`) öncelikli koruyarak font küçültmeyi deneyen, sığmadığında otomatik word-wrap yapan ve hem satır genişliği (`max_line_w <= max_width_mm`) hem blok yüksekliği (`total_h <= max_height_mm`) koşullarını birlikte doğrulayan akıllı motor kodlandı.
     - **Maksimum Tavan Garantisi:** Font boyutu asla `target_font_size_mm` değerinin üzerine çıkamaz (kısa metinlerde hedef font korunur, uzun metinlerde güvenle küçülür).
  2. `src/ui/preview_canvas.py` ve `src/export/dxf_exporter.py` entegrasyonu:
     - Şirket logo alanı (`LOGO_EMBLEM`) bulunan hücrelerde metin için ayrılan kullanılabilir genişlik logo genişliği kadar düşürüldü ve metinler logoya çarpmayacak şekilde sağa yaslandı.
     - Canlı CAD ekranı ile DXF çıktısı arasında milimetrik metin yerleşimi ve font boyutları %100 özdeş (WYSIWYG) kılındı.
  3. `tests/test_ui_v2_tasks_verification.py` dosyasına `test_task_30_text_fitting_and_max_font_size_enforcement` testi eklendi.
  4. Test süitindeki 97 testin tamamı (%100) başarıyla yeşile ulaştırıldı.

##### 🔹 [TASK-31] ГОСТ 2.301-68 Pafta Formatı Alt Etiketi (Формат А1А, Формат А3А vb.) — 🔍 Onay Bekliyor
- **İstek:** Her sayfanın altında bulunan standart pafta format bilgisi (ГОСТ 2.301-68 ve СПДС standartları doğrultusunda, örn. `Формат А1А`, `Формат А3А`, `Формат А4`) eklenmelidir (kullanıcının ilettiği `media_1791461654975_df1a6c3d.png` ekran görüntüsü).
- **Yapılan İş:**
  1. `src/config/sheet_config.py` içerisindeki `LayoutConfig` sınıfına `get_format_designation()` metodu eklendi:
     - ГОСТ 2.301-68 ve СПДС (nanoCAD/AutoCAD СПДС) standart kurallarına göre pafta boyutu ve yönelimine bağlı olarak etiket üretildi: Yatay paftalarda sonuna Kiril `А` eklenir (A1 Yatay -> `Формат А1А`, A3 Yatay -> `Формат А3А`), Dikey paftalarda sade format yazılır (A4 Dikey -> `Формат А4`).
  2. `src/export/dxf_exporter.py` motoruna entegre edildi:
     - `_draw_sheet_frames_only` metodu güncellendi: Pafta iç çerçeve alt kenarı ile sayfa dış sınırı arasındaki 5.0 mm'lik marjinde ($Y = 2.5\text{ mm}$), Form 3 antetinin sağındaki 50 mm'lik şirket unvanı kutusunun tam ortasına ($X = \text{inner\_frame.x\_max} - 25.0\text{ mm}$) `MIDDLE_CENTER` hizalamalı, 2.5 mm font yüksekliğinde `ISOCPEUR` (`KM_TABLO_METIN`) metni eklendi.
  3. `src/ui/preview_canvas.py` canlı CAD tuvaline entegre edildi:
     - `_draw_sheet` içerisinde aynı koordinatlarda ($X = f.x\_max - 25.0\text{ mm}$, $Y = 2.5\text{ mm}$) font metrikleri (`QFontMetricsF`) ve gerçek CAD oranlarıyla canlı olarak çizildi; DXF ile canlı CAD arasında %100 WYSIWYG uyum korundu.
  4. `tests/test_ui_v2_tasks_verification.py` dosyasına `test_task_31_sheet_format_label_under_frame` testi eklenerek format türetme kuralları, DXF metin varlığı/konumu ve canlı tuval sahnesi doğrulandı.
  5. Test süitindeki 98 testin tamamı (%100) başarıyla yeşile ulaştırıldı.

##### 🔹 [TASK-32] ГОСТ 2.104 / ГОСТ Р 21.101 Sol Kenar Boşluğu Ek Tabloları (İnventar & Согласовано) — 🔍 Onay Bekliyor
- **İstek:** Çizim paftalarının sol kenar boşluğunda (20 mm ciltleme / delgeç payı) yer alan standart yan şerit tabloları (İnventar Bilgileri ve Согласовано) standartlara tam uygun şekilde paftaya eklenmelidir; bağımsız bir tablo modülü olarak değil, doğrudan pafta çerçevesi bileşeni olarak çizilmelidir (kullanıcının ilettiği `media_1791462831724_1ddba5bc.png` ekran görüntüsü).
- **Standart & Mühendislik Detayı (ГОСТ 2.104-2006 & ГОСТ Р 21.101-2020):**
  1. **Tablo 1: İnventar Bilgileri (İç Çerçeve Sol Alt Köşesinden $Y=5\text{ mm}$'den Başlar):**
     - Ölçüler: $85\text{ mm}$ boy, $12\text{ mm}$ en ($5\text{ mm}$ metin bandı + $7\text{ mm}$ boş kayıt alanı).
     - Hücreler:
       - `Инв. № подл.` ($25\text{ mm}$ boy)
       - `Подп. и дата` ($35\text{ mm}$ boy)
       - `Взам. инв. №` ($25\text{ mm}$ boy)
  2. **Tablo 2: Согласовано Tablosu (Doğrudan Tablo 1'in Üzerinde $Y = 90\text{ mm}$ ila $155\text{ mm}$):**
     - Ölçüler: $65\text{ mm}$ boy, $15\text{ mm}$ en ($5\text{ mm}$ başlık bandı + $2 \times 5\text{ mm}$ satır).
     - Hücreler:
       - Başlık: `Согласовано` ($65\text{ mm}$ boy, tek parça birleşik).
       - Alt Izgara: $20\text{ mm}$, $20\text{ mm}$, $15\text{ mm}$, $10\text{ mm}$ boylarında 4 kolon $\times$ 2 satır.
  3. **Rotasyon ve Font:**
     - Metinler saat yönünün tersine 90° açıyla döndürülerek ($+90^\circ$ / dikey okuma) $2.5\text{ mm}$ `ISOCPEUR` fontunda tam ortalanmıştır.
- **Yapılan İş:**
  1. `src/export/dxf_exporter.py`: `_draw_sheet_frames_only` içerisine `_draw_side_stamps(msp, f)` metodu entegre edildi. Kalın çerçeveler `LAYER_SHEET_FRAME` (0.50 mm), iç ızgaralar `LAYER_GRID` (0.15 mm), metinler `LAYER_TEXT` katmanında 1:1 ölçekle çizildi.
  2. `src/ui/preview_canvas.py`: `_draw_sheet` içerisine `_draw_side_stamps(f)` metodu entegre edildi. `QTransform` kullanılarak 90° açıyla döndürülmüş ve hassas merkezlenmiş vektör çizimi sağlandı.
  3. `tests/test_ui_v2_tasks_verification.py`: `test_task_32_sheet_left_binding_margin_side_stamps` testi kodlandı. DXF çıktısındaki 4 metin, 90° rotasyon ve canlı CAD tuval sahne varlığı doğrulandı.
##### 🔹 [TASK-33] ГОСТ Р 21.101 Form 2 Referans ve Ek Dokümanlar Tablosu & Çok Dilli Standartlar Kütüphanesi — 🔍 Onay Bekliyor
- **İstek:** Kullanıcı "Ведомость ссылочных и прилагаемых документов" tablosunun (ГОСТ Р 21.101 Form 2) eklenmesini; kullanıcının hazır standartları seçebilmesini, kendi standartlarını ekleyebilmesini, standartların okunmasını kolaylaştırmak için Rusça başlığın yanında **Türkçe ve İngilizce karşılıklarının** görünmesini; standartları kütüphaneye ekleyebilme, düzenleyebilme ve silebilme (CRUD) yeteneğini talep etti.
- **Mühendislik & ГОСТ Form 2 Standart Detayı:**
  1. **Tablo Geometrisi:**
     - Toplam genişlik $185.0\text{ mm}$ (ГОСТ 21.101 Form 3 ana antet ile tam aynı genişlikte olup antetin hemen üstüne veya paftaya milimetrik kilitlenir).
     - Sütunlar: `Обозначение` ($60.0\text{ mm}$), `Наименование` ($95.0\text{ mm}$), `Примечание` ($30.0\text{ mm}$).
     - Başlık: 1. satır tüm sütunları kapsayan $185\text{ mm}$ genişliğinde birleşik hücre: `Ведомость ссылочных и прилагаемых документов` ($12.0\text{ mm}$ yükseklik, $3.5\text{ mm}$ bold font).
     - Bölüm Ayraçları: `Ссылочные документы` ve `Прилагаемые документы` orta sütunda ortalı veya ayrılmış olarak çizilir.
- **Yapılan İş:**
  1. **Veri Modelleri (`src/tables/reference_documents/model.py`):**
     - `ReferenceDocItem`: Kod (`designation`), Rusça başlık (`title`), Türkçe karşılığı (`title_tr`), İngilizce karşılığı (`title_en`), bölüm (`section`), not (`note`), `is_section_header`.
     - `StandardLibraryItem`: Kütüphanede saklanan standart kartı (Kod, RU, TR, EN, Bölüm, Kategori, Not).
     - `ReferenceDocsDocument`: Tablo dokümanı modeli.
  2. **Kalıcı JSON Kütüphane Yöneticisi (`src/tables/reference_documents/library.py`):**
     - Kullanıcının görselinde yer alan **14 adet temel KM çelik standardı** (ГОСТ 27751-2014, СП 16.13330.2017, СП 20.13330.2016, СП 28, СП 48, СП 70, СП 72, СТО АРСС, СП 470, ГОСТ 23118-2019, СНиП 12-03, СНиП 12-04, СП 112, ФЗ №123-ФЗ) ve ilave temel standartlar (ГОСТ 21.502, ГОСТ Р 21.101, sac, profil ve ek dokümanlar) RU, TR ve EN zengin karşılıklarıyla varsayılan olarak tanımlandı.
     - `StandardsLibraryManager`: CRUD (Ekle, Güncelle, Sil, Listele, Arama, Sıfırla) ve `standards_library.json` kalıcı dosya kaydı geliştirildi.
  3. **CAD Tablo İnşa Edicisi (`src/tables/reference_documents/builder.py`):**
     - 1:1 ölçekli, 3 sütunlu ($60, 95, 30\text{ mm}$), üst başlığı iç çerçeveye kilitli Form 2 CAD `Table` modeli üretildi.
  4. **Kütüphane Yönetim Modalları (`src/tables/reference_documents/dialogs.py`):**
     - `StandardsLibraryDialog`: Arama filtreli (Kod, RU, TR, EN), kategori filtreli, genişletilmiş çoklu seçimli kütüphane tarayıcısı. "Tabloya Aktar", "Yeni Ekle", "Düzenle", "Sil", "Varsayılanlara Sıfırla" aksiyonları.
     - `StandardEditDialog`: Standart kodu, Rusça başlık, Türkçe ve İngilizce karşılık, bölüm ve kategori giriş formu.
  5. **Veri Giriş Editörü (`src/tables/reference_documents/editor.py`):**
     - 6 sütunlu (`Обозначение`, `Наименование RU`, `Türkçe Karşılığı TR`, `English Title EN`, `Раздел`, `Примечание`), Excel kısayollu (Tab, Enter, F2, Ctrl+C/V), `SolidItemDelegate` opak zeminli modern Notion/Linear gridi.
     - Hızlı araç çubuğu: "📚 Standart Kütüphanesi", "＋ Doküman Ekle", "📑 Bölüm Ekle", "🗑️ Sil", "▲/▼ Taşı", "📋 Hazır KM Standartları", "🗑️ Temizle".
     - Kod yazıldığında kütüphaneden RU/TR/EN başlıklarını otomatik tamamlama (auto-fill).
  6. **Sistem Entegrasyonu:**
     - `ReferenceDocsModule` `TableModule` sözleşmesini uygulayarak `TableRegistry`'ye kaydedildi.
     - Sol kenar çubuğunda `📚` rozeti ile aktifleşti, Quick Switcher (Ctrl+T / Ctrl+K) ve TopBar'a bağlandı.
     - 1:1 DXF dışa aktarımı doğrulandı.
  7. **Kapsamlı Test Süiti (`tests/test_reference_docs.py`):**
     - 8 yeni test (Model, Kütüphane CRUD, Görseldeki 14 standardın doğrulaması, Builder, Validator, Editor, DXF) yazıldı.
     - Toplam 107 testin tamamı (%100) başarıyla yeşile ulaştırıldı.

##### 🔹 [TASK-34] Standart Kodlarının Hücrede Ortalanması & Çok Satırlı İsimlerde Dinamik Font Küçültme — 🔍 Onay Bekliyor
- **İstek:** Canlı CAD'de ve DXF'te standart kodları (Обозначение) hücre içinde ortalanmalı. Çok uzun isimlerde font küçültülebilmeli, alt satıra geçebilmeli ve maksimum yazı boyutu standartlardan alınmalı (kullanıcının ilettiği `media_1791466106335_70bcd482.png` ekran görüntüsü).
- **Tespit Edilen Kök Nedenler:**
  1. `src/tables/reference_documents/builder.py` içerisinde 18 karakterden uzun kodlar (`СТО АРСС 11251254.001-018-5`, `СП 470.1325800.2019`) sola yaslanıyordu (`HAlign.LEFT`).
  2. `wrap_cell_text` fonksiyonunda 2 satırlı metinlerin blok yüksekliği hesabında descender ve satır aralığı marjini nominal harf boyundan hesaplandığı için 2. satır hücrenin alt ızgara çizgisine temas ediyordu/taşıyordu.
  3. `src/ui/preview_canvas.py` içerisinde `cur_y = cy_top + (ch - total_h) / 2.0` hesabında `total_h` metin item yüksekliği yerine sadece `font_h` içerdiği için çok satırlı bloklar aşağıya doğru kayarak alt çizgiye biniyordu.
- **Yapılan İş:**
  1. **Tüm Kodların Ortalanması (`src/tables/reference_documents/builder.py`):**
     - İstisnasız tüm standart kodları (`item.designation`) `halign=HAlign.CENTER` olarak ayarlandı.
  2. **Maksimum Font Tavanı ve Dinamik Küçültme (`src/models/text_layout.py`):**
     - `estimate_block_height(lines, font_h)` fonksiyonu entegre edildi: Tek satırlarda standart tavan font ($2.5\text{ mm}$) korunurken, 2 satırlı uzun başlıklarda font boyutu otomatik olarak $\sim 2.15 - 2.25\text{ mm}$ seviyesine optimize edilerek hücre dikey alanına tam sığması sağlandı.
  3. **Milimetrik Simetrik Dikey Merkezleme (`src/ui/preview_canvas.py` & `src/export/dxf_exporter.py`):**
     - Tuvalde `actual_total_h = (len - 1) * line_spacing + (fm.height() * scale_factor)` formülü ile üst ve alt kenar boşlukları kusursuz simetrik hale getirildi; çizgiye binme %100 önlendi.
     - DXF exportunda da aynı `line_spacing = font_h * 1.25` katsayısı kullanılarak canlı CAD ile DXF %100 özdeş (WYSIWYG) kılındı.
  4. **Doğrulama Testleri (`tests/test_reference_docs.py`):**
     - `test_all_designations_centered_and_long_name_font_scaling` testi kodlanarak kodların ortalanması, tek satırlarda 2.5 mm tavan fontun korunması ve çok satırlarda fontun küçülerek blok yüksekliğinin hücreyi aşmaması doğrulandı.
  5. Toplam 108 testin tamamı (%100) başarıyla yeşile ulaştırıldı.

##### 🔹 [TASK-35] ГОСТ Р 21.101 Form 2 'Ведомость основных комплектов рабочих чертежей' Modülü & Manuel Veri Editörü — 🔍 Onay Bekliyor
- **İstek:** Kullanıcı, "Ведомость основных комплектов рабочих чертежей" (Temel Çalışma Çizimleri Takımları Listesi) tablosunun sisteme eklenmesini ve buradaki verilerin kullanıcı tarafından tamamen manuel girilebilmesini talep etti (`media_1791468077813_b3c7f992.png` referans ekran görüntüsü).
- **Mühendislik & ГОСТ Form 2 Standart Detayı:**
  1. **Standart & Geometri:**
     - Standart: **ГОСТ Р 21.101-2020** (Приложение В, Форма 2).
     - Toplam Genişlik: $185.0\text{ mm}$ (ГОСТ Form 3 ana antet ile tam aynı genişlikte, antet üzerine veya paftanın istenen konumuna milimetrik kilitlenir).
     - Sütunlar:
       - `Обозначение`: $60.0\text{ mm}$ (Çizim takımı pozisyon kodu / desig, örn: `РД-2026-П-КМ1-01`). Hücre içinde yatayda tam ortalı (`HAlign.CENTER`).
       - `Наименование`: $95.0\text{ mm}$ (Takım adı ve bina kat açıklaması). Sola yaslı (`HAlign.LEFT`), çok satırlı metin sarımı (word-wrap).
       - `Примечание`: $30.0\text{ mm}$ (Mühendislik notları). Hücre içinde ortalı (`HAlign.CENTER`).
     - Başlık: Tablonun üst sınırının üzerinde, ortalı $3.5\text{ mm}$ bold metin: `Ведомость основных комплектов рабочих чертежей`. DXF ve canlı CAD tuvalinde otomatik üretilir.
     - Satır Yükseklikleri: Başlık satırı $15.0\text{ mm}$ (standart ГОСТ Form 2 yüksekliği); veri satırları en az $8.0\text{ mm}$ ve çok satırlı metinlerde harflerin sıkışmaması için kelime sayısına göre dinamik hesaplanan satır yüksekliği ($11\text{ mm}$, $15\text{ mm}$ vb.).
- **Yapılan İş:**
  1. **Veri Modelleri (`src/tables/main_drawings/model.py`):**
     - `DrawingSetItem`: `designation`, `name`, `note` alanları ve serileştirme (`to_dict` / `from_dict`).
     - `MainDrawingsDocument`: Kullanıcının ilettiği referans görseldeki **12 satırlık gerçek KM proje verisi** (`РД-2026-П-КМ1-01`'den `РД-2026-Ф2-КМ1-04`'e kadar) başlangıç varsayılanı olarak modellendi.
  2. **Ölçü ve Konfigürasyon (`src/tables/main_drawings/config.py`):**
     - $60, 95, 30\text{ mm}$ sütun genişlikleri, $15\text{ mm}$ başlık yüksekliği, $8\text{ mm}$ minimum satır boyutu ve GOST tipografi parametreleri tanımlandı.
  3. **CAD Tablo İnşa Edicisi (`src/tables/main_drawings/builder.py`):**
     - 1:1 ölçekli CAD `Table` modeli, tablo dışı üst başlık, dinamik kelime sarımlı satır yüksekliği hesabı ve hücre hizalamaları üretildi.
  4. **Doğrulayıcı (`src/tables/main_drawings/validator.py`):**
     - Boş tablo ve eksik alan kontrolleri yapıldı.
  5. **Manuel Veri Giriş Editörü (`src/tables/main_drawings/editor.py`):**
     - Tamamen manuel girişe odaklı Notion/Linear gridi: Çift dilli başlıklar (`Обозначение\n(Tanım / Kod)`, `Наименование\n(Adı / Açıklama)`, `Примечание\n(Not / Açıklama)`).
     - `SolidItemDelegate` ile düzenleme esnasında opak zemin, metin çakışmasının engellenmesi ve geniş imleç alanı.
     - Hızlı eylem araç çubuğu: "＋ Çizim Takımı Ekle" (zümrüt yeşili), "🗑️ Sil" (kırmızı), "▲/▼ Taşı", "📋 Örnek Verileri Yükle" (görseldeki 12 satırı yeniden yükleme), "🧹 Temizle".
     - Klavye navigasyonu (Enter -> alt satır, Tab -> yan sütun, F2 -> hücre düzenleme, Delete -> hücre içeriğini silme).
     - Excel & Google Sheets uyumlu TSV kopyala/yapıştır (Ctrl+C, Ctrl+V) ve sağ tık bağlam menüsü.
  6. **Sistem Entegrasyonu:**
     - `MainDrawingsModule` `TableModule` sözleşmesiyle `TableRegistry`'ye otomatik kaydedildi (`src/tables/main_drawings/__init__.py`).
     - `src/tables/__init__.py` paketine dahil edildi.
     - `src/ui/i18n.py` içerisine TR, EN ve RU dil çevirileri eklendi.
     - `LinearSidebar` üzerinde `📑` ikonlu gezinme öğesi ve `TableEditorWrapper` başlık/alt başlık entegrasyonu tamamlandı.
  7. **Kapsamlı Test Süiti (`tests/test_main_drawings.py`):**
     - 9 yeni test (Model, Serileştirme, Konfigürasyon, Builder, Dinamik Satır Boyutlandırma, Validator, Registry, DXF Export, Editor Widget CRUD) kodlandı.
     - Toplam 117 testin tamamı (%100) başarıyla yeşile ulaştırıldı.

---

##### 🔹 [TASK-36] ГОСТ Р 21.101 Form 1 'Ведомость рабочих чертежей основного комплекта' Modülü & Manuel Veri Editörü — 🔍 Onay Bekliyor
- **İstek:** Kullanıcı "Ведомость рабочих чертежей основного комплекта" (Ana Takım Çalışma Çizimleri / Pafta Listesi) tablosunun eklenmesini, şimdilik verilerin manuel girilebilmesini, ileride programın PDF dosyalarından okuyarak bu tabloyu otomatik oluşturacağını belirtti.
- **Mühendislik & ГОСТ Form 1 Standart Detayı:**
  1. **Standart & Geometri:**
     - Standart: **ГОСТ Р 21.101-2020** (Приложение В, Форма 1).
     - Toplam Genişlik: $185.0\text{ mm}$ (ГОСТ Form 3 ana antet ile tam aynı genişlikte olup antetin hemen üstüne veya paftaya milimetrik oturur).
     - Sütunlar:
       - `Лист` (Pafta / Çizim No): $15.0\text{ mm}$ (ortalı)
       - `Наименование` (Çizim Adı / Başlık): $140.0\text{ mm}$ (sola dayalı)
       - `Примечание` (Not / Açıklama): $30.0\text{ mm}$ (ortalı)
       - Toplam: $15 + 140 + 30 = 185.0\text{ mm}$.
  2. **Satır Yükseklikleri & Tipografi:**
     - Başlık Satırı: $15.0\text{ mm}$ yükseklik, $3.0\text{ mm}$ bold font (`Лист`, `Наименование`, `Примечание`).
     - Tablo Dışı Üst Başlık: `Ведомость рабочих чертежей основного комплекта` ($3.5\text{ mm}$ bold font, tablonun üst sınırında).
     - Veri Satırları: Minimum $8.0\text{ mm}$, çok satırlı metinlerde dinamik kelime sarımına göre otomatik genişleyen satır yüksekliği ($2.5\text{ mm}$ ISOCPEUR CAD fontu).
- **Yapılan İş:**
  1. **Veri Modeli (`src/tables/working_drawings/model.py`):**
     - `WorkingDrawingItem`: `sheet_number`, `name`, `note`, `to_dict()`, `from_dict()`.
     - `get_default_sample_items()`: Kullanıcının referans görselindeki **10 adet gerçek KM pafta satırı** (`1: Общие данные`, `2.1: Общие указания (начало)`, `2.2: Общие указания (окончание)`, `3: Спецификация металлопроката`, `4: Схема расположения...`, `5: Разрезы 1-1...9-9`, `6: Разрезы 10-10...19-19`, `7: Монтажный стык...`, `8: Узлы изменения сечения колонн...`, `9: Сечения сердечников...`).
     - `WorkingDrawingsDocument`: `populate_from_items`, `append_item`, `clear_items` fonksiyonlarıyla gelecekte eklenecek PDF ayrıştırıcıları için genişletilebilir açık mimari kuruldu.
  2. **Parametrik CAD İnşa Edicisi (`src/tables/working_drawings/builder.py`):**
     - 1:1 ölçekli CAD `Table` modeli, tablo dışı üst başlık, dinamik kelime sarımlı satır yüksekliği hesabı ve milimetrik hücre hizalamaları üretildi.
  3. **Doğrulayıcı (`src/tables/working_drawings/validator.py`):**
     - Boş tablo, boş satırlar ve yinelenen pafta numaraları kontrolleri kodlandı.
  4. **Manuel Veri Giriş Editörü (`src/tables/working_drawings/editor.py`):**
     - Tamamen manuel girişe odaklı Notion/Linear gridi: Çift dilli başlıklar (`Лист\n(Pafta No)`, `Наименование\n(Çizim Adı)`, `Примечание\n(Not)`).
     - `SolidItemDelegate` ile opak zemin, metin çakışmasının engellenmesi ve geniş imleç alanı.
     - Hızlı eylem araç çubuğu: "＋ Pafta Ekle" (zümrüt yeşili), "🗑️ Sil" (kırmızı), "▲/▼ Taşı", "📋 Örnek KM Doldur" (görseldeki 10 satırı yeniden yükleme), "📄 PDF'ten Aktar (Yakında)" (gelecek özellik ipuçlu buton), "🧹 Temizle".
     - Klavye navigasyonu (Enter -> alt satır, Tab -> yan sütun, F2 -> hücre düzenleme, Delete -> hücre içeriğini silme).
     - Excel & Google Sheets uyumlu TSV kopyala/yapıştır (Ctrl+C, Ctrl+V) ve sağ tık bağlam menüsü.
  5. **Sistem Entegrasyonu:**
     - `WorkingDrawingsModule` `TableModule` sözleşmesiyle `TableRegistry`'ye otomatik kaydedildi (`src/tables/working_drawings/__init__.py`).
     - `src/tables/__init__.py` paketine dahil edildi.
     - `src/ui/i18n.py` içerisine TR, EN ve RU dil çevirileri eklendi.
     - `LinearSidebar` üzerinde `📋` ikonlu gezinme öğesi ve `TableEditorWrapper` başlık/alt başlık entegrasyonu tamamlandı.
  6. **Kapsamlı Test Süiti (`tests/test_working_drawings.py`):**
     - 10 yeni test (Model, Serileştirme ve PDF Arayüzü, Konfigürasyon, Builder, Dinamik Satır Boyutlandırma, Validator, Registry, DXF Export, Editor Widget CRUD, UI Entegrasyonu) kodlandı.
     - Toplam 127 testin tamamı (%100) başarıyla yeşile ulaştırıldı.


##### 🔹 [TASK-37] Zadax.net Web Sitesi Bağlantısı ve Versiyon Güncelleme Bildirimi (Manuel İndirme) — 🔍 Onay Bekliyor
- **İstek:** About sayfasına `www.zadax.net` ibaresinin eklenmesi; otomatik arka plan indirmesi yapılmayıp yalnızca sürüm kontrolü yapılması; yeni sürüm çıktığında kullanıcıya bilgi verilmesi ve isterse `zadax.net` ürün bağlantısını tarayıcıda açıp manuel indirmesi seçeneğinin sunulması.
- **Yapılan İş:**
  1. **Merkezi Sürüm & Ürün Meta Verileri (`src/version.py`):**
     - `APP_NAME`, `APP_VERSION` ("1.2.0"), `COMPANY_NAME` ("Zadax"), `COMPANY_WEBSITE` ("https://www.zadax.net"), `COMPANY_DISPLAY_URL` ("www.zadax.net"), `DEFAULT_UPDATE_CHECK_URL` ("https://www.zadax.net/updates/km-layout-tables/version.json").
  2. **Versiyon Kontrol Servisi (`src/services/updater.py`):**
     - `parse_version`: Semantik sürüm ayrıştırma ("1.2.0" -> (1, 2, 0), "1.10.0" > "1.2.0").
     - `is_version_newer`: Yerel sürüm ile uzak sürüm karşılaştırması.
     - `UpdateInfo`: Sürüm, yayın tarihi, `product_url`, sürüm notları (changelog) veri sınıfı.
     - `UpdateCheckWorker (QThread)`: Arayüzü dondurmadan arka planda zadax.net JSON endpoint'ini sorgulayan iş parçacığı.
  3. **Hakkında Diyaloğu Entegrasyonu (`src/ui_v2/about_dialog.py`):**
     - Üst kartta `🌐 www.zadax.net` tıklanabilir buton bağlantısı (`QDesktopServices.openUrl`).
     - Zadax.net Versiyon Kontrol Paneli: "🔄 Güncellemeleri Denetle" butonu.
     - Canlı durum bildirimi ("Yazılımınız güncel" veya "🚀 Yeni sürüm mevcut: v1.3.0").
     - Yeni sürüm varsa: Kullanıcıya diyalog ile soru ("Yeni sürüm yayınlandı! Zadax.net ürün sayfasını açmak ister misiniz?") ve "🌐 zadax.net'te Ürün Sayfasını Aç (İndir)" butonu.
     - Tıklandığında doğrudan web tarayıcısında Zadax ürün/indirme sayfası açılarak kullanıcının manuel indirmesi sağlanır.
  4. **Kapsamlı Test Süiti (`tests/test_updater_and_about.py`):**
     - 5 birim ve arayüz testi yazıldı (Meta veriler, Semantik karşılaştırma, Worker mock yanıtları, Network hatası, UI buton ve tarayıcı yönlendirme akışları).
     - Toplam 132 testin tamamı (%100) başarıyla yeşile ulaştırıldı.

##### 🔹 [TASK-38] QtAwesome Vektörel İkon Altyapısı (Solid fa5s & Regular fa5r/fa5) — 🔍 Onay Bekliyor
- **İstek:** Arayüzdeki emojiler yerine modern `qtawesome` kütüphanesinin entegre edilmesi; Butonlar ve araç çubuklarında Solid (`fa5s`), hafif arayüz ve doküman sekmelerinde Regular (`fa5r`/`fa5`) ikonların kullanılması; 18-22 px boyut ve nötr gri / vurgulu mavi renk paleti uygulanması.
- **Yapılan İş:**
  1. **Merkezi İkon Modülü (`src/ui_v2/icons.py`):**
     - Font Awesome 5 Free Solid (`fa5s.*`) ve Regular (`fa5.*` / `fa5r.*` alias desteği) entegrasyonu.
     - Standart renkler: `COLOR_NEUTRAL` (`#9ca3af`), `COLOR_MUTED` (`#646979`), `COLOR_ACCENT_BLUE` (`#3b82f6`), `COLOR_PRIMARY` (`#5e6ad2`), `COLOR_SUCCESS` (`#10b981`), `COLOR_DANGER` (`#ef4444`).
     - Standart boyutlar: 18-22 px (`DEFAULT_SIZE = 18`, `icon_size()`).
  2. **TopBar & Sidebar Entegrasyonu:**
     - TopBar: Kenar çubuğu (`fa5s.bars`), arama (`fa5s.search`), hakkında (`fa5s.info-circle`), DXF export (`fa5s.bolt`).
     - Sidebar: Çalışma alanı (`fa5s.drafting-compass`), doküman sekmeleri (`fa5.file-alt`, `fa5.id-badge`, `fa5.bookmark`, `fa5.clipboard`, `fa5.copy` Regular hafif ikonlar).
  3. **About Dialog & Tablo Editörleri:**
     - About: Güncelleme denetle (`fa5s.sync-alt`), Kapat (`fa5s.times`), web bağlantıları (`fa5s.globe`, `fa5s.external-link-alt`).
     - Editör Araç Çubuğu: Eleman Ekle (`fa5s.plus`), Sil (`fa5s.trash-alt`), Yukarı/Aşağı (`fa5s.arrow-up`, `fa5s.arrow-down`), Örnekler (`fa5s.sync-alt`).
  4. **Test Süiti (`tests/test_icons.py`):**
     - 4 yeni birim testi eklendi (Kütüphane varlığı, Solid ikonlar, Regular/alias ikonlar, Boyut ve renk standartları).
     - Toplam 136 testin tamamı (%100) başarıyla yeşile ulaştırıldı.

##### 🔹 [TASK-39] DXF Dışa Aktar Butonuna Sağdan Sola Jilet Parıltısı Animasyonu — 🔍 Onay Bekliyor
- **İstek:** "dxf'e aktar butonu şöyle sağdan sola parlayan animasyon yap. jilet gibi" — Kullanıcı, üst gezinme çubuğundaki ana eylem butonu olan "DXF Dışa Aktar" butonuna sağdan sola doğru akan, jilet gibi keskin ve estetik bir parıltı (shimmer sheen sweep) animasyonu eklenmesini talep etti.
- **Tasarım & Teknik Çözüm:**
  1. **`LinearShimmerButton` Sınıfı (`src/ui_v2/components.py`):**
     - Standart `QPushButton`'dan türetildi; yerel odak, tık mekanizmaları, ikon ve metin desteği %100 korundu.
     - **Sağdan Sola Süpürme:** Normalleştirilmiş koordinat $X$, `1.4` (sağ dış sınır) değerinden `-0.4` (sol dış sınır) değerine doğru akar.
     - **Jilet Kesim Açısı:** $22.0^\circ$ dinamik eğim ile kılıç/bıçak yansıması geometrisi.
     - **Jilet Gibi Keskin Yansıma Profili:** Geniş ve bulanık bir sis yerine, merkezde $1.36\text{ px}$ genişliğinde saf opak beyaz tepe noktası (`alpha = 255`), $5.4\text{ px}$ sıkı yansıma geçişi (`alpha = 220 \to 110`) ve dışta hafif bir aura (`alpha = 25`) kullanıldı.
     - **Kenarlık Kenetlenmesi:** `QPainterPath` ile butonun $6\text{ px}$ yuvarlatılmış köşelerine kusursuz kenetlenerek taşmalar önlendi.
     - **Akıcı Ritim & Easing:** `QEasingCurve.Type.InOutCubic`, $800\text{ ms}$ süpürme hızı, $3.2\text{ s}$ bekleme döngüsü.
     - **Hover Tetikleyicisi:** Fare butonun üzerine geldiğinde (`enterEvent`) bekleme sayacı sıfırlanıp parıltı anında tetiklenerek interaktif SaaS hissi sağlandı.
  2. **TopBar Entegrasyonu (`src/ui_v2/top_bar.py`):**
     - `self.btn_export = LinearShimmerButton(" DXF Dışa Aktar")` olarak bağlandı.
     - `fa5s.bolt` ikonu ve `#primaryButton` Linear stili aynen korundu.
  3. **Birim Testler (`tests/test_ui_v2.py`):**
     - `test_linear_shimmer_button_properties_and_direction` ve `test_top_bar_uses_shimmer_button` testleri eklendi.
  4. Toplam 138 testin tamamı (%100) başarıyla yeşile ulaştırıldı.

##### 🔹 [TASK-40] CAD Ekranının Açılıp Kapatılabilir (Collapsible/Toggle) Yapılması (Default Açık) — 🔍 Onay Bekliyor
- **İstek:** "cad ekranını da kapatılıp açılabilir hale getirelin. defaoult açık kalsın" — Kullanıcı, CAD önizleme tuvalinin istenildiğinde gizlenip açılabilmesini, varsayılan olarak açık kalmasını talep etti.
- **Tasarım & Teknik Çözüm:**
  1. **Varsayılan Durum:** CAD ekranı (`cad_panel`) varsayılan olarak açık (`isHidden() == False`), %42 Editör - %58 CAD oranlarında başlatılır.
  2. **LinearTopBar Entegrasyonu (`src/ui_v2/top_bar.py`):**
     - Üst gezinme çubuğuna `btn_toggle_cad` (" CAD Ekranı", `fa5s.desktop`) butonu eklendi.
     - Açıkken aktif mor/yüzey dolgusu ve mavi ikon (`#3b82f6`), kapalıyken kesikli çerçeve ve pasif gri ikon ile anlık durum bildirimi sağlar.
     - Çift dilli çeviri desteği (`i18n.t("btn_cad_panel")`).
  3. **Floating HUD Entegrasyonu (`src/ui_v2/cad_panel.py`):**
     - Canlı CAD tuvalinin altındaki yüzen HUD hapına küçük kapatma butonu (`btn_close`, `fa5s.times`) eklendi.
  4. **Klavye Kısayolları (`src/ui_v2/window.py`):**
     - `Ctrl+J` ve `F10` kısayolları doğrudan CAD ekranını açıp kapatmaya bağlandı.
  5. **Akıllı Splitter Hafızası:**
     - Kapatıldığında kullanıcının mevcut bölücü genişlik oranları (`_saved_splitter_sizes`) hafızaya alınır, tablo editörü tam ekran genişliğini alır.
     - Tekrar açıldığında hafızadaki oranlar birebir geri yüklenir ve `fit_to_view()` ile CAD çizimi tuvale anında ortalanarak sığdırılır.
  6. **Birim Testler (`tests/test_ui_v2.py`):**
     - `test_ui_v2_cad_panel_toggle_and_default_state` testi eklendi (default açık olma, TopBar butonuyla kapatıp açma, HUD butonuyla kapatma ve metot testi).
  7. Toplam 139 testin tamamı (%100) başarıyla yeşile ulaştırıldı.

##### 🔹 [TASK-41] Hızlı Arama (Ctrl+K) Tablo İsimleri Senkronizasyonu & Kenar Çubuğu Menüsü — 🔍 Onay Bekliyor
- **İstek:** 
  1. "işretli buton ne işe yarıyor" — Sol kenar çubuğundaki "KM Proje Çizimleri" başlığının sağındaki açılır menü (chevron) butonunun ne işe yaradığı soruldu.
  2. "birde hızlı aram kısmınıda çıkan tablo isimleri tüm programdaki aynı olsun" — Hızlı arama diyaloğundaki (Ctrl+K / Ctrl+T / QuickTableSwitcherDialog) tablo isimlerinin sol kenar çubuğu ve tüm programdaki yerelleştirilmiş standart isimlerle birebir aynı olması talep edildi.
- **Tasarım & Teknik Çözüm:**
  1. **İşaretli Buton (`btn_more`):**
     - Notion/Linear tasarım şablonundan gelen bu açılır buton, aktif çalışma alanı / proje menüsüne dönüştürüldü (`_show_workspace_menu`).
     - Tıklandığında "📁 KM Proje Çizimleri (Aktif)", "🔍 Tablo Ara... (Ctrl+K)" ve "ℹ️ Hakkında & Bilgi" seçeneklerini içeren modern koyu temalı bir popup menü açar. (İstenirse arayüzden tamamen de kaldırılabilir).
  2. **Merkezi Tablo Başlığı Fonksiyonu (`src/ui/i18n.py` & `src/ui_v2/sidebar.py`):**
     - `get_module_display_title(module_or_id)` merkezi fonksiyonu yazıldı: Aktif dil seçimine (TR/RU/EN) göre tablonun sistem başlığını döndürür (örn. "Eleman Listesi", "Ana Antet (Form 3)", "Referans ve Ek Dokümanlar Listesi" vb.).
     - `get_module_icon_name(module_or_id)` ile vektörel ikonlar modül kimliğine eşlendi.
  3. **Hızlı Arama Penceresi Yenilenmesi (`src/ui/quick_switcher.py`):**
     - Linear/Notion koyu temasında (`theme_linear`) yeniden düzenlendi.
     - Liste elemanlarının 1. satırına programdaki ile birebir aynı yerelleştirilmiş tablo başlığı, 2. satırına ise orijinal GOST Rusça teknik adı (`ГОСТ 21.502`, `ГОСТ Р 21.101 Form 2` vb.) eklendi.
     - Vektörel Font Awesome ikonları entegre edildi.
     - Arama filtresi hem yerelleştirilmiş Türkçe başlığı ("eleman", "antet", "doküman"), hem Rusça GOST adını, hem de modül kimliğini tanıyacak şekilde çok dilli akıllı aramaya kavuşturuldu.
  4. **Birim Testler (`tests/test_ui_v2_tasks_verification.py`):**
     - `test_task_41_quick_switcher_titles_and_workspace_menu` testi yazıldı: Başlıkların `get_module_display_title` ile eşleştiği, arama filtrelemesinin çalıştığı ve menü tetikleyicisinin aktif olduğu doğrulandı.
  5. Toplam 140 testin tamamı (%100) başarıyla yeşile ulaştırıldı.

##### 🔹 [TASK-42] Tablo Temizleme ve Satır Silmede 1'er Boş Satır Korunması — 🔍 Onay Bekliyor
- **İstek:** "temizle butonuna basınca komple tabloyu ce içerisindeki siliyoır. halbuki içeriği silmeli ve 1'er satır bıraklamı." — Kullanıcı, "Temizle" butonuna basıldığında tablonun sıfır satıra inip tamamen yok olması yerine, hücre içeriklerinin boşaltılmasını ve her tabloda 1 adet boş veri satırı bırakılmasını talep etti.
- **Tasarım & Teknik Çözüm:**
  1. **Eleman Listesi (`src/tables/elements_schedule/editor.py`):**
     - Araç çubuğuna `btn_clear` ("🧹 Temizle") butonu eklendi ve `i18n.t("clear_table")` ile bağlandı.
     - `_clear_table(prompt=True)` metodu eklendi: Onay sorusunun ardından tüm satırları sıfırlayıp 1 adet boş satır (`mark="Б1"`, boş kesit/kuvvet/çelik/not) bırakır ve 1. satırı seçer.
     - `_delete_selected_row()` metodunda tüm satırlar silindiğinde de tablonun boş kalmaması için otomatik olarak 1 adet temiz satır oluşturulması garanti altına alındı.
  2. **Temel Çalışma Çizimleri Takımları Listesi (`src/tables/main_drawings/editor.py`):**
     - `_clear_table(prompt=True)` metodu güncellendi: Tabloyu 0 satıra indirmek yerine tüm hücreleri temizleyip 1 adet boş `DrawingSetItem("", "", "")` satırı bırakır.
     - `_delete_selected_row()` içerisinde son satır silindiğinde de tablonun kaybolmasını önleyip 1 adet boş satır oluşturur.
  3. **Ana Takım Çalışma Çizimleri / Pafta Listesi (`src/tables/working_drawings/editor.py`):**
     - `_clear_table(prompt=True)` metodu onay diyaloğu ve 1 adet temiz pafta satırı (`sheet_number="", name="", note=""`) bırakacak şekilde yeniden düzenlendi.
     - `_delete_selected_row()` içerisinde tüm satırlar silindiğinde `_add_row()` ile 1 temiz satırın kalması sağlandı.
  4. **Referans ve Ek Dokümanlar Listesi (`src/tables/reference_documents/editor.py`):**
     - `_clear_table(prompt=True)` metodu 0 satıra indirmek yerine `_add_doc_row()` çağrısıyla 1 adet temiz doküman satırı bırakır.
     - `_delete_selected_row()` son satır silindiğinde en az 1 satırın korunmasını sağlar.
  5. **Ana Antet / Form 3 Sorumlular Tablosu (`src/tables/title_block/*`):**
     - `media_1791535271389_86ab0cab.png` referansı doğrultusunda, Form 3 "Temizle" butonuna basıldığında Sorumlular (Разработчики и подписи - Графы 10..13) tablosundaki standart unvanlar (`Разраб.`, `Проверил`, `Гл. констр.`, `Н. контр.`, `Нач. отд.`, `ГИП`) korunurken; kırmızı daire içine alınan **Soyadı (Фамилия), İmza (Подпись) ve Tarih (Дата)** alanları tamamen boşaltılır (`build_empty_signatories()`).
  6. **Çok Dilli Sözlük (`src/ui/i18n.py`):**
     - TR: `"clear_table": "Temizle"`
     - EN: `"clear_table": "Clear"`
     - RU: `"clear_table": "Очистить"`
  7. **Birim Testler (`tests/test_ui_v2_tasks_verification.py` & `tests/test_title_block.py`):**
     - `test_task_42_clear_table_leaves_one_empty_row` ve `test_title_block_editor_widget` testleri güncellendi: 4 tablonun tamamında temizleme ve silme durumlarında 1 adet boş satır kaldığı ve Form 3 antetinde sorumluların soyad/imza/tarih alanlarının sıfırlandığı doğrulandı.
  8. Toplam 141 testin tamamı (%100) başarıyla yeşile ulaştırıldı.

##### 🔹 [TASK-43] Örnek Şablon Verilerinin Jenerik/Kurgusal Hale Getirilmesi (Standartlar Tablosu Sabit) — 🔍 Onay Bekliyor
- **İstek:** "tüm örnekleri gerçek olmayan veriler ile dolduralım. salla birşeyler. standartların tablosunu değiştirme o zaten sabit" — Kullanıcı, açık kaynak / public paylaşıma hazırlık kapsamında, gerçek veya ticari projelere ait örnek verilerin (Moskova gökdelen şantiyesi, gerçek kişi soyadları vb.) jenerik, hayali ve temsili Rus endüstriyel yapı şablon verileriyle değiştirilmesini; resmi standartlar tablosuna (`reference_documents` / GOST/SP kütüphanesine) ise dokunulmamasını talep etti.
- **Tasarım & Teknik Çözüm:**
  1. **Dokunulmayan Sabit Standartlar Tablosu Kuralı:**
     - Kullanıcının kesin talimatı gereği `reference_documents` modülü ve `standards_library.json` (resmi GOST, SP, SNiP standartları ve TR/RU açıklamaları) kesinlikle korunmuş ve değiştirilmemiştir.
  2. **ГОСТ Р 21.101 Form 3 Ana Antet (`src/tables/title_block/*`):**
     - **Doküman Kodu:** `2026-001-КМ`
     - **Proje / Şantiye Adı:** Hayali endüstriyel park adresi: `"Производственно-складской комплекс в промышленном парке «Северный»,\nрасположенный по адресу: Московская область, г.о. Солнечногорск, тер. Промзона-1,\nземельный участок с кадастровым номером 50:09:0000000:12345"` (Hücre word-wrap ve font boyutlandırmasını test edecek zenginlikte).
     - **Yapı Adı:** `"Главный производственный корпус\nМеталлический каркас"`
     - **Pafta Başlığı:** `"Схема расположения колонн и балок на отм. +4.200"`
     - **Tasarım Firması:** `"ООО «ПРОЕКТ-СТРОЙ»"`, `company_logo=False`
     - **Sorumlu Mühendisler (Графы 10..13):** Temsili klasik mühendis soyadları:
       - `Разраб.`: Иванов (23.09.26)
       - `Проверил`: Петров (23.09.26)
       - `Гл. констр.`: Сидоров (23.09.26)
       - `Н. контр.`: Кузнецов (23.09.26)
       - `Нач. отд.`: Смирнов (23.09.26)
       - `ГИП`: Попов (23.09.26)
  3. **ГОСТ Р 21.101 Form 2 Temel Çizim Takımları (`src/tables/main_drawings/model.py`):**
     - 12 adet genel disiplin takımıyla dolduruldu:
       - `2026-001-ПЗ`: Пояснительная записка
       - `2026-001-АР`: Архитектурные решения
       - `2026-001-КЖ1`: Конструкции железобетонные. Фундаменты
       - `2026-001-КЖ2`: Конструкции железобетонные. Каркас
       - `2026-001-КМ1`: Конструкции металлические. Каркас главного корпуса
       - `2026-001-КМ2`: Конструкции металлические. Фахверк и связи
       - `2026-001-КМ3`: Конструкции металлические. Эстакада трубопроводов
       - `2026-001-КМД`: Конструкции металлические деталировочные
       - `2026-001-ОВ`: Отопление, вентиляция и кондиционирование
       - `2026-001-ВК`: Водоснабжение и канализация
       - `2026-001-ЭОМ`: Силовое электрооборудование и электроосвещение
       - `2026-001-АК`: Автоматизация комплексная
  4. **ГОСТ Р 21.101 Form 1 Ana Takım Pafta Listesi (`src/tables/working_drawings/model.py`):**
     - 10 adet standart KM çizim paftası:
       - Лист 1: Общие данные
       - Лист 2: Схема расположения колонн и связей на отм. 0.000
       - Лист 3: Схема расположения балок перекрытия на отм. +4.200
       - Лист 4: Схема расположения ферм и прогонов покрытия на отм. +8.400
       - Лист 5: Схема расположения связей по колоннам и покрытию
       - Лист 6: Разрезы 1-1, 2-2, 3-3
       - Лист 7: Узлы опирания и крепления балок перекрытия (узлы 1...8)
       - Лист 8: Узлы сопряжения ферм с колоннами и опирания прогонов (узлы 9...16)
       - Лист 9: Узлы вертикальных и горизонтальных связей (узлы 17...22)
       - Лист 10: Спецификация металлопроката и ведомость расхода стали
  5. **Birim Testler (`tests/test_main_drawings.py`, `tests/test_working_drawings.py`, `tests/test_title_block.py`, `tests/test_ui_v2_tasks_verification.py`):**
     - Tüm model, builder, editor ve DXF doğrulama testleri yeni jenerik verilerle senkronize edildi.
  6. Toplam 141 testin tamamı (%100) başarıyla yeşile ulaştırıldı.

##### 🔹 [TASK-44] Çok Dilli Başlık/Üst Bilgi Senkronizasyonu & GOST Form 2 Bölüm (Раздел) Mimarisi — 🔍 Onay Bekliyor
- **Yapılan İş:**
  1. **Kırmızı Alan Yerelleştirmesi:**
     - `TableEditorWrapper` başlık alanı (`lbl_title`, `lbl_subtitle`, `lbl_hint`) seçilen dile göre dinamik hale getirildi.
     - `src/ui/i18n.py` içerisine tüm modüller için `wrapper_title_*`, `wrapper_subtitle_*` ve `hint_excel_paste` anahtarları (TR/EN/RU) eklendi.
     - `LinearTopBar` aktif tablo breadcrumb etiketi ve Hakkında butonu dil değişimine bağlandı (`get_module_display_title`).
     - `reference_documents`, `main_drawings` ve `working_drawings` editör araç çubuğu butonları, bilgi kartları ve sütun başlıkları (`_apply_headers`) anlık dil değişimine bağlandı.
  2. **Bölüm (Раздел) ve Sarı Alan Mimarisi:**
     - ГОСТ Р 21.101-2020 Form 2 gereği tablonun *"Ссылочные документы"* (Referans Belgeler) ve *"Прилагаемые документы"* (İlişikteki Belgeler) bölümlerine ayrılma mantığı belgelendi.
     - `📑 [BÖLÜM]` ayraç etiketleri çok dilli hale getirildi (`[BÖLÜM]`, `[SECTION]`, `[РАЗДЕЛ]`), veri senkronizasyonu tüm dilleri tanıyacak şekilde güncellendi.
  3. **Testler:** 141 birim ve arayüz testinin tümü (%100) başarıyla doğrulandı.

##### 🔹 [TASK-45] Form 3 Antet ve Tüm Editör Başlıklarının Dinamik Çok Dilli Senkronizasyonu (TR/EN/RU) — 🔍 Onay Bekliyor
- **Yapılan İş:**
  1. **Form 3 Antet (Title Block) Çok Dilli Etiketleri:**
     - Kullanıcının ilettiği ekran görüntüsünde (`media_1791555349058_bdff0952.png`) İngilizce arayüz seçilmesine rağmen parantez içerisinde Türkçe kalan etiketler (`2 • НАИМЕНОВАНИЕ ОБЪЕКТА СТРОИТЕЛЬСТВА (TESİS / PROJE ADI & ADRESİ)`, `9 • ОРГАНИЗАЦИЯ (KURULUŞ / ŞİRKET)`) tespit edildi.
     - `src/ui/i18n.py` içerisine Form 3 için `tb_field_doc_code`, `tb_field_project_name`, `tb_field_building_name`, `tb_field_stage_sheet_total`, `tb_field_sheet_title`, `tb_field_company`, `tb_title_changes`, `tb_title_signatories`, `tb_col_*`, `tb_logo_*`, `tb_info_footer` çok dilli anahtarları eklendi.
     - TR: Rusça GOST + Türkçe Parantez, EN: Rusça GOST + İngilizce Parantez, RU: Sade tekil Rusça GOST terimleri uygulandı.
  2. **Anlık Dinamik Dil Geçişi:**
     - `TitleBlockEditorWidget`, `MainDrawingsEditorWidget`, `WorkingDrawingsEditorWidget`, `ElementsScheduleWidget` ve `CadViewportPanel` sınıfları `i18n.language_changed` sinyaline bağlandı. Dil değiştiği anda tek bir tıklama ile tüm etiketler, sütun başlıkları, butonlar ve rozetler yeniden oluşturulmadan dinamik olarak güncellenir.
  3. **CAD Tuvali ve HUD Rozetleri:**
     - `CadViewportPanel` ("📐 CANLI CAD TUVALİ" / "LIVE CAD VIEWPORT" / "ИНТЕРАКТИВНЫЙ CAD ВИД") ve `FloatingHudToolbar` butonları/ipuçları dile duyarlı hale getirildi; PySide6 nesne ömrü `try...except RuntimeError` ile güvene alındı.
  4. **Testler (`test_task_45_multilingual_sync`):**
     - TR, EN ve RU dillerinde Form 3 Antet etiketleri, revizyon ve imza tabloları, çalışma çizimleri butonları ve CAD rozetlerinin anlık değiştiği test edilerek 142 testin tamamı (%100) başarıyla doğrulandı.

##### 🔹 [TASK-46] Tablo İsimlerinin ГОСТ Standartlarına Tam Uyumlu Hale Getirilmesi (Madde 1) — 🔍 Onay Bekliyor
- **İstek:** "1-tablo isimleri gost'a tam uyumlu olacak."
- **Yapılan İş:**
  1. `src/ui/i18n.py` ve tablo modüllerindeki (`elements_schedule`, `title_block`, `reference_documents`, `main_drawings`, `working_drawings`) başlıklar resmi Rus standartlarındaki terminolojiye tam uyumlu hale getirildi.
  2. Kenar çubuğu (`LinearSidebar`), hızlı geçiş (`QuickTableSwitcherDialog`), üst bar breadcrumb ve editör başlıklarında ГОСТ adları ve iki satırlı iki dilli (Rusça standart + parantez içi Türkçe/İngilizce) isimler senkronize edildi.

##### 🔹 [TASK-47] Profil Listesinde (Ведомость элементов) Profil Kesit Şeklinin Profil İsminin Yanında Gösterilmesi (Madde 2) — 🔍 Onay Bekliyor
- **İstek:** "2- profil listesinde profil tipinin şekli tabloda profil isminin yanında görünecek."
- **Yapılan İş:**
  1. `src/tables/elements_schedule/sketch_renderer.py` modülü geliştirilerek `get_sketch_icon()` ile tüm kesit tipleri için (I-kiriş, Kutu, Boru, Şveller, Köşebent, Levha vb.) 24px yüksek çözünürlüklü vektörel CAD kesit ikonları üretildi.
  2. `src/tables/elements_schedule/editor.py` tablosunda "Сечение / Состав" hücresine profil tipine karşılık gelen kesit ikonu doğrudan entegre edildi.

##### 🔹 [TASK-48] Profil Listesi Hücre Temizleme Sonrası Kiril Kısayolu Ekleme Hatasının Düzeltilmesi (Madde 3) — 🔍 Onay Bekliyor
- **İstek:** "3-profil listesi tablosunda veri girişi olan kısımda profil isminde içerik silinip kiril alfabesinin kısayollarından eklenince silinmiş durumuna değilde önceki metnin sonunda ekliyor. düzeltilmeli."
- **Yapılan İş:**
  1. `src/tables/elements_schedule/editor.py` içerisindeki `_insert_char_to_active_cell` metodu güncellendi:
     - `QApplication.focusWidget()` ile aktif düzenleme yapılan `QLineEdit` tespit edilip karakter doğrudan odaklı editörün imleç konumuna eklendi.
     - Metin silinmişse silinmiş güncel boş metin üzerine ekleme yapılması sağlandı; eski metin dizgisine ekleme bug'ı tamamen giderildi.

##### 🔹 [TASK-49] Veri Giriş Alanı ile CAD Tuvali Arasında Boyutlandırma Esnekliği (QSplitter) (Madde 4) — 🔍 Onay Bekliyor
- **İstek:** "4- orta alan veri girişi yapılcan kısım sağ taraftan boyutu değiştirilemiyor. cad alanı sabit genişlikte kalıyor."
- **Yapılan İş:**
  1. `src/ui_v2/window.py` içerisindeki yatay `QSplitter` ayırıcısına minimum genişlik kısıtlamaları (`editor_wrapper` 320px, `cad_panel` 250px) ve `setHandleWidth(6)` atandı.
  2. `src/ui_v2/theme_linear.py` CSS temasında `QSplitter::handle:horizontal` modern 6px genişliğinde, yüksek kontrastlı hover efektli olarak stillendirildi; kullanıcının fareyle rahatça tutup boyutu değiştirebilmesi sağlandı.

##### 🔹 [TASK-50] DXF Export Sonrası Dosya Yolunu / Klasörü Açma Onay Diyaloğu (Madde 5) — 🔍 Onay Bekliyor
- **İstek:** "5-dxf export aldığında dosya yolunu açmak için kullanıcıya sorsun"
- **Yapılan İş:**
  1. `src/ui_v2/window.py` içerisindeki `_export_dxf` metodu güncellendi.
  2. Dışa aktarma tamamlandığında kullanıcıya `open_folder_prompt` onay kutusu gösterilir; kullanıcı "Klasörü Aç" butonuna tıkladığında Windows Explorer (`explorer /select, <path>`) açılarak üretilen DXF dosyası vurgulanır.
  3. `src/ui/i18n.py` sözlüğüne TR, EN ve RU dillerinde çeviri anahtarları eklendi.

##### 🔹 [TASK-51] Title Block Logo Alanında Şirket Yazısı Olmadığında Logonun Kutu İçinde Ortalanması (Madde 6) — 🔍 Onay Bekliyor
- **İstek:** "6-title blockta alogo kısmında eğer şiket yazısı eklenmeyecekse resim kutu içinde ortalanmalı"
- **Yapılan İş:**
  1. `src/tables/title_block/builder.py`, `src/ui/preview_canvas.py` ve `src/export/dxf_exporter.py` güncellendi.
  2. Şirket adı (`company_name`) boş olduğunda logo amblemi 50x15 mm kutunun tam ortasına ($X$ ve $Y$ merkezli) yerleştirildi; hem tuvalde hem DXF çıktısında WYSIWYG ortalama sağlandı.

##### 🔹 [TASK-52] Title Block Sorumlular Tablosunda Soyisim Sütunu Konumunun Standarttan Kontrolü (Madde 7) — 🔍 Onay Bekliyor
- **İstek:** "7-title blockta soyismin olduğu sutun bir soldan başlamalı. (standarttan kontrol edilerek)"
- **Yapılan İş:**
  1. ГОСТ Р 21.101-2020 Form 3 standardı (Çizim 1) incelendi:
     - Графа 10 (Görev / Должность): 20 mm (`colspan=2`, cols 0..1)
     - Графа 11 (Soyadı / Фамилия): 25 mm (`colspan=2`, cols 2..3 - bir soldan başlar!)
     - Графа 12 (İmza / Подпись): 10 mm (col 4)
     - Графа 13 (Tarih / Дата): 15 mm (col 5)
  2. `src/tables/title_block/builder.py` ve `src/tables/title_block/editor.py` güncellenerek soyisim sütunu standart gereği bir soldan başlatıldı.

##### 🔹 [TASK-53] Title Block Revizyon Sütunları Genişliğinin Standarttan Kontrol Edilip Ayarlanması (Madde 8) — 🔍 Onay Bekliyor
- **İstek:** "8-titleblockta revision sutunları genişliği kontrol edilmeli (standarttan kontrol edilerek)"
- **Yapılan İş:**
  1. ГОСТ Р 21.101-2020 Form 3 standardı revizyon tablosu kontrol edildi:
     - `Изм.` (10 mm), `Кол.уч.` (10 mm), `Лист` (10 mm), `№док.` (15 mm), `Подпись` (10 mm), `Дата` (15 mm). Toplam 70 mm.
  2. `TitleBlockTableBuilder` COL_WIDTHS ve `TitleBlockEditorWidget` revizyon tablosu sütun genişlikleri resmi GOST milimetrik değerlerine tam hizalandı.

##### 🔹 [TASK-54] Güncelleme Kontrol Ayarlarının ve Tercihlerinin Yapılandırılması (Madde 9) — 🔍 Onay Bekliyor
- **İstek:** "9-güncelleme kontrol ayarları yaplacak."
- **Yapılan İş:**
  1. `src/services/settings.py` içinde `UpdaterSetting` modeli kuruldu (başlangıçta kontrol etme, kontrol URL'si `https://zadax.net/...`).
  2. `src/ui_v2/settings_dialog.py` Ayarlar penceresine canlı test butonu ("Bağlantıyı Sına") ve otomatik kontrol tercihleri eklendi.
  3. `src/services/updater.py` modülüne HTML fallback regex ayrıştırıcısı eklenerek Zadax.net ürün sayfası HTML içeriğinden sürüm ve indirme linki yakalama yeteneği kazandırıldı.

##### 🔹 [TASK-55] Hakkında (About) Butonlarının Hover Olmadığında da Farklı Renklerle Görünmesi (Madde 10) — 🔍 Onay Bekliyor
- **İstek:** "10-about kısmında butonlar mause olmayınca da renklenecek. farklı renkler ile."
- **Yapılan İş:**
  1. `src/ui_v2/about_dialog.py` içindeki tüm aksiyon butonları varsayılan durumlarında da farklı ve yüksek kontrastlı renklere kavuşturuldu:
     - `btn_web_link`: Deep Sky (`#0369a1` zemin, `#38bdf8` kenarlık)
     - `btn_check_update`: Indigo (`#4338ca` zemin, `#6366f1` kenarlık)
     - `btn_open_product_page`: Emerald Green (`#047857` zemin, `#10b981` kenarlık)
     - `btn_close`: Slate Steel (`#334155` zemin, kırmızı hover)

##### 🔹 [TASK-56] Tüm Tabloları Paftalara Otomatik Yerleştiren Dinamik Sistem & Ortak Antet (Madde 11) — 🔍 Onay Bekliyor
- **İstek:** "11-tüm tabloları paftalara otomatik yerleştiren sistem yapılacak. tablo eklenmesine uyumlu şekilde. seçilen sayfa boyuyu yeterli değilse başka bir pafta daha açacak. titleblock tüm paftalarda ortak kullanılacak."
- **Yapılan İş:**
  1. `src/models/multi_sheet.py` altında `MultiSheetLayoutManager` motoru geliştirildi:
     - Tabloların toplam yüksekliklerini hesaplayarak seçilen paftaya (A4, A3, A2, A1) sığmadığında otomatik olarak yeni paftalar (Pafta 1, Pafta 2...) açar.
     - Form 3 ana anteti (185x55 mm) her paftanın sağ alt köşesinde ortak proje bilgileriyle oluşturur; pafta numarasını (`Лист 1`, `Лист 2`...) ve toplam pafta sayısını (`Листов N`) otomatik dinamik üretir.
  2. `src/export/dxf_exporter.py` sınıfına `export_multi_sheet()` metodu eklendi; tüm paftalar AutoCAD Modelspace'te 50 mm aralıkla yan yana 1:1 ölçekli dışa aktarılır.
  3. `src/ui/preview_canvas.py` ve `src/ui_v2/cad_panel.py` üzerine `render_multi_sheet()` ve HUD çoklu pafta butonu entegre edildi.

##### 🔹 [TASK-57] AutoCAD DXF Katman (Layer) İsimleri, Renkleri ve Ayarlar Paneli — 🔍 Onay Bekliyor
- **İstek:** "1- ayarlar alanı eklenmeli. burada aucad layer isimleri ve renkleri falan tutulsun. kullanıcı isterse değiştirsin."
- **Yapılan İş:**
  1. `src/services/settings.py` altında `SettingsManager` geliştirildi; `~/.km_tables_studio/settings.json` dosyasında katman adları, ACI renkleri (1..255), çizgi kalınlıkları ve tipleri kalıcı olarak saklanır.
  2. `src/ui_v2/settings_dialog.py` (`LinearSettingsDialog`) modern ayarlar penceresi oluşturuldu; ACI renk paleti, çizgi kalınlıkları seçimi ve "Varsayılanlara Sıfırla" desteği sunuldu.
  3. `LinearTopBar` üzerine "⚙️ Ayarlar" butonu eklendi.
  4. `DxfExporter` motoru katman adlarını doğrudan `SettingsManager` üzerinden dinamik çözecek şekilde entegre edildi.

##### 🔹 [TASK-58] Tablo Şablon / Önayar (Preset) Yönetim Sistemi (Bağımsız Kaydetme & Yükleme) — 🔍 Onay Bekliyor
- **İstek:** "2-tablolar için kullanıcı yaptığı tabloları ayrı ayrı preset olarak kaydetsin. her tabloyu baştan yapmasına gerek kalmaz. aynı projede çalışıyorsa önceki yaptığı tabloyu çağırıp üzerinde oynama yapabilir."
- **Yapılan İş:**
  1. `src/services/preset_manager.py` altında `PresetManager` geliştirildi; her tablo modülü için `~/.km_tables_studio/presets/<module_id>/` altında JSON şablonları saklanır, listelenir, yüklenir ve silinir.
  2. `src/ui_v2/preset_dialog.py` (`SavePresetDialog`, `LoadPresetDialog`) önayar pencereleri kodlandı.
  3. `src/ui_v2/editor_wrapper.py` başlık satırına "💾 Şablon Kaydet" ve "📂 Şablon Yükle" butonları yerleştirildi; yüklenen şablonun aktif editöre ve canlı CAD tuvaline anında yansıtılması sağlandı.

##### 🔹 [TASK-59] Title Block "Logo Göster" Checkbox Görünürlüğü (Madde 1) — 🔍 Onay Bekliyor
- **İstek:** "1-titleblockta logo göster seçneği tıklayınca görünmez oluyor."
- **Yapılan İş:**
  1. `src/ui_v2/assets/checkmark.svg` temiz beyaz vektörel onay simgesi oluşturuldu.
  2. `src/ui_v2/theme_linear.py` içerisinde `QCheckBox`, `QCheckBox::indicator`, `QCheckBox::indicator:checked` QSS stilleri tanımlandı; tıklandığında arka plan mor/vurgulu renge dönüp beyaz onay işareti görünür kılındı.

##### 🔹 [TASK-60] Tablo İsimlerinin Standart Üçlü Formata Getirilmesi (GOST / Tablo No / İsim) (Madde 2) — 🔍 Onay Bekliyor
- **İstek:** "2- tablo isimleri GOST no/ tablo no (yoksa appendix no) / isim olsun. çevirileride buna göre olsun."
- **Yapılan İş:**
  1. `src/ui/i18n.py` içerisindeki tüm modül başlıkları TR, RU ve EN için standart formata dönüştürüldü:
     - TR: `ГОСТ 21.502 / Tablo 1 / Eleman Listesi`, `ГОСТ Р 21.101 / Form 3 / Başlık Bloğu (Antet)`, `ГОСТ Р 21.101 / Form 2 / Referans ve Ek Dokümanlar`, `ГОСТ Р 21.101 / Form 2 / Ana Çizim Takımları`, `ГОСТ Р 21.101 / Form 1 / Çalışma Çizimleri Listesi`.
     - RU: `ГОСТ 21.502 / Таблица 1 / Ведомость элементов`, `ГОСТ Р 21.101 / Форма 3 / Основная надпись`, `ГОСТ Р 21.101 / Форма 2 / Ведомость ссылочных и прилагаемых документов` vb.
     - EN: `GOST 21.502 / Table 1 / Elements Schedule`, `GOST R 21.101 / Form 3 / Title Block` vb.

##### 🔹 [TASK-61] Ayarlar Menüsü "Uygulama Açıldığında Güncelle" Checkbox Görünürlüğü (Madde 3) — 🔍 Onay Bekliyor
- **İstek:** "3- uygulama her açıldığında güncelleme chek listi seçilince görünmez oluyor."
- **Yapılan İş:**
  1. `src/ui_v2/theme_linear.py` QCheckBox kuralı ile onaylandığında kutucuğun kaybolma problemi çözüldü.
  2. `src/ui_v2/settings_dialog.py` içindeki `chk_startup_update` bileşeni tam görünür ve stabil hale getirildi.

##### 🔹 [TASK-62] Güncelleme URL Alanının Sabitlenmesi & Resmi Sunucu Kartı (Madde 4) — 🔍 Onay Bekliyor
- **İstek:** "4-güncelleme adresini kullanıcıya bırakma"
- **Yapılan İş:**
  1. `src/ui_v2/settings_dialog.py` içerisindeki kullanıcı tarafından düzenlenebilen `QLineEdit` giriş kutusu kaldırıldı.
  2. Resmi doğrulanmış adres (`DEFAULT_UPDATE_CHECK_URL`) sabit, kopyalanabilir bilgi kartı olarak gösterildi.
  3. Bağlantı testi ve ayar kaydetme daima resmi adrese bağlandı.

##### 🔹 [TASK-63] AutoCAD Katman Adı Alanı İmleç ve Satır Yüksekliği İyileştirmesi (Madde 5) — 🔍 Onay Bekliyor
- **İstek:** "5-autocad katman ayarları katman adı alanı imleçten küçük."
- **Yapılan İş:**
  1. `src/ui_v2/settings_dialog.py` katman tablosu satır yüksekliği `36px`'e çıkartıldı.
  2. Katman adı `QLineEdit` yüksekliği `28px`, font boyutu `12px` ve iç boşluğu `padding: 4px 8px` olarak güncellendi. İmleç artık basık kalmıyor ve rahat hareket ediyor.

##### 🔹 [TASK-64] AutoCAD Renk Ayarlarında Renk Kutuları (Swatch) ve 255 ACI Renk Paleti (Madde 6) — 🔍 Onay Bekliyor
- **İstek:** "6-autocad renk ayarlarında renkleri de göstersin ayrıca autocaddeki kadar renk paleti olsun"
- **Yapılan İş:**
  1. `make_color_icon` fonksiyonu ile renk açılır kutusundaki her rengin yanına gerçek renk önizleme kutusu (swatch) eklendi.
  2. `AciColorPickerDialog` iletişim kutusu geliştirildi; AutoCAD'deki gibi 1-9 Standart renkler, 10-249 renk matrisi (24 sütun x 10 satır) ve 250-255 gri tonları içeren tam 255'lik AutoCAD Color Index paleti entegre edildi.

##### 🔹 [TASK-65] AutoCAD Çizgi Kalınlıkları İçin Özel Kalınlık (Custom mm) Desteği (Madde 7) — 🔍 Onay Bekliyor
- **İstek:** "7-autocad ayarları kalınlık için custon da olsun. kullanıcı isterse kalınlık girsin"
- **Yapılan İş:**
  1. Çizgi kalınlığı açılır menüsüne `📐 Özel Kalınlık...` seçeneği eklendi.
  2. Kullanıcı bu seçeneği seçtiğinde açılan sayısal girdi kutusuyla dilediği milimetrik kalınlığı (örn: 0.40 mm) girebilmesi ve menüye dinamik eklenmesi sağlandı.

##### 🔹 [TASK-66] Kenar Çubuğu Alt Callout Kartının ve Üst Bar GOST Rozetinin Kaldırılması (Madde 8) — 🔍 Onay Bekliyor
- **İstek:** "8-resimde verdiğim şeyleri kaldır." (Resim 1: Sol kenar çubuğu altındaki yeşil ГОСТ kartı, Resim 2: Üst bardaki yeşil GOST uyum rozeti).
- **Yapılan İş:**
  1. `src/ui_v2/sidebar.py` içerisinden `status_callout` yeşil kartı arayüzden kaldırıldı.
  2. `src/ui_v2/top_bar.py` içerisinden `badge_gost` yeşil rozeti arayüzden kaldırıldı.

##### 🔹 [TASK-67] Dil Seçeneklerinin Yanına Ülke Bayrak Simgelerinin Eklenmesi (🇹🇷, 🇬🇧, 🇷🇺) (Madde 9) — 🔍 Onay Bekliyor
- **İstek:** "9-dil seçeneklerin yanına bayrak ekle."
- **Yapılan İş:**
  1. `src/ui_v2/top_bar.py` dil seçici butonları `🇹🇷 TR`, `🇬🇧 EN`, `🇷🇺 RU` olarak güncellendi.
  2. Buton boyutları (48x24px) ve stilleri bayrakların net görünmesi için optimize edildi.

##### 🔹 [TASK-68] Eleman Listesi "Eleman Ekle" Butonundaki Mükerrer '+' İşaretinin Temizlenmesi (Madde 10) — 🔍 Onay Bekliyor
- **İstek:** "10-eleman listesinde eleman ekle butonunda 2 tane + var."
- **Yapılan İş:**
  1. `src/ui/i18n.py` dosyasındaki `add_element` çevirilerindeki metin içi '+' işaretleri kaldırıldı (`Eleman Ekle`, `Add Element`, `Добавить элемент`).
  2. Buton ikonu olan `+` simgesi ile metin temiz biçimde hizalandı.

##### 🔹 [TASK-69] Editör Başlık Metni ile Şablon Butonlarının Ayrılması (Çakışma Önleme) (Madde 11) — 🔍 Onay Bekliyor
- **İstek:** "11-3. resimde metin ile buton çakışması var. bu alanı tüm tablolarda kontrol et. butonlar için uygun bir yer bul."
- **Yapılan İş:**
  1. `src/ui_v2/editor_wrapper.py` başlık alanı iki ayrı satıra bölündü:
     - 1. Satır: Yalnızca tablo ikonu ve tam sayfa genişliğindeki tablo başlığı (metin asla kırpılmaz veya butonlarla çakışmaz).
     - 2. Satır: Alt başlık, Excel yapıştırma ipucu ve sağ tarafta "💾 Şablon Kaydet" / "📂 Şablon Yükle" butonları.

##### 🔹 [TASK-70] Üst Barda Yalnızca Logo ve "KM Studio" İsim Alanının Bırakılması (Madde 12) — 🔍 Onay Bekliyor
- **İstek:** "12-en üst barda sadece logo ve KM Studio yazsa yeterli. yanındaki gost adını ve tablo adını sil."
- **Yapılan İş:**
  1. `src/ui_v2/top_bar.py` sol gezinme bölümündeki ayrıştırıcılar, standart adı (`ГОСТ 21.502`) ve aktif tablo adı etiketleri üst bardan kaldırıldı.
  2. Yalnızca menü butonu ve `📐 KM Studio` logosu bırakıldı.

##### 🔹 [TASK-71] Eleman Listesinde Profil İsmi Değişince Anında Algılama & Gecikmesiz Senkronizasyon (Madde 13) — 🔍 Onay Bekliyor
- **İstek:** "13-eleman listesinde veri girişi kısmında profil ismi değişince hemen değiştirmiyor. biraz bekleme yapıyor."
- **Yapılan İş:**
  1. `src/tables/elements_schedule/editor.py` içerisine `ProfileCellDelegate` eklendi; kullanıcı hücrede profil ismini yazarken `textChanged` sinyaliyle kesit türü anında algılanır.
  2. `_detect_sketch_type` fonksiyonu ile Rusça standart haddelenmiş profiller (`20К1`, `25Ш1`, `30Б2`, `16П`, `100х100х4`, `L 75х6` vb.) anında tanınarak eskiz türü ve ikonu eşzamanlı güncellenir.
##### 🔹 [TASK-72] Çoklu Çıktıda Paftalarda Tablo Çakışmasının Kesin Önlenmesi & Dinamik Sütun Paketleme — 🔍 Onay Bekliyor
- **İstek:** "çoklu çıktıda paftalarda böyle çakışma olmasın" (Ekran görüntüsü: `media_1791809000094_f549e299.png`)
- **Kök Neden:**
  - `MultiSheetLayoutManager` içerisinde sol sütun (2. sütun) yerleşimi hesaplanırken sağdaki 1. sütun tablosunun genişliği Form 3 antet genişliği olan `tb_w = 185.0 mm` varsayılıyordu (`tbl_cad_x = inner_w - tb_w - TABLE_GAP - t_w`).
  - Ancak GOST 21.502 uyumlu "Ведомость элементов" tablosunun genişliği **197.0 mm**'dir.
  - Bu nedenle 1. sütun sola doğru $X = inner\_w - 197.0$ noktasına kadar uzanırken, 2. sütunun sağ kenarı $X = inner\_w - 193.0$ noktasına yerleştiriliyor ve aralarında tam **4.0 mm fiziksel çakışma** (overlap) meydana geliyordu.
- **Yapılan İş:**
  1. `src/models/multi_sheet.py` dosyasındaki `MultiSheetLayoutManager.calculate_layout` algoritması dinamik sağdan-sola sütun paketleme (`PageState`, `open_new_column`) mimarisine geçirildi:
     - 1. Sütun (Sağ kenar, Antet üstü): `x_right = inner_w`, alt sınır antetin üstü (`min_y = tb_h + TABLE_GAP`), taban genişliği `max(tb_w, max_width_tables)`.
     - 2. ve Sonraki Sütunlar (Sola doğru): Sağ kenarı önceki sütunun gerçek maksimum genişliğine göre belirlenir (`x_right = prev_col.x_right - prev_col.max_width - TABLE_GAP`). Böylece tablolar kaç mm olursa olsun sütunlar arası mesafe daima en az `TABLE_GAP` (8.0 mm) kalır.
     - Antetin solunda kalan sütunlar tüm dikey yüksekliği (`min_y = TABLE_GAP`) kullanır.
     - Bir sütuna veya paftaya sığmayan tablolar için yatayda iç çerçeve payı kontrol edilir (`tbl_cad_x >= 0.0`); yatayda sığmayan tablolar için otomatik olarak yeni pafta (Pafta 2, 3...) açılır.
  2. `src/ui_v2/cad_panel.py` içindeki Floating HUD Araç Çubuğu modernize edildi; çift kutu QFrame çizgileri düzeltildi, 1px dikey ayırıcılar eklendi ve koordinat genişliği dinamik kılındı.
  3. `src/ui_v2/window.py` içerisinde çoklu paftaya dahil edilecek tablolar filtrelendi (pasif çelik sarfiyat ve antet hariç tutuldu).
  4. `tests/test_tasks_46_to_58.py` altına `test_task_56_no_table_overlaps_multi_sheet` geometrik sınırlayıcı kutu (Bounding Box) ayrıklık testi eklendi; tüm paftalarda sıfır çakışma doğrulandı.

##### 🔹 [TASK-73] Güncelleme Ayarının Kullanıcıdan Gizlenmesi & Resmi Zadax Ürün Sayfası Entegrasyonu — 🔍 Onay Bekliyor
- **İstek:** "güncelleme ayarını kullanıcıdan gizle. KOntrol edilecek link ise şu: https://zadax.net/tr/products/km-tables-studio-celik-yap-tablolar-ve-dxf-uretici/"
- **Yapılan İş:**
  1. `src/version.py` dosyasındaki `DEFAULT_UPDATE_CHECK_URL` resmi Zadax ürün sayfası adresine güncellendi (`https://zadax.net/tr/products/km-tables-studio-celik-yap-tablolar-ve-dxf-uretici/`).
  2. `src/ui_v2/settings_dialog.py` içerisindeki resmi sunucu kartı (`self.card_server`), test butonu (`self.btn_test_url`), sonuç etiketi (`self.lbl_test_result`) ve geriye dönük uyumluluk metin kutusu (`self.txt_update_url`) kullanıcı arayüzünden tamamen gizlendi (`.hide()`).
  3. `src/services/updater.py` içerisinde `_parse_html_page` fonksiyonu Zadax ürün sayfası JSON-LD `softwareVersion` ("v1.3.0") şemasını ve sayfa içi versiyon etiketlerini ayrıştıracak şekilde optimize edildi; ürün sayfası yönlendirme linki olarak doğrudan bu adres bağlandı.
  4. `src/services/settings.py` ayar yükleme ve kaydetme mimarisi güncellendi; kullanıcı girdisinden bağımsız olarak kontrol adresi daima resmi ürün sayfasına bağlandı.
  5. `tests/test_revisions_batch_13.py` ve `tests/test_updater_and_about.py` testleri güncellendi; tüm 169 test %100 başarıyla geçti.

##### 🔹 [TASK-74] AutoCAD Katman Tablosu Sütun Sıkışmasının Giderilmesi & Dinamik Genişlik — 🔍 Onay Bekliyor
- **İstek:** "bu alanda sığmamış" ve "hücreye sığmamış" (Ekran görüntüleri: `media_1791983906448_29d3c32a.png`, `media_1791988568294_696a3eca.png`)
- **Kök Neden:**
  - Sütun 2 (`Renk (ACI)`) içerisindeki `cb_color` ("7 - Beyaz / Siyah (White)") ve palet butonu `btn_palette` 240px genişliğe sıkıştığında, ComboBox sağ parantezi `)` kesiliyor; buton içindeki "🎨" emojisi ise Windows DirectWrite metin motorunda tek piksellik dikey çizgi (`|`) şeklinde bozuk kırpılıyordu.
  - Sütun 0'daki uzun açıklamalarda `...` (üç nokta) oluşuyor; Sütun 3'teki "0.70 mm (Ana dış çerçeve - GOST 2.303)" metni ise açılır oka temas ediyordu.
- **Yapılan İş:**
  1. `src/ui_v2/settings_dialog.py` pencere boyutları ferah `setMinimumSize(960, 520)` ve `resize(1020, 570)` değerlerine optimize edildi.
  2. Tablo sütun yerleşimi ve genişlikleri tam metin sığacak şekilde yeniden kalibre edildi:
     - Sütun 0 (`İşlev (Açıklama)`): `Interactive` (265px — hiçbir açıklamada üç nokta kalmaz).
     - Sütun 1 (`Katman Adı (AutoCAD)`): `Interactive` (155px — katman isimleri tam sığar).
     - Sütun 2 (`Renk (ACI)`): `Interactive` (260px — `cb_color` metni ve parantezleri tam görünür).
     - Sütun 3 (`Kalınlık`): `Stretch` (250px+ — kalan tüm alanı doldurur).
  3. Palet butonundaki bozuk emoji `"🎨"` yerine QtAwesome vektörel SVG ikonu (`fa5s.palette`) entegre edildi; buton 28x28 pikselde net ve profesyonel bir görünüme kavuşturuldu.
  4. Çizgi kalınlığı 0.70 mm metni gereksiz uzantıdan arındırılarak `"0.70 mm (Ana dış çerçeve)"` formatına getirildi.
  5. `tests/test_revisions_batch_13.py` ve tüm test süiti (184 test) %100 başarıyla doğrulandı.

##### 🔹 [TASK-75] GOST Rus Çelik Sortament / Profil Seçici Kütüphanesi (Item 2.1) — 🔍 Onay Bekliyor
- **İstek:** "2.1'i yapmak istiyorum. kütüphane için veriye ihtiyacın olacak mı?"
- **Yapılan İş:**
  1. Kullanıcıdan ek veri ihtiyacı olmadan, Rus GOST standartlarına uygun kapsamlı yerleşik profil kütüphanesi oluşturuldu (`src/config/gost_profiles.json`):
     - Двутавры (I-Kirişler): GOST R 57837-2017 / GOST 26020-83 (Б, Ш, К serileri: 20Б1, 30Б1, 40Б1, 20Ш1, 30К1 vb.)
     - Швеллеры (U-Kanallar): GOST 8240-97 (У ve П serileri: 10П, 16П, 20П, 14У, 20У vb.)
     - Трубы профильные (Kare & Dikdörtgen Kutu Profiller): GOST 30245-2003 / GOST 8639 (80x80x4, 100x100x5, 120x80x4, 140x140x6 vb.)
     - Трубы круглые (Yuvarlak Çelik Borular): GOST 10704-91 / GOST 8732 (89x4, 108x4, 159x5, 219x6 vb.)
     - Уголки (Eşkenar ve Çeşitkenar Köşebentler): GOST 8509-93 (50x5, 75x6, 100x8, 125x8 vb.)
  2. `src/services/profile_database.py` servisi geliştirildi: kategoriye göre filtreleme, anlık metin arama ve seçilen profilden eskiz tipini (`sketch_type`) otomatik çıkarma mimarisi kuruldu.
  3. `src/ui_v2/profile_picker_dialog.py` Linear Dark modal diyaloğu kodlandı: anlık arama kutusu, kategori hapları (Pills), profil tablosu (profil adı, standart, h/b/s/t boyutları, birim ağırlık kg/m) ve çift tıklama/seçme ile doğrudan tabloya ekleme desteği sağlandı.
  4. `src/tables/elements_schedule/editor.py` içerisine "📚 GOST Profil..." butonu ve çift tıklama ile profil seçici diyaloğu entegre edildi.
  5. `tests/test_profile_picker.py` ile veritabanı, filtreleme ve GUI diyaloğu test edildi.

##### 🔹 [TASK-76] 1:1 Vektörel PDF Dışa Aktarma Motoru (Tekli ve Çoklu Paftalar) (Item 2.3) — 🔍 Onay Bekliyor
- **İstek:** "2.3'ü de ekleyelim. hem tüm tablolar için hemde çoklu tablolar için"
- **Yapılan İş:**
  1. `src/ui/preview_canvas.py` üzerine `print_mode` (monokrom GOST teknik çizim modu: beyaz zemin, siyah net çizgiler, siyah metinler, koordinat eksensiz) ve tekil paftayı sayfaya çizen `render_single_sheet_page(page)` fonksiyonları eklendi.
  2. `src/export/pdf_exporter.py` bağımsız 1:1 vektörel PDF dışa aktarıcısı kodlandı:
     - `QPdfWriter` ve `QPainter` donanım vektör motoru kullanıldı.
     - 1 CAD birimi = 1.0 mm kesin metrik ölçek sağlandı (A0, A1, A2, A3, A4 paftalarında yatay ve dikey yönde tam milimetrik GOST çerçeve ve Form 3 antet).
     - UTF-8 Kiril metinleri ve font boyutlandırmaları kayıpsız vektörel olarak basıldı.
     - Tekli tablolar için `export_sheet` ve çok sayfalı çizim setleri için çok sayfalı (`newPage()`) `export_multi_sheet` metotları uygulandı.
  3. `src/ui_v2/top_bar.py` üzerine "📄 PDF Aktar" butonu ve `Ctrl+P` kısayolu entegre edildi.
  4. `src/ui_v2/window.py` içerisinde aktif tablo veya çoklu pafta moduna göre dinamik PDF export akışı ve dışa aktarım sonrası klasörü açma diyaloğu bağlandı.
  5. `tests/test_pdf_exporter.py` ile tekli ve çoklu pafta PDF üretimi doğrulandı.

##### 🔹 [TASK-77] Ortak Antet (Title Block) Verilerinin Tüm Tablolar ve Paftalarla Eşzamanlanması (Item 3.2) — 🔍 Onay Bekliyor
- **İstek:** "3.2 zaten titleblock ta veri varsa oradan çekecek diye anlaşmıştık."
- **Yapılan İş:**
  1. Title block (Form 3 ana antet) modülünde yapılan tüm veri değişikliklerinin (`doc_code`, `project_name`, `building_name`, `company_name`, mühendis imzaları vb.) anında tüm modüllerin `module_layout_configs` yapılandırmalarına ve ana `self.layout_config.title_block_doc` nesnesine aktarılması sağlandı (`src/ui_v2/window.py`).
  2. Eleman Listesi veya diğer tablolara geçildiğinde antetin güncel şirket, proje ve imza verileriyle çizilmeye devam ettiği doğrulandı.
  3. Çoklu pafta hesaplamasında (`MultiSheetLayoutManager`) ortak antet (`shared_title_block`) kullanıcının en son girdiği gerçek antet belgesinden beslendi.
  4. `tests/test_ui_v2_new_features.py` altında `test_title_block_synchronization` testi ile tam entegrasyon kanıtlandı.

##### 🔹 [TASK-78] Yerel Proje Formatı (.kmproj) Kaydetme, Yükleme ve Proje Yönetimi (Item 4.1) — 🔍 Onay Bekliyor
- **İstek:** "4.1'i yapalım"
- **Yapılan İş:**
  1. `src/services/project_manager.py` servisi geliştirildi (`.kmproj` JSON tabanlı yerel proje dosya formatı):
     - Tüm modüllerin dokümanları (`module_documents`), her tabloya özel bağımsız pafta konfigürasyonları (`module_layout_configs`), ortak antet ve katman ayarları eksiksiz serileştirildi ve geri yüklendi.
  2. `src/ui_v2/top_bar.py` sol üst alanına modern açılır "📁 Proje ▾" menüsü eklendi:
     - 📄 Yeni Proje (`Ctrl+N`)
     - 📂 Proje Aç... (`Ctrl+O`)
     - 💾 Projeyi Kaydet (`Ctrl+S`)
     - 💾 Farklı Kaydet... (`Ctrl+Shift+S`)
  3. `src/ui_v2/window.py` içerisinde proje açma/kaydetme/yeni proje döngüsü, pencere başlığı senkronizasyonu (`ProjeAdı.kmproj — KM Studio`), durum çubuğu bildirimleri kuruldu.
  4. `tests/test_project_manager.py` ve `tests/test_ui_v2_new_features.py` testleriyle kaydetme/yükleme roundtrip döngüsü doğrulandı.

##### 🔹 [TASK-79] Geri Al / İleri Al (Undo / Redo) Geri Alma Altyapısı (Item 4.2) — 🔍 Onay Bekliyor
- **İstek:** "4.2'yi ekleyelm"
- **Yapılan İş:**
  1. `src/services/undo_manager.py` servisi `QUndoStack` tabanlı anlık durum (snapshot) komut yapısıyla kodlandı (`UndoManager`, `SnapshotUndoCommand`).
  2. Python/Qt nesne ömrü (C++ deleted object) koruması ve derin kopya (`copy.deepcopy`) koruması eklenerek referans mutasyonu engellendi.
  3. `src/ui_v2/editor_wrapper.py` editör araç çubuğuna "↩ Geri Al" ve "↪ İleri Al" butonları yerleştirildi; durumlarına göre dinamik olarak enable/disable edilmeleri sağlandı.
  4. Global klavye kısayolları bağlandı: `Ctrl+Z` (Geri Al), `Ctrl+Y` ve `Ctrl+Shift+Z` (İleri Al).
  5. `tests/test_undo_manager.py` ve `tests/test_ui_v2_new_features.py` testleriyle tam işlevsellik doğrulandı.

---

## 🧪 BÖLÜM 2: Test ve Kalite Güvencesi (QA)
- **Toplam Test Sayısı:** 184 adet test (`python -m pytest` ile %100 başarılı).
- **Yeni Doğrulama Testleri:**
  - `tests/test_profile_picker.py`: GOST Profil veritabanı, filtreleme ve seçim modalı testleri.
  - `tests/test_pdf_exporter.py`: 1:1 vektörel PDF tekli ve çok sayfalı dışa aktarma testleri.
  - `tests/test_project_manager.py`: Yerel `.kmproj` projesi serileştirme ve yükleme testleri.
  - `tests/test_undo_manager.py`: QUndoStack snapshot komutları, undo/redo geçmişi ve temizleme testleri.
  - `tests/test_ui_v2_new_features.py`: Window entegrasyonu, başlık bloğu senkronizasyonu, undo/redo ve proje kaydetme yaşam döngüsü testleri.
- DXF ve PDF çıktılarının **1:1 ölçekli** (`$INSUNITS = 4`) ve Form 3 antetinin **sağ altta sabit** olduğu doğrulandı.
- Git commit işlemi kullanıcı talimatına istinaden **yapılmamış**, tüm değişiklikler test edilmek üzere çalışma dizininde temiz bırakılmıştır.

---

## ✅ BÖLÜM 3: Tamamlanan İşler (8 Adet Onaylı)

| ID | Modül / Görev | Durum | Nasıl Yapıldı? (Teknik Özet) |
| :--- | :--- | :---: | :--- |
| **COMP-01** | **Parametrik Çekirdek & Tablo Modeli** | Tamamlandı | `Point2D`, `Rect2D`, `TableCell`, `TableRow`, `Table` sınıfları sıfırdan yazıldı. Hücre birleştirme (`rowspan`, `colspan`) ve milimetrik koordinat hesaplayıcı mantığı kuruldu. |
| **COMP-02** | **1:1 Ölçekli Bağımsız DXF Motoru** | Tamamlandı | `ezdxf` motoruyla AutoCAD gerektirmeyen DXF R2010 dışa aktarıcısı kodlandı. Çizim kesinlikle 1:1 ölçekli (`1 CAD birimi = 1 mm`, `$INSUNITS = 4`) üretildi. Form 3 antet (185x55 mm) daima sağ alt köşeye kilitlendi. Katmanlar (`KM_TABLO_CERCEVE`, `KM_TABLO_IZGARA`, `KM_TABLO_METIN`, `KM_TABLO_ESKIZ`) ve UTF-8 Kiril desteği sağlandı. |
| **COMP-03** | **Canlı 2D Vektörel CAD Tuvali** | Tamamlandı | Donanım hızlandırmalı PySide6 `QGraphicsView` ve `QGraphicsScene` üzerine canlı çizim tuvali geliştirildi. Akıcı Pan (fare orta tuş/sürükle), Zoom (tekerlek) ve sağ üstte yüzen şeffaf cam HUD hapı (`FloatingHudToolbar`: Sığdır, 100%, +/-, koordinat takibi) entegre edildi. |
| **COMP-04** | **Modüler Tablo Sözleşmesi (`TableRegistry`)** | Tamamlandı | Birden fazla tablonun sisteme kolayca eklenebilmesi için `TableModule` soyut arayüzü ve `TableRegistry` singleton sınıfı kuruldu. Her tablonun kendi veri modelini, doğrulayıcısını ve editörünü bağımsız yönetmesi sağlandı. |
| **COMP-05** | **Eleman Listesi Modülü (`elements_schedule`)** | Tamamlandı | "Ведомость элементов" için `ScheduleItem`, `ElementPart` modelleri, kesit eskizleri (I-profil, kutu, boru, şveller, levha vb.) ve DXF tablo inşa edicisi (`ElementsScheduleTableBuilder`) kodlandı. |
| **COMP-06** | **UI v2 (Linear / Notion SaaS) Mimarisi** | Tamamlandı | Eski v1 iptal edilerek modern koyu tema SaaS arayüzü kuruldu: Compact TopBar (breadcrumb, GOST rozeti, hızlı arama, DXF buton), Notion Sidebar (doküman ağacı, pafta boyutları), TableEditorWrapper ve LinearStatusBar bileşenleri oluşturuldu. |
| **COMP-07** | **UI v2 Başlatıcı Entegrasyonu** | Tamamlandı | `main.py` dosyası doğrudan `from src.ui_v2 import KmLinearMainWindow` başlatacak şekilde güncellendi. `main_v2.py` geriye dönük uyumluluk için buna bağlandı. |
| **COMP-08** | **Kapsamlı Test Süiti** | Tamamlandı | `pytest` altyapısı ile birim ve UI entegrasyon testleri yazıldı ve hepsi başarıyla yeşile ulaştırıldı. |
