"""
KM Tablo Oluşturucu - Çoklu Dil (i18n) ve Yerelleştirme Altyapısı.
Türkçe (TR - Varsayılan), İngilizce (EN) ve Rusça (RU) dil desteği.
"""
from typing import Dict
from PySide6.QtCore import QObject, Signal

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "TR": {
        # Menü Çubuğu
        "menu_file": "Dosya",
        "menu_edit": "Düzen",
        "menu_tables": "Tablolar",
        "menu_view": "Görünüm",
        "menu_tools": "Araçlar",
        "menu_help": "Yardım",

        # Menü Aksiyonları
        "action_new": "Yeni Belge",
        "action_open": "Aç...",
        "action_save": "Kaydet",
        "action_save_as": "Farklı Kaydet...",
        "action_export_dxf": "AutoCAD DXF Dışa Aktar...",
        "action_exit": "Çıkış",
        "action_undo": "Geri Al",
        "action_redo": "Yinele",
        "action_copy": "Kopyala",
        "action_paste": "Yapıştır",
        "action_add_row": "Eleman Ekle",
        "action_delete_row": "Seçiliyi Sil",
        "action_move_up": "Yukarı Taşı",
        "action_move_down": "Aşağı Taşı",
        "action_quick_switch": "Tablo Değiştir (Hızlı Ara)",
        "action_toggle_explorer": "Tablo Gezginini Göster/Gizle",
        "action_toggle_preview": "CAD Önizlemeyi Göster/Gizle",
        "action_fit_view": "Görünümü Sığdır",
        "action_zoom_in": "Yakınlaştır (+)",
        "action_zoom_out": "Uzaklaştır (−)",
        "action_zoom_actual": "Birebir Ölçek (100%)",
        "action_about": "Hakkında",
        "action_shortcuts": "Klavye Kısayolları",

        # Üst Bar ve Genel
        "app_title": "KM TABLO OLUŞTURUCU",
        "app_subtitle": "·  Çelik Konstrüksiyon ГОСТ Tablo Asistanı",
        "table_type": "Tablo Tipi:",
        "fit_view": "Görünümü Sığdır",
        "refresh": "Yenile",
        "export_dxf": "AutoCAD DXF Olarak Dışa Aktar",
        "lang_select": "Dil / Language:",

        # Tablo Gezgini ve Quick Switcher
        "explorer_title": "TABLO GEZGİNİ",
        "search_table_placeholder": "Tablo ara... (Ctrl+T)",
        "quick_switcher_title": "Tablo Değiştir",
        "quick_switcher_hint": "Aramak için tablo adı veya GOST numarası yazın...",

        # Sekmeler (Geriye dönük uyumluluk)
        "tab_elements": "Elemanlar (Таблица)",
        "tab_sheet": "Pafta & Antet (ГОСТ)",
        "tab_info": "Bilgi & Standartlar",

        # Eleman Editörü Toolbar
        "elements_title": "ELEMAN LİSTESİ",
        "add_element": "Eleman Ekle",
        "delete_element": "Sil",
        "move_up": "Yukarı",
        "move_down": "Aşağı",
        "load_samples": "Örnekleri Yükle",
        "clear_table": "Temizle",
        "full_keyboard": "⌨ Tam Klavye",
        "ru_label": "RU:",

        # Tablo Çift Dilli Başlıkları (1. Satır Sabit Rusça GOST, 2. Satır Seçilen Dil)
        "col_sub_mark": "Marka",
        "col_sub_sketch": "Eskiz",
        "col_sub_composition": "Kesit / Profil",
        "col_sub_force_a": "Kesme",
        "col_sub_force_n": "Eksenel",
        "col_sub_force_m": "Moment",
        "col_sub_steel": "Çelik",
        "col_sub_note": "Not",
        "col_mark": "Марка\n(Marka)",
        "col_sketch": "Эскиз\n(Eskiz)",
        "col_composition": "Сечение / Состав\n(Kesit / Profil)",
        "col_force_a": "A, кН\n(Kesme)",
        "col_force_n": "N, кН\n(Eksenel)",
        "col_force_m": "M, кН·м\n(Moment)",
        "col_steel": "Сталь\n(Çelik)",
        "col_note": "Примечание\n(Not)",

        # Çelik Sarfiyat Tablosu (Ведомость расхода стали)
        "steel_consumption_title": "ÇELİK SARFİYAT LİSTESİ",
        "steel_consumption_name": "Ведомость расхода стали (ГОСТ 21.502)",
        "steel_consumption_desc": "Profil ve çelik kalitelerine göre sarfiyat tablosu (ГОСТ 21.502)",

        # Başlık Bloğu (Форма 3 Antet)
        "title_block_title": "ANA ANTET / BAŞLIK BLOĞU",
        "title_block_name": "Основная надпись (Форма 3)",
        "title_block_desc": "ГОСТ Р 21.101-2020 Form 3 ana antet ve revizyon bloğu (185 x 55 mm)",
        "col_sc_mark": "Марка\n(Marka)",
        "col_sc_i_beam": "Двутавры\n(I-Kiriş)",
        "col_sc_channel": "Швеллеры\n(Kanal)",
        "col_sc_angle": "Уголки\n(Köşebent)",
        "col_sc_tube": "Трубы\n(Kutu/Boru)",
        "col_sc_plate": "Лист\n(Sac/Lama)",
        "col_sc_total": "Всего, кг\n(Toplam)",
        "elem_count_fmt": "({count} eleman)",
        "grand_total_fmt": "Toplam: {total} kg",
        "val_sc_empty_table": "Tabloda henüz eleman tanımlanmamış.",
        "val_sc_empty_mark": "Satır #{idx}: Eleman markası boş bırakılamaz.",
        "val_sc_dup_mark": "Satır #{idx}: Yinelenen eleman markası tespit edildi ('{mark}').",
        "val_sc_neg_weight": "Satır #{idx} ('{mark}'): Profil ağırlıkları negatif olamaz.",
        "val_sc_zero_weight": "Satır #{idx} ('{mark}'): Hiçbir profil ağırlığı girilmemiş.",
        "val_sc_invalid_num": "Satır #{idx} ('{mark}'): '{field}' alanı için girilen değer ('{val}') geçerli bir sayı olmalıdır.",

        # Pafta & Yerleşim
        "sheet_panel_title": "SAYFA & YERLEŞİM",
        "placement_label": "Yerleşim:",
        "size_label": "Boyut:",
        "orient_label": "Yönelim:",
        "module_elements_schedule": "ГОСТ 21.502 / Tablo 1 / Eleman Listesi",
        "module_steel_consumption": "ГОСТ 21.502 / Çelik Sarfiyat Listesi",
        "module_title_block": "ГОСТ Р 21.101 / Form 3 / Başlık Bloğu (Antet)",
        "module_reference_docs": "ГОСТ Р 21.101 / Form 2 / Referans ve Ek Dokümanlar",
        "module_main_drawings": "ГОСТ Р 21.101 / Form 2 / Ana Çizim Takımları",
        "module_working_drawings": "ГОСТ Р 21.101 / Form 1 / Çalışma Çizimleri Listesi",
        "col_sub_sheet_num": "Pafta No",
        "col_sub_drawing_name": "Çizim Adı",
        "col_sub_code": "Kod / Standart No",
        "col_sub_ru": "Rusça Başlık",
        "col_sub_tr": "Türkçe Karşılığı",
        "col_sub_en": "English Title",
        "col_sub_sec": "Bölüm",
        "sidebar_tables_header": "TABLOLAR",
        "sidebar_sheet_header": "PAFTA AYARLARI",
        "sidebar_size": "Boyut",
        "sidebar_orientation": "Yön",
        "sidebar_placement": "Yerleşim",
        "placement_standalone": "Yalnızca Tablo (0,0)",
        "placement_above_titleblock": "Antet Üstü (Sağ Alt)",
        "placement_top_right": "Sağ Üst Köşe",
        "placement_top_left": "Sol Üst Köşe",
        "placement_center_sheet": "Pafta Ortası (Merkez)",
        "orient_landscape": "Yatay (Landscape)",
        "orient_portrait": "Dikey (Portrait)",

        # CAD Tuvali Toolbar & Durum
        "cad_title": "CAD ÖNİZLEME",
        "cad_subtitle": "·  1:1 Milimetrik Vektör",
        "zoom_fit": "Sığdır",
        "status_ready": "✓ Hazır. {count} eleman tanımlı. DXF oluşturulabilir.",
        "status_warning": "⚠ Uyarı: {msg}",
        "status_exported": "✓ Başarıyla kaydedildi: {filename}",
        "export_success_title": "Dışa Aktarma Başarılı",
        "export_success_msg": "Tablo AutoCAD DXF formatında başarıyla kaydedildi:\n\n{path}",
        "open_folder_prompt": "Dosyanın bulunduğu klasörü açmak ister misiniz?",
        "btn_open_folder": "📂 Klasörü Aç",
        "btn_close": "Kapat",
        "validation_warn_title": "Eksik / Hatalı Veri",
        "error_title": "Hata",
        "btn_cad_panel": "CAD Ekranı",
        "tooltip_toggle_cad": "CAD Ekranını Gizle / Göster (Ctrl+J)",
        "btn_multi_sheet": "Çoklu Pafta",
        "tooltip_multi_sheet": "Tüm Proje Tablolarını Paftalara Otomatik Yerleştir (ГОСТ)",

        # Editör Konteyneri (TableEditorWrapper) Başlık & Alt Başlıkları
        "wrapper_title_elements_schedule": "ГОСТ 21.502 / Tablo 1 / Eleman Listesi",
        "wrapper_subtitle_elements_schedule": "ГОСТ 21.502-2007 • Çelik Yapı Elemanları Çizim Tablosu",
        "wrapper_title_title_block": "ГОСТ Р 21.101 / Form 3 / Başlık Bloğu (Antet)",
        "wrapper_subtitle_title_block": "ГОСТ Р 21.101-2020 • Form 3 Ana Antet (185 × 55 mm)",
        "wrapper_title_reference_docs": "ГОСТ Р 21.101 / Form 2 / Referans ve Ek Dokümanlar",
        "wrapper_subtitle_reference_docs": "ГОСТ Р 21.101-2020 • Form 2 Referans ve Ek Dokümanlar",
        "wrapper_title_working_drawings": "ГОСТ Р 21.101 / Form 1 / Çalışma Çizimleri Listesi",
        "wrapper_subtitle_working_drawings": "ГОСТ Р 21.101-2020 • Form 1 Çalışma Çizimleri Pafta Listesi",
        "wrapper_title_main_drawings": "ГОСТ Р 21.101 / Form 2 / Ana Çizim Takımları",
        "wrapper_subtitle_main_drawings": "ГОСТ Р 21.101-2020 • Form 2 Çizim Takımları Listesi",
        "wrapper_title_generic": "Standart Çizim Tablosu",
        "wrapper_subtitle_generic": "ГОСТ Standart Mühendislik Tablosu",
        "hint_excel_paste": "Excel'den yapıştırmak için Ctrl+V kullanabilirsiniz",
        "hint_excel_paste_short": "Ctrl+V ile Excel'den Yapıştır",
        "btn_save_preset": "💾 Şablon Kaydet",
        "btn_load_preset": "📂 Şablon Yükle",

        # Referans Dokümanlar Editör Araç Çubuğu & Bilgi Notu
        "btn_standards_lib": "Standart Kütüphanesi",
        "btn_add_document": "Doküman Ekle",
        "btn_add_section": "Bölüm Ekle",
        "btn_delete_row": "Sil",
        "btn_move_up": "Yukarı",
        "btn_move_down": "Aşağı",
        "btn_km_samples": "Hazır KM Standartları",
        "btn_load_samples": "Örnek Verileri Yükle",
        "btn_clear": "Temizle",
        "tag_section": "BÖLÜM",
        "info_ref_docs_title": "💡 ГОСТ Р 21.101 Form 2 Referans ve Ek Dokümanlar Listesi",
        "info_ref_docs_desc": "• Teknik çizim çıktısında (DXF) standart gereği Rusça GOST sütunları (Обозначение, Наименование, Примечание) yer alır.\n• Mühendislerin standardı rahatça inceleyebilmesi için tabloda Türkçe ve İngilizce karşılıkları birlikte sunulmuştur.\n• Kısayollar: [Tab] Sonraki Hücre | [Enter] Alt Hücre | [F2] Düzenle | [Ctrl+C / Ctrl+V] Excel Kopyala/Yapıştır.",

        # Title Block (Form 3 Antet) Çevirileri
        "tb_title_changes": "📐 ТАБЛИЦА ИЗМЕНЕНИЙ (REVİZYONLAR)",
        "tb_title_signatories": "✍️ РАЗРАБОТЧИКИ И ПОДПИСИ (SORUMLULAR)",
        "tb_field_doc_code": "1 • ОБОЗНАЧЕНИЕ ДОКУМЕНТА (DOKÜMAN KODU / ŞİFRESİ)",
        "tb_field_project_name": "2 • НАИМЕНОВАНИЕ ОБЪЕКТА СТРОИТЕЛЬСТВА (TESİS / PROJE ADI & ADRESİ)",
        "tb_field_building_name": "3 • ЗДАНИЕ / СООРУЖЕНИЕ (YAPI / BÖLÜM)",
        "tb_field_stage_sheet_total": "6, 7, 8 • СТАДИЯ / ЛИСТ / ЛИСТОВ (AŞAMA / PAFTA / TOPLAM)",
        "tb_field_sheet_title": "4 • НАИМЕНОВАНИЕ ЧЕРТЕЖА (PAFTA BAŞLIĞI)",
        "tb_field_company": "9 • ОРГАНИЗАЦИЯ (KURULUŞ / ŞİRKET)",
        "tb_col_role": "Должность (Görev)",
        "tb_col_name": "Фамилия (Soyadı)",
        "tb_col_sign": "Подпись (İmza)",
        "tb_col_date": "Дата (Tarih)",
        "tb_col_stage": "Стадия (Aşama)",
        "tb_col_sheet": "Лист (Pafta)",
        "tb_col_sheets": "Листов (Toplam)",
        "tb_col_rev_num": "Изм. (Rev)",
        "tb_col_rev_count": "Кол.уч. (Adet)",
        "tb_col_rev_sheet": "Лист (Pafta)",
        "tb_col_rev_doc": "№док. (No)",
        "tb_logo_show": "Logo Göster",
        "tb_logo_select": "📁 Logo Seç...",
        "tb_info_footer": "Verileri doğrudan antet kutucuklarına yazabilirsiniz. Sağdaki CAD tuvali ve AutoCAD DXF çıktısı 1:1 milimetrik GOST katmanlarıyla eşzamanlı üretilir.",

        # Diğer Editör Butonları ve Bilgi Notları
        "btn_add_drawing_set": "Çizim Takımı Ekle",
        "btn_add_sheet": "Pafta Ekle",
        "info_main_drawings_title": "💡 ГОСТ Р 21.101-2020 Form 2 — Çizim Takımları Listesi (Ведомость основных комплектов рабочих чертежей)",
        "info_main_drawings_desc": "• Tüm alanlar kullanıcı tarafından manuel olarak düzenlenebilir. Excel veya Google Sheets'ten kopyalanan satırlar doğrudan yapıştırılabilir (Ctrl+V).\n• Standart Form 2 genişliği 185 mm'dir (60 + 95 + 30 mm). Tablo başlığı standart gereği tablonun üstünde yer alır ve DXF çıktısında otomatik üretilir.",
        "info_working_drawings_title": "💡 ГОСТ Р 21.101-2020 Form 1 — Çalışma Çizimleri / Pafta Listesi (Ведомость рабочих чертежей основного комплекта)",
        "info_working_drawings_desc": "• Pafta numaraları (1, 2.1, 2.2 vb.) ve çizim adları manuel olarak girilebilir. Excel'den doğrudan kopyala-yapıştır yapılabilir (Ctrl+V).\n• Standart Form 1 toplam genişliği 185 mm'dir (15 + 140 + 30 mm). Tablo başlığı standart gereği tablonun üstünde yer alır ve DXF çıktısında otomatik üretilir.\n• Gelecek Sürüm: Proje PDF dosyalarından pafta listesi otomatik olarak okunup bu tabloya doldurulacaktır.",
        "info_elements_schedule": "<b>ГОСТ 21.502-2007:</b> A (Kesme kuvveti), N (Eksenel yük) ve M (Eğilme momenti) değerleri sırasıyla кН ve кН·м cinsindedir. Kısayollar: <b>Tab</b>: Yan Hücre · <b>Enter</b>: Alt Hücre · <b>F2</b>: Düzenle · <b>Ctrl+V</b>: Excel'den Yapıştır",

        # UI Genel & Arayüz Kontrolleri
        "search_command_bar": "  Hızlı Tablo / Komut Ara...    Ctrl+K ",
        "badge_gost_compliant": "GOST Uyumlu",
        "badge_cad_viewport": "CANLI CAD TUVALİ",
        "sidebar_workspace_title": "KM Proje Çizimleri",
        "sidebar_filter_placeholder": "Tablolarda ara...",
        "sidebar_status_compliant": "✓ ГОСТ 21.502 Uyumlu",
        "sidebar_status_compliant_desc": "Çizim standartlarına tam uyum doğrulandı.",
        "sidebar_status_warning_desc": "Eksik veya standart dışı veri bulundu.",
        "btn_cad_panel_close_tooltip": "CAD Ekranını Kapat (Ctrl+J)",
        "btn_settings": "Ayarlar",
    },
    "EN": {
        "menu_file": "File",
        "menu_edit": "Edit",
        "menu_tables": "Tables",
        "menu_view": "View",
        "menu_tools": "Tools",
        "menu_help": "Help",

        "action_new": "New Document",
        "action_open": "Open...",
        "action_save": "Save",
        "action_save_as": "Save As...",
        "action_export_dxf": "Export AutoCAD DXF...",
        "action_exit": "Exit",
        "action_undo": "Undo",
        "action_redo": "Redo",
        "action_copy": "Copy",
        "action_paste": "Paste",
        "action_add_row": "Add Element",
        "action_delete_row": "Delete Row",
        "action_move_up": "Move Up",
        "action_move_down": "Move Down",
        "action_quick_switch": "Switch Table (Quick Search)",
        "action_toggle_explorer": "Toggle Table Explorer",
        "action_toggle_preview": "Toggle CAD Preview",
        "action_fit_view": "Fit to View",
        "action_zoom_in": "Zoom In (+)",
        "action_zoom_out": "Zoom Out (−)",
        "action_zoom_actual": "Actual Size (100%)",
        "action_about": "About",
        "action_shortcuts": "Keyboard Shortcuts",

        "app_title": "KM TABLE GENERATOR",
        "app_subtitle": "·  GOST Steel Construction Schedule Assistant",
        "table_type": "Table Type:",
        "fit_view": "Fit View",
        "refresh": "Refresh",
        "export_dxf": "Export AutoCAD DXF",
        "lang_select": "Language:",

        "explorer_title": "TABLE EXPLORER",
        "search_table_placeholder": "Search table... (Ctrl+T)",
        "quick_switcher_title": "Switch Table",
        "quick_switcher_hint": "Type table name or GOST standard...",

        "tab_elements": "Elements (Таблица)",
        "tab_sheet": "Sheet & Titleblock (ГОСТ)",
        "tab_info": "Info & Standards",

        "elements_title": "SCHEDULE OF ELEMENTS",
        "add_element": "Add Element",
        "delete_element": "Delete",
        "move_up": "Move Up",
        "move_down": "Move Down",
        "load_samples": "Load Samples",
        "clear_table": "Clear",
        "full_keyboard": "⌨ Full Keyboard",
        "ru_label": "RU:",

        # Schedule Column Sub-labels (Line 1: Russian GOST, Line 2: English)
        "col_sub_mark": "Mark",
        "col_sub_sketch": "Sketch",
        "col_sub_composition": "Section / Profile",
        "col_sub_force_a": "Shear",
        "col_sub_force_n": "Axial",
        "col_sub_force_m": "Moment",
        "col_sub_steel": "Steel",
        "col_sub_note": "Note",
        "col_mark": "Марка\n(Mark)",
        "col_sketch": "Эскиз\n(Sketch)",
        "col_composition": "Сечение / Состав\n(Section / Profile)",
        "col_force_a": "A, кН\n(Shear)",
        "col_force_n": "N, кН\n(Axial)",
        "col_force_m": "M, кН·м\n(Moment)",
        "col_steel": "Сталь\n(Steel)",
        "col_note": "Примечание\n(Note)",

        # Steel Consumption Schedule
        "steel_consumption_title": "STEEL CONSUMPTION SCHEDULE",
        "steel_consumption_name": "Steel Consumption Schedule (GOST 21.502)",
        "steel_consumption_desc": "Steel consumption by profiles and grades (GOST 21.502)",

        # Title Block (Form 3)
        "title_block_title": "TITLE BLOCK",
        "title_block_name": "Title Block (GOST Form 3)",
        "title_block_desc": "GOST R 21.101-2020 Form 3 Title Block (185 x 55 mm)",
        "col_sc_mark": "Element\nMark",
        "col_sc_i_beam": "I-Beams,\nkg",
        "col_sc_channel": "Channels,\nkg",
        "col_sc_angle": "Angles,\nkg",
        "col_sc_tube": "Tubes,\nkg",
        "col_sc_plate": "Plates,\nkg",
        "col_sc_total": "Total,\nkg",
        "elem_count_fmt": "({count} elements)",
        "grand_total_fmt": "Total: {total} kg",
        "val_sc_empty_table": "No elements defined in the table.",
        "val_sc_empty_mark": "Row #{idx}: Element mark cannot be empty.",
        "val_sc_dup_mark": "Row #{idx}: Duplicate element mark detected ('{mark}').",
        "val_sc_neg_weight": "Row #{idx} ('{mark}'): Profile weights cannot be negative.",
        "val_sc_zero_weight": "Row #{idx} ('{mark}'): No profile weights specified.",
        "val_sc_invalid_num": "Row #{idx} ('{mark}'): Invalid numerical value in field '{field}' ('{val}').",

        "sheet_panel_title": "SHEET & PLACEMENT",
        "placement_label": "Placement:",
        "size_label": "Format:",
        "orient_label": "Orientation:",
        "module_elements_schedule": "GOST 21.502 / Table 1 / Elements Schedule",
        "module_steel_consumption": "GOST 21.502 / Steel Consumption Schedule",
        "module_title_block": "GOST R 21.101 / Form 3 / Title Block",
        "module_reference_docs": "GOST R 21.101 / Form 2 / Reference & Attached Documents",
        "module_main_drawings": "GOST R 21.101 / Form 2 / Main Drawing Sets",
        "module_working_drawings": "GOST R 21.101 / Form 1 / Working Drawings Schedule",
        "col_sub_sheet_num": "Sheet No",
        "col_sub_drawing_name": "Drawing Title",
        "col_sub_code": "Code / Standard No",
        "col_sub_ru": "Russian Title",
        "col_sub_tr": "Turkish Translation",
        "col_sub_en": "English Title",
        "col_sub_sec": "Section",
        "sidebar_tables_header": "TABLES",
        "sidebar_sheet_header": "SHEET SETTINGS",
        "sidebar_size": "Size",
        "sidebar_orientation": "Orientation",
        "sidebar_placement": "Placement",
        "placement_standalone": "Standalone Table (0,0)",
        "placement_above_titleblock": "Above Title Block (Bottom-Right)",
        "placement_top_right": "Top-Right Corner",
        "placement_top_left": "Top-Left Corner",
        "placement_center_sheet": "Center Sheet",
        "orient_landscape": "Landscape",
        "orient_portrait": "Portrait",

        "cad_title": "CAD PREVIEW",
        "cad_subtitle": "·  1:1 Millimetric Vector",
        "zoom_fit": "Fit",
        "status_ready": "✓ Ready. {count} elements defined. DXF can be generated.",
        "status_warning": "⚠ Warning: {msg}",
        "status_exported": "✓ Successfully saved: {filename}",
        "export_success_title": "Export Succeeded",
        "export_success_msg": "Table exported to AutoCAD DXF successfully:\n\n{path}",
        "open_folder_prompt": "Would you like to open the containing folder?",
        "btn_open_folder": "📂 Open Folder",
        "btn_close": "Close",
        "validation_warn_title": "Warning",
        "error_title": "Error",
        "btn_cad_panel": "CAD View",
        "tooltip_toggle_cad": "Toggle CAD Viewport (Ctrl+J)",
        "btn_multi_sheet": "Multi Sheet",
        "tooltip_multi_sheet": "Automatically Distribute Project Tables to Sheets (GOST)",

        # Editor Container (TableEditorWrapper) Titles & Subtitles
        "wrapper_title_elements_schedule": "GOST 21.502 / Table 1 / Elements Schedule",
        "wrapper_subtitle_elements_schedule": "GOST 21.502-2007 • Structural Steel Elements Schedule",
        "wrapper_title_title_block": "GOST R 21.101 / Form 3 / Title Block",
        "wrapper_subtitle_title_block": "GOST R 21.101-2020 • Form 3 Title Block (185 x 55 mm)",
        "wrapper_title_reference_docs": "GOST R 21.101 / Form 2 / Reference & Attached Documents",
        "wrapper_subtitle_reference_docs": "GOST R 21.101-2020 • Form 2 Reference & Attached Documents",
        "wrapper_title_working_drawings": "GOST R 21.101 / Form 1 / Working Drawings Schedule",
        "wrapper_subtitle_working_drawings": "GOST R 21.101-2020 • Form 1 Working Drawings Schedule",
        "wrapper_title_main_drawings": "GOST R 21.101 / Form 2 / Main Drawing Sets",
        "wrapper_subtitle_main_drawings": "GOST R 21.101-2020 • Form 2 Main Drawing Sets",
        "wrapper_title_generic": "Standard Engineering Table",
        "wrapper_subtitle_generic": "GOST Standard Engineering Table",
        "hint_excel_paste": "You can use Ctrl+V to paste from Excel",
        "hint_excel_paste_short": "Paste from Excel (Ctrl+V)",
        "btn_save_preset": "💾 Save Preset",
        "btn_load_preset": "📂 Load Preset",

        # Reference Documents Toolbar & Info Card
        "btn_standards_lib": "Standards Library",
        "btn_add_document": "Add Document",
        "btn_add_section": "Add Section",
        "btn_delete_row": "Delete",
        "btn_move_up": "Move Up",
        "btn_move_down": "Move Down",
        "btn_km_samples": "Standard KM Presets",
        "btn_load_samples": "Load Samples",
        "btn_clear": "Clear",
        "tag_section": "SECTION",
        "info_ref_docs_title": "💡 GOST R 21.101 Form 2 Reference and Attached Documents List",
        "info_ref_docs_desc": "• The technical drawing export (DXF) contains standard Russian GOST columns (Обозначение, Наименование, Примечание).\n• Turkish and English translations are provided side-by-side for engineering review.\n• Shortcuts: [Tab] Next Cell | [Enter] Down | [F2] Edit | [Ctrl+C / Ctrl+V] Excel Copy/Paste.",

        # Title Block (Form 3 Antet) Translations
        "tb_title_changes": "📐 ТАБЛИЦА ИЗМЕНЕНИЙ (REVISIONS)",
        "tb_title_signatories": "✍️ РАЗРАБОТЧИКИ И ПОДПИСИ (SIGNATORIES)",
        "tb_field_doc_code": "1 • ОБОЗНАЧЕНИЕ ДОКУМЕНТА (DOCUMENT CODE)",
        "tb_field_project_name": "2 • НАИМЕНОВАНИЕ ОБЪЕКТА СТРОИТЕЛЬСТВА (PROJECT / SITE & ADDRESS)",
        "tb_field_building_name": "3 • ЗДАНИЕ / СООРУЖЕНИЕ (BUILDING / STRUCTURE)",
        "tb_field_stage_sheet_total": "6, 7, 8 • СТАДИЯ / ЛИСТ / ЛИСТОВ (STAGE / SHEET / SHEETS)",
        "tb_field_sheet_title": "4 • НАИМЕНОВАНИЕ ЧЕРТЕЖА (SHEET TITLE)",
        "tb_field_company": "9 • ОРГАНИЗАЦИЯ (COMPANY / ORGANIZATION)",
        "tb_col_role": "Должность (Role)",
        "tb_col_name": "Фамилия (Surname)",
        "tb_col_sign": "Подпись (Sign)",
        "tb_col_date": "Дата (Date)",
        "tb_col_stage": "Стадия (Stage)",
        "tb_col_sheet": "Лист (Sheet)",
        "tb_col_sheets": "Листов (Total)",
        "tb_col_rev_num": "Изм. (Rev)",
        "tb_col_rev_count": "Кол.уч. (Qty)",
        "tb_col_rev_sheet": "Лист (Sheet)",
        "tb_col_rev_doc": "№док. (Doc)",
        "tb_logo_show": "Show Logo",
        "tb_logo_select": "📁 Select Logo...",
        "tb_info_footer": "You can edit data directly in title block fields. CAD preview and AutoCAD DXF export are synchronized 1:1 with GOST layers.",

        # Other Editor Buttons & Info Cards
        "btn_add_drawing_set": "Add Drawing Set",
        "btn_add_sheet": "Add Sheet",
        "info_main_drawings_title": "💡 GOST R 21.101-2020 Form 2 — Main Drawing Sets Schedule (Ведомость основных комплектов рабочих чертежей)",
        "info_main_drawings_desc": "• All fields can be edited manually. Rows copied from Excel or Google Sheets can be pasted directly (Ctrl+V).\n• Standard Form 2 width is 185 mm (60 + 95 + 30 mm). Table title is placed above table by standard and exported in DXF automatically.",
        "info_working_drawings_title": "💡 GOST R 21.101-2020 Form 1 — Working Drawings / Sheet List (Ведомость рабочих чертежей основного комплекта)",
        "info_working_drawings_desc": "• Sheet numbers (1, 2.1, 2.2 etc.) and drawing titles can be edited manually. Excel rows can be pasted directly (Ctrl+V).\n• Standard Form 1 width is 185 mm (15 + 140 + 30 mm). Table title is placed above table by standard and exported in DXF automatically.\n• Future Version: Sheet list will be automatically parsed from project PDF drawings.",
        "info_elements_schedule": "<b>GOST 21.502-2007:</b> A (Shear force), N (Axial load) and M (Bending moment) values are in kN and kN·m. Shortcuts: <b>Tab</b>: Next Cell · <b>Enter</b>: Next Row · <b>F2</b>: Edit · <b>Ctrl+V</b>: Paste from Excel",

        # UI Chrome & Controls
        "search_command_bar": "  Quick Table / Command Palette...    Ctrl+K ",
        "badge_gost_compliant": "GOST Compliant",
        "badge_cad_viewport": "LIVE CAD VIEWPORT",
        "sidebar_workspace_title": "KM Project Drawings",
        "sidebar_filter_placeholder": "Search tables...",
        "sidebar_status_compliant": "✓ GOST 21.502 Compliant",
        "sidebar_status_compliant_desc": "Full drawing standard compliance verified.",
        "sidebar_status_warning_desc": "Incomplete or non-standard data detected.",
        "btn_cad_panel_close_tooltip": "Hide CAD View (Ctrl+J)",
        "btn_settings": "Settings",
    },
    "RU": {
        "menu_file": "Файл",
        "menu_edit": "Правка",
        "menu_tables": "Таблицы",
        "menu_view": "Вид",
        "menu_tools": "Инструменты",
        "menu_help": "Справка",

        "action_new": "Новый документ",
        "action_open": "Открыть...",
        "action_save": "Сохранить",
        "action_save_as": "Сохранить как...",
        "action_export_dxf": "Экспорт в AutoCAD DXF...",
        "action_exit": "Выход",
        "action_undo": "Отменить",
        "action_redo": "Повторить",
        "action_copy": "Копировать",
        "action_paste": "Вставить",
        "action_add_row": "Добавить элемент",
        "action_delete_row": "Удалить строку",
        "action_move_up": "Вверх",
        "action_move_down": "Вниз",
        "action_quick_switch": "Выбрать таблицу (Быстрый поиск)",
        "action_toggle_explorer": "Обозреватель таблиц",
        "action_toggle_preview": "Предпросмотр CAD",
        "action_fit_view": "Вписать в окно",
        "action_zoom_in": "Приблизить (+)",
        "action_zoom_out": "Отдалить (−)",
        "action_zoom_actual": "Масштаб 1:1 (100%)",
        "action_about": "О программе",
        "action_shortcuts": "Горячие клавиши",

        "app_title": "ГЕНЕРАТОР ТАБЛИЦ КМ",
        "app_subtitle": "·  Помощник таблиц КМ по ГОСТ",
        "table_type": "Тип таблицы:",
        "fit_view": "Вписать",
        "refresh": "Обновить",
        "export_dxf": "Экспорт в AutoCAD DXF",
        "lang_select": "Язык:",

        "explorer_title": "ОБОЗРЕВАТЕЛЬ ТАБЛИЦ",
        "search_table_placeholder": "Поиск таблицы... (Ctrl+T)",
        "quick_switcher_title": "Перейти к таблице",
        "quick_switcher_hint": "Введите название таблицы или номер ГОСТ...",

        "tab_elements": "Ведомость элементов",
        "tab_sheet": "Лист и Штамп (ГОСТ)",
        "tab_info": "Справка и ГОСТы",

        "elements_title": "СПИСОК ЭЛЕМЕНТОВ",
        "add_element": "Добавить элемент",
        "delete_element": "Удалить",
        "move_up": "Вверх",
        "move_down": "Вниз",
        "load_samples": "Загрузить примеры",
        "clear_table": "Очистить",
        "full_keyboard": "⌨ Клавиатура",
        "ru_label": "RU:",

        # Подзаголовки столбцов таблицы (Строка 1: ГОСТ, Строка 2: Русский)
        "col_sub_mark": "Марка",
        "col_sub_sketch": "Эскиз",
        "col_sub_composition": "Сечение / Профиль",
        "col_sub_force_a": "Сдвиг",
        "col_sub_force_n": "Осевое",
        "col_sub_force_m": "Момент",
        "col_sub_steel": "Марка стали",
        "col_sub_note": "Инфо",
        "col_mark": "Марка\n(Марка)",
        "col_sketch": "Эскиз\n(Эскиз)",
        "col_composition": "Сечение / Состав\n(Сечение / Профиль)",
        "col_force_a": "A, кН\n(Сдвиг)",
        "col_force_n": "N, кН\n(Осевое)",
        "col_force_m": "M, кН·м\n(Момент)",
        "col_steel": "Сталь\n(Марка стали)",
        "col_note": "Примечание\n(Инфо)",

        # Ведомость расхода стали
        "steel_consumption_title": "ВЕДОМОСТЬ РАСХОДА СТАЛИ",
        "steel_consumption_name": "Ведомость расхода стали (ГОСТ 21.502)",
        "steel_consumption_desc": "Расход стали по профилям и маркам металла (ГОСТ 21.502)",

        # Основная надпись (Форма 3)
        "title_block_title": "ОСНОВНАЯ НАДПИСЬ",
        "title_block_name": "Основная надпись (Форма 3)",
        "title_block_desc": "ГОСТ Р 21.101-2020 Форма 3 основная надпись (185 x 55 мм)",
        "col_sc_mark": "Марка\nэлемента",
        "col_sc_i_beam": "Двутавры,\nкг",
        "col_sc_channel": "Швеллеры,\nкг",
        "col_sc_angle": "Уголки,\nкг",
        "col_sc_tube": "Трубы,\nкг",
        "col_sc_plate": "Лист,\nкг",
        "col_sc_total": "Всего,\nкг",
        "elem_count_fmt": "({count} элем.)",
        "grand_total_fmt": "Всего: {total} кг",
        "val_sc_empty_table": "В таблице нет элементов.",
        "val_sc_empty_mark": "Строка #{idx}: Марка элемента не может быть пустой.",
        "val_sc_dup_mark": "Строка #{idx}: Обнаружена повторяющаяся марка ('{mark}').",
        "val_sc_neg_weight": "Строка #{idx} ('{mark}'): Масса профилей не может быть отрицательной.",
        "val_sc_zero_weight": "Строка #{idx} ('{mark}'): Масса профилей не указана.",
        "val_sc_invalid_num": "Строка #{idx} ('{mark}'): Недопустимое числовое значение в поле '{field}' ('{val}').",

        "sheet_panel_title": "ЛИСТ И РАСПОЛОЖЕНИЕ",
        "placement_label": "Позиция:",
        "size_label": "Формат:",
        "orient_label": "Ориентация:",
        "module_elements_schedule": "ГОСТ 21.502 / Таблица 1 / Ведомость элементов",
        "module_steel_consumption": "ГОСТ 21.502 / Ведомость расхода стали",
        "module_title_block": "ГОСТ Р 21.101 / Форма 3 / Основная надпись",
        "module_reference_docs": "ГОСТ Р 21.101 / Форма 2 / Ведомость ссылочных и прилагаемых документов",
        "module_main_drawings": "ГОСТ Р 21.101 / Форма 2 / Ведомость основных комплектов рабочих чертежей",
        "module_working_drawings": "ГОСТ Р 21.101 / Форма 1 / Ведомость рабочих чертежей основного комплекта",
        "col_sub_sheet_num": "Лист",
        "col_sub_drawing_name": "Наименование",
        "col_sub_code": "Обозначение",
        "col_sub_ru": "Наименование",
        "col_sub_tr": "Турецкий перевод",
        "col_sub_en": "Английский перевод",
        "col_sub_sec": "Раздел",
        "sidebar_tables_header": "ТАБЛИЦЫ",
        "sidebar_sheet_header": "ПАРАМЕТРЫ ЛИСТА",
        "sidebar_size": "Формат",
        "sidebar_orientation": "Ориентация",
        "sidebar_placement": "Размещение",
        "placement_standalone": "Только таблица (0,0)",
        "placement_above_titleblock": "Над основной надписью (Справа внизу)",
        "placement_top_right": "Верхний правый угол",
        "placement_top_left": "Верхний левый угол",
        "placement_center_sheet": "По центру листа",
        "orient_landscape": "Горизонтально",
        "orient_portrait": "Вертикально",

        "cad_title": "ПРЕДПРОСМОТР CAD",
        "cad_subtitle": "·  1:1 Векторный вид",
        "zoom_fit": "Вписать",
        "status_ready": "✓ Готово. Элементов: {count}. Можно экспортировать.",
        "status_warning": "⚠ Предупреждение: {msg}",
        "status_exported": "✓ Успешно сохранено: {filename}",
        "export_success_title": "Экспорт завершен",
        "export_success_msg": "Таблица успешно экспортирована в AutoCAD DXF:\n\n{path}",
        "open_folder_prompt": "Открыть папку с сохраненным файлом?",
        "btn_open_folder": "📂 Открыть папку",
        "btn_close": "Закрыть",
        "validation_warn_title": "Предупреждение",
        "error_title": "Ошибка",
        "btn_cad_panel": "Панель CAD",
        "tooltip_toggle_cad": "Скрыть / Показать экран CAD (Ctrl+J)",
        "btn_multi_sheet": "Многолистовой план",
        "tooltip_multi_sheet": "Автоматическое размещение всех таблиц проекта по листам (ГОСТ)",

        # Заголовки и подзаголовки редактора (TableEditorWrapper)
        "wrapper_title_elements_schedule": "ГОСТ 21.502 / Таблица 1 / Ведомость элементов",
        "wrapper_subtitle_elements_schedule": "ГОСТ 21.502-2007 • Элементы металлических конструкций",
        "wrapper_title_title_block": "ГОСТ Р 21.101 / Форма 3 / Основная надпись",
        "wrapper_subtitle_title_block": "ГОСТ Р 21.101-2020 • Форма 3 Основная надпись (185 x 55 мм)",
        "wrapper_title_reference_docs": "ГОСТ Р 21.101 / Форма 2 / Ведомость ссылочных и прилагаемых документов",
        "wrapper_subtitle_reference_docs": "ГОСТ Р 21.101-2020 • Форма 2 Ссылочные и прилагаемые документы",
        "wrapper_title_working_drawings": "ГОСТ Р 21.101 / Форма 1 / Ведомость рабочих чертежей основного комплекта",
        "wrapper_subtitle_working_drawings": "ГОСТ Р 21.101-2020 • Форма 1 Рабочие чертежи основного комплекта",
        "wrapper_title_main_drawings": "ГОСТ Р 21.101 / Форма 2 / Ведомость основных комплектов рабочих чертежей",
        "wrapper_subtitle_main_drawings": "ГОСТ Р 21.101-2020 • Форма 2 Основные комплекты рабочих чертежей",
        "wrapper_title_generic": "Стандартная таблица",
        "wrapper_subtitle_generic": "Инженерная таблица по стандарту ГОСТ",
        "hint_excel_paste": "Для вставки из Excel используйте Ctrl+V",
        "hint_excel_paste_short": "Вставка из Excel (Ctrl+V)",
        "btn_save_preset": "💾 Сохранить шаблон",
        "btn_load_preset": "📂 Загрузить шаблон",

        # Панель инструментов ссылочных документов и инфо-карточка
        "btn_standards_lib": "Библиотека стандартов",
        "btn_add_document": "Добавить документ",
        "btn_add_section": "Добавить раздел",
        "btn_delete_row": "Удалить",
        "btn_move_up": "Вверх",
        "btn_move_down": "Вниз",
        "btn_km_samples": "Стандарты КМ",
        "btn_load_samples": "Загрузить примеры",
        "btn_clear": "Очистить",
        "tag_section": "РАЗДЕЛ",
        "info_ref_docs_title": "💡 ГОСТ Р 21.101 Форма 2 Ведомость ссылочных и прилагаемых документов",
        "info_ref_docs_desc": "• В техническом чертеже (DXF) по стандарту отображаются столбцы на русском языке (Обозначение, Наименование, Примечание).\n• Для удобства инженеров перевод на турецкий и английский языки представлен параллельно.\n• Горячие клавиши: [Tab] След. ячейка | [Enter] Вниз | [F2] Изменить | [Ctrl+C / Ctrl+V] Копировать/Вставить Excel.",

        # Основная надпись (Форма 3 Штамп) Переводы
        "tb_title_changes": "📐 ТАБЛИЦА ИЗМЕНЕНИЙ",
        "tb_title_signatories": "✍️ РАЗРАБОТЧИКИ И ПОДПИСИ",
        "tb_field_doc_code": "1 • ОБОЗНАЧЕНИЕ ДОКУМЕНТА",
        "tb_field_project_name": "2 • НАИМЕНОВАНИЕ ОБЪЕКТА СТРОИТЕЛЬСТВА",
        "tb_field_building_name": "3 • ЗДАНИЕ / СООРУЖЕНИЕ",
        "tb_field_stage_sheet_total": "6, 7, 8 • СТАДИЯ / ЛИСТ / ЛИСТОВ",
        "tb_field_sheet_title": "4 • НАИМЕНОВАНИЕ ЧЕРТЕЖА",
        "tb_field_company": "9 • ОРГАНИЗАЦИЯ",
        "tb_col_role": "Должность",
        "tb_col_name": "Фамилия",
        "tb_col_sign": "Подпись",
        "tb_col_date": "Дата",
        "tb_col_stage": "Стадия",
        "tb_col_sheet": "Лист",
        "tb_col_sheets": "Листов",
        "tb_col_rev_num": "Изм.",
        "tb_col_rev_count": "Кол.уч.",
        "tb_col_rev_sheet": "Лист",
        "tb_col_rev_doc": "№док.",
        "tb_logo_show": "Показать логотип",
        "tb_logo_select": "📁 Выбрать логотип...",
        "tb_info_footer": "Данные вводятся непосредственно в графы штампа. CAD вид и экспорт AutoCAD DXF синхронизированы 1:1 по слоям ГОСТ.",

        # Кнопки и подсказки других редакторов
        "btn_add_drawing_set": "Добавить комплект",
        "btn_add_sheet": "Добавить лист",
        "info_main_drawings_title": "💡 ГОСТ Р 21.101-2020 Форма 2 — Ведомость основных комплектов рабочих чертежей",
        "info_main_drawings_desc": "• Все поля заполняются вручную. Строки из Excel можно вставлять напрямую (Ctrl+V).\n• Ширина таблицы по Форме 2 составляет 185 мм (60 + 95 + 30 мм). Заголовок формируется автоматически в соответствии с ГОСТ.",
        "info_working_drawings_title": "💡 ГОСТ Р 21.101-2020 Форма 1 — Ведомость рабочих чертежей основного комплекта",
        "info_working_drawings_desc": "• Номера листов (1, 2.1, 2.2 и т.д.) и наименования вводятся вручную. Поддерживается вставка из Excel (Ctrl+V).\n• Ширина таблицы по Форме 1 составляет 185 мм (15 + 140 + 30 мм). Заголовок формируется по ГОСТ автоматически.\n• В будущей версии: Список листов будет считываться из PDF-файлов чертежей проекта.",
        "info_elements_schedule": "<b>ГОСТ 21.502-2007:</b> Значения A (Перерезывающая сила / сдвиг), N (Осевая / продольная сила) и M (Изгибающий момент) указываются в кН и кН·м. Горячие клавиши: <b>Tab</b>: След. ячейка · <b>Enter</b>: След. строка · <b>F2</b>: Правка · <b>Ctrl+V</b>: Вставка из Excel",

        # Интерфейс и элементы управления
        "search_command_bar": "  Быстрый переход / Команды...    Ctrl+K ",
        "badge_gost_compliant": "ГОСТ Совместимо",
        "badge_cad_viewport": "ИНТЕРАКТИВНЫЙ CAD ВИД",
        "sidebar_workspace_title": "Чертежи проекта КМ",
        "sidebar_filter_placeholder": "Поиск таблиц...",
        "sidebar_status_compliant": "✓ Соответствует ГОСТ 21.502",
        "sidebar_status_compliant_desc": "Полное соответствие стандартам чертежей.",
        "sidebar_status_warning_desc": "Обнаружены неполные или нестандартные данные.",
        "btn_cad_panel_close_tooltip": "Скрыть CAD вид (Ctrl+J)",
        "btn_settings": "Настройки",
    }
}


