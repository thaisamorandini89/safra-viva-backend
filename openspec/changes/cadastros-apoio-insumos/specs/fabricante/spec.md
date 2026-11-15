# fabricante Spec Delta

## Purpose

Cadastro de fabricantes dos produtos usados como insumos, com nome único e
exclusão protegida quando o fabricante está em uso.

## ADDED Requirements

### Requirement: Cadastro de fabricante

O sistema SHALL permitir cadastrar fabricantes via `POST /api/fabricantes`,
exigindo `nome_fabricante` e aceitando `cnpj`, `telefone`, `email`, `website` e
`observacoes` opcionais. Os textos SHALL ser gravados sem espaços nas
extremidades e o `cnpj` SHALL ser gravado só com os dígitos. O sistema SHALL
recusar com HTTP 400 o `cnpj` que não tenha 14 dígitos e o `nome_fabricante` já
usado por outro fabricante, sem diferenciar maiúsculas de minúsculas.

#### Scenario: Cadastro válido

- **WHEN** um `POST /api/fabricantes` é enviado com `nome_fabricante` inédito
- **THEN** a resposta é HTTP 201 com `id_fabricante` e `nome_fabricante`
- **AND** o fabricante é gravado ativo

#### Scenario: Nome ausente

- **WHEN** um `POST /api/fabricantes` é enviado sem `nome_fabricante` ou com ele
  vazio
- **THEN** a resposta é HTTP 400
- **AND** nenhum fabricante é criado

#### Scenario: Nome repetido

- **WHEN** um `POST /api/fabricantes` é enviado com o nome de um fabricante já
  cadastrado, com outra capitalização
- **THEN** a resposta é HTTP 400 com mensagem indicando o nome repetido
- **AND** nenhum fabricante é criado

#### Scenario: CNPJ com quantidade de dígitos errada

- **WHEN** um `POST /api/fabricantes` é enviado com `cnpj` que não tem 14
  dígitos
- **THEN** a resposta é HTTP 400 com mensagem indicando o CNPJ inválido
- **AND** nenhum fabricante é criado

### Requirement: Consulta de fabricantes

O sistema SHALL expor `GET /api/fabricantes`, devolvendo todos os fabricantes,
ativos e inativos, em ordem alfabética de `nome_fabricante`, e
`GET /api/fabricantes/{id_fabricante}`, devolvendo um fabricante. Cada item
SHALL trazer `id_fabricante`, `nome_fabricante`, `cnpj`, `telefone`, `email`,
`website`, `observacoes` e `status`.

#### Scenario: Listagem

- **WHEN** um `GET /api/fabricantes` é realizado
- **THEN** a resposta é HTTP 200 com os fabricantes em ordem alfabética,
  incluindo os inativos

#### Scenario: Fabricante inexistente

- **WHEN** um `GET /api/fabricantes/{id_fabricante}` é feito para um id
  inexistente
- **THEN** a resposta é HTTP 404

### Requirement: Atualização de fabricante

O sistema SHALL permitir atualização parcial via
`PUT /api/fabricantes/{id_fabricante}`, alterando apenas os campos enviados,
inclusive `status`, com as mesmas regras do cadastro.

#### Scenario: Atualização válida

- **WHEN** um `PUT /api/fabricantes/{id_fabricante}` é enviado com `website`
- **THEN** a resposta é HTTP 200
- **AND** só o website do fabricante é alterado

#### Scenario: Fabricante inativado

- **WHEN** um `PUT /api/fabricantes/{id_fabricante}` é enviado com `status`
  falso
- **THEN** a resposta é HTTP 200
- **AND** o fabricante continua sendo devolvido por `GET /api/fabricantes`, com
  `status` falso

#### Scenario: Dado inválido na atualização

- **WHEN** um `PUT /api/fabricantes/{id_fabricante}` é enviado com
  `nome_fabricante` vazio, com o nome de outro fabricante ou com `cnpj` sem 14
  dígitos
- **THEN** a resposta é HTTP 400
- **AND** o fabricante permanece inalterado

#### Scenario: Atualização de fabricante inexistente

- **WHEN** um `PUT /api/fabricantes/{id_fabricante}` é feito para um id
  inexistente
- **THEN** a resposta é HTTP 404

### Requirement: Exclusão de fabricante

O sistema SHALL permitir excluir um fabricante via
`DELETE /api/fabricantes/{id_fabricante}` e SHALL recusar com HTTP 400, com
mensagem indicando que o fabricante está em uso e pode ser inativado, a exclusão
de um fabricante referenciado por algum produto.

#### Scenario: Exclusão de fabricante sem uso

- **WHEN** um `DELETE /api/fabricantes/{id_fabricante}` é feito para um
  fabricante sem produtos
- **THEN** a resposta é HTTP 200
- **AND** o fabricante deixa de ser devolvido por `GET /api/fabricantes`

#### Scenario: Fabricante usado por produto

- **WHEN** um `DELETE /api/fabricantes/{id_fabricante}` é feito para um
  fabricante referenciado por um produto
- **THEN** a resposta é HTTP 400 com mensagem indicando que o fabricante está em
  uso
- **AND** o fabricante continua cadastrado

#### Scenario: Exclusão de fabricante inexistente

- **WHEN** um `DELETE /api/fabricantes/{id_fabricante}` é feito para um id
  inexistente
- **THEN** a resposta é HTTP 404
