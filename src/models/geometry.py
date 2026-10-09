"""
2D Geometri ve Koordinat Yardımcıları.
CAD düzlemi (X sağa, Y yukarı) ve Tuval düzlemi (X sağa, Y aşağı) dönüşümleri.
"""
from dataclasses import dataclass
from typing import Tuple

@dataclass
class Point2D:
    x: float
    y: float

    def offset(self, dx: float, dy: float) -> "Point2D":
        return Point2D(self.x + dx, self.y + dy)

    def as_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)

@dataclass
class Rect2D:
    x: float      # Sol alt (CAD) veya Sol üst (Ekran)
    y: float
    width: float
    height: float

    @property
    def x_min(self) -> float:
        return self.x

    @property
    def x_max(self) -> float:
        return self.x + self.width

    @property
    def y_min(self) -> float:
        return self.y

    @property
    def y_max(self) -> float:
        return self.y + self.height

    @property
    def center_x(self) -> float:
        return self.x + self.width / 2.0

    @property
    def center_y(self) -> float:
        return self.y + self.height / 2.0

    def contains(self, pt: Point2D) -> bool:
        return self.x_min <= pt.x <= self.x_max and self.y_min <= pt.y <= self.y_max
