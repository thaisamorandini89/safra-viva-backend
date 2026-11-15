# movimentacao-estoque Specification

## Purpose
Registra as entradas e saídas de estoque dos insumos, atualizando o saldo e
guardando os dados de origem, destino e rastreabilidade de cada movimentação.

## Requirements

### Requirement: Estrutura da movimentação de estoque

O sistema SHALL persistir movimentações na tabela `movimentacao_estoque` com:
`id_movimentacao` (UUID em formato string, PK), `id_insumo` (FK obrigatória
para `insumo.id_insumo`), `tipo_movimentacao` ('ENTRADA' ou 'SAIDA',
obrigatório), `quantidade` (Numeric(14,3), obrigatório e positivo),
`data_movimentacao` (DateTime, preenchida pelo banco),
`id_funcionario` (String(36), FK opcional para `funcionario.id_funcionario`;
obrigatório na interface), `observacao` (String(500), opcional) e
`valor_unitario` (Numeric(14,2), opcional).

A movimentação SHALL suportar campos de detalhe condicionais, todos opcionais
no banco (`nullable=True`):

- Dados da Entrada: `id_fornecedor` (FK para `fornecedor.id_fornecedor`),
  `numero_nota_fiscal` (String(50)), `numero_lote` (String(50)),
  `data_fabricacao` (Date) e `data_validade` (Date).
- Destino e Rastreabilidade (Saída): `id_talhao` (FK para `talhao.id_talhao`),
  `safra` (String(20)), `id_atividade` (FK para `tipo_atividade.id_atividade`) e
  `destino_finalidade` (String(255)).

#### Scenario: Tabela criada por migration

- **WHEN** a migration é aplicada
- **THEN** a tabela `movimentacao_estoque` existe com as colunas, FKs e
  restrições descritas

### Requirement: Registro de entrada de estoque

Ao registrar uma movimentação de tipo ENTRADA via `POST /api/movimentacoes`,
o sistema SHALL somar `quantidade` ao `estoque_atual` do insumo vinculado,
persistindo movimentação e saldo na mesma transação.

#### Scenario: Entrada registrada

- **WHEN** um `POST /api/movimentacoes` é enviado com tipo ENTRADA,
  insumo existente e quantidade positiva
- **THEN** a movimentação é persistida
- **AND** `estoque_atual` do insumo é incrementado em `quantidade`
- **AND** a resposta é HTTP 201 com a movimentação e o novo `estoque_atual`

### Requirement: Registro de saída de estoque

Ao registrar uma movimentação de tipo SAIDA, o sistema SHALL subtrair
`quantidade` do `estoque_atual` do insumo, rejeitando a operação quando o
saldo for insuficiente.

#### Scenario: Saída com saldo suficiente

- **WHEN** um `POST /api/movimentacoes` é enviado com tipo SAIDA e
  `quantidade` menor ou igual ao `estoque_atual` do insumo
- **THEN** a movimentação é persistida
- **AND** `estoque_atual` é decrementado em `quantidade`
- **AND** a resposta é HTTP 201

#### Scenario: Saída com saldo insuficiente

- **WHEN** um `POST /api/movimentacoes` é enviado com tipo SAIDA e
  `quantidade` maior que o `estoque_atual`
- **THEN** nenhuma movimentação é registrada
- **AND** o `estoque_atual` permanece inalterado
- **AND** a resposta é HTTP 400 com mensagem de saldo insuficiente

### Requirement: Validação do payload de movimentação

O sistema SHALL validar o payload com schema Pydantic, rejeitando com HTTP 400:
tipo diferente de ENTRADA/SAIDA, quantidade ausente, zero ou negativa, insumo
inexistente e funcionário informado inexistente.

#### Scenario: Tipo inválido

- **WHEN** um `POST /api/movimentacoes` é enviado com `tipo_movimentacao`
  fora de {ENTRADA, SAIDA}
