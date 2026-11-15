# Design

## Context

Projeto Flask + SQLAlchemy + Alembic com camadas controller → service → model e
validação de borda em Pydantic v2 (`pydantic==2.7.1` já no `requirements.txt`),
seguindo o padrão já estabelecido pela change `movimentacao-estoque`. Ver
proposal.md — Why para a motivação. O banco atual não possui as entidades
`Safra`, `CentroCusto` nem qualquer estrutura financeira; as entidades de
negócio existentes usam PK inteira, exceto `movimentacao_estoque` e `funcionario`
que usam UUID em `String(36)`.

## Goals / Non-Goals

**Goals:**
- Fornecer CRUD de lançamentos financeiros, centro de custo e safra, seguindo o
  padrão de camadas existente.
- Garantir as regras de negócio RN001–RN005 na camada de serviço.
- Entregar endpoints de agregação (saldo, fluxo de caixa, indicadores) em JSON.
- Não quebrar entidades/endpoints existentes.

**Non-Goals:**
- Telas, gráficos e dashboards (frontend).
- Exportação de arquivos Excel/PDF no backend.
- Cadastro completo/rico de safra e cultura (entidade `Cultura` própria); safra
  recebe cadastro mínimo e cultura fica como campo texto auxiliar.
- Conciliação bancária automática e anexos de arquivos.
- Autenticação/autorização (não existe no projeto hoje).

## Decisions

### PK UUID string para lançamento, inteira para safra e centro de custo

`LancamentoFinanceiro.id_lancamento` será `db.String(36)` com
`default=lambda: str(uuid.uuid4())`, acompanhando o padrão de
`movimentacao_estoque` para a entidade transacional de maior volume e que o
requisito pede como UUID. `Safra` e `CentroCusto`, por serem cadastros de
dimensão, mantêm PK inteira como as demais entidades de cadastro, reduzindo
atrito. Alternativa descartada: UUID em tudo (inconsistente com o restante dos
cadastros).

### Enums como String validados por Pydantic

`tipo`, `forma_pagamento`, `status` (lançamento) e `tipo` (centro de custo) serão
`db.String` validados na borda com `Literal` do Pydantic, sem `ENUM` nativo do
PostgreSQL — mesmo critério da change `movimentacao-estoque`, evitando migrations
de alteração de enum no futuro.

### FKs de vínculo opcionais

`id_empresa`, `id_propriedade`, `id_talhao`, `id_safra` e `id_centro_custo` são
FKs anuláveis no lançamento; o requisito trata os vínculos como opcionais
(RN004 é "sempre que aplicável"). A existência de cada vínculo informado é
validada no service antes do commit, retornando HTTP 400 quando inválido.

### Rateio em tabela própria, validado na mesma transação

O rateio (RN005) fica em `rateio_lancamento` (1:N a partir do lançamento). A soma
dos percentuais deve ser 100%, validada no service; lançamento e parcelas são
persistidos no mesmo `commit`, com rollback em falha — mesmo padrão
transacional de `movimentacao-estoque`. Alternativa descartada: guardar rateio
como JSON no próprio lançamento (dificulta agregação por talhão).

### Integridade histórica via flag `conciliado`

RN003 é aplicado no service de exclusão: `DELETE` é bloqueado (HTTP 400) quando
`conciliado` é verdadeiro. Não há exclusão lógica adicional nesta change; o campo
`status` ('PENDENTE'/'PAGO') é independente da conciliação.

### Agregações via SQLAlchemy, sem camada de BI

Saldo, fluxo de caixa e indicadores são calculados com consultas de agregação
(`func.sum`, `group_by`) no `financeiro_service`, retornando JSON. Custo/receita
por hectare dividem os valores agregados pela área da safra ou do talhão,
tratando área nula/zero como indicador nulo (sem divisão por zero). Alternativa
descartada: views materializadas (complexidade desnecessária para o volume
atual).

### Pydantic na borda, service como fonte da verdade

Schemas Pydantic validam formato/tipos no controller (`model_validate` → 400 com
erros do `ValidationError`); regras que dependem do banco (existência de
vínculos, soma de rateio, bloqueio de exclusão) permanecem no service. `valor` e
`percentual` tipados como `Decimal` com `gt=0`.

## Risks / Trade-offs

- **Vínculos opcionais permitem lançamento sem rastreabilidade** → aceitável por
  RN004 ("quando aplicável"); indicadores por safra/talhão/cultura só consideram
  lançamentos com o vínculo correspondente preenchido.
- **Custo por hectare depende de área cadastrada** → quando a área da
  safra/talhão é nula, o indicador por hectare retorna nulo em vez de erro.
- **Edição de lançamento conciliado** → esta change bloqueia apenas a exclusão
  (RN003); a edição de conciliados não é restringida e fica registrada como
  possível endurecimento futuro.
- **`cultura` como texto livre** → agregação por cultura depende de consistência
  textual; mitigação: normalizar (trim) na entrada. Entidade `Cultura` dedicada
  fica para change futura.

## Migration Plan

1. Criar os modelos e registrar em `models/__init__.py`.
2. Gerar a migration Alembic criando as tabelas na ordem de dependência:
   `safra` e `centro_custo` antes de `lancamento_financeiro`, e
   `rateio_lancamento` por último (FK para lançamento e talhão).
3. Aplicar com `flask db upgrade`.
4. Rollback: `flask db downgrade` remove as tabelas na ordem inversa; não há
   alteração em tabelas existentes, então o rollback é isolado.
