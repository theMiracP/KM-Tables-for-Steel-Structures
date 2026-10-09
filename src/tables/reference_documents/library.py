"""
Standartlar ve Referans Dokümanlar Kütüphane Yöneticisi (StandardsLibraryManager).
Kullanıcının hazır standartları seçebilmesi, yeni standart ekleyebilmesi, düzenleyebilmesi
veya silebilmesi (CRUD) için kalıcı JSON tabanlı veri tabanı motoru.
"""
import json
import os
from typing import List, Optional, Dict, Any
from src.tables.reference_documents.model import (
    StandardLibraryItem, ReferenceDocItem, ReferenceDocsDocument
)

# Kütüphane JSON dosyasının varsayılan konumu
CONFIG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "config"))
DEFAULT_LIBRARY_PATH = os.path.join(CONFIG_DIR, "standards_library.json")

# Referans görselde yer alan 14 temel KM standardı + ek temel yapı standartları
DEFAULT_STANDARDS_DATA: List[Dict[str, str]] = [
    {
        "id": "std_gost_27751",
        "designation": "ГОСТ 27751-2014",
        "title_ru": "Надёжность строительных конструкций и оснований. Основные положения",
        "title_tr": "Yapı Taşıyıcı Sistemlerinin ve Temellerin Güvenilirliği. Temel Hükümler",
        "title_en": "Reliability of Construction Structures and Foundations. General Principles",
        "section": "Ссылочные документы",
        "category": "Temel & Güvenilirlik",
        "note": "",
    },
    {
        "id": "std_sp_16",
        "designation": "СП 16.13330.2017",
        "title_ru": "Стальные конструкции",
        "title_tr": "Çelik Yapılar (Güncellenmiş SNiP II-23-81*)",
        "title_en": "Steel Structures (Updated SNiP II-23-81*)",
        "section": "Ссылочные документы",
        "category": "КМ Çelik Yapılar",
        "note": "",
    },
    {
        "id": "std_sp_20",
        "designation": "СП 20.13330.2016",
        "title_ru": "Нагрузки и воздействия",
        "title_tr": "Yükler ve Etkiler (Güncellenmiş SNiP 2.01.07-85*)",
        "title_en": "Loads and Actions (Updated SNiP 2.01.07-85*)",
        "section": "Ссылочные документы",
        "category": "Yükler & Hesap",
        "note": "",
    },
    {
        "id": "std_sp_28",
        "designation": "СП 28.13330.2017",
        "title_ru": "Защита строительных конструкций от коррозии",
        "title_tr": "Yapı Elemanlarının Korozyondan Korunması (Güncellenmiş SNiP 2.03.11-85)",
        "title_en": "Corrosion Protection of Building Structures (Updated SNiP 2.03.11-85)",
        "section": "Ссылочные документы",
        "category": "Korozyon & Boya",
        "note": "",
    },
    {
        "id": "std_sp_48",
        "designation": "СП 48.13330.2019",
        "title_ru": "Организация строительства",
        "title_tr": "İnşaat Organizasyonu ve Yönetimi (Güncellenmiş SNiP 12-01-2004)",
        "title_en": "Organization of Construction (Updated SNiP 12-01-2004)",
        "section": "Ссылочные документы",
        "category": "Uygulama & Şantiye",
        "note": "",
    },
    {
        "id": "std_sp_70",
        "designation": "СП 70.13330.2012",
        "title_ru": "Несущие и ограждающие конструкции",
        "title_tr": "Taşıyıcı ve Cephe/Kuşatıcı Yapı Elemanları (Güncellenmiş SNiP 3.03.01-87)",
        "title_en": "Load-bearing and Enclosing Structures (Updated SNiP 3.03.01-87)",
        "section": "Ссылочные документы",
        "category": "Uygulama & Şantiye",
        "note": "",
    },
    {
        "id": "std_sp_72",
        "designation": "СП 72.13330.2016",
        "title_ru": "Защита строительных конструкций и сооружений от коррозии",
        "title_tr": "Yapı ve Tesislerin Korozyona Karşı Korunması (Uygulama Kuralları)",
        "title_en": "Corrosion Protection of Building Structures and Facilities",
        "section": "Ссылочные документы",
        "category": "Korozyon & Boya",
        "note": "",
    },
    {
        "id": "std_sto_arss",
        "designation": "СТО АРСС 11251254.001-018-5",
        "title_ru": "Изготовление и контроль качества стальных строительных конструкций",
        "title_tr": "Çelik Yapı İmalatı ve Kalite Kontrolü (ARSS Standardı)",
        "title_en": "Manufacturing and Quality Control of Steel Building Structures (ARSS Standard)",
        "section": "Ссылочные документы",
        "category": "КМ Çelik Yapılar",
        "note": "",
    },
    {
        "id": "std_sp_470",
        "designation": "СП 470.1325800.2019",
        "title_ru": "Конструкции стальные. Правила производства работ",
        "title_tr": "Çelik Yapılar. İmalat ve Montaj İş Kuralları",
        "title_en": "Steel Structures. Rules for Execution of Work",
        "section": "Ссылочные документы",
        "category": "КМ Çelik Yapılar",
        "note": "",
    },
    {
        "id": "std_gost_23118",
        "designation": "ГОСТ 23118-2019",
        "title_ru": "Конструкции стальные строительные. Общие технические условия",
        "title_tr": "Çelik Yapı İmalatı. Genel Teknik Şartlar",
        "title_en": "Steel Construction Structures. General Specifications",
        "section": "Ссылочные документы",
        "category": "КМ Çelik Yapılar",
        "note": "",
    },
    {
        "id": "std_snip_12_03",
        "designation": "СНиП 12-03-2001",
        "title_ru": "Безопасность труда в строительстве. Часть 1. Общие требования",
        "title_tr": "İnşaatta İş Sağlığı ve Güvenliği. Bölüm 1. Genel Gereklilikler",
        "title_en": "Occupational Safety in Construction. Part 1. General Requirements",
        "section": "Ссылочные документы",
        "category": "İş Sağlığı & Güvenlik",
        "note": "",
    },
    {
        "id": "std_snip_12_04",
        "designation": "СНиП 12-04-2002",
        "title_ru": "Безопасность труда в строительстве. Часть 2. Строительное производство",
        "title_tr": "İnşaatta İş Sağlığı ve Güvenliği. Bölüm 2. İnşaat Üretim Sahası",
        "title_en": "Occupational Safety in Construction. Part 2. Construction Production",
        "section": "Ссылочные документы",
        "category": "İş Sağlığı & Güvenlik",
        "note": "",
    },
    {
        "id": "std_sp_112",
        "designation": "СП 112.13330.2011",
        "title_ru": "Пожарная безопасность зданий и сооружений",
        "title_tr": "Bina ve Yapıların Yangın Güvenliği (Güncellenmiş SNiP 21-01-97*)",
        "title_en": "Fire Safety of Buildings and Structures (Updated SNiP 21-01-97*)",
        "section": "Ссылочные документы",
        "category": "Yangın Güvenliği",
        "note": "",
    },
    {
        "id": "std_fz_123",
        "designation": "ФЗ №123-ФЗ",
        "title_ru": "Технический регламент о требованиях пожарной безопасности",
        "title_tr": "Yangın Güvenliği Şartlarına İlişkin Federal Teknik Yönetmelik",
        "title_en": "Technical Regulations on Fire Safety Requirements (Federal Law 123-FZ)",
        "section": "Ссылочные документы",
        "category": "Yangın Güvenliği",
        "note": "",
    },
    # Ek Temel ГОСТ Standartları
    {
        "id": "std_gost_21_502",
        "designation": "ГОСТ 21.502-2007",
        "title_ru": "Правила выполнения проектной и рабочей документации металлических конструкций",
        "title_tr": "Metal / Çelik Konstrüksiyon Çizim ve Dokümantasyon Kuralları",
        "title_en": "Rules for Execution of Steel Structure Project and Working Documentation",
        "section": "Ссылочные документы",
        "category": "КМ Çelik Yapılar",
        "note": "",
    },
    {
        "id": "std_gost_21_101",
        "designation": "ГОСТ Р 21.101-2020",
        "title_ru": "Основные требования к проектной и рабочей документации",
        "title_tr": "Proje ve Uygulama Dokümantasyonu Temel Kuralları (SPDS)",
        "title_en": "Basic Requirements for Design and Working Documentation",
        "section": "Ссылочные документы",
        "category": "Genel Proje Standartları",
        "note": "",
    },
    {
        "id": "std_gost_27772",
        "designation": "ГОСТ 27772-2021",
        "title_ru": "Прокат для строительных стальных конструкций. Общие технические условия",
        "title_tr": "Yapı Çelikleri Malzeme Standardı (C245, C255, C345, C355 vb.)",
        "title_en": "Rolled Steel for Building Structures. General Specifications",
        "section": "Ссылочные документы",
        "category": "Malzeme & Çelik",
        "note": "",
    },
    {
        "id": "std_gost_26020",
        "designation": "ГОСТ 26020-83",
        "title_ru": "Двутавры стальные горячекатаные с параллельными гранями полок",
        "title_tr": "Sıcak Haddelenmiş Paralel Başlıklı I-Kiriş Profilleri",
        "title_en": "Hot-rolled Steel I-beams with Parallel Flange Edges",
        "section": "Ссылочные документы",
        "category": "Profiller & Kesitler",
        "note": "",
    },
    {
        "id": "std_gost_8240",
        "designation": "ГОСТ 8240-97",
        "title_ru": "Швеллеры стальные горячекатаные",
        "title_tr": "Sıcak Haddelenmiş Çelik U-Profilleri (Şveller)",
        "title_en": "Hot-rolled Steel Channels",
        "section": "Ссылочные документы",
        "category": "Profiller & Kesitler",
        "note": "",
    },
    {
        "id": "std_gost_8509",
        "designation": "ГОСТ 8509-93",
        "title_ru": "Уголки стальные горячекатаные равнополочные",
        "title_tr": "Sıcak Haddelenmiş Eşit Kollu Köşebentler",
        "title_en": "Hot-rolled Steel Equal-leg Angles",
        "section": "Ссылочные документы",
        "category": "Profiller & Kesitler",
        "note": "",
    },
    {
        "id": "std_gost_30245",
        "designation": "ГОСТ 30245-2003",
        "title_ru": "Профили стальные гнутые замкнутые сварные квадратные и прямоугольные",
        "title_tr": "Kaynaklı Kutu ve Dikdörtgen Çelik Profil Boruları",
        "title_en": "Steel Welded Cold-formed Hollow Square and Rectangular Structural Sections",
        "section": "Ссылочные документы",
        "category": "Profiller & Kesitler",
        "note": "",
    },
    {
        "id": "std_gost_19903",
        "designation": "ГОСТ 19903-2015",
        "title_ru": "Прокат листовой горячекатаный. Сортамент",
        "title_tr": "Sıcak Haddelenmiş Sac ve Levha Boyut Standardı",
        "title_en": "Hot-rolled Steel Sheets and Plates. Dimensions",
        "section": "Ссылочные документы",
        "category": "Malzeme & Sac",
        "note": "",
    },
    # Örnek Ek Dokümanlar (Прилагаемые документы)
    {
        "id": "att_km_vm",
        "designation": "КМ.ВМ",
        "title_ru": "Ведомость потребности в металле",
        "title_tr": "Metal İhtiyaç Tablosu",
        "title_en": "Bill of Metal Requirements",
        "section": "Прилагаемые документы",
        "category": "Ek Dokümanlar",
        "note": "",
    },
    {
        "id": "att_km_tb",
        "designation": "КМ.ТБ",
        "title_ru": "Таблица монтажных болтов",
        "title_tr": "Montaj Civata Tablosu",
        "title_en": "Schedule of Erection Bolts",
        "section": "Прилагаемые документы",
        "category": "Ek Dokümanlar",
        "note": "",
    },
    {
        "id": "att_km_ol",
        "designation": "КМ.ОЛ",
        "title_ru": "Опросный лист",
        "title_tr": "Sipariş ve Teknik Talep Formu",
        "title_en": "Inquiry / Technical Specification Sheet",
        "section": "Прилагаемые документы",
        "category": "Ek Dokümanlar",
        "note": "",
    },
]


