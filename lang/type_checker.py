"""
Type Checker for JCraft
Validates types statically before execution
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from .parser import (
    Program, FunctionDecl, VarDecl, Assign, Call, PrintStmt, ReturnStmt,
    IfStmt, WhileStmt, ForStmt, DoWhileStmt, SwitchStmt, BreakStmt, ContinueStmt,
    ExprBin, ExprUnary, Literal, VarRef, ListLiteral, MapLiteral,
    IndexAccess, IndexAssign, ASTNode
)


class TypeCheckError(Exception):
    """Type validation error"""
    pass


@dataclass
class TypeInfo:
    """Type information for an expression"""
    base_type: str  # 'bloques', 'texto', 'inventario', 'mapa', etc.
    generic_params: List[str] = field(default_factory=list)  # For inventario<T> or mapa<K,V>
    
    
    def __str__(self):
        if self.generic_params:
            return f"{self.base_type}<{','.join(self.generic_params)}>"
        return self.base_type
    
    def is_numeric(self):
        """Check if type is numeric"""
        return self.base_type in ('bloques', 'coordenada')
    
    def is_comparable(self):
        """Check if type can be used in comparisons"""
        return self.base_type in ('bloques', 'coordenada', 'texto', 'glifo')


class TypeChecker:
    """Static type validator for JCraft"""
    
    def __init__(self):
        # Symbol table: name -> TypeInfo
        self.variables: Dict[str, TypeInfo] = {}
        # Functions: name -> (return_type, [param_types])
        self.functions: Dict[str, tuple] = {}
        # Current function context (to validate return)
        self.current_function_return_type: Optional[TypeInfo] = None
        # Scope stack for local variables
        self.scope_stack: List[Dict[str, TypeInfo]] = [{}]
        # Error counter
        self.errors: List[str] = []
        
        # Built-in functions
        self._init_builtins()
    
    def _init_builtins(self):
        """Initialize built-in functions"""
        # cofre(texto) : texto - requires prompt parameter
        self.functions['cofre'] = (TypeInfo('texto'), [TypeInfo('texto')])
        
        # letrero(expr) : vacío
        self.functions['letrero'] = (TypeInfo('vacío'), [TypeInfo('texto')])  # Accepts anything
        
        # length(collection) : bloques
        self.functions['length'] = (TypeInfo('bloques'), [None])  # Accepts collections
        
        # push(inventario<T>, T) : vacío
        self.functions['push'] = (TypeInfo('vacío'), [None, None])
        
        # pop(inventario<T>) : T
        self.functions['pop'] = (None, [None])  # Return type depends on argument
        
        # tiene(mapa<K,V>, K) : redstone
        self.functions['tiene'] = (TypeInfo('redstone'), [None, None])
        
        # Conversions
        self.functions['to_bloques'] = (TypeInfo('bloques'), [None])
        self.functions['to_coordenada'] = (TypeInfo('coordenada'), [None])
        self.functions['to_texto'] = (TypeInfo('texto'), [None])
        self.functions['to_redstone'] = (TypeInfo('redstone'), [None])
        self.functions['to_glifo'] = (TypeInfo('glifo'), [None])
    
    def error(self, message: str):
        """Register a type error"""
        self.errors.append(message)
    
    def push_scope(self):
        """Create a new scope for local variables"""
        self.scope_stack.append({})
    
    def pop_scope(self):
        """Exit current scope"""
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()
    
    def declare_variable(self, name: str, type_info: TypeInfo):
        """Declare a variable in current scope"""
        current_scope = self.scope_stack[-1]
        if name in current_scope:
            self.error(f"Variable '{name}' already declared in this scope")
        current_scope[name] = type_info
        # Also in global table for easy access
        self.variables[name] = type_info
    
    def get_variable_type(self, name: str) -> Optional[TypeInfo]:
        """Get the type of a variable"""
        # Search from innermost to outermost scope
        for scope in reversed(self.scope_stack):
            if name in scope:
                return scope[name]
        return None
    
    def parse_type_annotation(self, type_str: str) -> TypeInfo:
        """Parse a type annotation like 'inventario<bloques>' or 'mapa<texto,bloques>'"""
        if '<' in type_str:
            # Generic type
            base = type_str[:type_str.index('<')]
            params_str = type_str[type_str.index('<')+1:type_str.rindex('>')]
            params = [p.strip() for p in params_str.split(',')]
            return TypeInfo(base, params)
        else:
            return TypeInfo(type_str)
    
    def check(self, program: Program) -> bool:
        """
        Check types of the entire program.
        Returns True if no errors, False if there are errors.
        """
        self.errors = []
        
        # First pass: collect function declarations
        main_count = 0
        for decl in program.declarations:
            if isinstance(decl, FunctionDecl):
                # Check for duplicate functions
                if decl.name in self.functions:
                    self.error(f"Function '{decl.name}' declared multiple times")
                
                # Count mains
                if decl.name == 'main':
                    main_count += 1
                
                param_types = [self.parse_type_annotation(ptype) for ptype, _ in decl.params]
                return_type = self.parse_type_annotation(decl.return_type)
                self.functions[decl.name] = (return_type, param_types)
        
        # Verify main is unique
        if main_count == 0:
            self.error("Function 'main' not found (required and must be unique)")
        elif main_count > 1:
            self.error(f"Function 'main' declared {main_count} times (must be unique)")
        
        # Second pass: check function bodies and global variables
        for decl in program.declarations:
            if isinstance(decl, FunctionDecl):
                self.check_function(decl)
            elif isinstance(decl, VarDecl):
                self.check_var_decl(decl)
        
        # Verify main signature (if exists)
        if 'main' in self.functions:
            return_type, param_types = self.functions['main']
            if return_type.base_type != 'vacío':
                self.error(f"main must return 'vacío', not '{return_type}'")
            if len(param_types) > 0:
                self.error(f"main must not have parameters (has {len(param_types)})")
        
        return len(self.errors) == 0
    
    def check_function(self, func: FunctionDecl):
        """Check function body"""
        # New scope for parameters and local variables
        self.push_scope()
        
        # Save expected return type
        old_return_type = self.current_function_return_type
        self.current_function_return_type = self.parse_type_annotation(func.return_type)
        
        # Declare parameters
        for ptype, pname in func.params:
            param_type = self.parse_type_annotation(ptype)
            self.declare_variable(pname, param_type)
        
        # Check body
        has_return = False
        for stmt in func.body:
            self.check_statement(stmt)
            if isinstance(stmt, ReturnStmt):
                has_return = True
        
        # Verify non-void functions return
        if self.current_function_return_type.base_type != 'vacío' and not has_return:
            self.error(f"Function '{func.name}' must return a value of type '{self.current_function_return_type}'")
        
        # Restore
        self.current_function_return_type = old_return_type
        self.pop_scope()
    
    def check_var_decl(self, var: VarDecl):
        """Check variable declaration"""
        declared_type = self.parse_type_annotation(var.var_type)
        expr_type = self.infer_type(var.value)
        
        if expr_type and not self.types_compatible(declared_type, expr_type):
            self.error(f"Variable '{var.name}': tipo declarado '{declared_type}' "
                      f"incompatible con tipo de inicialización '{expr_type}'")
        
        self.declare_variable(var.name, declared_type)
    
    def check_statement(self, stmt: ASTNode):
        """Check a statement"""
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
            # letrero accepts anything (converts to text)
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
                if cond is not None:  # Not 'dispensador' (else)
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
                if case_val is not None:  # Not 'defecto'
                    case_type = self.infer_type(case_val)
                    if switch_type and case_type and not self.types_compatible(switch_type, case_type):
                        self.error(f"Case type '{case_type}' incompatible with "
                                  f"switch expression '{switch_type}'")
                for s in case_body:
                    self.check_statement(s)
        
        elif isinstance(stmt, Call):
            self.infer_type(stmt)  # Calls can also be statements
        
        elif isinstance(stmt, (BreakStmt, ContinueStmt)):
            pass  # Don't require type validation
    
    def check_index_assign(self, stmt: IndexAssign):
        """Check index assignment: xs[i] = value"""
        if isinstance(stmt.target, VarRef):
            target_type = self.get_variable_type(stmt.target.name)
            if not target_type:
                self.error(f"Variable '{stmt.target.name}' no declarada")
                return
            
            if target_type.base_type == 'inventario':
                # Check that index is bloques
                index_type = self.infer_type(stmt.index)
                if index_type and index_type.base_type != 'bloques':
                    self.error(f"Inventario index must be 'bloques', not '{index_type}'")
                
                # Check that value is of correct type
                if target_type.generic_params:
                    expected_type = TypeInfo(target_type.generic_params[0])
                    value_type = self.infer_type(stmt.value)
                    if value_type and not self.types_compatible(expected_type, value_type):
                        self.error(f"Value type '{value_type}' incompatible with "
                                  f"inventario type '{expected_type}'")
            
            elif target_type.base_type == 'mapa':
                # Check that key is of correct type
                if target_type.generic_params:
                    key_type_expected = TypeInfo(target_type.generic_params[0])
                    key_type = self.infer_type(stmt.index)
                    if key_type and not self.types_compatible(key_type_expected, key_type):
                        self.error(f"Key type '{key_type}' incompatible with "
                                  f"mapa type '{key_type_expected}'")
                    
                    # Check that value is of correct type
                    value_type_expected = TypeInfo(target_type.generic_params[1])
                    value_type = self.infer_type(stmt.value)
                    if value_type and not self.types_compatible(value_type_expected, value_type):
                        self.error(f"Value type '{value_type}' incompatible with "
                                  f"mapa type '{value_type_expected}'")
            else:
                self.error(f"Cannot index type '{target_type}'")
    
    def infer_type(self, expr: Any) -> Optional[TypeInfo]:
        """Infer the type of an expression"""
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
                # Use literal_type to distinguish STRING ("...") from CHAR ('...')
                if hasattr(expr, 'literal_type'):
                    if expr.literal_type == 'CHAR':
                        return TypeInfo('glifo')
                    elif expr.literal_type == 'STRING':
                        return TypeInfo('texto')
                # Fallback: if no literal_type, use length (legacy)
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
        """Infer type of binary expression"""
        left_type = self.infer_type(expr.left)
        right_type = self.infer_type(expr.right)
        
        if not left_type or not right_type:
            return None
        
        # Arithmetic operators
        if expr.op in ('+', '-', '*', '/', '%'):
            # Special case: text concatenation with +
            if expr.op == '+' and (left_type.base_type == 'texto' or right_type.base_type == 'texto'):
                return TypeInfo('texto')
            
            # Numeric operations
            if not left_type.is_numeric() or not right_type.is_numeric():
                self.error(f"Operator '{expr.op}' requires numeric types, "
                          f"not '{left_type}' and '{right_type}'")
                return None
            
            # If one is coordenada, result is coordenada
            if left_type.base_type == 'coordenada' or right_type.base_type == 'coordenada':
                return TypeInfo('coordenada')
            return TypeInfo('bloques')
        
        # Relational operators
        elif expr.op in ('==', '!='):
            # Any type can be compared for equality
            return TypeInfo('redstone')
        
        elif expr.op in ('<', '>', '<=', '>='):
            if not left_type.is_comparable() or not right_type.is_comparable():
                self.error(f"Operator '{expr.op}' not supported for types "
                          f"'{left_type}' and '{right_type}'")
                return None
            return TypeInfo('redstone')
        
        # Logical operators
        elif expr.op in ('y', 'o'):
            if left_type.base_type != 'redstone' or right_type.base_type != 'redstone':
                self.error(f"Operator '{expr.op}' requires 'redstone' types, "
                          f"not '{left_type}' and '{right_type}'")
                return None
            return TypeInfo('redstone')
        
        return None
    
    def infer_unary_type(self, expr: ExprUnary) -> Optional[TypeInfo]:
        """Infer type of unary expression"""
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
        """Infer type of function call"""
        if call.callee not in self.functions:
            self.error(f"Function '{call.callee}' not declared")
            return None
        
        return_type, param_types = self.functions[call.callee]
        
        # Check number of arguments (flexible for builtins)
        if param_types and None not in param_types:
            if len(call.args) != len(param_types):
                self.error(f"Function '{call.callee}' expects {len(param_types)} arguments, "
                          f"received {len(call.args)}")
        
        # Infer argument types
        for arg in call.args:
            self.infer_type(arg)
        
        return return_type
    
    def infer_list_type(self, expr: ListLiteral) -> Optional[TypeInfo]:
        """Infer type of list literal"""
        if not expr.elements:
            # Empty list - type will be determined by context (variable declaration)
            return TypeInfo('inventario', ['?'])
        
        # Infer type of first element
        first_type = self.infer_type(expr.elements[0])
        if not first_type:
            return None
        
        # Check that all elements are of the same type
        for elem in expr.elements[1:]:
            elem_type = self.infer_type(elem)
            if elem_type and not self.types_compatible(first_type, elem_type):
                self.error(f"List with inconsistent element types: "
                          f"'{first_type}' and '{elem_type}'")
        
        return TypeInfo('inventario', [str(first_type)])
    
    def infer_map_type(self, expr: MapLiteral) -> Optional[TypeInfo]:
        """Infer type of map literal"""
        if not expr.pairs:
            # Empty map - type will be determined by context (variable declaration)
            return TypeInfo('mapa', ['?', '?'])
        
        # Infer types of first pair
        first_key_type = self.infer_type(expr.pairs[0][0])
        first_val_type = self.infer_type(expr.pairs[0][1])
        
        if not first_key_type or not first_val_type:
            return None
        
        # Check consistency
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
        """Infer type of index access"""
        target_type = self.infer_type(expr.target)
        
        if not target_type:
            return None
        
        if target_type.base_type == 'inventario':
            # Verificar que el índice sea bloques
            index_type = self.infer_type(expr.index)
            if index_type and index_type.base_type != 'bloques':
                self.error(f"Índice de inventario debe ser 'bloques', no '{index_type}'")
            
            # Retornar tipo del elemento
            if target_type.generic_params:
                return TypeInfo(target_type.generic_params[0])
            return None
        
        elif target_type.base_type == 'mapa':
            # Verificar tipo de clave
            if target_type.generic_params:
                key_type_expected = TypeInfo(target_type.generic_params[0])
                key_type = self.infer_type(expr.index)
                if key_type and not self.types_compatible(key_type_expected, key_type):
                    self.error(f"Tipo de clave '{key_type}' incompatible con '{key_type_expected}'")
                
                # Retornar tipo del valor
                return TypeInfo(target_type.generic_params[1])
            return None
        
        else:
            self.error(f"No se puede indexar tipo '{target_type}'")
            return None
    
    def types_compatible(self, expected: TypeInfo, actual: TypeInfo) -> bool:
        """Verifica si dos tipos son compatibles"""
        # Tipos exactamente iguales
        if expected == actual:
            return True
        
        # bloques se puede promover a coordenada
        if expected.base_type == 'coordenada' and actual.base_type == 'bloques':
            return True
        
        # Tipo desconocido '?' es compatible con cualquiera (para listas/mapas vacíos)
        if '?' in expected.generic_params or '?' in actual.generic_params:
            return True
        
        return False
    
    def print_errors(self):
        """Imprime todos los errores encontrados"""
        if not self.errors:
            print("No se encontraron errores de tipo")
            return
        
        print(f"Se encontraron {len(self.errors)} error(es) de tipo:\n")
        for i, error in enumerate(self.errors, 1):
            print(f"{i}. {error}")
    
    def get_formatted_errors(self):
        """Return formatted errors as a list of strings"""
        if not self.errors:
            return []
        
        formatted = [f"Found {len(self.errors)} type error(s):\n"]
        for i, error in enumerate(self.errors, 1):
            formatted.append(f"{i}. {error}")
        
        return formatted
