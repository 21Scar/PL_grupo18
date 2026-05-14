
### Decisões de design documentadas:




-   **Formato suportado**: free-form apenas. O Fortran 77 original usa colunas fixas
    (código na col. 7+, labels nas cols. 1-5, continuação na col. 6), mas o PLY
    não tem suporte nativo a regras posicionais. Optámos por free-form para manter
    o foco no compilador em si; esta decisão está registada no relatório.

-   **Comentários**: apenas o estilo '!' (free-form). A sintaxe de 'C' na coluna 1 foi
    removida porque o PLY não garante que âncoras de linha ('^') funcionem
    corretamente dentro do seu motor de regex combinado. Tentar suportá-la criava
    um bug silencioso: linhas começadas por 'C' eram tokenizadas como identificador.

-   **Normalização de maiúsculas**: todos os identificadores são convertidos para
    uppercase em t_ID. O Fortran é case-insensitive por especificação, e trabalhar
    sempre em uppercase simplifica o parser e a tabela de símbolos.

-   **Newlines**: consumidos silenciosamente (apenas incrementam lineno). O parser
    delimita instruções pela gramática e não por tokens de fim-de-linha, o que
    evita ter de lidar com newlines opcionais em cada regra gramatical.

-   **Testabilidade**: o lexer é criado através de build_lexer() em vez de ser
    instanciado ao nível do módulo. Isto permite que os testes criem instâncias
    independentes sem estado partilhado entre testes.

- **Corpus dos testes**: a suite de testes inclui 125 testes unitários cobrindo:
  - Lexer: 14 classes com testes de palavras-chave, literais, operadores, comentários
  - Parser: 14 classes com testes de programa, declarações, expressões, controlo de fluxo
  - Semântica: 8 classes com testes de tabela de símbolos, resolução FuncCall/ArrayRef, validação de labels e tipos
  - Geração de código: validação de tradução para EWVM (vide `src/codegen.py`)

na pasta raiz ('PL_grupo18') rodar:

- pytest : resumo dos testes
- pytest -v : para ver todos os testes

---
---

## Análise Semântica (Análise Semântica)

### Ferramenta utilizada
`ply.yacc` — gerador de parsers LALR(1) integrado com o PLY.

### Estrutura da AST
A AST é composta por nós Python definidos em `src/ast_nodes.py` usando
`dataclasses`. A hierarquia divide-se em:
- **Nós de programa**: `Program`, `FunctionDef`, `SubroutineDef`
- **Nós de instrução**: `Assign`, `DoLoop`, `IfThen`, `GotoStmt`, `PrintStmt`, `ReadStmt`, `Continue`, `StopStmt`, `ReturnStmt`, `CallStmt`
- **Nós de expressão**: `BinOp`, `UnaryOp`, `ID`, `IntLit`, `RealLit`, `StrLit`, `BoolLit`, `FuncCall`, `ArrayRef`

### Decisões de design

- **`ArrayRef` vs `FuncCall`**: em Fortran, `NUMS(I)` pode ser um acesso a
  array ou uma chamada de função — a sintaxe é idêntica. O parser gera sempre
  `FuncCall`; a análise semântica distingue consultando a tabela de símbolos.

- **Ciclo DO**: o body entre `DO label` e `label CONTINUE` é recolhido pela
  regra `do_stmt : DO INT_LIT ID EQUALS expr COMMA expr stmt_list INT_LIT CONTINUE`.
  A correspondência entre labels é validada na análise semântica.

- **Precedência de operadores**: definida explicitamente na tabela `precedence`
  do PLY, seguindo a especificação ANSI X3.9-1978 (aritméticos > relacionais > lógicos).

- **Normalização de maiúsculas**: herdada do lexer — todos os identificadores
  chegam ao parser em uppercase, pelo que as regras gramaticais não precisam
  de lidar com variações de capitalização.

- **Newlines**: não são emitidos como tokens (decisão do lexer). O parser
  delimita instruções pela gramática, sem regras de fim-de-linha explícitas.

### Problemas conhecidos (a resolver)

