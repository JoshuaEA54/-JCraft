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
class WhileStmt(ASTNode):
    # spawner (cond): ... romper;
    condition: Any
    body: List[ASTNode]


@dataclass
class ForStmt(ASTNode):
    # cultivar (init; cond; step): ... cosechar;
    init: Optional[Any]  # puede ser VarDecl o Assign
    condition: Any
    step: Optional[Any]  # expresión de incremento
    body: List[ASTNode]


@dataclass
class DoWhileStmt(ASTNode):
    # creeper: ... boom (cond);
    body: List[ASTNode]
    condition: Any


@dataclass
class SwitchStmt(ASTNode):
    # portal (expr): caso val: ... caso val: ... defecto: ... salir_portal;
    expr: Any
    cases: List[tuple]  # (value_expr or None for default, body statements)


@dataclass
class BreakStmt(ASTNode):
    # romper(); -> break
    pass


@dataclass
class ContinueStmt(ASTNode):
    # continuar(); -> continue
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


@dataclass
class VarRef(ASTNode):
    name: str


@dataclass
class ListLiteral(ASTNode):
    # inventario<T>: [1, 2, 3]
    elements: List[Any]


@dataclass
class MapLiteral(ASTNode):
    # mapa<K,V>: {"a": 1, "b": 2}
    pairs: List[tuple]  # list of (key_expr, value_expr)


@dataclass
class IndexAccess(ASTNode):
    # xs[i] or m[k]
    target: Any
    index: Any


