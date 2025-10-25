from lang.lexer import tokenize
from lang.parser import Parser
from lang.interpreter import Interpreter

codigo = '''
mesa_crafteo vacío main():
    inventario<bloques> xs = [1, 2, 3];
    letrero "Primer: " + xs[0];
fin
'''

print("Tokenizando...")
tokens = tokenize(codigo)
print(f"Tokens: {len(tokens)}")

print("\nParseando...")
parser = Parser(tokens)
ast = parser.parse()
print(f"AST: {ast}")

print("\nEjecutando...")
interp = Interpreter(debug=True)
interp.run(ast)
print('\nResults:', interp.results)
