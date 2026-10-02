# Tasks

## 1. Modelo

- [x] 1.1 Em `models/produto.py`, remover `marca = db.Column(db.String(150))` e
      adicionar `id_marca = db.Column(db.Integer, db.ForeignKey('marca.id_marca'), nullable=True)`.
- [x] 1.2 Adicionar `relationship` entre `Produto` e `Marca` (backref `produtos`).

## 2. Migration

- [x] 2.1 Gerar a migration a partir da head atual (`a4828862173e`).
- [x] 2.2 No `upgrade`, adicionar a coluna `id_marca` antes de remover `marca`.
- [x] 2.3 Inserir em `marca` as descrições distintas e não nulas existentes em
      `produto.marca` que ainda não estejam cadastradas.
- [x] 2.4 Atualizar `produto.id_marca` com o id correspondente ao texto antigo.
- [x] 2.5 Criar a constraint de FK `produto.id_marca → marca.id_marca` e
      remover a coluna `marca`.
- [x] 2.6 Implementar o `downgrade` (recriar `marca` texto, repopular a partir
      da FK, remover `id_marca`).
- [x] 2.7 Aplicar a migration e conferir os dados migrados.

## 3. Serviço e API

- [x] 3.1 Em `ProdutoService.listar_*`, substituir `"marca": prod.marca` por
      `"id_marca"` e `"descricao_marca"` (nulo quando não houver marca).
- [x] 3.2 Na criação, ler `id_marca` do payload, validar que a marca existe
      (`ValueError` quando não existir) e persistir.
- [x] 3.3 Na atualização, aceitar `id_marca` (inclusive `null` para desvincular)
      com a mesma validação de existência.
- [x] 3.4 Garantir que `controllers/produto_controller.py` repassa o novo campo
      e devolve 400 para `id_marca` inválido.

## 4. Validação

- [x] 4.1 Testar `POST`/`PUT` de produto com `id_marca` válido, inválido e nulo.
- [x] 4.2 Testar `GET` de produtos conferindo `id_marca` e `descricao_marca`.
- [x] 4.3 Atualizar as requisições de Produto no `insomnia_safraviva.json`.
