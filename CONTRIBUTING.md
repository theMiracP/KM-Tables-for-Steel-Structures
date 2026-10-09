# Katkıda Bulunma Rehberi (Contributing Guide)

**KM Layout Tables Studio** projesine katkıda bulunmak istediğiniz için teşekkürler! Bu proje, Rusya GOST standartlarına uygun Çelik Konstrüksiyon (КМ) teknik çizim tabloları oluşturan bağımsız bir CAD mühendislik aracıdır.

---

## 🛠️ Geliştirme Ortamı Kurulumu

1. Projeyi çatallayın (Fork) ve yerel makinenize klonlayın:
   ```bash
   git clone https://github.com/<kullanici_adiniz>/KM-Tables-for-Steel-Structures.git
   cd KM-Tables-for-Steel-Structures
   ```

2. Sanal ortam oluşturun ve aktif edin:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```

3. Gerekli bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

4. Uygulamayı başlatın:
   ```bash
   python main.py
   ```

---

## 📐 Mühendislik & Standart Kuralları

- **Kesin Standart Uyumu:** Tablolar ve çizim geometrileri GOST standartlarına (`ГОСТ 21.502-2007`, `ГОСТ Р 21.101-2020`, `ГОСТ 2.301`, `ГОСТ 2.302-68`) kesinlikle uygun olmalıdır.
- **1:1 Ölçek:** Üretilen DXF çizimlerinde 1 CAD birimi daima 1.0 mm olmalıdır (`$INSUNITS = 4`).
- **Arayüz Mimarisi:** Geliştirmeler `src/ui_v2` (Linear / Notion temalı modern SaaS arayüzü) üzerinden yürütülmelidir.
- **Çoklu Dil Desteği:** Yeni eklenen arayüz metinleri `src/ui/i18n.py` içerisine eklenmelidir.

---

## 🧪 Testler

Yapılan her değişikliğin mevcut özellikleri bozmadığından emin olmak için test süitini çalıştırın:

```bash
python -m pytest
```

Yeni bir modül veya özellik eklediğinizde lütfen `tests/` dizini altına ilgili birim testlerini de ekleyin.

---

## 🚀 Değişiklik Gönderme (Pull Request)

1. Anlamlı bir dal (branch) açın:
   ```bash
   git checkout -b feature/yeni-tablo-adi
   ```
2. Değişikliklerinizi commit edin (Conventional Commits önerilir: `feat:`, `fix:`, `docs:`, `refactor:`):
   ```bash
   git commit -m "feat: GOST 21.502 yeni kesit tipi eklendi"
   ```
3. Dalınızı uzak depoya gönderin ve GitHub üzerinden Pull Request (PR) açın.
