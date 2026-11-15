# insumo Specification

## Purpose
TBD - created by archiving change insumo-spec-e-fix-serializacao. Update Purpose after archive.

## Requirements

### Requirement: Estrutura da entidade Insumo

O sistema SHALL representar o insumo como item de estoque vinculado a um produto,
na tabela `insumo`, com `id_insumo` (PK), `id_produto` (FK obrigatória para
`produto.id_produto`), `estoque_atual` (numérico 14,3 obrigatório, padrão 0),
`estoque_minimo` e `valor_unitario` (numéricos opcionais, padrão 0),
`id_propriedade` (FK opcional para `propriedade.id_propriedade`), `status`
(booleano, padrão verdadeiro) e `data_cadastro` (preenchida pelo banco).

Os dados comerciais (nome, categoria, unidade de medida, fabricante e marca)
SHALL permanecer no produto, nunca duplicados no insumo.

#### Scenario: Insumo persistido com vínculo obrigatório

- **WHEN** um insumo é criado
- **THEN** ele referencia obrigatoriamente um produto existente
- **AND** os valores numéricos não informados são gravados como 0

#### Scenario: Insumo sem propriedade

- **WHEN** um insumo é criado sem `id_propriedade`
- **THEN** ele é persistido com `id_propriedade` nulo

### Requirement: Cadastro de insumo

O sistema SHALL permitir cadastrar insumos via `POST /api/insumos`, exigindo
`id_produto` válido ou um objeto `produto` com os dados de um produto novo, e
aceitando `estoque_atual`, `estoque_minimo`, `valor_unitario`,
`id_propriedade` e `status` opcionais. Quando `produto` for informado, o sistema SHALL
criar o produto e o insumo na mesma transação, aplicando ao produto as mesmas
validações do cadastro de produtos. A resposta SHALL trazer o insumo completo,
no formato da consulta.

#### Scenario: Cadastro realizado com sucesso

- **WHEN** um `POST /api/insumos` é enviado com `id_produto` existente
- **THEN** o insumo é persistido
- **AND** a resposta é HTTP 201 contendo `id_insumo` e `id_produto`

#### Scenario: Cadastro com produto novo

- **WHEN** um `POST /api/insumos` é enviado sem `id_produto` e com `produto`
  contendo nome, categoria e unidade de medida válidos
- **THEN** o produto e o insumo são persistidos, com o insumo vinculado ao
  produto criado
- **AND** a resposta é HTTP 201 com o insumo completo, incluindo os dados do
  produto

#### Scenario: Produto novo inválido

- **WHEN** um `POST /api/insumos` é enviado com `produto` sem nome, sem
  categoria, sem unidade de medida ou com categoria, fabricante, marca ou
  fornecedor inexistente
- **THEN** nem o produto nem o insumo são criados
- **AND** a resposta é HTTP 400 com a mensagem de erro correspondente

#### Scenario: Produto ausente ou inexistente

- **WHEN** um `POST /api/insumos` é enviado sem `id_produto` e sem `produto`, ou
  com um `id_produto` inexistente
- **THEN** nenhum insumo é criado
- **AND** a resposta é HTTP 400 com a mensagem de erro correspondente

#### Scenario: Produto informado das duas formas

- **WHEN** um `POST /api/insumos` é enviado com `id_produto` e `produto` ao
  mesmo tempo
- **THEN** nada é criado
- **AND** a resposta é HTTP 400

#### Scenario: Propriedade inexistente

- **WHEN** um `POST /api/insumos` é enviado com `id_propriedade` inexistente
- **THEN** nada é criado
- **AND** a resposta é HTTP 400

#### Scenario: Insumo cadastrado inativo

- **WHEN** um `POST /api/insumos` é enviado com `status` falso
- **THEN** o insumo é persistido com `status` falso
- **AND** sem `status` no payload o insumo é persistido como ativo

#### Scenario: Valor numérico inválido

- **WHEN** um campo numérico é enviado com um valor não conversível
- **THEN** a operação é rejeitada
- **AND** a resposta é HTTP 400 indicando o campo inválido

### Requirement: Consulta de insumos com dados do produto

O sistema SHALL retornar, em `GET /api/insumos` e `GET /api/insumos/{id_insumo}`,
os dados de estoque do insumo enriquecidos com os dados do produto vinculado:
`nome_produto`, `id_categoria_insumo`, `categoria_nome`, `subcategoria`,
`unidade_medida`, `id_fabricante`, `fabricante_nome`, `id_marca`,
`descricao_marca`, `id_fornecedor`, `fornecedor_nome`, `registro_mapa`,
`ficha_tecnica` e `observacoes`, além de `id_propriedade` e `nome_propriedade`
do insumo.

