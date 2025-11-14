import re
from dataclasses import dataclass
from typing import List, Optional

KEYWORDS = {
    'cultivar', 'cosechar', 'observador', 'comparador', 'dispensador',
    'creeper', 'boom', 'portal', 'caso', 'defecto', 'salir_portal',
    'spawner', 'romper', 'mesa_crafteo', 'craftear', 'letrero', 'cofre',
    'verdadero', 'falso', 'bloques', 'coordenada', 'texto',
    'redstone', 'glifo', 'inventario', 'mapa', 'vacío', 'y', 'o', 'no',
    'fin'
}

@dataclass
class Token:
    type: str
    value: Optional[object]
    line: int
    column: int

class Lexer:
    """Regex-based lexer for :JCraft preserving line/column info."""

    token_specification = [
        ('BLOCKCOMMENT', r'/\*[\s\S]*?\*/'),
        ('COMMENT', r'#.*'),
        ('NEWLINE', r'\n'),
        ('SKIP', r'[ \t\r]+'),
        ('STRING', r'"(?:\\.|[^"\\])*"'),
        ('CHAR', r"'(?:\\.|[^\\'])'"),
        ('FLOAT', r'\d+\.\d+'),
        ('INT', r'\d+'),
    ('OP', r'==|!=|<=|>=|\+=|-=|\*=|/=|%=|[+\-*/%=]'),
        ('SEMI', r';'),
        ('COLON', r':'),
        ('COMMA', r','),
        ('LPAREN', r'\('),
        ('RPAREN', r'\)'),
        ('LBRACK', r'\['),
        ('RBRACK', r'\]'),
        ('LBRACE', r'\{'),
        ('RBRACE', r'\}'),
        ('LT', r'<'),
        ('GT', r'>'),
    # identifier: start with a letter (unicode-aware) or underscore, then word chars
    ('ID', r"[^\W\d]\w*"),
        ('MISMATCH', r'.'),
    ]

    def __init__(self, source: str):
        self.source = source
        self.token_regex = '|'.join(f"(?P<{name}>{pattern})" for name, pattern in self.token_specification)

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        line_num = 1
        line_start = 0

        for mo in re.finditer(self.token_regex, self.source):
            kind = mo.lastgroup
            value = mo.group(kind)
            col = mo.start() - line_start + 1

            if kind == 'NEWLINE':
                line_num += 1
                line_start = mo.end()
                continue

            if kind == 'SKIP' or kind == 'COMMENT' or kind == 'BLOCKCOMMENT':
                # update line count for block comments
                if kind == 'BLOCKCOMMENT':
                    line_num += value.count('\n')
                    last_nl = value.rfind('\n')
                    if last_nl >= 0:
                        line_start = mo.start() + last_nl + 1
                continue

            if kind == 'ID':
                low = value.lower()
                if low in KEYWORDS:
                    if low == 'verdadero':
                        tokens.append(Token('BOOL', True, line_num, col))
                        continue
                    if low == 'falso':
                        tokens.append(Token('BOOL', False, line_num, col))
                        continue
                    tokens.append(Token('KEYWORD', low, line_num, col))
                    continue
                tokens.append(Token('IDENT', value, line_num, col))
                continue

            if kind == 'INT':
                tokens.append(Token('INT', int(value), line_num, col))
                continue
            if kind == 'FLOAT':
                tokens.append(Token('FLOAT', float(value), line_num, col))
                continue
            if kind == 'STRING':
                inner = value[1:-1]
                # Solo procesar escapes básicos (\n, \t, etc.) sin destruir UTF-8
                unescaped = inner.replace('\\n', '\n').replace('\\t', '\t').replace('\\\\', '\\').replace('\\"', '"')
                tokens.append(Token('STRING', unescaped, line_num, col))
                continue
            if kind == 'CHAR':
                ch = value[1:-1]
                # Igual para char
                unescaped = ch.replace('\\n', '\n').replace('\\t', '\t').replace('\\\\', '\\').replace("\\'", "'")
                tokens.append(Token('CHAR', unescaped, line_num, col))
                continue
            if kind == 'OP':
                tokens.append(Token('OP', value, line_num, col))
                continue
            if kind in ('SEMI', 'COLON', 'COMMA', 'LPAREN', 'RPAREN', 'LBRACK', 'RBRACK', 'LBRACE', 'RBRACE', 'LT', 'GT'):
                tokens.append(Token(kind, value, line_num, col))
                continue

            if kind == 'MISMATCH':
                raise LexerError(f'Unexpected token {value!r} at {line_num}:{col}')

        return tokens

class LexerError(Exception):
    pass

def tokenize(source: str) -> List[Token]:
    return Lexer(source).tokenize()


if __name__ == '__main__':
    sample = '''
    # ejemplo :JCraft
    mesa_crafteo vacío main():
      bloques vidas = 3;
      letrero "Vidas: " + vidas;
    fin
    '''
    for t in tokenize(sample):
        print(t)

