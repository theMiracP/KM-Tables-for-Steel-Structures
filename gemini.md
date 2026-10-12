# KM Tablo Oluşturucu — Geliştirici & Ajan Kılavuzu (gemini.md)

Bu dosya, bu repoda çalışacak yapay zeka ajanları (Gemini / Antigravity) ve geliştiriciler için temel mimari ilkeleri, mühendislik standartlarını ve güncel kararları içerir.

---

## 📌 1. Proje Özeti ve Amacı
- **Proje Adı:** KM Tablo Oluşturucu (KM Layout Tables Studio)
- **Kapsam:** Rusya GOST standartlarına uygun Çelik Konstrüksiyon (КМ - Конструкции металлические) teknik çizimlerinde ihtiyaç duyulan **tüm tabloları** (Eleman Listesi, Çelik Sarfiyatı/TSS, Metiz Tablosu vb.) zamanla bünyesine katacak bağımsız, modüler bir CAD masaüstü mühendislik aracıdır. Tek bir tabloyla sınırlı değildir; mimari tüm KM tablolarını destekleyecek şekilde genişleyebilir olmalıdır.
- **Hedef Standartlar:**
  - Tüm tablolar ilgili standartlara **kesinlikle ve tavizsiz uygun** olmalıdır.
  - `ГОСТ 21.502-2007`: Çelik yapı çizimleri ve eleman listesi şemaları.
  - `ГОСТ Р 21.101-2020` / `ГОСТ 2.301`: Pafta boyutları, çerçeve ve Form 3 ana antet (185 x 55 mm).
  - `ГОСТ 2.302-68`: Çizim ölçekleri.
  - *(Standart güncellemeleri veya yeni tablo standartları kullanıcı tarafından iletilecektir).*
- **Temel Yetenekler:**
  - Bağımsız DXF R2010 üretimi (`ezdxf` motoru, AutoCAD gerektirmez, 1:1 ölçek, milimetrik koordinatlar, katmanlı, UTF-8 Kiril metinler).
  - Canlı 2D vektörel CAD önizleme tuvali (Donanım hızlandırmalı QGraphicsView).
  - Masaüstü GUI: PySide6 (Qt6).

---

## 🖥️ 2. Arayüz Mimarisi ve Tasarım İlkeleri
- **Geçerli Arayüz (UI v2):** Projede eski arayüz (v1) tamamen iptal edilmiştir. Kod tabanında v1 artığı bırakılmayacak; tüm geliştirme ve çalıştırma işlemleri **`src/ui_v2`** (Linear / Notion SaaS tarzı) üzerinden yürütülecektir.
- **Başlatıcı:** `main.py` doğrudan `from src.ui_v2 import KmLinearMainWindow` sınıfını çalıştırır.
- **Ana Bileşenler:**
  - `KmLinearMainWindow` (`src/ui_v2/window.py`): Ana uygulama penceresi.
  - `LinearTopBar` (`src/ui_v2/top_bar.py`): Minimalist üst gezinme çubuğu, breadcrumb, GOST rozeti, DXF dışa aktar butonu.
  - `LinearSidebar` (`src/ui_v2/sidebar.py`): Tablo listesi ve her tabloya özel bağımsız pafta parametreleri.
  - `CadViewportPanel` (`src/ui_v2/cad_panel.py`): Canlı CAD tuvali ve üzerinde yüzen Floating Glass HUD araç çubuğu.
  - `TableEditorWrapper` (`src/ui_v2/editor_wrapper.py`): Veri giriş editör sarmalayıcısı.
  - `LinearStatusBar` (`src/ui_v2/status_bar.py`): Alt durum çubuğu.

---

## 📐 3. Mühendislik ve Tablo Kuralları

### Standartlara Bakış İlkesi
- Standartlara göre her tablonun kuralları, sütunları ve hesaplama mantığı kendine özel olabilir.
- Tüm tabloların paylaştığı genel kurallar (antet yerleşimi, katmanlar, yazı tipleri, 1:1 ölçek vb.) ortak altyapıda yönetilirken; tabloya özel kurallar için doğrudan ilgili GOST standardına bakılmalı ve uygulanmalıdır.

### "Ведомость элементов" (Eleman Listesi) Kuralları
Tablo sütunları ГОСТ 21.502 standardına tam uyumlu olmalıdır:
1. **Марка (Marka):** Eleman pozisyon kodu (örn. Б1, К1, Ф1).
2. **Эскиз (Eskiz):** Profil kesit geometrisi (I-kiriş, Kutu, Boru, Levha, Kaynaklı vb.).
3. **Сечение / Состав (Kesit / Profil):** Standart profil veya kaynaklı levha kalınlıkları (örn. `20К1`, `400х200х10`).
4. **Усилия (Kuvvetler):**
   - `A, кН`: Kesme kuvveti (Mesnet tepkisi / Поперечная сила).
   - `N, кН`: Eksenel yük (Normal / boyuna kuvvet / Продольная сила).
   - `M, кН·м`: Eğilme momenti (Изгибающий момент).
   - *(Not: Veri girişinde gereksiz "Q" veya kaymış kuvvet kolonları bulunmaz).*
