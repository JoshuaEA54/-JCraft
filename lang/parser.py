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
    branches: List[tuple]


@dataclass
class WhileStmt(ASTNode):
    condition: Any
    body: List[ASTNode]


@dataclass
class ForStmt(ASTNode):
    init: Optional[Any]
    condition: Any
    step: Optional[Any]
    body: List[ASTNode]


@dataclass
class DoWhileStmt(ASTNode):
    body: List[ASTNode]
    condition: Any


@dataclass
class SwitchStmt(ASTNode):
    expr: Any
    cases: List[tuple]


@dataclass
class BreakStmt(ASTNode):
    pass


@dataclass
class ContinueStmt(ASTNode):
    pass


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
    literal_type: Optional[str] = None


@dataclass
class VarRef(ASTNode):
    name: str


@dataclass
class ListLiteral(ASTNode):
    elements: List[Any]


@dataclass
class MapLiteral(ASTNode):
    pairs: List[tuple]


@dataclass
class IndexAccess(ASTNode):
    target: Any
    index: Any


@dataclass
class IndexAssign(ASTNode):
    target: Any
    index: Any
    value: Any


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
            if ttype == "IDENT" and tok.type == "KEYWORD":
                raise ParserError(
                    f"No puedes usar '{tok.value}' como nombre de variable. "
                    f"'{tok.value}' es una palabra reservada del lenguaje. "
                    f"(línea {tok.line}, columna {tok.column})"
                )
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
            node = self.parse_declaration()
            if node:
                decls.append(node)
        return Program(decls)

    def parse_declaration(self) -> Optional[ASTNode]:
        tok = self.current()
        if not tok:
            return None

        if tok.type == "KEYWORD" and tok.value == "mesa_crafteo":
            self.advance()
            rt = self._expect_type_token()
            name_tok = self.expect("IDENT")
            name = name_tok.value
            self.expect("LPAREN")
            params = self.parse_param_list()
            self.expect("RPAREN")
            self.expect("COLON")
            body = self.parse_block_until("KEYWORD", "fin")
            return FunctionDecl(rt, name, params, body)

        if tok.type == "KEYWORD" and tok.value in (
            "bloques",
            "coordenada",
            "texto",
            "redstone",
            "glifo",
            "inventario",
            "mapa",
        ):
            var_type = self._expect_type_token()
            name_tok = self.expect("IDENT")
            name = name_tok.value
            tok2 = self.current()
            if tok2 and tok2.type == "OP" and tok2.value == "=":
                self.advance()
                expr = self.parse_expression()
                self.expect("SEMI")
                return VarDecl(var_type, name, expr)
            else:
                raise ParserError(
                    f"Expected '=' after variable declaration at {tok.line}:{tok.column}"
                )

        raise ParserError(f"Unexpected token {tok} at top-level")

    def _expect_type_token(self) -> str:
        tok = self.current()
        if not tok:
            raise ParserError("Expected type but got EOF")
        if tok.type != "KEYWORD":
            raise ParserError(
                f"Expected type keyword but got {tok.type} at {tok.line}:{tok.column}"
            )
        
        base_type = tok.value
        self.advance()
        
        if self.current() and self.current().type in ("LT", "OP") and \
           (self.current().type == "LT" or self.current().value == "<"):
            
            if base_type not in ("inventario", "mapa"):
                raise ParserError(
                    f"Type '{base_type}' cannot have type parameters at {tok.line}:{tok.column}"
                )
            
            self.advance()
            
            if base_type == "inventario":
                return self._parse_inventario_type(tok.line, tok.column)
            elif base_type == "mapa":
                return self._parse_mapa_type(tok.line, tok.column)
        else:
            if base_type == "inventario":
                raise ParserError(
                    f"Type 'inventario' requires a type parameter: inventario<T> at {tok.line}:{tok.column}"
                )
            elif base_type == "mapa":
                raise ParserError(
                    f"Type 'mapa' requires two type parameters: mapa<K,V> at {tok.line}:{tok.column}"
                )
        
        return base_type
    
    def _parse_inventario_type(self, line: int, column: int) -> str:
        tok = self.current()
        if not tok or tok.type != "KEYWORD":
            raise ParserError(
                f"Expected type parameter for inventario but got {tok.type if tok else 'EOF'} at {line}:{column}"
            )
        
        if tok.value in ("inventario", "mapa"):
            element_type = self._expect_type_token()
        else:
            element_type = tok.value
            self.advance()
        
        if self.current() and self.current().type == "COMMA":
            raise ParserError(
                f"inventario requires exactly 1 type parameter, not 2 at {self.current().line}:{self.current().column}"
            )
        
        tok = self.current()
        if not (tok and (tok.type == "GT" or (tok.type == "OP" and tok.value == ">"))):
            raise ParserError(
                f"Expected '>' to close inventario type at {tok.line if tok else 'EOF'}:{tok.column if tok else 'EOF'}"
            )
        self.advance()
        
        return f"inventario<{element_type}>"
    
    def _parse_mapa_type(self, line: int, column: int) -> str:
        tok = self.current()
        if not tok or tok.type != "KEYWORD":
            raise ParserError(
                f"Expected key type parameter for mapa but got {tok.type if tok else 'EOF'} at {line}:{column}"
            )
        
        if tok.value in ("inventario", "mapa"):
            key_type = self._expect_type_token()
        else:
            key_type = tok.value
            self.advance()
        
        if not (self.current() and self.current().type == "COMMA"):
            raise ParserError(
                f"Expected ',' after key type in mapa at {self.current().line if self.current() else 'EOF'}:{self.current().column if self.current() else 'EOF'}"
            )
        self.advance()
        
        tok = self.current()
        if not tok or tok.type != "KEYWORD":
            raise ParserError(
                f"Expected value type parameter for mapa but got {tok.type if tok else 'EOF'} at {line}:{column}"
            )
        
        if tok.value in ("inventario", "mapa"):
            value_type = self._expect_type_token()
        else:
            value_type = tok.value
            self.advance()
        
        if self.current() and self.current().type == "COMMA":
            raise ParserError(
                f"mapa requires exactly 2 type parameters, not more at {self.current().line}:{self.current().column}"
            )
        
        tok = self.current()
        if not (tok and (tok.type == "GT" or (tok.type == "OP" and tok.value == ">"))):
            raise ParserError(
                f"Expected '>' to close mapa type at {tok.line if tok else 'EOF'}:{tok.column if tok else 'EOF'}"
            )
        self.advance()
        
        return f"mapa<{key_type},{value_type}>"

    def parse_param_list(self) -> List[tuple]:
        params = []
        if self.current() and self.current().type == "RPAREN":
            return params
        while True:
            typ = self._expect_type_token()
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

        if tok.type == "KEYWORD" and tok.value in (
            "bloques",
            "coordenada",
            "texto",
            "redstone",
            "glifo",
            "inventario",
            "mapa",
        ):
            var_type = self._expect_type_token()
            name_tok = self.expect("IDENT")
            name = name_tok.value
            self.expect("OP", "=")
            expr = self.parse_expression()
            self.expect("SEMI")
            return VarDecl(var_type, name, expr)

        if tok.type == "KEYWORD" and tok.value == "letrero":
            self.advance()
            expr = self.parse_expression()
            self.expect("SEMI")
            return PrintStmt(expr)

        if tok.type == "KEYWORD" and tok.value in ("comparador", "dispensador"):
            raise ParserError(f"'{tok.value}' without preceding 'observador' at {tok.line}:{tok.column}")

        if tok.type == "KEYWORD" and tok.value == "observador":
            branches: List[tuple] = []
            self.advance()
            self.expect("LPAREN")
            cond = self.parse_expression()
            self.expect("RPAREN")
            self.expect("COLON")

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

            while self.current() and self.current().type == 'KEYWORD' and self.current().value in ('comparador', 'dispensador'):
                kw = self.current().value
                self.advance()
                cond = None
                if kw == 'comparador':
                    self.expect('LPAREN')
                    cond = self.parse_expression()
                    self.expect('RPAREN')
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
                
                if kw == 'dispensador':
                    break

            if not (self.current() and self.current().type == 'KEYWORD' and self.current().value == 'fin'):
                raise ParserError("Expected 'fin' to close observador/comparador/dispensador block")
            self.advance()
            return IfStmt(branches)

        if tok.type == "KEYWORD" and tok.value == "spawner":
            self.advance()
            self.expect("LPAREN")
            cond = self.parse_expression()
            self.expect("RPAREN")
            self.expect("COLON")
            body = self.parse_block_until("KEYWORD", "romper")
            return WhileStmt(cond, body)

        if tok.type == "KEYWORD" and tok.value == "cultivar":
            self.advance()
            self.expect("LPAREN")
            init_tok = self.current()
            init_stmt = None
            if init_tok and init_tok.type == "KEYWORD" and init_tok.value in ("bloques", "coordenada", "texto", "redstone", "glifo", "inventario", "mapa"):
                var_type = init_tok.value
                self.advance()
                name_tok = self.expect("IDENT")
                self.expect("OP", "=")
                expr = self.parse_expression()
                init_stmt = VarDecl(var_type, name_tok.value, expr)
            elif init_tok and init_tok.type == "IDENT":
                name = init_tok.value
                self.advance()
                self.expect("OP", "=")
                expr = self.parse_expression()
                init_stmt = Assign(name, expr)
            self.expect("SEMI")
            cond = self.parse_expression()
            self.expect("SEMI")
            step_tok = self.current()
            step_stmt = None
            if step_tok and step_tok.type == "IDENT":
                peek = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
                if peek and peek.type == "OP" and peek.value == "=":
                    name = step_tok.value
                    self.advance()
                    self.expect("OP", "=")
                    expr = self.parse_expression()
                    step_stmt = Assign(name, expr)
                else:
                    step_stmt = self.parse_expression()
            else:
                step_stmt = self.parse_expression()
            self.expect("RPAREN")
            self.expect("COLON")
            body = self.parse_block_until("KEYWORD", "cosechar")
            return ForStmt(init_stmt, cond, step_stmt, body)

        if tok.type == "KEYWORD" and tok.value == "creeper":
            self.advance()
            self.expect("COLON")
            body: List[ASTNode] = []
            while True:
                ntok = self.current()
                if not ntok:
                    raise ParserError("Unterminated creeper block, expected 'boom'")
                if ntok.type == "KEYWORD" and ntok.value == "boom":
                    break
                stmt = self.parse_statement()
                if stmt:
                    body.append(stmt)
            self.advance()
            self.expect("LPAREN")
            cond = self.parse_expression()
            self.expect("RPAREN")
            self.expect("SEMI")
            return DoWhileStmt(body, cond)

        if tok.type == "KEYWORD" and tok.value == "portal":
            self.advance()
            self.expect("LPAREN")
            switch_expr = self.parse_expression()
            self.expect("RPAREN")
            self.expect("COLON")
            cases: List[tuple] = []
            while True:
                ntok = self.current()
                if not ntok:
                    raise ParserError("Unterminated portal block, expected 'salir_portal'")
                if ntok.type == "KEYWORD" and ntok.value == "salir_portal":
                    break
                if ntok.type == "KEYWORD" and ntok.value == "caso":
                    self.advance()
                    case_val = self.parse_expression()
                    self.expect("COLON")
                    case_body: List[ASTNode] = []
                    while True:
                        peek = self.current()
                        if not peek:
                            raise ParserError("Unterminated caso block")
                        if peek.type == "KEYWORD" and peek.value in ("caso", "defecto", "salir_portal"):
                            break
                        stmt = self.parse_statement()
                        if stmt:
                            case_body.append(stmt)
                    cases.append((case_val, case_body))
                elif ntok.type == "KEYWORD" and ntok.value == "defecto":
                    self.advance()
                    self.expect("COLON")
                    default_body: List[ASTNode] = []
                    while True:
                        peek = self.current()
                        if not peek:
                            raise ParserError("Unterminated defecto block")
                        if peek.type == "KEYWORD" and peek.value in ("caso", "salir_portal"):
                            break
                        stmt = self.parse_statement()
                        if stmt:
                            default_body.append(stmt)
                    cases.append((None, default_body))
                else:
                    raise ParserError(f"Expected 'caso' or 'defecto' in portal block at {ntok.line}:{ntok.column}")
            self.advance()
            return SwitchStmt(switch_expr, cases)

        if tok.type == "KEYWORD" and tok.value == "craftear":
            self.advance()
            expr = self.parse_expression()
            self.expect("SEMI")
            return ReturnStmt(expr)

        if tok.type in ("IDENT", "KEYWORD"):
            nxt = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
            
            if nxt and nxt.type == "LBRACK":
                name = tok.value
                self.advance()
                self.expect("LBRACK")
                index_expr = self.parse_expression()
                self.expect("RBRACK")
                
                op_tok = self.current()
                if not (op_tok and op_tok.type == "OP" and op_tok.value in ("=", "+=", "-=", "*=", "/=", "%=")):
                    raise ParserError(f"Expected assignment operator after index at {op_tok.line}:{op_tok.column}")
                
                op = op_tok.value
                self.advance()
                value_expr = self.parse_expression()
                self.expect("SEMI")
                
                if op in ("+=", "-=", "*=", "/=", "%="):
                    base_op = op[0]
                    value_expr = ExprBin(base_op, IndexAccess(VarRef(name), index_expr), value_expr)
                
                return IndexAssign(VarRef(name), index_expr, value_expr)
            
            if nxt and nxt.type == "LPAREN":
                if tok.value == "romper":
                    self.advance()
                    self.expect("LPAREN")
                    self.expect("RPAREN")
                    self.expect("SEMI")
                    return BreakStmt()
                elif tok.value == "continuar":
                    self.advance()
                    self.expect("LPAREN")
                    self.expect("RPAREN")
                    self.expect("SEMI")
                    return ContinueStmt()
                else:
                    callee = tok.value
                    self.advance()
                    self.expect("LPAREN")
                    args = self.parse_argument_list()
                    self.expect("RPAREN")
                    if self.current() and self.current().type == "SEMI":
                        self.advance()
                    return Call(callee, args)
            elif nxt and nxt.type == "OP" and nxt.value in ("=", "+=", "-=", "*=", "/=", "%="):
                name = tok.value
                self.advance()
                op_tok = self.current()
                op = op_tok.value
                self.advance()
                expr = self.parse_expression()
                self.expect("SEMI")
                
                if op in ("+=", "-=", "*=", "/=", "%="):
                    base_op = op[0]
                    expr = ExprBin(base_op, VarRef(name), expr)
                
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
        return self.parse_postfix()
    
    def parse_postfix(self):
        node = self.parse_primary()
        while self.current() and self.current().type == "LBRACK":
            self.advance()
            index_expr = self.parse_expression()
            self.expect("RBRACK")
            node = IndexAccess(node, index_expr)
        return node

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
            return Literal(tok.value, literal_type='STRING')
        if tok.type == "CHAR":
            self.advance()
            return Literal(tok.value, literal_type='CHAR')
        if tok.type == "BOOL":
            self.advance()
            return Literal(tok.value)
        if tok.type in ("IDENT", "KEYWORD"):
            name = tok.value
            if (
                self.pos + 1 < len(self.tokens)
                and self.tokens[self.pos + 1].type == "LPAREN"
            ):
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
        
        if tok.type == "LBRACK":
            self.advance()
            elements = []
            if not (self.current() and self.current().type == "RBRACK"):
                while True:
                    elements.append(self.parse_expression())
                    if self.current() and self.current().type == "COMMA":
                        self.advance()
                        continue
                    break
            self.expect("RBRACK")
            return ListLiteral(elements)
        
        if tok.type == "LBRACE":
            self.advance()
            pairs = []
            if not (self.current() and self.current().type == "RBRACE"):
                while True:
                    key = self.parse_expression()
                    self.expect("COLON")
                    value = self.parse_expression()
                    pairs.append((key, value))
                    if self.current() and self.current().type == "COMMA":
                        self.advance()
                        continue
                    break
            self.expect("RBRACE")
            return MapLiteral(pairs)

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