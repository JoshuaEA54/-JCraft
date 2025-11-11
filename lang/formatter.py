import re
from typing import List


class JCraftFormatter:
    """
    Formateador de código :JCraft que aplica indentación y estructura
    correcta al código fuente.
    """
    
    def __init__(self, indent_size: int = 4):
        self.indent_size = indent_size
        
        # Almacenamiento temporal para strings y comentarios durante el formateo
        self.strings = []
        self.comments = []
        
        # Palabras clave que inician bloques (requieren fin, romper, cosechar, etc.)
        self.block_openers = {
            'mesa_crafteo', 'observador', 'comparador', 'dispensador',
            'spawner', 'cultivar', 'creeper', 'portal', 'caso', 'defecto'
        }
        
        # Palabras clave que cierran bloques
        # NOTA: boom NO es un closer, siempre va con condición: boom(x < 3)
        self.block_closers = {
            'fin', 'romper', 'cosechar', 'salir_portal'
        }
        
        # Alternativas condicionales que van al mismo nivel que observador
        # IMPORTANTE: comparador requiere paréntesis, dispensador NO
        self.conditional_alternatives = {'comparador', 'dispensador'}
        
        # Alternativas de switch que van al mismo nivel que portal (NO incrementan indent extra)
        self.switch_alternatives = {'caso', 'defecto'}
        
        # Openers que requieren paréntesis después del keyword (ej: observador (cond))
        self.openers_require_paren = {'observador', 'portal', 'comparador', 'spawner', 'cultivar'}
    
    def format(self, code: str) -> str:
        """
        Formatea el código :JCraft completo.
        """
        # Reiniciar almacenamiento temporal
        self.strings = []
        self.comments = []
        
        # Limpiar y preservar strings y comentarios
        cleaned = self._clean_code(code)
        
        # Dividir en tokens básicos
        tokens = self._tokenize_advanced(cleaned)
        
        # Formatear con indentación
        formatted_lines = self._format_with_indentation(tokens)
        
        # Limpiar líneas en blanco
        result = '\n'.join(formatted_lines)
        result = self._clean_blank_lines(result)
        
        # Restaurar comentarios
        for i, c in enumerate(self.comments):
            result = result.replace(f"__COMMENT_{i}__", c)
        
        return result
    
    def _clean_code(self, code: str) -> str:
        """Preserva strings y comentarios para procesamiento"""
        def save_string(match):
            self.strings.append(match.group(0))
            return f"__STRING_{len(self.strings)-1}__"
        
        def save_comment(match):
            self.comments.append(match.group(0))
            return f"__COMMENT_{len(self.comments)-1}__"
        
        # Guardar strings temporalmente (comillas dobles y simples)
        code = re.sub(r'"(?:[^"\\]|\\.)*"', save_string, code)
        code = re.sub(r"'(?:[^'\\]|\\.)*'", save_string, code)
        
        # Guardar comentarios temporalmente (comentarios de línea que empiezan con #)
        code = re.sub(r'#[^\n]*', save_comment, code)
        
        # Procesar línea por línea para separar comentarios standalone
        lines = code.split('\n')
        processed_lines = []
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
                
            # Si la línea solo contiene un comentario, es standalone
            if re.match(r'^__COMMENT_\d+__$', stripped):
                # Marcar como comentario standalone y agregar ; para que se tokenize separado
                processed_lines.append(f'__STANDALONECOMMENT__{stripped};')
            else:
                # Línea con código, mantener comentarios inline unidos
                processed_lines.append(stripped)
        
        # Unir todas las líneas
        code = ' '.join(processed_lines)
        
        # Restaurar strings
        for i, s in enumerate(self.strings):
            code = code.replace(f"__STRING_{i}__", s)
        
        # NO restaurar comentarios aquí, se restaurarán al final
        
        return code
    
    def _tokenize_advanced(self, code: str) -> List[str]:
        """
        Tokeniza el código separando statements y estructuras de control.
        
        Proceso:
        1. Divide el código por separadores (';' y ':')
        2. Respeta strings y paréntesis (no divide dentro de ellos)
        3. Separa tokens compuestos (ej: "fin craftear" -> ["fin", "craftear"])
        
        Returns:
            Lista de tokens individuales
        """
        # Paso 1: Dividir por separadores básicos
        raw_tokens = self._split_by_separators(code)
        
        # Paso 2: Dividir tokens compuestos (ej: "fin craftear x")
        final_tokens = []
        for token in raw_tokens:
            final_tokens.extend(self._split_compound_tokens(token))
        
        return final_tokens
    
    def _split_by_separators(self, code: str) -> List[str]:
        """
        Divide el código por los separadores ';' y ':', pero respeta:
        - Strings (contenido entre comillas)
        - Paréntesis (no divide dentro de llamadas a función)
        - Llaves (no divide dentro de mapas/diccionarios)
        - Comentarios inline (el ; seguido de comentario no separa)
        
        Returns:
            Lista de tokens sin procesar
        """
        tokens = []
        current_token = ""
        
        # Estados del parser
        in_string = False
        string_char = None  # Guardamos qué tipo de comilla abrió el string (" o ')
        escape_next = False
        paren_depth = 0   # Contador de paréntesis abiertos
        brace_depth = 0   # Contador de llaves abiertas
        
        i = 0
        while i < len(code):
            char = code[i]
            
            # 1. Manejar caracteres escapados en strings
            if escape_next:
                current_token += char
                escape_next = False
                i += 1
                continue
            
            if char == '\\' and in_string:
                current_token += char
                escape_next = True
                i += 1
                continue
            
            # 2. Detectar inicio/fin de string (comillas dobles o simples)
            if char in ('"', "'"):
                if not in_string:
                    # Iniciar string
                    in_string = True
                    string_char = char
                elif char == string_char:
                    # Cerrar string (solo si coincide con la comilla que lo abrió)
                    in_string = False
                    string_char = None
                current_token += char
                i += 1
                continue
            
            # 3. Si estamos en un string, agregar todo sin procesar
            if in_string:
                current_token += char
                i += 1
                continue
            
            # 4. Contar paréntesis (para no dividir en llamadas a función)
            if char == '(':
                paren_depth += 1
                current_token += char
                i += 1
                continue
            
            if char == ')':
                paren_depth -= 1
                current_token += char
                i += 1
                continue
            
            # 5. Contar llaves (para no dividir dentro de mapas/diccionarios)
            if char == '{':
                brace_depth += 1
                current_token += char
                i += 1
                continue
            
            if char == '}':
                brace_depth -= 1
                current_token += char
                i += 1
                continue
            
            # 6. Separadores solo funcionan fuera de paréntesis Y llaves
            if paren_depth == 0 and brace_depth == 0:
                # Punto y coma separa statements, EXCEPTO si va seguido de comentario
                if char == ';':
                    # Mirar hacia adelante para ver si hay un comentario
                    lookahead = code[i+1:].lstrip()
                    if lookahead.startswith('__COMMENT_'):
                        # Hay un comentario inline, agregar ; y continuar hasta el comentario
                        current_token += char
                        i += 1
                        # Agregar espacios y el comentario
                        while i < len(code) and code[i] in ' \t':
                            current_token += code[i]
                            i += 1
                        # Agregar el placeholder del comentario
                        match = re.match(r'(__COMMENT_\d+__)', code[i:])
                        if match:
                            current_token += match.group(1)
                            i += len(match.group(1))
                        # Ahora sí, guardar el token completo
                        if current_token.strip():
                            tokens.append(current_token.strip())
                        current_token = ""
                        continue
                    
                    # Separación normal (sin comentario)
                    if current_token.strip():
                        tokens.append(current_token.strip())
                    current_token = ""
                    i += 1
                    continue
                
                # Dos puntos separa declaraciones (función, if, etc.)
                if char == ':':
                    current_token += char
                    if current_token.strip():
                        tokens.append(current_token.strip())
                    current_token = ""
                    i += 1
                    continue
            
            # 7. Carácter normal, agregar al token actual
            current_token += char
            i += 1
        
        # Agregar el último token si existe
        if current_token.strip():
            tokens.append(current_token.strip())
        
        return tokens
    
    def _split_compound_tokens(self, token: str) -> List[str]:
        """
        Separa tokens que tienen un closer seguido de otro statement.
        
        Problema: En código sin formato, puede aparecer:
            "fin craftear x"  -> debería ser ["fin", "craftear x"]
            "romper letrero('x')"  -> debería ser ["romper", "letrero('x')"]
        
        Solución: Si el token empieza con un closer, lo separamos.
        
        Args:
            token: Token que puede contener un closer + otro statement
            
        Returns:
            Lista con el token dividido (o el mismo si no es compuesto)
        """
        token = token.strip()
        
        # Palabras que cierran bloques
        # boom NO está aquí porque siempre va con condición: boom(x < 3)
        closers = ['fin', 'romper', 'cosechar', 'salir_portal']
        
        # Revisar cada closer
        for closer in closers:
            # Caso 1: El token es exactamente el closer (ej: "fin")
            if token == closer:
                return [token]
            
            # Caso 2: El closer está al inicio seguido de espacio (ej: "fin craftear x")
            if token.startswith(closer + ' '):
                # Separar: "fin" + "craftear x"
                rest = token[len(closer):].strip()
                
                if rest:
                    # Dividir recursivamente por si hay más closers
                    # Ejemplo: "fin fin craftear x" -> ["fin", "fin", "craftear x"]
                    return [closer] + self._split_compound_tokens(rest)
        
        # No es un token compuesto, retornar como está
        return [token]
    
    def _starts_with_keyword(self, token: str, keywords: set) -> bool:
        """Verifica si el token comienza con alguna de las palabras clave"""
        token_lower = token.lower().lstrip()
        for kw in keywords:
            if token_lower.startswith(kw):
                # Asegurar límite de palabra (evitar 'observadorx')
                after = token_lower[len(kw):]
                if after == '' or after[0].isspace() or after[0] in '(:':
                    return True
        return False

    def _keyword_followed_by(self, token: str, keywords: set, follow_chars: List[str]) -> bool:
        """Verifica si el token comienza con una keyword y a continuación aparece uno de follow_chars

        Ejemplo: _keyword_followed_by('observador (x > 0)', {'observador'}, ['(']) -> True
        Permite espacios entre la keyword y el caracter de seguimiento.
        """
        token_lower = token.lower().lstrip()
        for kw in keywords:
            if token_lower.startswith(kw):
                after = token_lower[len(kw):].lstrip()
                for ch in follow_chars:
                    if after.startswith(ch):
                        return True
        return False

    def _keyword_has_paren_after(self, token: str, kw: str) -> bool:
        """Comprueba si la keyword `kw` aparece al inicio de `token` y está seguida por '(' (permitiendo espacios)."""
        token_lower = token.lower().lstrip()
        if token_lower.startswith(kw):
            after = token_lower[len(kw):].lstrip()
            return after.startswith('(')
        return False
    
    def _format_with_indentation(self, tokens: List[str]) -> List[str]:
        """
        Aplica indentación correcta a cada token.
        
        Reglas:
        1. Cada statement termina con ;
        2. Los bloques (mesa_crafteo, observador, etc.) aumentan indentación
        3. comparador/dispensador van al mismo nivel que su observador
        4. fin/romper/cosechar/salir_portal cierran bloque sin ;
        5. boom(condición) cierra el bloque creeper CON ; (como do-while)
        
        IMPORTANTE: 
        - Todos los closers (fin, romper, boom, etc.) retroceden ANTES de imprimir
        - La diferencia: boom(condición) lleva ; pero los demás no
        - EXCEPCIÓN: romper dentro de portal NO retrocede (es contenido del caso)
        """
        formatted = []
        indent_level = 0
        inside_portal = 0  # Contador de portales anidados
        inside_case = False  # Si estamos dentro de un caso activo
        
        for token in tokens:
            token = token.strip()
            if not token:
                continue
            
            # PASO 1: Detectar si es un comentario standalone
            if token.startswith('__STANDALONECOMMENT__'):
                # Extraer el placeholder del comentario
                comment_placeholder = token.replace('__STANDALONECOMMENT__', '').strip()
                indent_str = ' ' * (indent_level * self.indent_size)
                formatted_line = indent_str + comment_placeholder
                formatted.append(formatted_line)
                continue
            
            # Detectar si el token tiene un comentario inline
            comment_match = re.search(r'(__COMMENT_\d+__)', token)
            has_inline_comment = comment_match is not None
            
            if has_inline_comment:
                # Separar el código del comentario
                comment_placeholder = comment_match.group(1)
                # Quitar el comentario Y el ; que lo precede si existe
                code_part = token.replace(comment_placeholder, '').strip()
                if code_part.endswith(';'):
                    code_part = code_part[:-1].strip()
                
                # PASO 2: Ajustar indentación según el tipo de token
                is_boom_closer = bool(re.match(r'^boom\b\s*\(', code_part.lower()))
                
                # Detectar si es dispensador (sin paréntesis) o comparador (con paréntesis)
                is_dispensador = code_part.lower().lstrip().startswith('dispensador')
                is_comparador_with_paren = self._keyword_followed_by(code_part, {'comparador'}, ['('])
                is_romper = code_part == 'romper'
                is_salir_portal = code_part == 'salir_portal'
                is_switch_alternative = self._starts_with_keyword(code_part, self.switch_alternatives)
                
                # Retroceder nivel ANTES de imprimir si es:
                # - Un closer (fin, cosechar, salir_portal)
                # - boom(condición)
                # - comparador(cond) - va al mismo nivel que observador
                # - dispensador - va al mismo nivel que observador
                # - caso/defecto cuando ya hay un caso anterior (van al mismo nivel entre sí)
                # EXCEPCIÓN: romper dentro de portal NO retrocede (es contenido del caso, como break; en C++)
                if (code_part in self.block_closers or
                    is_boom_closer or
                    is_comparador_with_paren or
                    is_dispensador or
                    (is_switch_alternative and inside_case)):  # Solo retroceder si ya hay un caso activo
                    # romper dentro de portal no retrocede (es parte del contenido del caso)
                    if is_romper and inside_portal > 0:
                        pass  # No retroceder
                    else:
                        indent_level = max(0, indent_level - 1)
                        # salir_portal necesita retroceder un nivel adicional si hay caso activo
                        if is_salir_portal and inside_portal > 0:
                            if inside_case:
                                indent_level = max(0, indent_level - 1)
                            inside_portal -= 1
                            inside_case = False
                
                # PASO 3: Crear línea formateada
                indent_str = ' ' * (indent_level * self.indent_size)
                
                if code_part.endswith(':'):
                    formatted_line = indent_str + code_part + '  ' + comment_placeholder
                elif code_part in self.block_closers:
                    formatted_line = indent_str + code_part + '  ' + comment_placeholder
                else:
                    formatted_line = indent_str + code_part + ';  ' + comment_placeholder
                
                formatted.append(formatted_line)
                
                # PASO 4: Aumentar indentación si abrimos bloque
                if code_part.endswith(':') and self._starts_with_keyword(code_part, self.block_openers):
                    # Detectar si es portal para incrementar contador
                    if code_part.lower().lstrip().startswith('portal'):
                        inside_portal += 1
                        inside_case = False  # Resetear al entrar a portal
                    
                    # Detectar si es caso/defecto para marcar que hay un caso activo
                    if is_switch_alternative:
                        inside_case = True
                    
                    # Validar si requiere paréntesis
                    opener_ok = True
                    for kw in self.openers_require_paren:
                        if code_part.lower().lstrip().startswith(kw):
                            if not self._keyword_has_paren_after(code_part, kw):
                                opener_ok = False
                            break
                    if opener_ok:
                        indent_level += 1
                continue
            
            # PASO 2: Ajustar el nivel de indentación según el tipo de token
            
            # boom(condición) también retrocede ANTES de imprimirse (cierra el creeper)
            # Puede tener espacios antes del paréntesis: "boom (x < 3)" o "boom(x < 3)"
            is_boom_closer = bool(re.match(r'^boom\b\s*\(', token.lower()))
            
            # Detectar si es dispensador (sin paréntesis) o comparador (con paréntesis)
            is_dispensador = token.lower().lstrip().startswith('dispensador')
            is_comparador_with_paren = self._keyword_followed_by(token, {'comparador'}, ['('])
            is_romper = token == 'romper'
            is_salir_portal = token == 'salir_portal'
            is_switch_alternative = self._starts_with_keyword(token, self.switch_alternatives)
            
            # Estos tokens retroceden ANTES de imprimirse (van al mismo nivel que el opener)
            if (token in self.block_closers or
                is_boom_closer or
                # comparador(cond) debe ir al mismo nivel que observador
                is_comparador_with_paren or
                # dispensador (sin paréntesis) debe ir al mismo nivel que observador
                is_dispensador or
                # caso/defecto cuando ya hay un caso anterior (van al mismo nivel entre sí)
                (is_switch_alternative and inside_case)):
                # EXCEPCIÓN: romper dentro de portal NO retrocede (es contenido del caso, como break; en C++)
                if is_romper and inside_portal > 0:
                    pass  # No retroceder, es parte del contenido del caso
                else:
                    indent_level = max(0, indent_level - 1)
                    # salir_portal necesita retroceder un nivel adicional si hay caso activo
                    if is_salir_portal and inside_portal > 0:
                        if inside_case:
                            indent_level = max(0, indent_level - 1)
                        inside_portal -= 1
                        inside_case = False
            
            # PASO 3: Crear la línea formateada con la indentación actual
            indent_str = ' ' * (indent_level * self.indent_size)
            
            if token.endswith(':'):
                # Declaraciones (función, if, etc.) no llevan ;
                formatted_line = indent_str + token
            elif token in self.block_closers:
                # Closers de bloque (fin, romper, cosechar, salir_portal) no llevan ;
                formatted_line = indent_str + token
            else:
                # Statements normales (incluyendo boom(condición)) llevan ;
                formatted_line = indent_str + token + ';'
            
            formatted.append(formatted_line)
            
            # PASO 4: Si abrimos un bloque, aumentar indentación para el siguiente
            if token.endswith(':') and self._starts_with_keyword(token, self.block_openers):
                # Detectar si es portal para incrementar contador
                if token.lower().lstrip().startswith('portal'):
                    inside_portal += 1
                    inside_case = False  # Resetear al entrar a portal
                
                # Detectar si es caso/defecto para marcar que hay un caso activo
                if is_switch_alternative:
                    inside_case = True
                
                # Si el opener requiere paréntesis (ej. observador), validar que efectivamente haya '('
                opener_ok = True
                for kw in self.openers_require_paren:
                    if token.lower().lstrip().startswith(kw):
                        if not self._keyword_has_paren_after(token, kw):
                            opener_ok = False
                        break
                if opener_ok:
                    indent_level += 1
        
        return formatted
    
    def _clean_blank_lines(self, text: str) -> str:
        """Limpia líneas en blanco excesivas y organiza el código"""
        lines = text.split('\n')
        cleaned = []
        blank_count = 0
        prev_was_fin = False
        
        for line in lines:
            stripped = line.strip()
            
            # Si es una línea vacía
            if not stripped:
                blank_count += 1
                # Permitir máximo 1 línea en blanco consecutiva
                if blank_count <= 1:
                    cleaned.append('')
                continue
            
            # Agregar línea en blanco antes de mesa_crafteo (excepto el primero)
            if stripped.startswith('mesa_crafteo') and cleaned and prev_was_fin:
                if cleaned[-1].strip():  # Si la última línea no está vacía
                    cleaned.append('')
            
            blank_count = 0
            prev_was_fin = stripped.startswith('fin')
            cleaned.append(line)
        
        # Remover líneas en blanco al inicio
        while cleaned and not cleaned[0].strip():
            cleaned.pop(0)
        
        # Asegurar que termina con exactamente una línea en blanco
        while cleaned and not cleaned[-1].strip():
            cleaned.pop()
        cleaned.append('')
        
        return '\n'.join(cleaned)


def format_jcraft_code(code: str, indent_size: int = 4) -> str:
    """
    Función auxiliar para formatear código :JCraft.
    
    Args:
        code: Código fuente
        indent_size: Tamaño de indentación (default: 4 espacios)
    
    Returns:
        Código formateado
    """
    formatter = JCraftFormatter(indent_size)
    return formatter.format(code)


if __name__ == "__main__":
    # Ejemplo de uso
    test_code = """
    mesa_crafteo bloques suma(bloques a, bloques b): craftear a + b; fin
    mesa_crafteo vacío main(): bloques x = 5; bloques y = 3; bloques resultado = suma(x, y); letrero("Resultado: " + to_texto(resultado)); observador (resultado > 5): letrero("Mayor que 5"); comparador (resultado == 5): letrero("Igual a 5"); dispensador: letrero("Menor que 5"); fin fin
    """
    
    print("=== CÓDIGO SIN FORMATO ===")
    print(test_code)
    print("\n=== CÓDIGO FORMATEADO ===")
    print(format_jcraft_code(test_code))
