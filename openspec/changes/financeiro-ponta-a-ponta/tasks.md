# Tasks

## 1. Preparação

- [x] 1.1 Criar a branch `feat/financeiro-ponta-a-ponta` no backend e no
      `frontendweb`, a partir da `homolog` atualizada, com os containers no ar e
      as migrations aplicadas; verificar que `GET /api/lancamentos`,
      `GET /api/safras` e `GET /api/centros-custo` respondem 200.

## 2. Verificação da change `financeiro` (backend)

- [x] 2.1 Verificar pela API os seis cenários da spec `safra` e os quatro da
      spec `centro-custo` da change `financeiro`, corrigindo no código os
      desvios encontrados; registrar o resultado de cada cenário.
- [x] 2.2 Verificar pela API os dezesseis cenários da spec
      `lancamento-financeiro` da change `financeiro`, marcando um lançamento
      como conciliado direto no banco para o cenário de exclusão, e corrigir os
      desvios encontrados.
- [x] 2.3 Verificar pela API os nove cenários da spec `relatorios-financeiros`
      da change `financeiro`, conferindo os valores de saldo, saldo acumulado e
      indicadores por hectare, e corrigir os desvios encontrados.
- [x] 2.4 Adicionar ao `insomnia_safraviva.json` as requisições de safras,
      centros de custo, lançamentos e relatórios financeiros; verificar que o
      arquivo continua sendo JSON válido e contém as rotas.
- [x] 2.5 Marcar no `tasks.md` da change `financeiro` as tasks confirmadas pela
      verificação; verificar com `openspec list --json` o total de tasks
      concluídas e relatar as que não puderam ser confirmadas.

## 3. Safra e centro de custo (backend)

- [x] 3.1 Recusar término anterior ao início e nome repetido na propriedade;
      verificar pela API o cenário de "Período válido da safra" e os dois de
      "Nome de safra único na propriedade".
- [x] 3.2 Criar a edição de safra; verificar pela API os quatro cenários de
      "Edição de safra".
- [x] 3.3 Criar a exclusão de safra; verificar pela API os três cenários de
      "Exclusão de safra".
- [x] 3.4 Criar a edição e a exclusão de centro de custo; verificar pela API os
      quatro cenários de "Edição de centro de custo" e os três de "Exclusão de
      centro de custo".

## 4. Conciliação (backend)

- [x] 4.1 Criar a rota de conciliação; verificar pela API os cinco cenários de
      "Conciliação de lançamento".
- [x] 4.2 Recusar a edição do lançamento conciliado; verificar pela API os dois
      cenários de "Lançamento conciliado protegido contra alteração" e a
      regressão: editar e excluir um lançamento não conciliado continuam
      respondendo 200.

## 5. Dados reais e erros (frontend)

- [x] 5.1 Em `api.ts`, aplicar às funções do Financeiro a regra única de
      demonstração e criar as funções de safra, centro de custo e conciliação;
      cobrir com testes que resposta vazia devolve lista vazia, falha de rede
      devolve demonstração e recusa do backend é propagada; verificar que
      `npm test` passa e que `tsc` não aponta erros novos.

## 6. Telas (frontend)

- [x] 6.1 Criar a aba "Safras" no Financeiro, com lista, cadastro, edição,
      inativação e exclusão; verificar no navegador que uma safra cadastrada
      continua na lista após recarregar a página, que o nome repetido mostra a
      mensagem do backend e que excluir uma safra com lançamento é barrado.
- [x] 6.2 Criar a aba "Centros de Custo", com as mesmas ações; verificar no
      navegador o cadastro, a edição e a exclusão barrada de um centro em uso.
- [x] 6.3 No formulário de lançamento, listar só safras e centros ativos e
      orientar o cadastro quando não houver nenhum; verificar no navegador que,
      sem safras cadastradas, o combo não mostra as de demonstração, que uma
      safra recém-cadastrada aparece sem recarregar e que um lançamento salvo
      com ela continua na lista após recarregar a página.
- [x] 6.4 Na lista de lançamentos, adicionar conciliar e desfazer a conciliação
      e travar editar e excluir do conciliado; verificar no navegador que
      conciliar um lançamento pendente mostra a mensagem do backend, que o
      conciliado não pode ser editado nem excluído e que desfazer libera os
      dois.

## 7. Verificação integrada

- [x] 7.1 Executar o roteiro no navegador: cadastrar safra e centro de custo,
      lançar uma receita e uma despesa com rateio, conferir dashboard, fluxo de
      caixa e relatórios com os valores lançados, conciliar e desfazer.
      Verificar também `npm test`, `tsc` sem erros novos e
      `openspec validate financeiro-ponta-a-ponta --strict`.
- [x] 7.2 Remover os dados de teste criados e verificar pela API que safras,
      centros de custo e lançamentos voltaram ao estado inicial.
