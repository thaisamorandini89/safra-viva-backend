# tipo-atividade Spec Delta

## ADDED Requirements

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
