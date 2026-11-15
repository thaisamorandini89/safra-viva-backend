# Design

## Context

Motivação e escopo em `proposal.md`. O que condiciona o desenho:

- A criação de insumo grava `estoque_atual` direto no registro e, com `produto`
  aninhado, já cria produto e insumo numa transação.
- O serviço de movimentações tem uma função que aplica uma movimentação (saldo,
  lotes e registro) sem `commit`, recebendo a origem. Ela busca o insumo pelo id
  e valida funcionário e fornecedor, levantando erro de regra.
- `movimentacao_estoque.origem` é texto de 10 caracteres, hoje com `MANUAL` e
  `ATIVIDADE`.
- A exclusão recusa qualquer insumo com movimentação. `lote_insumo` referencia o
  insumo sem exclusão em cascata; `movimentacao_lote` é apagada em cascata com a
  movimentação.
- A criação hoje converte qualquer erro do salvamento em erro 500.
- O formulário de cadastro não tem responsável, lote nem datas.

## Goals / Non-Goals

**Goals:**
- O saldo de um insumo novo é sempre explicado pelas suas movimentações.
- Uma única regra de entrada: o estoque inicial usa o mesmo caminho da entrada
  manual, inclusive para lotes e validade.
- Um cadastro feito por engano continua podendo ser desfeito.

**Non-Goals:**
- Corrigir o saldo sem movimentação de insumos já cadastrados.
- Fechar a alteração direta de `estoque_atual` pelo `PUT`.
- Custo médio ou atualização do valor unitário pela entrada.

## Decisions

### 1. O estoque inicial passa pela aplicação de movimentação

Na criação, o insumo é gravado com saldo zero e, se `estoque_atual` for maior
que zero, a entrada é aplicada pela função de movimentação já existente, antes
do `commit` único.

- *Por quê*: reaproveita as regras de lote, validade divergente e registro da
  ligação com o lote, sem duplicá-las.
- *Alternativa*: a tela chamar `POST /api/movimentacoes` depois de criar o
  insumo. Descartada: uma falha no meio deixaria o insumo sem o saldo informado.

### 2. Contrato: `estoque_atual` continua sendo a quantidade

`estoque_atual` mantém o significado atual no `POST`. Os dados da entrada vêm no
objeto opcional `entrada_inicial` (`numero_lote`, `data_fabricacao`,
`data_validade`, `id_funcionario`).

- *Por quê*: quem já envia só `estoque_atual` continua funcionando e passa a ter
  a entrada registrada.
- *Alternativa*: campos soltos no corpo do insumo. Descartada por misturar dados
  do insumo com dados de uma movimentação.

### 3. Dados derivados da entrada

Data: dia corrente no fuso da aplicação. Valor unitário: o do insumo.
Fornecedor: o do produto, quando houver. Observação: "Estoque inicial do
cadastro". O responsável é opcional na API, como nas demais movimentações, e
obrigatório na tela.

### 4. Origem `CADASTRO`

A entrada do estoque inicial é gravada com origem `CADASTRO`. Não há migration:
a coluna já comporta o valor.

- *Por quê*: a regra de exclusão precisa distinguir essa entrada de uma entrada
  manual, e a tela a rotula como "Estoque inicial".
- *Alternativa*: usar `MANUAL` e reconhecer pela observação. Descartada: texto
  livre não é critério confiável para liberar uma exclusão.

### 5. Exclusão do insumo que só tem a entrada inicial

A exclusão é permitida quando o insumo não consta em atividade e todas as suas
movimentações têm origem `CADASTRO`. Nesse caso são apagados, na mesma
transação, as movimentações, os lotes do insumo e o insumo.

- *Por quê*: sem isso, todo insumo cadastrado com estoque inicial ficaria
  impossível de excluir (decisão da usuária).

### 6. Erros de regra na criação respondem 400

Erros de regra e de validação da entrada (lote com validade inválida,
funcionário inexistente, quantidade negativa, dados de entrada sem quantidade)
desfazem a transação e respondem HTTP 400, em vez de cair no tratamento genérico
de erro de salvamento.

### 7. Telas

No modo de criação, a seção "Controle de Estoque" mostra, quando o estoque
inicial é maior que zero, o responsável (obrigatório) e lote, fabricação e
validade (opcionais), com a mesma validação de datas do formulário de
movimentação. `insumoParaApi` envia `entrada_inicial` só na criação e só com
estoque inicial. `movimentacaoDaApi` passa a mapear a origem `CADASTRO`, e o
histórico mostra "Estoque inicial" na coluna de origem dessa entrada. Depois do
cadastro, o módulo invalida a consulta de movimentações.

## Risks / Trade-offs

- [Insumos antigos continuam com saldo sem entrada] → fora do escopo; no banco
  local o único insumo tem saldo zero.
- [Estoque inicial negativo passa a ser recusado] → hoje é aceito pela API; a
  tela já impede.
- [O `PUT` ainda altera `estoque_atual` sem movimentação] → a tela não envia o
  campo; registrado como não objetivo.
- [No modo de demonstração o lote do estoque inicial não é guardado] → só ocorre
  com o backend fora do ar.

## Migration Plan

1. Publicar o backend antes do frontend: `entrada_inicial` é opcional e o valor
   `CADASTRO` é tratado pela tela antiga como entrada comum.
2. Reversão: voltar o código. As entradas já registradas com origem `CADASTRO`
   permanecem como movimentações válidas.
