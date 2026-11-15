# atividade-agricola Spec Delta

## Purpose

Registra as operações de campo executadas em um talhão, com categoria, tipo,
responsável, período, status, custos e os insumos e máquinas utilizados.

## ADDED Requirements

### Requirement: Baixa de estoque ao concluir a operação

O sistema SHALL gerar, ao salvar uma operação com `status` `Concluída`, uma
saída de estoque para cada insumo da operação com quantidade positiva e saldo
utilizável suficiente. Cada saída SHALL ficar vinculada à operação, ter origem
`ATIVIDADE` e usar o talhão, a safra, o responsável e a `data_fim` da operação e
o valor unitário do insumo.

#### Scenario: Conclusão com saldo

- **WHEN** um `PUT /api/atividades/{id}` altera para `Concluída` uma operação
  com dois insumos listados, ambos com saldo utilizável suficiente
- **THEN** a resposta é HTTP 200
- **AND** duas saídas são registradas e o `estoque_atual` de cada insumo é
  decrementado na quantidade listada
- **AND** os dois insumos da operação vêm com `baixado` verdadeiro

#### Scenario: Operação criada já concluída

- **WHEN** um `POST /api/atividades` é enviado com `status` `Concluída`,
  `data_fim` e insumos com saldo
- **THEN** a resposta é HTTP 201 e as saídas são geradas

#### Scenario: Dados da saída gerada

- **WHEN** uma saída gerada pela conclusão é consultada em
  `GET /api/movimentacoes`
- **THEN** ela traz o `id_atividade_agricola` da operação, o talhão, o tipo de
  atividade, a data igual à `data_fim` e `origem` igual a `ATIVIDADE`

#### Scenario: Operação não concluída

- **WHEN** uma operação é criada ou atualizada com `status` `Planejada` ou
  `Em Andamento`
- **THEN** nenhuma saída de estoque é gerada

#### Scenario: Insumo sem quantidade

- **WHEN** uma operação é concluída com um insumo listado sem quantidade ou com
  quantidade zero
- **THEN** nenhuma saída é gerada para esse insumo e ele não é informado como
  pendente

### Requirement: Insumo sem saldo suficiente na conclusão

Quando o saldo utilizável de um insumo for menor que a quantidade listada, o
sistema SHALL concluir a operação sem gerar saída para esse insumo, mantendo as
saídas dos demais, e SHALL informá-lo como pendente na resposta. O sistema
SHALL NOT retirar parte da quantidade.

#### Scenario: Um insumo sem saldo entre dois

- **WHEN** uma operação é concluída com um insumo com saldo suficiente e outro
  com saldo utilizável menor que a quantidade listada
- **THEN** a resposta é HTTP 200 e a operação fica `Concluída`
- **AND** o primeiro insumo vem com `baixado` verdadeiro e tem a saída gerada
- **AND** o segundo vem com `baixado` falso, sem saída, com o `estoque_atual`
  inalterado, e consta em `baixa_estoque.pendentes`

### Requirement: Devolução ao estoque ao alterar operação concluída

Ao salvar uma alteração em uma operação concluída ou ao excluí-la, o sistema
SHALL desfazer as saídas geradas por ela, devolvendo as quantidades ao
`estoque_atual` e aos lotes de origem e removendo essas saídas do histórico. Se
a operação continuar `Concluída` após a alteração, o sistema SHALL gerar as
saídas novamente conforme a lista atual de insumos.

#### Scenario: Reabertura

- **WHEN** um `PUT /api/atividades/{id}` altera o `status` de `Concluída` para
  `Em Andamento`
- **THEN** as saídas geradas pela operação deixam de constar no histórico
- **AND** o `estoque_atual` dos insumos volta ao valor anterior à conclusão
- **AND** os insumos da operação vêm com `baixado` falso

#### Scenario: Alteração da quantidade

- **WHEN** um `PUT /api/atividades/{id}` altera a quantidade de um insumo de uma
  operação que continua `Concluída`
- **THEN** o `estoque_atual` do insumo reflete apenas a nova quantidade

#### Scenario: Devolução ao lote

- **WHEN** uma operação concluída cuja saída consumiu um lote é reaberta
- **THEN** o saldo desse lote volta ao valor anterior à conclusão

#### Scenario: Nova tentativa de insumo pendente

- **WHEN** um insumo ficou pendente, o estoque recebe uma entrada suficiente e
  um `PUT /api/atividades/{id}` é enviado para a operação concluída
- **THEN** a saída do insumo é gerada e ele passa a vir com `baixado` verdadeiro

#### Scenario: Exclusão de operação concluída

- **WHEN** um `DELETE /api/atividades/{id}` é enviado para uma operação
  concluída com saídas geradas
- **THEN** a resposta é HTTP 200
- **AND** as saídas geradas são removidas e o `estoque_atual` é devolvido

#### Scenario: Alteração recusada

- **WHEN** um `PUT /api/atividades/{id}` em uma operação concluída é recusado
  por uma regra da operação
- **THEN** as saídas geradas e os saldos permanecem como estavam

### Requirement: Situação da baixa na resposta da operação

O sistema SHALL incluir, em toda resposta que devolve o objeto da operação, os
campos `baixado` e `id_movimentacao` em cada insumo, e o objeto `baixa_estoque`
com `geradas` (quantidade de saídas automáticas vigentes) e `pendentes` (lista
com `id_insumo`, `nome`, `quantidade` e `disponivel`).

#### Scenario: Operação concluída com pendência

- **WHEN** um `GET /api/atividades/{id}` devolve uma operação concluída com um
  insumo baixado e outro pendente
- **THEN** `baixa_estoque.geradas` é 1
- **AND** `baixa_estoque.pendentes` traz o insumo pendente com a quantidade
  listada e o saldo utilizável atual em `disponivel`

#### Scenario: Operação não concluída

- **WHEN** um `GET /api/atividades` devolve uma operação `Planejada`
- **THEN** os insumos vêm com `baixado` falso e `baixa_estoque` traz `geradas`
  igual a 0 e `pendentes` vazia
