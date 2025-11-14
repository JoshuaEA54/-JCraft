from typing import Any, Callable, Dict, List, Optional
from .parser import (
    Program, FunctionDecl, VarDecl, Assign, Call, PrintStmt, ReturnStmt, 
    Literal, VarRef, ExprBin, ExprUnary, IfStmt, WhileStmt, ForStmt, 
    DoWhileStmt, SwitchStmt, BreakStmt, ContinueStmt, ListLiteral, 
    MapLiteral, IndexAccess, IndexAssign
)
import time


class InterpreterError(Exception):
    pass


class BreakException(Exception):
    """Control flow exception for break statement"""
    pass


class ContinueException(Exception):
    """Control flow exception for continue statement"""
    pass


class LoopLimitExceeded(InterpreterError):
    """Exception raised when a loop exceeds the maximum iteration limit"""
    pass


class Interpreter:
    MAX_LOOP_ITERATIONS = 1_000_000
    
    def __init__(self, input_callback: Optional[Callable[[str], str]] = None, 
                 output_callback: Optional[Callable[[str], None]] = None,
                 stop_callback: Optional[Callable[[], bool]] = None,
                 debug: bool = False):
        self.variables: Dict[str, Any] = {}
        self.functions: Dict[str, FunctionDecl] = {}
        self.results: List[str] = []
        self.input_callback = input_callback or (lambda prompt: input(prompt))
        self.output_callback = output_callback
        self.stop_callback = stop_callback 
        self.debug = debug
        self.output_callback = output_callback  # Callback para enviar outputs en tiempo real
        self._last_output_time = 0
        self._output_throttle = 0.01  # Segundos mínimos entre outputs (10ms)

    def _estimate_loop_iterations(self, init_val, condition, step_val):
        """
        Estimate the number of iterations a for loop will take.
        Returns estimated iterations or None if cannot determine.
        """
        try:
            # Intentar extraer información del bucle for común: i = 0; i < N; i += step
            if not isinstance(init_val, (int, float)):
                return None
            if not isinstance(step_val, (int, float)):
                return None
            
            # Calcular límite basado en la condición
            # Nota: esto es una estimación simplificada
            if step_val == 0:
                return float('inf')  # Bucle infinito
            
            # Si step es negativo y init es menor, será infinito
            # Si step es positivo y la condición no avanza, será infinito
            return None  # No podemos determinar con certeza
        except:
            return None

    def debug_print(self, *args):
        if self.debug:
            print('DEBUG:', *args)

    def _send_output_throttled(self, output: str):
        """Envía output al callback con throttling para evitar saturar la UI"""
        current_time = time.time()
        if current_time - self._last_output_time >= self._output_throttle:
            self.output_callback(output)
            self._last_output_time = current_time
        else:
            # Si estamos emitiendo muy rápido, hacer un pequeño sleep
            time.sleep(self._output_throttle)
            self.output_callback(output)
            self._last_output_time = time.time()

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
            if self.output_callback:
                self._send_output_throttled(out)
            self.debug_print('print ->', out)
            return None

        if isinstance(stmt, ReturnStmt):
            val = self.evaluate(stmt.expr) if stmt.expr is not None else None
            self.debug_print('return ->', val)
            return val

        if isinstance(stmt, Call):
            # builtins: letrero, cofre, length, push, pop, tiene
            if stmt.callee == 'letrero':
                if len(stmt.args) != 1:
                    raise InterpreterError('letrero expects 1 argument')
                val = self.evaluate(stmt.args[0])
                out = str(val)
                self.results.append(out)
                if self.output_callback:
                    self._send_output_throttled(out)
                self.debug_print('letrero ->', val)
                return None
            if stmt.callee == 'cofre':
                # cofre(prompt) returns texto from input callback
                if len(stmt.args) != 1:
                    raise InterpreterError('cofre expects exactly 1 argument (prompt text)')
                prompt_val = self.evaluate(stmt.args[0])
                prompt = str(prompt_val)
                value = self.input_callback(prompt)
                return value
            if stmt.callee == 'push':
                # push(lista, elemento)
                if len(stmt.args) != 2:
                    raise InterpreterError('push expects 2 arguments (list, element)')
                arr = self.evaluate(stmt.args[0])
                val = self.evaluate(stmt.args[1])
                if not isinstance(arr, list):
                    raise InterpreterError('push expects a list as first argument')
                arr.append(val)
                self.debug_print(f'push -> {arr}')
                return None
            if stmt.callee == 'pop':
                # pop(lista) - removes and returns last element
                if len(stmt.args) != 1:
                    raise InterpreterError('pop expects 1 argument (list)')
                arr = self.evaluate(stmt.args[0])
                if not isinstance(arr, list):
                    raise InterpreterError('pop expects a list')
                if len(arr) == 0:
                    raise InterpreterError('pop on empty list')
                val = arr.pop()
                self.debug_print(f'pop -> {val}')
                return val
            # user function call
            return self.call_function(stmt.callee, stmt.args)

        if isinstance(stmt, Assign):
            val = self.evaluate(stmt.value)
            self.variables[stmt.name] = val
            self.debug_print(f"assign {stmt.name} = {val}")
            return None
        
        if isinstance(stmt, IndexAssign):
            # xs[i] = value or m[k] = value
            target = self.evaluate(stmt.target)
            index = self.evaluate(stmt.index)
            value = self.evaluate(stmt.value)
            try:
                target[index] = value
                self.debug_print(f"index assign {target}[{index}] = {value}")
            except (KeyError, IndexError, TypeError) as e:
                raise InterpreterError(f"Index assignment error: {e}")
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

        if isinstance(stmt, IfStmt):
            # branches: list of (cond_expr or None, stmts)
            for cond_expr, body in stmt.branches:
                take = False
                if cond_expr is None:
                    # else branch
                    take = True
                else:
                    val = self.evaluate(cond_expr)
                    take = bool(val)
                if take:
                    rv = self.execute_block(body)
                    return rv
            return None

        if isinstance(stmt, WhileStmt):
            # spawner (cond): ... romper;
            iteration_count = 0
            while True:
                # Verificar si se debe detener
                if self.stop_callback and self.stop_callback():
                    raise InterruptedError("Ejecución detenida por el usuario")
                
                iteration_count += 1
                if iteration_count > self.MAX_LOOP_ITERATIONS:
                    raise LoopLimitExceeded(
                        f'While loop exceeded {self.MAX_LOOP_ITERATIONS:,} iterations'
                    )
                cond_val = self.evaluate(stmt.condition)
                if not bool(cond_val):
                    break
                try:
                    rv = self.execute_block(stmt.body)
                    if rv is not None:
                        return rv
                except BreakException:
                    break
                except ContinueException:
                    continue
            return None

        if isinstance(stmt, ForStmt):
            # cultivar (init; cond; step): ... cosechar;
            # execute init
            if stmt.init:
                self.execute_statement(stmt.init)
            
            # Pre-validación: intentar detectar rangos problemáticos
            try:
                # Verificar la condición inicial
                initial_cond = self.evaluate(stmt.condition)
                
                # Si la condición usa operadores de comparación con literales grandes
                if isinstance(stmt.condition, ExprBin):
                    right_val = self.evaluate(stmt.condition.right)
                    # Detectar límites extremadamente grandes
                    if isinstance(right_val, (int, float)) and abs(right_val) > self.MAX_LOOP_ITERATIONS:
                        # Obtener el valor inicial de la variable del loop
                        if isinstance(stmt.condition.left, VarRef):
                            var_name = stmt.condition.left.name
                            if var_name in self.variables:
                                start_val = self.variables[var_name]
                                if isinstance(start_val, (int, float)):
                                    # Calcular iteraciones estimadas
                                    diff = abs(right_val - start_val)
                                    if diff > self.MAX_LOOP_ITERATIONS:
                                        raise LoopLimitExceeded(
                                            f'For loop range too large: {diff:,} iterations (max: {self.MAX_LOOP_ITERATIONS:,})'
                                        )
            except LoopLimitExceeded:
                raise
            except:
                pass  # No pudimos validar, continuar con ejecución normal
            
            # loop con validación de respaldo
            iteration_count = 0
            while True:
                # Verificar si se debe detener
                if self.stop_callback and self.stop_callback():
                    raise InterruptedError("Ejecución detenida por el usuario")
                
                iteration_count += 1
                if iteration_count > self.MAX_LOOP_ITERATIONS:
                    raise LoopLimitExceeded(
                        f'For loop exceeded {self.MAX_LOOP_ITERATIONS:,} iterations'
                    )
                cond_val = self.evaluate(stmt.condition)
                if not bool(cond_val):
                    break
                try:
                    rv = self.execute_block(stmt.body)
                    if rv is not None:
                        return rv
                except BreakException:
                    break
                except ContinueException:
                    pass  # continue to step
                # execute step (puede ser Assign o expresión)
                if stmt.step:
                    if isinstance(stmt.step, Assign):
                        self.execute_statement(stmt.step)
                    else:
                        self.evaluate(stmt.step)
            return None

        if isinstance(stmt, DoWhileStmt):
            # creeper: ... boom (cond);
            iteration_count = 0
            while True:
                # Verificar si se debe detener
                if self.stop_callback and self.stop_callback():
                    raise InterruptedError("Ejecución detenida por el usuario")
                
                iteration_count += 1
                if iteration_count > self.MAX_LOOP_ITERATIONS:
                    raise LoopLimitExceeded(
                        f'Do-while loop exceeded {self.MAX_LOOP_ITERATIONS:,} iterations'
                    )
                try:
                    rv = self.execute_block(stmt.body)
                    if rv is not None:
                        return rv
                except BreakException:
                    break
                except ContinueException:
                    pass  # continue to condition check
                cond_val = self.evaluate(stmt.condition)
                if not bool(cond_val):
                    break
            return None

        if isinstance(stmt, SwitchStmt):
            # portal (expr): caso ... defecto ... salir_portal;
            switch_val = self.evaluate(stmt.expr)
            matched = False
            try:
                for case_val_expr, case_body in stmt.cases:
                    if case_val_expr is None:
                        # defecto (default)
                        if not matched:
                            rv = self.execute_block(case_body)
                            if rv is not None:
                                return rv
                            matched = True
                    else:
                        case_val = self.evaluate(case_val_expr)
                        if switch_val == case_val:
                            rv = self.execute_block(case_body)
                            if rv is not None:
                                return rv
                            matched = True
                            break  # no fall-through by default
            except BreakException:
                pass  # break out of switch
            return None

        if isinstance(stmt, BreakStmt):
            raise BreakException()

        if isinstance(stmt, ContinueStmt):
            raise ContinueException()

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
        
        if isinstance(expr, ListLiteral):
            # [1, 2, 3] -> Python list
            return [self.evaluate(e) for e in expr.elements]
        
        if isinstance(expr, MapLiteral):
            # {"a": 1, "b": 2} -> Python dict
            return {self.evaluate(k): self.evaluate(v) for k, v in expr.pairs}
        
        if isinstance(expr, IndexAccess):
            # xs[i] or m[k]
            target = self.evaluate(expr.target)
            index = self.evaluate(expr.index)
            try:
                return target[index]
            except (KeyError, IndexError, TypeError) as e:
                raise InterpreterError(f"Index access error: {e}")
        
        if isinstance(expr, Call):
            # Si es una llamada que retorna algo (como cofre o una función con return)
            callee = expr.callee
            
            # === Funciones de conversión de tipo ===
            if callee == 'to_bloques':
                if len(expr.args) != 1:
                    raise InterpreterError('to_bloques expects 1 argument')
                val = self.evaluate(expr.args[0])
                try:
                    return int(val)
                except Exception:
                    raise InterpreterError(f"No se puede convertir '{val}' a bloques")
            
            if callee == 'to_coordenada':
                if len(expr.args) != 1:
                    raise InterpreterError('to_coordenada expects 1 argument')
                val = self.evaluate(expr.args[0])
                try:
                    return float(val)
                except Exception:
                    raise InterpreterError(f"No se puede convertir '{val}' a coordenada")
            
            if callee == 'to_texto':
                if len(expr.args) != 1:
                    raise InterpreterError('to_texto expects 1 argument')
                val = self.evaluate(expr.args[0])
                return str(val)
            
            if callee == 'to_redstone':
                if len(expr.args) != 1:
                    raise InterpreterError('to_redstone expects 1 argument')
                val = self.evaluate(expr.args[0])
                if isinstance(val, str):
                    val_lower = val.lower()
                    if val_lower in ('verdadero', 'true', '1'):
                        return True
                    if val_lower in ('falso', 'false', '0'):
                        return False
                return bool(val)
            
            if callee == 'to_glifo':
                if len(expr.args) != 1:
                    raise InterpreterError('to_glifo expects 1 argument')
                val = self.evaluate(expr.args[0])
                if isinstance(val, str) and len(val) == 1:
                    return val
                raise InterpreterError(f"El valor '{val}' no es un glifo válido (carácter único)")
            
            # === Otras funciones nativas ===
            if callee == 'cofre':
                if len(expr.args) != 1:
                    raise InterpreterError('cofre expects exactly 1 argument (prompt text)')
                prompt_val = self.evaluate(expr.args[0])
                prompt = str(prompt_val)
                value = self.input_callback(prompt)
                return value
            if callee == 'length':
                # length(lista o mapa) -> longitud
                if len(expr.args) != 1:
                    raise InterpreterError('length expects 1 argument')
                val = self.evaluate(expr.args[0])
                if not isinstance(val, (list, dict)):
                    raise InterpreterError('length expects a list or map')
                return len(val)
            if callee == 'tiene':
                # tiene(mapa, clave) -> redstone (bool)
                if len(expr.args) != 2:
                    raise InterpreterError('tiene expects 2 arguments (map, key)')
                m = self.evaluate(expr.args[0])
                k = self.evaluate(expr.args[1])
                if not isinstance(m, dict):
                    raise InterpreterError('tiene expects a map as first argument')
                return k in m
            if callee == 'pop':
                # pop puede usarse como expresión también
                if len(expr.args) != 1:
                    raise InterpreterError('pop expects 1 argument')
                arr = self.evaluate(expr.args[0])
                if not isinstance(arr, list):
                    raise InterpreterError('pop expects a list')
                if len(arr) == 0:
                    raise InterpreterError('pop on empty list')
                return arr.pop()
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


def run_source(source: str, 
               input_callback: Optional[Callable[[str], str]] = None, 
               output_callback: Optional[Callable[[str], None]] = None,
               stop_callback: Optional[Callable[[], bool]] = None,
               debug: bool = False, 
               type_check: bool = True, 
               print_ast: bool = False):
    from .lexer import tokenize
    from .parser import Parser
    from .type_checker import TypeChecker

    toks = tokenize(source)
    p = Parser(toks)
    prog = p.parse()
    
    # Imprimir AST en consola si está habilitado
    if print_ast:
        print("\n" + "="*60)
        print("ÁRBOL SINTÁCTICO ABSTRACTO (AST)")
        print("="*60)
        print(prog)
        print("="*60 + "\n")
    
    # Verificación de tipos estática (si está habilitada)
    if type_check:
        checker = TypeChecker()
        if not checker.check(prog):
            # Retornar los errores formateados en lugar de imprimirlos
            error_messages = checker.get_formatted_errors()
            error_text = "\n".join(error_messages)
            raise InterpreterError(error_text)
    
    interp = Interpreter(input_callback=input_callback, 
                        output_callback=output_callback, 
                        stop_callback=stop_callback,
                        debug=debug)
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
