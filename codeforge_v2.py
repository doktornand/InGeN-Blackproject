#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════╗
║  CODEFORGE v2.0  —  INGEN SYSTEMS WORKSTATION                     ║
║  Visual Program Composer  /  Node-Based CodeGen Engine            ║
║  *** AUTHORIZED PERSONNEL ONLY ***                                ║
║  Features: Nodal Flow · Undo-Tree · Auto-Layout · CRT FX          ║
╚═══════════════════════════════════════════════════════════════════╝
"""

import sys
import json
import os
import re
import copy
import uuid
import math
from collections import defaultdict, deque
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QSplitter, QTreeWidget, QTreeWidgetItem, QLabel, QFrame,
    QScrollArea, QPushButton, QTextEdit, QLineEdit, QComboBox,
    QMessageBox, QFileDialog, QTabWidget, QGroupBox, QFormLayout,
    QDialog, QDialogButtonBox, QStatusBar, QAction, QMenuBar,
    QToolBar, QSizePolicy, QAbstractItemView, QHeaderView,
    QGraphicsDropShadowEffect, QSpinBox, QCheckBox, QGraphicsOpacityEffect,
    QShortcut, QInputDialog, QProgressBar
)
from PyQt5.QtCore import (
    Qt, QTimer, QPoint, QRect, QMimeData, QThread, pyqtSignal,
    QPropertyAnimation, QEasingCurve, QSize, QByteArray, QObject,
    QLineF, QPointF, QTime
)
from PyQt5.QtGui import (
    QFont, QColor, QPalette, QPainter, QBrush, QPen, QPixmap,
    QFontDatabase, QLinearGradient, QTextCharFormat, QSyntaxHighlighter,
    QTextDocument, QCursor, QDrag, QIcon, QPainterPath, QKeySequence,
    QRadialGradient, QTransform
)

# ═══════════════════════════════════════════════════════════════════
#  COLOUR PALETTE  —  INGEN AMBER/GREEN TERMINAL + CRT PHOSPHOR
# ═══════════════════════════════════════════════════════════════════
C = {
    'bg':           '#050805',
    'bg_panel':     '#0a0f0a',
    'bg_card':      '#0d140d',
    'bg_hover':     '#142014',
    'border':       '#1a2e1a',
    'border_bright':'#2a5a2a',
    'amber':        '#ffb000',
    'amber_dim':    '#7a5500',
    'amber_bright': '#ffd060',
    'green':        '#00ff41',
    'green_dim':    '#004d14',
    'green_mid':    '#00b32d',
    'green_bright': '#80ff9f',
    'red':          '#ff3030',
    'red_dim':      '#4d0000',
    'cyan':         '#00e5ff',
    'cyan_dim':     '#003d45',
    'white':        '#c8ffc8',
    'white_dim':    '#4a664a',
    'fn_color':     '#00ff41',
    'var_color':    '#ffb000',
    'ctrl_color':   '#00e5ff',
    'flow_color':   '#ff00aa',
    'comment':      '#2a5a2a',
    'phosphor_glow':'#00ff4133',
    'glass':        '#00ff4108',
}

STYLESHEET = f"""
QMainWindow, QWidget {{
    background-color: {C['bg']};
    color: {C['green']};
    font-family: 'Courier New', 'Consolas', monospace;
    font-size: 11px;
}}
QMenuBar {{
    background-color: {C['bg_panel']};
    color: {C['amber']};
    border-bottom: 1px solid {C['border_bright']};
    font-size: 11px;
    padding: 2px;
}}
QMenuBar::item:selected {{
    background-color: {C['green_dim']};
    color: {C['green']};
}}
QMenu {{
    background-color: {C['bg_panel']};
    color: {C['green']};
    border: 1px solid {C['border_bright']};
}}
QMenu::item:selected {{
    background-color: {C['green_dim']};
    color: {C['amber']};
}}
QSplitter::handle {{
    background-color: {C['border_bright']};
    width: 2px;
    height: 2px;
}}
QScrollBar:vertical {{
    background: {C['bg']};
    width: 8px;
    border: none;
}}
QScrollBar::handle:vertical {{
    background: {C['green_dim']};
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{
    background: {C['green_mid']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QScrollBar:horizontal {{
    background: {C['bg']};
    height: 8px;
    border: none;
}}
QScrollBar::handle:horizontal {{
    background: {C['green_dim']};
    min-width: 20px;
}}
QToolBar {{
    background-color: {C['bg_panel']};
    border-bottom: 1px solid {C['border_bright']};
    spacing: 4px;
    padding: 2px 6px;
}}
QStatusBar {{
    background-color: {C['bg_panel']};
    color: {C['amber_dim']};
    border-top: 1px solid {C['border']};
    font-size: 10px;
}}
QTabWidget::pane {{
    border: 1px solid {C['border_bright']};
    background: {C['bg']};
}}
QTabBar::tab {{
    background: {C['bg_panel']};
    color: {C['white_dim']};
    border: 1px solid {C['border']};
    border-bottom: none;
    padding: 4px 12px;
    font-size: 10px;
    font-family: 'Courier New', monospace;
}}
QTabBar::tab:selected {{
    background: {C['bg']};
    color: {C['amber']};
    border-color: {C['amber_dim']};
}}
QLineEdit, QSpinBox, QComboBox {{
    background-color: {C['bg_card']};
    color: {C['green']};
    border: 1px solid {C['border_bright']};
    padding: 3px 6px;
    font-family: 'Courier New', monospace;
    font-size: 11px;
    selection-background-color: {C['green_dim']};
}}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
    border-color: {C['green']};
}}
QComboBox::drop-down {{
    border: none;
    background: {C['green_dim']};
}}
QComboBox QAbstractItemView {{
    background-color: {C['bg_panel']};
    color: {C['green']};
    border: 1px solid {C['border_bright']};
    selection-background-color: {C['green_dim']};
}}
QTreeWidget {{
    background-color: {C['bg_panel']};
    color: {C['green']};
    border: 1px solid {C['border']};
    alternate-background-color: {C['bg_card']};
    font-size: 11px;
}}
QTreeWidget::item:hover {{
    background-color: {C['bg_hover']};
    color: {C['amber']};
}}
QTreeWidget::item:selected {{
    background-color: {C['green_dim']};
    color: {C['green_bright']};
}}
QHeaderView::section {{
    background-color: {C['bg_card']};
    color: {C['amber']};
    border: 1px solid {C['border']};
    padding: 3px;
    font-size: 10px;
}}
QGroupBox {{
    border: 1px solid {C['border_bright']};
    border-radius: 2px;
    margin-top: 14px;
    color: {C['amber']};
    font-size: 10px;
    font-family: 'Courier New', monospace;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px;
    color: {C['amber']};
}}
QCheckBox {{
    color: {C['green']};
    spacing: 5px;
}}
QCheckBox::indicator {{
    width: 12px;
    height: 12px;
    border: 1px solid {C['border_bright']};
    background: {C['bg_card']};
}}
QCheckBox::indicator:checked {{
    background: {C['green_dim']};
    border-color: {C['green']};
}}
QProgressBar {{
    background: {C['bg_card']};
    border: 1px solid {C['border_bright']};
    color: {C['amber']};
    text-align: center;
    font-size: 9px;
}}
QProgressBar::chunk {{
    background: {C['green_dim']};
}}
"""

# ═══════════════════════════════════════════════════════════════════
#  STYLED BUTTON
# ═══════════════════════════════════════════════════════════════════
class ForgeButton(QPushButton):
    def __init__(self, text, variant='green', parent=None):
        super().__init__(text, parent)
        self.variant = variant
        self._apply_style()
        self.setCursor(QCursor(Qt.PointingHandCursor))

    def _apply_style(self):
        colors = {
            'green':  (C['green_dim'], C['green'],      C['border_bright'], C['green_bright']),
            'amber':  (C['amber_dim'], C['amber'],      '#7a5500',          C['amber_bright']),
            'red':    (C['red_dim'],   C['red'],        '#4d0000',          '#ff6060'),
            'cyan':   (C['cyan_dim'],  C['cyan'],       '#003d45',          '#60f0ff'),
            'ghost':  (C['bg_card'],   C['white_dim'],  C['border'],        C['white']),
            'pink':   ('#2a0018',      C['flow_color'], '#4d002e',          '#ff66cc'),
        }
        bg, fg, border, hover_fg = colors.get(self.variant, colors['green'])
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {fg};
                border: 1px solid {border};
                padding: 5px 14px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                font-weight: bold;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background-color: {border};
                color: {hover_fg};
                border-color: {hover_fg};
            }}
            QPushButton:pressed {{
                background-color: {fg};
                color: {C['bg']};
            }}
            QPushButton:disabled {{
                background-color: {C['bg']};
                color: {C['white_dim']};
                border-color: {C['border']};
            }}
        """)

# ═══════════════════════════════════════════════════════════════════
#  SYNTAX HIGHLIGHTER
# ═══════════════════════════════════════════════════════════════════
class CodeHighlighter(QSyntaxHighlighter):
    def __init__(self, document, language='CSharp'):
        super().__init__(document)
        self.language = language
        self._build_rules()

    def _fmt(self, color, bold=False, italic=False):
        f = QTextCharFormat()
        f.setForeground(QColor(color))
        if bold:   f.setFontWeight(QFont.Bold)
        if italic: f.setFontItalic(True)
        return f

    def _build_rules(self):
        self.rules = []
        kw_cs = r'\b(public|private|static|void|string|int|bool|var|new|return|if|else|for|foreach|while|try|catch|throw|using|class|namespace|async|await|true|false|null|this|await|var|let|const)\b'
        kw_ps = r'\b(function|param|begin|process|end|if|else|foreach|while|return|try|catch|throw|\$[a-zA-Z_]\w*|Write-Host|Write-Log|Get-|Set-|New-|Remove-|Invoke-)\b'
        kw_js = r'\b(function|async|await|const|let|var|return|if|else|for|while|try|catch|throw|new|true|false|null|undefined|this|of|in|class|import|from|export)\b'
        kw_map = {'CSharp': kw_cs, 'PowerShell': kw_ps, 'JavaScript': kw_js}
        kw = kw_map.get(self.language, kw_cs)
        self.rules += [
            (re.compile(kw),                     self._fmt(C['cyan'], bold=True)),
            (re.compile(r'"[^"\\]*(?:\\.[^"\\]*)*"'), self._fmt(C['amber'])),
            (re.compile(r"'[^'\\]*(?:\\.[^'\\]*)*'"), self._fmt(C['amber'])),
            (re.compile(r'\b\d+(\.\d+)?\b'),     self._fmt(C['amber_bright'])),
            (re.compile(r'//[^\n]*'),             self._fmt(C['comment'], italic=True)),
            (re.compile(r'#[^\n]*'),              self._fmt(C['comment'], italic=True)),
            (re.compile(r'\b[A-Z][a-zA-Z0-9_]*(?=\()'), self._fmt(C['green_bright'])),
            (re.compile(r'\$[a-zA-Z_]\w*'),      self._fmt(C['var_color'])),
            (re.compile(r'[{}()\[\];,.]'),        self._fmt(C['white_dim'])),
        ]

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            for m in pattern.finditer(text):
                self.setFormat(m.start(), m.end() - m.start(), fmt)


# ═══════════════════════════════════════════════════════════════════
#  NODE PORT  —  Input/Output anchor for connections
# ═══════════════════════════════════════════════════════════════════
class NodePort:
    """Represents a connection port on a CanvasBlock"""
    PORT_FLOW = 'flow'
    PORT_DATA = 'data'

    def __init__(self, name, dtype, direction, port_type, parent_block, index=0, total=1):
        self.name = name
        self.dtype = dtype  # string, int, bool, void, flow
        self.direction = direction  # 'in' or 'out'
        self.port_type = port_type  # PORT_FLOW or PORT_DATA
        self.parent = parent_block
        self.index = index
        self.total = total
        self.connections = []  # list of NodeConnection
        self.radius = 6
        self._hot = False

    def rect(self):
        """Return port QRect in block-local coordinates"""
        pw = self.parent.width()
        ph = self.parent.height()
        if self.port_type == self.PORT_FLOW:
            if self.direction == 'in':
                # Top center
                x = pw // 2 - self.radius
                y = -self.radius
            else:
                # Bottom center
                x = pw // 2 - self.radius
                y = ph - self.radius
        else:
            # Data ports distributed along left/right edges
            spacing = ph / (self.total + 1)
            y = int(spacing * (self.index + 1)) - self.radius
            if self.direction == 'in':
                x = -self.radius
            else:
                x = pw - self.radius
        return QRect(x, y, self.radius * 2, self.radius * 2)

    def center(self):
        r = self.rect()
        return QPoint(r.x() + r.width() // 2, r.y() + r.height() // 2)

    def global_center(self):
        c = self.center()
        return self.parent.mapToParent(c)

    def color(self):
        if self.port_type == self.PORT_FLOW:
            return C['flow_color']
        type_colors = {
            'string': C['amber'],
            'int': C['green_bright'],
            'bool': C['cyan'],
            'object': C['white'],
            'void': C['white_dim'],
            'Action': C['ctrl_color'],
            'FileInfo[]': C['amber_dim'],
            'Promise<object>': C['cyan_dim'],
            'number': C['green_bright'],
        }
        return type_colors.get(self.dtype, C['green'])

    def can_connect_to(self, other):
        if self.direction == other.direction:
            return False
        if self.parent is other.parent:
            return False
        if self.port_type != other.port_type:
            return False
        # Type compatibility (loose)
        if self.port_type == self.PORT_DATA:
            # Any data type can connect loosely; strict mode checks later
            pass
        return True


# ═══════════════════════════════════════════════════════════════════
#  NODE CONNECTION  —  Bézier wire between ports
# ═══════════════════════════════════════════════════════════════════
class NodeConnection:
    def __init__(self, port_out, port_in):
        self.source = port_out
        self.target = port_in
        self.source.connections.append(self)
        self.target.connections.append(self)
        self._temp_end = None  # For dragging new connections

    def delete(self):
        if self in self.source.connections:
            self.source.connections.remove(self)
        if self in self.target.connections:
            self.target.connections.remove(self)

    def path(self):
        """Return QPainterPath for the connection line"""
        if self._temp_end:
            p1 = self.source.global_center()
            p2 = self._temp_end
        else:
            p1 = self.source.global_center()
            p2 = self.target.global_center()

        path = QPainterPath(QPointF(p1))
        dx = abs(p2.x() - p1.x()) * 0.5
        if self.source.port_type == NodePort.PORT_FLOW:
            dy = abs(p2.y() - p1.y()) * 0.5
            ctrl1 = QPointF(p1.x(), p1.y() + dy)
            ctrl2 = QPointF(p2.x(), p2.y() - dy)
        else:
            ctrl1 = QPointF(p1.x() + dx, p1.y())
            ctrl2 = QPointF(p2.x() - dx, p2.y())
        path.cubicTo(ctrl1, ctrl2, QPointF(p2))
        return path

    def color(self):
        if self._temp_end:
            return C['amber'] if self.source.can_connect_to(self.target) else C['red']
        # Validate type match
        if self.source.dtype != self.target.dtype and self.source.port_type == NodePort.PORT_DATA:
            return C['red']  # type mismatch warning
        return self.source.color()


# ═══════════════════════════════════════════════════════════════════
#  UNDO SYSTEM  —  Command Pattern with Temporal Tree
# ═══════════════════════════════════════════════════════════════════
class Command:
    def __init__(self, description=""):
        self.description = description
        self.timestamp = datetime.now()
    def execute(self): pass
    def undo(self): pass

class AddBlockCmd(Command):
    def __init__(self, canvas, data, block_type, pos):
        super().__init__(f"Add {block_type}")
        self.canvas = canvas
        self.data = data
        self.block_type = block_type
        self.pos = pos
        self.block = None
    def execute(self):
        self.block = self.canvas._do_add_block(self.data, self.block_type, self.pos)
    def undo(self):
        if self.block:
            self.canvas._do_remove_block(self.block)

class RemoveBlockCmd(Command):
    def __init__(self, canvas, block):
        super().__init__(f"Remove {block.block_type}")
        self.canvas = canvas
        self.block = block
        self.data = block.data
        self.block_type = block.block_type
        self.pos = block.pos()
        self.conns = []
        # Store connections
        for port in block.ports:
            for c in port.connections[:]:
                self.conns.append((c.source, c.target))
    def execute(self):
        self.canvas._do_remove_block(self.block)
    def undo(self):
        self.block = self.canvas._do_add_block(self.data, self.block_type, self.pos)
        # Restore connections
        for src, tgt in self.conns:
            self.canvas._do_connect(src, tgt)

class MoveBlockCmd(Command):
    def __init__(self, block, old_pos, new_pos):
        super().__init__("Move block")
        self.block = block
        self.old_pos = old_pos
        self.new_pos = new_pos
    def execute(self):
        self.block.move(self.new_pos)
    def undo(self):
        self.block.move(self.old_pos)

class ConnectCmd(Command):
    def __init__(self, canvas, port_out, port_in):
        super().__init__("Connect ports")
        self.canvas = canvas
        self.port_out = port_out
        self.port_in = port_in
        self.conn = None
    def execute(self):
        self.conn = self.canvas._do_connect(self.port_out, self.port_in)
    def undo(self):
        if self.conn:
            self.canvas._do_disconnect(self.conn)

class DisconnectCmd(Command):
    def __init__(self, canvas, conn):
        super().__init__("Disconnect ports")
        self.canvas = canvas
        self.conn = conn
        self.src = conn.source
        self.tgt = conn.target
    def execute(self):
        self.canvas._do_disconnect(self.conn)
    def undo(self):
        self.canvas._do_connect(self.src, self.tgt)

class GroupBlocksCmd(Command):
    def __init__(self, canvas, blocks, group_name):
        super().__init__(f"Group {len(blocks)} blocks")
        self.canvas = canvas
        self.blocks = blocks
        self.group_name = group_name
        self.group = None
    def execute(self):
        self.group = self.canvas._do_group(self.blocks, self.group_name)
    def undo(self):
        if self.group:
            self.canvas._do_ungroup(self.group)

class UndoManager(QObject):
    history_changed = pyqtSignal()

    def __init__(self, max_history=50):
        super().__init__()
        self.history = []
        self.index = -1
        self.max_history = max_history

    def push(self, cmd):
        # Truncate redo branch
        if self.index < len(self.history) - 1:
            self.history = self.history[:self.index + 1]
        self.history.append(cmd)
        if len(self.history) > self.max_history:
            self.history.pop(0)
        else:
            self.index += 1
        cmd.execute()
        self.history_changed.emit()

    def undo(self):
        if self.index >= 0:
            cmd = self.history[self.index]
            cmd.undo()
            self.index -= 1
            self.history_changed.emit()
            return cmd.description
        return None

    def redo(self):
        if self.index < len(self.history) - 1:
            self.index += 1
            cmd = self.history[self.index]
            cmd.execute()
            self.history_changed.emit()
            return cmd.description
        return None

    def can_undo(self):
        return self.index >= 0

    def can_redo(self):
        return self.index < len(self.history) - 1

    def tree_summary(self):
        """Return list of (depth, description, is_active) for visualization"""
        result = []
        for i, cmd in enumerate(self.history):
            result.append((0, cmd.description, i == self.index))
        return result

# ═══════════════════════════════════════════════════════════════════
#  CANVAS BLOCK v2  —  With Node Ports & Multi-Selection
# ═══════════════════════════════════════════════════════════════════
class CanvasBlock(QFrame):
    BLOCK_FUNCTION  = 'function'
    BLOCK_VARIABLE  = 'variable'
    BLOCK_CONTROL   = 'control'
    BLOCK_GROUP     = 'group'

    selected_signal = pyqtSignal(object)
    remove_signal   = pyqtSignal(object)
    port_clicked    = pyqtSignal(object, object)  # block, port
    moved_signal    = pyqtSignal(object, QPoint, QPoint)  # block, old_pos, new_pos

    def __init__(self, data, block_type, parent=None):
        super().__init__(parent)
        self.data       = data
        self.block_type = block_type
        self.block_id   = str(uuid.uuid4())[:8]
        self._selected  = False
        self._drag_pos  = None
        self._old_pos   = None
        self.ports      = []
        self.is_group   = block_type == self.BLOCK_GROUP
        self.group_children = []  # if group
        self.collapsed  = False

        self.setFixedWidth(260)
        self._build_ui()
        self._build_ports()
        self._apply_style()

    def _color(self):
        return {
            self.BLOCK_FUNCTION: C['fn_color'],
            self.BLOCK_VARIABLE: C['var_color'],
            self.BLOCK_CONTROL:  C['ctrl_color'],
            self.BLOCK_GROUP:    C['amber'],
        }.get(self.block_type, C['green'])

    def _icon(self):
        return {
            self.BLOCK_FUNCTION: '⚙',
            self.BLOCK_VARIABLE: '◈',
            self.BLOCK_CONTROL:  '⬡',
            self.BLOCK_GROUP:    '▣',
        }.get(self.block_type, '•')

    def _build_ports(self):
        self.ports.clear()
        col = self._color()

        if self.block_type == self.BLOCK_FUNCTION:
            # Flow ports
            self.ports.append(NodePort('flow_in', 'flow', 'in', NodePort.PORT_FLOW, self))
            self.ports.append(NodePort('flow_out', 'flow', 'out', NodePort.PORT_FLOW, self))
            # Data inputs from parameters
            params = self.data.get('parameters', [])
            for i, p in enumerate(params):
                self.ports.append(NodePort(
                    p.get('name', f'arg{i}'),
                    p.get('datatype', 'object'),
                    'in', NodePort.PORT_DATA, self, i, len(params)
                ))
            # Data output from return
            ret = self.data.get('returns', {})
            if isinstance(ret, dict) and ret.get('datatype', 'void') != 'void':
                self.ports.append(NodePort(
                    'return', ret.get('datatype', 'object'),
                    'out', NodePort.PORT_DATA, self, 0, 1
                ))

        elif self.block_type == self.BLOCK_VARIABLE:
            self.ports.append(NodePort('flow_in', 'flow', 'in', NodePort.PORT_FLOW, self))
            self.ports.append(NodePort('flow_out', 'flow', 'out', NodePort.PORT_FLOW, self))
            self.ports.append(NodePort(
                self.data.get('name', 'val'),
                self.data.get('datatype', 'object'),
                'out', NodePort.PORT_DATA, self, 0, 1
            ))

        elif self.block_type == self.BLOCK_CONTROL:
            self.ports.append(NodePort('flow_in', 'flow', 'in', NodePort.PORT_FLOW, self))
            struct = self.data.get('structure', '')
            if struct == 'if':
                self.ports.append(NodePort('flow_true', 'flow', 'out', NodePort.PORT_FLOW, self))
                self.ports.append(NodePort('flow_false', 'flow', 'out', NodePort.PORT_FLOW, self))
                self.ports.append(NodePort('condition', 'bool', 'in', NodePort.PORT_DATA, self, 0, 1))
            else:
                self.ports.append(NodePort('flow_out', 'flow', 'out', NodePort.PORT_FLOW, self))
                if struct in ('for', 'foreach', 'while'):
                    self.ports.append(NodePort('collection', 'object', 'in', NodePort.PORT_DATA, self, 0, 1))

        elif self.block_type == self.BLOCK_GROUP:
            self.ports.append(NodePort('flow_in', 'flow', 'in', NodePort.PORT_FLOW, self))
            self.ports.append(NodePort('flow_out', 'flow', 'out', NodePort.PORT_FLOW, self))

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(3)

        if self.is_group:
            self._build_group_ui(layout)
            return

        # Header row
        hdr = QHBoxLayout()
        icon_lbl = QLabel(self._icon())
        icon_lbl.setStyleSheet(f"color: {self._color()}; font-size: 14px;")
        name = self.data.get('name', self.data.get('structure', '?'))
        self.name_lbl = QLabel(name)
        self.name_lbl.setStyleSheet(f"color: {self._color()}; font-weight: bold; font-size: 12px;")

        self.close_btn = QPushButton('✕')
        self.close_btn.setFixedSize(16, 16)
        self.close_btn.setStyleSheet(f"""
            QPushButton {{background: transparent; color: {C['white_dim']};
                border: none; font-size: 10px; padding: 0;}}
            QPushButton:hover {{color: {C['red']};}}
        """)
        self.close_btn.clicked.connect(lambda: self.remove_signal.emit(self))

        hdr.addWidget(icon_lbl)
        hdr.addWidget(self.name_lbl)
        hdr.addStretch()
        hdr.addWidget(self.close_btn)
        layout.addLayout(hdr)

        # Sub-info
        if self.block_type == self.BLOCK_FUNCTION:
            lang = self.data.get('language', '')
            fam = self.data.get('famille', '')
            sub = QLabel(f"{lang}  │  {fam}")
            sub.setStyleSheet(f"color: {C['white_dim']}; font-size: 9px;")
            layout.addWidget(sub)
            ret = self.data.get('returns', {})
            if isinstance(ret, dict) and ret.get('datatype', 'void') != 'void':
                ret_lbl = QLabel(f"→ {ret.get('datatype', '')}")
                ret_lbl.setStyleSheet(f"color: {C['amber_dim']}; font-size: 9px;")
                layout.addWidget(ret_lbl)
        elif self.block_type == self.BLOCK_VARIABLE:
            dtype = self.data.get('datatype', '')
            scope = self.data.get('scope', '')
            sub = QLabel(f"{dtype}  │  {scope}")
            sub.setStyleSheet(f"color: {C['white_dim']}; font-size: 9px;")
            layout.addWidget(sub)
            dv = self.data.get('default_value', '')
            if dv:
                dv_lbl = QLabel(f"= {dv}")
                dv_lbl.setStyleSheet(f"color: {C['amber']}; font-size: 9px;")
                dv_lbl.setMaximumWidth(240)
                layout.addWidget(dv_lbl)
        elif self.block_type == self.BLOCK_CONTROL:
            desc = self.data.get('description', '')
            sub = QLabel(desc)
            sub.setStyleSheet(f"color: {C['white_dim']}; font-size: 9px;")
            sub.setWordWrap(True)
            layout.addWidget(sub)

        # Type badge
        type_badge = QLabel(f" {self.block_type.upper()} ")
        type_badge.setStyleSheet(f"""
            background-color: {self._color()}22;
            color: {self._color()};
            border: 1px solid {self._color()}44;
            font-size: 8px; padding: 1px 4px;
        """)
        layout.addWidget(type_badge)

        self.setMinimumHeight(layout.sizeHint().height() + 16)

    def _build_group_ui(self, layout):
        self.group_title = QLabel(self.data.get('name', 'GROUP'))
        self.group_title.setStyleSheet(f"color: {C['amber']}; font-weight: bold; font-size: 13px;")
        layout.addWidget(self.group_title)
        info = QLabel(f"[{len(self.group_children)} blocks]")
        info.setStyleSheet(f"color: {C['white_dim']}; font-size: 9px;")
        layout.addWidget(info)
        self.setStyleSheet(f"""
            CanvasBlock {{
                background-color: {C['bg_card']}88;
                border: 2px dashed {C['amber']}66;
                border-radius: 4px;
            }}
        """)
        self.setMinimumHeight(80)
        self.setMinimumWidth(300)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw ports
        for port in self.ports:
            r = port.rect()
            color = QColor(port.color())
            if port._hot:
                color = QColor(C['white'])
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color, 1))
            if port.port_type == NodePort.PORT_FLOW:
                # Triangle for flow
                tri = QPainterPath()
                c = r.center()
                if port.direction == 'in':
                    tri.moveTo(c.x(), c.y() - 5)
                    tri.lineTo(c.x() - 4, c.y() + 3)
                    tri.lineTo(c.x() + 4, c.y() + 3)
                else:
                    tri.moveTo(c.x(), c.y() + 5)
                    tri.lineTo(c.x() - 4, c.y() - 3)
                    tri.lineTo(c.x() + 4, c.y() - 3)
                tri.closeSubpath()
                painter.drawPath(tri)
            else:
                painter.drawEllipse(r)
            # Type label near port
            painter.setPen(QColor(C['white_dim']))
            painter.setFont(QFont('Courier New', 7))
            if port.direction == 'in' and port.port_type == NodePort.PORT_DATA:
                painter.drawText(r.x() + 14, r.y() + 8, port.name[:8])
            elif port.direction == 'out' and port.port_type == NodePort.PORT_DATA:
                tw = painter.fontMetrics().width(port.name[:8])
                painter.drawText(r.x() - tw - 4, r.y() + 8, port.name[:8])
        painter.end()

    def port_at(self, pos):
        """Return port at local position, or None"""
        for port in self.ports:
            if port.rect().adjusted(-4, -4, 4, 4).contains(pos):
                return port
        return None

    def _apply_style(self):
        if self.is_group:
            return
        col = self._color()
        self.setStyleSheet(f"""
            CanvasBlock {{
                background-color: {C['bg_card']};
                border: 1px solid {col}44;
                border-left: 3px solid {col};
            }}
            CanvasBlock:hover {{
                background-color: {C['bg_hover']};
                border-left: 3px solid {col};
                border-color: {col}88;
            }}
        """)
        self.setCursor(QCursor(Qt.OpenHandCursor))

    def set_selected(self, selected):
        self._selected = selected
        col = self._color()
        if self.is_group:
            return
        if selected:
            self.setStyleSheet(f"""
                CanvasBlock {{
                    background-color: {col}15;
                    border: 1px solid {col};
                    border-left: 3px solid {col};
                }}
            """)
            # Glow effect
            glow = QGraphicsDropShadowEffect(self)
            glow.setBlurRadius(20)
            glow.setColor(QColor(col))
            glow.setOffset(0, 0)
            self.setGraphicsEffect(glow)
        else:
            self.setGraphicsEffect(None)
            self._apply_style()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            port = self.port_at(event.pos())
            if port:
                self.port_clicked.emit(self, port)
                return
            self._drag_pos = event.pos()
            self._old_pos = self.pos()
            self.selected_signal.emit(self)
            self.setCursor(QCursor(Qt.ClosedHandCursor))
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self._drag_pos and self._old_pos and self.pos() != self._old_pos:
            self.moved_signal.emit(self, self._old_pos, self.pos())
        self._drag_pos = None
        self._old_pos = None
        self.setCursor(QCursor(Qt.OpenHandCursor))
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() == Qt.LeftButton:
            delta = event.pos() - self._drag_pos
            new_pos = self.pos() + delta
            # Clamp
            if self.parent():
                pw = self.parent().width()
                ph = self.parent().height()
                nx = max(0, min(new_pos.x(), pw - self.width()))
                ny = max(0, min(new_pos.y(), ph - self.height()))
                self.move(nx, ny)
                # If group, move children relatively
                if self.is_group:
                    for child in self.group_children:
                        child.move(child.pos() + QPoint(nx, ny) - (self.pos() - delta))
        super().mouseMoveEvent(event)

    def update_group_bounds(self):
        """Resize group to fit children"""
        if not self.is_group or not self.group_children:
            return
        xs = [c.x() for c in self.group_children]
        ys = [c.y() for c in self.group_children]
        ws = [c.width() for c in self.group_children]
        hs = [c.height() for c in self.group_children]
        margin = 20
        self.move(min(xs) - margin, min(ys) - margin)
        self.setFixedWidth(max(xs + ws) - min(xs) + margin * 2)
        self.setFixedHeight(max(ys + hs) - min(ys) + margin * 2)

