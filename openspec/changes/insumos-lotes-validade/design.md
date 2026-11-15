# Design

## Context

Motivação e escopo em `proposal.md`. O que condiciona o desenho:

- `movimentacao_estoque` já guarda `numero_lote`, `data_fabricacao` e
  `data_validade` nas entradas, como dados soltos. O saldo existe só no total
  (`insumo.estoque_atual`), atualizado na mesma transação da movimentação, com o
  insumo travado por `SELECT ... FOR UPDATE`.
- As telas já têm o modelo de lote (`numero_lote`, datas, `quantidade`) e
  calculam vencido e próximo do vencimento a partir da lista `lotes` do insumo.
  Hoje a entrada soma no lote só na memória e a saída não mexe em lote.
- A tela bloqueia qualquer saída de um produto que tenha lote vencido com saldo.
  Sem uma forma de retirar esse saldo, o produto ficaria bloqueado para sempre.
- A change `atividades-baixa-estoque` vai precisar desfazer saídas, devolvendo o
  saldo aos lotes de onde saiu.
- A data local hoje é calculada dentro de
  `services/atividade_agricola_service.py`.

## Goals / Non-Goals

**Goals:**
- Saldo por lote confiável, mantido pelo backend na mesma transação da
  movimentação.
- Nenhuma mudança no significado de `estoque_atual`, que continua sendo o total.
- Registro de quais lotes cada movimentação afetou.

**Non-Goals:**
- Reconstruir lotes de entradas antigas.
- Escolha de lote pelo usuário numa saída comum.
- Impedir estoque inicial sem lote no cadastro do insumo.

## Decisions

### 1. Tabela de lotes com saldo e tabela de ligação com a movimentação

`lote_insumo` guarda o saldo de cada lote (único por insumo e número).
`movimentacao_lote` registra, para cada movimentação, os lotes afetados e a
quantidade de cada um, com exclusão em cascata junto da movimentação.

- *Por quê*: a ligação dá a rastreabilidade (qual lote foi para qual talhão) e é
  o que permite devolver o saldo ao lote certo quando uma saída for desfeita.
- *Alternativa*: guardar só o saldo no lote. Descartada por não permitir desfazer
  nem rastrear.

### 2. Saldo sem lote por diferença

O saldo sem lote não é armazenado: é `estoque_atual` menos a soma dos lotes.
Entradas sem número de lote e o estoque inicial do cadastro caem nele.

### 3. Ordem de consumo e saldo utilizável

Uma saída comum consome: lotes não vencidos com validade (a mais próxima
primeiro), lotes sem validade e, por fim, o saldo sem lote. O saldo utilizável é
`estoque_atual` menos o saldo dos lotes vencidos, e é o limite da saída.

- *Por quê*: o saldo sem lote não tem validade conhecida, então fica por último.

### 4. Descarte como saída com lote indicado

`id_lote` numa SAIDA retira só daquele lote e ignora a regra de vencimento. Na
tela, a ação "Descartar" de um lote vencido abre o formulário de saída com o
lote fixo, a quantidade igual ao saldo e o destino "Descarte de lote vencido",
mantendo data e responsável obrigatórios.

- *Alternativa*: um terceiro tipo de movimentação (`DESCARTE`). Descartada por
  alterar o enumerado e todos os relatórios que somam entradas e saídas.

### 5. Validade do lote não muda por entrada

Entrada em lote existente com validade diferente é recusada: mesmo número de
lote com outra validade indica erro de digitação ou outro lote.

### 6. Data local compartilhada

A função que devolve a data corrente no fuso da aplicação (`APP_TIMEZONE`) sai do
serviço de atividades para um módulo `utils/datas.py`, usado pelos dois
serviços.

### 7. Lotes vêm do backend nas telas

`insumoDaApi` passa a mapear `lotes`, e `movimentacaoDaApi` os lotes da
movimentação. Depois de registrar uma movimentação, o módulo de Insumos invalida
as consultas de insumos para recarregar saldos e lotes; a atualização local
existente continua servindo ao modo de demonstração. A validação da saída usa um
helper de saldo utilizável em `types/insumo.ts`.

### 8. Sem reconstrução de lotes

A migration só cria as tabelas. Entradas antigas com número de lote não geram
lote, porque as saídas antigas não dizem de qual lote saíram e o saldo por lote
não pode ser deduzido.

## Risks / Trade-offs

- [Estoque existente fica todo "sem lote"] → só novas entradas com número de
  lote criam lotes; registrado como não objetivo.
- [Regra de validade divergente pode barrar uma entrada legítima] → a mensagem
  informa a validade já registrada; o usuário pode usar outro número de lote.
- [Saída que antes passava agora é recusada] → só acontece quando há saldo
  vencido, e a mensagem explica o motivo e aponta o descarte.
- [Migration não versionada] → gerada no container, como as anteriores.

## Migration Plan

1. Gerar a migration no container, revisar que cria apenas `lote_insumo` e
   `movimentacao_lote` com constraints nomeadas, e aplicar.
2. Publicar o backend antes do frontend: `lotes` é um campo a mais nas
   respostas.
3. Reversão: `flask db downgrade` remove as duas tabelas; os saldos totais não
   são afetados.
