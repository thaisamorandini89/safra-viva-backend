# Design — Atividades Agrícolas (Opção A)

## Contexto e restrições

- A entidade `Atividade` (tabela `atividade`, PK inteira `id_atividade`) é hoje
  referenciada por `movimentacao_estoque.id_atividade`. Conceitualmente ela é o
  **Tipo de Atividade** (Pulverização, Adubação…) — o que a saída de estoque
  seleciona. Será formalizada como `tipo_atividade`.
- O frontend (`src/types/atividade.ts`) já define o contrato rico da operação de
  campo (`AtividadeAgricola` com `insumos[]`, `maquinas[]`, status textual e
  derivados) e consome `/api/atividades`.
- `migrations/` é root-owned e está no `.gitignore`: a migration é gerada e
  aplicada dentro do container (`docker exec flask_backend`).
- Padrão: controller → service → model, com Pydantic na borda nos módulos novos.

## Decisão 0 — Nomenclatura (Opção A, escolhida pela usuária)

| Entidade | Tabela | Endpoint |
|---|---|---|
| Categoria | `categoria_atividade` | `/api/categorias-atividade` |
| Tipo | `tipo_atividade` (rename de `atividade`) | `/api/tipos-atividade` |
| Operação de campo | `atividade_agricola` | `/api/atividades` |

## Decisão 1 — Renomear `atividade` → `tipo_atividade`

Rename da tabela preservando a PK inteira e os dados (vazia em homolog). A FK
`movimentacao_estoque.id_atividade` é recriada apontando para `tipo_atividade`
(coluna e valores inalterados; mantemos o nome `id_atividade` para não mexer na
change de movimentação). Adiciona-se `id_categoria_atividade` (FK, obrigatório) e
remove-se `data_atividade`. A classe passa a ser `TipoAtividade`.

Alternativa rejeitada: manter `atividade` como operação rica e criar
`tipo_atividade` do zero — exigiria migrar a FK da movimentação para a tabela
nova e duplicaria semântica. O rename é mais limpo.

## Decisão 2 — Operação de campo em tabela nova `atividade_agricola`

PK própria `id_atividade_agricola` para não colidir com `tipo_atividade`.
Referencia categoria e tipo por FK (a categoria é redundante com a do tipo, mas
o frontend trata categoria e tipo como seleções independentes e a categoria
pode existir sem tipo selecionado; manter ambas simplifica os filtros).

## Decisão 3 — Insumos e máquinas como tabelas filhas com FK

`atividade_insumo` e `atividade_maquina` são 1:N com `ondelete='CASCADE'` e
`cascade="all, delete-orphan"`. No `PUT`, as coleções são **substituídas**
(apaga e recria), estratégia simples e previsível para listas pequenas.

- **Insumo da atividade referencia o `Insumo` cadastrado** (Opção 2 escolhida
  pela usuária): `atividade_insumo.id_insumo` é FK obrigatória para
  `insumo.id_insumo`. Guardamos também `nome` e `unidade` como **snapshot**
  (derivados de `produto.nome_produto`/`produto.unidade_medida` no momento do
  registro), preservando o histórico mesmo que o insumo mude ou seja excluído.
  Isso prepara a **baixa automática de estoque** e os **relatórios de consumo**
  por talhão/safra citados na documentação do módulo.
- **Máquina da atividade referencia o novo catálogo `maquina`**:
  `atividade_maquina.id_maquina` é FK obrigatória para `maquina.id_maquina`, com
  `nome` como snapshot.

## Decisão 3.1 — Catálogo de Máquinas e Implementos

Como a tela "Máquina / Implemento" passou a ser um **dropdown**, criamos a
entidade de catálogo `maquina` (`id_maquina` PK, `nome` único obrigatório,
`tipo` opcional, `observacoes` opcional, `status` default True) com CRUD em
`/api/maquinas`. Um seed popula as máquinas padrão (Trator John Deere 6110J,
Massey Ferguson 7180, Colheitadeira New Holland CR, Pulverizador Jacto, Grade
Aradora, Subsolador, Plantadeira Semeato, Distribuidor de Calcário, Pivô Central
Valley), que hoje estão hardcoded no mock do frontend.

