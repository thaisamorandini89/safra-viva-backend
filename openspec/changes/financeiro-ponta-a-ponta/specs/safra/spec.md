# safra Spec Delta

## Purpose

Cadastro de safra agrícola — período, propriedade, cultura e área — usado como
dimensão para vincular lançamentos financeiros e apurar o resultado por safra e
por cultura.

## ADDED Requirements

### Requirement: Período válido da safra

O sistema SHALL recusar com HTTP 400, no cadastro e na edição, a safra cuja
`data_fim` seja anterior à `data_inicio`.

#### Scenario: Término anterior ao início

- **WHEN** um `POST /api/safras` é enviado com `data_fim` anterior à
  `data_inicio`
- **THEN** a resposta é HTTP 400
- **AND** nenhuma safra é persistida

### Requirement: Nome de safra único na propriedade

O sistema SHALL recusar com HTTP 400 o cadastro ou a edição que deixe duas
safras da mesma propriedade com o mesmo `nome`, sem diferenciar maiúsculas de
minúsculas.

#### Scenario: Nome repetido na mesma propriedade

- **WHEN** um `POST /api/safras` é enviado com o `nome` de uma safra já
  cadastrada na mesma propriedade, com outra capitalização
- **THEN** a resposta é HTTP 400 com mensagem indicando o nome repetido
- **AND** nenhuma safra é persistida

#### Scenario: Mesmo nome em outra propriedade

- **WHEN** um `POST /api/safras` é enviado com o `nome` de uma safra cadastrada
  em outra propriedade
- **THEN** a resposta é HTTP 201

### Requirement: Edição de safra

O sistema SHALL permitir atualização parcial via `PUT /api/safras/{id_safra}`,
alterando apenas os campos enviados entre `nome`, `cultura`, `data_inicio`,
`data_fim`, `area_plantada` e `status`, com as validações do cadastro, e
devolvendo a safra completa. A propriedade da safra SHALL NOT ser alterada: um
`id_propriedade` diferente do atual é recusado com HTTP 400.

#### Scenario: Edição válida

- **WHEN** um `PUT /api/safras/{id_safra}` é enviado com `cultura` e
  `area_plantada`
- **THEN** a resposta é HTTP 200 com a safra completa
- **AND** somente os campos enviados são alterados

#### Scenario: Safra inativada

- **WHEN** um `PUT /api/safras/{id_safra}` é enviado com `status` falso
- **THEN** a safra continua sendo devolvida por `GET /api/safras`, com `status`
  falso

#### Scenario: Dado inválido na edição

- **WHEN** um `PUT /api/safras/{id_safra}` é enviado com `nome` vazio, com
  `data_fim` anterior à `data_inicio` ou com `id_propriedade` diferente do atual
- **THEN** a resposta é HTTP 400
- **AND** a safra permanece inalterada

#### Scenario: Edição de safra inexistente

- **WHEN** um `PUT /api/safras/{id_safra}` é feito para um id inexistente
- **THEN** a resposta é HTTP 404

### Requirement: Exclusão de safra

O sistema SHALL permitir excluir uma safra via `DELETE /api/safras/{id_safra}`
e SHALL recusar com HTTP 400, com mensagem indicando que a safra está em uso, a
exclusão de uma safra referenciada por algum lançamento financeiro.

#### Scenario: Exclusão de safra sem uso

- **WHEN** um `DELETE /api/safras/{id_safra}` é feito para uma safra sem
  lançamentos
- **THEN** a resposta é HTTP 200
- **AND** a safra deixa de ser devolvida por `GET /api/safras`

#### Scenario: Safra com lançamentos

- **WHEN** um `DELETE /api/safras/{id_safra}` é feito para uma safra
  referenciada por um lançamento
- **THEN** a resposta é HTTP 400 com mensagem indicando que a safra está em uso
- **AND** a safra continua cadastrada

#### Scenario: Exclusão de safra inexistente

- **WHEN** um `DELETE /api/safras/{id_safra}` é feito para um id inexistente
- **THEN** a resposta é HTTP 404
