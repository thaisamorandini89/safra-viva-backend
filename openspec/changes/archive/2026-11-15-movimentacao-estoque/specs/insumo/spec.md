# insumo Spec Delta

## ADDED Requirements

### Requirement: Saldo atualizado por movimentação

O `estoque_atual` do insumo SHALL ser atualizado automaticamente pelo registro
de movimentações de estoque (ENTRADA soma, SAIDA subtrai), na mesma transação
do registro da movimentação.

#### Scenario: Saldo reflete a movimentação

- **WHEN** uma movimentação é registrada com sucesso para um insumo
- **THEN** o `estoque_atual` retornado em `GET /api/insumos/{id_insumo}`
  reflete o novo saldo