# ═══════════════════════════════════════════════════════════════════
#  CANVAS WIDGET v2  —  Nodal Graph, Undo, Groups, CRT FX
# ═══════════════════════════════════════════════════════════════════
class CanvasWidget(QWidget):
    selection_changed = pyqtSignal(object)
    canvas_changed    = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.blocks   = []
        self.connections = []
        self.selected_blocks = []
        self.undo_manager = UndoManager(max_history=100)
        self.undo_manager.history_changed.connect(self._on_undo_state)

        self._dragging_conn = None  # (source_port, temp_connection)
        self._temp_conn_end = None
        self._marquee_rect = None
        self._marquee_start = None
        self._scan_offset = 0
        self._flicker = 0.0

        self.setMinimumSize(1200, 800)
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(40)  # 25 fps for smooth wires & CRT

        # CRT overlay effect widget
        self.crt_overlay = QWidget(self)
        self.crt_overlay.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.crt_overlay.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.crt_overlay.setStyleSheet("background: transparent;")
        self.crt_overlay.show()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.crt_overlay.setGeometry(self.rect())

    def _tick(self):
        self._scan_offset = (self._scan_offset + 2) % self.height()
        self._flicker = (self._flicker + 0.1) % (2 * 3.14159)
        self.crt_overlay.update()
        self.update()

    def _on_undo_state(self):
        self.canvas_changed.emit()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Background with subtle noise
        painter.fillRect(self.rect(), QColor(C['bg']))

        # Grid
        painter.setPen(QPen(QColor(C['border']), 1, Qt.DotLine))
        step = 30
        for x in range(0, self.width(), step):
            painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), step):
            painter.drawLine(0, y, self.width(), y)

        # Draw connections first (behind blocks)
        for conn in self.connections:
            path = conn.path()
            color = QColor(conn.color())
            # Glow
            glow = QPen(color, 3)
            glow.setCapStyle(Qt.RoundCap)
            painter.setPen(glow)
            painter.drawPath(path)
            # Core
            core = QPen(QColor(C['bg']), 1)
            painter.setPen(core)
            painter.drawPath(path)

        # Draw temp connection
        if self._dragging_conn:
            conn = self._dragging_conn[1]
            path = conn.path()
            pen = QPen(QColor(C['amber']), 2, Qt.DashLine)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            painter.drawPath(path)

        # Marquee selection
        if self._marquee_rect:
            painter.setPen(QPen(QColor(C['green']), 1, Qt.DashLine))
            painter.setBrush(QBrush(QColor(C['green_dim'] + '44')))
            painter.drawRect(self._marquee_rect)

        # Corner labels
        painter.setPen(QColor(C['comment']))
        f = QFont('Courier New', 9)
        painter.setFont(f)
        painter.drawText(8, 18, "// INGEN SYSTEMS :: CODEFORGE CANVAS v2.0 [NODAL]")
        painter.drawText(8, self.height() - 24, f"BLOCKS: {len(self.blocks)}  CONNS: {len(self.connections)}")
        status = "[DRAG PORTS TO CONNECT  |  CTRL+G GROUP  |  A AUTO-LAYOUT  |  DEL REMOVE]"
        sw = painter.fontMetrics().width(status)
        painter.drawText(self.width() - sw - 10, self.height() - 24, status)

        if not self.blocks:
            painter.setPen(QColor(C['white_dim']))
            f2 = QFont('Courier New', 14)
            painter.setFont(f2)
            msg = "[ NODAL CANVAS — DRAG ELEMENTS & LINK PORTS ]"
            w = painter.fontMetrics().width(msg)
            painter.drawText((self.width() - w) // 2, self.height() // 2, msg)

        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Check port click on any block
            for block in self.blocks:
                local = block.mapFromParent(event.pos())
                port = block.port_at(local)
                if port and port.direction == 'out':
                    # Start connection drag
                    temp_conn = NodeConnection(port, port)  # self-loop as temp
                    temp_conn._temp_end = event.pos()
                    self._dragging_conn = (port, temp_conn)
                    self._temp_conn_end = event.pos()
                    return

            # Check block click
            clicked_block = None
            for block in reversed(self.blocks):
                if block.geometry().contains(event.pos()):
                    clicked_block = block
                    break

            if clicked_block:
                if not (event.modifiers() & Qt.ControlModifier):
                    self._clear_selection()
                self._select_block(clicked_block)
                return
            else:
                # Start marquee
                self._clear_selection()
                self._marquee_start = event.pos()
                self._marquee_rect = QRect(event.pos(), QSize(0, 0))

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging_conn:
            self._temp_conn_end = event.pos()
            self._dragging_conn[1]._temp_end = event.pos()
            # Highlight compatible ports
            for block in self.blocks:
                for port in block.ports:
                    if port.direction == 'in' and port.parent != self._dragging_conn[0].parent:
                        local = block.mapFromParent(event.pos())
                        if port.rect().adjusted(-8, -8, 8, 8).contains(local):
                            port._hot = True
                        else:
                            port._hot = False
                        block.update()
            self.update()
            return

        if self._marquee_start:
            self._marquee_rect = QRect(self._marquee_start, event.pos()).normalized()
            self.update()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._dragging_conn:
            src_port = self._dragging_conn[0]
            # Find target port
            for block in self.blocks:
                local = block.mapFromParent(event.pos())
                port = block.port_at(local)
                if port and port.direction == 'in' and port.parent != src_port.parent:
                    if src_port.can_connect_to(port):
                        # Check not already connected
                        already = any(c.source == src_port and c.target == port for c in self.connections)
                        if not already:
                            cmd = ConnectCmd(self, src_port, port)
                            self.undo_manager.push(cmd)
                            self.canvas_changed.emit()
                    break
            # Clear hot states
            for block in self.blocks:
                for port in block.ports:
                    port._hot = False
                block.update()
            self._dragging_conn = None
            self.update()
            return

        if self._marquee_rect:
            for block in self.blocks:
                if self._marquee_rect.intersects(block.geometry()):
                    self._select_block(block)
            self._marquee_rect = None
            self._marquee_start = None
            self.update()
            return

        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        key = event.key()
        mods = event.modifiers()

        if key == Qt.Key_Delete or key == Qt.Key_Backspace:
            self._delete_selected()
        elif key == Qt.Key_G and (mods & Qt.ControlModifier) and (mods & Qt.ShiftModifier):
            self._ungroup_selected()
        elif key == Qt.Key_G and (mods & Qt.ControlModifier):
            self._group_selected()
        elif key == Qt.Key_A and (mods & Qt.ControlModifier):
            self._select_all()
        elif key == Qt.Key_L and (mods & Qt.ControlModifier):
            self.auto_layout()
        elif key == Qt.Key_Z and (mods & Qt.ControlModifier) and (mods & Qt.ShiftModifier):
            desc = self.undo_manager.redo()
            if desc:
                self._emit_status(f"Redo: {desc}")
        elif key == Qt.Key_Z and (mods & Qt.ControlModifier):
            desc = self.undo_manager.undo()
            if desc:
                self._emit_status(f"Undo: {desc}")
        elif key == Qt.Key_Y and (mods & Qt.ControlModifier):
            desc = self.undo_manager.redo()
            if desc:
                self._emit_status(f"Redo: {desc}")
        else:
            super().keyPressEvent(event)

    def _emit_status(self, msg):
        # Will be connected to status bar in main window
        pass

    def _clear_selection(self):
        for b in self.selected_blocks:
            b.set_selected(False)
        self.selected_blocks.clear()
        self.selection_changed.emit(None)

    def _select_block(self, block):
        if block not in self.selected_blocks:
            self.selected_blocks.append(block)
            block.set_selected(True)
            self.selection_changed.emit(block)

    def _delete_selected(self):
        if not self.selected_blocks:
            return
        # Group delete into one undo? For simplicity, one by one
        for block in list(self.selected_blocks):
            cmd = RemoveBlockCmd(self, block)
            self.undo_manager.push(cmd)
        self._clear_selection()
        self.canvas_changed.emit()

    def _group_selected(self):
        if len(self.selected_blocks) < 2:
            return
        name, ok = QInputDialog.getText(self, "Group Blocks", "Group name:", text="Macro_01")
        if ok and name:
            cmd = GroupBlocksCmd(self, list(self.selected_blocks), name)
            self.undo_manager.push(cmd)
            self._clear_selection()
            self.canvas_changed.emit()

    def _ungroup_selected(self):
        for block in list(self.selected_blocks):
            if block.is_group:
                self.undo_manager.push(DisconnectGroupCmd(self, block))  # Will define below
        self._clear_selection()

    def _select_all(self):
        self._clear_selection()
        for b in self.blocks:
            self._select_block(b)

    # ─── Internal Doers (used by UndoManager) ─────────────────────
    def _do_add_block(self, data, block_type, pos):
        block = CanvasBlock(data, block_type, self)
        block.selected_signal.connect(self._on_block_selected)
        block.remove_signal.connect(self._do_remove_block)
        block.port_clicked.connect(self._on_port_clicked)
        block.moved_signal.connect(self._on_block_moved)
        block.move(pos.x(), pos.y())
        block.show()
        self.blocks.append(block)
        self.canvas_changed.emit()
        return block

    def _do_remove_block(self, block):
        if block in self.blocks:
            # Remove connections first
            for port in block.ports:
                for c in port.connections[:]:
                    self._do_disconnect(c)
            self.blocks.remove(block)
        if block in self.selected_blocks:
            self.selected_blocks.remove(block)
        block.hide()
        block.deleteLater()
        self.canvas_changed.emit()

    def _do_connect(self, port_out, port_in):
        conn = NodeConnection(port_out, port_in)
        self.connections.append(conn)
        self.update()
        return conn

    def _do_disconnect(self, conn):
        if conn in self.connections:
            conn.delete()
            self.connections.remove(conn)
            self.update()

    def _do_group(self, blocks, name):
        # Compute bounds
        xs = [b.x() for b in blocks]
        ys = [b.y() for b in blocks]
        ws = [b.width() for b in blocks]
        hs = [b.height() for b in blocks]
        margin = 20
        gx = min(xs) - margin
        gy = min(ys) - margin
        gw = max([x + w for x, w in zip(xs, ws)]) - min(xs) + margin * 2
        gh = max([y + h for y, h in zip(ys, hs)]) - min(ys) + margin * 2

        data = {'name': name, 'type': 'group'}
        group = CanvasBlock(data, CanvasBlock.BLOCK_GROUP, self)
        group.move(gx, gy)
        group.setFixedSize(gw, gh)
        group.group_children = blocks
        group.show()
        # Stack group behind children
        for b in blocks:
            group.stackUnder(b)
        self.blocks.append(group)
        self.update()
        return group

    def _do_ungroup(self, group):
        if group in self.blocks:
            self.blocks.remove(group)
        group.hide()
        group.deleteLater()
        self.update()

    def _on_block_selected(self, block):
        if not (QApplication.keyboardModifiers() & Qt.ControlModifier):
            self._clear_selection()
        self._select_block(block)

    def _on_port_clicked(self, block, port):
        pass  # Handled in mousePressEvent

    def _on_block_moved(self, block, old_pos, new_pos):
        cmd = MoveBlockCmd(block, old_pos, new_pos)
        self.undo_manager.push(cmd)

    def add_block(self, data, block_type):
        pos = QPoint(20 + (len(self.blocks) % 3) * 280, 20 + (len(self.blocks) // 3) * 160)
        cmd = AddBlockCmd(self, data, block_type, pos)
        self.undo_manager.push(cmd)
        return cmd.block

    def remove_block(self, block):
        cmd = RemoveBlockCmd(self, block)
        self.undo_manager.push(cmd)

    def clear(self):
        self.undo_manager = UndoManager(max_history=100)
        self.undo_manager.history_changed.connect(self._on_undo_state)
        for b in list(self.blocks):
            b.hide()
            b.deleteLater()
        self.blocks.clear()
        self.connections.clear()
        self.selected_blocks.clear()
        self.selection_changed.emit(None)
        self.canvas_changed.emit()
        self.update()

    def auto_layout(self):
        """DAG layer-based auto layout using flow connections"""
        if not self.blocks:
            return
        # Build adjacency from flow connections
        adj = defaultdict(list)
        indeg = defaultdict(int)
        all_blocks = set(self.blocks)
        for conn in self.connections:
            if conn.source.port_type == NodePort.PORT_FLOW and conn.source.direction == 'out':
                src = conn.source.parent
                tgt = conn.target.parent
                if src in all_blocks and tgt in all_blocks:
                    adj[src].append(tgt)
                    indeg[tgt] += 1
        for b in self.blocks:
            if b not in indeg:
                indeg[b] = 0

        # Topological sort (Kahn)
        queue = deque([b for b in self.blocks if indeg[b] == 0])
        layers = {}
        layer_idx = 0
        while queue:
            layer_size = len(queue)
            for _ in range(layer_size):
                b = queue.popleft()
                layers[b] = layer_idx
                for nb in adj[b]:
                    indeg[nb] -= 1
                    if indeg[nb] == 0:
                        queue.append(nb)
            layer_idx += 1
        # Remaining (cycles) get max layer
        for b in self.blocks:
            if b not in layers:
                layers[b] = layer_idx

        # Position
        layer_counts = defaultdict(int)
        x_spacing = 320
        y_spacing = 180
        for b in self.blocks:
            li = layers[b]
            yi = layer_counts[li]
            x = 40 + li * x_spacing
            y = 40 + yi * y_spacing
            b.move(x, y)
            layer_counts[li] += 1
        self.update()

    def get_ordered_blocks(self):
        """Topological order based on flow connections, fallback to spatial"""
        if not any(c.source.port_type == NodePort.PORT_FLOW for c in self.connections):
            return sorted(self.blocks, key=lambda b: (b.y(), b.x()))
        # DAG topo sort
        adj = defaultdict(list)
        indeg = defaultdict(int)
        for conn in self.connections:
            if conn.source.port_type == NodePort.PORT_FLOW:
                src = conn.source.parent
                tgt = conn.target.parent
                adj[src].append(tgt)
                indeg[tgt] += 1
        for b in self.blocks:
            if b not in indeg:
                indeg[b] = 0
        queue = deque([b for b in self.blocks if indeg[b] == 0])
        ordered = []
        while queue:
            b = queue.popleft()
            ordered.append(b)
            for nb in adj[b]:
                indeg[nb] -= 1
                if indeg[nb] == 0:
                    queue.append(nb)
        # Add remaining (cycles) spatially
        remaining = [b for b in self.blocks if b not in ordered]
        ordered += sorted(remaining, key=lambda b: (b.y(), b.x()))
        return ordered

    def to_dict(self):
        conns = []
        for c in self.connections:
            conns.append({
                'src_block': c.source.parent.block_id,
                'src_port': c.source.name,
                'tgt_block': c.target.parent.block_id,
                'tgt_port': c.target.name,
            })
        return {
            'blocks': [{
                'block_id': b.block_id,
                'block_type': b.block_type,
                'data': b.data,
                'pos': {'x': b.x(), 'y': b.y()},
                'is_group': b.is_group,
                'children_ids': [c.block_id for c in b.group_children] if b.is_group else [],
            } for b in self.blocks],
            'connections': conns,
        }

    def from_dict(self, data):
        self.clear()
        block_map = {}
        for bd in data.get('blocks', []):
            block = self._do_add_block(bd['data'], bd['block_type'], QPoint(bd['pos']['x'], bd['pos']['y']))
            block_map[block.block_id] = block
            if bd.get('is_group'):
                block.is_group = True
                block.group_children = []
                # Children will be linked after all blocks loaded
        # Link group children
        for bd in data.get('blocks', []):
            if bd.get('is_group'):
                bid = bd.get('block_id')
                if bid in block_map:
                    for cid in bd.get('children_ids', []):
                        if cid in block_map:
                            block_map[bid].group_children.append(block_map[cid])
        # Restore connections
        for cd in data.get('connections', []):
            src_b = block_map.get(cd['src_block'])
            tgt_b = block_map.get(cd['tgt_block'])
            if src_b and tgt_b:
                src_p = next((p for p in src_b.ports if p.name == cd['src_port']), None)
                tgt_p = next((p for p in tgt_b.ports if p.name == cd['tgt_port']), None)
                if src_p and tgt_p:
                    self._do_connect(src_p, tgt_p)
        self.update()

# ═══════════════════════════════════════════════════════════════════
#  CODE GENERATOR v2  —  Dataflow-aware topological compilation
# ═══════════════════════════════════════════════════════════════════
class CodeGenerator:
    _temp_counter = 0

    @staticmethod
    def generate(canvas_blocks, connections, language, program_name='GeneratedProgram', wrap_class=True):
        ordered = canvas_blocks  # Already topologically sorted from canvas
        lang = language

        # Pre-compute data connections map
        data_src = {}  # target_port -> source_port
        flow_next = defaultdict(list)  # block -> [next_blocks via flow]
        for c in connections:
            if c.source.port_type == NodePort.PORT_DATA:
                data_src[c.target] = c.source
            elif c.source.port_type == NodePort.PORT_FLOW and c.source.direction == 'out':
                flow_next[c.source.parent].append(c.target.parent)

        # Collect blocks by type
        fns  = [b for b in ordered if b.block_type == CanvasBlock.BLOCK_FUNCTION and b.data.get('language', lang) == lang]
        vars_ = [b for b in ordered if b.block_type == CanvasBlock.BLOCK_VARIABLE and b.data.get('language', lang) == lang]
        ctrls = [b for b in ordered if b.block_type == CanvasBlock.BLOCK_CONTROL]
        groups = [b for b in ordered if b.block_type == CanvasBlock.BLOCK_GROUP]

        CodeGenerator._temp_counter = 0

        if lang == 'CSharp':
            return CodeGenerator._gen_csharp_v2(ordered, fns, vars_, ctrls, groups, data_src, flow_next, program_name, wrap_class)
        elif lang == 'PowerShell':
            return CodeGenerator._gen_ps_v2(ordered, fns, vars_, ctrls, groups, data_src, flow_next, program_name)
        elif lang == 'JavaScript':
            return CodeGenerator._gen_js_v2(ordered, fns, vars_, ctrls, groups, data_src, flow_next, program_name)
        else:
            return f"// ERROR: Unsupported language '{lang}'"

    @staticmethod
    def _temp_var():
        CodeGenerator._temp_counter += 1
        return f"__auto_{CodeGenerator._temp_counter}"

    @staticmethod
    def _resolve_input(port, data_src, emitted):
        """Return code string for a connected input port"""
        if port not in data_src:
            return None
        src = data_src[port]
        src_block = src.parent
        if src_block.block_type == CanvasBlock.BLOCK_VARIABLE:
            return src_block.data.get('name', 'var')
        elif src_block.block_type == CanvasBlock.BLOCK_FUNCTION:
            # Check if already emitted
            if src in emitted:
                return emitted[src]
            # Need to inline or temp
            return None  # Will be handled upstream
        return None

    @staticmethod
    def _gen_csharp_v2(ordered, fns, vars_, ctrls, groups, data_src, flow_next, name, wrap_class):
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        lines = [
            f"// ═══════════════════════════════════════════════════",
            f"// {name}.cs  —  Generated by CODEFORGE v2.0 [NODAL]",
            f"// INGEN Systems Workstation  /  {ts}",
            f"// Dataflow compilation with topological ordering",
            f"// ═══════════════════════════════════════════════════",
            "",
            "using System;",
            "using System.IO;",
            "using System.Text;",
            "using System.Threading;",
            "using System.Collections.Generic;",
            "using System.Text.Json;",
            "",
        ]
        if wrap_class:
            lines += [f"namespace CodeForge.Generated", "{", f"    public class {name}", "    {"]
        indent = "        " if wrap_class else "    "

        # Variables declarations
        if vars_:
            lines.append(indent + "// ─── Variables ───────────────────────────────")
            for b in vars_:
                d = b.data
                dt = d.get('datatype', 'object')
                vn = d.get('name', 'variable')
                dv = d.get('default_value', 'null')
                scope = 'public static' if d.get('scope') == 'global' else 'private static'
                lines.append(f"{indent}{scope} {dt} {vn} = {dv};")
            lines.append("")

        # Function definitions
        if fns:
            lines.append(indent + "// ─── Function Definitions ──────────────────")
            for b in fns:
                src = b.data.get('source', '// [source not available]')
                for line in src.split('\n'):
                    lines.append(indent + line)
                lines.append("")

        # Main entry point with dataflow execution
        lines.append(indent + "// ─── Entry Point (Dataflow) ───────────────")
        lines.append(indent + "public static void Main(string[] args)")
        lines.append(indent + "{")
        lines.append(f'{indent}    WriteLog("Starting {name}", "INFO");')
        lines.append("")

        emitted = {}  # src_port -> temp_var_name

        for b in ordered:
            if b.block_type == CanvasBlock.BLOCK_VARIABLE:
                continue  # Already declared
            elif b.block_type == CanvasBlock.BLOCK_FUNCTION:
                d = b.data
                fname = d.get('name', 'Func')
                params_info = d.get('parameters', [])
                args = []
                for p in params_info:
                    pname = p.get('name', '')
                    # Find matching port
                    port = next((port for port in b.ports if port.name == pname and port.direction == 'in'), None)
                    if port and port in data_src:
                        val = CodeGenerator._resolve_input(port, data_src, emitted)
                        if val:
                            args.append(val)
                        else:
                            # Source function not yet emitted? Use default
                            args.append(p.get('default', 'null') if not p.get('required') else 'null')
                    else:
                        if not p.get('required') and 'default' in p:
                            args.append(p['default'])
                        else:
                            args.append('null')
                arg_str = ', '.join(args)
                ret = d.get('returns', {})
                has_ret = isinstance(ret, dict) and ret.get('datatype', 'void') != 'void'
                if has_ret:
                    # Check if return port is consumed
                    ret_port = next((p for p in b.ports if p.name == 'return' and p.direction == 'out'), None)
                    if ret_port and any(c.source == ret_port for c in data_src.values()):
                        tv = CodeGenerator._temp_var()
                        emitted[ret_port] = tv
                        lines.append(f"{indent}    var {tv} = {fname}({arg_str});")
                    else:
                        lines.append(f"{indent}    {fname}({arg_str});")
                else:
                    lines.append(f"{indent}    {fname}({arg_str});")

            elif b.block_type == CanvasBlock.BLOCK_CONTROL:
                struct = b.data.get('structure', '')
                CodeGenerator._emit_ctrl_cs_v2(lines, struct, b.data, b, data_src, flow_next, indent + "    ", emitted)

        lines.append("")
        lines.append(f'{indent}    WriteLog("{name} completed.", "INFO");')
        lines.append(indent + "}")
        if wrap_class:
            lines += ["    }", "}"]
        return '\n'.join(lines)

    @staticmethod
    def _emit_ctrl_cs_v2(lines, struct, data, block, data_src, flow_next, indent, emitted):
        pad = indent
        if struct == 'if':
            # Check if condition port connected
            cond_port = next((p for p in block.ports if p.name == 'condition'), None)
            cond = 'true'
            if cond_port and cond_port in data_src:
                val = CodeGenerator._resolve_input(cond_port, data_src, emitted)
                if val:
                    cond = val
                else:
                    cond = data.get('condition', 'true')
            else:
                cond = data.get('condition', 'true')
            lines.append(f"{pad}if ({cond})")
            lines.append(f"{pad}{{")
            lines.append(f"{pad}    // TODO: true branch")
            # Follow flow_true connections
            true_port = next((p for p in block.ports if p.name == 'flow_true'), None)
            if true_port:
                for c in true_port.connections:
                    tgt = c.target.parent
                    # Inline simple call if function
                    if tgt.block_type == CanvasBlock.BLOCK_FUNCTION:
                        lines.append(f"{pad}    // Connected: {tgt.data.get('name', '')}")
            lines.append(f"{pad}}}")
            false_port = next((p for p in block.ports if p.name == 'flow_false'), None)
            if false_port and false_port.connections:
                lines.append(f"{pad}else")
                lines.append(f"{pad}{{")
                lines.append(f"{pad}    // TODO: false branch")
                lines.append(f"{pad}}}")
        elif struct == 'for':
            var = data.get('var', 'i')
            end = data.get('limit', '10')
            lines.append(f"{pad}for (int {var} = 0; {var} < {end}; {var}++)")
            lines.append(f"{pad}{{")
            lines.append(f"{pad}    // TODO: loop body")
            lines.append(f"{pad}}}")
        elif struct == 'foreach':
            item = data.get('item', 'item')
            coll = data.get('collection', 'collection')
            # Check data connection for collection
            coll_port = next((p for p in block.ports if p.name == 'collection'), None)
            if coll_port and coll_port in data_src:
                val = CodeGenerator._resolve_input(coll_port, data_src, emitted)
                if val:
                    coll = val
            lines.append(f"{pad}foreach (var {item} in {coll})")
            lines.append(f"{pad}{{")
            lines.append(f"{pad}    // TODO: foreach body")
            lines.append(f"{pad}}}")
        elif struct == 'while':
            cond = data.get('condition', 'true')
            lines.append(f"{pad}while ({cond})")
            lines.append(f"{pad}{{")
            lines.append(f"{pad}    // TODO: while body")
            lines.append(f"{pad}}}")
        elif struct == 'try_catch':
            exc = data.get('exception', 'Exception')
            lines.append(f"{pad}try")
            lines.append(f"{pad}{{")
            lines.append(f"{pad}    // TODO: try block")
            lines.append(f"{pad}}}")
            lines.append(f"{pad}catch ({exc} ex)")
            lines.append(f"{pad}{{")
            lines.append(f'{pad}    WriteLog($"Error: {{ex.Message}}", "ERROR");')
            lines.append(f"{pad}}}")

    @staticmethod
    def _gen_ps_v2(ordered, fns, vars_, ctrls, groups, data_src, flow_next, name):
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        lines = [
            f"# ═══════════════════════════════════════════════════",
            f"# {name}.ps1  —  Generated by CODEFORGE v2.0 [NODAL]",
            f"# INGEN Systems Workstation  /  {ts}",
            f"# ═══════════════════════════════════════════════════",
            "#Requires -Version 5.1",
            "Set-StrictMode -Version Latest",
            "$ErrorActionPreference = 'Stop'",
            "",
        ]
        if vars_:
            lines.append("# ─── Variables ───────────────────────────────────")
            for b in vars_:
                d = b.data
                vn = f"${d.get('name', 'var')}"
                dv = d.get('default_value', '$null')
                lines.append(f"{vn} = {dv}")
            lines.append("")
        if fns:
            lines.append("# ─── Functions ───────────────────────────────────")
            for b in fns:
                lines += b.data.get('source', '# [none]').split('\n')
                lines.append("")
        lines.append("# ─── Main Execution ──────────────────────────────")
        lines.append(f'Write-Host "[INFO] Starting {name}" -ForegroundColor Green')
        lines.append("")
        emitted = {}
        for b in ordered:
            if b.block_type == CanvasBlock.BLOCK_VARIABLE:
                continue
            elif b.block_type == CanvasBlock.BLOCK_FUNCTION:
                d = b.data
                fname = d.get('name', 'Func')
                params_info = d.get('parameters', [])
                args = []
                for p in params_info:
                    pname = p.get('name', '')
                    port = next((port for port in b.ports if port.name == pname and port.direction == 'in'), None)
                    if port and port in data_src:
                        val = CodeGenerator._resolve_input(port, data_src, emitted)
                        if val:
                            args.append(f"${val}")
                        else:
                            args.append(p.get('default', '$null') if not p.get('required') else '$null')
                    else:
                        args.append(p.get('default', '$null') if not p.get('required') else '$null')
                arg_str = ' '.join(f"-{p.get('name')} {a}" for p, a in zip(params_info, args)) if params_info else ''
                lines.append(f"{fname} {arg_str}")
            elif b.block_type == CanvasBlock.BLOCK_CONTROL:
                struct = b.data.get('structure', '')
                CodeGenerator._emit_ctrl_ps_v2(lines, struct, b.data, indent=0)
        lines.append(f'Write-Host "[INFO] {name} completed." -ForegroundColor Green')
        return '\n'.join(lines)

    @staticmethod
    def _emit_ctrl_ps_v2(lines, struct, data, indent=0):
        pad = ' ' * indent
        if struct == 'if':
            cond = data.get('condition', '$true')
            lines += [f"{pad}if ({cond}) {{", f"{pad}    # TODO", f"{pad}}}"]
        elif struct == 'for':
            var = data.get('var', 'i'); end = data.get('limit', '10')
            lines += [f"{pad}for (${var} = 0; ${var} -lt {end}; ${var}++) {{", f"{pad}    # TODO", f"{pad}}}"]
        elif struct == 'foreach':
            item = data.get('item', 'item'); coll = data.get('collection', '$collection')
            lines += [f"{pad}foreach (${item} in {coll}) {{", f"{pad}    # TODO", f"{pad}}}"]
        elif struct == 'while':
            cond = data.get('condition', '$true')
            lines += [f"{pad}while ({cond}) {{", f"{pad}    # TODO", f"{pad}}}"]
        elif struct == 'try_catch':
            lines += [f"{pad}try {{", f"{pad}    # TODO", f"{pad}}} catch {{",
                      f"{pad}    Write-Error $_.Exception.Message", f"{pad}}}"]

    @staticmethod
    def _gen_js_v2(ordered, fns, vars_, ctrls, groups, data_src, flow_next, name):
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        lines = [
            f"// ═══════════════════════════════════════════════════",
            f"// {name}.js  —  Generated by CODEFORGE v2.0 [NODAL]",
            f"// INGEN Systems Workstation  /  {ts}",
            f"// ═══════════════════════════════════════════════════",
            "'use strict';",
            "",
        ]
        if vars_:
            lines.append("// ─── Variables ───────────────────────────────────")
            for b in vars_:
                d = b.data
                kw = 'const' if d.get('scope') == 'global' else 'let'
                vn = d.get('name', 'variable')
                dv = d.get('default_value', 'null')
                lines.append(f"{kw} {vn} = {dv};")
            lines.append("")
        if fns:
            lines.append("// ─── Functions ───────────────────────────────────")
            for b in fns:
                lines += b.data.get('source', '// [none]').split('\n')
                lines.append("")
        lines.append("// ─── Main Execution ──────────────────────────────")
        lines.append(f"(async function {name}() {{")
        lines.append(f'  console.log("[INFO] Starting {name}");')
        lines.append("")
        emitted = {}
        for b in ordered:
            if b.block_type == CanvasBlock.BLOCK_VARIABLE:
                continue
            elif b.block_type == CanvasBlock.BLOCK_FUNCTION:
                d = b.data
                fname = d.get('name', 'func')
                params_info = d.get('parameters', [])
                args = []
                for p in params_info:
                    pname = p.get('name', '')
                    port = next((port for port in b.ports if port.name == pname and port.direction == 'in'), None)
                    if port and port in data_src:
                        val = CodeGenerator._resolve_input(port, data_src, emitted)
                        if val:
                            args.append(val)
                        else:
                            args.append('null')
                    else:
                        args.append('null')
                arg_str = ', '.join(args)
                ret = d.get('returns', {})
                has_ret = isinstance(ret, dict) and ret.get('datatype', 'void') != 'void'
                if has_ret:
                    ret_port = next((p for p in b.ports if p.name == 'return' and p.direction == 'out'), None)
                    if ret_port and any(c.source == ret_port for c in data_src.values()):
                        tv = CodeGenerator._temp_var()
                        emitted[ret_port] = tv
                        lines.append(f"  const {tv} = await {fname}({arg_str});")
                    else:
                        lines.append(f"  await {fname}({arg_str});")
                else:
                    lines.append(f"  await {fname}({arg_str});")
            elif b.block_type == CanvasBlock.BLOCK_CONTROL:
                struct = b.data.get('structure', '')
                CodeGenerator._emit_ctrl_js_v2(lines, struct, b.data, indent=2)
        lines.append(f'  console.log("[INFO] {name} completed.");')
        lines.append("})();")
        return '\n'.join(lines)

    @staticmethod
    def _emit_ctrl_js_v2(lines, struct, data, indent=2):
        pad = ' ' * indent
        if struct == 'if':
            cond = data.get('condition', 'true')
            lines += [f"{pad}if ({cond}) {{", f"{pad}  // TODO", f"{pad}}}"]
        elif struct == 'for':
            var = data.get('var', 'i'); end = data.get('limit', '10')
            lines += [f"{pad}for (let {var} = 0; {var} < {end}; {var}++) {{", f"{pad}  // TODO", f"{pad}}}"]
        elif struct == 'foreach':
            item = data.get('item', 'item'); coll = data.get('collection', 'collection')
            lines += [f"{pad}for (const {item} of {coll}) {{", f"{pad}  // TODO", f"{pad}}}"]
        elif struct == 'while':
            cond = data.get('condition', 'true')
            lines += [f"{pad}while ({cond}) {{", f"{pad}  // TODO", f"{pad}}}"]
        elif struct == 'try_catch':
            lines += [f"{pad}try {{", f"{pad}  // TODO", f"{pad}}} catch (err) {{",
                      f"{pad}  console.error('[ERROR]', err.message);", f"{pad}}}"]

# ═══════════════════════════════════════════════════════════════════
#  DISCONNECT GROUP COMMAND
# ═══════════════════════════════════════════════════════════════════
class DisconnectGroupCmd(Command):
    def __init__(self, canvas, group):
        super().__init__("Ungroup")
        self.canvas = canvas
        self.group = group
        self.children = list(group.group_children)
        self.name = group.data.get('name', 'Group')
        self.pos = group.pos()
        self.size = group.size()
    def execute(self):
        self.canvas._do_ungroup(self.group)
    def undo(self):
        data = {'name': self.name, 'type': 'group'}
        group = self.canvas._do_add_block(data, CanvasBlock.BLOCK_GROUP, self.pos)
        group.setFixedSize(self.size)
        group.group_children = self.children
        for c in self.children:
            group.stackUnder(c)
        self.group = group


# ═══════════════════════════════════════════════════════════════════
#  CRT OVERLAY  —  Phosphor glow, scanlines, vignette, flicker
# ═══════════════════════════════════════════════════════════════════
class CRTOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self._scan_y = 0
        self._flicker = 0.0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(50)

    def _tick(self):
        self._scan_y = (self._scan_y + 3) % (self.parent().height() if self.parent() else 600)
        self._flicker = (self._flicker + 0.15) % 6.283
        self.update()

    def paintEvent(self, event):
        if not self.parent():
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()

        # Scanlines
        painter.setPen(QPen(QColor('#000000'), 1))
        for y in range(0, h, 3):
            painter.drawLine(0, y, w, y)

        # Vignette
        grad = QRadialGradient(QPointF(w/2, h/2), max(w, h) * 0.7)
        grad.setColorAt(0.0, QColor('#00000000'))
        grad.setColorAt(1.0, QColor('#001100aa'))
        painter.fillRect(self.rect(), grad)

        # Moving scan beam
        beam = QLinearGradient(0, self._scan_y - 20, 0, self._scan_y + 20)
        beam.setColorAt(0.0, QColor('#00ff4100'))
        beam.setColorAt(0.5, QColor('#00ff4122'))
        beam.setColorAt(1.0, QColor('#00ff4100'))
        painter.fillRect(QRect(0, self._scan_y - 10, w, 20), beam)

        # Subtle flicker overlay
        alpha = int(8 + 4 * math.sin(self._flicker))
        painter.fillRect(self.rect(), QColor(0, 0, 0, alpha))

        # Corner phosphor glow
        glow = QRadialGradient(QPointF(w - 40, 40), 80)
        glow.setColorAt(0.0, QColor('#00ff4108'))
        glow.setColorAt(1.0, QColor('#00000000'))
        painter.fillRect(self.rect(), glow)

        painter.end()


# ═══════════════════════════════════════════════════════════════════
#  CONTROL STRUCTURE DIALOG  (unchanged core)
# ═══════════════════════════════════════════════════════════════════
class ControlDialog(QDialog):
    STRUCTURES = {
        'if':        ('IF condition',         ['condition']),
        'for':       ('FOR loop',             ['var', 'limit']),
        'foreach':   ('FOREACH loop',         ['item', 'collection']),
        'while':     ('WHILE loop',           ['condition']),
        'try_catch': ('TRY/CATCH block',      []),
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('ADD CONTROL STRUCTURE')
        self.setStyleSheet(STYLESHEET)
        self.setMinimumWidth(420)
        self.result_data = None
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        hdr = QLabel("⬡  CONTROL STRUCTURE COMPOSER")
        hdr.setStyleSheet(f"color: {C['ctrl_color']}; font-size: 13px; font-weight: bold; padding: 8px;")
        layout.addWidget(hdr)
        struct_grp = QGroupBox("STRUCTURE TYPE")
        sg_layout  = QVBoxLayout(struct_grp)
        self.struct_combo = QComboBox()
        for key, (label, _) in self.STRUCTURES.items():
            self.struct_combo.addItem(label, key)
        self.struct_combo.currentIndexChanged.connect(self._refresh_fields)
        sg_layout.addWidget(self.struct_combo)
        layout.addWidget(struct_grp)
        self.fields_grp = QGroupBox("PARAMETERS")
        self.fields_layout = QFormLayout(self.fields_grp)
        layout.addWidget(self.fields_grp)
        self.field_widgets = {}
        self._refresh_fields()
        ok_btn = ForgeButton("ADD TO CANVAS", 'cyan')
        ok_btn.clicked.connect(self.accept)
        cancel_btn = ForgeButton("CANCEL", 'ghost')
        cancel_btn.clicked.connect(self.reject)
        btns_layout = QHBoxLayout()
        btns_layout.addWidget(cancel_btn)
        btns_layout.addWidget(ok_btn)
        layout.addLayout(btns_layout)

    def _refresh_fields(self):
        while self.fields_layout.count():
            item = self.fields_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.field_widgets.clear()
        key = self.struct_combo.currentData()
        if key in self.STRUCTURES:
            _, fields = self.STRUCTURES[key]
            for f in fields:
                lbl = QLabel(f.upper() + ":")
                lbl.setStyleSheet(f"color: {C['amber']}; font-size: 10px;")
                w = QLineEdit()
                w.setPlaceholderText(f"e.g. {f}")
                self.fields_layout.addRow(lbl, w)
                self.field_widgets[f] = w

    def get_data(self):
        key = self.struct_combo.currentData()
        label, fields = self.STRUCTURES[key]
        data = {
            'type':        'control',
            'structure':   key,
            'name':        label,
            'description': label,
            'language':    'any',
        }
        for f, w in self.field_widgets.items():
            data[f] = w.text().strip() or f
        return data


# ═══════════════════════════════════════════════════════════════════
#  LIBRARY PANEL  (unchanged)
# ═══════════════════════════════════════════════════════════════════
class LibraryPanel(QWidget):
    add_to_canvas = pyqtSignal(dict, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.library = {'functions': [], 'variables': []}
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        hdr = QLabel("▸ ELEMENT LIBRARY")
        hdr.setStyleSheet(f"color: {C['amber']}; font-weight: bold; font-size: 12px; padding: 4px;")
        layout.addWidget(hdr)
        self.search = QLineEdit()
        self.search.setPlaceholderText("/ search elements...")
        self.search.textChanged.connect(self._filter)
        layout.addWidget(self.search)
        self.lang_filter = QComboBox()
        self.lang_filter.addItems(['ALL', 'CSharp', 'PowerShell', 'JavaScript'])
        self.lang_filter.currentTextChanged.connect(self._filter)
        layout.addWidget(self.lang_filter)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['ELEMENT', 'LANG', 'FAMILY'])
        self.tree.setColumnWidth(0, 160)
        self.tree.setColumnWidth(1, 70)
        self.tree.setAlternatingRowColors(True)
        self.tree.setDragEnabled(True)
        self.tree.itemDoubleClicked.connect(self._on_double_click)
        layout.addWidget(self.tree)
        add_btn = ForgeButton("⊕  ADD TO CANVAS", 'green')
        add_btn.clicked.connect(self._on_add_click)
        layout.addWidget(add_btn)
        self.stats_lbl = QLabel("0 functions  /  0 variables")
        self.stats_lbl.setStyleSheet(f"color: {C['white_dim']}; font-size: 9px; padding: 2px;")
        layout.addWidget(self.stats_lbl)

    def load_library(self, data):
        self.library = data
        self._populate()

    def _populate(self):
        self.tree.clear()
        lang_f = self.lang_filter.currentText()
        search = self.search.text().lower()
        fn_root  = QTreeWidgetItem(self.tree, ['⚙ FUNCTIONS', '', ''])
        fn_root.setForeground(0, QColor(C['fn_color']))
        fn_root.setExpanded(True)
        var_root = QTreeWidgetItem(self.tree, ['◈ VARIABLES', '', ''])
        var_root.setForeground(0, QColor(C['var_color']))
        var_root.setExpanded(True)
        fn_count = var_count = 0
        for fn in self.library.get('functions', []):
            lang = fn.get('language', '')
            if lang_f != 'ALL' and lang != lang_f:
                continue
            if search and search not in fn.get('name', '').lower() and search not in fn.get('famille', '').lower():
                continue
            item = QTreeWidgetItem(fn_root, [fn.get('name', ''), lang, fn.get('famille', '')])
            item.setData(0, Qt.UserRole, ('function', fn))
            item.setForeground(0, QColor(C['fn_color']))
            item.setForeground(1, QColor(C['white_dim']))
            item.setForeground(2, QColor(C['amber_dim']))
            item.setToolTip(0, fn.get('description', ''))
            fn_count += 1
        for var in self.library.get('variables', []):
            lang = var.get('language', '')
            if lang_f != 'ALL' and lang != lang_f:
                continue
            if search and search not in var.get('name', '').lower():
                continue
            item = QTreeWidgetItem(var_root, [var.get('name', ''), lang, var.get('famille', '')])
            item.setData(0, Qt.UserRole, ('variable', var))
            item.setForeground(0, QColor(C['var_color']))
            item.setForeground(1, QColor(C['white_dim']))
            item.setForeground(2, QColor(C['amber_dim']))
            item.setToolTip(0, var.get('description', ''))
            var_count += 1
        self.stats_lbl.setText(f"{fn_count} functions  /  {var_count} variables")
        fn_root.setText(0, f"⚙ FUNCTIONS [{fn_count}]")
        var_root.setText(0, f"◈ VARIABLES [{var_count}]")

    def _filter(self):
        self._populate()

    def _get_selected_element(self):
        items = self.tree.selectedItems()
        if not items:
            return None, None
        item = items[0]
        data = item.data(0, Qt.UserRole)
        if data:
            return data
        return None, None

    def _on_add_click(self):
        btype, bdata = self._get_selected_element()
        if btype and bdata:
            self.add_to_canvas.emit(bdata, btype)

    def _on_double_click(self, item, col):
        data = item.data(0, Qt.UserRole)
        if data:
            btype, bdata = data
            self.add_to_canvas.emit(bdata, btype)

# ═══════════════════════════════════════════════════════════════════
#  PROPERTIES PANEL v2  —  With port inspection
# ═══════════════════════════════════════════════════════════════════
class PropertiesPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        hdr = QLabel("▸ PROPERTIES")
        hdr.setStyleSheet(f"color: {C['amber']}; font-weight: bold; font-size: 12px; padding: 4px;")
        layout.addWidget(hdr)
        self.tab = QTabWidget()
        layout.addWidget(self.tab)
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setStyleSheet(f"""
            QTextEdit {{ background: {C['bg_panel']}; color: {C['green']};
                border: 1px solid {C['border']}; font-family: 'Courier New', monospace; font-size: 10px; }}
        """)
        self.tab.addTab(self.info_text, "INFO")
        self.src_text = QTextEdit()
        self.src_text.setReadOnly(True)
        self.src_text.setStyleSheet(f"""
            QTextEdit {{ background: {C['bg_panel']}; color: {C['green']};
                border: 1px solid {C['border']}; font-family: 'Courier New', monospace; font-size: 10px; }}
        """)
        self.tab.addTab(self.src_text, "SOURCE")
        self.ports_text = QTextEdit()
        self.ports_text.setReadOnly(True)
        self.ports_text.setStyleSheet(f"""
            QTextEdit {{ background: {C['bg_panel']}; color: {C['green']};
                border: 1px solid {C['border']}; font-family: 'Courier New', monospace; font-size: 10px; }}
        """)
        self.tab.addTab(self.ports_text, "PORTS")
        self.clear_selection()

    def show_block(self, block):
        if block is None:
            self.clear_selection()
            return
        d = block.data
        btype = block.block_type
        lines = []
        lines.append(f"TYPE    : {btype.upper()}")
        lines.append(f"NAME    : {d.get('name', d.get('structure', 'N/A'))}")
        lines.append(f"ID      : {block.block_id}")
        lines.append(f"LANG    : {d.get('language', 'N/A')}")
        lines.append(f"FAMILY  : {d.get('famille', 'N/A')}")
        lines.append(f"DESC    : {d.get('description', 'N/A')}")
        lines.append("")
        if btype == CanvasBlock.BLOCK_FUNCTION:
            params = d.get('parameters', [])
            lines.append(f"PARAMETERS ({len(params)}):")
            for p in params:
                req = '✓' if p.get('required') else '○'
                default = f" = {p.get('default', '')}" if not p.get('required') else ''
                lines.append(f"  {req} {p.get('name','')} : {p.get('datatype','')}{default}")
            lines.append("")
            ret = d.get('returns', {})
            if isinstance(ret, dict):
                lines.append(f"RETURNS : {ret.get('datatype', 'void')}")
                lines.append(f"  {ret.get('description', '')}")
            throws = d.get('throws', [])
            if throws:
                lines.append(f"\nTHROWS  : {', '.join(throws)}")
            tags = d.get('tags', [])
            if tags:
                lines.append(f"\nTAGS    : {', '.join(tags)}")
        elif btype == CanvasBlock.BLOCK_VARIABLE:
            lines.append(f"DATATYPE : {d.get('datatype', 'N/A')}")
            lines.append(f"SCOPE    : {d.get('scope', 'N/A')}")
            lines.append(f"DEFAULT  : {d.get('default_value', 'N/A')}")
            tags = d.get('tags', [])
            if tags:
                lines.append(f"\nTAGS     : {', '.join(tags)}")
        elif btype == CanvasBlock.BLOCK_CONTROL:
            lines.append(f"STRUCTURE : {d.get('structure', 'N/A')}")
            for k, v in d.items():
                if k not in ('type', 'structure', 'name', 'description', 'language'):
                    lines.append(f"{k.upper():10}: {v}")
        elif btype == CanvasBlock.BLOCK_GROUP:
            lines.append(f"CHILDREN  : {len(block.group_children)} blocks")
        self.info_text.setPlainText('\n'.join(lines))
        src = d.get('source', '// No source available')
        self.src_text.setPlainText(src)
        lang = d.get('language', 'CSharp')
        CodeHighlighter(self.src_text.document(), lang)
        # Ports tab
        port_lines = []
        for p in block.ports:
            conn_count = len(p.connections)
            dir_sym = '▸' if p.direction == 'out' else '◂'
            type_sym = '⬢' if p.port_type == NodePort.PORT_FLOW else '◆'
            port_lines.append(f"{dir_sym} {type_sym} {p.name:12} : {p.dtype:10} [{conn_count} link(s)]")
        self.ports_text.setPlainText('\n'.join(port_lines) if port_lines else "// No ports")

    def clear_selection(self):
        self.info_text.setPlainText("// Select a block to view properties")
        self.src_text.setPlainText("// No element selected")
        self.ports_text.setPlainText("// No element selected")


# ═══════════════════════════════════════════════════════════════════
#  OUTPUT PANEL v2
# ═══════════════════════════════════════════════════════════════════
class OutputPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()
        self._highlighter = None

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        tb = QHBoxLayout()
        hdr = QLabel("▸ GENERATED CODE")
        hdr.setStyleSheet(f"color: {C['amber']}; font-weight: bold; font-size: 12px; padding: 4px;")
        tb.addWidget(hdr)
        self.lang_select = QComboBox()
        self.lang_select.addItems(['CSharp', 'PowerShell', 'JavaScript'])
        self.lang_select.setFixedWidth(130)
        tb.addWidget(QLabel("LANG:"))
        tb.addWidget(self.lang_select)
        self.name_input = QLineEdit("GeneratedProgram")
        self.name_input.setFixedWidth(160)
        tb.addWidget(QLabel("NAME:"))
        tb.addWidget(self.name_input)
        tb.addStretch()
        self.gen_btn  = ForgeButton("⚡ GENERATE",  'green')
        self.copy_btn = ForgeButton("⎘ COPY",       'amber')
        self.save_btn = ForgeButton("↓ SAVE CODE",  'cyan')
        self.validate_btn = ForgeButton("✓ VALIDATE", 'pink')
        tb.addWidget(self.gen_btn)
        tb.addWidget(self.copy_btn)
        tb.addWidget(self.save_btn)
        tb.addWidget(self.validate_btn)
        layout.addLayout(tb)
        self.editor = QTextEdit()
        self.editor.setStyleSheet(f"""
            QTextEdit {{ background: {C['bg_panel']}; color: {C['green']};
                border: 1px solid {C['border_bright']}; font-family: 'Courier New', monospace;
                font-size: 11px; selection-background-color: {C['green_dim']}; }}
        """)
        self.editor.setPlaceholderText("// Place elements on canvas, wire ports, then hit ⚡ GENERATE")
        layout.addWidget(self.editor)
        self.status = QLabel("Ready.")
        self.status.setStyleSheet(f"color: {C['white_dim']}; font-size: 9px; padding: 2px;")
        layout.addWidget(self.status)

    def set_code(self, code, language='CSharp'):
        self.editor.setPlainText(code)
        if self._highlighter:
            self._highlighter.setDocument(None)
        self._highlighter = CodeHighlighter(self.editor.document(), language)
        lines = code.count('\n') + 1
        chars = len(code)
        self.status.setText(f"Lines: {lines}  /  Chars: {chars}  /  Lang: {language}")

    def get_code(self):
        return self.editor.toPlainText()

    def get_language(self):
        return self.lang_select.currentText()

    def get_name(self):
        return self.name_input.text().strip() or 'GeneratedProgram'


# ═══════════════════════════════════════════════════════════════════
#  UNDO TREE PANEL  —  Visual history navigator
# ═══════════════════════════════════════════════════════════════════
class UndoTreePanel(QWidget):
    def __init__(self, undo_manager, parent=None):
        super().__init__(parent)
        self.undo_manager = undo_manager
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        hdr = QLabel("▸ TEMPORAL HISTORY")
        hdr.setStyleSheet(f"color: {C['amber']}; font-weight: bold; font-size: 12px; padding: 4px;")
        layout.addWidget(hdr)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['#', 'ACTION', 'TIME'])
        self.tree.setColumnWidth(0, 30)
        self.tree.setColumnWidth(1, 160)
        self.tree.setColumnWidth(2, 70)
        self.tree.setAlternatingRowColors(True)
        self.tree.setStyleSheet(f"""
            QTreeWidget {{ background: {C['bg_panel']}; color: {C['green']};
                border: 1px solid {C['border']}; font-size: 10px; }}
            QTreeWidget::item:selected {{ background: {C['green_dim']}; color: {C['amber']}; }}
        """)
        layout.addWidget(self.tree)
        self.refresh()

    def refresh(self):
        self.tree.clear()
        for i, cmd in enumerate(self.undo_manager.history):
            active = i == self.undo_manager.index
            item = QTreeWidgetItem(self.tree, [
                str(i + 1),
                ('▶ ' if active else '  ') + cmd.description,
                cmd.timestamp.strftime('%H:%M:%S')
            ])
            if active:
                item.setForeground(0, QColor(C['amber']))
                item.setForeground(1, QColor(C['amber_bright']))
                item.setBackground(0, QColor(C['green_dim'] + '44'))
            else:
                item.setForeground(1, QColor(C['white_dim']))
            item.setForeground(2, QColor(C['comment']))
        self.tree.scrollToBottom()

# ═══════════════════════════════════════════════════════════════════
#  MAIN WINDOW v2  —  Full integration of all subsystems
# ═══════════════════════════════════════════════════════════════════
class CodeForgeMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.library_data = {}
        self.current_project_path = None
        self._boot_phase = 0
        self._setup_window()
        self._setup_menu()
        self._setup_toolbar()
        self._setup_central()
        self._setup_statusbar()
        self._connect_signals()
        self._setup_shortcuts()
        self._boot_sequence()

    def _setup_window(self):
        self.setWindowTitle("CODEFORGE v2.0  —  INGEN SYSTEMS WORKSTATION [NODAL]")
        self.setMinimumSize(1400, 900)
        self.setStyleSheet(STYLESHEET)

    def _setup_menu(self):
        mb = self.menuBar()
        fm = mb.addMenu("FILE")
        fm.addAction("⊕  New Project",     self._new_project,  'Ctrl+N')
        fm.addAction("⊞  Open Project...", self._open_project, 'Ctrl+O')
        fm.addAction("↓  Save Project",    self._save_project, 'Ctrl+S')
        fm.addAction("↓  Save As...",      self._save_project_as)
        fm.addSeparator()
        fm.addAction("⊞  Load Library...", self._load_library, 'Ctrl+L')
        fm.addSeparator()
        fm.addAction("✕  Exit",            self.close,         'Ctrl+Q')

        em = mb.addMenu("EDIT")
        em.addAction("↶  Undo",            self._undo,         'Ctrl+Z')
        em.addAction("↷  Redo",            self._redo,         'Ctrl+Shift+Z')
        em.addAction("⎘  Copy Code",       self._copy_code,    'Ctrl+Shift+C')
        em.addAction("🗑  Clear Canvas",    self._clear_canvas)
        em.addSeparator()
        em.addAction("▣  Group Selected",  self._group_selected, 'Ctrl+G')
        em.addAction("□  Ungroup Selected",self._ungroup_selected, 'Ctrl+Shift+G')
        em.addSeparator()
        em.addAction("≋  Auto-Layout",     self._auto_layout,  'Ctrl+L')

        vm = mb.addMenu("VIEW")
        vm.addAction("⚡ Refresh Code",    self._generate_code, 'F5')
        vm.addAction("📜 Show Undo Tree",  self._toggle_undo_tree)

        hm = mb.addMenu("HELP")
        hm.addAction("ℹ  About CodeForge", self._show_about)
        hm.addAction("?  Shortcuts",       self._show_shortcuts)

    def _setup_toolbar(self):
        tb = self.addToolBar("Main")
        tb.setIconSize(QSize(16, 16))
        tb.setMovable(False)
        for label, slot, variant in [
            ("⊞ LOAD LIB",   self._load_library,   'amber'),
            ("⊕ CTRL BLOCK", self._add_ctrl_block,  'cyan'),
            ("▣ GROUP",      self._group_selected,   'pink'),
            ("≋ AUTO-LAY",   self._auto_layout,    'cyan'),
            ("⚡ GENERATE",  self._generate_code,   'green'),
            ("↓ SAVE PROJ",  self._save_project,    'amber'),
            ("↓ SAVE CODE",  self._save_code,       'cyan'),
            ("🗑 CLEAR",     self._clear_canvas,    'red'),
        ]:
            btn = ForgeButton(label, variant)
            btn.clicked.connect(slot)
            tb.addWidget(btn)
            tb.addSeparator()
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        tb.addWidget(spacer)
        self.clock_lbl = QLabel()
        self.clock_lbl.setStyleSheet(f"color: {C['amber']}; font-family: 'Courier New'; font-size: 11px; padding: 4px;")
        tb.addWidget(self.clock_lbl)
        clock_timer = QTimer(self)
        clock_timer.timeout.connect(self._update_clock)
        clock_timer.start(1000)
        self._update_clock()

    def _update_clock(self):
        self.clock_lbl.setText(datetime.now().strftime("[ %Y-%m-%d  %H:%M:%S ]"))

    def _setup_central(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Main horizontal splitter: Library | Canvas+Output | Properties+Undo
        hsplit = QSplitter(Qt.Horizontal)

        # Left: Library
        self.library_panel = LibraryPanel()
        self.library_panel.setMinimumWidth(260)
        self.library_panel.setMaximumWidth(380)
        hsplit.addWidget(self.library_panel)

        # Center: Canvas + Output
        center_split = QSplitter(Qt.Vertical)
        self.canvas_scroll = QScrollArea()
        self.canvas_scroll.setWidgetResizable(False)
        self.canvas = CanvasWidget()
        self.canvas.setMinimumSize(1000, 600)
        self.canvas_scroll.setWidget(self.canvas)
        self.canvas_scroll.setStyleSheet(f"background: {C['bg']}; border: none;")
        center_split.addWidget(self.canvas_scroll)

        # Output
        self.output_panel = OutputPanel()
        self.output_panel.setMinimumHeight(220)
        center_split.addWidget(self.output_panel)
        center_split.setSizes([520, 280])
        hsplit.addWidget(center_split)

        # Right: Properties + Undo Tree (vertical splitter)
        right_split = QSplitter(Qt.Vertical)
        self.props_panel = PropertiesPanel()
        self.props_panel.setMinimumWidth(260)
        self.props_panel.setMaximumWidth(400)
        right_split.addWidget(self.props_panel)

        self.undo_panel = UndoTreePanel(self.canvas.undo_manager)
        self.undo_panel.setMinimumHeight(150)
        self.undo_panel.setMaximumHeight(300)
        right_split.addWidget(self.undo_panel)
        right_split.setSizes([400, 200])
        hsplit.addWidget(right_split)

        hsplit.setSizes([280, 800, 300])
        main_layout.addWidget(hsplit)

        # CRT overlay on top
        self.crt = CRTOverlay(self.canvas_scroll.viewport())
        self.crt.setGeometry(self.canvas_scroll.viewport().rect())
        self.canvas_scroll.viewport().installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.canvas_scroll.viewport() and event.type() == event.Resize:
            self.crt.setGeometry(self.canvas_scroll.viewport().rect())
        return super().eventFilter(obj, event)

    def _setup_statusbar(self):
        sb = self.statusBar()
        self.status_main  = QLabel("INGEN SYSTEMS :: CODEFORGE v2.0 :: NODAL MODE")
        self.status_blocks= QLabel("CANVAS: 0 blocks")
        self.status_undo  = QLabel("UNDO: 0/0")
        sb.addWidget(self.status_main, 1)
        sb.addPermanentWidget(self.status_blocks)
        sb.addPermanentWidget(self.status_undo)

    def _connect_signals(self):
        self.library_panel.add_to_canvas.connect(self._add_to_canvas)
        self.canvas.selection_changed.connect(self.props_panel.show_block)
        self.canvas.canvas_changed.connect(self._on_canvas_changed)
        self.canvas.undo_manager.history_changed.connect(self._on_undo_changed)
        self.output_panel.gen_btn.clicked.connect(self._generate_code)
        self.output_panel.copy_btn.clicked.connect(self._copy_code)
        self.output_panel.save_btn.clicked.connect(self._save_code)
        self.output_panel.validate_btn.clicked.connect(self._validate_code)

    def _setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+Z"), self, self._undo)
        QShortcut(QKeySequence("Ctrl+Shift+Z"), self, self._redo)
        QShortcut(QKeySequence("Ctrl+Y"), self, self._redo)
        QShortcut(QKeySequence("Ctrl+G"), self, self._group_selected)
        QShortcut(QKeySequence("Ctrl+Shift+G"), self, self._ungroup_selected)
        QShortcut(QKeySequence("Ctrl+A"), self, self._select_all)
        QShortcut(QKeySequence("Ctrl+L"), self, self._auto_layout)
        QShortcut(QKeySequence("Delete"), self, self._delete_selected)
        QShortcut(QKeySequence("F5"), self, self._generate_code)

    def _add_to_canvas(self, data, block_type):
        block = self.canvas.add_block(data, block_type)
        self.status_main.setText(f"Added: {data.get('name', block_type)}")

    def _add_ctrl_block(self):
        dlg = ControlDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            self.canvas.add_block(data, CanvasBlock.BLOCK_CONTROL)
            self.status_main.setText(f"Control block added: {data.get('name', '')}")

    def _on_canvas_changed(self):
        n = len(self.canvas.blocks)
        c = len(self.canvas.connections)
        self.status_blocks.setText(f"CANVAS: {n} blk / {c} conn")

    def _on_undo_changed(self):
        um = self.canvas.undo_manager
        self.status_undo.setText(f"UNDO: {um.index + 1 if um.can_undo() else 0}/{len(um.history)}")
        self.undo_panel.refresh()

    def _undo(self):
        desc = self.canvas.undo_manager.undo()
        if desc:
            self.status_main.setText(f"↶ Undo: {desc}")

    def _redo(self):
        desc = self.canvas.undo_manager.redo()
        if desc:
            self.status_main.setText(f"↷ Redo: {desc}")

    def _group_selected(self):
        self.canvas._group_selected()

    def _ungroup_selected(self):
        self.canvas._ungroup_selected()

    def _select_all(self):
        self.canvas._select_all()

    def _delete_selected(self):
        self.canvas._delete_selected()

    def _auto_layout(self):
        self.canvas.auto_layout()
        self.status_main.setText("≋ Auto-layout applied (DAG topological)")

    def _generate_code(self):
        if not self.canvas.blocks:
            self.status_main.setText("⚠  No blocks on canvas")
            return
        lang = self.output_panel.get_language()
        name = self.output_panel.get_name()
        ordered = self.canvas.get_ordered_blocks()
        code = CodeGenerator.generate(ordered, self.canvas.connections, lang, name)
        self.output_panel.set_code(code, lang)
        self.status_main.setText(f"✓  Code generated  [{lang}] — {name} (dataflow-aware)")

    def _validate_code(self):
        code = self.output_panel.get_code()
        lang = self.output_panel.get_language()
        errors = []
        warnings = []

        if not code.strip():
            errors.append("Empty code buffer")

        # Basic syntax checks
        if lang == 'CSharp':
            if 'class' not in code and 'namespace' not in code:
                warnings.append("No class/namespace wrapper detected")
            open_braces = code.count('{')
            close_braces = code.count('}')
            if open_braces != close_braces:
                errors.append(f"Brace mismatch: {open_braces} open, {close_braces} close")
        elif lang == 'JavaScript':
            if not code.startswith("'use strict'"):
                warnings.append("Missing 'use strict' directive")
            open_parens = code.count('(')
            close_parens = code.count(')')
            if open_parens != close_parens:
                errors.append(f"Parenthesis mismatch: {open_parens} open, {close_parens} close")
        elif lang == 'PowerShell':
            if '#Requires' not in code:
                warnings.append("Missing #Requires directive")

        # Check for unconnected data ports
        for b in self.canvas.blocks:
            for p in b.ports:
                if p.direction == 'in' and p.port_type == NodePort.PORT_DATA and not p.connections:
                    if p.name != 'flow_in':
                        warnings.append(f"Unconnected input '{p.name}' on {b.data.get('name', 'block')}")

        msg = []
        if errors:
            msg.append("ERRORS:")
            msg += [f"  ✗ {e}" for e in errors]
        if warnings:
            msg.append("WARNINGS:")
            msg += [f"  ⚠ {w}" for w in warnings]
        if not errors and not warnings:
            msg.append("✓ VALIDATION PASSED — No issues detected")

        QMessageBox.information(self, "Validation Report", "\n".join(msg))
        self.status_main.setText(f"Validation: {len(errors)} errors, {len(warnings)} warnings")

    def _copy_code(self):
        code = self.output_panel.get_code()
        if code:
            QApplication.clipboard().setText(code)
            self.status_main.setText("✓  Code copied to clipboard")

    def _save_code(self):
        lang = self.output_panel.get_language()
        ext  = {'CSharp': 'cs', 'PowerShell': 'ps1', 'JavaScript': 'js'}.get(lang, 'txt')
        name = self.output_panel.get_name()
        path, _ = QFileDialog.getSaveFileName(self, "Save Code", f"{name}.{ext}",
                                               f"{lang} files (*.{ext})")
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.output_panel.get_code())
            self.status_main.setText(f"✓  Code saved: {path}")

    def _load_library(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Library", ".",
                                               "JSON files (*.json)")
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.library_data = data
                self.library_panel.load_library(data)
                n_fn  = len(data.get('functions', []))
                n_var = len(data.get('variables', []))
                self.status_main.setText(f"✓  Library loaded: {n_fn} functions, {n_var} variables")
            except Exception as e:
                QMessageBox.critical(self, "Load Error", f"Failed to load library:\n{e}")

    def _new_project(self):
        if self.canvas.blocks:
            r = QMessageBox.question(self, "New Project",
                "Clear current canvas and start a new project?",
                QMessageBox.Yes | QMessageBox.No)
            if r != QMessageBox.Yes:
                return
        self.canvas.clear()
        self.current_project_path = None
        self.output_panel.editor.clear()
        self.setWindowTitle("CODEFORGE v2.0  —  INGEN SYSTEMS WORKSTATION [NODAL]  —  [New Project]")
        self.status_main.setText("New project started")

    def _open_project(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Project", ".",
                                               "CodeForge Project (*.cfproj)")
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    proj = json.load(f)
                if 'library' in proj:
                    self.library_data = proj['library']
                    self.library_panel.load_library(proj['library'])
                if 'canvas' in proj:
                    self.canvas.from_dict(proj['canvas'])
                if 'output' in proj:
                    self.output_panel.lang_select.setCurrentText(proj['output'].get('language', 'CSharp'))
                    self.output_panel.name_input.setText(proj['output'].get('name', 'GeneratedProgram'))
                self.current_project_path = path
                self.setWindowTitle(f"CODEFORGE v2.0  —  {os.path.basename(path)}")
                self.status_main.setText(f"✓  Project loaded: {path}")
            except Exception as e:
                QMessageBox.critical(self, "Open Error", f"Failed to open project:\n{e}")

    def _save_project(self):
        if not self.current_project_path:
            self._save_project_as()
        else:
            self._write_project(self.current_project_path)

    def _save_project_as(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Project As", "project.cfproj",
                                               "CodeForge Project (*.cfproj)")
        if path:
            self.current_project_path = path
            self._write_project(path)

    def _write_project(self, path):
        try:
            proj = {
                'codeforge_version': '2.0',
                'saved_at': datetime.now().isoformat(),
                'library': self.library_data,
                'canvas':  self.canvas.to_dict(),
                'output': {
                    'language': self.output_panel.get_language(),
                    'name':     self.output_panel.get_name(),
                    'code':     self.output_panel.get_code(),
                }
            }
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(proj, f, indent=2, ensure_ascii=False)
            self.setWindowTitle(f"CODEFORGE v2.0  —  {os.path.basename(path)}")
            self.status_main.setText(f"✓  Project saved: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save project:\n{e}")

    def _clear_canvas(self):
        if self.canvas.blocks:
            r = QMessageBox.question(self, "Clear Canvas", "Clear all blocks from canvas?",
                                     QMessageBox.Yes | QMessageBox.No)
            if r == QMessageBox.Yes:
                self.canvas.clear()
                self.status_main.setText("Canvas cleared")

    def _toggle_undo_tree(self):
        self.undo_panel.setVisible(not self.undo_panel.isVisible())

    def _show_about(self):
        QMessageBox.information(self, "About CodeForge",
            "CODEFORGE v2.0 — NODAL EDITION\n"
            "INGEN Systems Workstation\n\n"
            "Visual Program Composer & Code Generator\n"
            "Features: Nodal Graph · Undo Tree · Auto-Layout · CRT FX\n"
            "Supports: C#, PowerShell, JavaScript\n\n"
            "[ THE CODE FINDS A WAY ]"
        )

    def _show_shortcuts(self):
        QMessageBox.information(self, "Keyboard Shortcuts",
            "Ctrl+N      New Project\n"
            "Ctrl+O      Open Project\n"
            "Ctrl+S      Save Project\n"
            "Ctrl+L      Load Library / Auto-Layout\n"
            "Ctrl+Z      Undo\n"
            "Ctrl+Shift+Z  Redo\n"
            "Ctrl+G      Group Selected Blocks\n"
            "Ctrl+Shift+G  Ungroup Selected\n"
            "Ctrl+A      Select All\n"
            "Del         Delete Selected\n"
            "F5          Generate Code\n"
            "\n"
            "MOUSE: Drag blocks · Drag ports to connect · Marquee select"
        )

    def _boot_sequence(self):
        self._boot_messages = [
            "INGEN SYSTEMS :: WORKSTATION BOOT SEQUENCE v4.0",
            "Initializing CODEFORGE NODAL kernel...",
            "Loading node graph engine... OK",
            "Loading temporal undo tree... OK",
            "Loading CRT phosphor subsystem... OK",
            "Loading dataflow compiler... OK",
            "Loading auto-layout DAG solver... OK",
            "Mounting library interface... OK",
            "System ready. Welcome, operator.",
            "Load a library JSON to begin. (FILE > Load Library)",
        ]
        self._boot_phase = 0
        self._boot_timer = QTimer(self)
        self._boot_timer.timeout.connect(self._next_boot_msg)
        self._boot_timer.start(250)
        default_lib = os.path.join(os.path.dirname(__file__), 'library.json')
        if os.path.exists(default_lib):
            try:
                with open(default_lib, 'r') as f:
                    data = json.load(f)
                self.library_data = data
                self.library_panel.load_library(data)
            except Exception:
                pass

    def _next_boot_msg(self):
        if self._boot_phase < len(self._boot_messages):
            self.status_main.setText(self._boot_messages[self._boot_phase])
            self._boot_phase += 1
        else:
            self._boot_timer.stop()


# ═══════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("CodeForge")
    app.setOrganizationName("INGEN Systems")
    app.setFont(QFont('Courier New', 10))
    win = CodeForgeMainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
