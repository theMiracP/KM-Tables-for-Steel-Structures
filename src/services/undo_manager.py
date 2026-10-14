"""
KM Studio - Undo / Redo Altyapısı (QUndoStack tabanlı).
Tablo hücreleri, satır ekleme/silme ve doküman değişikliklerini snapshot bazlı
geri (Ctrl+Z) ve ileri (Ctrl+Y / Ctrl+Shift+Z) alma yöneticisi.
"""
import copy
from typing import Any, Callable, Optional
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QUndoStack, QUndoCommand


class DocumentSnapshotCommand(QUndoCommand):
    """
    Belirli bir modül dokümanındaki durum değişimini saklayan QUndoCommand.
    """
    def __init__(
        self,
        description: str,
        module_id: str,
        old_state: Any,
        new_state: Any,
        apply_fn: Callable[[str, Any], None]
    ):
        super().__init__(description)
        self.module_id = module_id
        self.old_state = copy.deepcopy(old_state)
        self.new_state = copy.deepcopy(new_state)
        self.apply_fn = apply_fn
        self._initial_call = True

    def undo(self):
        self.apply_fn(self.module_id, copy.deepcopy(self.old_state))

    def redo(self):
        if self._initial_call:
            # Command stack'e ilk eklendiğinde durum zaten günceldir
            self._initial_call = False
            return
        self.apply_fn(self.module_id, copy.deepcopy(self.new_state))


class UndoManager(QObject):
    """
    Uygulama genelinde veya modül bazında çalışan QUndoStack yöneticisi.
    """
    can_undo_changed = Signal(bool)
    can_redo_changed = Signal(bool)
    undo_text_changed = Signal(str)
    redo_text_changed = Signal(str)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._stack = QUndoStack(self)
        self._is_applying = False

        self._stack.canUndoChanged.connect(self.can_undo_changed)
        self._stack.canRedoChanged.connect(self.can_redo_changed)
        self._stack.undoTextChanged.connect(self.undo_text_changed)
        self._stack.redoTextChanged.connect(self.redo_text_changed)

    @property
    def is_applying(self) -> bool:
        """Undo veya Redo işlemi icra edilirken yeni snapshot pushlanmasını engeller."""
        return self._is_applying

    def can_undo(self) -> bool:
        try:
            return self._stack.canUndo()
        except RuntimeError:
            return False

    def can_redo(self) -> bool:
        try:
            return self._stack.canRedo()
        except RuntimeError:
            return False

    def push_snapshot(
        self,
        description: str,
        module_id: str,
        old_state: Any,
        new_state: Any,
        apply_fn: Callable[[str, Any], None]
    ) -> None:
        """Yeni bir doküman durum değişimini yığına kaydeder."""
        if self._is_applying:
            return
        cmd = DocumentSnapshotCommand(
            description=description,
            module_id=module_id,
            old_state=old_state,
            new_state=new_state,
            apply_fn=self._wrap_apply(apply_fn)
        )
        self._stack.push(cmd)

    def _wrap_apply(self, apply_fn: Callable[[str, Any], None]) -> Callable[[str, Any], None]:
        def wrapper(module_id: str, state: Any):
            self._is_applying = True
            try:
                apply_fn(module_id, state)
            finally:
                self._is_applying = False
        return wrapper

    def undo(self) -> None:
        if self._stack.canUndo():
            self._stack.undo()

    def redo(self) -> None:
        if self._stack.canRedo():
            self._stack.redo()

    def clear(self) -> None:
        self._stack.clear()
