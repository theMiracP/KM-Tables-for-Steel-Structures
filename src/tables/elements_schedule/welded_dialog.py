"""
KM Studio - Kaynaklı / Bileşik Kesit Bileşen Düzenleyici (WeldedSectionDialog).
ГОСТ 21.502 Tablo 1 standartlarına uygun olarak 1-2 ve 1-2-3 pozisyonlu
kaynaklı kesit parçalarının (Полка, Стенка) parametrik tanımlanması.
"""
from typing import Optional, List
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QWidget
)
from src.models.sketch import SketchType
from src.tables.elements_schedule.sketch_renderer import get_sketch_icon
from src.ui_v2 import theme_linear as theme


class WeldedSectionDialog(QDialog):
    """
    Kaynaklı I-kiriş, kaynaklı kutu, T-profil ve haç kolonlar için
    çok parçalı levha bileşen düzenleyicisi.
    """
    def __init__(self, sketch_type: SketchType, current_composition: str = "", parent=None):
        super().__init__(parent)
        self.sketch_type = sketch_type
        self.result_composition = ""

        # Başlık ve parça tanımları
        self.parts_meta = self._get_parts_metadata(sketch_type)
        self.part_edits: List[QLineEdit] = []

        self.setWindowTitle("Kaynaklı Kesit Bileşenleri (ГОСТ 21.502)")
        self.resize(520, 360)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme.BG_APP};
                color: {theme.TEXT_PRIMARY};
            }}
        """)

        self._build_ui(current_composition)

    def _get_parts_metadata(self, stype: SketchType):
        if stype in (SketchType.WELDED_I_PACKAGE, SketchType.WELDED_CRUCIFORM):
            return [
                ("1", "Поз. 1 • Dış Flanş Levhası (Полка)", "-300 x 14"),
                ("2", "Поз. 2 • İç Flanş / Kanat Levhası (Полка)", "-260 x 12"),
                ("3", "Поз. 3 • Gövde Levhası (Стенка)", "-500 x 10"),
            ]
        elif stype == SketchType.WELDED_T:
            return [
                ("1", "Поз. 1 • Flanş Levhası (Полка)", "-200 x 12"),
                ("2", "Поз. 2 • Gövde Levhası (Стенка)", "-180 x 10"),
            ]
        elif stype == SketchType.COMPOUND_BOX_WELDED:
            return [
                ("1", "Поз. 1 • Üst / Alt Flanş Levhası (Полка)", "-130 x 12"),
                ("2", "Поз. 2 • Yan Gövde Levhaları (Стенка)", "-106 x 12"),
            ]
        else:  # WELDED_I_BEAM ve varsayılan 1-2
            return [
                ("1", "Поз. 1 • Flanş Levhası (Полка)", "-130 x 12"),
                ("2", "Поз. 2 • Gövde Levhası (Стенка)", "-106 x 12"),
            ]

    def _build_ui(self, initial_comp: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        # 1. Başlık ve İkon
        header = QHBoxLayout()
        lbl_icon = QLabel()
        lbl_icon.setPixmap(get_sketch_icon(self.sketch_type, size=28).pixmap(28, 28))
        header.addWidget(lbl_icon)

        title_col = QVBoxLayout()
        lbl_title = QLabel("Kaynaklı / Bileşik Kesit Tanımlayıcı")
        lbl_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #FFFFFF;")
        lbl_sub = QLabel("ГОСТ 21.502 Form 1 kuralına göre her levhanın genişlik ve et kalınlığı (-b × t)")
        lbl_sub.setStyleSheet(f"font-size: 11px; color: {theme.TEXT_MUTED};")
        title_col.addWidget(lbl_title)
        title_col.addWidget(lbl_sub)
        header.addLayout(title_col)
        header.addStretch()
        layout.addLayout(header)

        # Mevcut girdiyi parçalara ayır
        raw_parts = [p.strip() for p in initial_comp.split(",") if p.strip()]

        # 2. Bileşen Kartları
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.BG_SURFACE};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(10)

        for idx, (pos_no, label_text, default_hint) in enumerate(self.parts_meta):
            row_box = QVBoxLayout()
            lbl = QLabel(label_text)
            lbl.setStyleSheet("font-size: 11px; font-weight: 600; color: #94A3B8;")
            row_box.addWidget(lbl)

            edit_row = QHBoxLayout()
            edit = QLineEdit()
            init_val = raw_parts[idx] if idx < len(raw_parts) else default_hint
            # Başta - yoksa ekle
            if init_val and not (init_val.startswith("-") or init_val.startswith("—")):
                init_val = f"-{init_val}"
            edit.setText(init_val)
            edit.setPlaceholderText(f"örn: {default_hint}")
            edit.setFixedHeight(30)
            edit.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {theme.BG_APP};
                    color: #FFFFFF;
                    border: 1px solid {theme.BORDER_LIGHT};
                    border-radius: 5px;
                    padding: 0 10px;
                    font-size: 12px;
                }}
                QLineEdit:focus {{
                    border-color: {theme.ACCENT_PRIMARY};
                }}
            """)
            edit.textChanged.connect(self._update_preview)
            edit_row.addWidget(edit, 1)

            # Hızlı Önayar Butonları
            presets = ["-130 x 12", "-160 x 14", "-200 x 16", "-300 x 14", "-500 x 10"]
            for pr in presets[:3]:
                btn_pr = QPushButton(pr)
                btn_pr.setFixedHeight(26)
                btn_pr.setCursor(Qt.CursorShape.PointingHandCursor)
                btn_pr.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {theme.BG_SURFACE_ACTIVE};
                        color: {theme.TEXT_SECONDARY};
                        border: 1px solid {theme.BORDER_SUBTLE};
                        border-radius: 4px;
                        padding: 0 6px;
                        font-size: 10px;
                    }}
                    QPushButton:hover {{
                        background-color: {theme.ACCENT_PRIMARY};
                        color: #FFFFFF;
                    }}
                """)
                btn_pr.clicked.connect(lambda _, val=pr, e=edit: e.setText(val))
                edit_row.addWidget(btn_pr)

            row_box.addLayout(edit_row)
            card_layout.addLayout(row_box)
            self.part_edits.append(edit)

        layout.addWidget(card)

        # 3. Canlı Önizleme Çubuğu
        self.lbl_preview = QLabel()
        self.lbl_preview.setStyleSheet(f"""
            background-color: {theme.BG_SIDEBAR};
            color: #38BDF8;
            border: 1px solid {theme.BORDER_SUBTLE};
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 12px;
            font-weight: 600;
        """)
        layout.addWidget(self.lbl_preview)
        self._update_preview()

        layout.addStretch()

        # 4. Butonlar
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_cancel = QPushButton("İptal")
        btn_cancel.setFixedHeight(32)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {theme.TEXT_MUTED};
                border: 1px solid {theme.BORDER_SUBTLE};
                border-radius: 6px;
                padding: 0 16px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                color: #FFFFFF;
                border-color: {theme.TEXT_SECONDARY};
            }}
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)

        btn_save = QPushButton("✓ Seç ve Tabloya Aktar")
        btn_save.setFixedHeight(32)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.ACCENT_PRIMARY};
                color: #FFFFFF;
                border: 1px solid {theme.ACCENT_PRIMARY};
                border-radius: 6px;
                padding: 0 20px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {theme.ACCENT_PRIMARY_HOVER};
            }}
        """)
        btn_save.clicked.connect(self._on_save)
        btn_row.addWidget(btn_save)

        layout.addLayout(btn_row)

    def _update_preview(self):
        parts = []
        for e in self.part_edits:
            t = e.text().strip()
            if t:
                if not (t.startswith("-") or t.startswith("—")):
                    t = f"-{t}"
                parts.append(t)
        self.result_composition = ", ".join(parts)
        self.lbl_preview.setText(f"📋 Tablo Sonucu: <b>{self.result_composition or '(Bileşen girilmedi)'}</b>")

    def _on_save(self):
        self._update_preview()
        self.accept()
