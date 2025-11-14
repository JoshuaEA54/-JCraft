"""Gestión de indentación de código"""
import re
from typing import List
from .keywords import (BLOCK_OPENERS, BLOCK_CLOSERS, SWITCH_ALTERNATIVES,
                        OPENERS_REQUIRE_PAREN)


class Indenter:
    """Aplica indentación correcta al código"""
    
    def __init__(self, indent_size: int = 4):
        self.indent_size = indent_size
    
    def format_with_indentation(self, tokens: List[str]) -> List[str]:
        """Aplica indentación a los tokens"""
        formatted = []
        indent_level = 0
        inside_portal = 0
        inside_case = False
        
        for token in tokens:
            token = token.strip()
            if not token:
                continue
            
            if token.startswith('__STANDALONECOMMENT__'):
                formatted.append(self._format_standalone_comment(token, indent_level))
                continue
            
            comment_match = re.search(r'(__COMMENT_\d+__)', token)
            if comment_match:
                line, indent_level, inside_portal, inside_case = self._format_token_with_comment(
                    token, comment_match, indent_level, inside_portal, inside_case
                )
                formatted.append(line)
                continue
            
            line, indent_level, inside_portal, inside_case = self._format_token(
                token, indent_level, inside_portal, inside_case
            )
            formatted.append(line)
        
        return formatted
    
    def _format_standalone_comment(self, token: str, indent_level: int) -> str:
        """Formatea un comentario standalone"""
        comment_placeholder = token.replace('__STANDALONECOMMENT__', '').strip()
        indent_str = ' ' * (indent_level * self.indent_size)
        return indent_str + comment_placeholder
    
    def _format_token_with_comment(self, token: str, comment_match, indent_level: int,
                                   inside_portal: int, inside_case: bool):
        """Formatea un token que contiene comentario inline"""
        comment_placeholder = comment_match.group(1)
        code_part = token.replace(comment_placeholder, '').strip()
        if code_part.endswith(';'):
            code_part = code_part[:-1].strip()
        
        indent_level, inside_portal, inside_case = self._adjust_indent_before(
            code_part, indent_level, inside_portal, inside_case
        )
        
        indent_str = ' ' * (indent_level * self.indent_size)
        
        if code_part.endswith(':'):
            formatted_line = indent_str + code_part + '  ' + comment_placeholder
        elif code_part in BLOCK_CLOSERS:
            formatted_line = indent_str + code_part + '  ' + comment_placeholder
        else:
            formatted_line = indent_str + code_part + ';  ' + comment_placeholder
        
        indent_level, inside_portal, inside_case = self._adjust_indent_after(
            code_part, indent_level, inside_portal, inside_case
        )
        
        return formatted_line, indent_level, inside_portal, inside_case
    
    def _format_token(self, token: str, indent_level: int, inside_portal: int, inside_case: bool):
        """Formatea un token sin comentario"""
        indent_level, inside_portal, inside_case = self._adjust_indent_before(
            token, indent_level, inside_portal, inside_case
        )
        
        indent_str = ' ' * (indent_level * self.indent_size)
        
        if token.endswith(':'):
            formatted_line = indent_str + token
        elif token in BLOCK_CLOSERS:
            formatted_line = indent_str + token
        else:
            formatted_line = indent_str + token + ';'
        
        indent_level, inside_portal, inside_case = self._adjust_indent_after(
            token, indent_level, inside_portal, inside_case
        )
        
        return formatted_line, indent_level, inside_portal, inside_case
    
    def _adjust_indent_before(self, token: str, indent_level: int, inside_portal: int, inside_case: bool):
        """Ajusta indentación antes de imprimir el token"""
        is_boom_closer = bool(re.match(r'^boom\b\s*\(', token.lower()))
        is_dispensador = token.lower().lstrip().startswith('dispensador')
        is_comparador_with_paren = self._keyword_followed_by(token, {'comparador'}, ['('])
        is_romper = token == 'romper'
        is_salir_portal = token == 'salir_portal'
        is_switch_alternative = self._starts_with_keyword(token, SWITCH_ALTERNATIVES)
        
        if (token in BLOCK_CLOSERS or is_boom_closer or is_comparador_with_paren or
            is_dispensador or (is_switch_alternative and inside_case)):
            if is_romper and inside_portal > 0:
                pass
            else:
                indent_level = max(0, indent_level - 1)
                if is_salir_portal and inside_portal > 0:
                    if inside_case:
                        indent_level = max(0, indent_level - 1)
                    inside_portal -= 1
                    inside_case = False
        
        return indent_level, inside_portal, inside_case
    
    def _adjust_indent_after(self, token: str, indent_level: int, inside_portal: int, inside_case: bool):
        """Ajusta indentación después de imprimir el token"""
        if token.endswith(':') and self._starts_with_keyword(token, BLOCK_OPENERS):
            if token.lower().lstrip().startswith('portal'):
                inside_portal += 1
                inside_case = False
            
            if self._starts_with_keyword(token, SWITCH_ALTERNATIVES):
                inside_case = True
            
            opener_ok = True
            for kw in OPENERS_REQUIRE_PAREN:
                if token.lower().lstrip().startswith(kw):
                    if not self._keyword_has_paren_after(token, kw):
                        opener_ok = False
                    break
            if opener_ok:
                indent_level += 1
        
        return indent_level, inside_portal, inside_case
    
    @staticmethod
    def _starts_with_keyword(token: str, keywords: set) -> bool:
        """Verifica si el token comienza con alguna keyword"""
        token_lower = token.lower().lstrip()
        for kw in keywords:
            if token_lower.startswith(kw):
                after = token_lower[len(kw):]
                if after == '' or after[0].isspace() or after[0] in '(:':
                    return True
        return False
    
    @staticmethod
    def _keyword_followed_by(token: str, keywords: set, follow_chars: List[str]) -> bool:
        """Verifica si keyword está seguida por algún caracter específico"""
        token_lower = token.lower().lstrip()
        for kw in keywords:
            if token_lower.startswith(kw):
                after = token_lower[len(kw):].lstrip()
                for ch in follow_chars:
                    if after.startswith(ch):
                        return True
        return False
    
    @staticmethod
    def _keyword_has_paren_after(token: str, kw: str) -> bool:
        """Comprueba si keyword está seguida por '('"""
        token_lower = token.lower().lstrip()
        if token_lower.startswith(kw):
            after = token_lower[len(kw):].lstrip()
            return after.startswith('(')
        return False
