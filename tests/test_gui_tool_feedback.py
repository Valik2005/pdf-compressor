"""Regression tests for PDF-tools completion feedback and keyboard focus.

Run with PySide6 installed; offscreen mode also works on headless CI.
The PDF engine is not invoked by these UI-only tests.
"""
import importlib.util
import os
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")
pytest.importorskip("pymupdf")
from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="module")
def gui_module():
    source = Path(__file__).resolve().parents[1] / "app.pyw"
    loader = SourceFileLoader("pdf_compressor_gui_feedback_test", str(source))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def qt_app():
    return QApplication.instance() or QApplication([])


@pytest.fixture()
def window(gui_module, qt_app, monkeypatch, tmp_path):
    # Do not read or modify the developer's actual application settings.
    monkeypatch.setattr(
        gui_module, "QSettings",
        lambda *_args: QSettings(str(tmp_path / "test-settings.ini"), QSettings.IniFormat),
    )
    win = gui_module.MainWindow()
    win.show()
    # These tests exercise the PDF tools tab; widgets on an inactive tab
    # are not visible even when their own show() method has been called.
    win.tabs.setCurrentWidget(win.tools_page)
    qt_app.processEvents()
    yield win
    win.close()
    qt_app.processEvents()


def feedback(window, action, outputs=(), errors=(), message="Готово. Успешно: 1. Ошибок: 0."):
    window._tool_feedback_state = {
        "action": action, "message": message,
        "outputs": [str(path) for path in outputs],
        "errors": list(errors),
    }
    window.render_tool_feedback()


@pytest.mark.parametrize(
    ("action", "expected"),
    [
        ("merge", "PDF успешно объединены"),
        ("split", "Страницы успешно извлечены"),
        ("rotate", "PDF успешно повёрнут"),
    ],
)
def test_success_confirmation_for_each_tool(window, tmp_path, action, expected):
    result = tmp_path / "result.pdf"
    feedback(window, action, outputs=[result])
    assert window.tool_result_card.isVisible()
    assert window.tool_result_title.text() == expected
    assert str(result) in window.tool_result_detail.text()
    assert window.open_tool_folder_btn.isVisible()


def test_multiple_extracted_pages_show_count_and_folder(window, tmp_path):
    files = [tmp_path / f"page_{n}.pdf" for n in (1, 2, 3)]
    feedback(window, "split", outputs=files)
    assert "Создано файлов: 3" in window.tool_result_detail.text()
    assert str(tmp_path) in window.tool_result_detail.text()
    assert window.open_tool_folder_btn.isVisible()


@pytest.mark.parametrize(
    ("message", "errors", "expected"),
    [
        ("Готово. Успешно: 0. Ошибок: 1.", ["Неверный диапазон страниц"], "Ошибка операции"),
        ("Операция отменена. Успешно завершено: 0.", [], "Операция отменена"),
    ],
)
def test_no_false_success_on_error_or_cancel(window, message, errors, expected):
    feedback(window, "split", errors=errors, message=message)
    assert window.tool_result_title.text() == expected
    assert not window.open_tool_folder_btn.isVisible()


def test_open_folder_only_when_requested(window, gui_module, tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(gui_module, "open_file", lambda path: calls.append(path))
    feedback(window, "merge", outputs=[tmp_path / "merged.pdf"])
    assert calls == []  # No automatic Explorer launch.
    window.open_tool_result_folder()
    assert calls == [str(tmp_path)]


def test_feedback_retranslates_on_language_switch(window, tmp_path):
    feedback(window, "merge", outputs=[tmp_path / "merged.pdf"])
    window.language_box.setCurrentIndex(1)
    assert window.tool_result_title.text() == "PDFs merged successfully"
    assert window.open_tool_folder_btn.text() == "Open folder"
    assert "File created:" in window.tool_result_detail.text()


def test_finishing_tool_restores_originating_button_focus(window, qt_app, tmp_path):
    window.tabs.setCurrentWidget(window.tools_page)
    window.merge_btn.setFocus(Qt.OtherFocusReason)
    qt_app.processEvents()
    if QApplication.focusWidget() is not window.merge_btn:
        pytest.skip("The current Qt platform does not support keyboard focus.")

    window._active_action = "merge"
    window._tool_focus_button = window.merge_btn
    window._tool_outputs = [str(tmp_path / "merged.pdf")]
    window._tool_errors = []
    window.pending_end_message = "Готово. Успешно: 1. Ошибок: 0."
    window.busy = True
    window.merge_btn.setEnabled(False)
    window.split_btn.setFocus(Qt.OtherFocusReason)
    window.finalize_thread()
    qt_app.processEvents()

    assert QApplication.focusWidget() is window.merge_btn
    assert window.merge_btn.focusPolicy() != Qt.NoFocus  # Tab still works.
    assert window.tool_result_title.text() == "PDF успешно объединены"


def test_finishing_tool_does_not_steal_focus_from_edited_field(window, qt_app, tmp_path):
    window.tabs.setCurrentWidget(window.tools_page)
    window.split_pages.setFocus(Qt.OtherFocusReason)
    qt_app.processEvents()
    if QApplication.focusWidget() is not window.split_pages:
        pytest.skip("The current Qt platform does not support keyboard focus.")

    window._active_action = "split"
    window._tool_focus_button = window.split_btn
    window._tool_outputs = [str(tmp_path / "page.pdf")]
    window._tool_errors = []
    window.pending_end_message = "Готово. Успешно: 1. Ошибок: 0."
    window.busy = True
    window.finalize_thread()
    qt_app.processEvents()
    assert QApplication.focusWidget() is window.split_pages
