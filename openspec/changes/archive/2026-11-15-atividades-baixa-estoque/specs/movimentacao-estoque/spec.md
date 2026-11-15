# movimentacao-estoque Spec Delta

## Purpose

Registra as entradas e saídas de estoque dos insumos, atualizando o saldo e
guardando os dados de origem, destino e rastreabilidade de cada movimentação.

## ADDED Requirements

### Requirement: Origem da movimentação

O sistema SHALL informar em cada movimentação o campo `origem`, com o valor
`ATIVIDADE` para as saídas geradas pela conclusão de uma operação agrícola e
`MANUAL` para as demais. Toda movimentação registrada por
`POST /api/movimentacoes` SHALL ter origem `MANUAL`, independentemente do
payload.

#### Scenario: Movimentação lançada pela API

- **WHEN** um `POST /api/movimentacoes` é enviado, com ou sem `origem` no
  payload
- **THEN** a movimentação é devolvida com `origem` igual a `MANUAL`

#### Scenario: Movimentações anteriores

- **WHEN** um `GET /api/movimentacoes` devolve movimentações registradas antes
  desta mudança
- **THEN** elas vêm com `origem` igual a `MANUAL`

### Requirement: Filtro do histórico por operação

O sistema SHALL aceitar em `GET /api/movimentacoes` o filtro opcional
`id_atividade_agricola`, devolvendo apenas as movimentações vinculadas à
operação informada, manuais ou automáticas.

#### Scenario: Movimentações de uma operação

- **WHEN** um `GET /api/movimentacoes?id_atividade_agricola={id}` é realizado
  para uma operação com uma saída manual e uma automática
- **THEN** a resposta é HTTP 200 com as duas saídas e nenhuma outra

#### Scenario: Operação sem movimentações

- **WHEN** um `GET /api/movimentacoes?id_atividade_agricola={id}` é realizado
  para uma operação sem saídas vinculadas
- **THEN** a resposta é HTTP 200 com lista vazia

### Requirement: Saídas manuais preservadas na devolução

Ao desfazer as saídas de uma operação agrícola, o sistema SHALL remover apenas
as de origem `ATIVIDADE`. As saídas de origem `MANUAL` vinculadas à operação
SHALL permanecer no histórico com seus saldos, perdendo apenas o vínculo quando
a operação for excluída.

#### Scenario: Reabertura com saída manual vinculada

- **WHEN** uma operação concluída, com uma saída manual vinculada e uma
  automática, é reaberta
- **THEN** a saída automática é removida e seu saldo devolvido
- **AND** a saída manual permanece vinculada à operação, sem alteração de saldo

#### Scenario: Exclusão com saída manual vinculada

- **WHEN** a mesma operação é excluída
- **THEN** a saída manual permanece no histórico com `id_atividade_agricola`
  nulo e o tipo de atividade preservado
