# categoria-atividade Spec Delta

## Purpose

Catálogo das categorias operacionais (Preparo de Solo, Plantio, Tratos
Culturais e outras) que agrupam os tipos de atividade e classificam as operações
de campo.

## ADDED Requirements

### Requirement: Exclusão de categoria em uso

O sistema SHALL recusar com HTTP 400, com mensagem indicando que a categoria
está em uso, o `DELETE /api/categorias-atividade/{id}` de uma categoria
referenciada por algum tipo de atividade ou por alguma operação agrícola,
mantendo a categoria cadastrada.

#### Scenario: Categoria com tipos vinculados

- **WHEN** um `DELETE /api/categorias-atividade/{id}` é enviado para uma
  categoria que possui tipos de atividade
- **THEN** a resposta é HTTP 400 com mensagem indicando que a categoria está em
  uso
- **AND** a categoria continua cadastrada

#### Scenario: Categoria usada em operação

- **WHEN** um `DELETE /api/categorias-atividade/{id}` é enviado para uma
  categoria referenciada por uma operação agrícola
- **THEN** a resposta é HTTP 400 e a categoria continua cadastrada

#### Scenario: Categoria sem uso

- **WHEN** um `DELETE /api/categorias-atividade/{id}` é enviado para uma
  categoria sem tipos nem operações
- **THEN** a resposta é HTTP 200 e a categoria é removida

#### Scenario: Categoria inexistente

- **WHEN** um `DELETE /api/categorias-atividade/{id}` referencia um `id`
  inexistente
- **THEN** a resposta é HTTP 404
