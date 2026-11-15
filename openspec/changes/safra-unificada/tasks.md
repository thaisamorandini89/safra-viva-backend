# Tasks

## 1. Preparação

- [ ] 1.1 Criar a branch `feat/safra-unificada` no backend e no `frontendweb`, a
      partir de uma base que já contenha a change `financeiro-ponta-a-ponta`,
      com os containers no ar e as migrations aplicadas; verificar que
      `PUT /api/safras/{id}` e `DELETE /api/safras/{id}` existem e que
      `GET /api/atividades` responde 200.

## 2. Modelo (backend)

- [ ] 2.1 Adicionar `id_safra` à operação agrícola e à movimentação de estoque,
      gerar a migration no container com as FKs nomeadas e aplicar; verificar
      que `flask db upgrade` conclui, que o downgrade seguido de upgrade
      funciona, que `flask db check` não aponta diferenças e que os registros
      existentes mantêm a safra em texto.

## 3. Atividades (backend)

- [ ] 3.1 Aceitar, validar e devolver `id_safra` na operação, com `safra`
      derivado do cadastro; verificar pela API os cenários "Operação criada com
      safra cadastrada", "Safra inexistente" e "Safra removida da operação".
- [ ] 3.2 Exigir a mesma propriedade no estado final; verificar pela API os dois
      cenários de "Safra da mesma propriedade da operação".
- [ ] 3.3 Preservar o texto dos registros anteriores; verificar pela API os três
      cenários de "Safra em texto dos registros anteriores" e a regressão: um
      `POST /api/atividades` só com `safra` em texto continua respondendo 201.
- [ ] 3.4 Aceitar o filtro `id_safra`; verificar pela API o cenário de "Filtro
      de operações por safra cadastrada".
- [ ] 3.5 Levar a safra da operação à saída gerada pela conclusão; verificar
      pela API o cenário "Saída gerada com a safra da operação" e a regressão:
      reabrir a operação continua devolvendo o saldo ao estoque.

## 4. Movimentações e safra (backend)

- [ ] 4.1 Aceitar e devolver `id_safra` na saída; verificar pela API os quatro
      cenários de "Safra cadastrada na saída".
- [ ] 4.2 Conferir a propriedade do talhão e a safra da operação vinculada;
      verificar pela API os três cenários de "Coerência da safra com o talhão e
      a operação".
- [ ] 4.3 Recusar a exclusão da safra usada por operação ou movimentação;
      verificar pela API os dois cenários de "Safra em uso por operações e
      movimentações" e a regressão: a safra sem uso continua sendo excluída.

## 5. Telas (frontend)

- [ ] 5.1 Mapear `id_safra` nos tipos, em `api.ts` e em `insumosAdapter.ts`, e
      deixar de enviar a safra em texto; cobrir a tradução com testes e
      verificar que `npm test` passa e que `tsc` não aponta erros novos.
- [ ] 5.2 No formulário de atividade, trocar o campo de safra pelo combo das
      safras da propriedade do talhão, mostrando o texto antigo nos registros
      anteriores; verificar no navegador que o combo só lista safras da
      propriedade do talhão, que trocar o talhão para outra propriedade limpa a
      safra, que a atividade salva mostra a safra na lista e que editar a
      atividade com safra em texto sem mexer no combo mantém o texto.
- [ ] 5.3 No formulário de saída de estoque, trocar o campo de safra pelo combo
      e preencher e travar a safra ao escolher a atividade; verificar no
      navegador que a saída salva aparece no histórico com o nome da safra e
      que o filtro de safra das movimentações continua funcionando.

## 6. Verificação integrada

- [ ] 6.1 Executar o roteiro no navegador: cadastrar uma safra, criar uma
      atividade com ela, concluir com um insumo e conferir a safra na saída
      gerada, lançar uma despesa na mesma safra e conferir que a exclusão da
      safra é barrada. Verificar também `npm test`, `tsc` sem erros novos e
      `openspec validate safra-unificada --strict`.
- [ ] 6.2 Remover os dados de teste criados e verificar pela API que safras,
      atividades, movimentações e lançamentos voltaram ao estado inicial.