- **THEN** a resposta é HTTP 400 e nada é persistido

#### Scenario: Quantidade não positiva

- **WHEN** um `POST /api/movimentacoes` é enviado com `quantidade` <= 0
- **THEN** a resposta é HTTP 400 e nada é persistido

#### Scenario: Insumo inexistente

- **WHEN** um `POST /api/movimentacoes` referencia um `id_insumo` inexistente
- **THEN** a resposta é HTTP 400 e nada é persistido

#### Scenario: Funcionário opcional

- **WHEN** um `POST /api/movimentacoes` é enviado sem `id_funcionario`
- **THEN** a movimentação é registrada normalmente com funcionário nulo

### Requirement: Detalhes condicionais por tipo de movimentação

O sistema SHALL aceitar os campos de detalhe de entrada
(`id_fornecedor`, `numero_nota_fiscal`, `numero_lote`, `data_fabricacao`,
`data_validade`) apenas em movimentações ENTRADA, e os campos de destino e
rastreabilidade (`id_talhao`, `safra`, `id_atividade`,
`destino_finalidade`) apenas em movimentações SAIDA, rejeitando com HTTP 400 o
envio cruzado. `id_fornecedor`, `id_talhao` e `id_atividade`, quando
informados, SHALL referenciar registros existentes.

#### Scenario: Entrada com dados completos

- **WHEN** um `POST /api/movimentacoes` ENTRADA é enviado com fornecedor,
  nota fiscal, lote e datas de fabricação/validade
- **THEN** a movimentação é persistida com todos os campos informados
- **AND** a resposta é HTTP 201 contendo os detalhes da entrada

#### Scenario: Saída com destino e rastreabilidade

- **WHEN** um `POST /api/movimentacoes` SAIDA é enviado com talhão, safra,
  atividade relacionada e destino/finalidade
- **THEN** a movimentação é persistida com todos os campos informados
- **AND** a resposta é HTTP 201 contendo os detalhes da saída

#### Scenario: Campo de entrada em uma SAIDA

- **WHEN** um `POST /api/movimentacoes` SAIDA inclui qualquer campo de entrada
  (ex.: `numero_nota_fiscal`)
- **THEN** nada é persistido
- **AND** a resposta é HTTP 400 indicando o campo não permitido para o tipo

#### Scenario: Campo de saída em uma ENTRADA

- **WHEN** um `POST /api/movimentacoes` ENTRADA inclui qualquer campo de saída
  (ex.: `id_talhao`)
- **THEN** nada é persistido
- **AND** a resposta é HTTP 400 indicando o campo não permitido para o tipo

#### Scenario: Validade anterior à fabricação

- **WHEN** uma ENTRADA informa `data_validade` anterior a `data_fabricacao`
- **THEN** nada é persistido
- **AND** a resposta é HTTP 400

#### Scenario: Fornecedor, talhão ou atividade inexistente

- **WHEN** a movimentação referencia `id_fornecedor`, `id_talhao` ou
  `id_atividade` inexistente
- **THEN** nada é persistido
- **AND** a resposta é HTTP 400

### Requirement: Histórico de movimentações

O sistema SHALL expor `GET /api/movimentacoes` retornando o histórico ordenado
por `data_movimentacao` decrescente, com suporte ao filtro por insumo via
query param `id_insumo`, incluindo em cada item os dados do insumo/produto, o
nome do funcionário, o nome do fornecedor/talhão e a descrição da atividade
(quando houver).

#### Scenario: Listagem completa

- **WHEN** um `GET /api/movimentacoes` é realizado sem filtros
- **THEN** a resposta é HTTP 200 com todas as movimentações em ordem
  decrescente de data

#### Scenario: Filtro por insumo

- **WHEN** um `GET /api/movimentacoes?id_insumo={id}` é realizado
- **THEN** a resposta é HTTP 200 contendo apenas movimentações daquele insumo

