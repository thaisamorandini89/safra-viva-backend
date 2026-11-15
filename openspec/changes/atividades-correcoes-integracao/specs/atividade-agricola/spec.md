# atividade-agricola Spec Delta

## Purpose

Registra as operações de campo executadas em um talhão, com categoria, tipo,
responsável, período, status, custos e os insumos e máquinas utilizados.

## ADDED Requirements

### Requirement: Unicidade da operação por talhão, tipo e data de início

O sistema SHALL recusar com HTTP 400 a criação ou a atualização de uma operação
quando o resultado coincidir com outra operação existente no mesmo `id_talhao`,
`id_tipo_atividade` e `data_inicio`.

#### Scenario: Criação duplicada

- **WHEN** um `POST /api/atividades` é enviado com talhão, tipo e data de início
  iguais aos de uma operação existente
- **THEN** a resposta é HTTP 400 com mensagem indicando a duplicidade
- **AND** nada é persistido

#### Scenario: Atualização que gera duplicidade

- **WHEN** um `PUT /api/atividades/{id}` altera talhão, tipo ou data de início de
  modo que a operação coincida com outra existente
- **THEN** a resposta é HTTP 400
- **AND** a operação mantém os valores anteriores

#### Scenario: Atualização da própria operação

- **WHEN** um `PUT /api/atividades/{id}` altera outros campos sem mudar talhão,
  tipo e data de início
- **THEN** a resposta é HTTP 200

#### Scenario: Mesma operação em outra data

- **WHEN** um `POST /api/atividades` repete talhão e tipo de uma operação
  existente com `data_inicio` diferente
- **THEN** a resposta é HTTP 201

### Requirement: Consistência entre tipo e categoria

O sistema SHALL exigir que o tipo de atividade da operação pertença à categoria
da operação, recusando com HTTP 400 a criação ou a atualização que resulte em
uma combinação divergente.

#### Scenario: Criação com tipo de outra categoria

- **WHEN** um `POST /api/atividades` informa um `id_tipo_atividade` cuja
  categoria é diferente de `id_categoria_atividade`
- **THEN** a resposta é HTTP 400 e nada é persistido

#### Scenario: Atualização só da categoria

- **WHEN** um `PUT /api/atividades/{id}` altera apenas `id_categoria_atividade`
  para uma categoria à qual o tipo atual não pertence
- **THEN** a resposta é HTTP 400 e a operação não é alterada

#### Scenario: Atualização coerente de categoria e tipo

- **WHEN** um `PUT /api/atividades/{id}` altera categoria e tipo para uma
  combinação em que o tipo pertence à categoria
- **THEN** a resposta é HTTP 200

### Requirement: Data de término para operação concluída

O sistema SHALL recusar com HTTP 400 a criação ou a atualização que resulte em
uma operação com `status` igual a `Concluída` e sem `data_fim`.

#### Scenario: Criação concluída sem término

- **WHEN** um `POST /api/atividades` é enviado com `status` `Concluída` e sem
  `data_fim`
- **THEN** a resposta é HTTP 400 e nada é persistido

#### Scenario: Conclusão de operação sem término

- **WHEN** um `PUT /api/atividades/{id}` altera o `status` para `Concluída` em
  uma operação sem `data_fim`, sem informar `data_fim`
- **THEN** a resposta é HTTP 400 e a operação não é alterada

#### Scenario: Conclusão informando o término

- **WHEN** um `PUT /api/atividades/{id}` altera o `status` para `Concluída` e
  informa `data_fim`
- **THEN** a resposta é HTTP 200

#### Scenario: Remoção do término de operação concluída

- **WHEN** um `PUT /api/atividades/{id}` envia `data_fim` nulo para uma operação
  com `status` `Concluída`
- **THEN** a resposta é HTTP 400 e a operação não é alterada

### Requirement: Data de referência do atraso

O sistema SHALL calcular o campo `atrasada` e o indicador `atrasadas` comparando
o prazo da operação (`data_fim` ou, na falta, `data_inicio`) com a data corrente
no fuso horário configurado para a aplicação, cujo padrão é
`America/Sao_Paulo`, e não com a data UTC do servidor.

#### Scenario: Prazo no dia corrente após a virada do dia em UTC

- **WHEN** uma operação não concluída tem prazo igual à data local corrente
- **AND** a consulta ocorre em horário local no qual a data UTC já é a do dia
  seguinte
- **THEN** a operação é devolvida com `atrasada` igual a `false`

#### Scenario: Prazo vencido

- **WHEN** uma operação não concluída tem prazo anterior à data local corrente
- **THEN** a operação é devolvida com `atrasada` igual a `true`
- **AND** ela é contada em `atrasadas` nos indicadores

#### Scenario: Operação concluída

- **WHEN** uma operação com `status` `Concluída` tem prazo anterior à data local
  corrente
- **THEN** a operação é devolvida com `atrasada` igual a `false`

### Requirement: Nome da propriedade na operação

O sistema SHALL incluir `nome_propriedade` em toda resposta que devolve o objeto
da operação, resolvido a partir de `id_propriedade`, e SHALL devolvê-lo nulo
quando a operação não tiver propriedade.

#### Scenario: Listagem com propriedade

- **WHEN** um `GET /api/atividades` devolve uma operação com `id_propriedade`
- **THEN** o item inclui `nome_propriedade` com o nome da propriedade

#### Scenario: Propriedade derivada do talhão

- **WHEN** um `POST /api/atividades` é enviado sem `id_propriedade`
- **THEN** a resposta inclui o `id_propriedade` do talhão e o respectivo
  `nome_propriedade`
