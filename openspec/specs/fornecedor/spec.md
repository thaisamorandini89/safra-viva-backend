# fornecedor Specification

## Purpose

Cadastro de fornecedores de insumos, usados no produto e nas entradas de
estoque, com exclusão protegida quando o fornecedor está em uso.

## Requirements

### Requirement: Cadastro de fornecedor

O sistema SHALL permitir cadastrar fornecedores via `POST /api/fornecedores`,
exigindo `nome_fornecedor` e aceitando `nome_fantasia`, `cnpj`, `telefone`,
`email` e `observacoes` opcionais. Os textos SHALL ser gravados sem espaços nas
extremidades e o `cnpj` SHALL ser gravado só com os dígitos. O sistema SHALL
recusar com HTTP 400 o `cnpj` que não tenha 14 dígitos e o `cnpj` já usado por
outro fornecedor.

#### Scenario: Cadastro válido

- **WHEN** um `POST /api/fornecedores` é enviado com `nome_fornecedor` e um
  `cnpj` formatado com pontos, barra e traço
- **THEN** a resposta é HTTP 201 com `id_fornecedor` e `nome_fornecedor`
- **AND** o fornecedor é gravado ativo, com o `cnpj` só com os 14 dígitos

#### Scenario: Nome ausente

- **WHEN** um `POST /api/fornecedores` é enviado sem `nome_fornecedor` ou com ele
  vazio
- **THEN** a resposta é HTTP 400
- **AND** nenhum fornecedor é criado

#### Scenario: CNPJ com quantidade de dígitos errada

- **WHEN** um `POST /api/fornecedores` é enviado com `cnpj` que não tem 14
  dígitos
- **THEN** a resposta é HTTP 400 com mensagem indicando o CNPJ inválido
- **AND** nenhum fornecedor é criado

#### Scenario: CNPJ repetido

- **WHEN** um `POST /api/fornecedores` é enviado com o `cnpj` de um fornecedor já
  cadastrado, com ou sem formatação
- **THEN** a resposta é HTTP 400 com mensagem indicando o CNPJ repetido
- **AND** nenhum fornecedor é criado

### Requirement: Consulta de fornecedores

O sistema SHALL expor `GET /api/fornecedores`, devolvendo todos os fornecedores,
ativos e inativos, em ordem alfabética de `nome_fornecedor`, e
`GET /api/fornecedores/{id_fornecedor}`, devolvendo um fornecedor. Cada item
SHALL trazer `id_fornecedor`, `nome_fornecedor`, `nome_fantasia`, `cnpj`,
`telefone`, `email`, `observacoes` e `status`.

#### Scenario: Listagem

- **WHEN** um `GET /api/fornecedores` é realizado
- **THEN** a resposta é HTTP 200 com os fornecedores em ordem alfabética,
  incluindo os inativos

#### Scenario: Fornecedor inexistente

- **WHEN** um `GET /api/fornecedores/{id_fornecedor}` é feito para um id
  inexistente
- **THEN** a resposta é HTTP 404

### Requirement: Atualização de fornecedor

O sistema SHALL permitir atualização parcial via
`PUT /api/fornecedores/{id_fornecedor}`, alterando apenas os campos enviados,
inclusive `status`, com as mesmas regras do cadastro.

#### Scenario: Atualização válida

- **WHEN** um `PUT /api/fornecedores/{id_fornecedor}` é enviado com `telefone`
- **THEN** a resposta é HTTP 200
- **AND** só o telefone do fornecedor é alterado

#### Scenario: Fornecedor inativado

- **WHEN** um `PUT /api/fornecedores/{id_fornecedor}` é enviado com `status`
  falso
- **THEN** a resposta é HTTP 200
- **AND** o fornecedor continua sendo devolvido por `GET /api/fornecedores`, com
  `status` falso

#### Scenario: Dado inválido na atualização

- **WHEN** um `PUT /api/fornecedores/{id_fornecedor}` é enviado com
  `nome_fornecedor` vazio, com `cnpj` sem 14 dígitos ou com o `cnpj` de outro
  fornecedor
- **THEN** a resposta é HTTP 400
- **AND** o fornecedor permanece inalterado

#### Scenario: Atualização de fornecedor inexistente

- **WHEN** um `PUT /api/fornecedores/{id_fornecedor}` é feito para um id
  inexistente
- **THEN** a resposta é HTTP 404

### Requirement: Exclusão de fornecedor

O sistema SHALL permitir excluir um fornecedor via
`DELETE /api/fornecedores/{id_fornecedor}` e SHALL recusar com HTTP 400, com
mensagem indicando que o fornecedor está em uso e pode ser inativado, a exclusão
de um fornecedor referenciado por algum produto ou por alguma movimentação de
estoque.

#### Scenario: Exclusão de fornecedor sem uso

- **WHEN** um `DELETE /api/fornecedores/{id_fornecedor}` é feito para um
  fornecedor sem produtos nem movimentações
- **THEN** a resposta é HTTP 200
- **AND** o fornecedor deixa de ser devolvido por `GET /api/fornecedores`

#### Scenario: Fornecedor usado por produto

- **WHEN** um `DELETE /api/fornecedores/{id_fornecedor}` é feito para um
  fornecedor referenciado por um produto
- **THEN** a resposta é HTTP 400 com mensagem indicando que o fornecedor está em
  uso
- **AND** o fornecedor continua cadastrado

#### Scenario: Fornecedor usado em entrada de estoque

- **WHEN** um `DELETE /api/fornecedores/{id_fornecedor}` é feito para um
  fornecedor referenciado só por uma movimentação de entrada
- **THEN** a resposta é HTTP 400 com mensagem indicando que o fornecedor está em
  uso
- **AND** o fornecedor continua cadastrado

#### Scenario: Exclusão de fornecedor inexistente

- **WHEN** um `DELETE /api/fornecedores/{id_fornecedor}` é feito para um id
  inexistente
- **THEN** a resposta é HTTP 404
