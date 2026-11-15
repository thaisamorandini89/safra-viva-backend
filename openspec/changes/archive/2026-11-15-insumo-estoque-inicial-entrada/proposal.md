# Estoque inicial do insumo registrado como entrada

## Why

O "Estoque Inicial" informado no cadastro do insumo é gravado direto no saldo,
sem movimentação e sem lote. O histórico do insumo não explica de onde veio esse
saldo, ele nunca entra nos alertas de vencimento e não pode ser descartado como
vencido.

## What Changes

### Backend
- O cadastro de insumo com estoque inicial maior que zero passa a registrar, na
  mesma transação, uma entrada de estoque com essa quantidade.
- O cadastro passa a aceitar os dados dessa entrada: número do lote, datas de
  fabricação e validade e responsável, todos opcionais. Com número de lote, o
  lote é criado como em qualquer entrada.
- Essa entrada é identificada pela origem `CADASTRO`, ao lado de `MANUAL` e
  `ATIVIDADE`.
- Um insumo cuja única movimentação é a entrada do estoque inicial pode ser
  excluído; a entrada e o lote são removidos junto. Com qualquer outra
  movimentação, a exclusão continua recusada.
- Dados de entrada sem estoque inicial, estoque inicial negativo e dados
  inválidos são recusados sem criar nada.

### Frontend
- O formulário de "Novo Insumo" passa a pedir, quando há estoque inicial, o
  responsável (obrigatório) e, opcionalmente, lote, fabricação e validade.
- O histórico de movimentações identifica essa entrada como "Estoque inicial" e
  é recarregado depois do cadastro.

### Fora do escopo
- Gerar entrada para o saldo de insumos já cadastrados antes desta change.
- Impedir a alteração direta de `estoque_atual` por `PUT /api/insumos`, que a
  tela não usa.
- Guardar o lote do estoque inicial no modo de demonstração (backend fora do
  ar).

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities
- `insumo`: requisito novo para o estoque inicial registrado como entrada;
  "Exclusão de insumo" passa a permitir excluir o insumo que só tem a entrada do
  estoque inicial.
- `movimentacao-estoque`: "Origem da movimentação" ganha o valor `CADASTRO`.

## Impact

- **Backend**: `services/insumo_service.py` (criação e exclusão),
  `controllers/insumo_controller.py` (erros de validação da entrada). Reusa a
  aplicação de movimentação de `services/movimentacao_service.py`.
- **Banco**: sem migration; `movimentacao_estoque.origem` já comporta o valor
  novo.
- **API**: `POST /api/insumos` aceita `entrada_inicial` e passa a recusar
  estoque inicial negativo; `DELETE /api/insumos/{id}` passa a aceitar o insumo
  que só tem a entrada inicial; movimentações podem vir com `origem` igual a
  `CADASTRO`.
- **Frontend** (`frontendweb`): `src/types/insumo.ts`,
  `src/services/insumosAdapter.ts` e testes,
  `src/components/insumos/InsumoForm.tsx`, `InsumosModule.tsx`,
  `InsumoDetalhe.tsx` e `MovimentacoesLista.tsx`.
