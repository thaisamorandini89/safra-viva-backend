# lancamento-financeiro Spec Delta

## Purpose

Registro de receitas e despesas da operação agrícola com categorias, forma de
pagamento, status, vínculos (empresa, propriedade, talhão, safra, centro de
custo), rateio de despesas entre talhões e regras de integridade histórica.

## ADDED Requirements

### Requirement: Conciliação de lançamento

O sistema SHALL permitir marcar e desmarcar a conciliação de um lançamento via
`PUT /api/lancamentos/{id}/conciliacao`, com o campo booleano `conciliado`,
devolvendo o lançamento completo. Marcar como conciliado SHALL exigir `status`
igual a `PAGO`; desfazer a conciliação SHALL ser sempre permitido.

#### Scenario: Lançamento pago conciliado

- **WHEN** um `PUT /api/lancamentos/{id}/conciliacao` é enviado com `conciliado`
  verdadeiro para um lançamento com `status` `PAGO`
- **THEN** a resposta é HTTP 200
- **AND** o lançamento passa a ser devolvido com `conciliado` verdadeiro

#### Scenario: Lançamento pendente

- **WHEN** um `PUT /api/lancamentos/{id}/conciliacao` é enviado com `conciliado`
  verdadeiro para um lançamento com `status` `PENDENTE`
- **THEN** a resposta é HTTP 400 com mensagem indicando que só lançamento pago
  pode ser conciliado
- **AND** o lançamento continua com `conciliado` falso

#### Scenario: Conciliação desfeita

- **WHEN** um `PUT /api/lancamentos/{id}/conciliacao` é enviado com `conciliado`
  falso para um lançamento conciliado
- **THEN** a resposta é HTTP 200
- **AND** o lançamento passa a ser devolvido com `conciliado` falso

#### Scenario: Valor de conciliação inválido

- **WHEN** um `PUT /api/lancamentos/{id}/conciliacao` é enviado sem `conciliado`
  ou com um valor não booleano
- **THEN** a resposta é HTTP 400
- **AND** o lançamento permanece inalterado

#### Scenario: Conciliação de lançamento inexistente

- **WHEN** um `PUT /api/lancamentos/{id}/conciliacao` é feito para um id
  inexistente
- **THEN** a resposta é HTTP 404

### Requirement: Lançamento conciliado protegido contra alteração

O sistema SHALL recusar com HTTP 400, com mensagem indicando que o lançamento
está conciliado, o `PUT /api/lancamentos/{id}` de um lançamento com `conciliado`
verdadeiro. Desfeita a conciliação, a atualização SHALL voltar a ser aceita.

#### Scenario: Edição de lançamento conciliado

- **WHEN** um `PUT /api/lancamentos/{id}` é enviado para um lançamento
  conciliado
- **THEN** a resposta é HTTP 400 com mensagem indicando que o lançamento está
  conciliado
- **AND** o lançamento e o seu rateio permanecem inalterados

#### Scenario: Edição após desfazer a conciliação

- **WHEN** a conciliação de um lançamento é desfeita e um
  `PUT /api/lancamentos/{id}` válido é enviado em seguida
- **THEN** a resposta é HTTP 200 com o lançamento atualizado
