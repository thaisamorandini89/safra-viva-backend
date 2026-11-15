# atividade-agricola Spec Delta

## ADDED Requirements

### Requirement: Estrutura da operação agrícola

O sistema SHALL persistir cada operação de campo na tabela `atividade_agricola`
com `id_atividade_agricola` (PK inteira autoincremental), `id_categoria_atividade`
(FK, obrigatório), `id_tipo_atividade` (FK para `tipo_atividade`, obrigatório),
`id_talhao` (FK para `talhao`, obrigatório), `id_propriedade` (FK, opcional),
`id_empresa` (opcional), `safra` (String(20), opcional), `id_funcionario` (FK
String(36) para `funcionario`, opcional), `status` (**enumerado**, aceitando
exclusivamente `Planejada`, `Em Andamento` ou `Concluída`, default `Planejada`),
`data_inicio` (Date, obrigatório), `data_fim` (Date, opcional), `custo_operacao`
(Numeric(14,2), opcional), `observacoes` (String(1000), opcional) e
`data_cadastro` (DateTime, default agora).

#### Scenario: Tabelas criadas por migration

- **WHEN** a migration é aplicada
- **THEN** a tabela `atividade_agricola` possui as colunas descritas
- **AND** a coluna `status` é restrita aos valores `Planejada`, `Em Andamento` e
  `Concluída` no nível do banco (tipo enumerado)
- **AND** existem `atividade_insumo` e `atividade_maquina` com FK para
  `atividade_agricola` e remoção em cascata

#### Scenario: Status restrito

- **WHEN** uma operação é criada ou atualizada com `status` fora de `Planejada`,
  `Em Andamento`, `Concluída`
- **THEN** a resposta é HTTP 400 e nada é persistido

#### Scenario: Status padrão

- **WHEN** um `POST /api/atividades` é enviado sem `status`
- **THEN** a operação é persistida com `status` igual a `Planejada`

### Requirement: Opções de status para o frontend

O sistema SHALL expor `GET /api/atividades/status-opcoes` retornando a lista
ordenada dos valores de status permitidos (`Planejada`, `Em Andamento`,
`Concluída`), para alimentar o combo de seleção da interface.

#### Scenario: Listagem das opções

- **WHEN** um `GET /api/atividades/status-opcoes` é realizado
- **THEN** a resposta é HTTP 200 com `["Planejada", "Em Andamento", "Concluída"]`

### Requirement: Insumos e máquinas da operação

O sistema SHALL permitir associar a uma operação uma lista de insumos utilizados
e uma lista de máquinas e implementos, persistidas em `atividade_insumo` e
`atividade_maquina`. Cada insumo da lista SHALL referenciar um `Insumo`
cadastrado (`id_insumo`, obrigatório) e armazenar `nome` e `unidade` como
snapshot, além de `quantidade` e `custo`. Cada máquina da lista SHALL referenciar
uma `Maquina` cadastrada (`id_maquina`, obrigatório) e armazenar `nome` como
snapshot, além de `horas` e `custo`. Ao excluir a operação, seus insumos e
máquinas SHALL ser removidos em cascata.

#### Scenario: Criação com coleções

- **WHEN** um `POST /api/atividades` inclui `insumos` (com `id_insumo`) e
  `maquinas` (com `id_maquina`)
- **THEN** a operação é criada com os itens vinculados
- **AND** a resposta inclui as duas listas com os snapshots de nome/unidade

#### Scenario: Insumo inexistente no item

- **WHEN** um item de `insumos` referencia um `id_insumo` inexistente
- **THEN** a resposta é HTTP 400 e nada é persistido

#### Scenario: Máquina inexistente no item

- **WHEN** um item de `maquinas` referencia um `id_maquina` inexistente
- **THEN** a resposta é HTTP 400 e nada é persistido

#### Scenario: Substituição no update

- **WHEN** um `PUT /api/atividades/{id}` envia novas listas de `insumos`/`maquinas`
- **THEN** os itens anteriores são removidos e substituídos pelos novos

### Requirement: Cadastro de operação

O sistema SHALL expor `POST /api/atividades` exigindo `id_categoria_atividade`,
`id_tipo_atividade`, `id_talhao` e `data_inicio`. Categoria, tipo e talhão
informados SHALL existir; quando `id_funcionario` for informado, ele SHALL
existir. Quando `data_fim` e `data_inicio` estiverem presentes, `data_fim` SHALL
ser maior ou igual a `data_inicio`.

#### Scenario: Cadastro realizado

- **WHEN** um `POST /api/atividades` válido é enviado
- **THEN** a resposta é HTTP 201 com o objeto da operação (incluindo
  `id_atividade_agricola`, nomes resolvidos de categoria, tipo, talhão e
  responsável, listas e campos derivados)

#### Scenario: Referência inexistente

- **WHEN** um `POST /api/atividades` referencia categoria, tipo, talhão ou
  funcionário inexistente
- **THEN** a resposta é HTTP 400 e nada é persistido

#### Scenario: Período inválido

- **WHEN** um `POST /api/atividades` envia `data_fim` anterior a `data_inicio`
- **THEN** a resposta é HTTP 400 e nada é persistido

### Requirement: Listagem e filtros

O sistema SHALL expor `GET /api/atividades` retornando as operações ordenadas por
`data_inicio` decrescente, cada uma com os nomes resolvidos de categoria, tipo,
talhão e responsável, suas listas de insumos e máquinas e os campos derivados
`custo_total`, `duracao_dias`, `atrasada`, `insumos_count` e `maquinas_count`.
A listagem SHALL aceitar filtros opcionais por `status`, `id_categoria_atividade`,
`id_tipo_atividade`, `id_talhao`, `safra` e `busca`.

#### Scenario: Listagem sem filtros

- **WHEN** um `GET /api/atividades` é realizado
- **THEN** a resposta é HTTP 200 com a lista de operações e seus campos derivados

#### Scenario: Filtro por status

- **WHEN** um `GET /api/atividades?status=Em Andamento` é realizado
- **THEN** a resposta inclui apenas operações com esse status

### Requirement: Indicadores de atividades

O sistema SHALL expor `GET /api/atividades/indicadores` retornando `total`,
`custo_total`, `em_andamento`, `atrasadas`, `planejadas` e `concluidas`,
respeitando os mesmos filtros da listagem.

#### Scenario: Indicadores calculados

- **WHEN** um `GET /api/atividades/indicadores` é realizado
- **THEN** a resposta é HTTP 200 com os totais agregados

### Requirement: Detalhe, atualização e exclusão

O sistema SHALL expor `GET /api/atividades/{id}`, `PUT /api/atividades/{id}` e
`DELETE /api/atividades/{id}`. O `DELETE` SHALL remover a operação e seus insumos
e máquinas.

#### Scenario: Detalhe encontrado

- **WHEN** um `GET /api/atividades/{id}` existente é solicitado
- **THEN** a resposta é HTTP 200 com o objeto rico da operação

#### Scenario: Operação inexistente

- **WHEN** um `GET`, `PUT` ou `DELETE` referencia um `id` inexistente
- **THEN** a resposta é HTTP 404

#### Scenario: Exclusão em cascata

- **WHEN** um `DELETE /api/atividades/{id}` é realizado
- **THEN** a operação e seus registros em `atividade_insumo` e
  `atividade_maquina` são removidos
- **AND** a resposta é HTTP 200
