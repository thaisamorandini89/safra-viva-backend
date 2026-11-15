# maquina Spec Delta

## Purpose

Catálogo de máquinas e implementos disponíveis para serem associados às
operações agrícolas, com suas horas e custos de uso.

## ADDED Requirements

### Requirement: Exclusão de máquina em uso

O sistema SHALL recusar com HTTP 400, com mensagem indicando que a máquina está
em uso, o `DELETE /api/maquinas/{id}` de uma máquina referenciada por alguma
operação agrícola, mantendo a máquina cadastrada.

#### Scenario: Máquina usada em operação

- **WHEN** um `DELETE /api/maquinas/{id}` é enviado para uma máquina que consta
  na lista de máquinas de uma operação agrícola
- **THEN** a resposta é HTTP 400 com mensagem indicando que a máquina está em
  uso
- **AND** a máquina continua cadastrada

#### Scenario: Máquina sem uso

- **WHEN** um `DELETE /api/maquinas/{id}` é enviado para uma máquina que não
  consta em nenhuma operação
- **THEN** a resposta é HTTP 200 e a máquina é removida

#### Scenario: Máquina inexistente

- **WHEN** um `DELETE /api/maquinas/{id}` referencia um `id` inexistente
- **THEN** a resposta é HTTP 404
