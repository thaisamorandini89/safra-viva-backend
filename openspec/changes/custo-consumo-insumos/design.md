# Design

## Context

`AtividadeInsumo` guarda `quantidade` e `custo` digitados; `_montar_insumos`
copia o `custo` do payload, e `_custo_total` soma os custos dos itens quando não
há `custo_operacao`. O `PUT` substitui a lista inteira quando `insumos` vem no
corpo. A saída gerada pela conclusão já grava o `valor_unitario` do insumo, não
o custo do item. O `valor_unitario` do insumo vem do cadastro e não é atualizado
pelas entradas.

No frontend, o `AtividadeForm` carrega os insumos com `getInsumosCadastrados`
(que trazem `valor_unitario`) e envia `custo: i.custo || undefined`. O
`TalhaoDetalhe` mostra o histórico de safras do tipo `Talhao`; não consulta
movimentações. `GET /api/movimentacoes` já devolve `id_talhao`, `safra`,
`valor_unitario`, `nome_produto`, `unidade_medida` e `atividade_descricao`.

## Goals / Non-Goals

**Goals:**
- Um único lugar para a regra do custo calculado: o backend.
- Ver o consumo do talhão sem tela nova, no detalhe que já existe.

**Non-Goals:**
- Guardar se o custo foi calculado ou digitado.
- Mudar o valor gravado nas saídas geradas.

## Decisions

### 1. Valor unitário do cadastro

O cálculo usa o `valor_unitario` atual do insumo.

- *Alternativa*: custo médio das entradas. Descartada nesta change: exigiria
  atualizar o valor do insumo a cada entrada e decidir o que fazer com o estoque
  inicial e com o lote; fica para quando a compra gerar despesa.

### 2. Cálculo no backend, prévia no frontend

O backend calcula no `_montar_insumos`, que já roda no `POST` e no `PUT` com
lista. O formulário mostra a mesma conta como prévia e, para itens em modo
automático, envia o custo vazio, deixando o backend calcular. Cada item do
formulário guarda se o custo é manual; digitar um valor torna manual, apagar
volta ao automático. Ao abrir uma edição, o item é automático quando o custo
gravado está vazio ou é igual à conta com o valor unitário atual.

- *Por quê*: a regra vale também para quem usa a API, e o formulário não grava
  um valor diferente do que o backend calcularia.
- *Alternativa*: o frontend enviar o valor calculado. Descartada: a regra ficaria
  só na tela.

### 3. Custo zero digitado é mantido

O frontend passa a enviar `0` quando a pessoa digita zero, em vez de
`undefined`, para distinguir "custo zero" de "calcular".

### 4. Consumo do talhão pelas movimentações

O filtro `id_talhao` entra em `MovimentacaoService.listar` junto dos que já
existem. O `TalhaoDetalhe` busca `GET /api/movimentacoes?id_talhao={id}` com a
chave `["talhao-insumos", id]`, mostra só saídas e calcula o valor de cada uma
como quantidade × `valor_unitario` da movimentação; sem valor, mostra "—" e não
soma no total. Com o backend fora do ar, a seção mostra a mensagem de
indisponível em vez de dados de demonstração.

- *Por quê*: a movimentação é o registro do que saiu do estoque para o talhão,
  inclusive saídas manuais sem atividade.
- *Alternativa*: somar os insumos das atividades do talhão. Descartada: deixaria
  de fora as saídas manuais e contaria itens não baixados.

## Risks / Trade-offs

- [Valor unitário desatualizado gera custo errado] → a pessoa pode digitar o
  custo; o aviso de "calculado" mostra de onde veio o valor.
- [Editar uma atividade antiga sem mexer nos insumos recalcula itens sem custo]
  → é o comportamento esperado da regra; itens com custo digitado não mudam.

## Migration Plan

1. Publicar o backend antes do frontend: o filtro é aditivo e o cálculo só
   preenche custos vazios.
2. Reversão: voltar o código. Custos já calculados e gravados permanecem.
