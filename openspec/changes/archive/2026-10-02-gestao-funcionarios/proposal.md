# Proposal

## Why

A empresa agrícola não possui hoje nenhum cadastro de colaboradores: existe
apenas a entidade mínima `Responsavel` (`nome`, `cargo`, `status`), usada para
assinar movimentações de estoque. Não há CPF único, dados pessoais e
profissionais, controle de admissão/desligamento, nem vínculo com propriedades.
Sem isso falta rastreabilidade operacional e base para futuras funcionalidades
de atividades, produtividade e folha de pagamento. O Módulo 1.1 — Gestão de
Funcionários cria essa base.

## What Changes

- Nova entidade `Funcionario` (`models/funcionario.py`): `id_funcionario`
  (String(36) UUID, PK), `nome_completo` (String(150), obrigatório), `cpf`
  (String(11), único e obrigatório), `rg` (String(20), opcional),
  `data_nascimento` (Date, opcional), `telefone` (String(20), opcional),
  `email` (String(100), opcional), `cargo` (String(100), obrigatório),
  `data_admissao` (Date, obrigatório), `data_desligamento` (Date, opcional),
  `status` (Boolean, default True → Ativo/Inativo), `observacoes`
  (String(500), opcional), `data_cadastro` (DateTime, server default).
- Nova entidade de vínculo `FuncionarioPropriedade`
  (`models/funcionario_propriedade.py`): `id_funcionario_propriedade`
  (String(36) UUID, PK), `id_funcionario` (FK obrigatória para
  `funcionario`), `id_propriedade` (FK obrigatória para `propriedade`),
  `data_vinculacao` (Date/DateTime, default now). Permite vincular um
  funcionário a uma ou mais propriedades.
- Migration Alembic criando as tabelas `funcionario` e
  `funcionario_propriedade` (funcionário antes do vínculo).
- Schemas Pydantic (`schemas/funcionario_schema.py`) validando o payload de
  criação/atualização (CPF com 11 dígitos, campos obrigatórios, datas,
  normalização de CPF/telefone).
- Serviço `services/funcionario_service.py` com CRUD, inativação, busca por
  nome/CPF/cargo/propriedade/status, vínculo de propriedades e indicadores de
  dashboard (total, ativos, inativos, por propriedade).
- Endpoints REST em `controllers/funcionario_controller.py` sob `/api`:
  - `GET /api/funcionarios` — lista com filtros `?nome=`, `?cpf=`, `?cargo=`,
    `?id_propriedade=`, `?status=`.
  - `POST /api/funcionarios` — cadastra funcionário (CPF único).
  - `GET /api/funcionarios/{id}` — detalhe.
  - `PUT /api/funcionarios/{id}` — atualiza cadastro.
  - `DELETE /api/funcionarios/{id}` — inativa (soft delete via `status`).
  - `POST /api/funcionarios/{id}/propriedades` — vincula propriedade.
  - `GET /api/funcionarios/{id}/propriedades` — lista propriedades vinculadas.
  - `GET /api/funcionarios/indicadores` — cards do dashboard.
- Registro do blueprint em `app.py` e requisições no `insomnia_safraviva.json`.

## Capabilities

### New Capabilities
- `funcionario`: cadastro e gestão de colaboradores da empresa agrícola —
  dados pessoais e profissionais, CPF único, status ativo/inativo,
  admissão/desligamento, consultas/filtros e indicadores de dashboard.
- `funcionario-propriedade`: vínculo de funcionários a uma ou mais
  propriedades, com data de vinculação e consulta da distribuição de mão de
  obra por propriedade.

### Modified Capabilities
<!-- Nenhuma capability existente tem requisitos alterados. A entidade
     `Responsavel` permanece como está; `Funcionario` é uma entidade nova e
     independente. -->

## Impact

- Affected specs: `funcionario` (nova), `funcionario-propriedade` (nova)
- Affected code: `models/funcionario.py`, `models/funcionario_propriedade.py`,
  `models/__init__.py`, `schemas/funcionario_schema.py`,
  `services/funcionario_service.py`,
  `controllers/funcionario_controller.py`, `app.py`,
  `migrations/versions/*`, `insomnia_safraviva.json`
- Depende da entidade existente `Propriedade` (FK no vínculo).
- Sem breaking changes: a entidade `Responsavel` e os endpoints de
  movimentação de estoque continuam funcionando inalterados.

## Out of Scope

- Upload/armazenamento de anexos de documentos do colaborador (apenas
  `observacoes` nesta change; anexos ficam para evolução futura).
- Histórico/auditoria de alterações cadastrais (mencionado nos critérios,
  mas tratado em change futura).
- Apontamento de horas, equipes, produtividade e integração com folha de
  pagamento (evolução futura).
- Autenticação/perfis de acesso dos usuários do sistema.
