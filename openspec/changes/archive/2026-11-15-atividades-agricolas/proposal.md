# Módulo de Atividades Agrícolas (operações de campo)

## Why

O frontend já entrega a tela de **Atividades** (Dashboard, Listagem e Cadastro)
com um modelo rico de operação de campo: **categoria**, **tipo de atividade**,
talhão, safra, responsável, status (Planejada / Em Andamento / Concluída),
período, custo da operação, lista de **insumos utilizados** e de **máquinas e
implementos**, além de observações. Hoje essa tela funciona apenas com dados de
demonstração (`atividadesMock.ts`).

As telas deixam claro que **Categoria** e **Tipo de Atividade** são catálogos de
cadastro (dropdowns com valores pré-definidos), enquanto o formulário "Cadastro
de Atividade" registra a **operação de campo** executada em um talhão. Portanto
são três entidades distintas.

No backend hoje existe apenas a entidade `Atividade` **simples** (`descricao`,
`data_atividade`, `status` booleano), criada como lookup para o seletor
"Atividade Relacionada" da saída de estoque. Essa entidade corresponde,
conceitualmente, ao **Tipo de Atividade** (Pulverização, Adubação, Calagem…) —
exatamente o que a saída de estoque referencia. Ela será formalizada como
`tipo_atividade` e ganhará o vínculo com a categoria.

## What Changes

Modelagem em **5 entidades** (decisão: **Opção A** de nomenclatura de endpoints;
insumo da atividade com **FK para `Insumo`** e **catálogo de Máquina**):

### 1. `categoria_atividade` (nova — catálogo)
- `id_categoria_atividade` (PK), `nome` (String(80), obrigatório, único),
  `status` (Boolean, default True).
- Valores: Preparo de Solo, Plantio, Tratos Culturais, Irrigação, Colheita.
- Endpoints: `GET/POST /api/categorias-atividade`,
  `PUT/DELETE /api/categorias-atividade/<id>`.

### 2. `tipo_atividade` (renomeia a atual `atividade` — catálogo)
- Renomeia a tabela `atividade` → `tipo_atividade`, preservando a PK inteira
  `id_atividade` para **não quebrar** a FK `movimentacao_estoque.id_atividade`.
- `descricao` (String(100)) continua sendo o nome do tipo (Aração, Gradagem,
  Adubação, Pulverização, Calagem…).
- Adiciona `id_categoria_atividade` (FK → `categoria_atividade`, obrigatório).
- Mantém `status`; remove `data_atividade` (não faz sentido num catálogo).
- Endpoints: `GET/POST /api/tipos-atividade`,
  `PUT/DELETE /api/tipos-atividade/<id>`, com filtro opcional
  `?id_categoria_atividade=` para popular o dropdown dependente da categoria.
- A FK `movimentacao_estoque.id_atividade` passa a apontar para `tipo_atividade`
  (mesma coluna/valor, só muda o nome da tabela referenciada).

### 3. `maquina` (nova — catálogo de Máquinas e Implementos)
- `id_maquina` (PK), `nome` (String(150), obrigatório, único), `tipo`
  (String(50), opcional — ex.: Trator, Colheitadeira, Implemento),
  `observacoes` (String(500), opcional), `status` (Boolean, default True).
- Alimenta o dropdown "Máquina / Implemento" do formulário de atividade.
- Endpoints: `GET/POST /api/maquinas`, `GET/PUT/DELETE /api/maquinas/<id>`.

### 4. `atividade_agricola` (nova — a operação de campo)
- Tabela nova com `id_atividade_agricola` (PK inteira) e os campos do formulário:
  `id_categoria_atividade` (FK), `id_tipo_atividade` (FK → `tipo_atividade`),
  `id_talhao` (FK, obrigatório), `id_propriedade` (FK, opcional),
  `id_empresa` (opcional), `safra` (String(20), opcional),
  `id_funcionario` (FK String(36) → `funcionario`, responsável),
  `status` (**enumerado**, default `Planejada`), `data_inicio` (Date,
  obrigatório), `data_fim` (Date, opcional), `custo_operacao` (Numeric(14,2),
  opcional), `observacoes` (String(1000), opcional), `data_cadastro` (DateTime).
