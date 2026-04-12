import re
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PySide6.QtCore import QRegularExpression


class JCraftHighlighter(QSyntaxHighlighter):
    """Real-time syntax highlighter for :JCraft.

    Inspired by VS Code Dark+ — 5 visual categories so the colors carry meaning,
    not just decoration:

      Keyword  → blue   (ALL reserved words together: mesa_crafteo, fin, observador…)
      Ident    → teal   (every variable / function name the user defines)
      String   → orange (text between quotes)
      Number   → green  (numeric literals)
      Comment  → gray   (# … and /* … */)
    """

    def __init__(self, document):
        super().__init__(document)
        self._rules: list[tuple[QRegularExpression, QTextCharFormat]] = []
        self._init_formats()
        self._init_rules()

    # ------------------------------------------------------------------
    # Format builders
    # ------------------------------------------------------------------

    def _fmt(self, hex_color: str, bold: bool = False, italic: bool = False) -> QTextCharFormat:
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(hex_color))
        if bold:
            fmt.setFontWeight(QFont.Weight.Bold)
        if italic:
            fmt.setFontItalic(True)
        return fmt

    def _init_formats(self):
        # All reserved words — VS Code keyword blue (same family: mesa_crafteo = fin = observador)
        self.fmt_keyword = self._fmt("#569CD6", bold=True)
        # User-defined names (variables, function names) — VS Code variable teal
        self.fmt_ident   = self._fmt("#9CDCFE")
        # Boolean literals (verdadero / falso) — gold, clearly a "value" not a keyword or variable
        self.fmt_bool    = self._fmt("#DCDCAA", bold=True)
        # String & char literals — VS Code string orange
        self.fmt_string  = self._fmt("#CE9178")
        # Numeric literals — VS Code number light green
        self.fmt_number  = self._fmt("#B5CEA8")
        # Comments — VS Code comment green, italic
        self.fmt_comment = self._fmt("#6A9955", italic=True)

    # ------------------------------------------------------------------
    # Rules
    # ------------------------------------------------------------------

    def _init_rules(self):
        all_keywords = [
            # control flow
            "cultivar", "cosechar", "observador", "comparador", "dispensador",
            "creeper", "boom", "portal", "caso", "defecto", "salir_portal",
            "spawner", "romper", "fin",
            # function / return
            "mesa_crafteo", "craftear",
            # I/O
            "letrero", "cofre",
            # types
            "bloques", "coordenada", "texto", "redstone", "glifo",
            "inventario", "mapa",
            # void
            "vacío",
            # logical
            "y", "o", "no",
        ]

        joined = "|".join(re.escape(w) for w in all_keywords)
        kw_rx = QRegularExpression(rf"\b(?:{joined})\b")
        kw_rx.setPatternOptions(QRegularExpression.PatternOption.CaseInsensitiveOption)

        bool_rx = QRegularExpression(r"\b(?:verdadero|falso)\b")
        bool_rx.setPatternOptions(QRegularExpression.PatternOption.CaseInsensitiveOption)

        # Identifier pattern: ASCII + common Spanish accented chars
        ident_rx = QRegularExpression(r"\b[a-zA-ZÀ-ÿ_][a-zA-ZÀ-ÿ0-9_]*\b")

        # Rule order matters: later setFormat calls win for overlapping ranges.
        # Identifiers run first so keywords (added next) override them — this
        # gives keywords their blue while leaving user names teal.
        # Strings / comments run last so they win over anything inside them.
        self._rules = [
            # 1. All identifiers (will be overridden at keyword/boolean positions)
            (ident_rx,                                               self.fmt_ident),
            # 2. Reserved words (override the teal set above)
            (kw_rx,                                                  self.fmt_keyword),
            # 3. Boolean literals — gold, clearly a value not a keyword or variable
            (bool_rx,                                                self.fmt_bool),
            # 4. Numbers — float before int
            (QRegularExpression(r"\b\d+\.\d+\b"),                   self.fmt_number),
            (QRegularExpression(r"\b\d+\b"),                        self.fmt_number),
            # 5. String literals (double-quoted, escape sequences supported)
            (QRegularExpression(r'"(?:\\.|[^"\\])*"'),              self.fmt_string),
            # 6. Char literals (single-quoted)
            (QRegularExpression(r"'(?:\\.|[^\\'])'"),               self.fmt_string),
            # 7. Single-line comment — highest priority on its line
            (QRegularExpression(r"#[^\n]*"),                        self.fmt_comment),
        ]

        # Block-comment delimiters (used by the state machine below)
        self._bc_start = QRegularExpression(r"/\*")
        self._bc_end   = QRegularExpression(r"\*/")

    # ------------------------------------------------------------------
    # Core — Qt calls this for every changed block (real-time)
    # ------------------------------------------------------------------

    def highlightBlock(self, text: str):
        # Apply all single-line rules in order
        for pattern, fmt in self._rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                m = it.next()
                self.setFormat(m.capturedStart(), m.capturedLength(), fmt)

        # Block-comment state machine (applied after all rules → highest priority)
        # State 0 = normal code, State 1 = inside /* … */ spanning multiple lines
        self.setCurrentBlockState(0)
        start = 0

        if self.previousBlockState() != 1:
            m = self._bc_start.match(text)
            start = m.capturedStart() if m.hasMatch() else -1

        while start >= 0:
            m_end = self._bc_end.match(text, start)
            if not m_end.hasMatch():
                # Comment continues into the next block
                self.setCurrentBlockState(1)
                self.setFormat(start, len(text) - start, self.fmt_comment)
                break
            length = m_end.capturedStart() + m_end.capturedLength() - start
            self.setFormat(start, length, self.fmt_comment)
            # Check for another /* … on the same line after the closing */
            m_next = self._bc_start.match(text, start + length)
            start = m_next.capturedStart() if m_next.hasMatch() else -1
