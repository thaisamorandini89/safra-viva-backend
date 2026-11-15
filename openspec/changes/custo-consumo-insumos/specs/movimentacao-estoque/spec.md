# movimentacao-estoque Spec Delta

## ADDED Requirements

### Requirement: Filtro do histórico por talhão

O sistema SHALL aceitar em `GET /api/movimentacoes` o filtro opcional
`id_talhao`, devolvendo apenas as movimentações com aquele talhão, manuais ou
geradas por operação, combinável com os filtros `id_insumo` e
`id_atividade_agricola`.

#### Scenario: Saídas de um talhão

- **WHEN** um `GET /api/movimentacoes?id_talhao={id}` é realizado para um
  talhão com uma saída manual e uma gerada por operação, havendo saídas em outro
  talhão
- **THEN** a resposta é HTTP 200 com as duas saídas do talhão e nenhuma outra

#### Scenario: Talhão sem saídas

- **WHEN** um `GET /api/movimentacoes?id_talhao={id}` é realizado para um
  talhão sem movimentações
- **THEN** a resposta é HTTP 200 com lista vazia

#### Scenario: Filtro combinado com insumo

- **WHEN** um `GET /api/movimentacoes?id_talhao={id}&id_insumo={id}` é
  realizado
- **THEN** a resposta traz apenas as movimentações daquele talhão e daquele
  insumo
