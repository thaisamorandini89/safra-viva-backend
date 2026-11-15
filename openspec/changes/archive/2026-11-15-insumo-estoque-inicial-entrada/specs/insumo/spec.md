# insumo Spec Delta

## ADDED Requirements

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

## MODIFIED Requirements

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
