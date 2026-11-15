# Design

## Context

Motivação e escopo em `proposal.md`. O que condiciona o desenho:

- O backend do Financeiro está no ar: quatro tabelas, rotas de safras, centros
  de custo, lançamentos, saldo, fluxo de caixa e indicadores. Safra e centro de
  custo só têm criar e listar. `conciliado` existe no lançamento, mas nenhuma
  rota o altera.
- Os erros do backend seguem o formato já usado em movimentações
  (`error` e, na validação, `details` com `campo` e `mensagem`).
- No frontend, `getSafras`, `getCentrosCusto`, `getIndicadores` e
  `getTodosLancamentos` devolvem dados de demonstração quando o backend responde
  com lista vazia. `criarLancamento`, `atualizarLancamento` e `criarCentroCusto`
  tratam qualquer falha, inclusive uma recusa 400, como backend fora do ar e
  gravam na memória.
- A consulta de safras (`["financeiro-safras"]`) é compartilhada com Início,
  Notificações, Mapa, Relatórios e SafraIA.
- A tela Início já travou cerca de um minuto quando uma consulta ficou sem dados
  de demonstração com o backend parado.
- O backend não tem testes automatizados; a verificação é por API. O frontend
  tem `vitest`.
- Decisões da usuária: as telas de safra e de centro de custo ficam como abas do
  Financeiro; lançamento conciliado fica travado.

## Goals / Non-Goals

**Goals:**
- O que a tela mostra como salvo está salvo no backend.
- Uma regra única para dados de demonstração nas funções do Financeiro.
- A change `financeiro` fica verificada e pronta para arquivar.

**Non-Goals:**
- Reescrever o backend do Financeiro ou mudar o contrato das rotas existentes.
- Alterar o cálculo de saldo, fluxo de caixa e indicadores.
- Conciliação com extrato bancário importado.

## Decisions

### 1. Verificar antes de estender

O primeiro grupo de tasks confere, pela API, os 35 cenários das specs da change
`financeiro`. Um desvio do código em relação à spec é corrigido no código. Um
cenário da spec que pareça errado é levado à usuária antes de qualquer mudança.
O cenário de exclusão de lançamento conciliado é conferido marcando o
lançamento direto no banco, porque a conciliação só passa a existir depois.

- *Por quê*: os requisitos novos se apoiam nesse comportamento; estender sobre
  algo não conferido esconderia a origem de um defeito.

### 2. Regra única de demonstração

Nas funções do Financeiro em `api.ts`: se o backend respondeu, vale a resposta,
mesmo vazia; se respondeu com erro, o erro é propagado com a mensagem dele; só
quando não há resposta (rede ou proxy) entram os dados de demonstração. A
detecção reaproveita `erroDoBackend`, já usado em Insumos.

- *Por quê*: mantém a tela Início utilizável com o backend parado e acaba com o
  salvamento falso.
- *Alternativa*: remover os dados de demonstração do Financeiro. Descartada pelo
  travamento já visto na tela Início.

### 3. Conciliação em rota própria

`PUT /api/lancamentos/{id}/conciliacao` recebe só `conciliado`. O `PUT` do
lançamento continua sendo substituição completa e passa a recusar o conciliado.

- *Por quê*: o `PUT` do lançamento reaproveita o schema de criação; um campo
  `conciliado` nele obrigaria a reenviar o lançamento inteiro para conciliar e
  conflitaria com o bloqueio de edição.
- *Alternativa*: `conciliado` no corpo do `PUT`. Descartada pelo motivo acima.

### 4. Exclusão protegida e inativação

Safra e centro de custo em uso por lançamento não são excluídos; a saída é
inativar pelo `status`, como nos catálogos de atividades. As listagens
continuam devolvendo os inativos, e os combos das telas os escondem, exceto o já
selecionado numa edição.

### 5. Nome único e período sem migration

A unicidade do nome da safra na propriedade e a ordem das datas são conferidas
no serviço. Não há constraint nova no banco.

- *Por quê*: o diretório de migrations não é versionado; evitar migration
  simplifica a publicação.

### 6. A propriedade da safra não muda

A edição recusa trocar `id_propriedade`. Uma safra criada na propriedade errada
é excluída e recriada, o que só é possível enquanto não tiver uso.

- *Por quê*: a change `safra-unificada` vai exigir que a safra seja da mesma
  propriedade das atividades que a usam; permitir a troca abriria incoerência.

### 7. Telas

Duas abas novas no módulo Financeiro, "Safras" e "Centros de Custo", cada uma
com lista e formulário na mesma tela. Depois de salvar ou excluir, invalidam
`["financeiro-safras"]` e `["financeiro-centros-custo"]`, o que atualiza também
os outros módulos. Na lista de lançamentos, o conciliado mostra a ação de
desfazer no lugar de editar e excluir. Os avisos de erro usam o texto devolvido
pelo backend.

### 8. Testes do frontend

A regra de demonstração é coberta por testes que simulam o cliente HTTP:
resposta vazia devolve lista vazia, falha de rede devolve demonstração e recusa
do backend é propagada.

## Risks / Trade-offs

- [Módulos que hoje mostram safras de demonstração ficam vazios] → é o estado
  real; as abas novas permitem cadastrar.
- [A verificação pode revelar muitos desvios no backend existente] → cada
  correção fica limitada ao que a spec da change `financeiro` já diz; o que
  passar disso é levado à usuária.
- [Lançamentos pendentes entram no saldo e no fluxo de caixa] → é o que a spec
  atual define; fora do escopo.
- [A ordem de arquivamento importa] → `financeiro` antes desta, e esta antes de
  `safra-unificada`; registrado na proposta.

## Migration Plan

1. Publicar o backend antes do frontend: as rotas novas são aditivas. As duas
   recusas novas (`POST /api/safras` inválido e `PUT` de lançamento conciliado)
   não afetam a tela atual, que não cadastra safra nem concilia.
2. Reversão: voltar o código. Não há mudança de banco.
