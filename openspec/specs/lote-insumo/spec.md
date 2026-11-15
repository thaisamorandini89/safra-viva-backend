# lote-insumo Specification

## Purpose
Mantém os lotes de cada insumo, com saldo próprio, datas de fabricação e
validade, para rastrear o estoque por lote e identificar o que está vencido.

## Requirements

### Requirement: Lote de insumo com saldo próprio

O sistema SHALL manter, para cada insumo, lotes identificados por `numero_lote`
(único dentro do insumo), com `data_fabricacao` e `data_validade` opcionais e
`quantidade`, que é o saldo do lote e nunca fica negativo. A soma dos saldos dos
lotes de um insumo SHALL ser menor ou igual ao seu `estoque_atual`; a diferença
é o saldo sem lote.

#### Scenario: Tabelas criadas por migration

- **WHEN** a migration é aplicada
- **THEN** existe a tabela de lotes vinculada a `insumo`, com número de lote
  único por insumo
- **AND** existe a tabela que liga cada movimentação aos lotes afetados

#### Scenario: Mesmo número de lote em insumos diferentes

- **WHEN** dois insumos recebem entradas com o mesmo `numero_lote`
- **THEN** cada insumo passa a ter o seu próprio lote, com saldo independente

### Requirement: Lote criado ou somado pela entrada

Ao registrar uma ENTRADA com `numero_lote`, o sistema SHALL criar o lote do
insumo quando ele não existir, gravando as datas informadas, ou somar a
quantidade ao saldo do lote existente. Uma ENTRADA sem `numero_lote` SHALL
aumentar apenas o `estoque_atual`, sem alterar nenhum lote.

#### Scenario: Entrada em lote novo

- **WHEN** um `POST /api/movimentacoes` ENTRADA informa `numero_lote`,
  `data_validade` e quantidade para um insumo sem esse lote
- **THEN** o lote é criado com saldo igual à quantidade e com a validade
  informada
- **AND** o `estoque_atual` do insumo aumenta na mesma quantidade

#### Scenario: Entrada em lote existente

- **WHEN** um `POST /api/movimentacoes` ENTRADA informa o `numero_lote` de um
  lote já existente do insumo
- **THEN** o saldo do lote e o `estoque_atual` aumentam na quantidade informada
- **AND** nenhum lote novo é criado

#### Scenario: Entrada sem número de lote

- **WHEN** um `POST /api/movimentacoes` ENTRADA é enviado sem `numero_lote`
- **THEN** o `estoque_atual` aumenta e os lotes do insumo permanecem inalterados

### Requirement: Validade consistente do lote

O sistema SHALL recusar com HTTP 400 a ENTRADA que informe, para um lote já
existente, `data_validade` diferente da registrada no lote. Quando o lote ainda
não tiver validade registrada, a validade informada SHALL passar a valer para o
lote.

#### Scenario: Validade divergente

- **WHEN** um `POST /api/movimentacoes` ENTRADA informa o `numero_lote` de um
  lote existente com `data_validade` diferente da do lote
- **THEN** a resposta é HTTP 400
- **AND** nada é persistido e os saldos permanecem inalterados

#### Scenario: Validade informada depois

- **WHEN** um `POST /api/movimentacoes` ENTRADA informa `data_validade` para um
  lote existente que não tinha validade
- **THEN** o lote passa a ter a validade informada e o saldo é somado

### Requirement: Lote vencido

O sistema SHALL considerar vencido o lote cuja `data_validade` é anterior à data
corrente no fuso horário da aplicação. Lotes sem `data_validade` SHALL nunca ser
considerados vencidos.

#### Scenario: Lote que vence no dia corrente

- **WHEN** a `data_validade` de um lote é igual à data local corrente
- **THEN** o lote não é considerado vencido

#### Scenario: Lote com validade no dia anterior

- **WHEN** a `data_validade` de um lote é anterior à data local corrente
- **THEN** o lote é considerado vencido
