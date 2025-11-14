"""Tokenizador de código :JCraft"""
import re
from typing import List


class Tokenizer:
    """Divide el código en tokens individuales"""
    
    @staticmethod
    def tokenize(code: str) -> List[str]:
        """Tokeniza el código respetando strings, paréntesis y llaves"""
        raw_tokens = Tokenizer._split_by_separators(code)
        final_tokens = []
        for token in raw_tokens:
            final_tokens.extend(Tokenizer._split_compound_tokens(token))
        return final_tokens
    
    @staticmethod
    def _split_by_separators(code: str) -> List[str]:
        """Divide por ';' y ':' respetando estructuras anidadas"""
        tokens = []
        current_token = ""
        in_string = False
        string_char = None
        escape_next = False
        paren_depth = 0
        brace_depth = 0
        
        i = 0
        while i < len(code):
            char = code[i]
            
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
            
            if char in ('"', "'"):
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False
                    string_char = None
                current_token += char
                i += 1
                continue
            
            if in_string:
                current_token += char
                i += 1
                continue
            
            if char == '(':
                paren_depth += 1
            elif char == ')':
                paren_depth -= 1
            elif char == '{':
                brace_depth += 1
            elif char == '}':
                brace_depth -= 1
            
            if paren_depth == 0 and brace_depth == 0:
                if char == ';':
                    lookahead = code[i+1:].lstrip()
                    if lookahead.startswith('__COMMENT_'):
                        current_token += char
                        i += 1
                        while i < len(code) and code[i] in ' \t':
                            current_token += code[i]
                            i += 1
                        match = re.match(r'(__COMMENT_\d+__)', code[i:])
                        if match:
                            current_token += match.group(1)
                            i += len(match.group(1))
                        if current_token.strip():
                            tokens.append(current_token.strip())
                        current_token = ""
                        continue
                    
                    if current_token.strip():
                        tokens.append(current_token.strip())
                    current_token = ""
                    i += 1
                    continue
                
                if char == ':':
                    current_token += char
                    if current_token.strip():
                        tokens.append(current_token.strip())
                    current_token = ""
                    i += 1
                    continue
            
            current_token += char
            i += 1
        
        if current_token.strip():
            tokens.append(current_token.strip())
        
        return tokens
    
    @staticmethod
    def _split_compound_tokens(token: str) -> List[str]:
        """Separa closers que están pegados a otros statements"""
        token = token.strip()
        closers = ['fin', 'romper', 'cosechar', 'salir_portal']
        
        for closer in closers:
            if token == closer:
                return [token]
            
            if token.startswith(closer + ' '):
                rest = token[len(closer):].strip()
                if rest:
                    return [closer] + Tokenizer._split_compound_tokens(rest)
        
        return [token]
