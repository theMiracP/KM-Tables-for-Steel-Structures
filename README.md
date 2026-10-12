# KM Layout Tables Studio (КМ Tablo Oluşturucu)

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/GUI-PySide6%20%2F%20Qt6-green?style=flat-square&logo=qt" alt="PySide6 / Qt6">
  <img src="https://img.shields.io/badge/CAD-ezdxf%20R2010-orange?style=flat-square" alt="ezdxf R2010">
  <img src="https://img.shields.io/badge/Tests-132%20Passed%20(100%25)-brightgreen?style=flat-square" alt="Tests">
  <img src="https://img.shields.io/badge/Standards-GOST%2021.502%20%7C%20GOST%2021.101-purple?style=flat-square" alt="GOST Standards">
  <a href="https://www.zadax.net" target="_blank"><img src="https://img.shields.io/badge/Website-zadax.net-darkblue?style=flat-square" alt="zadax.net"></a>
</p>

Rusya **GOST** standartlarına uygun Çelik Konstrüksiyon (**КМ - Конструкции металлические**) teknik çizimlerinde kullanılan tüm mühendislik tablolarını saniyeler içinde parametrik olarak oluşturan, canlı 2D vektörel CAD tuvalinde anlık önizleme sunan ve AutoCAD gerektirmeyen bağımsız **1:1 DXF (AutoCAD R2010)** formatında dışa aktaran modern, modüler masaüstü CAD mühendislik stüdyosudur.

---

## ✨ Öne Çıkan Özellikler

### 📐 1. Rusya GOST Standartlarına Kesin ve Tavizsiz Uyum
- **ГОСТ 21.502-2007 (Ведомость элементов / Eleman Listesi):**
  - Standart 7 sütun: Marka (`Марка`), Kesit Eskizi (`Эскиз`), Profil/Bileşen (`Сечение / Состав`), Eksenel Kuvvet (`N, кН`), Eğilme Momenti (`M, кН·м`), Çelik Kalitesi (`Сталь`), Notlar (`Примечание`).
  - Dahili profil eskiz geometrileri (I-Profil, Kutu Profil, Yuvarlak Boru, Şveller, Levha vb.).
- **ГОСТ Р 21.101-2020 Form 3 (Başlık Bloğu / Form 3 Ana Antet):**
  - $185 \times 55\text{ mm}$ milimetrik ana antet; pafta boyutu veya yönü ne olursa olsun **daima sağ alt köşeye kilitlenir**.
  - Kurumsal şirket logosu (PNG, JPG, BMP) ekleme ve antet içinde otomatik ölçekleme desteği.
- **ГОСТ Р 21.101-2020 Form 2 (Ведомость ссылочных и прилагаемых документов):**
  - Referans ve Ek Dokümanlar Tablosu ($185\text{ mm}$ genişlik).
  - Kullanıma hazır **14 temel KM çelik standardı** içeren kalıcı, çok dilli (RU / TR / EN) ve CRUD destekli Standartlar Kütüphanesi.
- **ГОСТ Р 21.101-2020 Form 2 (Ведомость основных комплектов рабочих чертежей):**
  - Ana Çizim Takımları Listesi tablosu ($185\text{ mm}$ genişlik).
- **ГОСТ Р 21.101-2020 Form 1 (Ведомость рабочих чертежей основного комплекта):**
  - Pafta Çizimleri Listesi tablosu ($185\text{ mm}$ genişlik).
- **ГОСТ 2.104-2006 & ГОСТ Р 21.101 Sol Cilt Kenarı Ek Tabloları:**
  - $20\text{ mm}$ sol ciltleme kenarında Form 1a/2a İnventar Tablosu (`Инв. № подл.`, `Подп. и дата`, `Взам. инв. №`) ve 90° döndürülmüş onay damgası (`Согласовано`).
- **ГОСТ 2.301-68 Pafta Formatı Alt Etiketi:**
  - Pafta alt çerçevesi dışında yer alan dinamik format göstergesi (`Формат А3А`, `Формат А1А` vb.).
- **ГОСТ 2.302-68 (Kesin 1:1 Metrik Ölçek):**
  - Tüm çizimler milimetrik hassasiyette ($1\text{ CAD Birimi} = 1.0\text{ mm}$, `$INSUNITS = 4`) üretilir.

