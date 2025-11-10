"""
Formateador de código para :JCraft
Autor: Joshua Elizondo Abarca & Jazmín Gamboa Chacón
Universidad Nacional - Paradigmas de Programación

Este módulo formatea código :JCraft para mejorar legibilidad y consistencia.
El lenguaje permite código sin formato (todo en una línea con ;), 
pero el formateador ayuda a estructurar el código correctamente.
"""

import re
from typing import List


class JCraftFormatter:
    """
    Formateador de código :JCraft que aplica indentación y estructura
    correcta al código fuente.
    """
    
    def __init__(self, indent_size: int = 4):
        self.indent_size = indent_size
        
        # Palabras clave que inician bloques (requieren fin, romper, cosechar, boom, etc.)
        self.block_openers = {
            'mesa_crafteo', 'observador', 'comparador', 'dispensador',
            'spawner', 'cultivar', 'creeper', 'portal', 'caso', 'defecto'
        }
        
        # Palabras clave que cierran bloques
        self.block_closers = {
            'fin', 'romper', 'cosechar', 'boom', 'salir_portal'
        }
        
        # Alternativas condicionales que van al mismo nivel que observador
        self.conditional_alternatives = {'comparador', 'dispensador'}
        
        # Alternativas de switch que van al mismo nivel que caso
        self.switch_alternatives = {'caso', 'defecto'}
    
    def format(self, code: str) -> str:
        """
        Formatea el código :JCraft completo.
        """
        # Limpiar y preservar strings
        cleaned = self._clean_code(code)
        
        # Dividir en tokens básicos
        tokens = self._tokenize_advanced(cleaned)
        
        # Formatear con indentación
        formatted_lines = self._format_with_indentation(tokens)
        
        # Limpiar líneas en blanco
        result = '\n'.join(formatted_lines)
        result = self._clean_blank_lines(result)
        
        return result
    
    def _clean_code(self, code: str) -> str:
        """Limpia el código preservando strings"""
        # Preservar strings
        strings = []
        def save_string(match):
            strings.append(match.group(0))
            return f"__STRING_{len(strings)-1}__"
        
        # Guardar strings temporalmente
        code = re.sub(r'"(?:[^"\\]|\\.)*"', save_string, code)
        
        # Remover comentarios línea por línea
        lines = code.split('\n')
        cleaned_lines = []
        for line in lines:
            if '#' in line:
                line = line[:line.index('#')]
            if line.strip():  # Solo agregar líneas no vacías
                cleaned_lines.append(line)
        
        code = ' '.join(cleaned_lines)  # Unir todo en una línea
        
        # Restaurar strings
        for i, s in enumerate(strings):
            code = code.replace(f"__STRING_{i}__", s)
        
        return code
    
    def _tokenize_advanced(self, code: str) -> List[str]:
        """
        Tokeniza el código de manera avanzada, separando cada palabra clave
        y statement en su propio token.
        """
        tokens = []
        current = ""
        in_string = False
        escape_next = False
        paren_depth = 0
        
        i = 0
        while i < len(code):
            char = code[i]
            
            # Manejo de escapes en strings
            if escape_next:
                current += char
                escape_next = False
                i += 1
                continue
            
            if char == '\\' and in_string:
                current += char
                escape_next = True
                i += 1
                continue
            
            # Manejo de strings
            if char == '"':
                in_string = not in_string
                current += char
                i += 1
                continue
            
            if in_string:
                current += char
                i += 1
                continue
            
            # Contar paréntesis
            if char == '(':
                paren_depth += 1
                current += char
                i += 1
                continue
            
            if char == ')':
                paren_depth -= 1
                current += char
                i += 1
                continue
            
            # Separadores: ; y : (solo fuera de paréntesis y strings)
            if paren_depth == 0:
                if char == ';':
                    if current.strip():
                        tokens.append(current.strip())
                    current = ""
                    i += 1
                    continue
                
                if char == ':':
                    current += char
                    if current.strip():
                        tokens.append(current.strip())
                    current = ""
                    i += 1
                    continue
            
            current += char
            i += 1
        
        # Último token
        if current.strip():
            tokens.append(current.strip())
        
        # Post-procesamiento: dividir tokens que contengan closers seguidos de otros statements
        # Ejemplo: "fin craftear x" -> ["fin", "craftear x"]
        final_tokens = []
        for token in tokens:
            final_tokens.extend(self._split_compound_tokens(token))
        
        return final_tokens
    
    def _split_compound_tokens(self, token: str) -> List[str]:
        """
        Divide tokens compuestos donde un closer está seguido de otro statement.
        Ejemplo: "fin craftear x" -> ["fin", "craftear x"]
                 "romper letrero('x')" -> ["romper", "letrero('x')"]
        """
        token = token.strip()
        
        # Lista de closers que podrían estar al inicio
        closers = ['fin', 'romper', 'cosechar', 'boom', 'salir_portal']
        
        for closer in closers:
            if token == closer:
                # Es solo el closer, retornar como está
                return [token]
            
            if token.startswith(closer + ' '):
                # El closer está seguido de algo más
                rest = token[len(closer):].strip()
                if rest:
                    # Recursivamente dividir el resto por si tiene más closers
                    return [closer] + self._split_compound_tokens(rest)
        
        # No es un token compuesto
        return [token]
    
    def _starts_with_keyword(self, token: str, keywords: set) -> bool:
        """Verifica si el token comienza con alguna de las palabras clave"""
        token_lower = token.lower()
        for kw in keywords:
            if token_lower.startswith(kw):
                return True
        return False
    
    def _format_with_indentation(self, tokens: List[str]) -> List[str]:
        """
        Aplica indentación correcta a cada token.
        
        Reglas:
        1. Cada statement termina con ;
        2. Los bloques (mesa_crafteo, observador, etc.) aumentan indentación
        3. comparador/dispensador van al mismo nivel que observador
        4. fin/romper/cosechar/boom cierran el bloque y van al nivel del opener
        """
        formatted = []
        indent_level = 0
        
        for i, token in enumerate(tokens):
            token = token.strip()
            if not token:
                continue
            
            # Determinar el nivel de indentación para esta línea
            current_indent = indent_level
            
            # Si es un cierre de bloque, disminuir indentación ANTES de escribir
            if token in self.block_closers:
                indent_level = max(0, indent_level - 1)
                current_indent = indent_level
            
            # Si es comparador/dispensador, va al mismo nivel que el observador anterior
            # (mismo nivel que el bloque actual, no dentro)
            elif self._starts_with_keyword(token, self.conditional_alternatives):
                # Bajar un nivel temporalmente
                current_indent = max(0, indent_level - 1)
                # Mantener ese nivel para los siguientes statements
                indent_level = current_indent
            
            # Si es caso/defecto en un portal, va al mismo nivel que otros casos
            elif self._starts_with_keyword(token, self.switch_alternatives):
                current_indent = max(0, indent_level - 1)
                indent_level = current_indent
            
            # Aplicar indentación
            indent_str = ' ' * (current_indent * self.indent_size)
            
            # Agregar ; al final si no es una declaración con :
            # Nota: 'fin' y 'romper' NO deben llevar punto y coma según la especificación
            if token.endswith(':'):
                formatted_line = indent_str + token
            elif token in ['fin', 'romper', 'cosechar', 'boom', 'salir_portal']:
                # Closers de bloque permanecen sin punto y coma
                formatted_line = indent_str + token
            else:
                formatted_line = indent_str + token + ';'
            
            formatted.append(formatted_line)
            
            # Si abre un bloque, aumentar indentación para el siguiente
            if token.endswith(':') and self._starts_with_keyword(token, self.block_openers):
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
