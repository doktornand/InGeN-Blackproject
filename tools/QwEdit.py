#!/usr/bin/env python3
"""
CODEFORGE v2.0 — LIBRARY EDITOR & CLEANER
GUI pour charger, nettoyer, éditer et sauvegarder les bibliothèques JSON.
Compatible avec la structure DSI-Validated SysAdmin Library.
"""
import sys
import json
import uuid
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QFileDialog, QMessageBox, QTabWidget, QDialog, QDialogButtonBox,
    QFormLayout, QLineEdit, QTextEdit, QComboBox, QCheckBox, QLabel,
    QSplitter, QStatusBar, QToolBar, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor, QBrush, QTextCharFormat, QIcon

# ═══════════════════════════════════════════════════════════════════
#  COLOUR PALETTE (Identique à CodeForge v2.0)
# ═══════════════════════════════════════════════════════════════════
C = {
    'bg':           '#050805', 'bg_panel':     '#0a0f0a', 'bg_card':      '#0d140d',
    'bg_hover':     '#142014', 'border':       '#1a2e1a', 'border_bright':'#2a5a2a',
    'amber':        '#ffb000', 'amber_dim':    '#7a5500',
    'green':        '#00ff41', 'green_dim':    '#004d14', 'green_mid':    '#00b32d',
    'green_bright': '#80ff9f',  # ✅ AJOUTÉ ICI (correspond au thème codeforge_v2.py)
    'white_dim':    '#4a664a',
    'red':          '#ff3030', 'cyan':         '#00e5ff',
    'fn_color':     '#00ff41', 'var_color':    '#ffb000', 'comment':      '#2a5a2a'
}

STYLESHEET = f"""
QMainWindow, QWidget {{ background-color: {C['bg']}; color: {C['green']}; font-family: 'Courier New', monospace; font-size: 11px; }}
QToolBar {{ background-color: {C['bg_panel']}; border-bottom: 1px solid {C['border_bright']}; spacing: 6px; padding: 4px; }}
QTabWidget::pane {{ border: 1px solid {C['border_bright']}; background: {C['bg']}; }}
QTabBar::tab {{ background: {C['bg_panel']}; color: {C['white_dim']}; border: 1px solid {C['border']}; padding: 4px 12px; font-size: 10px; }}
QTabBar::tab:selected {{ background: {C['bg']}; color: {C['amber']}; border-color: {C['amber_dim']}; }}
QTableWidget {{ background-color: {C['bg_panel']}; color: {C['green']}; border: 1px solid {C['border']}; alternate-background-color: {C['bg_card']}; font-size: 10px; }}
QTableWidget::item:hover {{ background-color: {C['bg_hover']}; color: {C['amber']}; }}
QTableWidget::item:selected {{ background-color: {C['green_dim']}; color: {C['green_bright']}; }}
QHeaderView::section {{ background-color: {C['bg_card']}; color: {C['amber']}; border: 1px solid {C['border']}; padding: 4px; }}
QLineEdit, QComboBox, QTextEdit {{ background-color: {C['bg_card']}; color: {C['green']}; border: 1px solid {C['border_bright']}; padding: 4px; font-family: 'Courier New', monospace; }}
QLabel {{ color: {C['amber']}; }}
QStatusBar {{ background-color: {C['bg_panel']}; color: {C['amber_dim']}; border-top: 1px solid {C['border']}; }}
QPushButton {{ background-color: {C['green_dim']}; color: {C['green']}; border: 1px solid {C['border_bright']}; padding: 4px 10px; font-weight: bold; }}
QPushButton:hover {{ background-color: {C['border_bright']}; color: {C['amber']}; }}
QPushButton:pressed {{ background-color: {C['green']}; color: {C['bg']}; }}
"""

