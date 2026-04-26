
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



### Para rodar os testes:

na pasta raiz ('PL_grupo18') rodar:

- pytest : resumo dos testes
- pytest -v : para ver todos os testes
