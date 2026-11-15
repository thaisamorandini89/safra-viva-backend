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

## 6. Detalhes de Entrada e Saída (atualização da proposta)

- [x] 6.0 Pré-requisito: garantir que a migration da tabela `funcionario`
      está gerada e aplicada no banco (o modelo existe, mas a tabela não).
- [x] 6.1 Adicionar ao modelo `MovimentacaoEstoque` os campos comuns/entrada
      (todos nullable): `valor_unitario` Numeric(14,2), `id_fornecedor` FK →
      `fornecedor.id_fornecedor`, `numero_nota_fiscal` String(50),
      `numero_lote` String(50), `data_fabricacao` Date, `data_validade` Date.
- [x] 6.2 Adicionar os campos de saída (todos nullable): `id_talhao` FK →
      `talhao.id_talhao`, `safra` String(20), `id_atividade` FK →
      `atividade.id_atividade`, `destino_finalidade` String(255).
- [x] 6.3 Criar `models/atividade.py` (`id_atividade` PK, `descricao`
      String(100) not null, `data_atividade` Date opcional, `status` Boolean
      default True) e registrar em `models/__init__.py`.
- [x] 6.4 Substituir `id_responsavel` por `id_funcionario` (FK →
      `funcionario.id_funcionario`, nullable) no modelo da movimentação.
- [x] 6.5 Remover a entidade `Responsavel`: modelo, import em
      `models/__init__.py`, `services/responsavel_service.py`,
      `controllers/responsavel_controller.py` e blueprint em `app.py`.
- [x] 6.6 Gerar e aplicar a migration: criar `atividade`, alterar
      `movimentacao_estoque` (novas colunas; `id_responsavel` →
      `id_funcionario`) e dropar `responsavel`.
- [x] 6.7 Criar `services/atividade_service.py` e
      `controllers/atividade_controller.py` com `GET`/`POST /api/atividades`;
      registrar o blueprint em `app.py`.
- [x] 6.8 Atualizar `MovimentacaoCreate` com os novos campos opcionais
      (`id_funcionario`, `id_atividade`, etc.) e validação cruzada: campos de
      entrada rejeitados em SAIDA e campos de saída rejeitados em ENTRADA;
      `data_validade >= data_fabricacao`.
- [x] 6.9 No serviço, validar existência de `id_funcionario`, `id_fornecedor`,
      `id_talhao` e `id_atividade` quando informados e persistir os campos.
- [x] 6.10 Incluir os novos campos no retorno do `POST` e na listagem
      (`funcionario_nome`, `fornecedor_nome`, `nome_talhao` e
      `atividade_descricao` resolvidos por FK).
- [x] 6.11 Atualizar o `insomnia_safraviva.json`: remover a pasta de
      Responsáveis, adicionar Atividades e refazer os exemplos de
      Entrada/Saída.
- [x] 6.12 Testar: entrada completa (NF, lote, datas), saída completa (talhão,
      safra, atividade, destino), campo de entrada em SAIDA → 400, campo de
      saída em ENTRADA → 400, `data_validade` anterior à fabricação → 400,
      funcionário/fornecedor/talhão/atividade inexistentes → 400.
