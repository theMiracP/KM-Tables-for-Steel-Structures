import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QClipboard

_CLIPBOARD_STORE = ""

@pytest.fixture(scope="session")
def qapp():
    """Tüm Qt testleri için oturum düzeyinde tekil QApplication örneği."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

@pytest.fixture(autouse=True)
def mock_clipboard_on_os_lock(monkeypatch):
    """
    Windows üzerinde test koşarken OS clipboard kilidi (ERROR_ACCESS_DENIED)
    durumunda QClipboard için güvenli bir bellek içi yedekleme sağlar.
    """
    global _CLIPBOARD_STORE
    _CLIPBOARD_STORE = ""
    orig_setText = QClipboard.setText
    orig_text = QClipboard.text

    def safe_setText(self, text, mode=QClipboard.Mode.Clipboard):
        global _CLIPBOARD_STORE
        _CLIPBOARD_STORE = text
        try:
            orig_setText(self, text, mode)
        except Exception:
            pass

    def safe_text(self, mode=QClipboard.Mode.Clipboard):
        try:
            val = orig_text(self, mode)
            if val:
                return val
        except Exception:
            pass
        return _CLIPBOARD_STORE

    monkeypatch.setattr(QClipboard, "setText", safe_setText)
    monkeypatch.setattr(QClipboard, "text", safe_text)
