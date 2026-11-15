# centro-custo Spec Delta

## Purpose

Cadastro de centros de custo operacionais e administrativos, usados para
classificar os lançamentos financeiros.

## ADDED Requirements

### Requirement: Edição de centro de custo

O sistema SHALL permitir atualização parcial via
`PUT /api/centros-custo/{id_centro_custo}`, alterando apenas os campos enviados
entre `nome`, `tipo`, `descricao` e `status`, com as validações do cadastro, e
devolvendo o centro de custo completo.

#### Scenario: Edição válida

- **WHEN** um `PUT /api/centros-custo/{id_centro_custo}` é enviado com `nome` e
  `descricao`
- **THEN** a resposta é HTTP 200 com o centro de custo completo
- **AND** somente os campos enviados são alterados

#### Scenario: Centro de custo inativado

- **WHEN** um `PUT /api/centros-custo/{id_centro_custo}` é enviado com `status`
  falso
- **THEN** o centro continua sendo devolvido por `GET /api/centros-custo`, com
  `status` falso

#### Scenario: Dado inválido na edição

- **WHEN** um `PUT /api/centros-custo/{id_centro_custo}` é enviado com `nome`
  vazio ou com `tipo` fora de {OPERACIONAL, ADMINISTRATIVO}
- **THEN** a resposta é HTTP 400
- **AND** o centro de custo permanece inalterado

#### Scenario: Edição de centro de custo inexistente

- **WHEN** um `PUT /api/centros-custo/{id_centro_custo}` é feito para um id
  inexistente
- **THEN** a resposta é HTTP 404

### Requirement: Exclusão de centro de custo

O sistema SHALL permitir excluir um centro de custo via
`DELETE /api/centros-custo/{id_centro_custo}` e SHALL recusar com HTTP 400, com
mensagem indicando que o centro está em uso, a exclusão de um centro de custo
referenciado por algum lançamento financeiro.

#### Scenario: Exclusão de centro de custo sem uso

- **WHEN** um `DELETE /api/centros-custo/{id_centro_custo}` é feito para um
  centro sem lançamentos
- **THEN** a resposta é HTTP 200
- **AND** o centro deixa de ser devolvido por `GET /api/centros-custo`

#### Scenario: Centro de custo com lançamentos

- **WHEN** um `DELETE /api/centros-custo/{id_centro_custo}` é feito para um
  centro referenciado por um lançamento
- **THEN** a resposta é HTTP 400 com mensagem indicando que o centro está em uso
- **AND** o centro continua cadastrado

#### Scenario: Exclusão de centro de custo inexistente

- **WHEN** um `DELETE /api/centros-custo/{id_centro_custo}` é feito para um id
  inexistente
- **THEN** a resposta é HTTP 404
