"""
Este módulo define um lexer para Fortran 77 usando a biblioteca PLY.
"""

import re
import ply.lex as lex

# ─── Palavras-chave do Fortran 77 ────────────────────────────────────────────
# Mapeamento uppercase → nome do token. t_ID consulta este dicionário para
# decidir se um identificador é uma palavra-chave ou um ID de utilizador.
reserved = {
    'PROGRAM'   : 'PROGRAM',
    'END'       : 'END',
    'STOP'      : 'STOP',
    'INTEGER'   : 'INTEGER',
    'REAL'      : 'REAL',
    'LOGICAL'   : 'LOGICAL',
    'CHARACTER' : 'CHARACTER',
    'DIMENSION' : 'DIMENSION',
    'IF'        : 'IF',
    'THEN'      : 'THEN',
    'ELSE'      : 'ELSE',
    'ENDIF'     : 'ENDIF',
    'DO'        : 'DO',
    'CONTINUE'  : 'CONTINUE',
    'GOTO'      : 'GOTO',
    'PRINT'     : 'PRINT',
    'READ'      : 'READ',
    'WRITE'     : 'WRITE',
    'FUNCTION'  : 'FUNCTION',
    'SUBROUTINE': 'SUBROUTINE',
    'CALL'      : 'CALL',
    'RETURN'    : 'RETURN',
    'COMMON'    : 'COMMON',
    'PARAMETER' : 'PARAMETER',
}

# ─── Lista de tokens ──────────────────────────────────────────────────────────
# PLY exige que a variável 'tokens' esteja definida ao nível do módulo.
# Separamos em categorias para facilitar a leitura e a justificação no relatório.
tokens = list(reserved.values()) + [
    # Literais
    'ID', 'INT_LIT', 'REAL_LIT', 'STRING_LIT', 'BOOL_LIT',
    # Operadores aritméticos
    'PLUS', 'MINUS', 'STAR', 'SLASH', 'POWER',
    # Operadores relacionais e lógicos (todos tratados em t_RELOP)
    'EQ', 'NE', 'LT', 'LE', 'GT', 'GE',
    'AND', 'OR', 'NOT',
    # Pontuação e delimitadores
    'LPAREN', 'RPAREN', 'COMMA', 'EQUALS', 'COLON',
]

# ─── Regras simples — apenas expressão regular ────────────────────────────────
# PLY ordena as regras de string por comprimento decrescente, por isso POWER
# (r'\*\*') é tentado antes de STAR (r'\*'). Não é necessário ordenar manualmente.
t_PLUS   = r'\+'
t_MINUS  = r'-'
t_POWER  = r'\*\*'   # deve estar definido antes de t_STAR para garantir match
t_STAR   = r'\*'
t_SLASH  = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_COMMA  = r','
t_EQUALS = r'='
t_COLON  = r':'

# ─── Operadores relacionais e lógicos ────────────────────────────────────────
# Fortran usa a sintaxe .OP. (ponto-operador-ponto). Uma única função trata todos
# os operadores desta família e despacha para o tipo de token correto.
# Nome anterior 't_GT' era enganoso — renomeado para t_RELOP.
def t_RELOP(t):
    r'\.(GT|LT|GE|LE|EQ|NE|AND|OR|NOT)\.'
    _op_map = {
        '.GT.': 'GT', '.LT.': 'LT', '.GE.': 'GE', '.LE.': 'LE',
        '.EQ.': 'EQ', '.NE.': 'NE',
        '.AND.': 'AND', '.OR.': 'OR', '.NOT.': 'NOT',
    }
    t.type = _op_map[t.value.upper()]
    return t

# ─── Booleanos ────────────────────────────────────────────────────────────────
# Deve ser definido antes de t_RELOP no ficheiro para ter prioridade no PLY
# (funções são ordenadas por linha de definição). Convertemos já para bool Python.
def t_BOOL_LIT(t):
    r'\.(TRUE|FALSE)\.'
    t.value = (t.value.upper() == '.TRUE.')
    return t

# ─── Literais numéricos ───────────────────────────────────────────────────────
# REAL_LIT deve estar antes de INT_LIT: '3.14' seria consumido como INT_LIT '3'
# seguido de outros tokens se INT_LIT tivesse prioridade.
# O PLY dá prioridade a funções sobre strings; dentro das funções, a ordem é
# definida pela posição no ficheiro.
def t_REAL_LIT(t):
    r'\d+\.\d*([Ee][+-]?\d+)?|\d+[Ee][+-]?\d+'
    t.value = float(t.value)
    return t

def t_INT_LIT(t):
    r'\d+'
    t.value = int(t.value)
    return t

# ─── Strings ──────────────────────────────────────────────────────────────────
# Fortran usa aspas simples. Removemos as aspas delimitadoras já no lexer.
def t_STRING_LIT(t):
    r"'[^']*'"
    t.value = t.value[1:-1]
    return t

# ─── Identificadores e palavras-chave ─────────────────────────────────────────
# Fortran é case-insensitive: convertemos tudo para uppercase e consultamos
# o dicionário 'reserved'. Se o identificador não for uma palavra-chave, o tipo
# fica 'ID'.
def t_ID(t):
    r'[A-Za-z][A-Za-z0-9_]*'
    t.value = t.value.upper()
    t.type  = reserved.get(t.value, 'ID')
    return t

# ─── Comentários ─────────────────────────────────────────────────────────────
# Suportamos apenas comentários com '!' (free-form standard).
# A função não devolve 't', pelo que o token é descartado silenciosamente.
# Nota: suporte a 'C' na coluna 1 foi removido — ver cabeçalho do ficheiro.
def t_COMMENT(t):
    r'![^\n]*'
    pass

# ─── Newlines ─────────────────────────────────────────────────────────────────
# Não emitimos um token NEWLINE — o parser delimita instruções pela gramática.
# Apenas incrementamos o contador de linhas para mensagens de erro precisas.
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# ─── Ignorados ────────────────────────────────────────────────────────────────
# Espaços, tabs e carriage returns são descartados pelo PLY antes de tentar
# qualquer regra de token.
t_ignore = ' \t\r'

# ─── Erros ────────────────────────────────────────────────────────────────────
def t_error(t):
    print(f"Erro léxico — linha {t.lineno}: carácter ilegal '{t.value[0]}'")
    t.lexer.skip(1)

# ─── Fábrica pública ──────────────────────────────────────────────────────────
def build_lexer():
    """
    Constrói e devolve uma instância fresca do lexer PLY.

    Usar esta função em vez de importar o lexer diretamente garante que cada
    chamada (em testes ou no compilador) obtém um lexer com estado limpo
    (lineno=1, sem input residual).
    """
    return lex.lex(reflags=re.MULTILINE | re.IGNORECASE)


# ─── Ponto de entrada para teste rápido manual ───────────────────────────────
if __name__ == '__main__':
    _code = """\
PROGRAM FATORIAL
  INTEGER N, I, FAT
  FAT = 1
  DO 10 I = 1, N
    FAT = FAT * I
10 CONTINUE
  PRINT *, 'Fatorial:', FAT
END
"""
    _lexer = build_lexer()
    _lexer.input(_code)
    for tok in _lexer:
        print(tok)