# Tasks

## 1. Preparação

- [x] 1.1 Seguir na branch `feat/insumos-lotes-validade` do backend e do
      `frontendweb` (decisão da usuária: mesma branch, sem commit da change
      `insumos-lotes-validade`), com os containers no ar; verificar que
      `GET /api/insumos` já traz `lotes` e que `POST /api/movimentacoes` devolve
      `lotes`.

## 2. Modelo (backend)

- [x] 2.1 Adicionar `origem` à movimentação (padrão `MANUAL`, inclusive para as
      linhas existentes) e `id_movimentacao` ao item de insumo da operação,
      igualar a precisão de `movimentacao_estoque.quantidade` à do saldo,
      gerar a migration no container com a FK nomeada e aplicar; verificar que
      `flask db upgrade` conclui, que o downgrade seguido de upgrade funciona e
      que `flask db check` não aponta diferenças.

## 3. Movimentações (backend)

- [x] 3.1 Separar no serviço a aplicação de uma movimentação sem `commit` e a
      função que a desfaz (saldo, lotes e registro), mantendo o endpoint como
      está; verificar pela API a regressão: entrada com lote, saída comum, saída
      vinculada a operação e descarte continuam respondendo 201 com os mesmos
      saldos.
- [x] 3.2 Devolver `origem` e registrar sempre `MANUAL` no POST; verificar pela
      API os dois cenários de "Origem da movimentação".
- [x] 3.3 Aceitar o filtro `id_atividade_agricola` no histórico; verificar pela
      API os dois cenários de "Filtro do histórico por operação".

## 4. Baixa na operação (backend)

- [x] 4.1 Gerar as saídas ao salvar uma operação concluída, na mesma transação;
      verificar pela API os cinco cenários de "Baixa de estoque ao concluir a
      operação".
- [x] 4.2 Deixar pendente o insumo sem saldo utilizável suficiente, sem baixa
      parcial; verificar pela API o cenário de "Insumo sem saldo suficiente na
      conclusão".
- [x] 4.3 Desfazer e gerar de novo a cada salvamento de operação concluída e
      desfazer na exclusão; verificar pela API os seis cenários de "Devolução ao
      estoque ao alterar operação concluída", conferindo saldos e lotes.
- [x] 4.4 Preservar as saídas manuais; verificar pela API os dois cenários de
      "Saídas manuais preservadas na devolução".
- [x] 4.5 Incluir `baixado`, `id_movimentacao` e `baixa_estoque` na resposta da
      operação; verificar pela API os dois cenários de "Situação da baixa na
      resposta da operação".

## 5. Telas (frontend)

- [x] 5.1 Mapear `baixado`, `id_movimentacao`, `baixa_estoque` e `origem` nos
      tipos, em `api.ts` e em `insumosAdapter.ts`, e criar a consulta das
      movimentações de uma operação; cobrir a tradução com testes e verificar
      que `npm test` passa e que `tsc` não aponta erros novos.
- [x] 5.2 No formulário de atividade, mostrar o saldo utilizável de cada insumo
      escolhido, alertar quando a quantidade o excede e avisar que concluir gera
      a baixa; verificar no navegador que o alerta aparece ao digitar uma
      quantidade maior que o saldo e some ao reduzi-la.
- [x] 5.3 No módulo de Atividades, avisar os insumos pendentes depois de salvar
      e recarregar insumos e movimentações depois de salvar ou excluir;
      verificar no navegador que concluir uma atividade reduz o saldo mostrado
      na tela de Insumos sem recarregar a página, e que o aviso de pendência
      aparece quando falta saldo.
- [x] 5.4 No detalhe da atividade, mostrar a situação de cada insumo e as saídas
      de estoque ligadas à operação; no histórico de movimentações, identificar
      as saídas automáticas. Verificar no navegador que uma atividade concluída
      mostra o insumo como baixado e a saída correspondente, e que essa saída
      aparece identificada no histórico.

## 6. Verificação integrada

- [x] 6.1 Executar o roteiro no navegador: entrada de estoque em lote, atividade
      com dois insumos (um sem saldo), conclusão com aviso, conferência de saldo
      e lote, nova entrada e novo salvamento baixando o pendente, reabertura
      devolvendo tudo e exclusão. Verificar também `npm test`, `tsc` sem erros
      novos e `openspec validate atividades-baixa-estoque --strict`.
- [x] 6.2 Remover os dados de teste criados e verificar pela API que atividades,
      movimentações, lotes e saldos voltaram ao estado inicial.
