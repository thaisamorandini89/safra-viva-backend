# Lotes e validade de insumos

## Why

Os alertas de vencimento, a contagem de produtos vencidos e o bloqueio de
produto vencido das telas de Insumos só funcionam com dados de demonstração: o
backend não tem lotes. A entrada de estoque grava o número do lote e a validade
como texto solto na movimentação, e a saída não sabe de qual lote saiu.

## What Changes

### Backend
- Passa a existir o **lote de insumo**, com saldo próprio, criado ou somado pela
  entrada de estoque que informa número de lote.
- A saída de estoque passa a consumir os lotes automaticamente, pelo vencimento
  mais próximo. Lotes vencidos não são usados.
- A saída passa a ser limitada ao **saldo utilizável** (o estoque menos o que
  está em lotes vencidos).
- Cada movimentação passa a guardar e devolver de quais lotes entrou ou saiu.
- Passa a existir o **descarte de lote**: uma saída que indica o lote e pode
  retirar inclusive saldo vencido, para ele não ficar preso no estoque.
- A consulta de insumos passa a devolver os lotes de cada insumo.
- O vencimento é avaliado pela data local da aplicação.

### Frontend
- As telas de Insumos, o Início e as notificações passam a receber os lotes
  reais.
- A saída é validada pelo saldo utilizável, em vez de bloquear o produto inteiro
  quando há um lote vencido.
- O detalhe do insumo ganha a ação de descartar um lote vencido.
- Após registrar uma movimentação, os insumos são recarregados do backend.

### Fora do escopo
- Reconstruir lotes a partir de entradas antigas (as saídas antigas não dizem de
  qual lote saíram).
- Escolha manual do lote numa saída comum.
- Relatórios novos de consumo por lote.

## Capabilities

`movimentacao-estoque` ainda não está em `openspec/specs/` (vem de uma change
concluída e não arquivada); esta change só acrescenta requisitos a ela.

### New Capabilities
- `lote-insumo`: lotes de um insumo, com saldo, validade e regra de vencimento.
- `movimentacao-estoque`: saldo utilizável na saída, consumo de lotes pelo
  vencimento mais próximo, lotes de cada movimentação e descarte de lote.

### Modified Capabilities
- `insumo`: a consulta passa a devolver os lotes (requisito novo, sem alterar os
  existentes).

## Impact

- **Depende de**: `insumos-cadastro-integrado` aplicada antes, por mexerem nos
  mesmos arquivos de insumo.
- **Backend**: novos `models/lote_insumo.py` e `models/movimentacao_lote.py`;
  `services/movimentacao_service.py`, `schemas/movimentacao_schema.py`,
  `services/insumo_service.py`; a data local sai de
  `services/atividade_agricola_service.py` para um módulo compartilhado.
- **Banco**: uma migration com as tabelas `lote_insumo` e `movimentacao_lote`.
  Os dados existentes não são alterados; lotes começam vazios.
- **API**: `POST /api/movimentacoes` passa a recusar saída acima do saldo
  utilizável e entrada em lote com validade divergente, aceita `id_lote` na
  saída e devolve `lotes`; `GET /api/insumos` devolve `lotes`.
- **Frontend** (`frontendweb`): `src/services/insumosAdapter.ts` e testes,
  `src/types/insumo.ts`, `src/components/insumos/MovimentacaoForm.tsx`,
  `InsumoDetalhe.tsx`, `MovimentacoesLista.tsx` e `InsumosModule.tsx`.
