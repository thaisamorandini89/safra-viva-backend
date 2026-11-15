# Tasks

## 1. Preparação

- [ ] 1.1 Criar a branch `feat/custo-consumo-insumos` no backend e no
      `frontendweb` a partir da `homolog` atualizada, com os containers no ar;
      verificar que `GET /api/atividades` e `GET /api/movimentacoes` respondem
      200 e anotar as contagens de atividades, movimentações e insumos para
      restaurar no fim.

## 2. Custo calculado (backend)

- [ ] 2.1 Calcular o custo do item sem custo informado ao montar os insumos da
      operação; verificar pela API os sete cenários de "Custo calculado do
      insumo da operação" e a regressão: concluir a operação continua gerando a
      saída com o valor unitário do insumo.

## 3. Filtro por talhão (backend)

- [ ] 3.1 Aceitar `id_talhao` em `GET /api/movimentacoes`; verificar pela API os
      três cenários de "Filtro do histórico por talhão" e a regressão: os
      filtros `id_insumo` e `id_atividade_agricola` continuam funcionando.
- [ ] 3.2 Adicionar ao `insomnia_safraviva.json` a requisição de movimentações
      por talhão; verificar que o JSON é válido.

## 4. Telas (frontend)

- [ ] 4.1 Em `api.ts`, criar a busca das movimentações de um talhão sem dados de
      demonstração; cobrir com teste e verificar que `npm test` passa e que
      `tsc` não aponta erros novos.
- [ ] 4.2 No formulário de atividade, preencher o custo do insumo pela conta,
      com a indicação de calculado, e enviar vazio no modo automático e zero
      quando digitado; verificar no navegador que o custo aparece ao escolher
      insumo e quantidade, que digitar substitui, que apagar volta ao cálculo e
      que a atividade salva mostra o custo calculado pelo backend.
- [ ] 4.3 No detalhe do talhão, adicionar a seção "Insumos aplicados" com o
      total; verificar no navegador que uma saída manual e a saída de uma
      atividade concluída aparecem no talhão certo, que o total confere e que um
      talhão sem saídas mostra a mensagem de vazio.

## 5. Verificação integrada

- [ ] 5.1 Executar o roteiro no navegador: registrar entrada de um insumo com
      valor unitário, criar uma atividade com ele sem digitar custo, concluí-la,
      conferir o custo na atividade e a saída no detalhe do talhão. Verificar
      também `npm test`, `tsc` sem erros novos e
      `openspec validate custo-consumo-insumos --strict`.
- [ ] 5.2 Remover os dados de teste criados, sem tocar na atividade id 4, e
      verificar pela API que atividades, movimentações e insumos voltaram às
      contagens anotadas em 1.1.
