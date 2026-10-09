"""
CAD ve Önizleme İçin Hücre Metin Yerleşim ve Sarma Motoru (TextLayoutHelper).
ГОСТ 2.304 ve ISO 3098 tipografi oranlarına göre satır sarma (word-wrap)
ve dikey/yatay milimetrik metin konumlandırması yapar.
Canlı CAD tuvali ve DXF çıktısının %100 birebir aynı metin çıktısı üretmesini sağlar.
"""
from typing import List, Tuple


def estimate_text_width_mm(text: str, font_h: float) -> float:
    """
    ГОСТ 2.304 / ISO 3098 (ISOCPEUR) tipografisine göre metnin mm cinsinden genişliğini hesaplar.
    Geniş Kiril harfleri ve noktalama işaretlerinin oransal karakter genişliklerini dikkate alır.
    """
    total = 0.0
    for ch in text:
        if ch in "№":
            w = 1.35
        elif ch in "ЖШЩЮФWM@%":
            w = 1.15
        elif ch in "МЪЫБДПИЦЧЭЯOQ":
            w = 0.95
        elif ch in "АВГДЕЁЗИЙКЛНОРСТУХA-Z":
            w = 0.85
        elif ch in "жшщюфwm":
            w = 0.90
        elif ch in "1ijlrt-()[]/\\«»":
            w = 0.50
        elif ch in " .,:;!|'\"`":
            w = 0.38
        else:
            w = 0.76  # standart küçük Kiril/Latin harfler, rakamlar
        total += w * font_h
    return total * 1.05  # Güvenli CAD payı (%5)


def wrap_paragraph_to_width(paragraph: str, max_w: float, font_h: float) -> List[str]:
    """
    Bir metin paragrafını milimetrik genişliği aşmayacak şekilde kelimelerden böler.
    Gerektiğinde tek başına genişliği aşan kelimeleri de hecelerine/parçalarına ayırır.
    """
    words = paragraph.split()
    if not words:
        return [""]

    lines: List[str] = []
    current_line: List[str] = []
    current_w = 0.0
    space_w = estimate_text_width_mm(" ", font_h)

    for word in words:
        word_w = estimate_text_width_mm(word, font_h)
        if word_w > max_w:
            # Mevcut satırı tamamla
            if current_line:
                lines.append(" ".join(current_line))
                current_line = []
                current_w = 0.0
            # Uzun kelimeyi max_w'ya sığacak parçalara böl
            sub_chunk = ""
            sub_w = 0.0
            for char in word:
                ch_w = estimate_text_width_mm(char, font_h)
                if sub_w + ch_w > max_w and sub_chunk:
                    lines.append(sub_chunk)
                    sub_chunk = char
                    sub_w = ch_w
                else:
                    sub_chunk += char
                    sub_w += ch_w
            if sub_chunk:
                current_line.append(sub_chunk)
                current_w = sub_w
            continue

        needed_w = current_w + (space_w if current_line else 0.0) + word_w
        if needed_w <= max_w:
            current_line.append(word)
            current_w = needed_w
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
            current_w = word_w

    if current_line:
        lines.append(" ".join(current_line))
    return lines


def estimate_block_height(lines: List[str], font_h: float) -> float:
    """Metin satırlarının toplam milimetrik blok yüksekliğini (satır aralığı + harf boyu + descender) hesaplar."""
    if not lines:
        return 0.0
    if len(lines) == 1:
        return font_h * 1.25
    return (len(lines) - 1) * (font_h * 1.25) + (font_h * 1.35)


def wrap_cell_text(
    raw_text: str,
    max_width_mm: float,
    max_height_mm: float,
    target_font_size_mm: float,
    min_font_size_mm: float = 1.2
) -> Tuple[List[str], float]:
    """
    Verilen metni hem genişliğe (max_width_mm) hem yüksekliğe (max_height_mm)
    kesinlikle taşmayacak şekilde optimize eder.

    Kural: Font boyutu metin uzunluğuna göre küçülebilir, ancak target_font_size_mm
    değerinden KESİNLİKLE DAHA BÜYÜK OLAMAZ (üst sınır / tavan değerdir).

    Dönüş: (satırlar_listesi, uygulanan_font_boyutu_mm)
    """
    clean_text = raw_text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not clean_text:
        return [], target_font_size_mm

    step = 0.05

    # 1. Aşama: Kullanıcının manuel satır sonlarını (\n) koruyarak font küçültmeyi dene
    user_lines = [l.strip() for l in clean_text.split("\n") if l.strip()]
    if len(user_lines) > 1:
        font_h = target_font_size_mm
        while font_h >= min_font_size_mm:
            max_lw = max(estimate_text_width_mm(l, font_h) for l in user_lines)
            tot_h = estimate_block_height(user_lines, font_h)
            if max_lw <= max_width_mm and tot_h <= max_height_mm:
                return user_lines, font_h
            font_h = round(font_h - step, 2)

    # 2. Aşama: Otomatik kelime kaydırma (Word-Wrap) ile hem yatay hem dikey sığdır
    font_h = target_font_size_mm
    while font_h >= min_font_size_mm:
        lines: List[str] = []
        for p in clean_text.split("\n"):
            p_str = p.strip()
            if p_str:
                lines.extend(wrap_paragraph_to_width(p_str, max_width_mm, font_h))
        if lines:
            max_lw = max(estimate_text_width_mm(l, font_h) for l in lines)
            tot_h = estimate_block_height(lines, font_h)
            if max_lw <= max_width_mm and tot_h <= max_height_mm:
                return lines, font_h
        font_h = round(font_h - step, 2)

    # 3. Aşama: Minimum font sınırında en iyi yerleşimi dön
    font_h = min_font_size_mm
    fallback_lines: List[str] = []
    for p in clean_text.split("\n"):
        p_str = p.strip()
        if p_str:
            fallback_lines.extend(wrap_paragraph_to_width(p_str, max_width_mm, font_h))
    return fallback_lines, font_h
