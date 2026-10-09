"""
Profil ve Kesit Eskiz Modelleri (Сечение -> Эскиз).
Referans tablodaki profil sembollerini, kaynaklı kutu ve çok parçalı kompleks profil eskizlerini tanımlar.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple

class SketchType(str, Enum):
    NONE = "none"
    I_BEAM = "i_beam"                           # Haddelenmiş Dвутавр (I)
    WELDED_I_BEAM = "welded_i_beam"             # Kaynaklı I-Kiriş (1-2)
    WELDED_I_PACKAGE = "welded_i_package"       # Kaynaklı Paket Flanşlı I-Kiriş (1-2-3)
    WELDED_CRUCIFORM = "welded_cruciform"       # Kaynaklı Haç / Kolon (1-2-3)
    WELDED_T = "welded_t"                       # Kaynaklı T-Profil / Тавр (1-2)
    COMPOUND_BOX_WELDED = "compound_box_welded" # Kaynaklı Kutu (1-2)
    CHECKERED_PLATE = "checkered_plate"         # Baklavalı / Tırtıklı Sac (Рифленая сталь)
    RECT_TUBE = "rect_tube"                     # Kutu Profil (□)
    ROUND_TUBE = "round_tube"                   # Dairesel Boru (○)
    PLATE = "plate"                             # Levha / Lama (-)
    CHANNEL = "channel"                         # Şveller ([)
    ANGLE = "angle"                             # Köşebent (L)
    CUSTOM_TEXT = "custom_text"                 # Özel sembol / metin
    LOGO_EMBLEM = "logo_emblem"                 # Form 3 Kurumsal logo amblemi

@dataclass
class SketchPrimitive:
    """Eskiz içindeki temel çizgi, kutu, daire veya выноска (leader) metni primitifi."""
    kind: str  # "line", "rect", "circle", "leader_text"
    coords: Tuple[float, ...]  # line: (x1, y1, x2, y2), rect: (x, y, w, h), circle: (cx, cy, r)
    text: Optional[str] = None # leader_text için

@dataclass
class SectionSketch:
    sketch_type: SketchType = SketchType.NONE
    symbol_text: str = ""           # Basit sembol metni (örn: "I", "□", "○", "∅")
    callout_1: Optional[str] = None # Kaynak / parça pozisyon etiketi 1
    callout_2: Optional[str] = None # Kaynak / parça pozisyon etiketi 2
    callout_3: Optional[str] = None # Kaynak / parça pozisyon etiketi 3
    image_path: Optional[str] = None # Kurumsal logo vb. görsel dosya yolu

    def generate_primitives(self, box_x: float, box_y: float, box_w: float, box_h: float) -> List[SketchPrimitive]:
        """
        Belirtilen hücre sınırları içinde orantılı vektörel çizim elemanları üretir.
        box_y: CAD koordinatında alt kenardır.
        """
        prims: List[SketchPrimitive] = []
        cx = box_x + box_w / 2.0
        cy = box_y + box_h / 2.0
        size = min(box_w, box_h) * 0.55
        half = size / 2.0

        if self.sketch_type == SketchType.I_BEAM:
            # Standart / Haddelenmiş I-profil çizgileri
            flange_w = size * 0.75
            prims.append(SketchPrimitive("line", (cx - flange_w/2, cy + half, cx + flange_w/2, cy + half)))
            prims.append(SketchPrimitive("line", (cx - flange_w/2, cy - half, cx + flange_w/2, cy - half)))
            prims.append(SketchPrimitive("line", (cx, cy - half, cx, cy + half)))

        elif self.sketch_type == SketchType.WELDED_I_BEAM:
            # 1-2 Kaynaklı I-Kiriş (Görsel 3: Сварной двутавр из 3 листов)
            flange_w = size * 0.65
            ft = 1.0  # Flanş plaka kalınlığı
            # Üst ve alt flanş kutucukları (levhaları)
            prims.append(SketchPrimitive("rect", (cx - flange_w/2, cy + half - ft, flange_w, ft)))
            prims.append(SketchPrimitive("rect", (cx - flange_w/2, cy - half, flange_w, ft)))
            # Dikey gövde çizgisi (стенка)
            prims.append(SketchPrimitive("line", (cx, cy - half + ft, cx, cy + half - ft)))

            # Sol выноска 1 (Gövdeyi gösterir)
            p1_start = (cx, cy - 0.5)
            p1_mid = (cx - 4.5, cy - 3.0)
            p1_shelf = (cx - 7.5, cy - 3.0)
            prims.append(SketchPrimitive("line", (p1_start[0], p1_start[1], p1_mid[0], p1_mid[1])))
            prims.append(SketchPrimitive("line", (p1_mid[0], p1_mid[1], p1_shelf[0], p1_shelf[1])))
            prims.append(SketchPrimitive("leader_text", (p1_shelf[0] + 0.5, p1_shelf[1] + 0.5, 0, 0), text=self.callout_1 or "1"))

            # Sağ выноска 2 (Üst ve alt flanşlara dallanır)
            p2_top = (cx + flange_w/2, cy + half - ft/2)
            p2_bot = (cx + flange_w/2, cy - half + ft/2)
            p2_mid = (cx + flange_w/2 + 4.0, cy)
            p2_shelf = (cx + flange_w/2 + 7.5, cy)
            prims.append(SketchPrimitive("line", (p2_top[0], p2_top[1], p2_mid[0], p2_mid[1])))
            prims.append(SketchPrimitive("line", (p2_bot[0], p2_bot[1], p2_mid[0], p2_mid[1])))
            prims.append(SketchPrimitive("line", (p2_mid[0], p2_mid[1], p2_shelf[0], p2_shelf[1])))
            prims.append(SketchPrimitive("leader_text", (p2_mid[0] + 1.0, p2_mid[1] + 0.5, 0, 0), text=self.callout_2 or "2"))

        elif self.sketch_type == SketchType.WELDED_I_PACKAGE:
            # 1-2-3 Kaynaklı Paket Flanşlı I-Kiriş (Görsel 1: Двутавр с пакетом полок)
            flange_w = size * 0.70
            gap = 1.2  # Paket levhaları arası mesafe
            # Üst flanş 2 kat levha çizgileri
            prims.append(SketchPrimitive("line", (cx - flange_w/2, cy + half, cx + flange_w/2, cy + half)))
            prims.append(SketchPrimitive("line", (cx - flange_w/2, cy + half - gap, cx + flange_w/2, cy + half - gap)))
            # Alt flanş 2 kat levha çizgileri
            prims.append(SketchPrimitive("line", (cx - flange_w/2, cy - half, cx + flange_w/2, cy - half)))
            prims.append(SketchPrimitive("line", (cx - flange_w/2, cy - half + gap, cx + flange_w/2, cy - half + gap)))
            # Dikey gövde çizgisi
            prims.append(SketchPrimitive("line", (cx, cy - half + gap, cx, cy + half - gap)))

            # Sol выноска 1 (Dikey gövde)
            p1_start = (cx, cy - 1.0)
            p1_mid = (cx - 4.0, cy - 4.0)
            p1_shelf = (cx - 7.0, cy - 4.0)
            prims.append(SketchPrimitive("line", (p1_start[0], p1_start[1], p1_mid[0], p1_mid[1])))
            prims.append(SketchPrimitive("line", (p1_mid[0], p1_mid[1], p1_shelf[0], p1_shelf[1])))
            prims.append(SketchPrimitive("leader_text", (p1_shelf[0] + 0.5, p1_shelf[1] + 0.5, 0, 0), text=self.callout_1 or "1"))

            # Dış flanşlar выноска 2 (Üst ve alt dış levhalar)
            # Üst dış levhadan выноска 2
            p2_top_start = (cx + 1.5, cy + half)
            p2_top_mid = (cx + 4.5, cy + half + 2.5)
            p2_top_shelf = (cx + 7.5, cy + half + 2.5)
            prims.append(SketchPrimitive("line", (p2_top_start[0], p2_top_start[1], p2_top_mid[0], p2_top_mid[1])))
            prims.append(SketchPrimitive("line", (p2_top_mid[0], p2_top_mid[1], p2_top_shelf[0], p2_top_shelf[1])))
            prims.append(SketchPrimitive("leader_text", (p2_top_mid[0] + 0.5, p2_top_mid[1] + 0.5, 0, 0), text=self.callout_2 or "2"))

            # Alt dış levhadan выноска 2
            p2_bot_start = (cx + 1.5, cy - half)
            p2_bot_mid = (cx + 4.5, cy - half - 2.5)
            p2_bot_shelf = (cx + 7.5, cy - half - 2.5)
            prims.append(SketchPrimitive("line", (p2_bot_start[0], p2_bot_start[1], p2_bot_mid[0], p2_bot_mid[1])))
            prims.append(SketchPrimitive("line", (p2_bot_mid[0], p2_bot_mid[1], p2_bot_shelf[0], p2_bot_shelf[1])))
            prims.append(SketchPrimitive("leader_text", (p2_bot_mid[0] + 0.5, p2_bot_mid[1] + 0.5, 0, 0), text=self.callout_2 or "2"))

            # İç flanşlar выноска 3 (Üst ve alt iç levhalar merkeze birleşir)
            p3_top = (cx + flange_w/4, cy + half - gap)
            p3_bot = (cx + flange_w/4, cy - half + gap)
            p3_mid = (cx + flange_w/2 + 2.5, cy)
            p3_shelf = (cx + flange_w/2 + 6.0, cy)
            prims.append(SketchPrimitive("line", (p3_top[0], p3_top[1], p3_mid[0], p3_mid[1])))
            prims.append(SketchPrimitive("line", (p3_bot[0], p3_bot[1], p3_mid[0], p3_mid[1])))
            prims.append(SketchPrimitive("line", (p3_mid[0], p3_mid[1], p3_shelf[0], p3_shelf[1])))
            prims.append(SketchPrimitive("leader_text", (p3_mid[0] + 0.8, p3_mid[1] + 0.5, 0, 0), text=self.callout_3 or "3"))

        elif self.sketch_type == SketchType.WELDED_CRUCIFORM:
            # 1-2-3 Kaynaklı Haç / Kolon (Görsel 2: Сварное крестовое сечение)
            vh = size * 0.85
            hw = size * 0.85
            flange_len = 5.0
            # Ana dikey gövde (стенка)
            prims.append(SketchPrimitive("line", (cx, cy - vh/2, cx, cy + vh/2)))
            # Üst ve alt yatay flanşlar
            prims.append(SketchPrimitive("line", (cx - flange_len/2, cy + vh/2, cx + flange_len/2, cy + vh/2)))
            prims.append(SketchPrimitive("line", (cx - flange_len/2, cy - vh/2, cx + flange_len/2, cy - vh/2)))
            # Sol ve sağ yatay gövde parçaları
            prims.append(SketchPrimitive("line", (cx - hw/2, cy, cx, cy)))
            prims.append(SketchPrimitive("line", (cx, cy, cx + hw/2, cy)))
            # Sol ve sağ dikey flanşlar
            prims.append(SketchPrimitive("line", (cx - hw/2, cy - flange_len/2, cx - hw/2, cy + flange_len/2)))
            prims.append(SketchPrimitive("line", (cx + hw/2, cy - flange_len/2, cx + hw/2, cy + flange_len/2)))

            # Sol üst выноска 1 (Dikey ana gövdeyi gösterir)
            p1_start = (cx, cy + 2.0)
            p1_mid = (cx - 4.5, cy + 5.0)
            p1_shelf = (cx - 7.5, cy + 5.0)
            prims.append(SketchPrimitive("line", (p1_start[0], p1_start[1], p1_mid[0], p1_mid[1])))
            prims.append(SketchPrimitive("line", (p1_mid[0], p1_mid[1], p1_shelf[0], p1_shelf[1])))
            prims.append(SketchPrimitive("leader_text", (p1_shelf[0] + 0.5, p1_shelf[1] + 0.5, 0, 0), text=self.callout_1 or "1"))

            # Sağ üst выноска 2 (Üst yatay ve sağ dikey flanşları gösterir)
            p2_top = (cx + 1.0, cy + vh/2)
            p2_right = (cx + hw/2, cy + 1.5)
            p2_mid = (cx + hw/2 + 2.5, cy + vh/2 + 1.5)
            p2_shelf = (cx + hw/2 + 5.5, cy + vh/2 + 1.5)
            prims.append(SketchPrimitive("line", (p2_top[0], p2_top[1], p2_mid[0], p2_mid[1])))
            prims.append(SketchPrimitive("line", (p2_right[0], p2_right[1], p2_mid[0], p2_mid[1])))
            prims.append(SketchPrimitive("line", (p2_mid[0], p2_mid[1], p2_shelf[0], p2_shelf[1])))
            prims.append(SketchPrimitive("leader_text", (p2_mid[0] + 0.5, p2_mid[1] + 0.5, 0, 0), text=self.callout_2 or "2"))

            # Sol alt выноска 2 (Alt yatay ve sol dikey flanşları gösterir)
            p2_bot = (cx - 1.0, cy - vh/2)
            p2_left = (cx - hw/2, cy - 1.5)
            p2_bmid = (cx - hw/2 - 2.5, cy - vh/2 - 1.5)
            p2_bshelf = (cx - hw/2 - 5.5, cy - vh/2 - 1.5)
            prims.append(SketchPrimitive("line", (p2_bot[0], p2_bot[1], p2_bmid[0], p2_bmid[1])))
            prims.append(SketchPrimitive("line", (p2_left[0], p2_left[1], p2_bmid[0], p2_bmid[1])))
            prims.append(SketchPrimitive("line", (p2_bmid[0], p2_bmid[1], p2_bshelf[0], p2_bshelf[1])))
            prims.append(SketchPrimitive("leader_text", (p2_bshelf[0] + 0.5, p2_bshelf[1] + 0.5, 0, 0), text=self.callout_2 or "2"))

            # Sağ alt выноска 3 (Sol ve sağ yatay gövde parçalarını gösterir)
            p3_l = (cx - hw/4, cy)
            p3_r = (cx + hw/4, cy)
            p3_mid = (cx + hw/2 + 2.5, cy - vh/2 - 1.5)
            p3_shelf = (cx + hw/2 + 5.5, cy - vh/2 - 1.5)
            prims.append(SketchPrimitive("line", (p3_l[0], p3_l[1], p3_mid[0], p3_mid[1])))
            prims.append(SketchPrimitive("line", (p3_r[0], p3_r[1], p3_mid[0], p3_mid[1])))
            prims.append(SketchPrimitive("line", (p3_mid[0], p3_mid[1], p3_shelf[0], p3_shelf[1])))
            prims.append(SketchPrimitive("leader_text", (p3_mid[0] + 0.5, p3_mid[1] + 0.5, 0, 0), text=self.callout_3 or "3"))

        elif self.sketch_type == SketchType.RECT_TUBE:
            # Kutu profil (□)
            prims.append(SketchPrimitive("rect", (cx - half, cy - half, size, size)))

        elif self.sketch_type == SketchType.ROUND_TUBE:
            # Dairesel boru (○)
            prims.append(SketchPrimitive("circle", (cx, cy, half)))

        elif self.sketch_type == SketchType.PLATE:
            # Levha / полоса (-)
            prims.append(SketchPrimitive("line", (cx - half, cy, cx + half, cy)))

        elif self.sketch_type == SketchType.COMPOUND_BOX_WELDED:
            # 2 levhalı kutu ve выноски (1 ve 2 etiketli kaynak bayrakları)
            rw = size * 0.8
            rh = size * 0.8
            rx = cx - rw/2
            ry = cy - rh/2
            prims.append(SketchPrimitive("rect", (rx, ry, rw, rh)))
            # Sol alt выноска 1
            p1_start = (rx, ry)
            p1_mid = (rx - 4.0, ry - 3.0)
            p1_shelf = (rx - 7.0, ry - 3.0)
            prims.append(SketchPrimitive("line", (p1_start[0], p1_start[1], p1_mid[0], p1_mid[1])))
            prims.append(SketchPrimitive("line", (p1_mid[0], p1_mid[1], p1_shelf[0], p1_shelf[1])))
            prims.append(SketchPrimitive("leader_text", (p1_shelf[0] + 0.5, p1_shelf[1] + 0.5, 0, 0), text=self.callout_1 or "1"))
            # Sağ üst выноска 2
            p2_start = (rx + rw, ry + rh)
            p2_mid = (rx + rw + 3.0, ry + rh + 3.0)
            p2_shelf = (rx + rw + 6.0, ry + rh + 3.0)
            prims.append(SketchPrimitive("line", (p2_start[0], p2_start[1], p2_mid[0], p2_mid[1])))
            prims.append(SketchPrimitive("line", (p2_mid[0], p2_mid[1], p2_shelf[0], p2_shelf[1])))
            prims.append(SketchPrimitive("leader_text", (p2_mid[0] + 0.5, p2_mid[1] + 0.5, 0, 0), text=self.callout_2 or "2"))

        elif self.sketch_type == SketchType.WELDED_T:
            # 1-2 Kaynaklı T-Profil / Тавр (Görsel 1: media_1791175670024.png)
            flange_w = size * 0.75
            web_h = size * 0.70
            base_y = cy - half * 0.4
            # Alt yatay flanş çizgisi (Полка)
            prims.append(SketchPrimitive("line", (cx - flange_w/2, base_y, cx + flange_w/2, base_y)))
            # Dikey gövde çizgisi (Стенка)
            prims.append(SketchPrimitive("line", (cx, base_y, cx, base_y + web_h)))

            # Sol выноска 1 (Alt flanş levhasını gösterir)
            p1_start = (cx - flange_w/4, base_y)
            p1_mid = (cx - flange_w/2 - 3.0, base_y - 3.0)
            p1_shelf = (cx - flange_w/2 - 6.5, base_y - 3.0)
            prims.append(SketchPrimitive("line", (p1_start[0], p1_start[1], p1_mid[0], p1_mid[1])))
            prims.append(SketchPrimitive("line", (p1_mid[0], p1_mid[1], p1_shelf[0], p1_shelf[1])))
            prims.append(SketchPrimitive("leader_text", (p1_shelf[0] + 0.5, p1_shelf[1] + 0.5, 0, 0), text=self.callout_1 or "1"))

            # Sağ выноска 2 (Dikey gövdeyi gösterir)
            p2_start = (cx, base_y + web_h * 0.5)
            p2_mid = (cx + 4.5, base_y + web_h * 0.5 + 2.5)
            p2_shelf = (cx + 7.5, base_y + web_h * 0.5 + 2.5)
            prims.append(SketchPrimitive("line", (p2_start[0], p2_start[1], p2_mid[0], p2_mid[1])))
            prims.append(SketchPrimitive("line", (p2_mid[0], p2_mid[1], p2_shelf[0], p2_shelf[1])))
            prims.append(SketchPrimitive("leader_text", (p2_shelf[0] - 2.5, p2_shelf[1] + 0.5, 0, 0), text=self.callout_2 or "2"))

        elif self.sketch_type == SketchType.ANGLE:
            # L Köşebent (Görsel 2: media_1791175810162.png)
            aw = size * 0.65
            ah = size * 0.75
            prims.append(SketchPrimitive("line", (cx - aw/2, cy + ah/2, cx - aw/2, cy - ah/2)))
            prims.append(SketchPrimitive("line", (cx - aw/2, cy - ah/2, cx + aw/2, cy - ah/2)))

        elif self.sketch_type == SketchType.CHANNEL:
            # [ Şveller (Görsel 4: media_1791175945929.png)
            cw = size * 0.55
            ch = size * 0.75
            prims.append(SketchPrimitive("line", (cx + cw/2, cy + ch/2, cx - cw/2, cy + ch/2)))
            prims.append(SketchPrimitive("line", (cx - cw/2, cy - ch/2, cx - cw/2, cy + ch/2)))
            prims.append(SketchPrimitive("line", (cx - cw/2, cy - ch/2, cx + cw/2, cy - ch/2)))

        elif self.sketch_type == SketchType.CHECKERED_PLATE:
            # Baklavalı / Tırtıklı Sac (Görsel 3: media_1791175883680.png - Рифление)
            gw = size * 0.55
            # Çapraz baklava deseni
            for d in [-gw/3, 0, gw/3]:
                prims.append(SketchPrimitive("line", (cx - gw/2, cy - gw/2 + d, cx + gw/2, cy + gw/2 + d)))
                prims.append(SketchPrimitive("line", (cx - gw/2, cy + gw/2 + d, cx + gw/2, cy - gw/2 + d)))

        elif self.sketch_type == SketchType.LOGO_EMBLEM:
            # ГОСТ Form 3 Kurumsal dinamik logo amblemi (Kırmızı/Stilize S-kanadı)
            lx = box_x + 3.0
            ly = box_y + 2.0
            lh = box_h - 4.0
            lw = 8.0
            # İki parçalı stilize kanat/şerit geometrisi
            prims.append(SketchPrimitive("line", (lx, ly + lh * 0.9, lx + lw, ly + lh * 0.5)))
            prims.append(SketchPrimitive("line", (lx + lw, ly + lh * 0.5, lx + 2.0, ly + lh * 0.5)))
            prims.append(SketchPrimitive("line", (lx + 2.0, ly + lh * 0.5, lx + lw, ly + lh * 0.1)))
            prims.append(SketchPrimitive("line", (lx + lw, ly + lh * 0.1, lx, ly + lh * 0.45)))
            prims.append(SketchPrimitive("line", (lx, ly + lh * 0.45, lx + 3.0, ly + lh * 0.45)))
            prims.append(SketchPrimitive("line", (lx + 3.0, ly + lh * 0.45, lx, ly + lh * 0.9)))

        return prims
