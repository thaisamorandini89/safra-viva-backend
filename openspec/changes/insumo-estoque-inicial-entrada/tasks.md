# Tasks

## 1. Preparação

- [x] 1.1 Criar a branch `feat/insumo-estoque-inicial-entrada` no backend e no
      `frontendweb`, a partir da `homolog` atualizada, com os containers no ar e
      as migrations aplicadas; verificar que `GET /api/movimentacoes` responde
      200 e que `GET /api/insumos` traz `lotes`.

## 2. Estoque inicial como entrada (backend)

- [x] 2.1 Na criação do insumo, gravar o saldo zero e aplicar a entrada do
      estoque inicial na mesma transação, com origem `CADASTRO` e os dados
      derivados do design; verificar pela API os cenários "Cadastro com estoque
      inicial" e "Cadastro sem estoque inicial", e que o cadastro com `produto`
      aninhado continua respondendo 201.
- [x] 2.2 Aceitar `entrada_inicial` (lote, datas e responsável); verificar pela
      API os cenários "Estoque inicial em lote" e "Responsável da entrada
      inicial".
- [x] 2.3 Recusar com 400, sem criar nada, os dados de entrada sem estoque
      inicial e a entrada inválida; verificar pela API os cenários "Dados de
      entrada sem estoque inicial" e "Entrada inicial inválida", conferindo que
      a quantidade de produtos, insumos, movimentações e lotes não mudou.
- [x] 2.4 Verificar pela API os três cenários de "Origem da movimentação": a
      entrada inicial vem como `CADASTRO` e um `POST /api/movimentacoes` com
      `origem` igual a `CADASTRO` no payload é gravado como `MANUAL`.

## 3. Exclusão (backend)

- [x] 3.1 Permitir excluir o insumo que só tem a entrada do estoque inicial,
      removendo a entrada e o lote; verificar pela API os cinco cenários de
      "Exclusão de insumo".

## 4. Telas (frontend)

- [x] 4.1 Em `types/insumo.ts` e `insumosAdapter.ts`: incluir os dados da
      entrada inicial no payload de criação, enviar `entrada_inicial` só na
      criação com estoque inicial e mapear a origem `CADASTRO`; cobrir com
      testes e verificar que `npm test` passa e que `tsc` não aponta erros
      novos.
- [x] 4.2 No formulário de novo insumo, mostrar responsável (obrigatório), lote,
      fabricação e validade quando o estoque inicial for maior que zero;
      verificar no navegador que os campos aparecem ao digitar a quantidade e
      somem ao zerá-la, que salvar sem responsável é barrado e que a edição não
      mostra esses campos.
- [x] 4.3 Rotular a entrada como "Estoque inicial" no histórico do insumo e na
      lista de movimentações e recarregar as movimentações depois do cadastro;
      verificar no navegador que, após cadastrar um insumo com estoque inicial
      em lote, a entrada aparece no histórico sem recarregar a página e o lote
      aparece no detalhe.

## 5. Verificação integrada

- [x] 5.1 Executar o roteiro no navegador: cadastrar um insumo com estoque
      inicial em lote com validade, conferir saldo, lote e histórico, registrar
      uma saída e conferir que a exclusão é barrada; cadastrar outro com estoque
      inicial e excluí-lo. Verificar também `npm test`, `tsc` sem erros novos e
      `openspec validate insumo-estoque-inicial-entrada --strict`.
- [x] 5.2 Remover os dados de teste criados e verificar pela API que insumos,
      produtos, movimentações e lotes voltaram ao estado inicial.