- **`status` é um campo enumerado** que SÓ aceita `Planejada`, `Em Andamento` ou
  `Concluída`. Qualquer outro valor é rejeitado com HTTP 400. A persistência usa
  um Enum (SQLAlchemy `Enum` + Pydantic `Literal`), garantindo a restrição no
  banco e na validação.
- **Tabelas filhas 1:N (cascata)**:
  - `atividade_insumo`: **`id_insumo`** (FK → `insumo.id_insumo`, obrigatório),
    `nome` e `unidade` (snapshot do insumo, para histórico), `quantidade`
    (Numeric(14,3)), `custo` (Numeric(14,2)). O insumo referenciado SHALL existir;
    isso prepara a baixa de estoque e os relatórios de consumo.
  - `atividade_maquina`: **`id_maquina`** (FK → `maquina.id_maquina`, obrigatório),
    `nome` (snapshot), `horas` (Numeric(10,2)), `custo` (Numeric(14,2)).
- Endpoints (prefixo `/api`): `GET /atividades` (listagem com filtros),
  `GET /atividades/indicadores`, `GET /atividades/<id>`, `POST /atividades`,
  `PUT /atividades/<id>`, `DELETE /atividades/<id>`.
- **`GET /atividades/status-opcoes`**: retorna a lista dos valores de status
  permitidos (`Planejada`, `Em Andamento`, `Concluída`) para alimentar o combo
  do frontend, de modo que o usuário já receba as opções prontas para escolher.

### Responsável = Funcionário
O responsável da operação é o `funcionario` já existente
(`funcionario.id_funcionario`, String(36) UUID), como na movimentação de estoque.

### Integração com o frontend
`api.ts` e os componentes de Atividades passam a consumir os endpoints reais;
os selects de Categoria, Tipo, Talhão, Responsável, **Insumo** (vindo do cadastro
de insumos) e **Máquina/Implemento** (vindo do novo catálogo) são populados pelo
backend; o mock vira apenas fallback.

## Impact

- **Affected specs**: `categoria-atividade` (nova), `tipo-atividade` (nova),
  `maquina` (nova), `atividade-agricola` (nova).
- **Affected code (backend)**:
  - Novos: `models/categoria_atividade.py`, `models/maquina.py`,
    `models/atividade_agricola.py`, `models/atividade_insumo.py`,
    `models/atividade_maquina.py`,
    `controllers/categoria_atividade_controller.py`,
    `controllers/maquina_controller.py`,
    `services/categoria_atividade_service.py`, `services/maquina_service.py`,
    `schemas/atividade_schema.py`.
  - Renomeados: `models/atividade.py` → `models/tipo_atividade.py`
    (classe `TipoAtividade`, tabela `tipo_atividade`);
    `services/atividade_service.py` / `controllers/atividade_controller.py`
    divididos entre "tipo" (catálogo) e "atividade agrícola" (operação).
  - Alterados: `models/__init__.py`, `app.py`, `models/movimentacao_estoque.py`
    (FK repontada para `tipo_atividade`), migration Alembic.
- **Affected code (frontend)**: `src/services/api.ts`,
  `src/types/atividade.ts`, `src/components/atividades/*`.
- **Dados**: a tabela `atividade` está vazia em homologação (a tela usa mock),
  então o rename e as novas tabelas não migram dados; um seed opcional popula
  categorias, tipos e máquinas padrão.
- **Out of scope**: baixa automática de estoque ao concluir a atividade (fica no
  módulo de movimentação); `LoteInsumo`, alertas de validade e relatórios de
  consumo (irão para a change `insumo-lotes-e-relatorios`).
