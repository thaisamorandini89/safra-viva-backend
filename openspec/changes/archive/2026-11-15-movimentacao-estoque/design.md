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

### Responsável = Funcionário (substituição da entidade provisória)

A entidade `Responsavel` foi criada quando não havia cadastro de pessoas; com
o módulo de Funcionários entregue, manter as duas geraria cadastro duplicado.
Decisão: a movimentação referencia `funcionario.id_funcionario` e a entidade
`Responsavel` é removida por completo (modelo, tabela, serviço, controller e
rotas). Como a tabela `responsavel` está vazia em produção e o endpoint foi
lançado há poucos dias, a remoção direta é aceitável; não haverá migração de
dados nem período de depreciação.

### Atividade como entidade própria

A tela de Saída apresenta "Atividade Relacionada" como um seletor de registros
com descrição e data (Pulverização — 08/01/2025, Calagem — 02/07/2024, ...).
Texto livre não suportaria isso. Decisão: criar a entidade `Atividade`
(`id_atividade`, `descricao`, `data_atividade`, `status`) com `GET`/`POST`
mínimos, e a movimentação de SAIDA referencia `id_atividade` (FK opcional).
O campo `atividade_relacionada` (String) previsto na versão anterior desta
proposta não será criado.

### Campos condicionais em colunas nullable (tabela única)

Os detalhes de entrada (fornecedor, NF, lote, datas) e de saída (talhão, safra,
atividade, destino) ficam como colunas `nullable=True` na própria
`movimentacao_estoque`, em vez de tabelas separadas por tipo. A exclusividade
por tipo é garantida pelo schema Pydantic (`model_validator`): campos de
entrada presentes em SAIDA (ou vice-versa) → 400. Alternativa descartada:
herança/joined tables — complexidade desnecessária para dois tipos estáveis.

`id_responsavel` dá lugar a `id_funcionario`, que permanece `nullable=True`
no banco (a obrigatoriedade é regra da interface); `valor_unitario` entra como
Numeric(14,2) opcional, permitindo registrar o custo da operação sem acoplar à
precificação do insumo.

## Risks

- **Concorrência**: duas saídas simultâneas podem passar na validação de saldo.
  Mitigação nesta change: `with_for_update()` ao carregar o insumo no registro
  da movimentação.
- **Dupla via de atualização de saldo**: o `PUT /api/insumos` ainda permite
  editar `estoque_atual` diretamente, podendo divergir do histórico. Registrado
  como out of scope; recomenda-se change futura para bloquear.