### Requirement: Vínculo da saída com a operação agrícola

O sistema SHALL aceitar em movimentações SAIDA o campo opcional
`id_atividade_agricola`, que referencia uma operação agrícola existente, e SHALL
gravar em `id_atividade` o tipo de atividade dessa operação quando ele não for
informado. Em movimentações ENTRADA o campo SHALL ser recusado com HTTP 400.

#### Scenario: Saída vinculada a uma operação

- **WHEN** um `POST /api/movimentacoes` SAIDA informa `id_atividade_agricola` de
  uma operação existente, sem `id_atividade`
- **THEN** a resposta é HTTP 201 com `id_atividade_agricola` igual ao informado
- **AND** `id_atividade` e `atividade_descricao` correspondem ao tipo de
  atividade da operação

#### Scenario: Operação inexistente

- **WHEN** um `POST /api/movimentacoes` SAIDA informa um `id_atividade_agricola`
  inexistente
- **THEN** a resposta é HTTP 400
- **AND** nada é persistido e o `estoque_atual` do insumo permanece inalterado

#### Scenario: Operação em uma ENTRADA

- **WHEN** um `POST /api/movimentacoes` ENTRADA inclui `id_atividade_agricola`
- **THEN** a resposta é HTTP 400 indicando o campo não permitido para o tipo

#### Scenario: Saída sem operação

- **WHEN** um `POST /api/movimentacoes` SAIDA é enviado sem
  `id_atividade_agricola`
- **THEN** a movimentação é registrada com `id_atividade_agricola` nulo

### Requirement: Coerência da operação vinculada

Quando `id_atividade_agricola` for informado junto com `id_atividade` ou
`id_talhao`, o sistema SHALL exigir que eles correspondam ao tipo de atividade e
ao talhão da operação, recusando com HTTP 400 a movimentação divergente.

#### Scenario: Tipo divergente da operação

- **WHEN** um `POST /api/movimentacoes` SAIDA informa `id_atividade_agricola` e
  um `id_atividade` diferente do tipo da operação
- **THEN** a resposta é HTTP 400 e nada é persistido

#### Scenario: Talhão divergente da operação

- **WHEN** um `POST /api/movimentacoes` SAIDA informa `id_atividade_agricola` e
  um `id_talhao` diferente do talhão da operação
- **THEN** a resposta é HTTP 400 e nada é persistido

### Requirement: Histórico preservado ao excluir a operação

Ao excluir uma operação agrícola referenciada por movimentações de estoque, o
sistema SHALL manter as movimentações e o saldo dos insumos, removendo apenas o
vínculo com a operação e preservando o tipo de atividade gravado.

#### Scenario: Exclusão de operação com movimentações

- **WHEN** um `DELETE /api/atividades/{id}` é enviado para uma operação
  referenciada por uma movimentação
- **THEN** a resposta é HTTP 200
- **AND** a movimentação continua no histórico com `id_atividade_agricola` nulo
  e o mesmo `id_atividade`
- **AND** o `estoque_atual` do insumo permanece inalterado

### Requirement: Data informada da movimentação

O sistema SHALL aceitar no `POST /api/movimentacoes` o campo opcional
`data_movimentacao` (data no formato `AAAA-MM-DD`) e usá-lo como data da
movimentação. Quando o campo for omitido, a data SHALL ser a do registro.

#### Scenario: Movimentação com data informada

- **WHEN** um `POST /api/movimentacoes` informa `data_movimentacao`
- **THEN** a resposta é HTTP 201
- **AND** a movimentação é devolvida, na resposta e no histórico, com
  `data_movimentacao` no dia informado

#### Scenario: Movimentação sem data

- **WHEN** um `POST /api/movimentacoes` é enviado sem `data_movimentacao`
- **THEN** a movimentação é registrada com a data e a hora do registro

#### Scenario: Data inválida

- **WHEN** um `POST /api/movimentacoes` informa `data_movimentacao` que não é
  uma data válida
