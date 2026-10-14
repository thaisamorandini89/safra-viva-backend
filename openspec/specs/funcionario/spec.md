# funcionario Specification

## Purpose

Permite cadastrar e gerenciar os colaboradores da empresa agrícola, com dados
pessoais e profissionais, CPF único e controle de status (ativo/inativo),
servindo de base para rastreabilidade operacional e funcionalidades futuras.

## Requirements

### Requirement: Estrutura da entidade Funcionário

O sistema SHALL representar o funcionário na tabela `funcionario` com
`id_funcionario` (UUID string, PK), `nome_completo` (obrigatório), `cpf`
(obrigatório e único), `rg`, `data_nascimento`, `telefone`, `email`, `cargo`
(obrigatório), `data_admissao` (obrigatória), `data_desligamento`, `status`
(booleano, padrão ativo), `observacoes` e `data_cadastro` (preenchida pelo
banco).

#### Scenario: Funcionário persistido com campos obrigatórios

- **WHEN** um funcionário é criado com nome completo, CPF, cargo e data de admissão
- **THEN** ele é gravado com `status` ativo por padrão
- **AND** `data_cadastro` é preenchida automaticamente pelo banco

### Requirement: Cadastro de funcionário com CPF único

O sistema SHALL permitir cadastrar funcionários via `POST /api/funcionarios`,
exigindo `nome_completo`, `cpf` (11 dígitos), `cargo` e `data_admissao`, e
rejeitando CPF duplicado ou inválido.

#### Scenario: Cadastro realizado com sucesso

- **WHEN** um `POST /api/funcionarios` é enviado com os campos obrigatórios válidos
- **THEN** o funcionário é persistido
- **AND** a resposta é HTTP 201 contendo `id_funcionario` e `nome_completo`

#### Scenario: CPF ausente ou com formato inválido

- **WHEN** um `POST /api/funcionarios` é enviado sem CPF ou com CPF que não tenha 11 dígitos
- **THEN** nenhum funcionário é criado
- **AND** a resposta é HTTP 400 indicando o erro no CPF

#### Scenario: CPF já cadastrado

- **WHEN** um `POST /api/funcionarios` é enviado com um CPF que já existe
- **THEN** nenhum funcionário é criado
- **AND** a resposta é HTTP 400 informando que o CPF já está cadastrado

### Requirement: Atualização de cadastro

O sistema SHALL permitir atualizar o cadastro via
`PUT /api/funcionarios/{id_funcionario}`, preservando a unicidade do CPF e
registrando `data_desligamento` quando informada.

#### Scenario: Atualização bem-sucedida

- **WHEN** um `PUT /api/funcionarios/{id}` é enviado com dados válidos
- **THEN** o cadastro é atualizado
- **AND** a resposta é HTTP 200

#### Scenario: Funcionário inexistente

- **WHEN** um `PUT /api/funcionarios/{id}` referencia um id inexistente
- **THEN** a resposta é HTTP 404 informando que o funcionário não foi encontrado

### Requirement: Inativação de funcionário

O sistema SHALL permitir inativar um funcionário via
`DELETE /api/funcionarios/{id_funcionario}`, alterando o `status` para inativo
sem remover o registro (soft delete).

#### Scenario: Inativação bem-sucedida

- **WHEN** um `DELETE /api/funcionarios/{id}` é realizado para um funcionário ativo
- **THEN** o `status` passa a inativo e o registro é preservado
- **AND** a resposta é HTTP 200

### Requirement: Consulta e filtros de funcionários

O sistema SHALL retornar, em `GET /api/funcionarios`, a lista de funcionários e
SHALL suportar os filtros opcionais `nome`, `cpf`, `cargo`, `id_propriedade` e
`status`.

#### Scenario: Listagem completa

- **WHEN** um `GET /api/funcionarios` é realizado e existem funcionários cadastrados
- **THEN** a resposta é HTTP 200 com a lista de funcionários

#### Scenario: Filtro por nome ou CPF

- **WHEN** um `GET /api/funcionarios?nome=...` ou `?cpf=...` é realizado
- **THEN** a resposta é HTTP 200 contendo apenas os funcionários correspondentes

#### Scenario: Filtro por cargo, propriedade ou status

- **WHEN** um `GET /api/funcionarios?cargo=...`, `?id_propriedade=...` ou `?status=...` é realizado
- **THEN** a resposta é HTTP 200 contendo apenas os funcionários que atendem ao filtro

### Requirement: Indicadores de dashboard de funcionários

O sistema SHALL disponibilizar, em `GET /api/funcionarios/indicadores`, os
totais de funcionários, funcionários ativos, funcionários inativos e a
quantidade de funcionários por propriedade.

#### Scenario: Consulta de indicadores

- **WHEN** um `GET /api/funcionarios/indicadores` é realizado
- **THEN** a resposta é HTTP 200 contendo total, ativos, inativos e a distribuição por propriedade
