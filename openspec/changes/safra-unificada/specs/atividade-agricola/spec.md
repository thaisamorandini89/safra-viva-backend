# atividade-agricola Spec Delta

## ADDED Requirements

### Requirement: Safra cadastrada na operação

O sistema SHALL aceitar em `POST /api/atividades` e `PUT /api/atividades/{id}` o
campo opcional `id_safra`, de uma safra cadastrada, recusando com HTTP 400 a
safra inexistente. Toda resposta que devolve a operação SHALL trazer `id_safra`
e, em `safra`, o nome da safra cadastrada. A saída de estoque gerada pela
conclusão da operação SHALL levar a mesma safra.

#### Scenario: Operação criada com safra cadastrada

- **WHEN** um `POST /api/atividades` é enviado com o `id_safra` de uma safra da
  propriedade do talhão
- **THEN** a resposta é HTTP 201 com esse `id_safra`
- **AND** `safra` traz o nome da safra cadastrada

#### Scenario: Safra inexistente

- **WHEN** um `POST /api/atividades` é enviado com um `id_safra` inexistente
- **THEN** a resposta é HTTP 400
- **AND** nenhuma operação é persistida

#### Scenario: Safra removida da operação

- **WHEN** um `PUT /api/atividades/{id}` é enviado com `id_safra` nulo para uma
  operação com safra cadastrada
- **THEN** a operação passa a ser devolvida com `id_safra` e `safra` nulos

#### Scenario: Saída gerada com a safra da operação

- **WHEN** uma operação com `id_safra` é salva como `Concluída` e gera uma saída
  de estoque
- **THEN** a saída gerada é devolvida em `GET /api/movimentacoes` com o mesmo
  `id_safra`

### Requirement: Safra da mesma propriedade da operação

O sistema SHALL recusar com HTTP 400, na criação e em qualquer atualização, a
operação cuja safra pertença a uma propriedade diferente da propriedade da
operação, considerando o estado final dos dados.

#### Scenario: Safra de outra propriedade

- **WHEN** um `POST /api/atividades` é enviado com o `id_safra` de uma safra de
  propriedade diferente da propriedade do talhão
- **THEN** a resposta é HTTP 400 com mensagem indicando que a safra é de outra
  propriedade
- **AND** nenhuma operação é persistida

#### Scenario: Talhão trocado para outra propriedade

- **WHEN** um `PUT /api/atividades/{id}` troca o talhão de uma operação com
  safra cadastrada por um talhão de outra propriedade, sem alterar a safra
- **THEN** a resposta é HTTP 400
- **AND** a operação permanece inalterada

### Requirement: Safra em texto dos registros anteriores

A operação sem `id_safra` SHALL continuar devolvendo em `safra` o texto que já
estava gravado. Uma atualização que não informe `id_safra` SHALL NOT alterar a
safra da operação. Informar `id_safra` SHALL substituir o texto anterior.

#### Scenario: Operação anterior consultada

- **WHEN** um `GET /api/atividades/{id}` devolve uma operação gravada antes
  desta mudança com safra em texto
- **THEN** `safra` traz o texto gravado e `id_safra` é nulo

#### Scenario: Atualização sem informar a safra

- **WHEN** um `PUT /api/atividades/{id}` altera outro campo de uma operação com
  safra em texto, sem enviar `id_safra`
- **THEN** a operação continua sendo devolvida com o mesmo texto em `safra`

#### Scenario: Safra cadastrada escolhida em registro anterior

- **WHEN** um `PUT /api/atividades/{id}` é enviado com `id_safra` para uma
  operação com safra em texto
- **THEN** a operação passa a ser devolvida com esse `id_safra`
- **AND** `safra` traz o nome da safra cadastrada, no lugar do texto anterior

### Requirement: Filtro de operações por safra cadastrada

O sistema SHALL aceitar em `GET /api/atividades` o filtro opcional `id_safra`,
devolvendo apenas as operações vinculadas à safra informada.

#### Scenario: Operações de uma safra

- **WHEN** um `GET /api/atividades?id_safra={id}` é realizado
- **THEN** a resposta é HTTP 200 contendo apenas as operações com esse
  `id_safra`
