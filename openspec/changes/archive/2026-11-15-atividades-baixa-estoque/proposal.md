# Baixa de estoque ao concluir a atividade

## Why

A lista "Insumos Utilizados" da atividade e o estoque não conversam: a lista não
mexe no saldo, e a saída de estoque vinculada à operação não aparece na
atividade. Para o estoque refletir o que foi aplicado, o usuário precisa lançar
o mesmo consumo duas vezes.

## What Changes

### Backend
- Ao salvar uma atividade como `Concluída`, o sistema gera uma saída de estoque
  para cada insumo listado com quantidade, vinculada à operação e datada no
  término da atividade.
- Se faltar saldo utilizável para um insumo, a atividade é concluída assim
  mesmo: esse insumo fica sem baixa, os demais são baixados, e a resposta avisa
  quais ficaram pendentes. Não há baixa parcial de um insumo.
- Ao reabrir, alterar ou excluir uma atividade concluída, as saídas geradas por
  ela são desfeitas e o saldo volta ao estoque e aos lotes. Se a atividade
  continuar concluída, as saídas são geradas de novo conforme a lista atual, o
  que também tenta de novo os insumos pendentes.
- As saídas lançadas à mão e vinculadas à operação não mudam.
- A movimentação passa a informar a origem (`MANUAL` ou `ATIVIDADE`), e o
  histórico pode ser filtrado por operação.
- A atividade passa a informar, por insumo, se foi baixado, e a lista de
  pendentes.

### Frontend
- O formulário de atividade mostra o saldo disponível de cada insumo e avisa que
  concluir gera a baixa.
- Depois de salvar, a tela avisa quais insumos ficaram sem baixa.
- O detalhe da atividade mostra a situação de cada insumo e as saídas de estoque
  ligadas à operação, automáticas e manuais.
- O histórico de movimentações identifica as saídas automáticas.
- Estoque e histórico são recarregados depois de salvar ou excluir uma
  atividade.

### Fora do escopo
- Baixa parcial (retirar só parte da quantidade de um insumo).
- Estorno com lançamento de contrapartida: a saída desfeita some do histórico.
- Cálculo automático do custo do insumo na atividade.
- Impedir que o mesmo consumo seja lançado à mão e também pela lista da
  atividade.

## Capabilities

`atividade-agricola` e `movimentacao-estoque` ainda não estão em
`openspec/specs/` (vêm de changes concluídas e não arquivadas); esta change só
acrescenta requisitos a elas.

### New Capabilities
- `atividade-agricola`: baixa de estoque ao concluir, insumo sem saldo
  suficiente, devolução ao alterar operação concluída e situação da baixa na
  resposta.
- `movimentacao-estoque`: origem da movimentação, filtro do histórico por
  operação e preservação das saídas manuais na devolução.

### Modified Capabilities

Nenhuma capacidade de `openspec/specs/` tem requisito alterado.

## Impact

- **Depende de**: `insumos-lotes-validade` aplicada antes (saldo utilizável,
  consumo por lote e registro dos lotes de cada movimentação).
- **Backend**: `services/atividade_agricola_service.py`,
  `services/movimentacao_service.py`, `models/movimentacao_estoque.py`,
  `models/atividade_insumo.py`, `controllers/movimentacao_controller.py`.
- **Banco**: uma migration que adiciona `movimentacao_estoque.origem` e
  `atividade_insumo.id_movimentacao`. Movimentações existentes ficam como
  `MANUAL`.
- **API**: `POST`, `PUT` e `DELETE /api/atividades` passam a movimentar estoque
  quando a atividade está concluída; as respostas de atividade e de movimentação
  ganham campos; `GET /api/movimentacoes` aceita `id_atividade_agricola`.
- **Frontend** (`frontendweb`): `src/types/atividade.ts`, `src/types/insumo.ts`,
  `src/services/api.ts`, `src/services/insumosAdapter.ts` e testes,
  `src/components/atividades/AtividadeForm.tsx`, `AtividadeDetalhe.tsx`,
  `AtividadesModule.tsx` e `src/components/insumos/MovimentacoesLista.tsx`.
