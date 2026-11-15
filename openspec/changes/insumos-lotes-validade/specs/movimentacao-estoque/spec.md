# movimentacao-estoque Spec Delta

## Purpose

Registra as entradas e saídas de estoque dos insumos, atualizando o saldo e
guardando os dados de origem, destino e rastreabilidade de cada movimentação.

## ADDED Requirements

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
