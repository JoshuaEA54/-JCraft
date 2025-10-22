import re
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class Token:
	type: str
	value: Optional[str]
	line: int
	column: int

	def __repr__(self) -> str:
		return f"Token({self.type!r}, {self.value!r}, {self.line}, {self.column})"


class LexerError(Exception):
	pass


class Lexer:
	"""Lexer for the :JCraft language.

	Produces a list of Token(type, value, line, column).
	"""

	# Keywords from the language specification
	KEYWORDS = {
		'cultivar', 'cosechar', 'observador', 'comparador', 'dispensador',
		'creeper', 'boom', 'portal', 'caso', 'defecto', 'salir_portal',
		'spawner', 'romper', 'mesa_crafteo', 'craftear', 'letrero', 'cofre',
		'verdadero', 'falso', 'nulo', 'bloques', 'coordenada', 'texto',
		'redstone', 'glifo', 'inventario', 'mapa', 'vacío', 'y', 'o', 'no'
	}

	SIMPLE_TOKENS = {
		';': 'SEMI', ':': 'COLON', '(': 'LPAREN', ')': 'RPAREN',
		'[': 'LBRACK', ']': 'RBRACK', '{': 'LBRACE', '}': 'RBRACE',
		',': 'COMMA', '<': 'LT', '>': 'GT'
	}

	OPERATORS = {
		'==', '!=', '<=', '>=', '+', '-', '*', '/', '%', '=', '+=', '-=', '*=', '/=', '%='
	import re
	from dataclasses import dataclass
	from typing import List, Optional


	@dataclass
	class Token:
		type: str
		value: Optional[object]
		line: int
		column: int

		def __repr__(self) -> str:
			return f"Token({self.type!r}, {self.value!r}, {self.line}, {self.column})"


	class LexerError(Exception):
		pass


	KEYWORDS = {
		'cultivar', 'cosechar', 'observador', 'comparador', 'dispensador',
		'creeper', 'boom', 'portal', 'caso', 'defecto', 'salir_portal',
		'spawner', 'romper', 'mesa_crafteo', 'craftear', 'letrero', 'cofre',
		'verdadero', 'falso', 'nulo', 'bloques', 'coordenada', 'texto',
		'redstone', 'glifo', 'inventario', 'mapa', 'vacío', 'y', 'o', 'no',
		'fin'
	}


	class Lexer:
		"""Regex-based lexer for :JCraft preserving line/column info."""

		token_specification = [
			('BLOCKCOMMENT', r'/\*[\s\S]*?\*/'),
			('COMMENT', r'#.*'),
			('NEWLINE', r'\n'),
			('SKIP', r'[ \t\r]+'),
			('STRING', r'"(?:\\.|[^"\\])*"'),
			('CHAR', r'\'(?:\\.|[^\\'])\''),
			('FLOAT', r'\d+\.\d+'),
			('INT', r'\d+'),
			('OP', r'==|!=|<=|>=|\+=|-=|\*=|/=|%='),
			('OP', r'[+\-*/%=]'),
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
			('ID', r'[A-Za-z_][A-Za-z0-9_]*'),
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
						# line_start moved to last newline
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
						if low == 'nulo':
							tokens.append(Token('NULL', None, line_num, col))
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
					# strip quotes and unescape
					inner = value[1:-1]
					try:
						unescaped = bytes(inner, 'utf-8').decode('unicode_escape')
					except Exception:
						unescaped = inner
					tokens.append(Token('STRING', unescaped, line_num, col))
					continue
				if kind == 'CHAR':
					ch = value[1:-1]
					try:
						unescaped = bytes(ch, 'utf-8').decode('unicode_escape')
					except Exception:
						unescaped = ch
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
			raise LexerError(f"Unexpected character {ch!r} at {start_line}:{start_col}")


