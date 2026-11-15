# insumo Spec Delta

## ADDED Requirements

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
