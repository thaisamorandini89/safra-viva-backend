# Tasks

## 1. Preparação

- [x] 1.1 Criar a branch `fix/atividades-correcoes-integracao` a partir de
      `homolog` no backend e no `frontendweb` e subir os containers; verificar
      que `GET /api/atividades/status-opcoes` responde 200 pelo proxy do
      frontend (porta 5173).

## 2. Regras da operação agrícola (backend)

- [x] 2.1 Incluir `nome_propriedade` na serialização da operação; verificar que
      `POST /api/atividades` sem `id_propriedade` e `GET /api/atividades`
      devolvem o nome da propriedade do talhão.
- [x] 2.2 Validar, sobre o estado resultante de criação e atualização, que o
      tipo pertence à categoria; verificar pela API os três cenários de
      "Consistência entre tipo e categoria" (400, 400, 200).
- [x] 2.3 Validar que `Concluída` exige `data_fim` na criação e na atualização;
      verificar pela API os quatro cenários de "Data de término para operação
      concluída".
- [x] 2.4 Recusar operação duplicada (talhão, tipo e data de início) na criação
      e na atualização, ignorando a própria operação; verificar pela API os
      quatro cenários de "Unicidade da operação".
- [x] 2.5 Calcular `atrasada` com a data local (`APP_TIMEZONE`, padrão
      `America/Sao_Paulo`); verificar no container que a data usada é a local
      quando a data UTC já virou e, pela API, que prazo de ontem devolve
      `atrasada` verdadeiro, prazo de hoje devolve falso e os indicadores
      acompanham.

## 3. Exclusão de catálogos em uso (backend)

- [x] 3.1 Categoria: recusar a exclusão quando houver tipo ou operação
      vinculados e responder 400; verificar pela API os quatro cenários de
      "Exclusão de categoria em uso" (400, 400, 200, 404).
- [x] 3.2 Tipo: recusar a exclusão quando houver operação ou movimentação de
      estoque vinculada e responder 400; verificar pela API os quatro cenários
      de "Exclusão de tipo em uso".
- [x] 3.3 Máquina: recusar a exclusão quando constar em alguma operação e
      responder 400; verificar pela API os três cenários de "Exclusão de máquina
      em uso".

## 4. Movimentação vinculada à operação (backend)

- [x] 4.1 Adicionar `id_atividade_agricola` (FK opcional, `ON DELETE SET NULL`)
      ao modelo da movimentação e, ao schema, `id_atividade_agricola` (apenas em
      SAIDA) e `data_movimentacao` (data opcional); verificar que o backend
      inicia sem erro de importação.
- [x] 4.2 Gerar a migration no container, revisar que contém somente a coluna
      nova e sua FK, e aplicar; verificar que `flask db upgrade` conclui e que
      `flask db check` não aponta diferenças.
- [x] 4.3 No serviço: validar a operação, preencher o tipo a partir dela,
      recusar tipo ou talhão divergentes, gravar a data informada e devolver
      `id_atividade_agricola` e `codigo_talhao`; verificar pela API os cenários
      de "Vínculo da saída com a operação agrícola", "Coerência da operação
      vinculada", "Data informada da movimentação" e "Identificação do talhão e
      da operação no histórico".
- [x] 4.4 Verificar pela API o cenário de "Histórico preservado ao excluir a
      operação" (200, vínculo nulo, tipo preservado, saldo inalterado) e a
      regressão: SAIDA só com `id_atividade` e ENTRADA completa continuam
      respondendo 201.

## 5. Tradução de insumos e movimentações (frontend)

- [x] 5.1 Criar `src/services/insumosAdapter.ts` com as conversões de insumo,
      de movimentação e de payload descritas no design, mais a regra que decide
      entre propagar o erro do backend e usar o registro local; cobrir com
      `insumosAdapter.test.ts` e verificar que `npm test` passa.
- [x] 5.2 Ajustar os tipos de movimentação (`id_responsavel` como `string`,
      `id_fornecedor` no payload) e o mock de insumos; verificar que `tsc` não
      aponta erros novos em relação aos 6 já existentes no container.
- [x] 5.3 Em `api.ts`: usar a tradução em `getInsumos`, `getMovimentacoes` e
      `criarMovimentacao` com a rota `/api/movimentacoes`; adicionar
      `getInsumosCadastrados`, `getTalhoesCadastrados`, `getFornecedores` e
      `getAtividadesCadastradas` (usada pelo módulo de Atividades). Verificar no
      navegador que a lista de Insumos mostra o nome do insumo cadastrado e que
      o log do backend não registra mais 404 em `/api/movimentacoes-estoque`.

## 6. Formulário de movimentação de estoque (frontend)

- [x] 6.1 Usar funcionários ativos e fornecedores reais, talhões cadastrados,
      data inicial local e enviar a operação escolhida em "Atividade
      Relacionada"; verificar no navegador que uma saída vinculada a uma
      operação aparece no histórico e que `GET /api/movimentacoes` a devolve com
      `id_atividade_agricola` e o saldo do insumo decrementado.
- [x] 6.2 Verificar no navegador que uma entrada com fornecedor, nota fiscal e
      lote é gravada (aparece em `GET /api/movimentacoes` com o fornecedor) e
      que o saldo do insumo aumenta.

## 7. Tela de Atividades (frontend)

- [x] 7.1 No formulário: restaurar o aviso de atividade duplicada, usar talhões
      e insumos cadastrados (insumo já traduzido) e omitir itens inativos
      preservando o selecionado na edição. Verificar no navegador: duplicada é
      barrada com aviso; uma máquina inativada pela API some do combo de uma
      nova atividade e continua selecionada ao editar a operação que a usa.
- [x] 7.2 Calcular a data corrente com os componentes locais em
      `types/atividade.ts`, com teste em `vitest` para um horário após as 21h, e
      conferir que o detalhe e o CSV mostram o nome da propriedade; verificar
      que `npm test` passa e que o detalhe exibe o nome.
- [x] 7.3 Verificar, com o backend parado, que a tela de Atividades mostra o
      aviso de erro em vez de atividades de demonstração e que a tela Início
      continua abrindo.

## 8. Verificação integrada

- [x] 8.1 Executar o roteiro completo no navegador: criar operação, registrar
      saída de estoque vinculada a ela, conferir histórico e saldo, tentar
      duplicar a operação (barrado), excluir a operação e conferir que a
      movimentação permanece. Verificar também `npm test`, `tsc` sem erros novos
      e `openspec validate atividades-correcoes-integracao --strict`.
- [x] 8.2 Remover os dados de teste criados e verificar pela API que
      atividades, movimentações e saldos voltaram ao estado inicial.
