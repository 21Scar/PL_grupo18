# Processamento de Linguagens - Trabalho Prático

## 1. Introdução
Este documento detalha o desenvolvimento de um compilador para a linguagem Fortran 77 (standard ANSI X3.9-1978). O objetivo principal é analisar e traduzir código fonte Fortran, passando por fases de análise léxica, sintática, semântica e, por fim, a geração de código para uma Máquina Virtual (VM)[cite: 2].

## 2. Arquitetura do Compilador e Decisões de Implementação
Para garantir que o código se mantém organizado e modular, dividimos o projeto em ficheiros distintos dentro do diretório `src/`. A linguagem de implementação escolhida foi Python, suportada pelas bibliotecas requeridas.

### 2.1 Análise Léxica (`lexer.py`)
* **Implementação:** O analisador léxico foi construído utilizando a ferramenta `ply.lex`[cite: 2].
* **Justificação:** O `ply.lex` permite definir expressões regulares de forma clara para identificar palavras-chave da linguagem (como `PROGRAM`, `INTEGER`, `IF`, `DO`), identificadores, números e operadores[cite: 2]. A separação num ficheiro independente (`lexer.py`)[cite: 1] facilita a manutenção e os testes unitários isolados dos tokens gerados.

### 2.2 Análise Sintática (`parser.py`) e Árvore de Sintaxe Abstrata (`ast_nodes.py`)
* **Implementação:** A validação da estrutura gramatical foi implementada com a ferramenta `ply.yacc`[cite: 2] no ficheiro `parser.py`[cite: 1].
* **Decisão Arquitetónica (AST):** Em vez de processar o código diretamente no parser, tomámos a decisão de construir uma Árvore de Sintaxe Abstrata (Abstract Syntax Tree - AST), cujos nós estão definidos no ficheiro `ast_nodes.py`[cite: 1]. 
* **Justificação:** A utilização de uma AST é uma prática recomendada em construção de compiladores pois cria uma representação intermédia estruturada. Isto vai facilitar imenso as próximas fases do projeto[cite: 2], nomeadamente a análise semântica (verificação de tipos) e a posterior tradução para código da Máquina Virtual[cite: 2], além de permitir futuras otimizações de código[cite: 2].

## 3. Estratégia de Testes
* **Implementação:** Os testes foram colocados no diretório `test/`, utilizando a framework `pytest` (comprovado pela diretoria `.pytest_cache` e os ficheiros de testes gerados)[cite: 1].
* **Justificação:** Criámos ficheiros de teste separados para os diferentes módulos, nomeadamente `test_lexer.py` e `test_parser.py`[cite: 1]. Esta abordagem de *Test-Driven Development* (ou testes automatizados) permite verificar a correção do compilador a cada alteração[cite: 2]. Ao testar o Lexer e o Parser isoladamente, conseguimos identificar rapidamente se um erro provém de um token mal reconhecido ou de uma regra gramatical inválida.

## 4. Próximos Passos (Trabalho Futuro)
Nas próximas iterações, o foco será:
1. **Análise Semântica:** Implementar a validação de coerência, como a verificação de tipos e a correspondência dos labels nos ciclos `DO` com os comandos `CONTINUE`[cite: 2].
2. **Geração de Código:** Percorrer a AST (criada em `ast_nodes.py`[cite: 1]) para converter as estruturas lógicas diretamente em instruções da Máquina Virtual[cite: 2].