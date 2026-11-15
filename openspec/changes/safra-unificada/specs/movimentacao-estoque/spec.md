# movimentacao-estoque Spec Delta

## ADDED Requirements

### Requirement: Safra cadastrada na saída

O sistema SHALL aceitar em uma SAIDA o campo opcional `id_safra`, de uma safra
cadastrada, recusando com HTTP 400 a safra inexistente e o campo enviado em uma
ENTRADA. A resposta do `POST /api/movimentacoes` e cada item do
`GET /api/movimentacoes` SHALL trazer `id_safra` e, em `safra`, o nome da safra
cadastrada ou, nas movimentações sem `id_safra`, o texto já gravado.

#### Scenario: Saída com safra cadastrada

- **WHEN** um `POST /api/movimentacoes` SAIDA é enviado com `id_safra` de uma
  safra cadastrada
- **THEN** a resposta é HTTP 201 com esse `id_safra`
- **AND** `safra` traz o nome da safra cadastrada

#### Scenario: Safra inexistente na saída

- **WHEN** um `POST /api/movimentacoes` SAIDA é enviado com um `id_safra`
  inexistente
- **THEN** a resposta é HTTP 400
- **AND** nada é persistido e o saldo permanece inalterado

#### Scenario: Safra cadastrada em uma ENTRADA

- **WHEN** um `POST /api/movimentacoes` ENTRADA inclui `id_safra`
- **THEN** a resposta é HTTP 400 indicando o campo não permitido para o tipo

#### Scenario: Movimentação anterior com safra em texto

- **WHEN** um `GET /api/movimentacoes` devolve uma saída gravada antes desta
  mudança com safra em texto
- **THEN** o item traz o texto gravado em `safra` e `id_safra` nulo

### Requirement: Coerência da safra com o talhão e a operação

O sistema SHALL recusar com HTTP 400 a SAIDA cuja safra pertença a uma
propriedade diferente da propriedade do talhão informado. Na SAIDA vinculada a
uma operação agrícola com safra cadastrada, o sistema SHALL usar a safra da
operação quando `id_safra` não for informado e SHALL recusar com HTTP 400 um
`id_safra` diferente.

#### Scenario: Safra de propriedade diferente do talhão

- **WHEN** um `POST /api/movimentacoes` SAIDA é enviado com `id_talhao` e com o
  `id_safra` de uma safra de outra propriedade
- **THEN** a resposta é HTTP 400
- **AND** nada é persistido e o saldo permanece inalterado

#### Scenario: Saída vinculada herda a safra da operação

- **WHEN** um `POST /api/movimentacoes` SAIDA é enviado com
  `id_atividade_agricola` de uma operação com safra cadastrada, sem `id_safra`
- **THEN** a resposta é HTTP 201 com o `id_safra` da operação

#### Scenario: Safra diferente da operação

- **WHEN** um `POST /api/movimentacoes` SAIDA é enviado com
  `id_atividade_agricola` de uma operação com safra cadastrada e com um
  `id_safra` diferente
- **THEN** a resposta é HTTP 400
- **AND** nada é persistido e o saldo permanece inalterado
