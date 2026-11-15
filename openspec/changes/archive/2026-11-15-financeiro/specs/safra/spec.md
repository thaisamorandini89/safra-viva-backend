# Spec Delta

## Purpose

Cadastro de safra agrícola — período, propriedade, cultura e área — usado como
dimensão para vincular lançamentos financeiros e apurar o resultado por safra e
por cultura.

## ADDED Requirements

### Requirement: Estrutura da safra

O sistema SHALL persistir safras na tabela `safra` com: `id_safra` (PK),
`nome` (String, obrigatório), `cultura` (String, obrigatório), `id_propriedade`
(FK obrigatória para `propriedade.id_propriedade`), `data_inicio` (Date,
obrigatória), `data_fim` (Date, opcional), `area_plantada` (Numeric, opcional,
em hectares), `status` (Boolean, default True) e `data_cadastro` (DateTime,
preenchida pelo banco).

#### Scenario: Tabela criada por migration

- **WHEN** a migration é aplicada
- **THEN** a tabela `safra` existe com as colunas, FK e restrições descritas

### Requirement: Cadastro de safra

O sistema SHALL permitir cadastrar uma safra via `POST /api/safras`, exigindo
`nome`, `cultura`, `id_propriedade` e `data_inicio`, e validando que a
propriedade informada existe.

#### Scenario: Safra criada com dados válidos

- **WHEN** um `POST /api/safras` é enviado com nome, cultura, propriedade
  existente e data de início
- **THEN** a safra é persistida
- **AND** a resposta é HTTP 201 com o `id_safra` gerado

#### Scenario: Propriedade inexistente

- **WHEN** um `POST /api/safras` referencia um `id_propriedade` inexistente
- **THEN** nenhuma safra é persistida
- **AND** a resposta é HTTP 400 com mensagem indicando propriedade inválida

#### Scenario: Campo obrigatório ausente

- **WHEN** um `POST /api/safras` é enviado sem `nome`, `cultura`,
  `id_propriedade` ou `data_inicio`
- **THEN** a resposta é HTTP 400 e nada é persistido

### Requirement: Listagem de safras

O sistema SHALL expor `GET /api/safras` retornando as safras cadastradas, com
suporte ao filtro opcional por propriedade via query param `id_propriedade`.

#### Scenario: Listagem completa

- **WHEN** um `GET /api/safras` é realizado sem filtros
- **THEN** a resposta é HTTP 200 com as safras cadastradas

#### Scenario: Filtro por propriedade

- **WHEN** um `GET /api/safras?id_propriedade={id}` é realizado
- **THEN** a resposta é HTTP 200 contendo apenas safras daquela propriedade
