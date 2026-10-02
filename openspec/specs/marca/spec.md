# marca Specification

## Purpose
TBD - created by archiving change add-marca-entity. Update Purpose after archive.

## Requirements

### Requirement: Estrutura da entidade Marca

O sistema SHALL persistir marcas em uma tabela `marca` com chave primária
`id_marca` (inteiro autoincremental) e o campo `descricao_marca`
(texto de até 500 caracteres, obrigatório e único).

#### Scenario: Tabela criada por migration

- **WHEN** a migration de criação da marca é aplicada
- **THEN** a tabela `marca` existe com as colunas `id_marca` e `descricao_marca`
- **AND** `descricao_marca` possui restrições de NOT NULL e UNIQUE

### Requirement: Cadastro de marca

O sistema SHALL permitir o cadastro de uma marca via `POST /api/marcas`,
recebendo JSON com `descricao_marca`, removendo espaços nas extremidades
antes de persistir.

#### Scenario: Cadastro realizado com sucesso

- **WHEN** um `POST /api/marcas` é enviado com `descricao_marca` preenchido e inédito
- **THEN** a marca é persistida
- **AND** a resposta é HTTP 201 contendo `id_marca` e `descricao_marca`

#### Scenario: Descrição ausente ou vazia

- **WHEN** um `POST /api/marcas` é enviado sem `descricao_marca` ou com valor vazio
- **THEN** nenhuma marca é criada
- **AND** a resposta é HTTP 400 com mensagem indicando que a descrição é obrigatória

#### Scenario: Descrição duplicada

- **WHEN** um `POST /api/marcas` é enviado com `descricao_marca` já existente
- **THEN** nenhuma marca é criada
- **AND** a resposta é HTTP 400 com mensagem de duplicidade

### Requirement: Listagem de marcas

O sistema SHALL expor `GET /api/marcas` retornando todas as marcas ordenadas
alfabeticamente por `descricao_marca`.

#### Scenario: Listagem retornada

- **WHEN** um `GET /api/marcas` é realizado
- **THEN** a resposta é HTTP 200 com um array de objetos contendo
  `id_marca` e `descricao_marca` em ordem alfabética

### Requirement: Atualização de marca

O sistema SHALL permitir atualizar a descrição de uma marca existente via
`PUT /api/marcas/{id_marca}`, aplicando as mesmas validações de obrigatoriedade,
remoção de espaços nas extremidades e unicidade usadas no cadastro.

#### Scenario: Atualização realizada com sucesso

- **WHEN** um `PUT /api/marcas/{id_marca}` é enviado para uma marca existente
  com `descricao_marca` válido
- **THEN** a descrição é persistida
- **AND** a resposta é HTTP 200 contendo `id_marca` e `descricao_marca` atualizados

#### Scenario: Marca inexistente

- **WHEN** um `PUT /api/marcas/{id_marca}` é enviado para um id inexistente
- **THEN** nenhuma alteração é realizada
- **AND** a resposta é HTTP 404 com mensagem de marca não encontrada

#### Scenario: Descrição inválida ou duplicada na atualização

- **WHEN** um `PUT /api/marcas/{id_marca}` é enviado sem `descricao_marca`,
  com valor vazio ou com descrição já usada por outra marca
- **THEN** nenhuma alteração é realizada
- **AND** a resposta é HTTP 400 com a mensagem de erro correspondente

### Requirement: Exclusão de marca

O sistema SHALL permitir excluir uma marca existente via
`DELETE /api/marcas/{id_marca}`.

#### Scenario: Exclusão realizada com sucesso

- **WHEN** um `DELETE /api/marcas/{id_marca}` é enviado para uma marca existente
- **THEN** o registro é removido da tabela `marca`
- **AND** a resposta é HTTP 200 com mensagem de sucesso

#### Scenario: Exclusão de marca inexistente

- **WHEN** um `DELETE /api/marcas/{id_marca}` é enviado para um id inexistente
- **THEN** nenhuma exclusão é realizada
- **AND** a resposta é HTTP 404 com mensagem de marca não encontrada
