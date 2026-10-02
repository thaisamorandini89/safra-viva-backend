# Design

## Context

O projeto é Flask + SQLAlchemy + Alembic, com camadas controller → service →
model e validação manual nos services. `pydantic==2.7.1` já está no
`requirements.txt`, mas ainda não é usado — esta change introduz o primeiro
schema Pydantic, conforme a especificação.

## Decisions

### PK da movimentação como UUID string

`id_movimentacao` será `db.String(36)` com `default=lambda: str(uuid.uuid4())`,
em vez do tipo nativo `UUID` do PostgreSQL. Mantém o código portável e simples
(sem `sqlalchemy.dialects.postgresql`), aceitando o custo de armazenamento
ligeiramente maior. As demais entidades continuam com PK inteira.

### Atualização de saldo na mesma transação

`MovimentacaoService.registrar` insere a movimentação e atualiza
`insumo.estoque_atual` no mesmo `db.session.commit()`. Falha em qualquer passo
faz rollback de ambos, evitando saldo divergente do histórico.

Validações antes do commit:
- insumo existe;
- `tipo_movimentacao` ∈ {ENTRADA, SAIDA} (case-insensitive, normalizado para
  maiúsculas);
- `quantidade` > 0;
- para SAIDA: `estoque_atual >= quantidade`, senão `ValueError`
  ("Saldo insuficiente...") → HTTP 400;
- `id_responsavel`, quando informado, deve existir.

### Pydantic na borda, service como fonte da verdade

O schema `MovimentacaoCreate` (Pydantic v2) valida formato/tipos no controller
(`model_validate` → 400 com os erros do `ValidationError`). As regras que
dependem do banco (existência de insumo/responsável, saldo) permanecem no
service. Precisão monetária: `quantidade` tipada como `Decimal`, `gt=0`.

### Enum como String + CHECK na aplicação

`tipo_movimentacao` será `db.String(10)` validado na aplicação (Pydantic
`Literal['ENTRADA','SAIDA']`), sem `ENUM` nativo do PostgreSQL — evita o atrito
de migrations para alterar enums no futuro.

### Responsável mínimo

Apenas `GET`/`POST /api/responsaveis`, o suficiente para criar e vincular.
CRUD completo fica para uma change futura.

## Risks

- **Concorrência**: duas saídas simultâneas podem passar na validação de saldo.
  Mitigação nesta change: `with_for_update()` ao carregar o insumo no registro
  da movimentação.
- **Dupla via de atualização de saldo**: o `PUT /api/insumos` ainda permite
  editar `estoque_atual` diretamente, podendo divergir do histórico. Registrado
  como out of scope; recomenda-se change futura para bloquear.
