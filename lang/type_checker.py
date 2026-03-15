from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from .parser import (
    Program, FunctionDecl, VarDecl, Assign, Call, PrintStmt, ReturnStmt,
    IfStmt, WhileStmt, ForStmt, DoWhileStmt, SwitchStmt, BreakStmt, ContinueStmt,
    ExprBin, ExprUnary, Literal, VarRef, ListLiteral, MapLiteral,
    IndexAccess, IndexAssign, ASTNode
)


class TypeCheckError(Exception):
    pass


@dataclass
class TypeInfo:
    base_type: str
    generic_params: List[str] = field(default_factory=list)
    
    def __str__(self):
        if self.generic_params:
            return f"{self.base_type}<{','.join(self.generic_params)}>"
        return self.base_type
    
    def is_numeric(self):
        return self.base_type in ('bloques', 'coordenada')
    
    def is_comparable(self):
        return self.base_type in ('bloques', 'coordenada', 'texto', 'glifo')


class TypeChecker:
    
    def __init__(self):
        self.variables: Dict[str, TypeInfo] = {}
        self.functions: Dict[str, tuple] = {}
        self.current_function_return_type: Optional[TypeInfo] = None
        self.scope_stack: List[Dict[str, TypeInfo]] = [{}]
        self.errors: List[str] = []
        self._init_builtins()
    
    def _init_builtins(self):
        self.functions['cofre'] = (TypeInfo('texto'), [TypeInfo('texto')])
        self.functions['letrero'] = (TypeInfo('vacío'), [TypeInfo('texto')])
        self.functions['length'] = (TypeInfo('bloques'), [None])
        self.functions['push'] = (TypeInfo('vacío'), [None, None])
        self.functions['pop'] = (None, [None])
        self.functions['tiene'] = (TypeInfo('redstone'), [None, None])
        self.functions['to_bloques'] = (TypeInfo('bloques'), [None])
        self.functions['to_coordenada'] = (TypeInfo('coordenada'), [None])
        self.functions['to_texto'] = (TypeInfo('texto'), [None])
        self.functions['to_redstone'] = (TypeInfo('redstone'), [None])
        self.functions['to_glifo'] = (TypeInfo('glifo'), [None])
    
    def error(self, message: str):
        self.errors.append(message)
    
    def push_scope(self):
        self.scope_stack.append({})
    
    def pop_scope(self):
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()
    
    def declare_variable(self, name: str, type_info: TypeInfo):
        current_scope = self.scope_stack[-1]
        if name in current_scope:
            self.error(f"Variable '{name}' already declared in this scope")
        current_scope[name] = type_info
        self.variables[name] = type_info
    
    def get_variable_type(self, name: str) -> Optional[TypeInfo]:
        for scope in reversed(self.scope_stack):
            if name in scope:
                return scope[name]
        return None
    
    def parse_type_annotation(self, type_str: str) -> TypeInfo:
        if '<' in type_str:
            base = type_str[:type_str.index('<')]
            params_str = type_str[type_str.index('<')+1:type_str.rindex('>')]
            params = [p.strip() for p in params_str.split(',')]
            return TypeInfo(base, params)
        else:
            return TypeInfo(type_str)
    
    def check(self, program: Program) -> bool:
        self.errors = []
        
        main_count = 0
        for decl in program.declarations:
            if isinstance(decl, FunctionDecl):
                if decl.name in self.functions:
                    self.error(f"Function '{decl.name}' declared multiple times")
                
                if decl.name == 'main':
                    main_count += 1
                
                param_types = [self.parse_type_annotation(ptype) for ptype, _ in decl.params]
                return_type = self.parse_type_annotation(decl.return_type)
                self.functions[decl.name] = (return_type, param_types)
        
        if main_count == 0:
            self.error("Function 'main' not found (required and must be unique)")
        elif main_count > 1:
            self.error(f"Function 'main' declared {main_count} times (must be unique)")
        
        for decl in program.declarations:
            if isinstance(decl, FunctionDecl):
                self.check_function(decl)
            elif isinstance(decl, VarDecl):
                self.check_var_decl(decl)
        
        if 'main' in self.functions:
            return_type, param_types = self.functions['main']
            if return_type.base_type != 'vacío':
                self.error(f"main must return 'vacío', not '{return_type}'")
            if len(param_types) > 0:
                self.error(f"main must not have parameters (has {len(param_types)})")
        
        return len(self.errors) == 0
    
    def check_function(self, func: FunctionDecl):
        self.push_scope()
        
        old_return_type = self.current_function_return_type
        self.current_function_return_type = self.parse_type_annotation(func.return_type)
        
        for ptype, pname in func.params:
            param_type = self.parse_type_annotation(ptype)
            self.declare_variable(pname, param_type)
        
        for stmt in func.body:
            self.check_statement(stmt)

        has_return = self._contains_return(func.body)

        if self.current_function_return_type.base_type != 'vacío' and not has_return:
            self.error(f"Function '{func.name}' must return a value of type '{self.current_function_return_type}'")
        
        self.current_function_return_type = old_return_type
        self.pop_scope()
    
    def check_var_decl(self, var: VarDecl):
        declared_type = self.parse_type_annotation(var.var_type)
        expr_type = self.infer_type(var.value)
        
        if expr_type and not self.types_compatible(declared_type, expr_type):
            self.error(f"Variable '{var.name}': tipo declarado '{declared_type}' "
                      f"incompatible con tipo de inicialización '{expr_type}'")
        
        self.declare_variable(var.name, declared_type)
    
    def check_statement(self, stmt: ASTNode):
        if isinstance(stmt, VarDecl):
            self.check_var_decl(stmt)
        
        elif isinstance(stmt, Assign):
            var_type = self.get_variable_type(stmt.name)
            if not var_type:
                self.error(f"Variable '{stmt.name}' no declarada")
                return
            
            expr_type = self.infer_type(stmt.value)
            if expr_type and not self.types_compatible(var_type, expr_type):
                self.error(f"Asignación a '{stmt.name}': tipo '{expr_type}' "
                          f"incompatible con tipo de variable '{var_type}'")
        
        elif isinstance(stmt, IndexAssign):
            self.check_index_assign(stmt)
        
        elif isinstance(stmt, PrintStmt):
            self.infer_type(stmt.expr)
        
        elif isinstance(stmt, ReturnStmt):
            if not self.current_function_return_type:
                self.error("'craftear' outside of a function")
                return
            
            if stmt.expr is None:
                if self.current_function_return_type.base_type != 'vacío':
                    self.error(f"Expected to return '{self.current_function_return_type}', "
                              f"but no value returned")
            else:
                expr_type = self.infer_type(stmt.expr)
                if expr_type and not self.types_compatible(self.current_function_return_type, expr_type):
                    self.error(f"Return type '{expr_type}' incompatible with "
                              f"declared type '{self.current_function_return_type}'")
        
        elif isinstance(stmt, IfStmt):
            for cond, body in stmt.branches:
                if cond is not None:
                    cond_type = self.infer_type(cond)
                    if cond_type and cond_type.base_type != 'redstone':
                        self.error(f"Condition in 'observador/comparador' must be 'redstone', "
                                  f"not '{cond_type}'")
                for s in body:
                    self.check_statement(s)
        
        elif isinstance(stmt, WhileStmt):
            cond_type = self.infer_type(stmt.condition)
            if cond_type and cond_type.base_type != 'redstone':
                self.error(f"Condition in 'spawner' must be 'redstone', not '{cond_type}'")
            for s in stmt.body:
                self.check_statement(s)
        
        elif isinstance(stmt, DoWhileStmt):
            for s in stmt.body:
                self.check_statement(s)
            cond_type = self.infer_type(stmt.condition)
            if cond_type and cond_type.base_type != 'redstone':
                self.error(f"Condition in 'boom' must be 'redstone', not '{cond_type}'")
        
        elif isinstance(stmt, ForStmt):
            self.push_scope()
            if stmt.init:
                self.check_statement(stmt.init)
            if stmt.condition:
                cond_type = self.infer_type(stmt.condition)
                if cond_type and cond_type.base_type != 'redstone':
                    self.error(f"Condition in 'cultivar' must be 'redstone', not '{cond_type}'")
            if stmt.step:
                self.infer_type(stmt.step)
            for s in stmt.body:
                self.check_statement(s)
            self.pop_scope()
        
        elif isinstance(stmt, SwitchStmt):
            switch_type = self.infer_type(stmt.expr)
            for case_val, case_body in stmt.cases:
                if case_val is not None:
                    case_type = self.infer_type(case_val)
                    if switch_type and case_type and not self.types_compatible(switch_type, case_type):
                        self.error(f"Case type '{case_type}' incompatible with "
                                  f"switch expression '{switch_type}'")
                for s in case_body:
                    self.check_statement(s)
        
        elif isinstance(stmt, Call):
            self.infer_type(stmt)
        
        elif isinstance(stmt, (BreakStmt, ContinueStmt)):
            pass
    
    def check_index_assign(self, stmt: IndexAssign):
        if isinstance(stmt.target, VarRef):
            target_type = self.get_variable_type(stmt.target.name)
            if not target_type:
                self.error(f"Variable '{stmt.target.name}' no declarada")
                return
            
            if target_type.base_type == 'inventario':
                index_type = self.infer_type(stmt.index)
                if index_type and index_type.base_type != 'bloques':
                    self.error(f"Inventario index must be 'bloques', not '{index_type}'")
                
                if target_type.generic_params:
                    expected_type = TypeInfo(target_type.generic_params[0])
                    value_type = self.infer_type(stmt.value)
                    if value_type and not self.types_compatible(expected_type, value_type):
                        self.error(f"Value type '{value_type}' incompatible with "
                                  f"inventario type '{expected_type}'")
            
            elif target_type.base_type == 'mapa':
                if target_type.generic_params:
                    key_type_expected = TypeInfo(target_type.generic_params[0])
                    key_type = self.infer_type(stmt.index)
                    if key_type and not self.types_compatible(key_type_expected, key_type):
                        self.error(f"Key type '{key_type}' incompatible with "
                                  f"mapa type '{key_type_expected}'")
                    
                    value_type_expected = TypeInfo(target_type.generic_params[1])
                    value_type = self.infer_type(stmt.value)
                    if value_type and not self.types_compatible(value_type_expected, value_type):
                        self.error(f"Value type '{value_type}' incompatible with "
                                  f"mapa type '{value_type_expected}'")
            else:
                self.error(f"Cannot index type '{target_type}'")
    
    def infer_type(self, expr: Any) -> Optional[TypeInfo]:
        if expr is None:
            return None
        
        if isinstance(expr, Literal):
            val = expr.value
            if isinstance(val, bool):
                return TypeInfo('redstone')
            elif isinstance(val, int):
                return TypeInfo('bloques')
            elif isinstance(val, float):
                return TypeInfo('coordenada')
            elif isinstance(val, str):
                if hasattr(expr, 'literal_type'):
                    if expr.literal_type == 'CHAR':
                        return TypeInfo('glifo')
                    elif expr.literal_type == 'STRING':
                        return TypeInfo('texto')
                if len(val) == 1:
                    return TypeInfo('glifo')
                return TypeInfo('texto')
            return None
        
        elif isinstance(expr, VarRef):
            var_type = self.get_variable_type(expr.name)
            if not var_type:
                self.error(f"Variable '{expr.name}' no declarada")
            return var_type
        
        elif isinstance(expr, ExprBin):
            return self.infer_binary_type(expr)
        
        elif isinstance(expr, ExprUnary):
            return self.infer_unary_type(expr)
        
        elif isinstance(expr, Call):
            return self.infer_call_type(expr)
        
        elif isinstance(expr, ListLiteral):
            return self.infer_list_type(expr)
        
        elif isinstance(expr, MapLiteral):
            return self.infer_map_type(expr)
        
        elif isinstance(expr, IndexAccess):
            return self.infer_index_type(expr)
        
        return None
    
    def infer_binary_type(self, expr: ExprBin) -> Optional[TypeInfo]:
        left_type = self.infer_type(expr.left)
        right_type = self.infer_type(expr.right)
        
        if not left_type or not right_type:
            return None
        
        if expr.op in ('+', '-', '*', '/', '%'):
            if expr.op == '+' and (left_type.base_type == 'texto' or right_type.base_type == 'texto'):
                return TypeInfo('texto')
            
            if not left_type.is_numeric() or not right_type.is_numeric():
                self.error(f"Operator '{expr.op}' requires numeric types, "
                          f"not '{left_type}' and '{right_type}'")
                return None
            
            if left_type.base_type == 'coordenada' or right_type.base_type == 'coordenada':
                return TypeInfo('coordenada')
            return TypeInfo('bloques')
        
        elif expr.op in ('==', '!='):
            return TypeInfo('redstone')
        
        elif expr.op in ('<', '>', '<=', '>='):
            if not left_type.is_comparable() or not right_type.is_comparable():
                self.error(f"Operator '{expr.op}' not supported for types "
                          f"'{left_type}' and '{right_type}'")
                return None
            return TypeInfo('redstone')
        
        elif expr.op in ('y', 'o'):
            if left_type.base_type != 'redstone' or right_type.base_type != 'redstone':
                self.error(f"Operator '{expr.op}' requires 'redstone' types, "
                          f"not '{left_type}' and '{right_type}'")
                return None
            return TypeInfo('redstone')
        
        return None
    
    def infer_unary_type(self, expr: ExprUnary) -> Optional[TypeInfo]:
        operand_type = self.infer_type(expr.operand)
        
        if not operand_type:
            return None
        
        if expr.op == 'no':
            if operand_type.base_type != 'redstone':
                self.error(f"Operador 'no' requiere tipo 'redstone', no '{operand_type}'")
                return None
            return TypeInfo('redstone')
        
        elif expr.op == '-':
            if not operand_type.is_numeric():
                self.error(f"Operador '-' unario requiere tipo numérico, no '{operand_type}'")
                return None
            return operand_type
        
        return None
    
    def infer_call_type(self, call: Call) -> Optional[TypeInfo]:
        if call.callee not in self.functions:
            self.error(f"Function '{call.callee}' not declared")
            return None
        
        return_type, param_types = self.functions[call.callee]
        
        if param_types and None not in param_types:
            if len(call.args) != len(param_types):
                self.error(f"Function '{call.callee}' expects {len(param_types)} arguments, "
                          f"received {len(call.args)}")
        
        for arg in call.args:
            self.infer_type(arg)
        
        return return_type
    
    def infer_list_type(self, expr: ListLiteral) -> Optional[TypeInfo]:
        if not expr.elements:
            return TypeInfo('inventario', ['?'])
        
        first_type = self.infer_type(expr.elements[0])
        if not first_type:
            return None
        
        for elem in expr.elements[1:]:
            elem_type = self.infer_type(elem)
            if elem_type and not self.types_compatible(first_type, elem_type):
                self.error(f"List with inconsistent element types: "
                          f"'{first_type}' and '{elem_type}'")
        
        return TypeInfo('inventario', [str(first_type)])
    
    def infer_map_type(self, expr: MapLiteral) -> Optional[TypeInfo]:
        if not expr.pairs:
            return TypeInfo('mapa', ['?', '?'])
        
        first_key_type = self.infer_type(expr.pairs[0][0])
        first_val_type = self.infer_type(expr.pairs[0][1])
        
        if not first_key_type or not first_val_type:
            return None
        
        for key, val in expr.pairs[1:]:
            key_type = self.infer_type(key)
            val_type = self.infer_type(val)
            
            if key_type and not self.types_compatible(first_key_type, key_type):
                self.error(f"Map with inconsistent key types: "
                          f"'{first_key_type}' and '{key_type}'")
            
            if val_type and not self.types_compatible(first_val_type, val_type):
                self.error(f"Map with inconsistent value types: "
                          f"'{first_val_type}' and '{val_type}'")
        
        return TypeInfo('mapa', [str(first_key_type), str(first_val_type)])
    
    def infer_index_type(self, expr: IndexAccess) -> Optional[TypeInfo]:
        target_type = self.infer_type(expr.target)
        
        if not target_type:
            return None
        
        if target_type.base_type == 'inventario':
            index_type = self.infer_type(expr.index)
            if index_type and index_type.base_type != 'bloques':
                self.error(f"Índice de inventario debe ser 'bloques', no '{index_type}'")
            
            if target_type.generic_params:
                return TypeInfo(target_type.generic_params[0])
            return None
        
        elif target_type.base_type == 'mapa':
            if target_type.generic_params:
                key_type_expected = TypeInfo(target_type.generic_params[0])
                key_type = self.infer_type(expr.index)
                if key_type and not self.types_compatible(key_type_expected, key_type):
                    self.error(f"Tipo de clave '{key_type}' incompatible con '{key_type_expected}'")
                
                return TypeInfo(target_type.generic_params[1])
            return None
        
        else:
            self.error(f"No se puede indexar tipo '{target_type}'")
            return None

    def _contains_return(self, stmts: List[ASTNode]) -> bool:
        for stmt in stmts:
            if isinstance(stmt, ReturnStmt):
                return True

            if isinstance(stmt, IfStmt):
                for _, body in stmt.branches:
                    if self._contains_return(body):
                        return True

            if isinstance(stmt, WhileStmt) or isinstance(stmt, DoWhileStmt) or isinstance(stmt, ForStmt):
                body = getattr(stmt, 'body', None)
                if body and self._contains_return(body):
                    return True

            if isinstance(stmt, SwitchStmt):
                for _, case_body in stmt.cases:
                    if self._contains_return(case_body):
                        return True

        return False
    
    def types_compatible(self, expected: TypeInfo, actual: TypeInfo) -> bool:
        if expected == actual:
            return True
        
        if expected.base_type == 'coordenada' and actual.base_type == 'bloques':
            return True
        
        if '?' in expected.generic_params or '?' in actual.generic_params:
            return True
        
        return False
    
    def print_errors(self):
        if not self.errors:
            print("No se encontraron errores de tipo")
            return
        
        print(f"Se encontraron {len(self.errors)} error(es) de tipo:\n")
        for i, error in enumerate(self.errors, 1):
            print(f"{i}. {error}")
    
    def get_formatted_errors(self):
        if not self.errors:
            return []
        
        formatted = [f"Found {len(self.errors)} type error(s):\n"]
        for i, error in enumerate(self.errors, 1):
            formatted.append(f"{i}. {error}")
        
        return formatted