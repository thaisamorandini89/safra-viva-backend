# tipo-atividade Specification

## Purpose
Catálogo dos tipos de atividade (Aração, Adubação, Pulverização e outros), cada
um vinculado a uma categoria, usado nas operações agrícolas e nas saídas de
estoque.

## Requirements

### Requirement: Estrutura do tipo de atividade

O sistema SHALL persistir tipos de atividade na tabela `tipo_atividade`
(renomeada a partir de `atividade`) com `id_atividade` (PK inteira
autoincremental), `descricao` (String(100), obrigatório), `id_categoria_atividade`
(FK para `categoria_atividade`, obrigatório) e `status` (booleano, padrão
verdadeiro). A coluna `data_atividade` da versão anterior SHALL ser removida.

#### Scenario: Tabela renomeada por migration

- **WHEN** a migration é aplicada
- **THEN** a tabela `tipo_atividade` existe com as colunas descritas
- **AND** a coluna `data_atividade` não existe mais

### Requirement: Compatibilidade com a movimentação de estoque

O sistema SHALL preservar a referência `movimentacao_estoque.id_atividade`,
agora apontando para `tipo_atividade.id_atividade`, sem alterar o nome nem os
valores da coluna.

#### Scenario: Saída referenciando um tipo

- **WHEN** uma saída de estoque referencia um `id_atividade` existente em
  `tipo_atividade`
- **THEN** a movimentação é registrada normalmente

### Requirement: Cadastro e manutenção de tipos

O sistema SHALL expor `GET /api/tipos-atividade` (com filtro opcional
`id_categoria_atividade`), `POST /api/tipos-atividade`,
`PUT /api/tipos-atividade/{id}` e `DELETE /api/tipos-atividade/{id}`. A
`descricao` SHALL ser obrigatória e a `id_categoria_atividade` SHALL referenciar
uma categoria existente.

#### Scenario: Cadastro realizado

- **WHEN** um `POST /api/tipos-atividade` é enviado com `descricao` e
  `id_categoria_atividade` válidos
- **THEN** o tipo é persistido
- **AND** a resposta é HTTP 201 com `id_atividade`, `descricao` e
  `id_categoria_atividade`

#### Scenario: Categoria inexistente

- **WHEN** um `POST /api/tipos-atividade` referencia uma categoria inexistente
- **THEN** a resposta é HTTP 400 e nada é persistido

#### Scenario: Listagem filtrada por categoria

- **WHEN** um `GET /api/tipos-atividade?id_categoria_atividade=1` é realizado
- **THEN** a resposta inclui apenas os tipos daquela categoria

### Requirement: Exclusão de tipo em uso

O sistema SHALL recusar com HTTP 400, com mensagem indicando que o tipo está em
uso, o `DELETE /api/tipos-atividade/{id}` de um tipo referenciado por alguma
operação agrícola ou por alguma movimentação de estoque, mantendo o tipo
cadastrado.

#### Scenario: Tipo usado em operação

- **WHEN** um `DELETE /api/tipos-atividade/{id}` é enviado para um tipo
  referenciado por uma operação agrícola
- **THEN** a resposta é HTTP 400 com mensagem indicando que o tipo está em uso
- **AND** o tipo continua cadastrado

#### Scenario: Tipo usado em movimentação de estoque

- **WHEN** um `DELETE /api/tipos-atividade/{id}` é enviado para um tipo
  referenciado por uma movimentação de estoque
- **THEN** a resposta é HTTP 400 e o tipo continua cadastrado

#### Scenario: Tipo sem uso

- **WHEN** um `DELETE /api/tipos-atividade/{id}` é enviado para um tipo sem
  operações nem movimentações
- **THEN** a resposta é HTTP 200 e o tipo é removido

#### Scenario: Tipo inexistente

- **WHEN** um `DELETE /api/tipos-atividade/{id}` referencia um `id` inexistente
- **THEN** a resposta é HTTP 404
