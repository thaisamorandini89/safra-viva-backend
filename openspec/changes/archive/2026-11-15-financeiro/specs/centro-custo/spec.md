# Spec Delta

## Purpose

Cadastro de centros de custo operacionais e administrativos para classificar e
agrupar despesas do módulo financeiro.

## ADDED Requirements

### Requirement: Estrutura do centro de custo

O sistema SHALL persistir centros de custo na tabela `centro_custo` com:
`id_centro_custo` (PK), `nome` (String, obrigatório), `tipo` ('OPERACIONAL' ou
'ADMINISTRATIVO', obrigatório), `descricao` (String, opcional), `status`
(Boolean, default True) e `data_cadastro` (DateTime, preenchida pelo banco).

#### Scenario: Tabela criada por migration

- **WHEN** a migration é aplicada
- **THEN** a tabela `centro_custo` existe com as colunas e restrições descritas

### Requirement: Cadastro de centro de custo

O sistema SHALL permitir cadastrar um centro de custo via
`POST /api/centros-custo`, exigindo `nome` e `tipo` válido.

#### Scenario: Centro de custo criado

- **WHEN** um `POST /api/centros-custo` é enviado com `nome` e `tipo` válido
- **THEN** o centro de custo é persistido
- **AND** a resposta é HTTP 201 com o `id_centro_custo` gerado

#### Scenario: Tipo inválido

- **WHEN** um `POST /api/centros-custo` é enviado com `tipo` fora de
  {OPERACIONAL, ADMINISTRATIVO}
- **THEN** a resposta é HTTP 400 e nada é persistido

### Requirement: Listagem de centros de custo

O sistema SHALL expor `GET /api/centros-custo` retornando os centros de custo
cadastrados.

#### Scenario: Listagem completa

- **WHEN** um `GET /api/centros-custo` é realizado
- **THEN** a resposta é HTTP 200 com os centros de custo cadastrados
