# Design

## Context

Motivação e escopo em `proposal.md`. O que condiciona o desenho:

- A operação guarda seus insumos em `atividade_insumo` (insumo, quantidade,
  custo). No `PUT`, a lista enviada substitui a anterior.
- A movimentação já aceita `id_atividade_agricola` e, com a change
  `insumos-lotes-validade`, limita a saída ao saldo utilizável, consome lotes
  pelo vencimento e registra os lotes afetados.
- Hoje o registro de movimentação faz o próprio `commit` e só é chamado pelo
  controller de movimentações.
- Excluir uma operação mantém as saídas vinculadas, apenas removendo o vínculo
  (`ON DELETE SET NULL`). Essa regra foi definida para saídas lançadas à mão.
- Decisões já tomadas com a usuária: a falta de saldo não impede a conclusão; ao
  reabrir, alterar ou excluir, o saldo volta ao estoque.

## Goals / Non-Goals

**Goals:**
- A operação e suas saídas são gravadas ou desfeitas juntas, numa transação.
- Uma regra única cobre concluir, reabrir, alterar e tentar de novo.
- Saídas manuais nunca são tocadas pela automação.

**Non-Goals:**
- Baixa parcial de um insumo.
- Guardar o histórico das saídas desfeitas.
- Detectar consumo lançado em duplicidade (à mão e pela lista).

## Decisions

### 1. Geração dentro da transação da operação

O serviço de movimentações passa a ter uma função interna que aplica uma
movimentação (saldo, lotes e registro) sem `commit`, e outra que a desfaz. O
endpoint de movimentações continua igual, chamando a função interna e fazendo o
`commit`. O serviço de atividades usa as duas funções dentro do seu próprio
salvamento.

- *Por quê*: se a operação for recusada por uma regra, nada do estoque muda.
- *Alternativa*: a tela chamar a API de movimentações depois de salvar a
  atividade. Descartada: deixaria atividade concluída e estoque fora de sincronia
  em caso de falha no meio.

### 2. Ressincronização a cada salvamento de operação concluída

Em todo `PUT` de uma operação que estava ou fica `Concluída`, e na criação já
concluída, o serviço: desfaz as saídas automáticas existentes da operação,
aplica a alteração e valida as regras e, se o estado final for `Concluída`, gera
as saídas de novo. No `DELETE`, desfaz as automáticas antes de excluir.

- *Por quê*: uma regra só cobre conclusão, reabertura, mudança de insumos, de
  talhão ou de data e a nova tentativa dos pendentes.
- *Alternativa*: calcular a diferença entre a lista antiga e a nova e ajustar
  apenas o que mudou. Descartada pela complexidade, sem ganho para o usuário.

### 3. Identificação das saídas automáticas

`movimentacao_estoque` ganha `origem` (`MANUAL` por padrão, `ATIVIDADE` para as
geradas) e `atividade_insumo` ganha `id_movimentacao` (opcional,
`ON DELETE SET NULL`). As automáticas de uma operação são as de origem
`ATIVIDADE` com o seu `id_atividade_agricola`. `baixado` é derivado de
`id_movimentacao`.

### 4. Desfazer apaga a saída e devolve o saldo

Desfazer soma a quantidade de volta ao `estoque_atual`, devolve a cada lote o
que a ligação movimentação-lote registrou e apaga a movimentação.

Para a devolução ser exata, `movimentacao_estoque.quantidade` passa a ter a
mesma precisão do saldo do insumo e do item da operação (três casas). Com duas
casas, uma saída de 1,234 era gravada como 1,23 e devolveria 0,004 a menos.

- *Alternativa*: lançar uma entrada de estorno e manter a saída. É mais
  rastreável, mas cada salvamento de uma operação concluída geraria pares de
  lançamentos no histórico. Fica fora do escopo.

### 5. Pendência por insumo, sem baixa parcial

Cada item com quantidade positiva é tentado na ordem da lista. Se o saldo
utilizável for menor que a quantidade, o item fica sem saída. `pendentes` é
calculado na leitura: itens de operação concluída com quantidade e sem saída,
com o saldo utilizável atual em `disponivel`.

### 6. Dados da saída gerada

Quantidade do item, valor unitário do insumo, data igual a `data_fim`,
responsável, talhão, safra e tipo da operação, `id_atividade_agricola` e destino
"Aplicação na atividade". Os insumos são travados em ordem de id para evitar
bloqueio cruzado entre salvamentos simultâneos.

### 7. Telas

A resposta de criação e de atualização já traz `baixa_estoque`; o módulo de
Atividades mostra um aviso quando há pendentes e invalida as consultas de
insumos e de movimentações. O formulário mostra o saldo utilizável de cada
insumo escolhido e um alerta quando a quantidade o excede. O detalhe consulta
`GET /api/movimentacoes?id_atividade_agricola=` para listar as saídas ligadas à
operação. `movimentacaoDaApi` passa a mapear `origem`.

## Risks / Trade-offs

- [Saída desfeita some do histórico] → decisão registrada; o estorno com
  contrapartida fica como evolução.
- [Cada salvamento de operação concluída recria as saídas] → os ids das
  movimentações mudam; nada mais depende deles além do item da operação.
- [Devolução a um lote que venceu depois] → o saldo volta ao lote vencido e a
  nova geração pode deixar o insumo pendente; o aviso mostra isso.
- [Consumo em duplicidade] → uma saída manual vinculada e o mesmo insumo na
  lista são somados; o detalhe da atividade mostra as duas para o usuário ver.
- [Operações já concluídas antes da change] → não têm saídas geradas; passam a
  gerar no primeiro salvamento. Hoje não há operações concluídas com insumos no
  banco local.
- [Migration não versionada] → gerada no container, como as anteriores.

## Migration Plan

1. Gerar a migration no container, revisar que contém apenas `origem` (com
   valor padrão `MANUAL` para as linhas existentes),
   `atividade_insumo.id_movimentacao` com FK nomeada e a precisão de
   `movimentacao_estoque.quantidade`, e aplicar.
2. Publicar o backend antes do frontend.
3. Reversão: `flask db downgrade` remove as duas colunas; as saídas já geradas
   permanecem como movimentações comuns.

## Open Questions

- Se operações concluídas antes desta change devem ter a baixa gerada em lote é
  uma decisão de implantação por ambiente; não altera o desenho.
