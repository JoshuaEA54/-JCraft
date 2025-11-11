"""Postprocesamiento del código formateado"""


class CodePostprocessor:
    """Limpia y organiza el código formateado"""
    
    @staticmethod
    def clean_blank_lines(text: str) -> str:
        """Elimina líneas en blanco excesivas"""
        lines = text.split('\n')
        cleaned = []
        blank_count = 0
        prev_was_fin = False
        
        for line in lines:
            stripped = line.strip()
            
            if not stripped:
                blank_count += 1
                if blank_count <= 1:
                    cleaned.append('')
                continue
            
            if stripped.startswith('mesa_crafteo') and cleaned and prev_was_fin:
                if cleaned[-1].strip():
                    cleaned.append('')
            
            blank_count = 0
            prev_was_fin = stripped.startswith('fin')
            cleaned.append(line)
        
        while cleaned and not cleaned[0].strip():
            cleaned.pop(0)
        
        while cleaned and not cleaned[-1].strip():
            cleaned.pop()
        cleaned.append('')
        
        return '\n'.join(cleaned)
