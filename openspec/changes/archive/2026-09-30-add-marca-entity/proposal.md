# Adicionar estrutura da entidade Marca

## Why

Produtos e insumos precisam ser classificados por marca comercial. Hoje não existe
uma entidade dedicada, o que leva a texto livre e dados inconsistentes. Criar a
entidade `Marca` como cadastro básico padroniza os dados e prepara o vínculo
futuro com `Produto` / `Insumo`.

## What Changes

- Novo modelo `Marca` (`models/marca.py`) com os campos `id_marca` (PK, Integer)
  e `descricao_marca` (String(500), obrigatório, único).
- Nova migration Alembic criando a tabela `marca`.
- Novo serviço `MarcaService` com `listar_todos`, `criar_marca`,
  `atualizar_marca` e `excluir_marca`, seguindo o padrão de `TipoSoloService`
  (validação de obrigatoriedade, trim, duplicidade).
- Novo controller `marca_controller` com blueprint `marca_bp` expondo
  `GET /api/marcas`, `POST /api/marcas`, `PUT /api/marcas/<id_marca>` e
  `DELETE /api/marcas/<id_marca>`.
- Registro do blueprint em `app.py` com prefixo `/api`.

## Impact

- Affected specs: `marca` (nova capability)
- Affected code: `models/marca.py`, `services/marca_service.py`,
  `controllers/marca_controller.py`, `app.py`, `migrations/versions/*`
- Sem breaking changes: apenas adição de tabela e rotas novas.

## Out of Scope

- Vínculo (FK) entre `Marca` e `Produto`/`Insumo`.
- Exclusão lógica (soft delete) e histórico de alterações.
- Alterações no frontend.
