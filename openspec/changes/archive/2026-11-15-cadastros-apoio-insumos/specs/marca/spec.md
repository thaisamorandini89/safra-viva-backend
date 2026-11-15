# marca Spec Delta

## MODIFIED Requirements

### Requirement: Exclusão de marca

O sistema SHALL permitir excluir uma marca existente via
`DELETE /api/marcas/{id_marca}` e SHALL recusar com HTTP 400, com mensagem
indicando que a marca está em uso, a exclusão de uma marca referenciada por
algum produto.

#### Scenario: Exclusão realizada com sucesso

- **WHEN** um `DELETE /api/marcas/{id_marca}` é enviado para uma marca existente
  sem produtos
- **THEN** o registro é removido da tabela `marca`
- **AND** a resposta é HTTP 200 com mensagem de sucesso

#### Scenario: Marca usada por produto

- **WHEN** um `DELETE /api/marcas/{id_marca}` é enviado para uma marca
  referenciada por um produto
- **THEN** a resposta é HTTP 400 com mensagem indicando que a marca está em uso
- **AND** a marca continua cadastrada

#### Scenario: Exclusão de marca inexistente

- **WHEN** um `DELETE /api/marcas/{id_marca}` é enviado para um id inexistente
- **THEN** nenhuma exclusão é realizada
- **AND** a resposta é HTTP 404 com mensagem de marca não encontrada
