# categoria-atividade Specification

## Purpose
Catálogo das categorias operacionais (Preparo de Solo, Plantio, Tratos
Culturais e outras) que agrupam os tipos de atividade e classificam as operações
de campo.

## Requirements

### Requirement: Estrutura da categoria de atividade

O sistema SHALL persistir categorias de atividade na tabela
`categoria_atividade` com `id_categoria_atividade` (PK inteira autoincremental),
`nome` (String(80), obrigatório e único) e `status` (booleano, padrão
verdadeiro).

#### Scenario: Tabela criada por migration

- **WHEN** a migration é aplicada
- **THEN** a tabela `categoria_atividade` existe com as colunas descritas

### Requirement: Cadastro e manutenção de categorias

O sistema SHALL expor `GET /api/categorias-atividade`,
`POST /api/categorias-atividade`, `PUT /api/categorias-atividade/{id}` e
`DELETE /api/categorias-atividade/{id}`. O `nome` SHALL ser obrigatório e único.

#### Scenario: Cadastro realizado

- **WHEN** um `POST /api/categorias-atividade` é enviado com `nome` preenchido e
  inédito
- **THEN** a categoria é persistida
- **AND** a resposta é HTTP 201 com `id_categoria_atividade` e `nome`

#### Scenario: Nome ausente

- **WHEN** um `POST /api/categorias-atividade` é enviado sem `nome` ou vazio
- **THEN** a resposta é HTTP 400 e nada é persistido

#### Scenario: Nome duplicado

- **WHEN** um `POST /api/categorias-atividade` usa um `nome` já existente
- **THEN** a resposta é HTTP 400 e nada é persistido

#### Scenario: Listagem

- **WHEN** um `GET /api/categorias-atividade` é realizado
- **THEN** a resposta é HTTP 200 com as categorias cadastradas

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
