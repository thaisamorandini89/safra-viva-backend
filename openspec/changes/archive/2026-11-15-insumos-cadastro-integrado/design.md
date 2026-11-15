# Design

## Context

Motivação e escopo em `proposal.md`. O que condiciona o desenho:

- No backend, o insumo é o item de estoque de um **produto**: os dados
  comerciais ficam em `produto` e o saldo em `insumo`. A tela tem um formulário
  só, com os campos dos dois.
- `POST /api/insumos` exige `id_produto`. Há 10 produtos cadastrados e apenas um
  com insumo, sinal de que criar em dois passos já deixou produtos soltos.
- As 7 categorias da tela são as mesmas 7 cadastradas no backend. A tela usa os
  nomes para escolher ícone e cor.
- `src/services/insumosAdapter.ts` já traduz a leitura de insumos; `criarInsumo`
  ainda envia o formato da tela e cai num registro local quando o POST falha.
- Nomes de produto não são únicos no backend.

## Goals / Non-Goals

**Goals:**
- Um único pedido cria (ou atualiza) produto e insumo, sem estado intermediário.
- As telas de Insumos continuam com os tipos que já usam; a diferença de formato
  fica no módulo de tradução.

**Non-Goals:**
- Alterar o estoque pela edição do insumo: o saldo só muda por movimentação.
- Unicidade de nome de produto e reaproveitamento dos produtos sem insumo.

## Decisions

### 1. Produto aninhado no cadastro e na atualização do insumo

`POST /api/insumos` aceita `id_produto` **ou** `produto` (não os dois). Com
`produto`, o serviço monta o produto com as validações do cadastro de produtos e
grava produto e insumo num único commit. `PUT /api/insumos/{id}` aceita
`produto` com os campos a alterar no produto vinculado, também num único commit.
A montagem e a atualização do produto passam a ser funções reutilizáveis do
serviço de produtos, sem commit próprio.

- *Por quê*: é atômico e mantém a tela com um formulário só.
- *Alternativa*: a tela chamar `POST /api/produtos` e depois `POST /api/insumos`.
  Descartada: uma falha no segundo passo deixa o produto solto.

### 2. Resposta com o insumo completo

Criação e atualização devolvem o mesmo objeto da consulta (mantendo `message`,
`id_insumo` e `id_produto`), para a tela atualizar a lista sem outra chamada.

### 3. Categoria resolvida pelo nome

A tela mantém a lista fixa de categorias (dona dos ícones e cores) e resolve o
`id_categoria_insumo` consultando `GET /api/categorias-insumo` pelo nome. Se o
nome não existir no backend, o formulário mostra o erro em vez de enviar.

- *Alternativa*: popular o combo só com o backend. Descartada porque uma
  categoria nova não teria ícone nem cor nas telas.

### 4. Fabricante, marca e fornecedor por id

Os três campos viram combos alimentados por `/api/fabricantes`, `/api/marcas` e
`/api/fornecedores`, enviando ids. O formulário não cria esses cadastros. Os
combos omitem itens inativos, exceto o já selecionado numa edição.

### 5. Edição não altera o saldo

No modo de edição, o campo de estoque inicial fica oculto e `estoque_atual` não
é enviado. Estoque mínimo, valor unitário, status, propriedade e os dados do
produto são editáveis.

### 6. Exclusão em uso conferida antes de excluir

O serviço consulta movimentações de estoque e itens de insumo de atividades
antes do `delete` e levanta erro de regra (400). O controller passa a distinguir
"não encontrado" (404) dos demais erros de regra, como nos outros cadastros. O
produto vinculado é mantido.

### 7. Tradução e erros no frontend

`insumosAdapter.ts` ganha a conversão do formulário para o backend
(`insumoParaApi`) e passa a mapear os campos novos da consulta. `criarInsumo`,
`atualizarInsumo` e `excluirInsumo` seguem a regra já usada na movimentação: se
o backend respondeu com erro, a mensagem é propagada; o registro local só vale
quando não houve resposta do backend.

## Risks / Trade-offs

- [Produtos repetidos por nome] → o cadastro integrado sempre cria um produto
  novo; como não há unicidade, pode repetir um dos produtos sem insumo. Fora do
  escopo; registrado na proposta.
- [Categoria renomeada no backend] → o formulário acusa o erro em vez de gravar
  com categoria errada.
- [Combos sem tela de cadastro] → fabricante, marca ou fornecedor novos ainda
  dependem da API.
- [Migration não versionada] → gerada no container, como as anteriores.

## Migration Plan

1. Gerar a migration no container, revisar que contém apenas
   `insumo.id_propriedade` e sua FK nomeada, e aplicar.
2. Publicar o backend antes do frontend: os campos novos são opcionais.
3. Reversão: `flask db downgrade` remove a coluna.