Os valores relacionados SHALL ser resolvidos a partir das chaves estrangeiras do
produto e do insumo, nunca de atributos de texto inexistentes no modelo.

#### Scenario: Listagem com produto completo

- **WHEN** um `GET /api/insumos` é realizado e existem insumos cadastrados
- **THEN** a resposta é HTTP 200
- **AND** cada item traz os dados de estoque e os dados do produto vinculado,
  incluindo o nome do fabricante e a descrição da marca

#### Scenario: Produto sem fabricante ou sem marca

- **WHEN** o produto vinculado não possui fabricante e/ou marca
- **THEN** a resposta é HTTP 200
- **AND** os ids correspondentes são nulos e os nomes retornam vazios,
  sem erro de servidor

#### Scenario: Dados complementares e propriedade

- **WHEN** um `GET /api/insumos/{id_insumo}` é feito para um insumo com
  propriedade cujo produto tem subcategoria, fornecedor e registro MAPA
- **THEN** a resposta traz `subcategoria`, `id_fornecedor`, `fornecedor_nome`,
  `registro_mapa`, `id_propriedade` e `nome_propriedade` preenchidos

#### Scenario: Insumo inexistente

- **WHEN** um `GET /api/insumos/{id_insumo}` é feito para um id inexistente
- **THEN** a resposta é HTTP 404 com mensagem de insumo não encontrado

### Requirement: Atualização de insumo

O sistema SHALL permitir atualização parcial via
`PUT /api/insumos/{id_insumo}`, alterando apenas os campos presentes no payload
e validando o produto quando `id_produto` for informado. Quando o payload
trouxer o objeto `produto`, o sistema SHALL atualizar, na mesma transação, os
campos informados do produto vinculado, com as validações do cadastro de
produtos. A resposta SHALL trazer o insumo completo, no formato da consulta.

#### Scenario: Atualização parcial

- **WHEN** um `PUT /api/insumos/{id_insumo}` é enviado com apenas alguns campos
- **THEN** somente os campos enviados são alterados
- **AND** a resposta é HTTP 200

#### Scenario: Atualização dos dados do produto

- **WHEN** um `PUT /api/insumos/{id_insumo}` é enviado com `produto` contendo
  nome, fabricante ou outro dado comercial
- **THEN** o produto vinculado é atualizado com os campos enviados
- **AND** a resposta é HTTP 200 com o insumo completo já refletindo a alteração

#### Scenario: Dado de produto inválido

- **WHEN** um `PUT /api/insumos/{id_insumo}` é enviado com `produto` contendo
  nome vazio ou fabricante, marca, fornecedor ou categoria inexistente
- **THEN** nem o insumo nem o produto são alterados
- **AND** a resposta é HTTP 400

#### Scenario: Atualização de insumo inexistente

- **WHEN** um `PUT /api/insumos/{id_insumo}` é feito para um id inexistente
- **THEN** a resposta é HTTP 404

### Requirement: Exclusão de insumo

O sistema SHALL permitir excluir um insumo via `DELETE /api/insumos/{id_insumo}`,
mantendo o produto vinculado. O sistema SHALL recusar com HTTP 400, com mensagem
indicando que o insumo está em uso, a exclusão de um insumo que possua
movimentações de estoque além da entrada do estoque inicial ou conste na lista
de insumos de alguma atividade agrícola. Quando a única movimentação do insumo
for a entrada do estoque inicial, a exclusão SHALL remover também essa entrada
e o lote criado por ela.

#### Scenario: Exclusão realizada

- **WHEN** um `DELETE /api/insumos/{id_insumo}` é feito para um insumo existente
  e sem uso
- **THEN** o registro é removido
- **AND** a resposta é HTTP 200 com mensagem de sucesso
- **AND** o produto vinculado continua cadastrado

#### Scenario: Insumo só com o estoque inicial

- **WHEN** um `DELETE /api/insumos/{id_insumo}` é feito para um insumo cuja
  única movimentação é a entrada do estoque inicial, registrada em um lote
- **THEN** a resposta é HTTP 200
- **AND** o insumo, a entrada e o lote são removidos
- **AND** o produto vinculado continua cadastrado

#### Scenario: Insumo com movimentações

- **WHEN** um `DELETE /api/insumos/{id_insumo}` é feito para um insumo que possui
  alguma movimentação de estoque que não seja a entrada do estoque inicial
- **THEN** a resposta é HTTP 400 com mensagem indicando que o insumo está em uso
- **AND** o insumo e todas as suas movimentações continuam cadastrados