class EntryEditorDialog(QDialog):
    """Formulaire d'édition/ajout pour Functions ou Variables"""
    def __init__(self, parent=None, entry_type='function', data=None):
        super().__init__(parent)
        self.entry_type = entry_type
        self.data = data or {}
        self.setWindowTitle(f"{'EDIT' if data else 'ADD'} {entry_type.upper()}")
        self.setStyleSheet(STYLESHEET)
        self.setMinimumSize(650, 500)
        self._build_ui()
        self._load_data()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        self.form = QFormLayout()
        self.fields = {}
        
        # Champs communs
        for key, placeholder in [
            ('id', 'Auto-gen if empty'), ('name', 'Ex: New-ADUser'), ('language', 'PowerShell/CSharp/JavaScript'),
            ('famille', 'Ex: ActiveDirectory'), ('description', 'Description...')
        ]:
            w = QLineEdit()
            w.setPlaceholderText(placeholder)
            self.fields[key] = w
            self.form.addRow(f"{key.upper()}:", w)

        if self.entry_type == 'function':
            for key, ph in [('parameters', 'JSON Array []'), ('returns', 'JSON Object {}'), ('tags', 'Comma separated'), ('throws', 'Comma separated')]:
                w = QTextEdit() if key in ('parameters', 'returns') else QLineEdit()
                if isinstance(w, QTextEdit):
                    w.setMaximumHeight(80)
                w.setPlaceholderText(ph)
                self.fields[key] = w
                self.form.addRow(f"{key.upper()}:", w)
            self.fields['source'] = QTextEdit()
            self.fields['source'].setPlaceholderText("Source code...")
            self.fields['source'].setMaximumHeight(150)
            self.form.addRow("SOURCE:", self.fields['source'])
        else:
            for key, ph in [('datatype', 'string/int/bool/etc.'), ('default_value', ''), ('scope', 'local/global'), ('tags', 'Comma separated')]:
                w = QLineEdit()
                w.setPlaceholderText(ph)
                self.fields[key] = w
                self.form.addRow(f"{key.upper()}:", w)

        layout.addLayout(self.form)
        
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self._validate_and_accept)
        btns.rejected.connect(self.reject)
        btns.setStyleSheet("QPushButton { color: white; } QPushButton:hover { background: #004d14; }")
        layout.addWidget(btns)

    def _load_data(self):
        for k, w in self.fields.items():
            val = self.data.get(k)
            if val is None: continue
            if isinstance(w, QTextEdit):
                if k in ('parameters', 'returns'):
                    w.setPlainText(json.dumps(val, indent=2, ensure_ascii=False))
                elif k == 'source':
                    w.setPlainText(val)
            else:
                if k in ('tags', 'throws') and isinstance(val, list):
                    w.setText(', '.join(val))
                else:
                    w.setText(str(val))

    def _validate_and_accept(self):
        # Validation basique JSON pour parameters/returns
        try:
            if self.entry_type == 'function':
                p = self.fields['parameters'].toPlainText().strip()
                if p: json.loads(p)
                r = self.fields['returns'].toPlainText().strip()
                if r: json.loads(r)
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "JSON Error", f"Invalid JSON in parameters/returns:\n{e}")
            return
        self.accept()

    def get_data(self):
        result = {k: w.text().strip() for k, w in self.fields.items() if not isinstance(w, QTextEdit)}
        for k, w in self.fields.items():
            if isinstance(w, QTextEdit):
                txt = w.toPlainText().strip()
                if k in ('parameters', 'returns') and txt:
                    result[k] = json.loads(txt)
                elif k == 'source':
                    result[k] = txt
        # Convert comma lists to arrays
        for k in ('tags', 'throws'):
            if k in result and result[k]:
                result[k] = [x.strip() for x in result[k].split(',') if x.strip()]
        # Clean empty fields
        return {k: v for k, v in result.items() if v or v == 0}

class LibraryEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CODEFORGE v2.0 — LIBRARY EDITOR & CLEANER")
        self.resize(1100, 750)
        self.setStyleSheet(STYLESHEET)
        self.lib_data = {"metadata": {}, "functions": [], "variables": []}
        self.current_file = None
        self._setup_ui()
        self._setup_toolbar()
        self.statusBar().showMessage("Ready. Load a library.json to begin.")

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        self.tabs = QTabWidget()
        self.fn_table = self._create_table(['ID', 'Name', 'Language', 'Famille', 'Description'])
        self.var_table = self._create_table(['ID', 'Name', 'Language', 'Datatype', 'Scope', 'Default'])
        self.tabs.addTab(self.fn_table, "⚙ FUNCTIONS")
        self.tabs.addTab(self.var_table, "◈ VARIABLES")
        
        main_layout.addWidget(self.tabs)

    def _create_table(self, headers):
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setAlternatingRowColors(True)
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table.cellDoubleClicked.connect(lambda r, c: self._edit_selected())
        return table

    def _setup_toolbar(self):
        tb = self.addToolBar("Actions")
        tb.setMovable(False)
        actions = [
            ("📂 LOAD", self._load_file, "amber"),
            ("💾 SAVE", self._save_file, "green"),
            ("🧹 CLEAN & FIX", self._clean_library, "cyan"),
            ("➕ ADD", self._add_entry, "green"),
            ("✏️ EDIT", self._edit_selected, "amber"),
            ("🗑 DELETE", self._delete_selected, "red"),
            ("↺ RELOAD", self._refresh_tables, "green")
        ]
        for txt, slot, color in actions:
            btn = QPushButton(txt)
            btn.clicked.connect(slot)
            tb.addWidget(btn)

    def _load_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Library", "", "JSON files (*.json)")
        if not path: return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                raw = json.load(f)
            # Nettoyage immédiat au chargement
            self.lib_data = self._clean_data(raw)
            self.current_file = path
            self._refresh_tables()
            self.statusBar().showMessage(f"Loaded: {os.path.basename(path)} ({len(self.lib_data['functions'])} fn, {len(self.lib_data['variables'])} var)")
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Failed to parse JSON:\n{e}")

    def _save_file(self):
        if not self.current_file:
            path, _ = QFileDialog.getSaveFileName(self, "Save As", "", "JSON files (*.json)")
            if not path: return
            self.current_file = path
        try:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                json.dump(self.lib_data, f, indent=2, ensure_ascii=False)
            self.statusBar().showMessage(f"Saved: {self.current_file}")
            QMessageBox.information(self, "Success", "Library saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))

    def _clean_library(self):
        self.lib_data = self._clean_data(self.lib_data)
        self._refresh_tables()
        self.statusBar().showMessage("Library cleaned & validated. Non-dict entries removed. Missing fields defaulted.")
        QMessageBox.information(self, "Cleaned", "Invalid entries removed. Missing required fields auto-populated. IDs regenerated where empty.")

    def _clean_data(self, data):
        if not isinstance(data, dict): data = {}
        data.setdefault("metadata", {
            "version": "2.0", "description": "", "created": datetime.now().strftime("%Y-%m-%d"),
            "author": "DSI — INGEN Systems", "scope": "", "validation_status": "APPROVED",
            "languages": ["PowerShell", "CSharp", "JavaScript"]
        })
        
        # Nettoyage Functions
        clean_fns = [f for f in data.get("functions", []) if isinstance(f, dict)]
        for f in clean_fns:
            f.setdefault("id", f"fn_{uuid.uuid4().hex[:4]}")
            f.setdefault("type", "function")
            f.setdefault("parameters", [])
            f.setdefault("returns", {"datatype": "void", "description": ""})
            f.setdefault("source", "")
            f.setdefault("tags", [])
            f.setdefault("throws", [])
        data["functions"] = clean_fns

        # Nettoyage Variables
        clean_vars = [v for v in data.get("variables", []) if isinstance(v, dict)]
        for v in clean_vars:
            v.setdefault("id", f"var_{uuid.uuid4().hex[:4]}")
            v.setdefault("type", "variable")
            v.setdefault("scope", "local")
            v.setdefault("tags", [])
        data["variables"] = clean_vars
        return data

    def _refresh_tables(self):
        # Functions
        self.fn_table.setRowCount(0)
        for i, f in enumerate(self.lib_data.get("functions", [])):
            self.fn_table.insertRow(i)
            self.fn_table.setItem(i, 0, QTableWidgetItem(f.get("id", "")))
            self.fn_table.setItem(i, 1, QTableWidgetItem(f.get("name", "")))
            self.fn_table.setItem(i, 2, QTableWidgetItem(f.get("language", "")))
            self.fn_table.setItem(i, 3, QTableWidgetItem(f.get("famille", "")))
            desc = f.get("description", "")
            self.fn_table.setItem(i, 4, QTableWidgetItem(desc[:60] + "..." if len(desc)>60 else desc))
            
        # Variables
        self.var_table.setRowCount(0)
        for i, v in enumerate(self.lib_data.get("variables", [])):
            self.var_table.insertRow(i)
            self.var_table.setItem(i, 0, QTableWidgetItem(v.get("id", "")))
            self.var_table.setItem(i, 1, QTableWidgetItem(v.get("name", "")))
            self.var_table.setItem(i, 2, QTableWidgetItem(v.get("language", "")))
            self.var_table.setItem(i, 3, QTableWidgetItem(v.get("datatype", "")))
            self.var_table.setItem(i, 4, QTableWidgetItem(v.get("scope", "")))
            self.var_table.setItem(i, 5, QTableWidgetItem(str(v.get("default_value", ""))))

    def _get_selected_id(self):
        table = self.tabs.currentWidget()
        sel = table.selectionModel().selectedRows()
        if not sel: return None, table
        return table.item(sel[0].row(), 0).text(), table

    def _add_entry(self):
        dialog = EntryEditorDialog(self, entry_type="function" if self.tabs.currentIndex() == 0 else "variable")
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if not data.get("id"): data["id"] = f"{'fn' if self.tabs.currentIndex()==0 else 'var'}_{uuid.uuid4().hex[:4]}"
            if self.tabs.currentIndex() == 0:
                self.lib_data["functions"].append(data)
            else:
                self.lib_data["variables"].append(data)
            self._refresh_tables()

    def _edit_selected(self):
        item_id, table = self._get_selected_id()
        if not item_id: return
        is_fn = self.tabs.currentIndex() == 0
        target_list = self.lib_data["functions" if is_fn else "variables"]
        entry = next((e for e in target_list if e.get("id") == item_id), None)
        if not entry: return
        
        dialog = EntryEditorDialog(self, entry_type="function" if is_fn else "variable", data=entry)
        if dialog.exec_() == QDialog.Accepted:
            updated = dialog.get_data()
            updated["id"] = item_id # Keep ID stable
            idx = target_list.index(entry)
            target_list[idx] = updated
            self._refresh_tables()

    def _delete_selected(self):
        item_id, table = self._get_selected_id()
        if not item_id: return
        if QMessageBox.question(self, "Confirm", f"Delete {item_id}?") == QMessageBox.Yes:
            is_fn = self.tabs.currentIndex() == 0
            target = self.lib_data["functions" if is_fn else "variables"]
            self.lib_data["functions" if is_fn else "variables"] = [e for e in target if e.get("id") != item_id]
            self._refresh_tables()

def main():
    app = QApplication(sys.argv)
    app.setFont(QFont('Courier New', 10))
    win = LibraryEditor()
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
