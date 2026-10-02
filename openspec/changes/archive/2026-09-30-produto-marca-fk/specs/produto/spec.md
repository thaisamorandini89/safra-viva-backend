# produto Spec Delta

## ADDED Requirements

### Requirement: Vínculo de produto com marca

O produto SHALL referenciar a marca por meio do campo `id_marca`, chave
estrangeira opcional para `marca.id_marca`. O campo texto livre `marca` SHALL
deixar de existir no modelo e na API.

#### Scenario: Estrutura da coluna

- **WHEN** a migration de refatoração é aplicada
- **THEN** a tabela `produto` possui a coluna `id_marca` com FK para `marca.id_marca`
- **AND** a coluna `marca` não existe mais

#### Scenario: Migração dos dados existentes

- **WHEN** a migration é aplicada sobre produtos com textos de marca preenchidos
- **THEN** cada descrição distinta não nula passa a existir na tabela `marca`
- **AND** cada produto referencia a marca correspondente ao seu texto anterior
- **AND** produtos sem marca permanecem com `id_marca` nulo

### Requirement: Cadastro e atualização de produto com marca

O sistema SHALL aceitar `id_marca` nos payloads de criação e atualização de
produto, validando que a marca informada existe.

#### Scenario: Produto criado com marca válida

- **WHEN** um produto é cadastrado com `id_marca` existente
- **THEN** o produto é persistido vinculado àquela marca
- **AND** a resposta é HTTP 201

#### Scenario: Marca inexistente informada

- **WHEN** um produto é cadastrado ou atualizado com `id_marca` que não existe
- **THEN** a operação é rejeitada
- **AND** a resposta é HTTP 400 com mensagem indicando marca inválida

#### Scenario: Produto sem marca

- **WHEN** um produto é cadastrado sem `id_marca` ou atualizado com `id_marca` nulo
- **THEN** o produto é persistido com `id_marca` nulo
- **AND** a operação é concluída com sucesso

### Requirement: Retorno da marca do produto

O sistema SHALL retornar, nas respostas de produto, os campos `id_marca` e
`descricao_marca`, ambos nulos quando o produto não possuir marca vinculada.

#### Scenario: Listagem com marca vinculada

- **WHEN** um `GET` de produtos é realizado
- **THEN** cada produto com marca retorna `id_marca` e a `descricao_marca` correspondente
- **AND** produtos sem marca retornam ambos os campos nulos
