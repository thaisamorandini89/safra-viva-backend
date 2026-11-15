# Tasks

## 1. Preparação

- [x] 1.1 Criar a branch `feat/insumos-lotes-validade` no backend e no
      `frontendweb`, a partir de uma base que já contenha a change
      `insumos-cadastro-integrado`, com os containers no ar; verificar que
      `GET /api/insumos` responde 200 e já traz `id_propriedade`.

## 2. Modelo de lotes (backend)

- [x] 2.1 Criar os modelos de lote e de ligação movimentação-lote, registrá-los
      em `models/__init__.py`, gerar a migration no container com constraints
      nomeadas e aplicar; verificar que `flask db upgrade` conclui, que o
      downgrade seguido de upgrade funciona e que `flask db check` não aponta
      diferenças.
- [x] 2.2 Mover a data local para `utils/datas.py` e usá-la no serviço de
      atividades; verificar pela API que uma atividade com prazo de ontem
      continua vindo com `atrasada` verdadeiro e uma com prazo de hoje, falso.

## 3. Entrada e lotes (backend)

- [x] 3.1 Fazer a ENTRADA criar ou somar o lote e registrar a ligação; verificar
      pela API os cenários de "Lote criado ou somado pela entrada" e o de "Mesmo
      número de lote em insumos diferentes".
- [x] 3.2 Recusar validade divergente e preencher a validade ausente; verificar
      pela API os dois cenários de "Validade consistente do lote".

## 4. Saída, consumo e descarte (backend)

- [x] 4.1 Limitar a saída ao saldo utilizável, com a data local definindo o que
      está vencido; verificar pela API os cenários de "Saldo utilizável na
      saída" e de "Lote vencido".
- [x] 4.2 Consumir os lotes pela validade mais próxima e registrar a ligação;
      verificar pela API os três cenários de "Consumo de lotes pelo vencimento
      mais próximo", conferindo os saldos de cada lote.
- [x] 4.3 Aceitar `id_lote` na SAIDA para o descarte; verificar pela API os
      quatro cenários de "Descarte de lote".
- [x] 4.4 Devolver `lotes` na resposta do POST e no histórico; verificar pela API
      os dois cenários de "Lotes da movimentação na resposta" e a regressão:
      saída vinculada a uma operação e entrada sem lote continuam respondendo
      201.

## 5. Lotes na consulta de insumos (backend)

- [x] 5.1 Incluir `lotes` em `GET /api/insumos` e `GET /api/insumos/{id}`;
      verificar pela API os dois cenários de "Lotes na consulta de insumos".

## 6. Telas de Insumos (frontend)

- [x] 6.1 Em `insumosAdapter.ts` e nos tipos: mapear os lotes do insumo e da
      movimentação e enviar `id_lote`; criar o helper de saldo utilizável em
      `types/insumo.ts`; cobrir com testes e verificar que `npm test` passa e que
      `tsc` não aponta erros novos.
- [x] 6.2 Validar a saída pelo saldo utilizável no formulário e recarregar os
      insumos após registrar uma movimentação; verificar no navegador que uma
      entrada com lote e validade aparece no detalhe do insumo após recarregar a
      página, e que um insumo com um lote vencido e outro válido permite saída
      até o saldo válido.
- [x] 6.3 Adicionar a ação de descartar lote vencido no detalhe do insumo e
      mostrar os lotes consumidos no histórico; verificar no navegador que o
      descarte zera o lote, reduz o estoque e aparece no histórico com o número
      do lote.

## 7. Verificação integrada

- [x] 7.1 Executar o roteiro no navegador: duas entradas em lotes com validades
      diferentes, uma saída que consome os dois, conferência dos alertas de
      vencimento no dashboard com um lote vencido e descarte desse lote.
      Verificar também `npm test`, `tsc` sem erros novos e
      `openspec validate insumos-lotes-validade --strict`.
- [x] 7.2 Remover os dados de teste criados e verificar pela API que insumos,
      lotes e movimentações voltaram ao estado inicial.
