# categoria-atividade Spec Delta

## ADDED Requirements

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
