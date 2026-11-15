# Safra unificada

## Why

A safra é um cadastro no Financeiro, mas um texto digitado em atividades e em
movimentações de estoque. "2025/2026" numa atividade não é a mesma coisa que a
safra cadastrada onde os lançamentos são vinculados, então não dá para apurar,
por safra, o que foi feito, o que foi consumido e o que foi gasto.

## What Changes

### Backend
- Atividades e saídas de estoque passam a guardar a safra cadastrada
  (`id_safra`), validando que ela existe e que é da mesma propriedade.
- As respostas passam a trazer `id_safra`; o campo `safra` continua existindo e
  mostra o nome da safra cadastrada.
- Os registros que já têm safra em texto mantêm esse texto até que alguém
  escolha uma safra cadastrada neles.
- A saída gerada ao concluir uma atividade leva a safra da atividade. A saída
  manual vinculada a uma atividade herda a safra dela e não aceita outra.
- As atividades podem ser filtradas pela safra cadastrada.
- A safra usada por atividade ou movimentação não pode ser excluída.

### Frontend
- No formulário de atividade e no de saída de estoque, o campo de safra deixa de
  ser texto livre e passa a ser um combo das safras cadastradas da propriedade
  do talhão.
- Num registro antigo, a tela mostra a safra que estava em texto e a mantém se
  nada for escolhido.
- Sem safras cadastradas, o combo orienta o cadastro em Financeiro › Safras.

### Fora do escopo
- Converter automaticamente os textos antigos em safras cadastradas.
- Impedir, na API, a gravação de safra em texto quando `id_safra` não é
  informado; as telas é que deixam de enviar texto.
- Levar o custo das atividades aos indicadores financeiros por safra.
- Vincular talhões a safras.

## Capabilities

`safra` ainda não está em `openspec/specs/`: vem das changes `financeiro` e
`financeiro-ponta-a-ponta`. Esta change só acrescenta um requisito a ela.

### New Capabilities
- `safra`: exclusão recusada quando a safra é usada por atividade ou
  movimentação.

### Modified Capabilities
- `atividade-agricola`: requisitos novos para a safra cadastrada na operação, a
  mesma propriedade, a preservação do texto antigo e o filtro por safra.
- `movimentacao-estoque`: requisitos novos para a safra cadastrada na saída e a
  coerência dela com o talhão e a operação.

## Impact

- **Depende de**: `financeiro-ponta-a-ponta` aplicada antes (telas de cadastro
  de safra, safras reais nas consultas e exclusão de safra). Para arquivar,
  `financeiro` e `financeiro-ponta-a-ponta` precisam ser arquivadas antes.
- **Backend**: `models/atividade_agricola.py`, `models/movimentacao_estoque.py`,
  `schemas/atividade_schema.py`, `schemas/movimentacao_schema.py`,
  `services/atividade_agricola_service.py`, `services/movimentacao_service.py`,
  `services/safra_service.py` e `controllers/atividade_agricola_controller.py`.
- **Banco**: uma migration que adiciona `id_safra` a `atividade_agricola` e a
  `movimentacao_estoque`. Os dados existentes não são alterados.
- **API**: `POST` e `PUT /api/atividades` e `POST /api/movimentacoes` aceitam
  `id_safra`; as respostas ganham `id_safra`; `GET /api/atividades` aceita o
  filtro `id_safra`; `DELETE /api/safras/{id}` passa a recusar a safra usada por
  atividade ou movimentação.
- **Frontend** (`frontendweb`): `src/types/atividade.ts`, `src/types/insumo.ts`,
  `src/services/api.ts`, `src/services/insumosAdapter.ts` e testes,
  `src/components/atividades/AtividadeForm.tsx` e
  `src/components/insumos/MovimentacaoForm.tsx`.
