from dataclasses import dataclass
from typing import List, Optional, Any
from .lexer import Token, tokenize


@dataclass
class ASTNode:
    pass


@dataclass
class Program(ASTNode):
    declarations: List[ASTNode]


@dataclass
class FunctionDecl(ASTNode):
    return_type: str
    name: str
    params: List[tuple]
    body: List[ASTNode]


@dataclass
class VarDecl(ASTNode):
    var_type: str
    name: str
    value: Any


@dataclass
class Assign(ASTNode):
    name: str
    value: Any


@dataclass
class Call(ASTNode):
    callee: str
    args: List[Any]


@dataclass
class PrintStmt(ASTNode):
    expr: Any


@dataclass
class ReturnStmt(ASTNode):
    expr: Optional[Any]


@dataclass
class IfStmt(ASTNode):
    # branches: list of tuples (condition_expr or None for else, body statements list)
    branches: List[tuple]


@dataclass
class ExprBin(ASTNode):
    op: str
    left: Any
    right: Any


@dataclass
class ExprUnary(ASTNode):
    op: str
    operand: Any


@dataclass
class Literal(ASTNode):
    value: Any


@dataclass
class VarRef(ASTNode):
    name: str


class ParserError(Exception):
    pass


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def current(self) -> Optional[Token]:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def advance(self) -> Optional[Token]:
        tok = self.current()
        self.pos += 1
        return tok

    def expect(self, ttype: str, value: Optional[str] = None) -> Token:
        tok = self.current()
        if not tok:
            raise ParserError(f"Expected {ttype} but got EOF")
        if tok.type != ttype:
            raise ParserError(
                f"Expected {ttype} but got {tok.type} at {tok.line}:{tok.column}"
            )
        if value is not None and tok.value != value:
            raise ParserError(
                f"Expected {value} but got {tok.value} at {tok.line}:{tok.column}"
            )
        return self.advance()

    def parse(self) -> Program:
        decls = []
        while self.current() is not None:
            # skip stray newlines if any (lexer doesn't produce NEWLINE tokens except via COMMENTS)
            node = self.parse_declaration()
            if node:
                decls.append(node)
        return Program(decls)

    def parse_declaration(self) -> Optional[ASTNode]:
        tok = self.current()
        if not tok:
            return None

        # function: mesa_crafteo
        if tok.type == "KEYWORD" and tok.value == "mesa_crafteo":
            self.advance()
            # return type
            rt = self._expect_type_token()
            # function name (IDENT expected)
            name_tok = self.expect("IDENT")
            name = name_tok.value
            # params
            self.expect("LPAREN")
            params = self.parse_param_list()
            self.expect("RPAREN")
            self.expect("COLON")
            body = self.parse_block_until("KEYWORD", "fin")
            return FunctionDecl(rt, name, params, body)

        # variable declaration at top-level (only allowed per spec as globals)
        if tok.type == "KEYWORD" and tok.value in (
            "bloques",
            "coordenada",
            "texto",
            "redstone",
            "glifo",
            "inventario",
            "mapa",
        ):
            var_type = tok.value
            self.advance()
            name_tok = self.expect("IDENT")
            name = name_tok.value
            # assignment
            tok2 = self.current()
            if tok2 and tok2.type == "OP" and tok2.value == "=":
                self.advance()
                expr = self.parse_expression()
                # expect semicolon
                self.expect("SEMI")
                return VarDecl(var_type, name, expr)
            else:
                raise ParserError(
                    f"Expected '=' after variable declaration at {tok.line}:{tok.column}"
                )

        # otherwise unexpected at top-level
        raise ParserError(f"Unexpected token {tok} at top-level")

    def _expect_type_token(self) -> str:
        tok = self.current()
        if not tok:
            raise ParserError("Expected type but got EOF")
        if tok.type == "KEYWORD":
            self.advance()
            return tok.value
        raise ParserError(
            f"Expected type keyword but got {tok.type} at {tok.line}:{tok.column}"
        )

    def parse_param_list(self) -> List[tuple]:
        params = []
        if self.current() and self.current().type == "RPAREN":
            return params
        while True:
            # param type (KEYWORD)
            typ = self._expect_type_token()
            # permitir que el nombre sea IDENT o KEYWORD (por si acaso)
            tok = self.current()
            if not tok:
                raise ParserError("Expected parameter name but got EOF")
            if tok.type not in ("IDENT", "KEYWORD"):
                raise ParserError(
                    f"Expected parameter name but got {tok.type} at {tok.line}:{tok.column}"
                )
            name = tok.value
            self.advance()
            params.append((typ, name))
            if self.current() and self.current().type == "COMMA":
                self.advance()
                continue
            break
        return params

    def parse_block_until(self, end_type: str, end_value: str) -> List[ASTNode]:
        stmts: List[ASTNode] = []
        while True:
            tok = self.current()
            if not tok:
                raise ParserError(f"Unterminated block, expected {end_value}")
            if tok.type == end_type and tok.value == end_value:
                # consume end token
                self.advance()
                break
            stmt = self.parse_statement()
            if stmt:
                stmts.append(stmt)
        return stmts

    def parse_statement(self) -> Optional[ASTNode]:
        tok = self.current()
        if not tok:
            return None
        # variable declaration inside a block (e.g. 'bloques x = 1;')
        if tok.type == "KEYWORD" and tok.value in (
            "bloques",
            "coordenada",
            "texto",
            "redstone",
            "glifo",
            "inventario",
            "mapa",
        ):
            var_type = tok.value
            self.advance()
            name_tok = self.expect("IDENT")
            name = name_tok.value
            # assignment required
            self.expect("OP", "=")
            expr = self.parse_expression()
            self.expect("SEMI")
            return VarDecl(var_type, name, expr)

        # letrero <expr> ;
        if tok.type == "KEYWORD" and tok.value == "letrero":
            self.advance()
            expr = self.parse_expression()
            self.expect("SEMI")
            return PrintStmt(expr)

        # Control flow: observador / comparador / dispensador -> multi-branch if
        if tok.type == "KEYWORD" and tok.value in ("observador", "comparador", "dispensador"):
            branches: List[tuple] = []
            # primera rama
            kw = tok.value
            self.advance()
            cond = None
            if kw in ("observador", "comparador"):
                # expect '(' expr ')'
                self.expect("LPAREN")
                cond = self.parse_expression()
                self.expect("RPAREN")
            # expect ':' after header
            self.expect("COLON")

            # parse statements for this branch until next branch keyword or 'fin'
            stmts: List[ASTNode] = []
            while True:
                ntok = self.current()
                if not ntok:
                    raise ParserError("Unterminated if-like block")
                if ntok.type == 'KEYWORD' and ntok.value in ('comparador', 'dispensador', 'fin'):
                    break
                stmt = self.parse_statement()
                if stmt:
                    stmts.append(stmt)
            branches.append((cond, stmts))

            # subsequent branches
            while self.current() and self.current().type == 'KEYWORD' and self.current().value in ('comparador', 'dispensador'):
                kw = self.current().value
                self.advance()
                cond = None
                if kw == 'comparador':
                    self.expect('LPAREN')
                    cond = self.parse_expression()
                    self.expect('RPAREN')
                # expect ':' after header
                self.expect('COLON')
                stmts = []
                while True:
                    ntok = self.current()
                    if not ntok:
                        raise ParserError("Unterminated if-like block")
                    if ntok.type == 'KEYWORD' and ntok.value in ('comparador', 'dispensador', 'fin'):
                        break
                    stmt = self.parse_statement()
                    if stmt:
                        stmts.append(stmt)
                branches.append((cond, stmts))

            # expect 'fin'
            if not (self.current() and self.current().type == 'KEYWORD' and self.current().value == 'fin'):
                raise ParserError("Expected 'fin' to close observador/comparador/dispensador block")
            self.advance()
            return IfStmt(branches)

        # craftear <expr> ;
        if tok.type == "KEYWORD" and tok.value == "craftear":
            self.advance()
            expr = self.parse_expression()
            self.expect("SEMI")
            return ReturnStmt(expr)

        # function call or assignment
        if tok.type in ("IDENT", "KEYWORD"):
            # peek next
            nxt = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
            if nxt and nxt.type == "LPAREN":
                # call
                callee = tok.value
                self.advance()
                self.expect("LPAREN")
                args = self.parse_argument_list()
                self.expect("RPAREN")
                # call as statement must end with semicolon
                if self.current() and self.current().type == "SEMI":
                    self.advance()
                return Call(callee, args)
            elif nxt and nxt.type == "OP" and nxt.value == "=":
                # assignment
                name = tok.value
                self.advance()
                self.expect("OP", "=")
                expr = self.parse_expression()
                self.expect("SEMI")
                return Assign(name, expr)

        raise ParserError(
            f"Unexpected statement starting with {tok.type}({tok.value}) at {tok.line}:{tok.column}"
        )

    def parse_argument_list(self) -> List[Any]:
        args: List[Any] = []
        if self.current() and self.current().type == "RPAREN":
            return args
        while True:
            args.append(self.parse_expression())
            if self.current() and self.current().type == "COMMA":
                self.advance()
                continue
            break
        return args

    # Expression parsing with precedence
    def parse_expression(self) -> Any:
        return self.parse_logic()

    def parse_logic(self):
        node = self.parse_comparison()
        while (
            self.current()
            and self.current().type == "KEYWORD"
            and self.current().value in ("y", "o")
        ):
            op = self.current().value
            self.advance()
            right = self.parse_comparison()
            node = ExprBin(op, node, right)
        return node

    def parse_comparison(self):
        node = self.parse_add()
        while True:
            tok = self.current()
            if tok and (
                (tok.type == 'OP' and tok.value in ('==', '!=', '<', '>', '<=', '>=')) or
                tok.type in ('LT', 'GT')
            ):
                if tok.type in ('LT', 'GT'):
                    op = '<' if tok.type == 'LT' else '>'
                    self.advance()
                else:
                    op = tok.value
                    self.advance()
                right = self.parse_add()
                node = ExprBin(op, node, right)
            else:
                break
        return node

    def parse_add(self):
        node = self.parse_term()
        while self.current() and (
            self.current().type == "OP" and self.current().value in ("+", "-")
        ):
            op = self.current().value
            self.advance()
            right = self.parse_term()
            node = ExprBin(op, node, right)
        return node

    def parse_term(self):
        node = self.parse_unary()
        while self.current() and (
            self.current().type == "OP" and self.current().value in ("*", "/", "%")
        ):
            op = self.current().value
            self.advance()
            right = self.parse_unary()
            node = ExprBin(op, node, right)
        return node

    def parse_unary(self):
        tok = self.current()
        if tok and tok.type == "OP" and tok.value == "-":
            self.advance()
            operand = self.parse_unary()
            return ExprUnary("-", operand)
        if tok and tok.type == "KEYWORD" and tok.value == "no":
            self.advance()
            operand = self.parse_unary()
            return ExprUnary("no", operand)
        return self.parse_primary()

    def parse_primary(self):
        tok = self.current()
        if not tok:
            raise ParserError("Unexpected EOF in expression")
        if tok.type == "INT":
            self.advance()
            return Literal(tok.value)
        if tok.type == "FLOAT":
            self.advance()
            return Literal(tok.value)
        if tok.type == "STRING":
            self.advance()
            return Literal(tok.value)
        if tok.type == "CHAR":
            self.advance()
            return Literal(tok.value)
        if tok.type == "BOOL":
            self.advance()
            return Literal(tok.value)
        if tok.type == "NULL":
            self.advance()
            return Literal(None)
        if tok.type in ("IDENT", "KEYWORD"):
            # could be function call or variable
            name = tok.value
            # peek next
            if (
                self.pos + 1 < len(self.tokens)
                and self.tokens[self.pos + 1].type == "LPAREN"
            ):
                # function call
                self.advance()
                self.expect("LPAREN")
                args = self.parse_argument_list()
                self.expect("RPAREN")
                return Call(name, args)
            else:
                self.advance()
                return VarRef(name)
        if tok.type == "LPAREN":
            self.advance()
            node = self.parse_expression()
            self.expect("RPAREN")
            return node

        raise ParserError(f"Unexpected token in expression: {tok}")


if __name__ == "__main__":
    src = """
    mesa_crafteo vacío main():
      bloques vidas = 3;
      letrero "Vidas: " + vidas;
    fin
    """
    toks = tokenize(src)
    print("TOKENS:", toks)
    p = Parser(toks)
    prog = p.parse()
    print("\nAST:", prog)
