# Cadastro de insumo integrado ao backend

## Why

A tela "Novo Insumo" não chega ao backend: ela envia nome, categoria e demais
dados num único formato, o backend exige um produto já cadastrado, recusa o
pedido, e a tela guarda o insumo só na memória, perdendo-o ao recarregar. Além
disso a tela não tem como editar nem excluir, usa texto livre para fabricante,
marca e fornecedor, e pede uma propriedade que o backend não guarda.

## What Changes

### Backend
- `POST /api/insumos` passa a aceitar os dados de um produto novo no objeto
  `produto`, criando produto e insumo na mesma transação. `id_produto` continua
  aceito para vincular a um produto existente.
- `PUT /api/insumos/{id}` passa a aceitar `produto` para atualizar os dados
  comerciais do produto vinculado junto com os dados de estoque.
- Criação e atualização passam a devolver o insumo completo, no formato da
  consulta.
- A consulta de insumos passa a devolver subcategoria, fornecedor, registro
  MAPA, ficha técnica, observações e propriedade.
- O insumo ganha a propriedade (`id_propriedade`, opcional).
- Excluir um insumo com movimentações de estoque ou usado em atividades passa a
  responder HTTP 400 com mensagem clara, em vez de erro 500.

### Frontend
- O formulário de insumo passa a gravar no backend, com combos de fabricante,
  marca e fornecedor vindos dos cadastros, e ganha modo de edição.
- A lista e o detalhe ganham as ações de editar e excluir.
- Erros devolvidos pelo backend aparecem para o usuário; o registro local de
  demonstração só vale quando o backend está fora do ar.

### Fora do escopo
- Telas de cadastro de produto, fabricante, marca e fornecedor.
- Reaproveitar os produtos que hoje existem sem insumo, e impedir produtos com
  nome repetido.
- Lotes e validade (change `insumos-lotes-validade`).
- O script `scripts/seed-insumos.mjs` do frontend.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities
- `insumo`: a estrutura ganha a propriedade; o cadastro aceita o produto junto;
  a consulta devolve mais dados do produto e a propriedade; a atualização
  alcança o produto vinculado; a exclusão é recusada quando o insumo está em
  uso.

## Impact

- **Backend**: `models/insumo.py`, `services/insumo_service.py`,
  `services/produto_service.py` (montagem do produto reaproveitada),
  `controllers/insumo_controller.py`.
- **Banco**: uma migration que adiciona `insumo.id_propriedade` (FK opcional).
- **API**: `POST` e `PUT /api/insumos` aceitam campos novos e devolvem mais
  dados; `DELETE /api/insumos/{id}` passa a responder 400 quando em uso. Nenhuma
  rota é removida.
- **Frontend** (`frontendweb`): `src/services/insumosAdapter.ts` e seus testes,
  `src/services/api.ts`, `src/types/insumo.ts`,
  `src/components/insumos/InsumoForm.tsx`, `InsumosLista.tsx`,
  `InsumoDetalhe.tsx` e `InsumosModule.tsx`.
