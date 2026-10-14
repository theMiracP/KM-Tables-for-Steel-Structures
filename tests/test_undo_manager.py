"""
UndoManager birim testleri (Item 4.2).
"""
import pytest
from PySide6.QtWidgets import QApplication
from src.services.undo_manager import UndoManager


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_undo_manager_basic_push_and_undo(qapp):
    manager = UndoManager()
    assert not manager.can_undo()
    assert not manager.can_redo()

    applied_states = []

    def apply_fn(module_id: str, state: dict):
        applied_states.append((module_id, state))

    state_0 = {"count": 0}
    state_1 = {"count": 1}

    manager.push_snapshot("Increment to 1", "test_mod", state_0, state_1, apply_fn)
    assert manager.can_undo()
    assert not manager.can_redo()

    # Undo yap -> state_0 uygulanmalı
    manager.undo()
    assert len(applied_states) == 1
    assert applied_states[-1] == ("test_mod", {"count": 0})
    assert not manager.can_undo()
    assert manager.can_redo()

    # Redo yap -> state_1 uygulanmalı
    manager.redo()
    assert len(applied_states) == 2
    assert applied_states[-1] == ("test_mod", {"count": 1})
    assert manager.can_undo()
    assert not manager.can_redo()


def test_undo_manager_clear(qapp):
    manager = UndoManager()
    state_0 = {"val": "a"}
    state_1 = {"val": "b"}

    manager.push_snapshot("Change to b", "mod_a", state_0, state_1, lambda m, s: None)
    assert manager.can_undo()
    manager.clear()
    assert not manager.can_undo()
    assert not manager.can_redo()