- **THEN** a resposta é HTTP 400 e nada é persistido

### Requirement: Identificação do talhão e da operação no histórico

O sistema SHALL incluir `codigo_talhao` e `id_atividade_agricola` em cada item
do `GET /api/movimentacoes` e na resposta do `POST /api/movimentacoes`,
devolvendo-os nulos quando a movimentação não tiver talhão ou operação.

#### Scenario: Saída com talhão e operação

- **WHEN** um `GET /api/movimentacoes` devolve uma saída registrada com talhão e
  operação
- **THEN** o item inclui o `codigo_talhao` do talhão e o `id_atividade_agricola`
  da operação

#### Scenario: Entrada

- **WHEN** um `GET /api/movimentacoes` devolve uma entrada
- **THEN** o item traz `codigo_talhao` e `id_atividade_agricola` nulos

### Requirement: Saldo utilizável na saída

O sistema SHALL limitar a quantidade de uma SAIDA ao saldo utilizável do insumo,
que é o `estoque_atual` menos o saldo dos lotes vencidos, recusando com HTTP 400
a saída que o exceda, com mensagem que informe o saldo utilizável e a quantidade
vencida.

#### Scenario: Saída dentro do saldo utilizável

- **WHEN** um `POST /api/movimentacoes` SAIDA é enviado com quantidade menor ou
  igual ao saldo utilizável
- **THEN** a resposta é HTTP 201 e o `estoque_atual` é decrementado

#### Scenario: Saída acima do saldo utilizável

- **WHEN** um `POST /api/movimentacoes` SAIDA é enviado com quantidade maior que
  o saldo utilizável e menor ou igual ao `estoque_atual`
- **THEN** a resposta é HTTP 400 com mensagem informando o saldo utilizável e a
  quantidade em lotes vencidos
- **AND** nada é persistido e os saldos permanecem inalterados

### Requirement: Consumo de lotes pelo vencimento mais próximo

Ao registrar uma SAIDA sem lote indicado, o sistema SHALL retirar a quantidade
dos lotes não vencidos com saldo, na ordem da `data_validade` mais próxima,
depois dos lotes sem validade e, por último, do saldo sem lote. Lotes vencidos
SHALL NOT ser consumidos.

#### Scenario: Dois lotes válidos

- **WHEN** um insumo tem dois lotes não vencidos e uma SAIDA retira mais que o
  saldo do lote que vence primeiro
- **THEN** o lote que vence primeiro fica com saldo zero
- **AND** o restante é retirado do lote seguinte

#### Scenario: Lote vencido ignorado

- **WHEN** um insumo tem um lote vencido e um lote válido, e uma SAIDA é
  registrada dentro do saldo utilizável
- **THEN** a quantidade sai do lote válido
- **AND** o saldo do lote vencido permanece inalterado

#### Scenario: Saldo sem lote consumido por último

- **WHEN** um insumo tem saldo em lote válido e saldo sem lote, e uma SAIDA
  retira mais que o saldo do lote
- **THEN** o lote fica com saldo zero e o restante sai do saldo sem lote

### Requirement: Lotes da movimentação na resposta

O sistema SHALL incluir, na resposta do `POST /api/movimentacoes` e em cada item
do `GET /api/movimentacoes`, a lista `lotes` com os lotes afetados pela
movimentação e a quantidade de cada um, vazia quando nenhum lote foi afetado.

#### Scenario: Saída que consumiu dois lotes

- **WHEN** uma SAIDA retira quantidade de dois lotes
- **THEN** a resposta e o histórico trazem `lotes` com os dois números de lote e
  as respectivas quantidades

#### Scenario: Movimentação sem lote

- **WHEN** uma ENTRADA sem `numero_lote` é consultada no histórico
- **THEN** o item traz `lotes` como lista vazia

### Requirement: Descarte de lote

