# insumo Specification

## Purpose
TBD - created by archiving change insumo-spec-e-fix-serializacao. Update Purpose after archive.

## Requirements

### Requirement: Estrutura da entidade Insumo

O sistema SHALL representar o insumo como item de estoque vinculado a um produto,
na tabela `insumo`, com `id_insumo` (PK), `id_produto` (FK obrigatória para
`produto.id_produto`), `estoque_atual` (numérico 14,3 obrigatório, padrão 0),
`estoque_minimo` e `valor_unitario` (numéricos opcionais, padrão 0), `status`
(booleano, padrão verdadeiro) e `data_cadastro` (preenchida pelo banco).

Os dados comerciais (nome, categoria, unidade de medida, fabricante e marca)
SHALL permanecer no produto, nunca duplicados no insumo.

#### Scenario: Insumo persistido com vínculo obrigatório

- **WHEN** um insumo é criado
- **THEN** ele referencia obrigatoriamente um produto existente
- **AND** os valores numéricos não informados são gravados como 0

### Requirement: Cadastro de insumo

O sistema SHALL permitir cadastrar insumos via `POST /api/insumos`, exigindo
`id_produto` válido e aceitando `estoque_atual`, `estoque_minimo` e
`valor_unitario` opcionais.

#### Scenario: Cadastro realizado com sucesso

- **WHEN** um `POST /api/insumos` é enviado com `id_produto` existente
- **THEN** o insumo é persistido
- **AND** a resposta é HTTP 201 contendo `id_insumo` e `id_produto`

#### Scenario: Produto ausente ou inexistente

- **WHEN** um `POST /api/insumos` é enviado sem `id_produto` ou com um id inexistente
- **THEN** nenhum insumo é criado
- **AND** a resposta é HTTP 400 com a mensagem de erro correspondente

#### Scenario: Valor numérico inválido

- **WHEN** um campo numérico é enviado com um valor não conversível
- **THEN** a operação é rejeitada
- **AND** a resposta é HTTP 400 indicando o campo inválido

### Requirement: Consulta de insumos com dados do produto

O sistema SHALL retornar, em `GET /api/insumos` e `GET /api/insumos/{id_insumo}`,
os dados de estoque do insumo enriquecidos com os dados do produto vinculado:
`nome_produto`, `id_categoria_insumo`, `categoria_nome`, `unidade_medida`,
`id_fabricante`, `fabricante_nome`, `id_marca` e `descricao_marca`.

Os valores relacionados SHALL ser resolvidos a partir das chaves estrangeiras do
produto, nunca de atributos de texto inexistentes no modelo.

#### Scenario: Listagem com produto completo

- **WHEN** um `GET /api/insumos` é realizado e existem insumos cadastrados
- **THEN** a resposta é HTTP 200
- **AND** cada item traz os dados de estoque e os dados do produto vinculado,
  incluindo o nome do fabricante e a descrição da marca

#### Scenario: Produto sem fabricante ou sem marca

- **WHEN** o produto vinculado não possui fabricante e/ou marca
- **THEN** a resposta é HTTP 200
- **AND** os ids correspondentes são nulos e os nomes retornam vazios,
  sem erro de servidor

#### Scenario: Insumo inexistente

- **WHEN** um `GET /api/insumos/{id_insumo}` é feito para um id inexistente
- **THEN** a resposta é HTTP 404 com mensagem de insumo não encontrado

### Requirement: Atualização de insumo

O sistema SHALL permitir atualização parcial via
`PUT /api/insumos/{id_insumo}`, alterando apenas os campos presentes no payload
e validando o produto quando `id_produto` for informado.

#### Scenario: Atualização parcial

- **WHEN** um `PUT /api/insumos/{id_insumo}` é enviado com apenas alguns campos
- **THEN** somente os campos enviados são alterados
- **AND** a resposta é HTTP 200

#### Scenario: Atualização de insumo inexistente

- **WHEN** um `PUT /api/insumos/{id_insumo}` é feito para um id inexistente
- **THEN** a resposta é HTTP 404

### Requirement: Exclusão de insumo

O sistema SHALL permitir excluir um insumo via `DELETE /api/insumos/{id_insumo}`.

#### Scenario: Exclusão realizada

- **WHEN** um `DELETE /api/insumos/{id_insumo}` é feito para um insumo existente
- **THEN** o registro é removido
- **AND** a resposta é HTTP 200 com mensagem de sucesso

#### Scenario: Exclusão de insumo inexistente

- **WHEN** um `DELETE /api/insumos/{id_insumo}` é feito para um id inexistente
- **THEN** a resposta é HTTP 404
