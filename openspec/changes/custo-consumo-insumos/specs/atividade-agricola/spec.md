# atividade-agricola Spec Delta

## ADDED Requirements

### Requirement: Custo calculado do insumo da operação

Ao gravar uma operação via `POST /api/atividades` ou `PUT /api/atividades/{id}`
com a lista de `insumos`, o sistema SHALL calcular o `custo` de cada item que
tenha `quantidade` maior que zero e `custo` ausente ou nulo, como `quantidade`
multiplicada pelo `valor_unitario` do insumo naquele momento, arredondado em
duas casas. Um `custo` informado, inclusive zero, SHALL ser mantido. Quando o
insumo não tiver `valor_unitario` maior que zero, o `custo` do item SHALL ficar
nulo. Itens já gravados SHALL NOT ser recalculados sem uma nova gravação da
lista de insumos.

#### Scenario: Custo calculado

- **WHEN** um `POST /api/atividades` inclui um insumo com `valor_unitario` 12,50
  e um item com `quantidade` 3 sem `custo`
- **THEN** a resposta é HTTP 201 com o `custo` do item igual a 37,50
- **AND** o `custo_total` da operação inclui esse valor quando não há
  `custo_operacao`

#### Scenario: Custo informado mantido

- **WHEN** um `POST /api/atividades` inclui um item com `quantidade` 3 e `custo`
  20
- **THEN** a resposta é HTTP 201 com o `custo` do item igual a 20

#### Scenario: Custo zero informado

- **WHEN** um `POST /api/atividades` inclui um item com `quantidade` 3 e `custo`
  0
- **THEN** a resposta é HTTP 201 com o `custo` do item igual a 0

#### Scenario: Insumo sem valor unitário

- **WHEN** um `POST /api/atividades` inclui, sem `custo`, um item de um insumo
  com `valor_unitario` zero
- **THEN** a resposta é HTTP 201 com o `custo` do item nulo

#### Scenario: Item sem quantidade

- **WHEN** um `POST /api/atividades` inclui um item sem `quantidade` e sem
  `custo`
- **THEN** a resposta é HTTP 201 com o `custo` do item nulo

#### Scenario: Recalculado ao gravar de novo

- **WHEN** o `valor_unitario` do insumo muda e um `PUT /api/atividades/{id}`
  reenvia a lista de insumos com o item sem `custo`
- **THEN** o `custo` do item passa a usar o valor unitário novo

#### Scenario: Atualização sem a lista de insumos

- **WHEN** o `valor_unitario` do insumo muda e um `PUT /api/atividades/{id}` é
  enviado sem `insumos`
- **THEN** o `custo` dos itens da operação permanece o mesmo
