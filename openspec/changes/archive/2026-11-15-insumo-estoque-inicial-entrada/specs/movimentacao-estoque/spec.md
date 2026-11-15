# movimentacao-estoque Spec Delta

## MODIFIED Requirements

### Requirement: Origem da movimentação

O sistema SHALL informar em cada movimentação o campo `origem`, com o valor
`ATIVIDADE` para as saídas geradas pela conclusão de uma operação agrícola,
`CADASTRO` para a entrada do estoque inicial registrada no cadastro de um
insumo e `MANUAL` para as demais. Toda movimentação registrada por
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

#### Scenario: Entrada do estoque inicial

- **WHEN** um `GET /api/movimentacoes` devolve a entrada registrada pelo
  cadastro de um insumo com estoque inicial
- **THEN** ela vem com `origem` igual a `CADASTRO`
