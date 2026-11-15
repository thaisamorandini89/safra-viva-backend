# Custo e consumo de insumos

## Why

Na atividade agrícola, o custo de cada insumo é digitado à mão, embora o insumo
tenha valor unitário cadastrado. Quando ninguém digita, a atividade fica sem o
custo dos insumos, e o custo total e os indicadores de atividades saem menores
do que deveriam. Além disso, a tela do talhão mostra só o histórico de safras:
não há como ver quais insumos foram aplicados nele, embora cada saída de estoque
guarde o talhão.

## What Changes

### Backend
- Ao salvar uma atividade, o insumo com quantidade e sem custo informado recebe
  custo calculado: quantidade × valor unitário cadastrado no insumo. Custo
  informado, inclusive zero, é mantido. Atividades já gravadas só mudam quando
  forem salvas de novo.
- `GET /api/movimentacoes` passa a aceitar o filtro `id_talhao`.

### Frontend
- No formulário de atividade, o custo do insumo é preenchido ao escolher o
  insumo e a quantidade, com a indicação de que foi calculado. Digitar um valor
  substitui o cálculo; apagar o valor volta ao cálculo.
- O detalhe do talhão ganha a seção "Insumos aplicados": data, insumo,
  quantidade, valor, safra e atividade de origem de cada saída do talhão, com o
  total gasto.

### Fora do escopo
- Custo médio a partir das entradas: o valor unitário do insumo continua sendo o
  do cadastro.
- Custo das atividades nos indicadores do Financeiro e custo por hectare do
  talhão.
- Máquinas: o custo da máquina continua digitado.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities
- `atividade-agricola`: o custo do insumo da operação passa a ser calculado
  quando não informado.
- `movimentacao-estoque`: o histórico passa a ser filtrável por talhão.

## Impact

- **Depende de**: nada obrigatório. Recomendado aplicar depois de
  `safra-unificada`, que mexe no mesmo formulário de atividade e faz a safra
  cadastrada aparecer nas saídas.
- **Backend**: `services/atividade_agricola_service.py`,
  `services/movimentacao_service.py`, `controllers/movimentacao_controller.py`,
  `insomnia_safraviva.json`.
- **Banco**: sem migration.
- **API**: `POST` e `PUT /api/atividades` passam a devolver `custo` preenchido
  nos insumos sem custo informado; `GET /api/movimentacoes` aceita `id_talhao`.
- **Frontend** (`frontendweb`): `src/components/atividades/AtividadeForm.tsx`,
  `src/components/talhoes/TalhaoDetalhe.tsx`, `src/services/api.ts` e testes.