- **Conflito `ArrayRef` vs `FuncCall`**: as regras `expr : ID LPAREN expr_list RPAREN`
  e `array_ref : ID LPAREN expr_list RPAREN` têm o mesmo padrão, gerando um
  conflito shift/reduce no PLY. A correção é eliminar `ArrayRef` do parser e
  usar exclusivamente `FuncCall`, delegando a distinção à análise semântica.
  **Localização**: `src/parser.py`, funções `p_expr_func_call` e `p_array_ref`.

- **Ciclo DO com body vazio**: a implementação atual de `p_do_stmt` não recolhe
  as instruções entre `DO` e o `CONTINUE` correspondente — o campo `body` fica
  sempre vazio. A gramática precisa de ser reformulada para consumir o body
  diretamente, ou introduzir um pré-processador que agrupe essas instruções
  antes de as passar ao parser.
  **Localização**: `src/parser.py`, função `p_do_stmt`.

- **Conflito na `labeled_stmt`**: a regra `labeled_stmt : INT_LIT stmt` é
  ambígua em LALR(1) porque um `INT_LIT` no início de uma linha pode ser
  confundido com o início de uma expressão. Possíveis soluções: emitir um
  token `LABEL` distinto no lexer (exige detetar posição na linha), ou tratar
  labels num pré-processador antes do parser.
  **Localização**: `src/parser.py`, função `p_labeled_stmt`; possivelmente
  também `src/lexer.py`.

- **`PRINT` e `READ` com `STAR`**: o `*` em `PRINT *, ...` pode gerar conflitos
  com o operador de multiplicação se o PLY tentar aplicar a regra de `BinOp`
  nesse contexto. A correção passa por uma regra dedicada que consuma o `STAR`
  como indicador de formato livre antes de tentar reduzi-lo como operador.
  **Localização**: `src/parser.py`, funções `p_print_stmt` e `p_read_stmt`.


### Limitações documentadas

Registamos as seguintes limitações que permanecem na implementação actual; foram consideradas aceitáveis para a entrega mínima do projecto e estão documentadas para futura evolução:

- **Subprogramas no codegen não implementados**: o suporte sintáctico a `CALL` existe, mas `src/codegen.py` lanza `NotImplementedError` para chamadas a subrotinas/funções porque ainda não implementámos o modelo de frames e calling convention. O enunciado trata subprogramas como valorização opcional.
- **Arrays apenas 1D**: a implementação de arrays suporta apenas uma dimensão (declarações `ID(N)`). Multidimensionalidade fica para uma fase posterior.
- **Verificação de tipos parcial**: a análise semântica valida declarações e resolve ambiguidade `FuncCall`/`ArrayRef`, mas a verificação completa de compatibilidade de tipos em expressões binárias não está totalmente implementada (actualmente há heurísticas e avisos em vez de erros em alguns casos).


### Testes
Os testes do parser estão por implementar (`tests/test_parser.py`). Serão
estruturados de forma análoga a `tests/test_lexer.py`, verificando a estrutura
dos nós AST produzidos para cada construção da linguagem (atribuições,
expressões, controlo de fluxo, declarações). Os problemas conhecidos acima
serão corrigidos antes de os testes serem escritos.


### Validação de exemplos na EWVM

Foram incluídos os ficheiros de exemplo em Fortran e os respetivos ficheiros VM, conforme exigido no enunciado:

- `examples/hello.f` -> `examples/hello.vm`
- `examples/factorial.f` -> `examples/factorial.vm`
- `examples/somaarr.f` -> `examples/somaarr.vm`
- `examples/prime.f` -> `examples/prime.vm`
- `examples/fib.f` -> `examples/fib.vm`

Compilação dos exemplos:

- `python scripts/generate_examples.py`

Validação manual executada na EWVM:

- `hello.vm` imprime `Hello, World!`
- `factorial.vm` imprime `120`
- `somaarr.vm` imprime `15`
- `prime.vm` imprime `PRIME` (para `N=7`)
- `fib.vm` imprime a sequência `0 1 1 2 3 5` (para `N=6`)



