# movimentacao-estoque Spec Delta

## ADDED Requirements

### Requirement: Estrutura da movimentação de estoque

O sistema SHALL persistir movimentações na tabela `movimentacao_estoque` com:
`id_movimentacao` (UUID em formato string, PK), `id_insumo` (FK obrigatória
para `insumo.id_insumo`), `tipo_movimentacao` ('ENTRADA' ou 'SAIDA',
obrigatório), `quantidade` (Numeric(10,2), obrigatório e positivo),
`data_movimentacao` (DateTime, preenchida pelo banco),
`id_funcionario` (String(36), FK opcional para `funcionario.id_funcionario`;
obrigatório na interface), `observacao` (String(500), opcional) e
`valor_unitario` (Numeric(14,2), opcional).

A movimentação SHALL suportar campos de detalhe condicionais, todos opcionais
no banco (`nullable=True`):

- Dados da Entrada: `id_fornecedor` (FK para `fornecedor.id_fornecedor`),
  `numero_nota_fiscal` (String(50)), `numero_lote` (String(50)),
  `data_fabricacao` (Date) e `data_validade` (Date).
- Destino e Rastreabilidade (Saída): `id_talhao` (FK para `talhao.id_talhao`),
  `safra` (String(20)), `id_atividade` (FK para `atividade.id_atividade`) e
  `destino_finalidade` (String(255)).

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
inexistente e funcionário informado inexistente.

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

#### Scenario: Funcionário opcional

- **WHEN** um `POST /api/movimentacoes` é enviado sem `id_funcionario`
- **THEN** a movimentação é registrada normalmente com funcionário nulo

### Requirement: Detalhes condicionais por tipo de movimentação

O sistema SHALL aceitar os campos de detalhe de entrada
(`id_fornecedor`, `numero_nota_fiscal`, `numero_lote`, `data_fabricacao`,
`data_validade`) apenas em movimentações ENTRADA, e os campos de destino e
rastreabilidade (`id_talhao`, `safra`, `id_atividade`,
`destino_finalidade`) apenas em movimentações SAIDA, rejeitando com HTTP 400 o
envio cruzado. `id_fornecedor`, `id_talhao` e `id_atividade`, quando
informados, SHALL referenciar registros existentes.

#### Scenario: Entrada com dados completos

- **WHEN** um `POST /api/movimentacoes` ENTRADA é enviado com fornecedor,
  nota fiscal, lote e datas de fabricação/validade
- **THEN** a movimentação é persistida com todos os campos informados
- **AND** a resposta é HTTP 201 contendo os detalhes da entrada

#### Scenario: Saída com destino e rastreabilidade

- **WHEN** um `POST /api/movimentacoes` SAIDA é enviado com talhão, safra,
  atividade relacionada e destino/finalidade
- **THEN** a movimentação é persistida com todos os campos informados
- **AND** a resposta é HTTP 201 contendo os detalhes da saída

#### Scenario: Campo de entrada em uma SAIDA

- **WHEN** um `POST /api/movimentacoes` SAIDA inclui qualquer campo de entrada
  (ex.: `numero_nota_fiscal`)
- **THEN** nada é persistido
- **AND** a resposta é HTTP 400 indicando o campo não permitido para o tipo

#### Scenario: Campo de saída em uma ENTRADA

- **WHEN** um `POST /api/movimentacoes` ENTRADA inclui qualquer campo de saída
  (ex.: `id_talhao`)
- **THEN** nada é persistido
- **AND** a resposta é HTTP 400 indicando o campo não permitido para o tipo

#### Scenario: Validade anterior à fabricação

- **WHEN** uma ENTRADA informa `data_validade` anterior a `data_fabricacao`
- **THEN** nada é persistido
- **AND** a resposta é HTTP 400

#### Scenario: Fornecedor, talhão ou atividade inexistente

- **WHEN** a movimentação referencia `id_fornecedor`, `id_talhao` ou
  `id_atividade` inexistente
- **THEN** nada é persistido
- **AND** a resposta é HTTP 400

### Requirement: Histórico de movimentações

O sistema SHALL expor `GET /api/movimentacoes` retornando o histórico ordenado
por `data_movimentacao` decrescente, com suporte ao filtro por insumo via
query param `id_insumo`, incluindo em cada item os dados do insumo/produto, o
nome do funcionário, o nome do fornecedor/talhão e a descrição da atividade
(quando houver).

#### Scenario: Listagem completa

- **WHEN** um `GET /api/movimentacoes` é realizado sem filtros
- **THEN** a resposta é HTTP 200 com todas as movimentações em ordem
  decrescente de data

#### Scenario: Filtro por insumo

- **WHEN** um `GET /api/movimentacoes?id_insumo={id}` é realizado
- **THEN** a resposta é HTTP 200 contendo apenas movimentações daquele insumo
