# Tasks

## 1. Catálogo: Categoria de Atividade

- [x] 1.1 Criar `models/categoria_atividade.py` (`id_categoria_atividade` PK,
      `nome` String(80) not null unique, `status` Boolean default True).
- [x] 1.2 Criar `services/categoria_atividade_service.py` (listar, criar,
      atualizar, excluir; nome obrigatório e único).
- [x] 1.3 Criar `controllers/categoria_atividade_controller.py`
      (`GET/POST /categorias-atividade`, `PUT/DELETE /categorias-atividade/<id>`).

## 2. Catálogo: Tipo de Atividade (rename de `atividade`)

- [x] 2.1 Renomear `models/atividade.py` → `models/tipo_atividade.py`,
      classe `TipoAtividade`, tabela `tipo_atividade`; manter `id_atividade` PK e
      `descricao`; adicionar `id_categoria_atividade` FK (obrigatório); remover
      `data_atividade`; manter `status`.
- [x] 2.2 Adaptar `services/atividade_service.py` → `tipo_atividade_service.py`
      (listar com filtro `id_categoria_atividade`, criar, atualizar, excluir).
- [x] 2.3 Adaptar `controllers/atividade_controller.py` →
      `tipo_atividade_controller.py` (`GET/POST /tipos-atividade`,
      `PUT/DELETE /tipos-atividade/<id>`).
- [x] 2.4 Em `models/movimentacao_estoque.py`, repontar a FK `id_atividade` para
      `tipo_atividade.id_atividade` (sem mudar nome/valor da coluna).

## 2b. Catálogo: Máquina e Implemento

- [x] 2b.1 Criar `models/maquina.py` (`id_maquina` PK, `nome` String(150) not
      null unique, `tipo` String(50) opcional, `observacoes` String(500)
      opcional, `status` Boolean default True).
- [x] 2b.2 Criar `services/maquina_service.py` (listar, obter, criar, atualizar,
      excluir; nome obrigatório e único).
- [x] 2b.3 Criar `controllers/maquina_controller.py` (`GET/POST /maquinas`,
      `GET/PUT/DELETE /maquinas/<id>`).

## 3. Operação de campo: Atividade Agrícola

- [x] 3.1 Criar `models/atividade_agricola.py` (`id_atividade_agricola` PK,
      `id_categoria_atividade` FK, `id_tipo_atividade` FK, `id_talhao` FK not
      null, `id_propriedade` FK, `id_empresa`, `safra`, `id_funcionario` FK
      String(36), `status` como `Enum('Planejada','Em Andamento','Concluída',
      name='status_atividade')` default `Planejada`, `data_inicio` Date
      not null, `data_fim` Date, `custo_operacao` Numeric(14,2), `observacoes`
      String(1000), `data_cadastro` DateTime; relacionamentos `insumos`/
      `maquinas` com cascade all, delete-orphan).
- [x] 3.2 Criar `models/atividade_insumo.py` (`id` PK, `id_atividade_agricola`
      FK ondelete CASCADE, `id_insumo` FK → `insumo` not null, `nome`
      String(200) snapshot, `unidade` String(20) snapshot, `quantidade`
      Numeric(14,3), `custo` Numeric(14,2)) e `models/atividade_maquina.py`
      (`id` PK, `id_atividade_agricola` FK ondelete CASCADE, `id_maquina` FK →
      `maquina` not null, `nome` String(200) snapshot, `horas` Numeric(10,2),
      `custo` Numeric(14,2)).
- [x] 3.3 Registrar todos os modelos em `models/__init__.py` na ordem correta
      (categoria → tipo → maquina → atividade_agricola → filhas).

## 4. Schemas Pydantic

- [x] 4.1 Criar `schemas/atividade_schema.py` com `STATUS_ATIVIDADE`
      (`("Planejada","Em Andamento","Concluída")`), `AtividadeItemInsumo`
      (`id_insumo` int obrigatório, `quantidade`/`custo` ≥ 0 opcionais),
      `AtividadeItemMaquina` (`id_maquina` int obrigatório, `horas`/`custo` ≥ 0
      opcionais), `AtividadeCreate`, `AtividadeUpdate`, usando
      `Literal[*STATUS_ATIVIDADE]` para o campo `status`.
