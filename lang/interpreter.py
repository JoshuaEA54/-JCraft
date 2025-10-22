from typing import Any, Callable, Dict, List, Optional
from .parser import Program, FunctionDecl, VarDecl, Assign, Call, PrintStmt, ReturnStmt, Literal, VarRef, ExprBin, ExprUnary


class InterpreterError(Exception):
    pass


class Interpreter:
    def __init__(self, input_callback: Optional[Callable[[str], str]] = None, debug: bool = False):
        self.variables: Dict[str, Any] = {}
        self.functions: Dict[str, FunctionDecl] = {}
        self.results: List[str] = []
        self.input_callback = input_callback or (lambda prompt: input(prompt))
        self.debug = debug

    def debug_print(self, *args):
        if self.debug:
            print('DEBUG:', *args)

    def run(self, program: Program):
        # collect declarations
        for decl in program.declarations:
            if isinstance(decl, FunctionDecl):
                self.functions[decl.name] = decl
                self.debug_print(f"Defined function {decl.name} (returns {decl.return_type})")
            elif isinstance(decl, VarDecl):
                val = self.evaluate(decl.value)
                self.variables[decl.name] = val
                self.debug_print(f"Global var {decl.name} = {val}")
            else:
                # top-level statement (not allowed by spec) — try to execute
                self.execute_statement(decl)

        # find and call main
        if 'main' not in self.functions:
            raise InterpreterError('main function not found')
        main_fn = self.functions['main']
        # main must be vacío and no params
        if main_fn.params and len(main_fn.params) > 0:
            raise InterpreterError('main must not have parameters')
        # execute main
        self.execute_block(main_fn.body)
        return self.results

    def execute_block(self, stmts: List[Any]):
        for s in stmts:
            rv = self.execute_statement(s)
            if rv is not None:
                return rv
        return None

    def execute_statement(self, stmt: Any):
        # dispatch based on node type
        if isinstance(stmt, PrintStmt):
            val = self.evaluate(stmt.expr)
            out = str(val)
            self.results.append(out)
            self.debug_print('print ->', out)
            return None

        if isinstance(stmt, ReturnStmt):
            val = self.evaluate(stmt.expr) if stmt.expr is not None else None
            self.debug_print('return ->', val)
            return val

        if isinstance(stmt, Call):
            # builtins: letrero, cofre
            if stmt.callee == 'letrero':
                if len(stmt.args) != 1:
                    raise InterpreterError('letrero expects 1 argument')
                val = self.evaluate(stmt.args[0])
                self.results.append(str(val))
                self.debug_print('letrero ->', val)
                return None
            if stmt.callee == 'cofre':
                # cofre() returns texto from input callback
                prompt = ''
                if len(stmt.args) == 1:
                    prompt_val = self.evaluate(stmt.args[0])
                    prompt = str(prompt_val)
                value = self.input_callback(prompt)
                return value
            # user function call
            return self.call_function(stmt.callee, stmt.args)

        if isinstance(stmt, Assign):
            val = self.evaluate(stmt.value)
            self.variables[stmt.name] = val
            self.debug_print(f"assign {stmt.name} = {val}")
            return None

        if isinstance(stmt, VarDecl):
            val = self.evaluate(stmt.value)
            self.variables[stmt.name] = val
            self.debug_print(f"var {stmt.name} = {val}")
            return None

        if isinstance(stmt, FunctionDecl):
            # already handled at top-level, but support nested
            self.functions[stmt.name] = stmt
            self.debug_print(f"function {stmt.name} defined")
            return None

        raise InterpreterError(f'Unknown statement type: {type(stmt)}')

    def call_function(self, name: str, arg_exprs: List[Any]):
        if name not in self.functions:
            raise InterpreterError(f'Function {name} not defined')
        fn: FunctionDecl = self.functions[name]
        # evaluate args
        args = [self.evaluate(e) for e in arg_exprs]
        # check param length
        if len(args) != len(fn.params):
            raise InterpreterError(f'Function {name} expects {len(fn.params)} args, got {len(args)}')
        # setup local scope
        old_vars = self.variables.copy()
        for (ptype, pname), aval in zip(fn.params, args):
            self.variables[pname] = aval
        # execute body
        rv = self.execute_block(fn.body)
        # restore
        self.variables = old_vars
        return rv

    def evaluate(self, expr: Any):
        if expr is None:
            return None
        if isinstance(expr, Literal):
            return expr.value
        if isinstance(expr, VarRef):
            if expr.name not in self.variables:
                raise InterpreterError(f"Variable {expr.name} not defined")
            return self.variables[expr.name]
        if isinstance(expr, Call):
            # Si es una llamada que retorna algo (como cofre o una función con return)
            if expr.callee == 'cofre':
                prompt = ''
                if len(expr.args) == 1:
                    prompt_val = self.evaluate(expr.args[0])
                    prompt = str(prompt_val)
                value = self.input_callback(prompt)
                return value
            return self.call_function(expr.callee, expr.args)
        if isinstance(expr, ExprUnary):
            val = self.evaluate(expr.operand)
            if expr.op == '-':
                return -val
            if expr.op == 'no':
                return not bool(val)
            raise InterpreterError(f'Unknown unary op {expr.op}')
        if isinstance(expr, ExprBin):
            l = self.evaluate(expr.left)
            r = self.evaluate(expr.right)
            op = expr.op
            if op == '+':
                # allow concatenation between strings and other types
                if isinstance(l, str) or isinstance(r, str):
                    return str(l) + str(r)
                return l + r
            if op == '-':
                return l - r
            if op == '*':
                return l * r
            if op == '/':
                return l / r
            if op == '%':
                return l % r
            if op == '==':
                return l == r
            if op == '!=':
                return l != r
            if op == '<':
                return l < r
            if op == '>':
                return l > r
            if op == '<=':
                return l <= r
            if op == '>=':
                return l >= r
            if op in ('y', 'o'):
                if op == 'y':
                    return bool(l) and bool(r)
                return bool(l) or bool(r)
            raise InterpreterError(f'Unknown binary op {op}')

        raise InterpreterError(f'Cannot evaluate expression of type {type(expr)}')


def run_source(source: str, input_callback: Optional[Callable[[str], str]] = None, debug: bool = False):
    from .lexer import tokenize
    from .parser import Parser

    toks = tokenize(source)
    p = Parser(toks)
    prog = p.parse()
    interp = Interpreter(input_callback=input_callback, debug=debug)
    results = interp.run(prog)
    return results


if __name__ == '__main__':
    src = '''
    mesa_crafteo vacío main():
      bloques vidas = 3;
      letrero "Vidas: " + vidas;
    fin
    '''
    out = run_source(src, input_callback=lambda p: 'entrada_demo', debug=True)
    print('RESULTS:', out)
