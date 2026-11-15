# atividade Spec Delta

## ADDED Requirements

### Requirement: Estrutura da entidade Atividade

O sistema SHALL persistir atividades agrícolas na tabela `atividade` com
`id_atividade` (PK inteira autoincremental), `descricao` (String(100),
obrigatório), `data_atividade` (Date, opcional) e `status` (booleano, padrão
verdadeiro).

#### Scenario: Tabela criada por migration

- **WHEN** a migration é aplicada
- **THEN** a tabela `atividade` existe com as colunas descritas

### Requirement: Cadastro e listagem de atividades

O sistema SHALL expor `POST /api/atividades` (exigindo `descricao` não vazia)
e `GET /api/atividades` (ordenadas por `data_atividade` decrescente), para
alimentar o seletor "Atividade Relacionada" da saída de estoque.

#### Scenario: Cadastro realizado

- **WHEN** um `POST /api/atividades` é enviado com `descricao` preenchida
- **THEN** a atividade é persistida
- **AND** a resposta é HTTP 201 com `id_atividade`, `descricao` e
  `data_atividade`

#### Scenario: Descrição ausente

- **WHEN** um `POST /api/atividades` é enviado sem `descricao` ou com valor vazio
- **THEN** nenhuma atividade é criada
- **AND** a resposta é HTTP 400

#### Scenario: Listagem para o seletor

- **WHEN** um `GET /api/atividades` é realizado
- **THEN** a resposta é HTTP 200 com as atividades (descrição e data)
  ordenadas da mais recente para a mais antiga
