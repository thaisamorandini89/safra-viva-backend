# Spec Delta

## Purpose

Registro de receitas e despesas da operação agrícola com categorias, forma de
pagamento, status, vínculos (empresa, propriedade, talhão, safra, centro de
custo), rateio de despesas entre talhões e regras de integridade histórica.

## ADDED Requirements

### Requirement: Estrutura do lançamento financeiro

O sistema SHALL persistir lançamentos na tabela `lancamento_financeiro` com:
`id_lancamento` (UUID em formato string, PK), `tipo` ('RECEITA' ou 'DESPESA',
obrigatório), `categoria` (String, obrigatório), `descricao` (String, opcional),
`valor` (Numeric(14,2), obrigatório e positivo), `data_lancamento` (Date,
obrigatória), `forma_pagamento` ('DINHEIRO', 'PIX', 'BOLETO', 'CARTAO' ou
'TRANSFERENCIA', opcional), `status` ('PENDENTE' ou 'PAGO', default 'PENDENTE'),
`conciliado` (Boolean, default False), `observacao` (String, opcional),
`data_cadastro` (DateTime, preenchida pelo banco) e FKs opcionais `id_empresa`,
`id_propriedade`, `id_talhao`, `id_safra` e `id_centro_custo`.

#### Scenario: Tabela criada por migration

- **WHEN** a migration é aplicada
- **THEN** a tabela `lancamento_financeiro` existe com as colunas, FKs e
  restrições descritas

### Requirement: Campos obrigatórios do lançamento

O sistema SHALL exigir, em todo lançamento, os campos `tipo`, `data_lancamento`,
`valor` e `categoria`, rejeitando com HTTP 400 quando qualquer um estiver
ausente (RN001).

#### Scenario: Campo obrigatório ausente

- **WHEN** um `POST /api/lancamentos` é enviado sem `tipo`, `data_lancamento`,
  `valor` ou `categoria`
- **THEN** a resposta é HTTP 400 e nada é persistido

### Requirement: Valor positivo do lançamento

O sistema SHALL rejeitar lançamentos com `valor` igual ou inferior a zero
(RN002).

#### Scenario: Valor não positivo

- **WHEN** um `POST /api/lancamentos` é enviado com `valor` menor ou igual a zero
- **THEN** a resposta é HTTP 400 e nada é persistido

### Requirement: Registro de lançamento

O sistema SHALL permitir registrar um lançamento via `POST /api/lancamentos`,
validando que as entidades referenciadas (empresa, propriedade, talhão, safra,
centro de custo), quando informadas, existem.

#### Scenario: Lançamento válido

- **WHEN** um `POST /api/lancamentos` é enviado com tipo, categoria, data e valor
  positivo, e vínculos existentes
- **THEN** o lançamento é persistido com `id_lancamento` gerado e `status`
  'PENDENTE' por padrão
- **AND** a resposta é HTTP 201 com o lançamento criado

#### Scenario: Vínculo inexistente

- **WHEN** um `POST /api/lancamentos` referencia uma entidade vinculada
  (empresa, propriedade, talhão, safra ou centro de custo) inexistente
- **THEN** nenhum lançamento é persistido
- **AND** a resposta é HTTP 400 com mensagem indicando o vínculo inválido

### Requirement: Vínculo de despesa operacional com safra

O sistema SHALL permitir vincular lançamentos a uma safra via `id_safra`, de modo
que despesas operacionais agrícolas possam ser associadas à safra correspondente
quando aplicável (RN004).

#### Scenario: Despesa vinculada à safra

- **WHEN** um `POST /api/lancamentos` de tipo DESPESA é enviado com `id_safra`
  existente
- **THEN** o lançamento é persistido vinculado àquela safra

### Requirement: Rateio de despesa entre talhões

O sistema SHALL permitir distribuir uma despesa entre vários talhões (RN005),
persistindo cada parcela na tabela `rateio_lancamento` com `id_rateio` (PK),
`id_lancamento` (FK obrigatória), `id_talhao` (FK obrigatória) e `percentual`
(Numeric). A soma dos percentuais de um lançamento SHALL ser igual a 100%.

#### Scenario: Rateio válido

- **WHEN** um `POST /api/lancamentos` inclui uma lista de rateio cujos
  percentuais somam 100% e referenciam talhões existentes
- **THEN** o lançamento e suas parcelas de rateio são persistidos na mesma
  transação
- **AND** a resposta é HTTP 201

#### Scenario: Soma de percentuais inválida

- **WHEN** um `POST /api/lancamentos` inclui rateio cujos percentuais não somam
  100%
- **THEN** nenhum lançamento nem rateio é persistido
- **AND** a resposta é HTTP 400

#### Scenario: Talhão de rateio inexistente

- **WHEN** um rateio referencia um `id_talhao` inexistente
- **THEN** nenhum lançamento nem rateio é persistido
- **AND** a resposta é HTTP 400

### Requirement: Integridade histórica de lançamento conciliado

O sistema SHALL impedir a exclusão definitiva de um lançamento após ele ter sido
conciliado (RN003).

#### Scenario: Exclusão de lançamento não conciliado

- **WHEN** um `DELETE /api/lancamentos/{id}` é realizado sobre um lançamento com
  `conciliado` falso
- **THEN** o lançamento é excluído
- **AND** a resposta é HTTP 200

#### Scenario: Exclusão de lançamento conciliado

- **WHEN** um `DELETE /api/lancamentos/{id}` é realizado sobre um lançamento com
  `conciliado` verdadeiro
- **THEN** o lançamento não é excluído
- **AND** a resposta é HTTP 400 com mensagem indicando que lançamentos
  conciliados não podem ser excluídos

### Requirement: Atualização de lançamento

O sistema SHALL permitir atualizar um lançamento via `PUT /api/lancamentos/{id}`,
aplicando as mesmas validações de valor positivo, campos obrigatórios e
existência de vínculos.

#### Scenario: Atualização válida

- **WHEN** um `PUT /api/lancamentos/{id}` é enviado com dados válidos
- **THEN** o lançamento é atualizado
- **AND** a resposta é HTTP 200 com o lançamento atualizado

#### Scenario: Lançamento inexistente

- **WHEN** um `PUT /api/lancamentos/{id}` referencia um `id` inexistente
- **THEN** a resposta é HTTP 404

### Requirement: Listagem e filtros de lançamentos

O sistema SHALL expor `GET /api/lancamentos` retornando os lançamentos ordenados
por `data_lancamento` decrescente, com filtros opcionais por período
(`data_inicio`/`data_fim`), `tipo`, `id_safra`, `id_propriedade` e `id_talhao`.

#### Scenario: Listagem completa

- **WHEN** um `GET /api/lancamentos` é realizado sem filtros
- **THEN** a resposta é HTTP 200 com os lançamentos em ordem decrescente de data

#### Scenario: Filtro por período

- **WHEN** um `GET /api/lancamentos?data_inicio={d1}&data_fim={d2}` é realizado
- **THEN** a resposta é HTTP 200 contendo apenas lançamentos no intervalo

#### Scenario: Filtro por safra

- **WHEN** um `GET /api/lancamentos?id_safra={id}` é realizado
- **THEN** a resposta é HTTP 200 contendo apenas lançamentos daquela safra