### 🖥️ 2. Linear & Notion SaaS Tarzı Modern Arayüz (UI v2)
- **Obsidian Dark Teması:** Göz yormayan koyu renk paleti, 1px ultra-ince kenarlıklar ve Linear moru vurgusu.
- **Notion Tarzı Doküman Gezintisi:** Sol kenar çubuğundan tablolar arasında anında geçiş, arama filtresi ve durum rozetleri.
- **Hızlı Komut Paleti:** Klavyeden `Ctrl+K` veya `Ctrl+T` ile anında arama ve hızlı tablo değiştirici (Quick Switcher).
- **Çift Dilli Dinamik Başlıklar:** Kullanıcı ergonomisi için üstte orijinal Rusça GOST terimi, altta seçilen dildeki çevirisi (TR, EN, RU tek tıkla dil değiştirme).
- **Gelişmiş Hücre Düzenleyici:** Hücre içi düzenleme sırasında opak zemin, metin çakışmasını engelleyen `SolidItemDelegate` ve Excel/Google Sheets uyumlu TSV kopyala-yapıştır (`Ctrl+C`, `Ctrl+V`).
- **Bağımsız Pafta Hafızası:** Her tablo için bağımsız sayfa boyutu (A4, A3, A2, A1, A0), yönelim (Yatay / Dikey) ve pafta içi yerleşim (Antet Üstü, Sol Üst, Sağ Üst, Pafta Ortası).

### ⚡ 3. Canlı 2D Vektörel CAD Tuvali & Bağımsız DXF Motoru
- **Donanım Hızlandırmalı Tuval:** PySide6 `QGraphicsView` tabanlı canlı çizim ekranı; akıcı fare ile kaydırma (Pan), tekerlek ile yakınlaştırma (Zoom).
- **Floating Glass HUD:** Tuval üzerinde yüzen şeffaf cam araç çubuğu (Ekrana Sığdır, %100 Görünüm, Yakınlaştır/Uzaklaştır, Gerçek Zamanlı Koordinat Takibi).
- **AutoCAD Lisansı Gerektirmez:** `ezdxf R2010` çekirdeği ile bağımsız çalışır.
- **Katmanlı (Layered) Yapı:**
  - `KM_TABLO_CERCEVE` (0.50 mm kalın dış çerçeve)
  - `KM_TABLO_IZGARA` (0.15 mm ince iç ızgara)
  - `KM_TABLO_METIN` (0.25 mm UTF-8 Kiril metinler)
  - `KM_TABLO_ESKIZ` (0.35 mm kesit eskiz geometrileri)
  - `KM_TABLO_ANTET` (Pafta çerçevesi ve Form 3 antet çizgileri)
- **%100 WYSIWYG (Ne Görüyorsan Onu Alırsın):** Canlı CAD tuvalindeki yazı boyutları, satır kaydırmaları ve hücre hizalamaları DXF çıktısıyla milimetrik olarak birebir örtüşür. Otomatik kelime sarımı (word-wrap) ve dinamik font ölçekleme sayesinde hücre dışına taşma yaşanmaz.

