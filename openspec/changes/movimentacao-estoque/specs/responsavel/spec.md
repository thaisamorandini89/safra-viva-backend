# responsavel Spec Delta

## ADDED Requirements

### Requirement: Estrutura da entidade Responsável

O sistema SHALL persistir responsáveis na tabela `responsavel` com
`id_responsavel` (PK inteira autoincremental), `nome` (String(150),
obrigatório), `cargo` (String(100), opcional) e `status` (booleano,
padrão verdadeiro).

#### Scenario: Tabela criada por migration

- **WHEN** a migration é aplicada
- **THEN** a tabela `responsavel` existe com as colunas e restrições descritas

### Requirement: Cadastro e listagem de responsáveis

O sistema SHALL expor `POST /api/responsaveis` (exigindo `nome` não vazio) e
`GET /api/responsaveis` (lista ordenada por nome).

#### Scenario: Cadastro realizado

- **WHEN** um `POST /api/responsaveis` é enviado com `nome` preenchido
- **THEN** o responsável é persistido com `status` verdadeiro por padrão
- **AND** a resposta é HTTP 201 com `id_responsavel`, `nome` e `cargo`

#### Scenario: Nome ausente

- **WHEN** um `POST /api/responsaveis` é enviado sem `nome` ou com valor vazio
- **THEN** nenhum responsável é criado
- **AND** a resposta é HTTP 400

#### Scenario: Listagem

- **WHEN** um `GET /api/responsaveis` é realizado
- **THEN** a resposta é HTTP 200 com os responsáveis ordenados por nome
