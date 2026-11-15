# Proposal

## Why

O SafraViva controla propriedades, talhões, insumos, estoque e funcionários, mas
não possui controle financeiro: não há registro de receitas e despesas, cálculo
de saldo, rateio de custos por área nem indicadores de rentabilidade. Sem isso o
produtor rural não consegue avaliar a saúde financeira da fazenda nem a
rentabilidade por safra, talhão e cultura. Este módulo introduz o controle
financeiro integrado às entidades já existentes.

Como não existe cadastro de safra no banco — e os lançamentos financeiros
precisam ser vinculados a uma safra (RN004) para apurar resultado por safra e por
cultura —, a entidade `Safra` precisa ser criada antes, para ser referenciada
pelos lançamentos.

## What Changes

- Nova entidade `Safra` (`models/safra.py`): cadastro mínimo de safra vinculado a
  uma propriedade, com `cultura` como campo texto auxiliar, período (datas de
  início/fim) e área. Viabiliza o vínculo exigido pelo módulo financeiro.
- Nova entidade `CentroCusto` (`models/centro_custo.py`): `id_centro_custo` (PK),
  `nome`, `tipo` ('OPERACIONAL' | 'ADMINISTRATIVO'), `descricao`, `status`.
- Nova entidade `LancamentoFinanceiro` (`models/lancamento_financeiro.py`): PK
  UUID string, `tipo` ('RECEITA' | 'DESPESA'), `categoria`, `descricao`, `valor`
  (positivo), `data_lancamento`, `forma_pagamento`, `status` ('PENDENTE' |
  'PAGO'), `conciliado` (boolean), `observacao`, e FKs opcionais para empresa,
  propriedade, talhão, safra e centro de custo.
- Nova entidade `RateioLancamento` (`models/rateio_lancamento.py`): distribui uma
  despesa entre vários talhões (RN005), com `id_lancamento` (FK), `id_talhao`
  (FK) e `percentual`/`valor` do rateio.
- Migrations Alembic criando as tabelas `safra`, `centro_custo`,
  `lancamento_financeiro` e `rateio_lancamento`.
- Schemas Pydantic validando os payloads (tipo, valor positivo, categoria,
  forma de pagamento, status, rateio somando 100%).
- Regras de negócio no serviço: lançamento obrigatório com tipo/data/valor/
  categoria (RN001); valor sempre maior que zero (RN002); lançamento conciliado
  não pode ser excluído (RN003); rateio distribuído entre talhões (RN005).
- Endpoints REST:
  - `POST/GET/PUT/DELETE /api/lancamentos` — CRUD de lançamentos com filtros por
    período, tipo, safra, propriedade e talhão.
  - `POST/GET /api/centros-custo` — CRUD mínimo de centro de custo.
  - `POST/GET /api/safras` — CRUD mínimo de safra.
  - `GET /api/financeiro/saldo` — saldo financeiro (receitas − despesas).
  - `GET /api/financeiro/fluxo-caixa` — entradas, saídas e saldo acumulado por
    período.
  - `GET /api/financeiro/indicadores` — KPIs (lucro líquido, custo/receita/lucro
    por hectare, ROI, margem) por safra, talhão e cultura.
- Registro dos novos blueprints em `app.py` e requisições no
  `insomnia_safraviva.json`.

## Capabilities

### New Capabilities
- `safra`: cadastro de safra (período, propriedade, cultura e área) usado como
  dimensão de vínculo e apuração do resultado agrícola.
- `centro-custo`: cadastro de centros de custo operacionais e administrativos
  para classificar despesas.
- `lancamento-financeiro`: registro de receitas e despesas com categorias,
  forma de pagamento, status, vínculos (empresa/propriedade/talhão/safra/centro
  de custo), rateio de despesas entre talhões e regras de integridade.
- `relatorios-financeiros`: visões de agregação sobre lançamentos — saldo,
  fluxo de caixa e indicadores de rentabilidade (KPIs) por safra, talhão e
  cultura.

### Modified Capabilities
<!-- Nenhuma capacidade existente tem suas requisições alteradas. -->

## Impact

- Affected specs: `safra` (nova), `centro-custo` (nova),
  `lancamento-financeiro` (nova), `relatorios-financeiros` (nova)
- Affected code: `models/safra.py`, `models/centro_custo.py`,
  `models/lancamento_financeiro.py`, `models/rateio_lancamento.py`,
  `models/__init__.py`, `schemas/safra_schema.py`,
  `schemas/centro_custo_schema.py`, `schemas/lancamento_schema.py`,
  `services/safra_service.py`, `services/centro_custo_service.py`,
  `services/lancamento_service.py`, `services/financeiro_service.py`,
  `controllers/safra_controller.py`, `controllers/centro_custo_controller.py`,
  `controllers/lancamento_controller.py`,
  `controllers/financeiro_controller.py`, `app.py`,
  `migrations/versions/*`, `insomnia_safraviva.json`
- Dependências: reutiliza `pydantic` e `flask-migrate` já presentes; sem novas
  dependências.
- Sem breaking changes: entidades e endpoints existentes permanecem inalterados.
