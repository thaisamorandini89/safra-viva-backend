# Design

## Context

Motivação e escopo em `proposal.md`. O que condiciona o desenho:

- `atividade_agricola.safra` e `movimentacao_estoque.safra` são texto de 20
  caracteres. `safra.nome` tem até 200.
- A operação tem `id_propriedade`, preenchido pelo payload ou pela propriedade
  do talhão. A safra cadastrada tem `id_propriedade` obrigatório.
- As regras da operação são conferidas sobre o estado final dos dados, na
  criação e na atualização.
- A saída gerada pela conclusão da operação copia a safra em texto. A saída
  manual vinculada a uma operação já herda o tipo e exige o mesmo talhão.
- Na movimentação, os campos de destino só são aceitos em SAIDA.
- As telas montam as opções de safra a partir dos textos já usados nas
  atividades. Listas, filtros, dashboards e relatórios leem o texto `safra` das
  respostas.
- Com `financeiro-ponta-a-ponta`, `getSafras` devolve as safras cadastradas e
  existe tela para cadastrá-las.
- Decisões da usuária: a safra precisa ser da mesma propriedade do talhão; o
  texto antigo é mantido até alguém escolher uma safra cadastrada.

## Goals / Non-Goals

**Goals:**
- Atividade, saída de estoque e lançamento apontam para o mesmo cadastro de
  safra.
- Nenhum registro existente perde a safra que mostra hoje.
- Listas, filtros e relatórios das telas continuam funcionando sem alteração.

**Non-Goals:**
- Criar safras a partir dos textos antigos.
- Remover as colunas de texto.
- Fechar a API para safra em texto.

## Decisions

### 1. Coluna nova ao lado do texto

`id_safra` (opcional, FK nomeada para `safra`) entra em `atividade_agricola` e
em `movimentacao_estoque`. As colunas de texto permanecem como legado.

- *Por quê*: os textos antigos não trazem cultura, período nem propriedade, que
  o cadastro de safra exige; não há como convertê-los com segurança.
- *Alternativa*: criar uma safra para cada texto distinto. Descartada por exigir
  dados inventados.

### 2. `safra` na resposta é derivado

Nas respostas, `safra` é o nome da safra cadastrada quando há `id_safra`; senão,
o texto legado. Ao gravar um `id_safra`, o texto legado do registro é limpo; ao
gravar `id_safra` nulo, os dois ficam vazios.

- *Por quê*: listas, filtros, dashboards e relatórios das telas continuam lendo
  o mesmo campo, sem mudança; e não sobra texto divergente do cadastro.

### 3. A API continua aceitando texto sem `id_safra`

Um payload com `safra` em texto e sem `id_safra` continua gravando o texto, como
hoje. Com `id_safra` presente, o texto do payload é ignorado. As telas deixam de
enviar texto.

- *Por quê*: mantém válidos os requisitos atuais de atividades e movimentações e
  não quebra quem já usa a API.
- *Trade-off*: a unificação é garantida pelas telas, não pela API.

### 4. Mesma propriedade, no estado final

A regra entra na validação do estado final da operação: a propriedade da safra
tem de ser a da operação. Trocar o talhão para outra propriedade sem trocar a
safra é recusado. Na saída de estoque, a comparação é com a propriedade do
talhão informado; sem talhão, não há o que comparar.

### 5. Herança na saída vinculada a uma operação

A saída gerada pela conclusão copia `id_safra` e o texto legado da operação. A
saída manual vinculada a uma operação com safra cadastrada fica com a safra da
operação quando `id_safra` não é informado; um `id_safra` diferente é recusado,
como já acontece com o talhão.

### 6. Exclusão de safra

A exclusão criada em `financeiro-ponta-a-ponta` passa a conferir também
operações e movimentações. A FK não tem exclusão em cascata.

### 7. Telas

O campo de safra dos formulários de atividade e de saída de estoque vira um
combo alimentado por `getSafras`, com as safras ativas da propriedade do talhão
escolhido (mais a já selecionada numa edição). Trocar o talhão para outra
propriedade limpa a safra. Na saída, escolher a atividade preenche e trava a
safra. Num registro com texto legado, a tela mostra esse texto como informação
e, na edição, só envia `id_safra` quando o usuário mexe no combo. Sem safras
para a propriedade, o combo orienta o cadastro em Financeiro › Safras.

## Risks / Trade-offs

- [Registros antigos continuam fora das apurações por safra cadastrada] → só
  entram quando alguém escolhe a safra neles; hoje há uma atividade nessa
  situação.
- [Sem safra cadastrada para a propriedade, o campo fica vazio] → a tela orienta
  o cadastro; a safra continua opcional.
- [A API ainda grava texto] → decisão 3; pode ser fechada numa change futura.
- [Migration não versionada] → gerada no container, como as anteriores.

## Migration Plan

1. Gerar a migration no container, revisar que contém apenas as duas colunas
   `id_safra` com FKs nomeadas, e aplicar.
2. Publicar o backend antes do frontend: `id_safra` é opcional e as respostas
   só ganham um campo.
3. Reversão: `flask db downgrade` remove as duas colunas; os textos legados não
   são tocados, mas as safras escolhidas depois da mudança se perdem.