#### Scenario: Insumo usado em atividade

- **WHEN** um `DELETE /api/insumos/{id_insumo}` é feito para um insumo que consta
  na lista de insumos de uma atividade agrícola
- **THEN** a resposta é HTTP 400 e o insumo continua cadastrado

#### Scenario: Exclusão de insumo inexistente

- **WHEN** um `DELETE /api/insumos/{id_insumo}` é feito para um id inexistente
- **THEN** a resposta é HTTP 404

### Requirement: Saldo atualizado por movimentação

O `estoque_atual` do insumo SHALL ser atualizado automaticamente pelo registro
de movimentações de estoque (ENTRADA soma, SAIDA subtrai), na mesma transação
do registro da movimentação.

#### Scenario: Saldo reflete a movimentação

- **WHEN** uma movimentação é registrada com sucesso para um insumo
- **THEN** o `estoque_atual` retornado em `GET /api/insumos/{id_insumo}`
  reflete o novo saldo

### Requirement: Lotes na consulta de insumos

O sistema SHALL incluir, em cada insumo devolvido por `GET /api/insumos` e
`GET /api/insumos/{id_insumo}`, a lista `lotes` com `id_lote`, `numero_lote`,
`data_fabricacao`, `data_validade` e `quantidade` de cada lote do insumo,
ordenada pela validade mais próxima, e vazia quando o insumo não tiver lotes.

#### Scenario: Insumo com lotes

- **WHEN** um `GET /api/insumos/{id_insumo}` é feito para um insumo que recebeu
  entradas em dois lotes
- **THEN** a resposta traz `lotes` com os dois lotes, seus saldos e validades,
  começando pelo que vence primeiro

#### Scenario: Insumo sem lotes

- **WHEN** um `GET /api/insumos` devolve um insumo que nunca recebeu entrada com
  número de lote
- **THEN** o item traz `lotes` como lista vazia

### Requirement: Estoque inicial registrado como entrada

Quando o cadastro informar `estoque_atual` maior que zero, o sistema SHALL
registrar, na mesma transação, uma movimentação de ENTRADA com essa quantidade
e origem `CADASTRO`, datada no dia corrente da aplicação, com o valor unitário
do insumo e o fornecedor do produto. O cadastro SHALL aceitar o objeto opcional
`entrada_inicial`, com `numero_lote`, `data_fabricacao`, `data_validade` e
`id_funcionario`, aplicados a essa entrada.

#### Scenario: Cadastro com estoque inicial

- **WHEN** um `POST /api/insumos` é enviado com `estoque_atual` igual a 100
- **THEN** a resposta é HTTP 201 com `estoque_atual` igual a 100
- **AND** `GET /api/movimentacoes?id_insumo={id}` devolve uma única ENTRADA de
  100, com `origem` igual a `CADASTRO`, a data local corrente e o valor
  unitário do insumo

#### Scenario: Estoque inicial em lote

- **WHEN** um `POST /api/insumos` é enviado com `estoque_atual` maior que zero e
  `entrada_inicial` contendo `numero_lote` e `data_validade`
- **THEN** o insumo é devolvido com `lotes` contendo esse lote, com saldo igual
  ao estoque inicial e a validade informada
- **AND** a entrada registrada traz esse lote em `lotes`

#### Scenario: Responsável da entrada inicial

- **WHEN** um `POST /api/insumos` é enviado com `estoque_atual` maior que zero e
  `entrada_inicial.id_funcionario` de um funcionário existente
- **THEN** a entrada registrada traz esse funcionário como responsável

#### Scenario: Cadastro sem estoque inicial

- **WHEN** um `POST /api/insumos` é enviado sem `estoque_atual` ou com
  `estoque_atual` igual a zero, e sem `entrada_inicial`
- **THEN** o insumo é criado com `estoque_atual` igual a zero
- **AND** nenhuma movimentação é registrada

#### Scenario: Dados de entrada sem estoque inicial

- **WHEN** um `POST /api/insumos` é enviado com `entrada_inicial` contendo
  `numero_lote` ou datas, e `estoque_atual` ausente ou igual a zero
- **THEN** a resposta é HTTP 400
- **AND** nada é criado

#### Scenario: Entrada inicial inválida

- **WHEN** um `POST /api/insumos` é enviado com `estoque_atual` negativo, com
  `data_validade` anterior à `data_fabricacao` ou com `id_funcionario`
  inexistente
- **THEN** a resposta é HTTP 400
- **AND** nem o produto, nem o insumo, nem a movimentação, nem o lote são
  criados