@dataclass
class IndexAssign(ASTNode):
    # xs[i] = value or m[k] = value
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
            var_type = self._expect_type_token()  # Esto ahora maneja genéricos
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
        """
        Parse a type, including generics like inventario<bloques> or mapa<texto,bloques>
        Returns the full type string like "inventario<bloques>"
        """
        tok = self.current()
        if not tok:
            raise ParserError("Expected type but got EOF")
        if tok.type == "KEYWORD":
            base_type = tok.value
            self.advance()
            
            # Check for generic type: inventario<T> or mapa<K,V>
            if self.current() and self.current().type in ("LT", "OP") and \
               (self.current().type == "LT" or self.current().value == "<"):
                self.advance()  # consume <
                
                # Parse first type parameter (simple type only, no nested generics)
                tok = self.current()
                if not tok or tok.type != "KEYWORD":
                    raise ParserError(f"Expected type parameter but got {tok.type if tok else 'EOF'}")
                type_param1 = tok.value
                self.advance()
                
                type_params = [type_param1]
                
                # Check for second type parameter (for mapa<K,V>)
                if self.current() and self.current().type == "COMMA":
                    self.advance()
                    tok = self.current()
                    if not tok or tok.type != "KEYWORD":
                        raise ParserError(f"Expected second type parameter but got {tok.type if tok else 'EOF'}")
                    type_param2 = tok.value
                    self.advance()
                    type_params.append(type_param2)
                
                # Expect >
                tok = self.current()
                if tok and (tok.type == "GT" or (tok.type == "OP" and tok.value == ">")):
                    self.advance()
                else:
                    raise ParserError(f"Expected '>' to close generic type at {tok.line if tok else 'EOF'}")
                
                # Build full type string
                return f"{base_type}<{','.join(type_params)}>"
            
            return base_type
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
        # variable declaration inside a block (e.g. 'bloques x = 1;' or 'inventario<bloques> xs = [1,2];')
        if tok.type == "KEYWORD" and tok.value in (
            "bloques",
            "coordenada",
            "texto",
            "redstone",
            "glifo",
            "inventario",
            "mapa",
        ):
            var_type = self._expect_type_token()  # Maneja genéricos
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

        # spawner (cond): ... romper; -> while loop
        if tok.type == "KEYWORD" and tok.value == "spawner":
            self.advance()
            self.expect("LPAREN")
            cond = self.parse_expression()
            self.expect("RPAREN")
            self.expect("COLON")
            body = self.parse_block_until("KEYWORD", "romper")
            return WhileStmt(cond, body)

        # cultivar (init; cond; step): ... cosechar; -> for loop
        if tok.type == "KEYWORD" and tok.value == "cultivar":
            self.advance()
            self.expect("LPAREN")
            # init: puede ser VarDecl o Assign
            init_tok = self.current()
            init_stmt = None
            if init_tok and init_tok.type == "KEYWORD" and init_tok.value in ("bloques", "coordenada", "texto", "redstone", "glifo", "inventario", "mapa"):
                # VarDecl sin semicolon
                var_type = init_tok.value
                self.advance()
                name_tok = self.expect("IDENT")
                self.expect("OP", "=")
                expr = self.parse_expression()
                init_stmt = VarDecl(var_type, name_tok.value, expr)
            elif init_tok and init_tok.type == "IDENT":
                # Assign sin semicolon
                name = init_tok.value
                self.advance()
                self.expect("OP", "=")
                expr = self.parse_expression()
                init_stmt = Assign(name, expr)
            # expect ';'
            self.expect("SEMI")
            # condition
            cond = self.parse_expression()
            self.expect("SEMI")
            # step: puede ser Assign (i = i + 1) o expresión simple (i++)
            step_tok = self.current()
            step_stmt = None
            if step_tok and step_tok.type == "IDENT":
                # peek para ver si es asignación
                peek = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
                if peek and peek.type == "OP" and peek.value == "=":
                    # Assign
                    name = step_tok.value
                    self.advance()
                    self.expect("OP", "=")
                    expr = self.parse_expression()
                    step_stmt = Assign(name, expr)
                else:
                    # expresión simple
                    step_stmt = self.parse_expression()
            else:
                step_stmt = self.parse_expression()
            self.expect("RPAREN")
            self.expect("COLON")
            body = self.parse_block_until("KEYWORD", "cosechar")
            return ForStmt(init_stmt, cond, step_stmt, body)

        # creeper: ... boom (cond); -> do-while loop
        if tok.type == "KEYWORD" and tok.value == "creeper":
            self.advance()
            self.expect("COLON")
            # parse body until 'boom'
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
            # consume 'boom'
            self.advance()
            self.expect("LPAREN")
            cond = self.parse_expression()
            self.expect("RPAREN")
            self.expect("SEMI")
            return DoWhileStmt(body, cond)

        # portal (expr): caso ... defecto ... salir_portal; -> switch-case
        if tok.type == "KEYWORD" and tok.value == "portal":
            self.advance()
            self.expect("LPAREN")
            switch_expr = self.parse_expression()
            self.expect("RPAREN")
            self.expect("COLON")
            # parse cases
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
                    # parse statements until next 'caso', 'defecto', or 'salir_portal'
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
            # consume 'salir_portal'
            self.advance()
            return SwitchStmt(switch_expr, cases)

        # craftear <expr> ;
        if tok.type == "KEYWORD" and tok.value == "craftear":
            self.advance()
            expr = self.parse_expression()
            self.expect("SEMI")
            return ReturnStmt(expr)

        # function call or assignment (includes romper() and continuar())
        if tok.type in ("IDENT", "KEYWORD"):
            # peek next
            nxt = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
            
            # Check for index assignment: xs[i] = value or xs[i] += value
            if nxt and nxt.type == "LBRACK":
                name = tok.value
                self.advance()
                self.expect("LBRACK")
                index_expr = self.parse_expression()
                self.expect("RBRACK")
                
                # Check for = or compound assignment operator
                op_tok = self.current()
                if not (op_tok and op_tok.type == "OP" and op_tok.value in ("=", "+=", "-=", "*=", "/=", "%=")):
                    raise ParserError(f"Expected assignment operator after index at {op_tok.line}:{op_tok.column}")
                
                op = op_tok.value
                self.advance()
                value_expr = self.parse_expression()
                self.expect("SEMI")
                
                # Transform compound assignments: xs[i] += 1 -> xs[i] = xs[i] + 1
                if op in ("+=", "-=", "*=", "/=", "%="):
                    base_op = op[0]  # Extract '+', '-', '*', '/', '%'
                    value_expr = ExprBin(base_op, IndexAccess(VarRef(name), index_expr), value_expr)
                
                return IndexAssign(VarRef(name), index_expr, value_expr)
            
            if nxt and nxt.type == "LPAREN":
                # check if it's romper() or continuar()
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
                    # regular function call
                    callee = tok.value
                    self.advance()
                    self.expect("LPAREN")
                    args = self.parse_argument_list()
                    self.expect("RPAREN")
                    # call as statement must end with semicolon
                    if self.current() and self.current().type == "SEMI":
                        self.advance()
                    return Call(callee, args)
            elif nxt and nxt.type == "OP" and nxt.value in ("=", "+=", "-=", "*=", "/=", "%="):
                # assignment or compound assignment
                name = tok.value
                self.advance()
                op_tok = self.current()
                op = op_tok.value
                self.advance()
                expr = self.parse_expression()
                self.expect("SEMI")
                
                # Transform compound assignments: x += 1 -> x = x + 1
                if op in ("+=", "-=", "*=", "/=", "%="):
                    base_op = op[0]  # Extract '+', '-', '*', '/', '%'
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
        return self.parse_postfix()
    
    def parse_postfix(self):
        """Parse postfix operators like indexación: xs[0], m["key"]"""
        node = self.parse_primary()
        # Soporte para indexación postfix
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
        
        # Lista literal: [1, 2, 3]
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
        
        # Mapa literal: {"clave": valor, "otra": valor2}
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
