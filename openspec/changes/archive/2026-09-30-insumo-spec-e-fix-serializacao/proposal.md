# Documentar Insumo e corrigir a serialização do produto vinculado

## Why

A entidade `Insumo` (item de estoque vinculado a `Produto`) já está implementada,
mas nunca foi descrita em `openspec/specs/`, então não existe baseline do
comportamento esperado.

Durante o levantamento foi encontrado um **bug em produção**: `InsumoService.listar_todos`
lê `produto.fabricante` e `produto.marca`, atributos que não existem no modelo
`Produto` — `fabricante` nunca existiu (o campo é `id_fabricante`) e `marca` foi
removido na refatoração para FK. Com qualquer insumo cadastrado,
`GET /api/insumos` e `GET /api/insumos/{id}` retornam **HTTP 500**
(`'Produto' object has no attribute 'fabricante'`). Confirmado manualmente.

## What Changes

- Corrigir `InsumoService.listar_todos` para resolver fabricante e marca pelas
  FKs (`id_fabricante` → `Fabricante`, `id_marca` → `Marca`), em vez de ler
  atributos inexistentes.
- Padronizar a serialização, expondo `id_fabricante` / `fabricante_nome` e
  `id_marca` / `descricao_marca`, no mesmo formato já usado por `ProdutoService`.
- Registrar a capability `insumo` em `openspec/specs/`, documentando a estrutura,
  o CRUD em `/api/insumos` e as regras de validação numérica já implementadas.

## Impact

- Affected specs: `insumo` (nova capability)
- Affected code: `services/insumo_service.py`
- Correção de bug: `GET /api/insumos` e `GET /api/insumos/{id}` voltam a
  responder 200 quando há insumos cadastrados.
- Mudança de contrato: as chaves `fabricante` e `marca` (que hoje nunca chegam a
  ser retornadas, pois a rota falha) passam a ser `fabricante_nome` e
  `descricao_marca`, acompanhadas dos respectivos ids.

## Out of Scope

- Movimentações de estoque (entradas/saídas) e histórico.
- Alertas de estoque mínimo e bloqueio de saldo negativo.
- Unicidade de insumo por produto.
- Alterações no modelo `Insumo` ou no banco.
