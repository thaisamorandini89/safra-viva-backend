# Tasks

## 1. Preparação

- [x] 1.1 Criar a branch `feat/insumos-cadastro-integrado` a partir de `homolog`
      no backend e no `frontendweb`, com os containers no ar; verificar que
      `GET /api/insumos` responde 200 pelo proxy do frontend (porta 5173).

## 2. Propriedade do insumo (backend)

- [x] 2.1 Adicionar `id_propriedade` (FK opcional) ao modelo do insumo, gerar a
      migration no container com a FK nomeada e aplicar; verificar que
      `flask db upgrade` conclui, que o downgrade seguido de upgrade funciona e
      que `flask db check` não aponta diferenças.

## 3. Cadastro, consulta, atualização e exclusão (backend)

- [x] 3.1 Ampliar a consulta com subcategoria, fornecedor, registro MAPA, ficha
      técnica, observações e propriedade; verificar pela API os cenários de
      "Consulta de insumos com dados do produto".
- [x] 3.2 Tornar reutilizáveis, sem commit próprio, a montagem e a atualização
      do produto no serviço de produtos; verificar que `POST` e
      `PUT /api/produtos` continuam respondendo 201 e 200 e recusando marca
      inexistente com 400.
- [x] 3.3 Aceitar `produto` e `id_propriedade` no `POST /api/insumos`, criando
      tudo numa transação e devolvendo o insumo completo; verificar pela API os
      oito cenários de "Cadastro de insumo", conferindo que nada é criado nos
      casos de erro.
- [x] 3.4 Aceitar `produto` e `id_propriedade` no `PUT /api/insumos/{id}` e
      devolver o insumo completo; verificar pela API os quatro cenários de
      "Atualização de insumo".
- [x] 3.5 Recusar a exclusão de insumo com movimentações ou usado em atividade,
      respondendo 400, e manter o produto; verificar pela API os quatro cenários
      de "Exclusão de insumo".

## 4. Tradução e funções de API (frontend)

- [x] 4.1 Em `insumosAdapter.ts`: mapear os campos novos da consulta e criar a
      conversão do formulário para o backend (criação e edição), cobrindo com
      testes; verificar que `npm test` passa.
- [x] 4.2 Ajustar os tipos de insumo (ids de produto, fabricante, marca e
      fornecedor) e, em `api.ts`, criar `getCategoriasInsumo`, `getFabricantes`,
      `getMarcas`, `atualizarInsumo` e `excluirInsumo` e fazer `criarInsumo`
      usar a tradução e propagar o erro do backend; verificar que `tsc` não
      aponta erros novos em relação aos 6 existentes no container.

## 5. Formulário de insumo (frontend)

- [x] 5.1 Trocar os campos de fabricante, marca e fornecedor por combos dos
      cadastros e resolver a categoria para o id do backend; verificar no
      navegador que um insumo novo aparece em `GET /api/insumos` com produto,
      fabricante, marca, fornecedor e propriedade, e continua na lista após
      recarregar a página.
- [x] 5.2 Adicionar o modo de edição (formulário preenchido, sem estoque
      inicial); verificar no navegador que alterar nome, fabricante e estoque
      mínimo se reflete em `GET /api/insumos/{id}` sem mudar `estoque_atual`.

## 6. Ações na lista e no detalhe (frontend)

- [x] 6.1 Adicionar editar e excluir (com confirmação) na lista e no detalhe e
      ligar as mutações no módulo; verificar no navegador que excluir um insumo
      sem uso o remove da lista e do backend, e que excluir um insumo com
      movimentação mostra a mensagem de "em uso" e o mantém.

## 7. Verificação integrada

- [x] 7.1 Executar o roteiro no navegador: cadastrar insumo, registrar uma
      entrada para ele, editar seus dados, tentar excluí-lo (barrado) e usá-lo
      numa atividade. Verificar também `npm test`, `tsc` sem erros novos e
      `openspec validate insumos-cadastro-integrado --strict`.
- [x] 7.2 Remover os dados de teste criados e verificar pela API que insumos,
      produtos, movimentações e atividades voltaram ao estado inicial.
