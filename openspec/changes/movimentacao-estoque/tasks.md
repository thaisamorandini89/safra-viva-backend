# Tasks

## 1. Modelos e banco

- [x] 1.1 Criar `models/responsavel.py` com `Responsavel` (`id_responsavel` PK,
      `nome` String(150) not null, `cargo` String(100) opcional,
      `status` Boolean default True).
- [x] 1.2 Criar `models/movimentacao_estoque.py` com `MovimentacaoEstoque`
      (`id_movimentacao` String(36) PK com default `str(uuid.uuid4())`,
      `id_insumo` FK not null, `tipo_movimentacao` String(10) not null,
      `quantidade` Numeric(10,2) not null, `data_movimentacao` DateTime
      server_default now, `id_responsavel` FK opcional,
      `observacao` String(500) opcional).
- [x] 1.3 Registrar os dois modelos em `models/__init__.py`.
- [x] 1.4 Gerar a migration Alembic (tabela `responsavel` antes de
      `movimentacao_estoque`), revisar e aplicar com `flask db upgrade`.

## 2. Schemas Pydantic

- [x] 2.1 Criar `schemas/movimentacao_schema.py` com `MovimentacaoCreate`:
      `id_insumo: int`, `tipo_movimentacao: Literal['ENTRADA','SAIDA']`
      (normalizando caixa), `quantidade: Decimal` com `gt=0`,
      `id_responsavel: int | None`, `observacao: str | None` (máx. 500).
- [x] 2.2 Criar schema de resposta `MovimentacaoOut` (incluindo
      `estoque_atual` resultante do insumo).

## 3. Serviços

- [x] 3.1 Criar `services/responsavel_service.py` com `listar_todos` e
      `criar_responsavel` (nome obrigatório, trim).
- [x] 3.2 Criar `services/movimentacao_service.py` com `registrar(dados)`:
      carregar o insumo com `with_for_update()`, validar existência do insumo
      e do responsável (quando informado).
- [x] 3.3 Implementar a regra de saldo: ENTRADA soma em `estoque_atual`;
      SAIDA valida `estoque_atual >= quantidade` (senão `ValueError`) e subtrai.
- [x] 3.4 Persistir movimentação + saldo no mesmo commit, com rollback e
      `RuntimeError` em falha.
- [x] 3.5 Implementar `listar(id_insumo=None)` ordenado por
      `data_movimentacao` desc, com dados do insumo/produto e do responsável.

## 4. API

- [x] 4.1 Criar `controllers/responsavel_controller.py` com
      `GET`/`POST /responsaveis` (201/400/500).
- [x] 4.2 Criar `controllers/movimentacao_controller.py` com
      `POST /movimentacoes`: validar payload com `MovimentacaoCreate`
      (ValidationError → 400), registrar e retornar 201 com a movimentação e o
      novo `estoque_atual`; saldo insuficiente → 400; insumo/responsável
      inexistente → 400.
- [x] 4.3 Implementar `GET /movimentacoes` com query param opcional
      `id_insumo` (200).
- [x] 4.4 Registrar `responsavel_bp` e `movimentacao_bp` em `app.py`
      com `url_prefix='/api'`.

## 5. Validação

- [x] 5.1 Testar ENTRADA e conferir o incremento de `estoque_atual` no insumo.
- [x] 5.2 Testar SAIDA com saldo suficiente (decremento) e insuficiente (400,
      saldo inalterado, movimentação não registrada).
- [x] 5.3 Testar payloads inválidos (tipo desconhecido, quantidade <= 0,
      insumo/responsável inexistentes) → 400.
- [x] 5.4 Testar `GET /movimentacoes` com e sem filtro `id_insumo`.
- [x] 5.5 Adicionar as requisições de Responsável e Movimentação ao
      `insomnia_safraviva.json` e remover dados de teste.
