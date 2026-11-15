# movimentacao-estoque Spec Delta

## Purpose

Registra as entradas e saídas de estoque dos insumos, atualizando o saldo e
guardando os dados de origem, destino e rastreabilidade de cada movimentação.

## ADDED Requirements

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
