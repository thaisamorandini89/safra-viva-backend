# Tasks

## 1. Preparação

- [x] 1.1 Criar a branch `feat/cadastros-apoio-insumos` no backend e no
      `frontendweb` a partir da `homolog` atualizada, com os containers no ar;
      verificar que `GET /api/fornecedores`, `/api/fabricantes`, `/api/marcas`
      e `/api/produtos` respondem 200 e anotar as contagens para restaurar no
      fim.

## 2. Fornecedor e fabricante (backend)

- [x] 2.1 Validar CNPJ (14 dígitos) e CNPJ repetido no fornecedor, no cadastro
      e na atualização; verificar pela API os cenários de "Cadastro de
      fornecedor" e "Atualização de fornecedor".
- [x] 2.2 Recusar a exclusão de fornecedor usado por produto ou movimentação e
      separar 404 de 400 no controller; verificar pela API os quatro cenários de
      "Exclusão de fornecedor" e que "Consulta de fornecedores" segue igual.
- [x] 2.3 Validar CNPJ e nome repetido (sem diferenciar maiúsculas) no
      fabricante e recusar a exclusão em uso; verificar pela API todos os
      cenários da spec `fabricante`.
- [x] 2.4 Recusar a exclusão de marca usada por produto; verificar pela API os
      três cenários de "Exclusão de marca" e que os demais requisitos de `marca`
      continuam valendo.
- [x] 2.5 Adicionar ao `insomnia_safraviva.json` as requisições de fornecedor e
      fabricante (listar, consultar, criar, atualizar, excluir); verificar que o
      JSON é válido.

## 3. Insumo (backend)

- [x] 3.1 Recusar `id_produto` já vinculado a outro insumo no cadastro e na
      atualização; verificar pela API os três cenários de "Um insumo por
      produto" e a regressão: cadastro com `produto` novo continua respondendo
      201.

## 4. API do frontend

- [x] 4.1 Em `api.ts`, criar `getProdutos` e as funções de criar, atualizar e
      excluir fornecedor, fabricante e marca, propagando a recusa do backend e
      falhando sem resposta; em `insumosAdapter.ts`, enviar `id_produto` quando
      o insumo usa produto existente. Cobrir com testes e verificar que
      `npm test` passa e que `tsc` não aponta erros novos.

## 5. Telas (frontend)

- [x] 5.1 Criar a aba "Cadastros" em Insumos com a seção Fornecedores;
      verificar no navegador cadastro, edição, inativação, a mensagem de CNPJ
      repetido e a exclusão barrada de um fornecedor usado por produto, e que o
      fornecedor novo aparece no combo do "Novo Insumo" e da entrada de estoque
      sem recarregar.
- [x] 5.2 Criar as seções Fabricantes e Marcas; verificar no navegador
      cadastro, edição, nome repetido e exclusão barrada em uso, e que renomear
      um fabricante muda o nome mostrado na lista de insumos.
- [x] 5.3 No "Novo Insumo", adicionar a escolha entre produto existente e
      produto novo; verificar no navegador que o combo lista só produtos ativos
      sem insumo, que os dados do produto ficam travados, que o insumo salvo
      aparece no estoque com o produto escolhido e que nenhum produto novo foi
      criado.

## 6. Verificação integrada

- [x] 6.1 Executar o roteiro no navegador: cadastrar fornecedor, fabricante e
      marca, cadastrar um insumo com produto existente e outro com produto novo
      usando os três, registrar uma entrada com o fornecedor e conferir que a
      exclusão dos três é barrada. Verificar também `npm test`, `tsc` sem erros
      novos e `openspec validate cadastros-apoio-insumos --strict`.
- [x] 6.2 Remover os dados de teste criados e verificar pela API que
      fornecedores, fabricantes, marcas, produtos, insumos e movimentações
      voltaram às contagens anotadas em 1.1.
