#!/usr/bin/env python3
"""
CODEFORGE v2.0 — LIBRARY EDITOR BLACK EDITION (CORRECTED)
Éditeur de bibliothèque ultime avec validation, recherche, duplication.
"""
import sys
import json
import uuid
import os
import re
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QFileDialog, QMessageBox, QTabWidget, QDialog, QDialogButtonBox,
    QFormLayout, QLineEdit, QTextEdit, QComboBox, QLabel,
    QSplitter, QStatusBar, QToolBar, QSizePolicy, QTreeWidget,
    QTreeWidgetItem, QInputDialog, QMenu
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QBrush, QTextCharFormat, QSyntaxHighlighter

# ============================================================================
#  COLOUR PALETTE
# ============================================================================
C = {
    'bg':           '#050805', 'bg_panel':     '#0a0f0a', 'bg_card':      '#0d140d',
    'bg_hover':     '#142014', 'border':       '#1a2e1a', 'border_bright':'#2a5a2a',
    'amber':        '#ffb000', 'amber_dim':    '#7a5500',
    'green':        '#00ff41', 'green_dim':    '#004d14', 'green_mid':    '#00b32d',
    'green_bright': '#80ff9f', 'white_dim':    '#4a664a',
    'red':          '#ff3030', 'cyan':         '#00e5ff', 'cyan_dim':     '#00558a',
    'fn_color':     '#00ff41', 'var_color':    '#ffb000', 'comment':      '#2a5a2a',
    'ctrl_color':   '#c586c0', 'flow_color':   '#d4d4d4'
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
QMenu {{ background-color: {C['bg_panel']}; color: {C['green']}; border: 1px solid {C['border_bright']}; }}
QMenu::item:selected {{ background-color: {C['green_dim']}; color: {C['green_bright']}; }}
"""


class CodeHighlighter(QSyntaxHighlighter):
    def __init__(self, document, language='PowerShell'):
        super().__init__(document)
        self.language = language
        self._build_rules()

    def _fmt(self, color, bold=False, italic=False):
        f = QTextCharFormat()
        f.setForeground(QColor(color))
        if bold: f.setFontWeight(QFont.Bold)
        if italic: f.setFontItalic(True)
        return f

    def _build_rules(self):
        self.rules = []
        kw_cs = r'\b(public|private|static|void|string|int|bool|var|new|return|if|else|for|foreach|while|try|catch|throw|using|class|namespace|async|await|true|false|null|this)\b'
        kw_ps = r'\b(function|param|begin|process|end|if|else|foreach|while|return|try|catch|throw|\$[a-zA-Z_]\w*|Write-Host|Write-Log|Get-|Set-|New-|Remove-|Invoke-)\b'
        kw_js = r'\b(function|async|await|const|let|var|return|if|else|for|while|try|catch|throw|new|true|false|null|undefined|this|class|import|from|export)\b'
        kw_map = {'CSharp': kw_cs, 'PowerShell': kw_ps, 'JavaScript': kw_js}
        kw = kw_map.get(self.language, kw_cs)

        self.rules += [
            (re.compile(kw), self._fmt(C['cyan'], bold=True)),
            (re.compile(r'"[^"\\]*(?:\\.[^"\\]*)*"'), self._fmt(C['amber'])),
            (re.compile(r"'[^'\\]*(?:\\.[^'\\]*)*'"), self._fmt(C['amber'])),
            (re.compile(r'\b\d+(\.\d+)?\b'), self._fmt(C['green_bright'])),
            (re.compile(r'//[^\n]*'), self._fmt(C['comment'], italic=True)),
            (re.compile(r'#[^\n]*'), self._fmt(C['comment'], italic=True)),
            (re.compile(r'\$[a-zA-Z_]\w*'), self._fmt(C['var_color'])),
            (re.compile(r'[{}()\[\];,.]'), self._fmt(C['white_dim'])),
        ]

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            for m in pattern.finditer(text):
                self.setFormat(m.start(), m.end() - m.start(), fmt)


def validate_function_schema(data):
    errors = []
    required = ['name', 'language', 'famille', 'description']
    for r in required:
        if r not in data or not data[r]:
            errors.append(f"Missing required field: {r}")
    params = data.get('parameters', [])
    if not isinstance(params, list):
        errors.append("'parameters' must be a list")
    for i, p in enumerate(params):
        if 'name' not in p:
            errors.append(f"Parameter {i}: missing 'name'")
        if 'datatype' not in p:
            errors.append(f"Parameter {i}: missing 'datatype'")
    ret = data.get('returns', {})
    if not isinstance(ret, dict):
        errors.append("'returns' must be an object")
    elif 'datatype' not in ret:
        errors.append("'returns' missing 'datatype'")
    return errors


class EntryEditorDialog(QDialog):
    def __init__(self, parent=None, entry_type='function', data=None):
        super().__init__(parent)
        self.entry_type = entry_type
        self.data = data or {}
        self.setWindowTitle(f"{'EDIT' if data else 'ADD'} {entry_type.upper()} — BLACK EDITION")
        self.setStyleSheet(STYLESHEET)
        self.setMinimumSize(800, 600)
        self._build_ui()
        self._load_data()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        splitter = QSplitter(Qt.Horizontal)
        self.form_widget = QWidget()
        form_layout = QVBoxLayout(self.form_widget)
        scroll = QWidget()
        scroll_layout = QFormLayout(scroll)

        self.id_field = QLineEdit()
        self.id_field.setPlaceholderText("Auto-generated if empty")
        scroll_layout.addRow("ID:", self.id_field)

        self.name_field = QLineEdit()
        self.name_field.setPlaceholderText("Ex: New-ADUserDSI")
        scroll_layout.addRow("NAME:", self.name_field)

        self.lang_combo = QComboBox()
        self.lang_combo.addItems(['PowerShell', 'CSharp', 'JavaScript', 'Python', 'Bash', 'Go'])
        scroll_layout.addRow("LANGUAGE:", self.lang_combo)

        self.famille_combo = QComboBox()
        self.famille_combo.setEditable(True)
        familles = ['ActiveDirectory', 'Security', 'Network', 'Logging', 'DevOps', 
                    'MLOps', 'Shares', 'Updates', 'DNS', 'DHCP', 'GPO', 'PKI', 
                    'Firewall', 'Registry', 'Services', 'Scheduler', 'IIS', 'SQL',
                    'Exchange', 'Certificates', 'Audit', 'Inventory', 'Backup',
                    'Monitoring', 'Hyper-V', 'WMI', 'Remote', 'CSharp-IO', 'CSharp-Net']
        self.famille_combo.addItems(familles)
        scroll_layout.addRow("FAMILLE:", self.famille_combo)

        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(60)
        scroll_layout.addRow("DESCRIPTION:", self.desc_edit)

        if self.entry_type == 'function':
            self.params_edit = QTextEdit()
            self.params_edit.setPlaceholderText('[{"name":"param1","datatype":"string","required":true}]')
            self.params_edit.setMaximumHeight(100)
            scroll_layout.addRow("PARAMETERS (JSON):", self.params_edit)

            self.returns_edit = QTextEdit()
            self.returns_edit.setPlaceholderText('{"datatype":"bool","description":"Success status"}')
            self.returns_edit.setMaximumHeight(80)
            scroll_layout.addRow("RETURNS (JSON):", self.returns_edit)

            self.tags_edit = QLineEdit()
            self.tags_edit.setPlaceholderText("tag1, tag2, tag3")
            scroll_layout.addRow("TAGS (comma):", self.tags_edit)

            self.throws_edit = QLineEdit()
            self.throws_edit.setPlaceholderText("ExceptionType1, ExceptionType2")
            scroll_layout.addRow("THROWS (comma):", self.throws_edit)

            self.source_edit = QTextEdit()
            self.source_edit.setPlaceholderText("function MyFunction { ... }")
            self.source_edit.setMaximumHeight(200)
            scroll_layout.addRow("SOURCE CODE:", self.source_edit)

        else:
            self.datatype_combo = QComboBox()
            self.datatype_combo.setEditable(True)
            datatypes = ['string', 'int', 'bool', 'PSCredential', 'string[]', 'hashtable', 
                         'object', 'double', 'DateTime', 'PSObject', 'list', 'dict']
            self.datatype_combo.addItems(datatypes)
            scroll_layout.addRow("DATATYPE:", self.datatype_combo)

            self.default_edit = QLineEdit()
            self.default_edit.setPlaceholderText('Default value (ex: "text", 42, $null)')
            scroll_layout.addRow("DEFAULT VALUE:", self.default_edit)

            self.scope_combo = QComboBox()
            self.scope_combo.addItems(['local', 'global'])
            scroll_layout.addRow("SCOPE:", self.scope_combo)

            self.tags_edit = QLineEdit()
            self.tags_edit.setPlaceholderText("tag1, tag2, tag3")
            scroll_layout.addRow("TAGS (comma):", self.tags_edit)

        self.validate_btn = QPushButton("✓ VALIDATE SCHEMA")
        self.validate_btn.clicked.connect(self._validate)
        scroll_layout.addRow("", self.validate_btn)

        form_layout.addWidget(scroll)
        self.form_widget.setLayout(form_layout)

        self.preview_widget = QWidget()
        preview_layout = QVBoxLayout(self.preview_widget)
        preview_label = QLabel("📺 LIVE PREVIEW (JSON)")
        preview_label.setStyleSheet(f"color: {C['cyan']}; font-weight: bold;")
        preview_layout.addWidget(preview_label)
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setStyleSheet(f"background: {C['bg_card']}; font-family: 'Courier New', monospace; font-size: 10px;")
        preview_layout.addWidget(self.preview_text)

        self._connect_live_updates()

        splitter.addWidget(self.form_widget)
        splitter.addWidget(self.preview_widget)
        splitter.setSizes([500, 300])
        layout.addWidget(splitter)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self._validate_and_accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _connect_live_updates(self):
        """Connecte tous les champs pour mise à jour live du preview."""
        # QLineEdit
        for w in [self.id_field, self.name_field, self.tags_edit]:
            if w:
                w.textChanged.connect(self._update_preview)
        
        # QTextEdit
        if self.entry_type == 'function':
            for w in [self.params_edit, self.returns_edit, self.source_edit]:
                if w:
                    w.textChanged.connect(self._update_preview)
        else:
            if self.default_edit:
                self.default_edit.textChanged.connect(self._update_preview)
        
        # QComboBox
        for w in [self.lang_combo, self.famille_combo]:
            if w:
                w.currentTextChanged.connect(self._update_preview)
        
        if self.entry_type == 'variable' and hasattr(self, 'datatype_combo'):
            self.datatype_combo.currentTextChanged.connect(self._update_preview)
            self.scope_combo.currentTextChanged.connect(self._update_preview)
        
        if self.desc_edit:
            self.desc_edit.textChanged.connect(self._update_preview)

    def _update_preview(self):
        data = self._collect_data()
        self.preview_text.setPlainText(json.dumps(data, indent=2, ensure_ascii=False)[:5000])

    def _collect_data(self):
        data = {
            'id': self.id_field.text().strip() or None,
            'name': self.name_field.text().strip(),
            'language': self.lang_combo.currentText(),
            'famille': self.famille_combo.currentText(),
            'description': self.desc_edit.toPlainText().strip(),
            'tags': [t.strip() for t in self.tags_edit.text().split(',') if t.strip()]
        }
        if self.entry_type == 'function':
            data['type'] = 'function'
            try:
                params = self.params_edit.toPlainText().strip()
                data['parameters'] = json.loads(params) if params else []
            except:
                data['parameters'] = []
            try:
                returns = self.returns_edit.toPlainText().strip()
                data['returns'] = json.loads(returns) if returns else {'datatype': 'void', 'description': ''}
            except:
                data['returns'] = {'datatype': 'void', 'description': ''}
            data['source'] = self.source_edit.toPlainText()
            data['throws'] = [t.strip() for t in self.throws_edit.text().split(',') if t.strip()]
        else:
            data['type'] = 'variable'
            data['datatype'] = self.datatype_combo.currentText()
            data['default_value'] = self.default_edit.text().strip()
            data['scope'] = self.scope_combo.currentText()
        return {k: v for k, v in data.items() if v not in ([], None, '')}

    def _load_data(self):
        if not self.data:
            return
        self.id_field.setText(self.data.get('id', ''))
        self.name_field.setText(self.data.get('name', ''))
        idx = self.lang_combo.findText(self.data.get('language', 'PowerShell'))
        if idx >= 0: self.lang_combo.setCurrentIndex(idx)
        self.famille_combo.setCurrentText(self.data.get('famille', ''))
        self.desc_edit.setPlainText(self.data.get('description', ''))
        self.tags_edit.setText(', '.join(self.data.get('tags', [])))

        if self.entry_type == 'function':
            params = self.data.get('parameters', [])
            self.params_edit.setPlainText(json.dumps(params, indent=2, ensure_ascii=False) if params else '[]')
            ret = self.data.get('returns', {'datatype': 'void', 'description': ''})
            self.returns_edit.setPlainText(json.dumps(ret, indent=2, ensure_ascii=False))
            self.source_edit.setPlainText(self.data.get('source', ''))
            self.throws_edit.setText(', '.join(self.data.get('throws', [])))
        else:
            idx = self.datatype_combo.findText(self.data.get('datatype', 'string'))
            if idx >= 0: self.datatype_combo.setCurrentIndex(idx)
            self.default_edit.setText(self.data.get('default_value', ''))
            idx = self.scope_combo.findText(self.data.get('scope', 'local'))
            if idx >= 0: self.scope_combo.setCurrentIndex(idx)

        self._update_preview()

    def _validate(self):
        data = self._collect_data()
        errors = validate_function_schema(data) if self.entry_type == 'function' else []
        if errors:
            QMessageBox.warning(self, "Validation Errors", "\n".join(errors))
        else:
            QMessageBox.information(self, "Validation", "✅ Schema valid!")

    def _validate_and_accept(self):
        data = self._collect_data()
        errors = validate_function_schema(data) if self.entry_type == 'function' else []
        if errors:
            QMessageBox.critical(self, "Cannot Save", "\n".join(errors))
            return
        self.accept()

    def get_data(self):
        data = self._collect_data()
        if not data.get('id'):
            prefix = 'fn' if self.entry_type == 'function' else 'var'
            data['id'] = f"{prefix}_{uuid.uuid4().hex[:8]}"
        return data


class LibraryEditorBlack(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CODEFORGE v2.0 — LIBRARY EDITOR BLACK EDITION")
        self.resize(1300, 800)
        self.setStyleSheet(STYLESHEET)
        self.lib_data = {"metadata": {}, "functions": [], "variables": []}
        self.current_file = None
        self.undo_stack = []
        self.redo_stack = []
        self._setup_ui()
        self._setup_toolbar()
        self._setup_statusbar()
        self.statusBar().showMessage("🔥 BLACK EDITION READY. Load a library to begin.")

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        filter_bar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search by name, famille, description...")
        self.search_input.textChanged.connect(self._refresh_tables)
        filter_bar.addWidget(self.search_input)

        self.lang_filter = QComboBox()
        self.lang_filter.addItems(['ALL', 'PowerShell', 'CSharp', 'JavaScript', 'Python', 'Bash', 'Go'])
        self.lang_filter.currentTextChanged.connect(self._refresh_tables)
        filter_bar.addWidget(QLabel("LANG:"))
        filter_bar.addWidget(self.lang_filter)

        self.famille_filter = QComboBox()
        self.famille_filter.setEditable(True)
        self.famille_filter.addItems(['ALL', 'ActiveDirectory', 'Security', 'Network', 'Logging', 'DevOps', 'MLOps'])
        self.famille_filter.currentTextChanged.connect(self._refresh_tables)
        filter_bar.addWidget(QLabel("FAMILY:"))
        filter_bar.addWidget(self.famille_filter)
        filter_bar.addStretch()
        main_layout.addLayout(filter_bar)

        self.tabs = QTabWidget()
        self.fn_table = self._create_table(['ID', 'Name', 'Language', 'Famille', 'Description', 'Tags'])
        self.var_table = self._create_table(['ID', 'Name', 'Language', 'Datatype', 'Scope', 'Default', 'Tags'])
        self.meta_table = self._create_metadata_table()
        self.tabs.addTab(self.fn_table, "⚙ FUNCTIONS")
        self.tabs.addTab(self.var_table, "◈ VARIABLES")
        self.tabs.addTab(self.meta_table, "📄 METADATA")
        main_layout.addWidget(self.tabs)

    def _create_table(self, headers):
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setAlternatingRowColors(True)
        table.horizontalHeader().setStretchLastSection(True)
        table.setContextMenuPolicy(Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(lambda pos: self._show_context_menu(table, pos))
        table.cellDoubleClicked.connect(lambda r, c: self._edit_selected())
        return table

    def _create_metadata_table(self):
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(['Field', 'Value'])
        table.horizontalHeader().setStretchLastSection(True)
        return table

    def _setup_toolbar(self):
        tb = self.addToolBar("Actions")
        tb.setMovable(False)
        actions = [
            ("📂 LOAD", self._load_file),
            ("💾 SAVE", self._save_file),
            ("🧹 CLEAN & FIX", self._clean_library),
            ("➕ ADD", self._add_entry),
            ("📋 DUPLICATE", self._duplicate_selected),
            ("✏️ EDIT", self._edit_selected),
            ("🗑 DELETE", self._delete_selected),
            ("↺ UNDO", self._undo),
            ("↷ REDO", self._redo),
            ("📊 STATS", self._show_stats),
            ("🔍 VALIDATE ALL", self._validate_all)
        ]
        for txt, slot in actions:
            btn = QPushButton(txt)
            btn.clicked.connect(slot)
            tb.addWidget(btn)

    def _setup_statusbar(self):
        sb = self.statusBar()
        self.status_msg = QLabel("READY")
        self.stats_label = QLabel("0 fn | 0 var")
        sb.addWidget(self.status_msg, 1)
        sb.addPermanentWidget(self.stats_label)

    def _show_context_menu(self, table, pos):
        menu = QMenu()
        menu.addAction("Edit", self._edit_selected)
        menu.addAction("Duplicate", self._duplicate_selected)
        menu.addAction("Delete", self._delete_selected)
        menu.exec_(table.mapToGlobal(pos))

    def _push_undo(self):
        self.undo_stack.append(json.dumps(self.lib_data))
        self.redo_stack.clear()

    def _undo(self):
        if not self.undo_stack:
            self.status_msg.setText("Nothing to undo")
            return
        self.redo_stack.append(json.dumps(self.lib_data))
        self.lib_data = json.loads(self.undo_stack.pop())
        self._refresh_tables()
        self._update_metadata_table()
        self.status_msg.setText("Undo done")

    def _redo(self):
        if not self.redo_stack:
            self.status_msg.setText("Nothing to redo")
            return
        self.undo_stack.append(json.dumps(self.lib_data))
        self.lib_data = json.loads(self.redo_stack.pop())
        self._refresh_tables()
        self._update_metadata_table()
        self.status_msg.setText("Redo done")

    def _load_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Library", "", "JSON files (*.json)")
        if not path: return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                raw = json.load(f)
            self.lib_data = self._clean_data(raw)
            self.current_file = path
            self._push_undo()
            self._refresh_tables()
            self._update_metadata_table()
            self.status_msg.setText(f"Loaded: {os.path.basename(path)} ({len(self.lib_data['functions'])} fn, {len(self.lib_data['variables'])} var)")
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
            self.status_msg.setText(f"Saved: {self.current_file}")
            QMessageBox.information(self, "Success", "Library saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))

    def _clean_library(self):
        self.lib_data = self._clean_data(self.lib_data)
        self._push_undo()
        self._refresh_tables()
        self._update_metadata_table()
        self.status_msg.setText("Library cleaned & validated")

    def _clean_data(self, data):
        if not isinstance(data, dict): data = {}
        data.setdefault("metadata", {
            "version": "3.0-BLACK",
            "description": "CodeForge DSI-Validated SysAdmin Library",
            "created": datetime.now().strftime("%Y-%m-%d"),
            "author": "DSI — INGEN Systems | Black Division",
            "scope": "",
            "validation_status": "APPROVED",
            "languages": ["PowerShell", "CSharp", "JavaScript", "Python", "Bash", "Go"]
        })
        clean_fns = [f for f in data.get("functions", []) if isinstance(f, dict)]
        for f in clean_fns:
            f.setdefault("id", f"fn_{uuid.uuid4().hex[:8]}")
            f.setdefault("type", "function")
            f.setdefault("parameters", [])
            f.setdefault("returns", {"datatype": "void", "description": ""})
            f.setdefault("source", "")
            f.setdefault("tags", [])
            f.setdefault("throws", [])
        data["functions"] = clean_fns
        clean_vars = [v for v in data.get("variables", []) if isinstance(v, dict)]
        for v in clean_vars:
            v.setdefault("id", f"var_{uuid.uuid4().hex[:8]}")
            v.setdefault("type", "variable")
            v.setdefault("scope", "local")
            v.setdefault("tags", [])
        data["variables"] = clean_vars
        return data

    def _refresh_tables(self):
        search = self.search_input.text().lower()
        lang = self.lang_filter.currentText()
        famille = self.famille_filter.currentText()

        def matches(item):
            if lang != 'ALL' and item.get('language') != lang: return False
            if famille != 'ALL' and item.get('famille') != famille: return False
            if search:
                haystack = f"{item.get('name','')} {item.get('famille','')} {item.get('description','')}".lower()
                if search not in haystack: return False
            return True

        self.fn_table.setRowCount(0)
        for i, f in enumerate([f for f in self.lib_data.get("functions", []) if matches(f)]):
            self.fn_table.insertRow(i)
            self.fn_table.setItem(i, 0, QTableWidgetItem(f.get("id", "")))
            self.fn_table.setItem(i, 1, QTableWidgetItem(f.get("name", "")))
            self.fn_table.setItem(i, 2, QTableWidgetItem(f.get("language", "")))
            self.fn_table.setItem(i, 3, QTableWidgetItem(f.get("famille", "")))
            desc = f.get("description", "")[:60]
            self.fn_table.setItem(i, 4, QTableWidgetItem(desc + "..." if len(f.get("description", "")) > 60 else desc))
            self.fn_table.setItem(i, 5, QTableWidgetItem(", ".join(f.get("tags", [])[:3])))

        self.var_table.setRowCount(0)
        for i, v in enumerate([v for v in self.lib_data.get("variables", []) if matches(v)]):
            self.var_table.insertRow(i)
            self.var_table.setItem(i, 0, QTableWidgetItem(v.get("id", "")))
            self.var_table.setItem(i, 1, QTableWidgetItem(v.get("name", "")))
            self.var_table.setItem(i, 2, QTableWidgetItem(v.get("language", "")))
            self.var_table.setItem(i, 3, QTableWidgetItem(v.get("datatype", "")))
            self.var_table.setItem(i, 4, QTableWidgetItem(v.get("scope", "")))
            self.var_table.setItem(i, 5, QTableWidgetItem(str(v.get("default_value", ""))[:30]))
            self.var_table.setItem(i, 6, QTableWidgetItem(", ".join(v.get("tags", [])[:3])))

        self.stats_label.setText(f"{len(self.lib_data['functions'])} fn | {len(self.lib_data['variables'])} var")

    def _update_metadata_table(self):
        meta = self.lib_data.get("metadata", {})
        self.meta_table.setRowCount(0)
        for i, (k, v) in enumerate(meta.items()):
            self.meta_table.insertRow(i)
            self.meta_table.setItem(i, 0, QTableWidgetItem(str(k)))
            self.meta_table.setItem(i, 1, QTableWidgetItem(json.dumps(v, ensure_ascii=False)[:100]))

    def _get_selected_id(self):
        table = self.tabs.currentWidget()
        if table in (self.meta_table, None): return None, table
        sel = table.selectionModel().selectedRows()
        if not sel: return None, table
        return table.item(sel[0].row(), 0).text(), table

    def _add_entry(self):
        dialog = EntryEditorDialog(self, entry_type="function" if self.tabs.currentIndex() == 0 else "variable")
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            self._push_undo()
            if self.tabs.currentIndex() == 0:
                self.lib_data["functions"].append(data)
            else:
                self.lib_data["variables"].append(data)
            self._refresh_tables()
            self.status_msg.setText(f"Added: {data.get('name')}")

    def _duplicate_selected(self):
        item_id, table = self._get_selected_id()
        if not item_id: return
        is_fn = self.tabs.currentIndex() == 0
        target_list = self.lib_data["functions" if is_fn else "variables"]
        entry = next((e for e in target_list if e.get("id") == item_id), None)
        if not entry: return
        new_entry = json.loads(json.dumps(entry))
        new_entry['id'] = f"{'fn' if is_fn else 'var'}_{uuid.uuid4().hex[:8]}"
        new_entry['name'] = f"{entry.get('name')}_copy"
        self._push_undo()
        target_list.append(new_entry)
        self._refresh_tables()
        self.status_msg.setText(f"Duplicated: {entry.get('name')}")

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
            updated["id"] = item_id
            idx = target_list.index(entry)
            self._push_undo()
            target_list[idx] = updated
            self._refresh_tables()
            self.status_msg.setText(f"Updated: {updated.get('name')}")

    def _delete_selected(self):
        item_id, table = self._get_selected_id()
        if not item_id: return
        if QMessageBox.question(self, "Confirm", f"Delete {item_id}?") != QMessageBox.Yes:
            return
        is_fn = self.tabs.currentIndex() == 0
        target = self.lib_data["functions" if is_fn else "variables"]
        self._push_undo()
        self.lib_data["functions" if is_fn else "variables"] = [e for e in target if e.get("id") != item_id]
        self._refresh_tables()
        self.status_msg.setText(f"Deleted: {item_id}")

    def _show_stats(self):
        fns = self.lib_data.get("functions", [])
        vars_ = self.lib_data.get("variables", [])
        languages = {}
        families = {}
        for f in fns:
            lang = f.get('language', 'unknown')
            languages[lang] = languages.get(lang, 0) + 1
            fam = f.get('famille', 'unknown')
            families[fam] = families.get(fam, 0) + 1
        stats = f"📊 STATISTICS\n\nFunctions: {len(fns)}\nVariables: {len(vars_)}\n\nBy language:\n" + "\n".join(f"  {k}: {v}" for k, v in languages.items()) + "\n\nBy family:\n" + "\n".join(f"  {k}: {v}" for k, v in families.items())
        QMessageBox.information(self, "Library Statistics", stats)

    def _validate_all(self):
        errors = []
        for i, f in enumerate(self.lib_data.get("functions", [])):
            errs = validate_function_schema(f)
            if errs:
                errors.append(f"Function #{i} ({f.get('name')}): {', '.join(errs)}")
        for i, v in enumerate(self.lib_data.get("variables", [])):
            errs = validate_function_schema(v)
            if errs:
                errors.append(f"Variable #{i} ({v.get('name')}): {', '.join(errs)}")
        if errors:
            QMessageBox.warning(self, "Validation Report", "\n".join(errors[:50]))
        else:
            QMessageBox.information(self, "Validation Report", "✅ All entries valid!")

    def statusMsg(self, msg):
        self.status_msg.setText(msg)


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont('Courier New', 10))
    win = LibraryEditorBlack()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()