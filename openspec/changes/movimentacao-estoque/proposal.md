# Adicionar Movimentação de Estoque com Responsável

## Why

O módulo de insumos controla apenas o saldo estático (`estoque_atual`), sem
histórico de entradas e saídas nem rastreabilidade de quem realizou cada
operação. Hoje o saldo é editado diretamente via `PUT /api/insumos`, o que não
deixa trilha de auditoria. É necessário registrar movimentações que atualizem o
saldo de forma transacional e permitam reconstituir o histórico.

Como não existe cadastro de responsáveis no banco, a entidade `Responsavel`
precisa ser criada antes, para ser referenciada pela movimentação.

**Atualização (14/10/2026)**: com o módulo de Gestão de Funcionários entregue,
o responsável da movimentação passa a ser o **Funcionário** cadastrado
(`funcionario.id_funcionario`), substituindo a entidade provisória
`Responsavel`. Além disso, as telas de Saída mostram que a "Atividade
Relacionada" é uma seleção de registros existentes (Pulverização, Adubação,
Calagem, etc. com datas) — portanto vira a entidade `Atividade` referenciada
por FK, e não um texto livre.

## What Changes

- ~~Nova entidade `Responsavel`~~ **Substituída**: o responsável passa a ser o
  `Funcionario` já existente. A movimentação ganha `id_funcionario`
  (String(36), FK → `funcionario.id_funcionario`); a entidade `Responsavel`,
  sua tabela, serviço, controller e endpoints `/api/responsaveis` são
  **removidos**.
- Nova entidade `Atividade` (`models/atividade.py`): `id_atividade` (PK),
  `descricao` (String(100), obrigatório), `data_atividade` (Date, opcional),
  `status` (Boolean, default True), com `GET`/`POST /api/atividades` para
  alimentar o seletor da interface.
- Nova entidade `MovimentacaoEstoque` (`models/movimentacao_estoque.py`):
  `id_movimentacao` (UUID string, PK), `id_insumo` (FK obrigatória),
  `tipo_movimentacao` ('ENTRADA' | 'SAIDA', obrigatório), `quantidade`
  (Numeric(10,2), obrigatório), `valor_unitario` (Numeric(14,2), opcional),
  `data_movimentacao` (server default now), `id_funcionario` (FK opcional no
  banco; obrigatório na interface), `observacao` (String(500), opcional).
- Campos de detalhe de ENTRADA (todos `nullable=True`):
  `id_fornecedor` (FK → `fornecedor.id_fornecedor`), `numero_nota_fiscal`
  (String(50)), `numero_lote` (String(50)), `data_fabricacao` (Date),
  `data_validade` (Date).
- Campos de destino/rastreabilidade de SAIDA (todos `nullable=True`):
  `id_talhao` (FK → `talhao.id_talhao`), `safra` (String(20)),
  `id_atividade` (FK → `atividade.id_atividade`),
  `destino_finalidade` (String(255)).
- Migrations Alembic: criar `atividade`, garantir `funcionario` aplicada,
  ajustar `movimentacao_estoque` (trocar `id_responsavel` por
  `id_funcionario`, adicionar novos campos) e remover a tabela `responsavel`.
- Schemas Pydantic (`schemas/movimentacao_schema.py`) para validar o payload de
  criação de movimentação (tipo, quantidade positiva, campos opcionais),
  incluindo os campos de detalhe de entrada e de saída, com validação cruzada:
  campos de entrada só são aceitos em movimentações ENTRADA e campos de
  destino/rastreabilidade só em SAIDA.
- Regra de negócio no serviço: ENTRADA soma `quantidade` ao `estoque_atual` do
  insumo; SAIDA subtrai, rejeitando a operação quando o saldo for insuficiente.
  Registro da movimentação e atualização do saldo na mesma transação.
- Endpoints em `controllers/movimentacao_controller.py`:
  - `POST /api/movimentacoes` — registra a movimentação e atualiza o estoque.
  - `GET /api/movimentacoes` — lista o histórico, com filtro `?id_insumo=`.
- CRUD mínimo de atividade (`GET`/`POST /api/atividades`) para viabilizar o
  vínculo da saída.
- Registro dos blueprints em `app.py` e requisições no `insomnia_safraviva.json`.

## Impact

- Affected specs: `movimentacao-estoque` (nova), `atividade` (nova),
  `responsavel` (**removida** — substituída por funcionário),
  `insumo` (modificada: saldo passa a ser atualizado por movimentação)
- Affected code: `models/atividade.py`, `models/movimentacao_estoque.py`,
  `models/responsavel.py` (removido), `models/__init__.py`,
  `schemas/movimentacao_schema.py`,
  `services/atividade_service.py`, `services/movimentacao_service.py`,
  `services/responsavel_service.py` (removido),
  `controllers/atividade_controller.py`,
  `controllers/movimentacao_controller.py`,
  `controllers/responsavel_controller.py` (removido), `app.py`,
  `migrations/versions/*`, `insomnia_safraviva.json`
- **Breaking** para quem já consome a movimentação: o payload troca
  `id_responsavel` por `id_funcionario` e `atividade_relacionada` (texto) por
  `id_atividade` (FK); os endpoints `/api/responsaveis` deixam de existir.
- Sem breaking changes: os endpoints de insumo continuam funcionando;
  a edição direta de `estoque_atual` via `PUT /api/insumos` permanece
  (desaconselhada, mas não removida nesta change).

## Out of Scope

- Remoção/bloqueio da edição direta de `estoque_atual` no `PUT /api/insumos`.
- Edição e exclusão (estorno) de movimentações já registradas.
- CRUD completo de atividade (atualização/exclusão) e vínculo de atividade com
  talhão/safra.
- Relatórios e alertas de estoque mínimo.