5. **Сталь (Çelik Kalitesi):** Malzeme standardı (örn. `С255`, `С345`, `09Г2С`).
6. **Примечание (Notlar):** Mühendislik açıklamaları.

### Çift Dilli Başlık Kuralı
Kullanıcı ergonomisi için arayüzdeki tablo başlıkları iki satırlı formatlanır:
- Üstte: **Orijinal Rusça GOST Terimi**
- Altta: **Türkçe Karşılığı** (örn. `Марка\n(Marka)`, `Эскиз\n(Eskiz)`, `N, кН\n(Normal)`)

### DXF Çizim Kuralları
- **Kesin Ölçek:** DXF çıktısı her zaman **1:1 ölçekli** olmalıdır (1 CAD Birimi = 1.0 mm, `$INSUNITS = 4`, metrik).
- **Antet Konumu:** Form 3 ana antet (185 x 55 mm) paftanın **sağ alt köşesinde sabittir**. Pafta boyutu veya yönü (yatay/dikey) değişse bile antet daima sağ alt köşeye kenetlenir. Tablo, antetin sol-üst veya üst sınırına GOST boşluk kurallarına göre yerleşir.
- **Gelecek Antet Alanları:** İleride antetin içerisindeki mühendislik başlık alanları (çizen, onaylayan, proje adı, pafta no vb.) için arayüze özel veri giriş alanları eklenecektir.
- **Katmanlar (Layers):**
  - `KM_TABLO_CERCEVE`: Kalın dış çerçeve (0.50 mm, Beyaz/Siyah).
  - `KM_TABLO_IZGARA`: İnce iç ızgara çizgileri (0.15 mm, Color 8 / Gri).
  - `KM_TABLO_METIN`: Metinler (0.25 mm, Cyan veya Beyaz).
  - `KM_TABLO_ESKIZ`: Kesit eskiz geometrileri (0.35 mm, Sarı/Green).
  - `KM_TABLO_ANTET`: Çerçeve ve antet çizgileri.

---

## 🗂️ 4. Proje Dizin Yapısı
```
KM-Layout-Tables/
├── src/
│   ├── config/              # Standartlar, pafta ve tablo parametreleri
│   ├── contracts/           # Modüler TableModule soyut sınıfı
│   ├── export/              # ezdxf tabanlı DxfExporter motoru (1:1 ölçek)
│   ├── models/              # Tablo, hücre, eskiz, pafta veri modelleri
│   ├── tables/              # Kayıtlı tablo modülleri (elements_schedule vb.)
│   ├── ui/                  # Ortak altyapılar (preview_canvas.py, i18n.py, quick_switcher.py)
│   └── ui_v2/               # Aktif Linear / Notion SaaS arayüz paketi
├── tests/                   # pytest test süiti
├── main.py                  # Uygulama ana başlatıcısı (UI v2)
├── gemini.md                # Geliştirici ve ajan hafıza/kılavuz belgesi
├── README.md                # Kullanıcı kılavuzu
└── TODO.md                  # Güncel yapılacaklar ve revizyon listesi
```

---

## 🧪 5. Test ve Doğrulama Kuralları
- Testleri çalıştırmak için her zaman kök dizinde şu komut kullanılır:
  ```powershell
  python -m pytest
  ```
- Yapılan tüm kod değişikliklerinden sonra mevcut testlerin (ve yeni eklenecek testlerin) kırılmadığı doğrulanmalıdır.
- UI bileşenleri için `qapp` fikstürü kullanılır; pencereler `window.close()` ile temizlenmelidir.

---

## 🚦 6. Önemli Hatırlatmalar & Güncel Kararlar
1. **Çelik Sarfiyat Tablosu:** Mevcut hali iptal edilmiştir ve arayüzden kaldırılacaktır. Doğru standart kurallarıyla zamanı gelince baştan eklenecektir. Ancak `TableModule` ve `TableRegistry` altyapısı gelecekte yeni eklenecek tablolar için tam çalışır halde korunmalıdır.
2. **Pafta Boyutları ve Yönü:** Her paftanın ölçüleri ve yönü birbirinden farklı olabilir. Bu nedenle seçilen pafta ölçüleri ve yönü her tablo için bağımsız hafızada saklanmalıdır.
3. **v1 Artıklarının Temizlenmesi:** Projede v1'e ait eski dosyalar (`app.py`, eski `sidebar.py`, eski `header.py` vb.) temizlenecek, yalnızca ortak kullanılan bileşenler (`preview_canvas.py`, `i18n.py`, `quick_switcher.py`) muhafaza edilecektir.
4. **Dışa Aktarma:** `DxfExporter` metodunun adı `export`'tur. Arayüz çağrılarında `dxf_exporter.export(...)` kullanılmalıdır (ayrıca `export_table` alias olarak desteklenir).
5. **Görev Onay Kuralı:** `TODO.md` dosyasındaki revizyon görevleri kullanıcı tarafından bizzat incelenip onaylanmadıkça en alttaki "Tamamlanan İşler" tablosuna taşınmaz; "Onay Bekliyor" durumunda tutulur.
