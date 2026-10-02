# Design

## Context

`Produto.marca` é hoje `String(150)` nullable. A tabela `marca`
(`id_marca`, `descricao_marca` único) já existe e está vazia ou com poucos
registros. A mudança é breaking para a API e exige migração de dados.

## Decisions

### FK nullable

`id_marca` será nullable, espelhando o comportamento atual (`marca` era
opcional) e evitando bloquear produtos legados sem marca.

### Migração de dados dentro da migration

A conversão texto → FK acontece na própria migration, em três passos no
`upgrade`, antes do `drop_column`:

1. `INSERT INTO marca (descricao_marca) SELECT DISTINCT TRIM(marca) FROM produto
   WHERE marca IS NOT NULL AND TRIM(marca) <> '' AND NOT EXISTS (...)`
2. `UPDATE produto SET id_marca = m.id_marca FROM marca m WHERE TRIM(produto.marca) = m.descricao_marca`
3. `ALTER TABLE ... DROP COLUMN marca`

Alternativa descartada: script separado pós-deploy — deixaria uma janela com
dados inconsistentes e exigiria coordenação manual.

### Downgrade

O `downgrade` recria `marca VARCHAR(150)`, repopula a partir de
`marca.descricao_marca` (truncando em 150 caracteres) e remove `id_marca`.
Marcas criadas pela migração permanecem na tabela `marca` — reverter a
inserção não é seguro, pois outras entidades podem passar a referenciá-las.

### Contrato da API

`id_marca` substitui `marca` na entrada. Na saída expomos `id_marca` e
`descricao_marca`, evitando que o cliente precise de uma segunda chamada
para exibir o nome da marca.

## Risks

- **Breaking change**: clientes que enviam `marca` como string passam a ser
  rejeitados (campo ignorado / 400 se `id_marca` ausente for exigido). Mitigação:
  comunicar a mudança e atualizar a coleção do Insomnia.
- **Descrições sujas**: textos com diferenças de caixa/acento geram marcas
  duplicadas. A curadoria fica fora do escopo desta mudança.
- **Limite de tamanho**: `descricao_marca` tem 500 caracteres e `marca` tinha
  150, logo o `upgrade` não trunca; o `downgrade` pode truncar.
