"""
Type Checker para JCraft
Valida tipos estáticamente antes de la ejecución
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from .parser import (
    Program, FunctionDecl, VarDecl, Assign, Call, PrintStmt, ReturnStmt,
    IfStmt, WhileStmt, ForStmt, DoWhileStmt, SwitchStmt, BreakStmt, ContinueStmt,
    ExprBin, ExprUnary, Literal, VarRef, ListLiteral, MapLiteral,
    IndexAccess, IndexAssign, ASTNode
)


class TypeCheckError(Exception):
    """Error de validación de tipos"""
    pass


@dataclass
class TypeInfo:
    """Información de tipo para una expresión"""
    base_type: str  # 'bloques', 'texto', 'inventario', 'mapa', etc.
    generic_params: List[str] = None  # Para inventario<T> o mapa<K,V>
    
    def __post_init__(self):
        if self.generic_params is None:
            self.generic_params = []
    
    def __str__(self):
        if self.generic_params:
            return f"{self.base_type}<{','.join(self.generic_params)}>"
        return self.base_type
    
    def __eq__(self, other):
        if not isinstance(other, TypeInfo):
            return False
        return (self.base_type == other.base_type and 
                self.generic_params == other.generic_params)
    
    def is_numeric(self):
        """Verifica si es tipo numérico"""
        return self.base_type in ('bloques', 'coordenada')
    
    def is_comparable(self):
        """Verifica si se puede usar en comparaciones"""
        return self.base_type in ('bloques', 'coordenada', 'texto', 'glifo')
    
    def is_collection(self):
        """Verifica si es colección"""
        return self.base_type in ('inventario', 'mapa')


class TypeChecker:
    """Validador de tipos estático para JCraft"""
    
    def __init__(self):
        # Tabla de símbolos: nombre -> TypeInfo
        self.variables: Dict[str, TypeInfo] = {}
        # Funciones: nombre -> (return_type, [param_types])
        self.functions: Dict[str, tuple] = {}
        # Contexto de función actual (para validar return)
        self.current_function_return_type: Optional[TypeInfo] = None
        # Stack de scopes para variables locales
        self.scope_stack: List[Dict[str, TypeInfo]] = [{}]
        # Contador de errores
        self.errors: List[str] = []
        
        # Funciones built-in
        self._init_builtins()
    
    def _init_builtins(self):
        """Inicializa funciones built-in"""
        # cofre() : texto
        self.functions['cofre'] = (TypeInfo('texto'), [])
        
        # letrero(expr) : vacío
        self.functions['letrero'] = (TypeInfo('vacío'), [TypeInfo('texto')])  # Acepta cualquier cosa
        
        # length(colección) : bloques
        self.functions['length'] = (TypeInfo('bloques'), [None])  # Acepta colecciones
        
        # push(inventario<T>, T) : vacío
        self.functions['push'] = (TypeInfo('vacío'), [None, None])
        
        # pop(inventario<T>) : T
        self.functions['pop'] = (None, [None])  # Tipo de retorno depende del argumento
        
        # tiene(mapa<K,V>, K) : redstone
        self.functions['tiene'] = (TypeInfo('redstone'), [None, None])
        
        # Conversiones
        self.functions['to_bloques'] = (TypeInfo('bloques'), [None])
        self.functions['to_coordenada'] = (TypeInfo('coordenada'), [None])
        self.functions['to_texto'] = (TypeInfo('texto'), [None])
        self.functions['to_redstone'] = (TypeInfo('redstone'), [None])
        self.functions['to_glifo'] = (TypeInfo('glifo'), [None])
    
    def error(self, message: str):
        """Registra un error de tipo"""
        self.errors.append(message)
    
    def push_scope(self):
        """Crea un nuevo scope para variables locales"""
        self.scope_stack.append({})
    
    def pop_scope(self):
        """Sale del scope actual"""
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()
    
    def declare_variable(self, name: str, type_info: TypeInfo):
        """Declara una variable en el scope actual"""
        current_scope = self.scope_stack[-1]
        if name in current_scope:
            self.error(f"Variable '{name}' ya declarada en este scope")
        current_scope[name] = type_info
        # También en tabla global para fácil acceso
        self.variables[name] = type_info
    
    def get_variable_type(self, name: str) -> Optional[TypeInfo]:
        """Obtiene el tipo de una variable"""
        # Busca desde el scope más interno al más externo
        for scope in reversed(self.scope_stack):
            if name in scope:
                return scope[name]
        return None
    
    def parse_type_annotation(self, type_str: str) -> TypeInfo:
        """Parsea una anotación de tipo como 'inventario<bloques>' o 'mapa<texto,bloques>'"""
        if '<' in type_str:
            # Tipo genérico
            base = type_str[:type_str.index('<')]
            params_str = type_str[type_str.index('<')+1:type_str.rindex('>')]
            params = [p.strip() for p in params_str.split(',')]
            return TypeInfo(base, params)
        else:
            return TypeInfo(type_str)
    
    def check(self, program: Program) -> bool:
        """
        Verifica tipos del programa completo.
        Retorna True si no hay errores, False si hay errores.
        """
        self.errors = []
        
        # Primera pasada: recolectar declaraciones de funciones
        main_count = 0
        for decl in program.declarations:
            if isinstance(decl, FunctionDecl):
                # Verificar que no haya funciones duplicadas
                if decl.name in self.functions:
                    self.error(f"Función '{decl.name}' declarada múltiples veces")
                
                # Contar mains
                if decl.name == 'main':
                    main_count += 1
                
                param_types = [self.parse_type_annotation(ptype) for ptype, _ in decl.params]
                return_type = self.parse_type_annotation(decl.return_type)
                self.functions[decl.name] = (return_type, param_types)
        
        # Verificar que main es único
        if main_count == 0:
            self.error("Función 'main' no encontrada (obligatoria y debe ser única)")
        elif main_count > 1:
            self.error(f"Función 'main' declarada {main_count} veces (debe ser única)")
        
        # Segunda pasada: verificar cuerpos de funciones y variables globales
        for decl in program.declarations:
            if isinstance(decl, FunctionDecl):
                self.check_function(decl)
            elif isinstance(decl, VarDecl):
                self.check_var_decl(decl)
        
        # Verificar firma de main (si existe)
        if 'main' in self.functions:
            return_type, param_types = self.functions['main']
            if return_type.base_type != 'vacío':
                self.error(f"main debe retornar 'vacío', no '{return_type}'")
            if len(param_types) > 0:
                self.error(f"main no debe tener parámetros (tiene {len(param_types)})")
        
        return len(self.errors) == 0
    
    def check_function(self, func: FunctionDecl):
        """Verifica el cuerpo de una función"""
        # Nuevo scope para parámetros y variables locales
        self.push_scope()
        
        # Guardar tipo de retorno esperado
        old_return_type = self.current_function_return_type
        self.current_function_return_type = self.parse_type_annotation(func.return_type)
        
        # Declarar parámetros
        for ptype, pname in func.params:
            param_type = self.parse_type_annotation(ptype)
            self.declare_variable(pname, param_type)
        
        # Verificar cuerpo
        has_return = False
        for stmt in func.body:
            self.check_statement(stmt)
            if isinstance(stmt, ReturnStmt):
                has_return = True
        
        # Verificar que funciones no-void retornan
        if self.current_function_return_type.base_type != 'vacío' and not has_return:
            self.error(f"Función '{func.name}' debe retornar un valor de tipo '{self.current_function_return_type}'")
        
        # Restaurar
        self.current_function_return_type = old_return_type
        self.pop_scope()
    
    def check_var_decl(self, var: VarDecl):
        """Verifica declaración de variable"""
        declared_type = self.parse_type_annotation(var.var_type)
        expr_type = self.infer_type(var.value)
        
        if expr_type and not self.types_compatible(declared_type, expr_type):
            self.error(f"Variable '{var.name}': tipo declarado '{declared_type}' "
                      f"incompatible con tipo de inicialización '{expr_type}'")
        
        self.declare_variable(var.name, declared_type)
    
    def check_statement(self, stmt: ASTNode):
        """Verifica un statement"""
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
            # letrero acepta cualquier cosa (convierte a texto)
            self.infer_type(stmt.expr)
        
        elif isinstance(stmt, ReturnStmt):
            if not self.current_function_return_type:
                self.error("'craftear' fuera de una función")
                return
            
            if stmt.expr is None:
                if self.current_function_return_type.base_type != 'vacío':
                    self.error(f"Se esperaba retornar '{self.current_function_return_type}', "
                              f"pero no se retorna valor")
            else:
                expr_type = self.infer_type(stmt.expr)
                if expr_type and not self.types_compatible(self.current_function_return_type, expr_type):
                    self.error(f"Tipo de retorno '{expr_type}' incompatible con "
                              f"tipo declarado '{self.current_function_return_type}'")
        
        elif isinstance(stmt, IfStmt):
            for cond, body in stmt.branches:
                if cond is not None:  # No es 'dispensador' (else)
                    cond_type = self.infer_type(cond)
                    if cond_type and cond_type.base_type != 'redstone':
                        self.error(f"Condición de 'observador/comparador' debe ser 'redstone', "
                                  f"no '{cond_type}'")
                for s in body:
                    self.check_statement(s)
        
        elif isinstance(stmt, WhileStmt):
            cond_type = self.infer_type(stmt.condition)
            if cond_type and cond_type.base_type != 'redstone':
                self.error(f"Condición de 'spawner' debe ser 'redstone', no '{cond_type}'")
            for s in stmt.body:
                self.check_statement(s)
        
        elif isinstance(stmt, DoWhileStmt):
            for s in stmt.body:
                self.check_statement(s)
            cond_type = self.infer_type(stmt.condition)
            if cond_type and cond_type.base_type != 'redstone':
                self.error(f"Condición de 'boom' debe ser 'redstone', no '{cond_type}'")
        
        elif isinstance(stmt, ForStmt):
            self.push_scope()
            if stmt.init:
                self.check_statement(stmt.init)
            if stmt.condition:
                cond_type = self.infer_type(stmt.condition)
                if cond_type and cond_type.base_type != 'redstone':
                    self.error(f"Condición de 'cultivar' debe ser 'redstone', no '{cond_type}'")
            if stmt.step:
                self.infer_type(stmt.step)
            for s in stmt.body:
                self.check_statement(s)
            self.pop_scope()
        
        elif isinstance(stmt, SwitchStmt):
            switch_type = self.infer_type(stmt.expr)
            for case_val, case_body in stmt.cases:
                if case_val is not None:  # No es 'defecto'
                    case_type = self.infer_type(case_val)
                    if switch_type and case_type and not self.types_compatible(switch_type, case_type):
                        self.error(f"Tipo de caso '{case_type}' incompatible con "
                                  f"expresión de switch '{switch_type}'")
                for s in case_body:
                    self.check_statement(s)
        
        elif isinstance(stmt, Call):
            self.infer_type(stmt)  # Las llamadas también pueden ser statements
        
        elif isinstance(stmt, (BreakStmt, ContinueStmt)):
            pass  # No requieren validación de tipos
    
    def check_index_assign(self, stmt: IndexAssign):
        """Verifica asignación a índice: xs[i] = valor"""
        if isinstance(stmt.target, VarRef):
            target_type = self.get_variable_type(stmt.target.name)
            if not target_type:
                self.error(f"Variable '{stmt.target.name}' no declarada")
                return
            
            if target_type.base_type == 'inventario':
                # Verificar que el índice sea bloques
                index_type = self.infer_type(stmt.index)
                if index_type and index_type.base_type != 'bloques':
                    self.error(f"Índice de inventario debe ser 'bloques', no '{index_type}'")
                
                # Verificar que el valor sea del tipo correcto
                if target_type.generic_params:
                    expected_type = TypeInfo(target_type.generic_params[0])
                    value_type = self.infer_type(stmt.value)
                    if value_type and not self.types_compatible(expected_type, value_type):
                        self.error(f"Tipo de valor '{value_type}' incompatible con "
                                  f"tipo de inventario '{expected_type}'")
            
            elif target_type.base_type == 'mapa':
                # Verificar que la clave sea del tipo correcto
                if target_type.generic_params:
                    key_type_expected = TypeInfo(target_type.generic_params[0])
                    key_type = self.infer_type(stmt.index)
                    if key_type and not self.types_compatible(key_type_expected, key_type):
                        self.error(f"Tipo de clave '{key_type}' incompatible con "
                                  f"tipo de mapa '{key_type_expected}'")
                    
                    # Verificar que el valor sea del tipo correcto
                    value_type_expected = TypeInfo(target_type.generic_params[1])
                    value_type = self.infer_type(stmt.value)
                    if value_type and not self.types_compatible(value_type_expected, value_type):
                        self.error(f"Tipo de valor '{value_type}' incompatible con "
                                  f"tipo de mapa '{value_type_expected}'")
            else:
                self.error(f"No se puede indexar tipo '{target_type}'")
    
    def infer_type(self, expr: Any) -> Optional[TypeInfo]:
        """Infiere el tipo de una expresión"""
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
                # Usar literal_type para distinguir STRING ("...") de CHAR ('...')
                if hasattr(expr, 'literal_type'):
                    if expr.literal_type == 'CHAR':
                        return TypeInfo('glifo')
                    elif expr.literal_type == 'STRING':
                        return TypeInfo('texto')
                # Fallback: si no tiene literal_type, usar longitud (legacy)
                if len(val) == 1:
                    return TypeInfo('glifo')
                return TypeInfo('texto')
            elif val is None:
                return TypeInfo('nulo')
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
        """Infiere tipo de expresión binaria"""
        left_type = self.infer_type(expr.left)
        right_type = self.infer_type(expr.right)
        
        if not left_type or not right_type:
            return None
        
        # Operadores aritméticos
        if expr.op in ('+', '-', '*', '/', '%'):
            # Caso especial: concatenación de texto con +
            if expr.op == '+' and (left_type.base_type == 'texto' or right_type.base_type == 'texto'):
                return TypeInfo('texto')
            
            # Operaciones numéricas
            if not left_type.is_numeric() or not right_type.is_numeric():
                self.error(f"Operador '{expr.op}' requiere tipos numéricos, "
                          f"no '{left_type}' y '{right_type}'")
                return None
            
            # Si uno es coordenada, el resultado es coordenada
            if left_type.base_type == 'coordenada' or right_type.base_type == 'coordenada':
                return TypeInfo('coordenada')
            return TypeInfo('bloques')
        
        # Operadores relacionales
        elif expr.op in ('==', '!='):
            # Cualquier tipo se puede comparar por igualdad
            return TypeInfo('redstone')
        
        elif expr.op in ('<', '>', '<=', '>='):
            if not left_type.is_comparable() or not right_type.is_comparable():
                self.error(f"Operador '{expr.op}' no soportado para tipos "
                          f"'{left_type}' y '{right_type}'")
                return None
            return TypeInfo('redstone')
        
        # Operadores lógicos
        elif expr.op in ('y', 'o'):
            if left_type.base_type != 'redstone' or right_type.base_type != 'redstone':
                self.error(f"Operador '{expr.op}' requiere tipos 'redstone', "
                          f"no '{left_type}' y '{right_type}'")
                return None
            return TypeInfo('redstone')
        
        return None
    
    def infer_unary_type(self, expr: ExprUnary) -> Optional[TypeInfo]:
        """Infiere tipo de expresión unaria"""
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
        """Infiere tipo de llamada a función"""
        if call.callee not in self.functions:
            self.error(f"Función '{call.callee}' no declarada")
            return None
        
        return_type, param_types = self.functions[call.callee]
        
        # Verificar número de argumentos (flexible para builtins)
        if param_types and None not in param_types:
            if len(call.args) != len(param_types):
                self.error(f"Función '{call.callee}' espera {len(param_types)} argumentos, "
                          f"recibió {len(call.args)}")
        
        # Inferir tipos de argumentos
        for arg in call.args:
            self.infer_type(arg)
        
        return return_type
    
    def infer_list_type(self, expr: ListLiteral) -> Optional[TypeInfo]:
        """Infiere tipo de literal de lista"""
        if not expr.elements:
            # Lista vacía - requiere contexto de tipo
            return TypeInfo('inventario', ['?'])  # Tipo desconocido
        
        # Inferir tipo del primer elemento
        first_type = self.infer_type(expr.elements[0])
        if not first_type:
            return None
        
        # Verificar que todos los elementos sean del mismo tipo
        for elem in expr.elements[1:]:
            elem_type = self.infer_type(elem)
            if elem_type and not self.types_compatible(first_type, elem_type):
                self.error(f"Lista con elementos de tipos inconsistentes: "
                          f"'{first_type}' y '{elem_type}'")
        
        return TypeInfo('inventario', [str(first_type)])
    
    def infer_map_type(self, expr: MapLiteral) -> Optional[TypeInfo]:
        """Infiere tipo de literal de mapa"""
        if not expr.pairs:
            # Mapa vacío - requiere contexto de tipo
            return TypeInfo('mapa', ['?', '?'])
        
        # Inferir tipos del primer par
        first_key_type = self.infer_type(expr.pairs[0][0])
        first_val_type = self.infer_type(expr.pairs[0][1])
        
        if not first_key_type or not first_val_type:
            return None
        
        # Verificar consistencia
        for key, val in expr.pairs[1:]:
            key_type = self.infer_type(key)
            val_type = self.infer_type(val)
            
            if key_type and not self.types_compatible(first_key_type, key_type):
                self.error(f"Mapa con claves de tipos inconsistentes: "
                          f"'{first_key_type}' y '{key_type}'")
            
            if val_type and not self.types_compatible(first_val_type, val_type):
                self.error(f"Mapa con valores de tipos inconsistentes: "
                          f"'{first_val_type}' y '{val_type}'")
        
        return TypeInfo('mapa', [str(first_key_type), str(first_val_type)])
    
    def infer_index_type(self, expr: IndexAccess) -> Optional[TypeInfo]:
        """Infiere tipo de acceso por índice"""
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
        
        # nulo es compatible con cualquier tipo compuesto
        if actual.base_type == 'nulo' and expected.is_collection():
            return True
        
        # Tipo desconocido '?' es compatible con cualquiera
        if '?' in expected.generic_params or '?' in actual.generic_params:
            return True
        
        return False
    
    def print_errors(self):
        """Imprime todos los errores encontrados"""
        if not self.errors:
            print("✅ No se encontraron errores de tipo")
            return
        
        print(f"❌ Se encontraron {len(self.errors)} error(es) de tipo:\n")
        for i, error in enumerate(self.errors, 1):
            print(f"{i}. {error}")
