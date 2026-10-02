# Adicionar Movimentação de Estoque com Responsável

## Why

O módulo de insumos controla apenas o saldo estático (`estoque_atual`), sem
histórico de entradas e saídas nem rastreabilidade de quem realizou cada
operação. Hoje o saldo é editado diretamente via `PUT /api/insumos`, o que não
deixa trilha de auditoria. É necessário registrar movimentações que atualizem o
saldo de forma transacional e permitam reconstituir o histórico.

Como não existe cadastro de responsáveis no banco, a entidade `Responsavel`
precisa ser criada antes, para ser referenciada pela movimentação.

## What Changes

- Nova entidade `Responsavel` (`models/responsavel.py`): `id_responsavel` (PK),
  `nome` (String(150), obrigatório), `cargo` (String(100), opcional),
  `status` (Boolean, default True).
- Nova entidade `MovimentacaoEstoque` (`models/movimentacao_estoque.py`):
  `id_movimentacao` (UUID string, PK), `id_insumo` (FK obrigatória),
  `tipo_movimentacao` ('ENTRADA' | 'SAIDA', obrigatório), `quantidade`
  (Numeric(10,2), obrigatório), `data_movimentacao` (server default now),
  `id_responsavel` (FK opcional), `observacao` (String(500), opcional).
- Migration Alembic criando as tabelas `responsavel` e `movimentacao_estoque`.
- Schemas Pydantic (`schemas/movimentacao_schema.py`) para validar o payload de
  criação de movimentação (tipo, quantidade positiva, campos opcionais).
- Regra de negócio no serviço: ENTRADA soma `quantidade` ao `estoque_atual` do
  insumo; SAIDA subtrai, rejeitando a operação quando o saldo for insuficiente.
  Registro da movimentação e atualização do saldo na mesma transação.
- Endpoints em `controllers/movimentacao_controller.py`:
  - `POST /api/movimentacoes` — registra a movimentação e atualiza o estoque.
  - `GET /api/movimentacoes` — lista o histórico, com filtro `?id_insumo=`.
- CRUD mínimo de responsável (`GET`/`POST /api/responsaveis`) para viabilizar o
  vínculo.
- Registro dos blueprints em `app.py` e requisições no `insomnia_safraviva.json`.

## Impact

- Affected specs: `responsavel` (nova), `movimentacao-estoque` (nova),
  `insumo` (modificada: saldo passa a ser atualizado por movimentação)
- Affected code: `models/responsavel.py`, `models/movimentacao_estoque.py`,
  `models/__init__.py`, `schemas/movimentacao_schema.py`,
  `services/responsavel_service.py`, `services/movimentacao_service.py`,
  `controllers/responsavel_controller.py`,
  `controllers/movimentacao_controller.py`, `app.py`,
  `migrations/versions/*`, `insomnia_safraviva.json`
- Sem breaking changes: os endpoints de insumo continuam funcionando;
  a edição direta de `estoque_atual` via `PUT /api/insumos` permanece
  (desaconselhada, mas não removida nesta change).

## Out of Scope

- Remoção/bloqueio da edição direta de `estoque_atual` no `PUT /api/insumos`.
- Edição e exclusão (estorno) de movimentações já registradas.
- CRUD completo de responsável (atualização/exclusão) e vínculo com usuários.
- Relatórios e alertas de estoque mínimo.
