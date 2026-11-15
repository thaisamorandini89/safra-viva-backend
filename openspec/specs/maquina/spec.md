# maquina Specification

## Purpose
Catálogo de máquinas e implementos disponíveis para serem associados às
operações agrícolas, com suas horas e custos de uso.

## Requirements

### Requirement: Estrutura da máquina/implemento

O sistema SHALL persistir máquinas e implementos na tabela `maquina` com
`id_maquina` (PK inteira autoincremental), `nome` (String(150), obrigatório e
único), `tipo` (String(50), opcional), `observacoes` (String(500), opcional) e
`status` (booleano, padrão verdadeiro).

#### Scenario: Tabela criada por migration

- **WHEN** a migration é aplicada
- **THEN** a tabela `maquina` existe com as colunas descritas

### Requirement: Cadastro e manutenção de máquinas

O sistema SHALL expor `GET /api/maquinas`, `POST /api/maquinas`,
`GET /api/maquinas/{id}`, `PUT /api/maquinas/{id}` e `DELETE /api/maquinas/{id}`.
O `nome` SHALL ser obrigatório e único.

#### Scenario: Cadastro realizado

- **WHEN** um `POST /api/maquinas` é enviado com `nome` preenchido e inédito
- **THEN** a máquina é persistida
- **AND** a resposta é HTTP 201 com `id_maquina` e `nome`

#### Scenario: Nome ausente

- **WHEN** um `POST /api/maquinas` é enviado sem `nome` ou vazio
- **THEN** a resposta é HTTP 400 e nada é persistido

#### Scenario: Nome duplicado

- **WHEN** um `POST /api/maquinas` usa um `nome` já existente
- **THEN** a resposta é HTTP 400 e nada é persistido

#### Scenario: Listagem para o seletor

- **WHEN** um `GET /api/maquinas` é realizado
- **THEN** a resposta é HTTP 200 com as máquinas cadastradas

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
