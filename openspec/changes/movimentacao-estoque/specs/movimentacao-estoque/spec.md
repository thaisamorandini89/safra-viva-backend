# movimentacao-estoque Spec Delta

## ADDED Requirements

### Requirement: Estrutura da movimentação de estoque

O sistema SHALL persistir movimentações na tabela `movimentacao_estoque` com:
`id_movimentacao` (UUID em formato string, PK), `id_insumo` (FK obrigatória
para `insumo.id_insumo`), `tipo_movimentacao` ('ENTRADA' ou 'SAIDA',
obrigatório), `quantidade` (Numeric(10,2), obrigatório e positivo),
`data_movimentacao` (DateTime, preenchida pelo banco),
`id_responsavel` (FK opcional para `responsavel.id_responsavel`) e
`observacao` (String(500), opcional).

#### Scenario: Tabela criada por migration

- **WHEN** a migration é aplicada
- **THEN** a tabela `movimentacao_estoque` existe com as colunas, FKs e
  restrições descritas

### Requirement: Registro de entrada de estoque

Ao registrar uma movimentação de tipo ENTRADA via `POST /api/movimentacoes`,
o sistema SHALL somar `quantidade` ao `estoque_atual` do insumo vinculado,
persistindo movimentação e saldo na mesma transação.

#### Scenario: Entrada registrada

- **WHEN** um `POST /api/movimentacoes` é enviado com tipo ENTRADA,
  insumo existente e quantidade positiva
- **THEN** a movimentação é persistida
- **AND** `estoque_atual` do insumo é incrementado em `quantidade`
- **AND** a resposta é HTTP 201 com a movimentação e o novo `estoque_atual`

### Requirement: Registro de saída de estoque

Ao registrar uma movimentação de tipo SAIDA, o sistema SHALL subtrair
`quantidade` do `estoque_atual` do insumo, rejeitando a operação quando o
saldo for insuficiente.

#### Scenario: Saída com saldo suficiente

- **WHEN** um `POST /api/movimentacoes` é enviado com tipo SAIDA e
  `quantidade` menor ou igual ao `estoque_atual` do insumo
- **THEN** a movimentação é persistida
- **AND** `estoque_atual` é decrementado em `quantidade`
- **AND** a resposta é HTTP 201

#### Scenario: Saída com saldo insuficiente

- **WHEN** um `POST /api/movimentacoes` é enviado com tipo SAIDA e
  `quantidade` maior que o `estoque_atual`
- **THEN** nenhuma movimentação é registrada
- **AND** o `estoque_atual` permanece inalterado
- **AND** a resposta é HTTP 400 com mensagem de saldo insuficiente

### Requirement: Validação do payload de movimentação

O sistema SHALL validar o payload com schema Pydantic, rejeitando com HTTP 400:
tipo diferente de ENTRADA/SAIDA, quantidade ausente, zero ou negativa, insumo
inexistente e responsável informado inexistente.

#### Scenario: Tipo inválido

- **WHEN** um `POST /api/movimentacoes` é enviado com `tipo_movimentacao`
  fora de {ENTRADA, SAIDA}
- **THEN** a resposta é HTTP 400 e nada é persistido

#### Scenario: Quantidade não positiva

- **WHEN** um `POST /api/movimentacoes` é enviado com `quantidade` <= 0
- **THEN** a resposta é HTTP 400 e nada é persistido

#### Scenario: Insumo inexistente

- **WHEN** um `POST /api/movimentacoes` referencia um `id_insumo` inexistente
- **THEN** a resposta é HTTP 400 e nada é persistido

#### Scenario: Responsável opcional

- **WHEN** um `POST /api/movimentacoes` é enviado sem `id_responsavel`
- **THEN** a movimentação é registrada normalmente com responsável nulo

### Requirement: Histórico de movimentações

O sistema SHALL expor `GET /api/movimentacoes` retornando o histórico ordenado
por `data_movimentacao` decrescente, com suporte ao filtro por insumo via
query param `id_insumo`, incluindo em cada item os dados do insumo/produto e o
nome do responsável (quando houver).

#### Scenario: Listagem completa

- **WHEN** um `GET /api/movimentacoes` é realizado sem filtros
- **THEN** a resposta é HTTP 200 com todas as movimentações em ordem
  decrescente de data

#### Scenario: Filtro por insumo

- **WHEN** um `GET /api/movimentacoes?id_insumo={id}` é realizado
- **THEN** a resposta é HTTP 200 contendo apenas movimentações daquele insumo