- [x] 4.2 Validar `data_fim >= data_inicio`; normalizar `status` e
      `id_funcionario`/`id_responsavel`.

## 5. Serviço e controller da operação

- [x] 5.1 Criar `services/atividade_agricola_service.py`:
      `serializar(atv)` (rico + derivados), `listar(filtros)`, `obter(id)`,
      `criar(dados)`, `atualizar(id, dados)`, `excluir(id)`,
      `indicadores(filtros)`; validar categoria/tipo/talhão/funcionário e
      **cada `id_insumo` e `id_maquina`**; preencher o **snapshot** de
      `nome`/`unidade` (insumo) e `nome` (máquina); derivar `id_propriedade` do
      talhão.
- [x] 5.2 Criar `controllers/atividade_agricola_controller.py`:
      `GET /atividades`, `GET /atividades/indicadores`,
      `GET /atividades/status-opcoes` (lista dos status permitidos),
      `GET /atividades/<id>`, `POST /atividades`, `PUT /atividades/<id>`,
      `DELETE /atividades/<id>`.
- [x] 5.3 Atualizar `app.py` (blueprints: categoria, tipo, máquina, atividade
      agrícola).

## 6. Migration e seed

- [x] 6.1 Gerar a migration no container: criar `categoria_atividade` e
      `maquina`; renomear `atividade`→`tipo_atividade` + add FK categoria + drop
      `data_atividade`; recriar FK da movimentação; criar `atividade_agricola`,
      `atividade_insumo` (com FK `id_insumo`), `atividade_maquina` (com FK
      `id_maquina`). Revisar a ordem e aplicar com `flask db upgrade`.
- [x] 6.2 Seed opcional: categorias padrão (Preparo de Solo, Plantio, Tratos
      Culturais, Irrigação, Colheita), tipos padrão por categoria e máquinas
      padrão (Trator John Deere 6110J, Massey Ferguson 7180, Colheitadeira New
      Holland CR, Pulverizador Jacto, Grade Aradora, Subsolador, Plantadeira
      Semeato, Distribuidor de Calcário, Pivô Central Valley).

## 7. Testes de API

- [x] 7.1 CRUD de `/categorias-atividade`, `/tipos-atividade` (com filtro por
      categoria) e `/maquinas` → 200/201/400.
- [x] 7.2 `POST /atividades` completo (insumos com `id_insumo` + máquinas com
      `id_maquina`) → 201 e objeto rico com snapshots.
- [x] 7.3 `GET /atividades` com e sem filtros; `GET /atividades/indicadores`.
- [x] 7.4 `PUT` substituindo listas; `DELETE` com cascata.
- [x] 7.5 Erros: categoria/tipo/talhão/funcionário/**insumo**/**máquina**
      inexistentes, `data_fim < data_inicio`, status inválido → 400; id
      inexistente → 404.
- [x] 7.6 Regressão: criar saída de estoque referenciando um `id_atividade`
      (tipo) após o rename.

## 8. Integração com o frontend

- [x] 8.1 Ajustar `src/types/atividade.ts` (`id_responsavel` string; itens de
      insumo com `id_insumo` e máquina com `id_maquina`; incluir `categoria`,
      `custo_total`, `atrasada` quando vierem do backend).
- [x] 8.2 Em `src/services/api.ts`: funções para categorias, tipos (com filtro),
      máquinas, atividades (listar/obter/criar/atualizar/excluir/indicadores),
      carregando funcionários, talhões e insumos reais.
- [x] 8.3 Ajustar `components/atividades/*`: popular selects de Categoria, Tipo
      (dependente da categoria), Talhão, Responsável, **Insumo** (do cadastro de
      insumos) e **Máquina/Implemento** (do catálogo) com dados reais; o combo de
      **Status** é populado via `GET /api/atividades/status-opcoes`; manter o
      mock só como fallback.
- [x] 8.4 Teste manual no navegador: criar, listar, editar e excluir atividade.
