import ply.lex as lex
import re

# ─── Palavras-chave do Fortran 77 ───────────────────────────────────────────
reserved = {
    'PROGRAM': 'PROGRAM', 'END': 'END', 'STOP': 'STOP',
    'INTEGER': 'INTEGER', 'REAL': 'REAL', 'LOGICAL': 'LOGICAL',
    'CHARACTER': 'CHARACTER', 'DIMENSION': 'DIMENSION',
    'IF': 'IF', 'THEN': 'THEN', 'ELSE': 'ELSE', 'ENDIF': 'ENDIF',
    'DO': 'DO', 'CONTINUE': 'CONTINUE', 'GOTO': 'GOTO',
    'PRINT': 'PRINT', 'READ': 'READ', 'WRITE': 'WRITE',
    'FUNCTION': 'FUNCTION', 'SUBROUTINE': 'SUBROUTINE',
    'CALL': 'CALL', 'RETURN': 'RETURN',
    'COMMON': 'COMMON', 'PARAMETER': 'PARAMETER',
}

tokens = list(reserved.values()) + [
    # Literais
    'ID', 'INT_LIT', 'REAL_LIT', 'STRING_LIT', 'BOOL_LIT',
    # Operadores aritméticos
    'PLUS', 'MINUS', 'STAR', 'SLASH', 'POWER',
    # Operadores relacionais e lógicos
    'EQ', 'NE', 'LT', 'LE', 'GT', 'GE',
    'AND', 'OR', 'NOT',
    # Símbolos
    'LPAREN', 'RPAREN', 'COMMA', 'EQUALS',
    'COLON',
]

# ─── Regras simples (apenas regex) ──────────────────────────────────────────
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_POWER   = r'\*\*'
t_STAR    = r'\*'
t_SLASH   = r'/'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_COMMA   = r','
t_EQUALS  = r'='
t_COLON   = r':'

# ─── Operadores relacionais (Fortran usa .XX.) ───────────────────────────────
def t_GT(t):
    r'\.(GT|LT|GE|LE|EQ|NE|AND|OR|NOT)\.'
    ops = {
        '.GT.': 'GT', '.LT.': 'LT', '.GE.': 'GE', '.LE.': 'LE',
        '.EQ.': 'EQ', '.NE.': 'NE',
        '.AND.': 'AND', '.OR.': 'OR', '.NOT.': 'NOT',
    }
    t.type = ops[t.value.upper()]
    return t

def t_BOOL_LIT(t):
    r'\.(TRUE|FALSE)\.'
    t.value = t.value.upper() == '.TRUE.'
    return t

# ─── Literais numéricos ──────────────────────────────────────────────────────
def t_REAL_LIT(t):
    r'\d+\.\d*([Ee][+-]?\d+)?|\d+[Ee][+-]?\d+'
    t.value = float(t.value)
    return t

def t_INT_LIT(t):
    r'\d+'
    t.value = int(t.value)
    return t

# ─── Strings ─────────────────────────────────────────────────────────────────
def t_STRING_LIT(t):
    r"'[^']*'"
    t.value = t.value[1:-1]   # remove as aspas
    return t

# ─── Identificadores e palavras-chave ────────────────────────────────────────
def t_ID(t):
    r'[A-Za-z][A-Za-z0-9_]*'
    t.type = reserved.get(t.value.upper(), 'ID')
    t.value = t.value.upper()   # Fortran é case-insensitive
    return t

# ─── Comentários ─────────────────────────────────────────────────────────────
def t_COMMENT(t):
    r'![^\n]*'              # comentários com !  (formato livre)
    pass                    # descarta o token

def t_COMMENT_C(t):
    r'^[Cc][^\n]*'         # comentários com C na coluna 1 (formato fixo)
    pass

# ─── Newlines e espaços ───────────────────────────────────────────────────────
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore = ' \t\r'

# ─── Erros ───────────────────────────────────────────────────────────────────
def t_error(t):
    print(f"Linha {t.lineno}: caracter ilegal '{t.value[0]}'")
    t.lexer.skip(1)

# ─── Construção do lexer ──────────────────────────────────────────────────────
lexer = lex.lex(reflags=re.MULTILINE | re.IGNORECASE)

# ─── Teste rápido ─────────────────────────────────────────────────────────────
if __name__ == '__main__':
    code = """
PROGRAM FATORIAL
  INTEGER N, FAT
  FAT = 1
  DO 10 I = 1, N
    FAT = FAT * I
10 CONTINUE
  PRINT *, 'Fatorial:', FAT
END
"""
    lexer.input(code)
    for tok in lexer:
        print(tok)

# Nota:
# Nesta fase optamos por suportar free form para simplificar e acelerar a
# implementacao do lexer/parser com PLY. O foco inicial e validar os tokens,
# a gramatica base e a pipeline do compilador. O suporte a fixed form de
# Fortran 77 pode ser adicionado depois como extensao/pre-processamento.

#comando: & c:/python314/python.exe lexer.py