class StandardsLibraryManager:
    """
    Standartlar kütüphanesini yöneten singleton/servis sınıfı.
    Kullanıcının standart ekleme, düzenleme, silme ve arama işlemlerini yönetir.
    """
    def __init__(self, file_path: str = DEFAULT_LIBRARY_PATH):
        self.file_path = file_path
        self._standards: List[StandardLibraryItem] = []
        self.load()

    def load(self) -> None:
        """Kütüphaneyi dosyadan yükler, dosya yoksa varsayılanlarla oluşturur."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._standards = [StandardLibraryItem.from_dict(item) for item in data]
                return
            except Exception:
                pass  # Okuma hatasında varsayılanlara dön

        # Varsayılan standartları yükle ve dosyaya kaydet
        self.reset_to_defaults()

    def save(self) -> None:
        """Kütüphaneyi kalıcı JSON dosyasına yazar."""
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump([item.to_dict() for item in self._standards], f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Standartlar kütüphanesi kaydedilirken hata oluştu: {e}")

    def get_all(self) -> List[StandardLibraryItem]:
        """Kütüphanedeki tüm standartları listeler."""
        return list(self._standards)

    def get_by_id(self, item_id: str) -> Optional[StandardLibraryItem]:
        for item in self._standards:
            if item.id == item_id:
                return item
        return None

    def get_by_designation(self, designation: str) -> Optional[StandardLibraryItem]:
        desig_clean = designation.strip().lower()
        for item in self._standards:
            if item.designation.strip().lower() == desig_clean:
                return item
        return None

    def add(self, item: StandardLibraryItem) -> bool:
        """Yeni bir standart ekler ve kaydeder."""
        if not item.designation.strip():
            return False
        # Varsa güncelle, yoksa ekle
        existing = self.get_by_id(item.id)
        if existing:
            return self.update(item)
        self._standards.append(item)
        self.save()
        return True

    def update(self, item: StandardLibraryItem) -> bool:
        """Mevcut bir standardı günceller ve kaydeder."""
        for idx, cur in enumerate(self._standards):
            if cur.id == item.id:
                self._standards[idx] = item
                self.save()
                return True
        return False

    def delete(self, item_id: str) -> bool:
        """Bir standardı kütüphaneden siler ve kaydeder."""
        initial_len = len(self._standards)
        self._standards = [it for it in self._standards if it.id != item_id]
        if len(self._standards) < initial_len:
            self.save()
            return True
        return False

    def search(self, query: str = "", category: str = "Tümü") -> List[StandardLibraryItem]:
        """Arama ve kategori filtrelemesi yapar (TR, EN, RU ve kod üzerinde çalışır)."""
        q = query.strip().lower()
        results = []
        for item in self._standards:
            if category and category not in ("Tümü", "All", "Все"):
                if item.category.strip().lower() != category.strip().lower():
                    continue
            if not q:
                results.append(item)
                continue
            if (
                q in item.designation.lower()
                or q in item.title_ru.lower()
                or q in item.title_tr.lower()
                or q in item.title_en.lower()
                or q in item.note.lower()
            ):
                results.append(item)
        return results

    def get_categories(self) -> List[str]:
        """Mevcut standartların kategorilerini döndürür."""
        cats = sorted(list(set(it.category for it in self._standards if it.category)))
        return ["Tümü"] + cats

    def reset_to_defaults(self) -> None:
        """Kütüphaneyi varsayılan standart listesine sıfırlar."""
        self._standards = [StandardLibraryItem.from_dict(item) for item in DEFAULT_STANDARDS_DATA]
        self.save()

    def build_default_document(self) -> ReferenceDocsDocument:
        """
        Kullanıcının paylaştığı referans görseldeki 14 temel standardı içeren
        başlangıç dokümanını oluşturur.
        """
        items: List[ReferenceDocItem] = []

        # 1. Bölüm Başlığı: Ссылочные документы
        items.append(ReferenceDocItem(
            designation="",
            title="Ссылочные документы",
            title_tr="Referans Dokümanlar",
            title_en="Reference Documents",
            section="Ссылочные документы",
            is_section_header=True,
        ))

        # 2. Görseldeki ilk 14 standart
        for std_data in DEFAULT_STANDARDS_DATA[:14]:
            items.append(ReferenceDocItem(
                designation=std_data["designation"],
                title=std_data["title_ru"],
                title_tr=std_data["title_tr"],
                title_en=std_data["title_en"],
                section="Ссылочные документы",
                note=std_data["note"],
                is_section_header=False,
            ))

        return ReferenceDocsDocument(
            title="Ведомость ссылочных и прилагаемых документов",
            items=items,
        )


# Global singleton kütüphane yöneticisi
standards_library = StandardsLibraryManager()
