# maquina Spec Delta

## ADDED Requirements

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
