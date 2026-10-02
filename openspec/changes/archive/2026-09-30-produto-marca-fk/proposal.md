# Refatorar Produto para usar FK id_marca

## Why

O modelo `Produto` guarda a marca como texto livre (`marca VARCHAR(150)`), o que
permite grafias divergentes ("Bayer", "bayer", "Bayer S.A.") e impede
agrupar/filtrar produtos por marca de forma confiável. Com a entidade `Marca`
já criada, o campo texto deve ser substituído por uma chave estrangeira,
garantindo integridade referencial e padronização.

## What Changes

- **BREAKING**: `Produto.marca` (texto) é removido e substituído por
  `id_marca` (Integer, FK → `marca.id_marca`, nullable).
- Migration Alembic que: cria a coluna `id_marca`, migra os dados existentes
  (criando marcas a partir dos textos distintos e associando aos produtos),
  cria a FK e remove a coluna `marca`.
- `ProdutoService` passa a validar a existência da marca informada e a
  serializar `id_marca` + `descricao_marca` na listagem/retorno.
- Payloads de criação e atualização de produto passam a aceitar `id_marca`
  no lugar de `marca`.
- Requisições de Produto no `insomnia_safraviva.json` atualizadas.

## Impact

- Affected specs: `produto` (modificado), `marca` (relacionamento adicionado)
- Affected code: `models/produto.py`, `models/marca.py`,
  `services/produto_service.py`, `controllers/produto_controller.py`,
  `migrations/versions/*`, `insomnia_safraviva.json`
- **Breaking change** para consumidores da API: o campo `marca` (string)
  deixa de ser aceito e retornado; clientes devem usar `id_marca`.

## Out of Scope

- Vínculo de marca com `Insumo` ou `Fabricante`.
- Deduplicação manual/curadoria das marcas geradas pela migração de dados.
- Alterações no frontend.
