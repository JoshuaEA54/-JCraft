
STYLE_QSS = """
* {
  color: #E8EEF2;
}

QMainWindow { background: #0E1116; }

QMenuBar { background: rgba(14,17,22,0.85); border: none; }
QMenuBar::item { padding: 6px 12px; }
QMenuBar::item:selected { background: rgba(255,255,255,0.07); border-radius: 8px; }

QMenu { background: #151a20; border: 1px solid rgba(255,255,255,0.08); }
QMenu::item { padding: 6px 14px; }
QMenu::item:selected { background: rgba(255,255,255,0.08); }

.Card {
  background: rgba(17, 20, 26, 0.80);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px;
}

QSplitter::handle {
  background: rgba(0,0,0,0.28);
  width: 2px; margin: 0 4px;
}

QLabel#titleOutput { color: #B8C7D6; letter-spacing: 1px; }

QPlainTextEdit, QTextEdit {
  background: transparent;
  border: none;
  selection-background-color: #2ECC71;   /* grass */
  selection-color: #081F0D;
}

QPushButton {
  border-radius: 10px;
  padding: 10px 16px;
  border: 1px solid rgba(0,0,0,0.25);
  font-weight: 600;
}
QPushButton#btnPrimary {
  background: #2ECC71; /* grass */
  color: #08210F;
}
QPushButton#btnPrimary:hover { background: #3DDA7F; }
QPushButton#btnPrimary:pressed { background: #27B863; }

QStatusBar {
  background: rgba(14,17,22,0.85);
  border-top: 1px solid rgba(255,255,255,0.06);
  color: #9AA9B7;
}
"""