class LocalizationManager(QObject):
    """Merkezi dil yöneticisi."""
    language_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self._current_lang = "TR"

    @property
    def current_language(self) -> str:
        return self._current_lang

    def set_language(self, lang_code: str):
        code_upper = lang_code.upper()
        if code_upper in TRANSLATIONS and code_upper != self._current_lang:
            self._current_lang = code_upper
            self.language_changed.emit(code_upper)

    def t(self, key: str, **kwargs) -> str:
        lang_dict = TRANSLATIONS.get(self._current_lang, TRANSLATIONS["TR"])
        text = lang_dict.get(key, TRANSLATIONS["TR"].get(key, key))
        if kwargs:
            try:
                text = text.format(**kwargs)
            except Exception:
                pass
        return text


# Global tekil nesne
i18n = LocalizationManager()


def get_module_display_title(module_or_id) -> str:
    """
    Tüm programda (Sidebar, Quick Switcher, Dialoglar vb.) tek tip, standart tablo adını döner.
    Aktif seçilen dile (TR/RU/EN) göre anlık yerelleştirilir.
    """
    mod_id = getattr(module_or_id, "id", str(module_or_id))
    raw_name = getattr(module_or_id, "name", "")
    if not raw_name:
        try:
            from src.models.registry import TableRegistry
            m = TableRegistry.get(mod_id)
            if m:
                raw_name = m.name
        except Exception:
            pass

    if "elements" in mod_id or "elementov" in mod_id:
        return i18n.t("module_elements_schedule")
    elif "title_block" in mod_id or "antet" in mod_id:
        return i18n.t("module_title_block")
    elif "reference" in mod_id or "doc" in mod_id:
        return i18n.t("module_reference_docs")
    elif "working_drawings" in mod_id:
        return i18n.t("module_working_drawings")
    elif "main_drawings" in mod_id or "drawings" in mod_id or "main_sets" in mod_id:
        return i18n.t("module_main_drawings")
    elif "steel" in mod_id or "raskhod" in mod_id or "sarfiyat" in mod_id:
        return i18n.t("module_steel_consumption")
    else:
        return raw_name.split("(")[0].strip() if raw_name else mod_id