## Decisão 4 — Responsável é Funcionário

`atividade_agricola.id_funcionario` → `funcionario.id_funcionario` (String(36)).
A serialização expõe `id_responsavel` (o UUID string) e `responsavel`
(`nome_completo`). Aceita `id_funcionario` ou `id_responsavel` como alias no
corpo. Funcionário inexistente → 400.

## Decisão 5 — Validação com Pydantic

`schemas/atividade_schema.py`:
- `AtividadeItemInsumo` (`id_insumo` int obrigatório; `quantidade`, `custo`
  opcionais ≥ 0; `nome`/`unidade` ignorados na entrada, preenchidos como
  snapshot pelo service) e `AtividadeItemMaquina` (`id_maquina` int obrigatório;
  `horas`, `custo` opcionais ≥ 0; `nome` snapshot pelo service).
- `AtividadeCreate`: `id_categoria_atividade` (int, obrigatório),
  `id_tipo_atividade` (int, obrigatório), `id_talhao` (int, obrigatório),
  `data_inicio` (date, obrigatório), `status`
  (`Literal['Planejada','Em Andamento','Concluída']`, default `Planejada`),
  `id_funcionario`/`id_responsavel` (str, opcional), `safra`, `data_fim`,
  `custo_operacao`, `observacoes`, `insumos: list`, `maquinas: list`,
  `id_empresa`, `id_propriedade`.
  - `model_validator`: `data_fim >= data_inicio` quando ambos presentes.
- `AtividadeUpdate`: todos opcionais (mesmas validações quando presentes).
- Catálogos validados nos services (nome obrigatório/único; categoria do tipo
  deve existir).

## Decisão 5.1 — Status como enumerado (fonte única de verdade)

O conjunto de status permitidos é definido **uma única vez** em
`schemas/atividade_schema.py` como uma constante
`STATUS_ATIVIDADE = ("Planejada", "Em Andamento", "Concluída")`, usada em três
lugares para evitar divergência:
1. **Banco**: coluna `status` como SQLAlchemy `Enum(*STATUS_ATIVIDADE,
   name='status_atividade')` com default `Planejada`.
2. **Validação**: `Literal['Planejada','Em Andamento','Concluída']` nos schemas
   Pydantic; valor fora da lista → HTTP 400 automaticamente.
3. **Frontend**: endpoint `GET /api/atividades/status-opcoes` devolve
   `["Planejada", "Em Andamento", "Concluída"]` para popular o combo, de modo que
   o usuário já receba as opções prontas sem hardcode no cliente.

Assim a regra "só estes três valores" é imposta no banco, na API e exibida na
tela a partir da mesma origem.

## Decisão 6 — Campos derivados calculados no backend

Na serialização da operação, o service inclui:
- `custo_total`: `custo_operacao` se informado, senão soma de insumos + máquinas.
- `duracao_dias`: `(data_fim - data_inicio) + 1`, mínimo 1.
- `atrasada`: `status != 'Concluída'` e `(data_fim ?? data_inicio) < hoje`.
- `insumos_count` / `maquinas_count` e nomes resolvidos de talhão/responsável/
  categoria/tipo.

`GET /atividades/indicadores` retorna `total`, `custo_total`, `em_andamento`,
`atrasadas`, `planejadas`, `concluidas`, respeitando os filtros da listagem.

## Fluxo de criação da operação

```
POST /api/atividades
  → controller valida JSON com AtividadeCreate
  → service.criar():
      valida categoria, tipo, talhão (existem) e funcionário (se informado)
      deriva id_propriedade do talhão quando ausente
      cria AtividadeAgricola + filhas numa transação
      commit
  → 201 com o objeto serializado (rico)
```

## Riscos

- **FK da movimentação**: o rename recria a FK para `tipo_atividade`; validado
  por teste criando uma saída que referencia um tipo.
- **Contrato com o frontend**: `id_responsavel` passa de `number` para `string`
  (UUID); a integração ajusta o type e o carregamento de funcionários/talhões.
- **Ordem na migration**: criar `categoria_atividade` antes de alterar
  `tipo_atividade`; recriar a FK da movimentação após o rename da tabela.