O sistema SHALL aceitar em uma SAIDA o campo opcional `id_lote`, retirando a
quantidade exclusivamente desse lote, mesmo que ele esteja vencido. O lote SHALL
pertencer ao insumo da movimentação e a quantidade SHALL ser menor ou igual ao
saldo do lote; caso contrário, a resposta é HTTP 400. Em ENTRADA o campo SHALL
ser recusado com HTTP 400.

#### Scenario: Descarte de lote vencido

- **WHEN** um `POST /api/movimentacoes` SAIDA informa o `id_lote` de um lote
  vencido e quantidade igual ao seu saldo
- **THEN** a resposta é HTTP 201
- **AND** o saldo do lote fica zero e o `estoque_atual` é decrementado

#### Scenario: Quantidade acima do saldo do lote

- **WHEN** um `POST /api/movimentacoes` SAIDA informa `id_lote` e quantidade
  maior que o saldo do lote
- **THEN** a resposta é HTTP 400 e nada é persistido

#### Scenario: Lote de outro insumo

- **WHEN** um `POST /api/movimentacoes` SAIDA informa um `id_lote` que não
  pertence ao insumo informado ou não existe
- **THEN** a resposta é HTTP 400 e nada é persistido

#### Scenario: Lote indicado em uma ENTRADA

- **WHEN** um `POST /api/movimentacoes` ENTRADA inclui `id_lote`
- **THEN** a resposta é HTTP 400 indicando o campo não permitido para o tipo

### Requirement: Origem da movimentação

O sistema SHALL informar em cada movimentação o campo `origem`, com o valor
`ATIVIDADE` para as saídas geradas pela conclusão de uma operação agrícola e
`MANUAL` para as demais. Toda movimentação registrada por
`POST /api/movimentacoes` SHALL ter origem `MANUAL`, independentemente do
payload.

#### Scenario: Movimentação lançada pela API

- **WHEN** um `POST /api/movimentacoes` é enviado, com ou sem `origem` no
  payload
- **THEN** a movimentação é devolvida com `origem` igual a `MANUAL`

#### Scenario: Movimentações anteriores

- **WHEN** um `GET /api/movimentacoes` devolve movimentações registradas antes
  desta mudança
- **THEN** elas vêm com `origem` igual a `MANUAL`

### Requirement: Filtro do histórico por operação

O sistema SHALL aceitar em `GET /api/movimentacoes` o filtro opcional
`id_atividade_agricola`, devolvendo apenas as movimentações vinculadas à
operação informada, manuais ou automáticas.

#### Scenario: Movimentações de uma operação

- **WHEN** um `GET /api/movimentacoes?id_atividade_agricola={id}` é realizado
  para uma operação com uma saída manual e uma automática
- **THEN** a resposta é HTTP 200 com as duas saídas e nenhuma outra

#### Scenario: Operação sem movimentações

- **WHEN** um `GET /api/movimentacoes?id_atividade_agricola={id}` é realizado
  para uma operação sem saídas vinculadas
- **THEN** a resposta é HTTP 200 com lista vazia

### Requirement: Saídas manuais preservadas na devolução

Ao desfazer as saídas de uma operação agrícola, o sistema SHALL remover apenas
as de origem `ATIVIDADE`. As saídas de origem `MANUAL` vinculadas à operação
SHALL permanecer no histórico com seus saldos, perdendo apenas o vínculo quando
a operação for excluída.

#### Scenario: Reabertura com saída manual vinculada

- **WHEN** uma operação concluída, com uma saída manual vinculada e uma
  automática, é reaberta
- **THEN** a saída automática é removida e seu saldo devolvido
- **AND** a saída manual permanece vinculada à operação, sem alteração de saldo

#### Scenario: Exclusão com saída manual vinculada

- **WHEN** a mesma operação é excluída
- **THEN** a saída manual permanece no histórico com `id_atividade_agricola`
  nulo e o tipo de atividade preservado
