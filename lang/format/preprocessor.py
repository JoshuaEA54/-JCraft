"""Preprocesamiento de código para preservar strings y comentarios"""
import re

class CodePreprocessor:
    """Maneja la preservación y restauración de strings y comentarios"""
    
    def __init__(self):
        self.strings = []
        self.comments = []
    
    def clean_code(self, code: str) -> str:
        """Reemplaza strings y comentarios con placeholders"""
        code = self._preserve_strings(code)
        code = self._preserve_comments(code)
        code = self._restore_strings(code)
        return code
    
    def restore_comments(self, code: str) -> str:
        """Restaura los comentarios originales"""
        for i, comment in enumerate(self.comments):
            code = code.replace(f"__COMMENT_{i}__", comment)
        return code
    
    def _preserve_strings(self, code: str) -> str:
        """Guarda strings con placeholders"""
        def save_string(match):
            self.strings.append(match.group(0))
            return f"__STRING_{len(self.strings)-1}__"
        
        code = re.sub(r'"(?:[^"\\]|\\.)*"', save_string, code)
        code = re.sub(r"'(?:[^'\\]|\\.)*'", save_string, code)
        return code
    
    def _preserve_comments(self, code: str) -> str:
        """Guarda comentarios con placeholders y marca los standalone"""
        def save_comment(match):
            self.comments.append(match.group(0))
            return f"__COMMENT_{len(self.comments)-1}__"
        
        code = re.sub(r'#[^\n]*', save_comment, code)
        
        lines = code.split('\n')
        processed_lines = []
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            
            if re.match(r'^__COMMENT_\d+__$', stripped):
                processed_lines.append(f'__STANDALONECOMMENT__{stripped};')
            else:
                processed_lines.append(stripped)
        
        return ' '.join(processed_lines)
    
    def _restore_strings(self, code: str) -> str:
        """Restaura los strings originales"""
        for i, string in enumerate(self.strings):
            code = code.replace(f"__STRING_{i}__", string)
        return code
