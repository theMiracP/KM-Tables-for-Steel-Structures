"""
KM Tablo Oluşturucu - Linear / Notion SaaS Dashboard Mimarisi (UI v2).
Modern, minimalist, yüksek kontrastlı ve mühendislik odaklı SaaS arayüzü.
"""

def __getattr__(name: str):
    if name == "KmLinearMainWindow":
        from src.ui_v2.window import KmLinearMainWindow
        return KmLinearMainWindow
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ["KmLinearMainWindow"]