### 🌐 4. zadax.net Entegrasyonu ve Versiyon Bildirimi
- Hakkında (About) penceresinde resmi web sitesi bağlantısı: [www.zadax.net](https://www.zadax.net).
- Otomatik dosya indirmesi yapmadan, zadax.net üzerinden en son sürümü denetleyen hafif versiyon kontrolü (**Version Checker**).
- Yeni sürüm tespit edildiğinde kullanıcıyı bilgilendirme ve onay ile doğrudan zadax.net ürün/indirme sayfasını açma desteği.

---

## 📁 Proje Dizin Yapısı

```
KM-Layout-Tables/
├── src/
│   ├── config/              # Standartlar, pafta ölçüleri, tablo boyutları ve kütüphane JSON
│   ├── contracts/           # Modüler TableModule soyut sınıf sözleşmesi
│   ├── export/              # AutoCAD gerektirmeyen ezdxf tabanlı 1:1 DXF dışa aktarma motoru
│   ├── models/              # Geometri, Tablo, Hücre, Eskiz, Pafta ve Dinamik Metin Modelleri
│   ├── services/            # zadax.net versiyon kontrolü ve güncelleme bildirim servisi
│   ├── tables/              # Kayıtlı ve genişletilebilir GOST tablo modülleri
│   │   ├── elements_schedule/    # ГОСТ 21.502 Eleman Listesi (Ведомость элементов)
│   │   ├── title_block/          # ГОСТ Р 21.101 Form 3 Ana Antet ve Logo Motoru
│   │   ├── reference_documents/  # ГОСТ Р 21.101 Form 2 Referans ve Ek Dokümanlar Tablosu
│   │   ├── main_drawings/        # ГОСТ Р 21.101 Form 2 Ana Takım Çizim Listesi Tablosu
│   │   └── working_drawings/     # ГОСТ Р 21.101 Form 1 Çalışma Çizimleri Pafta Listesi Tablosu
│   ├── ui/                  # Ortak altyapılar (CAD Tuvali, Çok Dilli i18n, Komut Paleti)
│   ├── ui_v2/               # Aktif Linear / Notion SaaS Masaüstü Arayüzü
│   │   ├── window.py        # Ana pencere (KmLinearMainWindow)
│   │   ├── top_bar.py       # SaaS minimalist üst menü, dil seçici, GOST rozeti
│   │   ├── sidebar.py       # Notion tarzı sol navigasyon paneli ve pafta ayarları
│   │   ├── editor_wrapper.py# Dinamik tablo editör sarmalayıcısı
│   │   ├── cad_panel.py     # Canlı CAD tuvali ve Floating Glass HUD
│   │   ├── about_dialog.py  # zadax.net web bağlantılı Hakkında & Güncelleme penceresi
│   │   └── theme_linear.py  # Obsidian Dark teması ve QSS stilleri
│   └── version.py           # Merkezi sürüm ve ürün bilgileri (v1.3.0)
├── tests/                   # Kapsamlı pytest test süiti (168 test, %100 başarılı)
├── main.py                  # Uygulama ana başlatıcısı (UI v2)
├── requirements.txt         # Python bağımlılıkları (PySide6, ezdxf, Pillow, pytest)
├── README.md                # Proje tanıtım ve kullanıcı kılavuzu
└── TODO.md                  # Görev takibi ve mimari karar kayıtları
```

---

## ⚡ Kurulum ve Çalıştırma

### 1. Gereksinimler
- **Python:** 3.10 veya üzeri (3.11+ önerilir)
- **İşletim Sistemi:** Windows 10 / 11, Linux veya macOS

### 2. Bağımlılıkları Yükleme
Repoyu klonlayın ve gerekli Python paketlerini yükleyin:

```bash
git clone https://github.com/theMiracP/KM-Tables-for-Steel-Structures.git
cd KM-Tables-for-Steel-Structures
pip install -r requirements.txt
```

### 3. Uygulamayı Başlatma
Doğrudan ana betiği çalıştırın:

```bash
python main.py
```

---

## 🧪 Test Süiti ve Doğrulama

Tüm modelleri, parametrik geometri motorunu, metin sarım algoritmalarını, çoklu dil desteğini ve DXF dışa aktarma doğruluğunu test etmek için kök dizinde şu komutu çalıştırın:

```bash
python -m pytest
```

> ✅ **Mevcut Durum:** 132 testin tamamı (%100) başarıyla geçmektedir.

---

## 📐 AutoCAD ve CAD Yazılımlarında Kullanım

1. **Tablonuzu Seçin ve Verilerinizi Girin:**
   - Sol menüden düzenlemek istediğiniz GOST tablosunu seçin.
   - Excel'den veri kopyalayıp doğrudan tabloya yapıştırabilir veya manuel düzenleyebilirsiniz.
2. **Pafta Boyutunu ve Yerleşimini Belirleyin:**
   - Sayfa boyutunu (A3, A4, A2, A1 vb.) ve yönelimini belirleyin.
   - Tablonun Form 3 antetinin üstüne mi yoksa paftanın farklı bir köşesine mi yerleşeceğini seçin.
3. **Canlı Tuvalde Kontrol Edin:**
   - Sağ taraftaki CAD tuvalinde pan ve zoom yaparak çiziminizi milimetrik olarak denetleyin.
4. **DXF Olarak Dışa Aktarın:**
   - Üst bardaki **"⚡ DXF Dışa Aktar"** butonuna basın.
5. **CAD Yazılımında Açın:**
   - Üretilen DXF dosyasını **AutoCAD, BricsCAD, ZWCAD, DraftSight** veya **DWG TrueView** ile doğrudan açabilir ya da mevcut bir çizim içine `INSERT` komutu ile blok olarak ekleyebilirsiniz.

---

## 🌐 Bağlantılar & Lisans

- **Resmi Web Sitesi:** [www.zadax.net](https://www.zadax.net)
- **Lisans:** Bu proje [MIT Lisansı](LICENSE) altında sunulmaktadır.
- **Katkıda Bulunma:** Hata bildirimleri, standart önerileri veya katkılar için Pull Request açabilir ya da Issue oluşturabilirsiniz.
