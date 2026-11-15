# safra Spec Delta

## Purpose

Cadastro de safra agrícola — período, propriedade, cultura e área — usado como
dimensão para vincular lançamentos financeiros, operações agrícolas e saídas de
estoque, e apurar o resultado por safra e por cultura.

## ADDED Requirements

### Requirement: Safra em uso por operações e movimentações

O sistema SHALL recusar com HTTP 400, com mensagem indicando que a safra está em
uso, o `DELETE /api/safras/{id_safra}` de uma safra referenciada por alguma
operação agrícola ou por alguma movimentação de estoque.

#### Scenario: Safra usada por operação

- **WHEN** um `DELETE /api/safras/{id_safra}` é feito para uma safra vinculada a
  uma operação agrícola
- **THEN** a resposta é HTTP 400 com mensagem indicando que a safra está em uso
- **AND** a safra continua cadastrada

#### Scenario: Safra usada por movimentação

- **WHEN** um `DELETE /api/safras/{id_safra}` é feito para uma safra vinculada a
  uma saída de estoque
- **THEN** a resposta é HTTP 400
- **AND** a safra continua cadastrada
