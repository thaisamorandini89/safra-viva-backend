# tipo-atividade Spec Delta

## Purpose

Catálogo dos tipos de atividade (Aração, Adubação, Pulverização e outros), cada
um vinculado a uma categoria, usado nas operações agrícolas e nas saídas de
estoque.

## ADDED Requirements

### Requirement: Exclusão de tipo em uso

O sistema SHALL recusar com HTTP 400, com mensagem indicando que o tipo está em
uso, o `DELETE /api/tipos-atividade/{id}` de um tipo referenciado por alguma
operação agrícola ou por alguma movimentação de estoque, mantendo o tipo
cadastrado.

#### Scenario: Tipo usado em operação

- **WHEN** um `DELETE /api/tipos-atividade/{id}` é enviado para um tipo
  referenciado por uma operação agrícola
- **THEN** a resposta é HTTP 400 com mensagem indicando que o tipo está em uso
- **AND** o tipo continua cadastrado

#### Scenario: Tipo usado em movimentação de estoque

- **WHEN** um `DELETE /api/tipos-atividade/{id}` é enviado para um tipo
  referenciado por uma movimentação de estoque
- **THEN** a resposta é HTTP 400 e o tipo continua cadastrado

#### Scenario: Tipo sem uso

- **WHEN** um `DELETE /api/tipos-atividade/{id}` é enviado para um tipo sem
  operações nem movimentações
- **THEN** a resposta é HTTP 200 e o tipo é removido

#### Scenario: Tipo inexistente

- **WHEN** um `DELETE /api/tipos-atividade/{id}` referencia um `id` inexistente
- **THEN** a resposta é HTTP 404
