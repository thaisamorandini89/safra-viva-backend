# Spec Delta

## Purpose

Visões de agregação sobre os lançamentos financeiros — saldo, fluxo de caixa e
indicadores de rentabilidade (KPIs) por safra, talhão e cultura — para apoiar
decisões do produtor rural.

## ADDED Requirements

### Requirement: Saldo financeiro

O sistema SHALL expor `GET /api/financeiro/saldo` calculando o saldo como a soma
das receitas menos a soma das despesas, com filtros opcionais por período,
propriedade e safra.

#### Scenario: Cálculo do saldo

- **WHEN** um `GET /api/financeiro/saldo` é realizado
- **THEN** a resposta é HTTP 200 com `receita_total`, `despesa_total` e
  `saldo` (receita_total − despesa_total)

#### Scenario: Saldo filtrado por safra

- **WHEN** um `GET /api/financeiro/saldo?id_safra={id}` é realizado
- **THEN** a resposta é HTTP 200 considerando apenas lançamentos daquela safra

### Requirement: Fluxo de caixa

O sistema SHALL expor `GET /api/financeiro/fluxo-caixa` retornando, por período,
os lançamentos com data, descrição, entrada, saída e saldo acumulado, ordenados
por data crescente.

#### Scenario: Fluxo de caixa por período

- **WHEN** um `GET /api/financeiro/fluxo-caixa?data_inicio={d1}&data_fim={d2}`
  é realizado
- **THEN** a resposta é HTTP 200 com itens contendo data, descrição, entrada,
  saída e saldo acumulado em ordem crescente de data

#### Scenario: Saldo acumulado

- **WHEN** o fluxo de caixa contém múltiplos lançamentos
- **THEN** o saldo de cada item reflete o acumulado dos lançamentos anteriores
  mais o atual

### Requirement: Indicadores de rentabilidade

O sistema SHALL expor `GET /api/financeiro/indicadores` retornando KPIs
financeiros — receita total, despesa total, lucro líquido, margem líquida e ROI
— com agregação por safra, por talhão ou por cultura conforme o parâmetro
`agrupar_por`.

#### Scenario: Indicadores por safra

- **WHEN** um `GET /api/financeiro/indicadores?agrupar_por=safra` é realizado
- **THEN** a resposta é HTTP 200 com, para cada safra, receita total, despesa
  total, lucro líquido, margem líquida e ROI

#### Scenario: Indicadores por cultura

- **WHEN** um `GET /api/financeiro/indicadores?agrupar_por=cultura` é realizado
- **THEN** a resposta é HTTP 200 com os KPIs agregados por cultura

#### Scenario: Agrupamento inválido

- **WHEN** um `GET /api/financeiro/indicadores?agrupar_por={valor}` usa um valor
  fora de {safra, talhao, cultura}
- **THEN** a resposta é HTTP 400

### Requirement: Custo e receita por hectare

O sistema SHALL calcular custo por hectare, receita por hectare e lucro por
hectare quando houver área disponível (da safra ou do talhão), dividindo os
valores agregados pela área correspondente.

#### Scenario: Custo por hectare com área disponível

- **WHEN** um `GET /api/financeiro/indicadores?agrupar_por=talhao` é realizado
  para talhões com área informada
- **THEN** cada item inclui `custo_por_hectare`, `receita_por_hectare` e
  `lucro_por_hectare`

#### Scenario: Área ausente

- **WHEN** a área correspondente é nula ou zero
- **THEN** os indicadores por hectare são retornados como nulos, sem erro de
  divisão
