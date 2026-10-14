# Design

## Context

Ver proposal.md — Why. O backend é Flask + SQLAlchemy com organização em
`models/`, `controllers/` (Blueprints sob `url_prefix='/api'`), `services/`
(classes com métodos estáticos: `listar_todas`, `buscar_por_id`, `criar_*`,
`atualizar_*`, `excluir_*`) e `schemas/` (Pydantic). As entidades de domínio
usam nomes em português, `status` booleano e `data_cadastro` com
`server_default=db.func.now()`. Já existe a entidade `Propriedade`
(`id_propriedade` PK inteiro) que será referenciada pelo vínculo, e a entidade
mínima `Responsavel`, que não será alterada.

## Goals / Non-Goals

**Goals:**
- Seguir os padrões já estabelecidos (model/controller/service/schema) para
  manter consistência com `propriedade`, `insumo` e `movimentacao-estoque`.
- Garantir CPF único e soft delete (inativação via `status`).
- Suportar vínculo N:N implícito entre funcionário e propriedade via tabela
  associativa com data de vinculação.

**Non-Goals:**
- Anexos de documentos, auditoria de alterações, apontamento de horas e folha
  de pagamento (ver Out of Scope da proposta).

## Decisions

- **PK em UUID string (String(36)) para `funcionario` e
  `funcionario_propriedade`**: o DER do módulo especifica ID UUID, e a change
  `movimentacao-estoque` já adotou `String(36)` com `default=str(uuid.uuid4())`
  para `MovimentacaoEstoque`. Mantém o padrão recém-introduzido no projeto.
  *Alternativa*: inteiro autoincremento (como `propriedade`) — descartada por
  divergir do DER solicitado.
- **CPF como `String(11)` com `unique=True`**: armazenar apenas dígitos,
  normalizando no schema Pydantic (remover pontos/traços). A unicidade é
  garantida no banco e validada no serviço para retornar HTTP 400 amigável
  antes do IntegrityError.
- **Inativação como soft delete**: `DELETE` altera `status` para `False` em vez
  de remover o registro, preservando rastreabilidade (coerente com `status`
  usado nas demais entidades).
- **Vínculo em tabela associativa própria (`funcionario_propriedade`)** com
  `data_vinculacao`, em vez de relação direta, porque o DER pede o atributo de
  data e porque um funcionário pode ter múltiplos vínculos.
- **Filtros via query params** em `GET /api/funcionarios` (`nome`, `cpf`,
  `cargo`, `id_propriedade`, `status`), montados dinamicamente no serviço —
  mesmo padrão de filtro opcional usado em `GET /api/movimentacoes?id_insumo=`.
- **Indicadores em endpoint dedicado** `GET /api/funcionarios/indicadores`
  para alimentar os cards do dashboard sem sobrecarregar a listagem.

## Risks / Trade-offs

- Validação de CPF apenas estrutural (11 dígitos), sem checagem de dígitos
  verificadores → mitigação: validação de dígitos pode ser adicionada depois no
  schema sem alterar o contrato da API.
- Filtro por `id_propriedade` exige join com `funcionario_propriedade` → pode
  retornar funcionários duplicados; mitigação: usar `distinct` na consulta.
- UUID como PK aumenta ligeiramente o tamanho do índice frente a inteiro →
  impacto desprezível na escala esperada e justificado pela consistência com o
  DER e com a change anterior.

## Migration Plan

- Gerar migration Alembic criando `funcionario` antes de
  `funcionario_propriedade` (ordem de FK). Aplicar com `flask db upgrade`.
- Rollback: `flask db downgrade` remove as duas tabelas; nenhuma tabela
  existente é alterada, então não há impacto em dados legados.
