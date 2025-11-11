"""Formateador principal de código :JCraft"""
from .preprocessor import CodePreprocessor
from .tokenizer import Tokenizer
from .indenter import Indenter
from .postprocessor import CodePostprocessor


class JCraftFormatter:
    """Formateador de código :JCraft"""
    
    def __init__(self, indent_size: int = 4):
        self.indent_size = indent_size
        self.preprocessor = CodePreprocessor()
        self.indenter = Indenter(indent_size)
        self.postprocessor = CodePostprocessor()
    
    def format(self, code: str) -> str:
        """Formatea el código :JCraft completo"""
        cleaned = self.preprocessor.clean_code(code)
        tokens = Tokenizer.tokenize(cleaned)
        formatted_lines = self.indenter.format_with_indentation(tokens)
        result = '\n'.join(formatted_lines)
        result = self.postprocessor.clean_blank_lines(result)
        result = self.preprocessor.restore_comments(result)
        return result


def format_jcraft_code(code: str, indent_size: int = 4) -> str:
    """Función auxiliar para formatear código :JCraft"""
    formatter = JCraftFormatter(indent_size)
    return formatter.format(code)
