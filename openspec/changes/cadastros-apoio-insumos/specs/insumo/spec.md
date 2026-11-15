# insumo Spec Delta

## ADDED Requirements

### Requirement: Um insumo por produto

O sistema SHALL recusar com HTTP 400, com mensagem indicando que o produto já
tem insumo, o cadastro de insumo via `POST /api/insumos` com um `id_produto` já
vinculado a outro insumo. A atualização de um insumo SHALL recusar da mesma
forma a troca para um `id_produto` já vinculado a outro insumo.

#### Scenario: Produto existente sem insumo

- **WHEN** um `POST /api/insumos` é enviado com o `id_produto` de um produto sem
  insumo
- **THEN** a resposta é HTTP 201 com o insumo vinculado ao produto
- **AND** nenhum produto novo é criado

#### Scenario: Produto que já tem insumo

- **WHEN** um `POST /api/insumos` é enviado com o `id_produto` de um produto que
  já tem insumo
- **THEN** a resposta é HTTP 400 com mensagem indicando que o produto já tem
  insumo
- **AND** nenhum insumo é criado

#### Scenario: Troca para produto que já tem insumo

- **WHEN** um `PUT /api/insumos/{id_insumo}` é enviado com o `id_produto` de um
  produto vinculado a outro insumo
- **THEN** a resposta é HTTP 400
- **AND** o insumo permanece inalterado
