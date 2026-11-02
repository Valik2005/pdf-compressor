"""Localization checks that do not require the Qt GUI runtime."""
import ast
import re
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "app.pyw"
CODE = SOURCE.read_text(encoding="utf-8")
TREE = ast.parse(CODE)


def translations():
    for node in TREE.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "I18N_EN" for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError("Translation dictionary not found")


def test_static_ui_copy_translated():
    dictionary = translations()
    checked = 0
    for node in ast.walk(TREE):
        if not isinstance(node, ast.Call):
            continue
        name = (node.func.id if isinstance(node.func, ast.Name)
                else node.func.attr if isinstance(node.func, ast.Attribute) else "")
        if name not in {"QLabel", "QPushButton", "QCheckBox", "setPlaceholderText", "addItem", "addTab"}:
            continue
        for arg in node.args:
            if not (isinstance(arg, ast.Constant) and isinstance(arg.value, str)):
                continue
            if re.search(r"[а-яА-ЯёЁ]", arg.value) and arg.value != "Русский":
                assert arg.value in dictionary, f"Missing English translation: {arg.value}"
                checked += 1
    assert checked > 25


def test_language_state_and_switch():
    assert 'self.settings.setValue("language", self.language)' in CODE
    assert 'self.language_box.addItem("English", "en")' in CODE
    assert 'self.language_box.addItem("Русский", "ru")' in CODE
    assert 'self.capture_texts()' in CODE
    assert 'self.apply_language()' in CODE
    assert 'self.refresh_table()' in CODE
    assert 'self.set_status(self._status_ru)' in CODE


def test_no_ui_layout_regression_from_release_25():
    assert 'self.main_split' in CODE
    assert 'RoundedCard' in CODE
    assert 'QScrollArea' in CODE
    assert 'def compress_pdf' not in CODE  # engine stays in its own file
