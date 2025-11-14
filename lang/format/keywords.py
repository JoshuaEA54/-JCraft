"""Definición de palabras clave del lenguaje :JCraft"""

BLOCK_OPENERS = {
    'mesa_crafteo', 'observador', 'comparador', 'dispensador',
    'spawner', 'cultivar', 'creeper', 'portal', 'caso', 'defecto'
}

BLOCK_CLOSERS = {
    'fin', 'romper', 'cosechar', 'salir_portal'
}

CONDITIONAL_ALTERNATIVES = {'comparador', 'dispensador'}

SWITCH_ALTERNATIVES = {'caso', 'defecto'}

OPENERS_REQUIRE_PAREN = {'observador', 'portal', 'comparador', 'spawner', 'cultivar'}
