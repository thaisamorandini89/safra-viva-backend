# atividade-agricola Specification

## Purpose
Registra as operações de campo executadas em um talhão, com categoria, tipo,
responsável, período, status, custos e os insumos e máquinas utilizados.

## Requirements

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
