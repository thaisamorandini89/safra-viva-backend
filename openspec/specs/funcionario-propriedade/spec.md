# funcionario-propriedade Specification

## Purpose

Permite vincular funcionários a uma ou mais propriedades da empresa agrícola,
registrando a data de vinculação e possibilitando visualizar a distribuição da
mão de obra por propriedade.

## Requirements

### Requirement: Estrutura do vínculo Funcionário-Propriedade

O sistema SHALL representar o vínculo na tabela `funcionario_propriedade` com
`id_funcionario_propriedade` (UUID string, PK), `id_funcionario` (FK
obrigatória para `funcionario`), `id_propriedade` (FK obrigatória para
`propriedade`) e `data_vinculacao` (preenchida pelo sistema quando não
informada).

#### Scenario: Vínculo persistido

- **WHEN** um vínculo é criado entre um funcionário e uma propriedade existentes
- **THEN** o registro é gravado com `data_vinculacao` preenchida

### Requirement: Vinculação de funcionário a propriedade

O sistema SHALL permitir vincular um funcionário a uma propriedade via
`POST /api/funcionarios/{id_funcionario}/propriedades`, aceitando que um mesmo
funcionário seja vinculado a mais de uma propriedade.

#### Scenario: Vínculo criado com sucesso

- **WHEN** um `POST /api/funcionarios/{id}/propriedades` é enviado com `id_propriedade` existente
- **THEN** o vínculo é persistido
- **AND** a resposta é HTTP 201

#### Scenario: Funcionário ou propriedade inexistente

- **WHEN** o funcionário ou a propriedade informados não existem
- **THEN** nenhum vínculo é criado
- **AND** a resposta é HTTP 400 indicando o registro não encontrado

### Requirement: Consulta de propriedades vinculadas

O sistema SHALL listar, em
`GET /api/funcionarios/{id_funcionario}/propriedades`, as propriedades
vinculadas ao funcionário.

#### Scenario: Listagem de vínculos

- **WHEN** um `GET /api/funcionarios/{id}/propriedades` é realizado
- **THEN** a resposta é HTTP 200 com as propriedades vinculadas e suas datas de vinculação
