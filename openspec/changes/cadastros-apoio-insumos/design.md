# Design

## Context

As rotas de fornecedor, fabricante, marca e produto já existem (`/api/fornecedores`,
`/api/fabricantes`, `/api/marcas`, `/api/produtos`). Os serviços de fornecedor e
fabricante convertem qualquer falha do banco em `RuntimeError`, que o controller
devolve como 500; é isso que acontece hoje na exclusão em uso (chave
estrangeira), no CNPJ de fornecedor repetido (coluna única) e no nome de
fabricante repetido (coluna única). Os controllers de fornecedor e fabricante
mapeiam todo `ValueError` da exclusão para 404. O de marca já separa
`LookupError` (404) de `ValueError` (400).

No frontend, `getFornecedores`, `getFabricantes` e `getMarcas` já existem em
`api.ts`, com as chaves de cache `["fornecedores"]`, `["fabricantes"]` e
`["marcas"]`, usadas pelo `InsumoForm` e pelo `MovimentacaoForm`. Não há função
de produtos no frontend. O `insumoParaApi` sempre envia o objeto `produto`.

Não há dados duplicados hoje: nenhum fabricante, marca ou CNPJ de fornecedor
repetido, e nenhum nome de fornecedor repetido.

## Goals / Non-Goals

**Goals:**
- Trocar os 500 previsíveis por 400 com mensagem, sem migration.
- Telas de fornecedor, fabricante e marca no padrão das abas de Safras e
  Centros de Custo do Financeiro.

**Non-Goals:**
- Unicidade de nome de produto ou de fornecedor.
- Mudar a regra de marca repetida, que continua diferenciando maiúsculas de
  minúsculas como hoje.

## Decisions

### 1. Uso conferido antes de excluir

O serviço verifica as referências antes do `delete` e lança `ValueError` com a
mensagem de "em uso"; o "não encontrado" de fornecedor e fabricante passa a usar
`LookupError`, como a marca, e os controllers mapeiam `LookupError` → 404 e
`ValueError` → 400. Referências conferidas: produto (fornecedor, fabricante,
marca) e movimentação de estoque (fornecedor).

- *Por quê*: mensagem clara e sem depender do texto do erro do banco.
- *Alternativa*: capturar `IntegrityError` e traduzir. Descartada: a mensagem
  ficaria genérica e o controller teria de distinguir pelo texto.

### 2. Unicidade e CNPJ validados no serviço

CNPJ só com dígitos e exatamente 14; CNPJ de fornecedor e nome de fabricante
conferidos contra os demais registros antes de gravar, ignorando o próprio na
atualização. O nome de fabricante é comparado sem diferenciar maiúsculas de
minúsculas. O CNPJ de fabricante não é único, como no banco.

### 3. Um insumo por produto, conferido no serviço

`criar_insumo` e `atualizar_insumo` recusam `id_produto` já vinculado a outro
insumo. Sem constraint nova no banco, porque o diretório de migrations não é
versionado.

### 4. Aba "Cadastros" dentro de Insumos

Uma aba nova em `InsumosModule` com três seções alternadas por botões
(Fornecedores, Fabricantes, Marcas), cada uma com lista e formulário na mesma
tela, como `SafrasAba`. Fornecedor e fabricante têm inativar/reativar; marca só
editar e excluir. Depois de salvar ou excluir, invalidam a chave do próprio
cadastro e `["insumos"]`, porque a lista de insumos mostra os nomes deles.

- *Alternativa*: item próprio no menu lateral. Descartada: os cadastros só
  existem para servir aos insumos.

### 5. Escrita sem modo de demonstração

As funções novas de criar, atualizar e excluir fornecedor, fabricante e marca
propagam a recusa do backend com `erroDoBackend` e, sem resposta, falham com
mensagem de servidor indisponível, como as escritas do Financeiro.

### 6. Produto existente no "Novo Insumo"

Só no cadastro, o formulário ganha a escolha "Produto existente / Produto novo".
O combo de produto existente lista `GET /api/produtos` filtrado no frontend:
produtos ativos e sem insumo, cruzando com `id_produto` dos insumos já
carregados. Escolhido o produto, os campos do produto são preenchidos e
travados, e o payload leva `id_produto` em vez de `produto`. A edição de insumo
continua como hoje.

- *Por quê*: o backend já aceita `id_produto`; filtrar no frontend evita mudar a
  resposta de produtos. A recusa do backend cobre a corrida entre duas telas.

## Risks / Trade-offs

- [Fornecedor/fabricante cadastrado com CNPJ fora do padrão antes da change] →
  hoje não há nenhum; um registro assim só é barrado se o CNPJ for reenviado na
  edição.
- [Lista de produtos sem insumo depende da lista de insumos carregada] → o
  backend recusa o produto que já tem insumo, e o erro aparece na tela.

## Migration Plan

1. Publicar o backend antes do frontend: as mudanças só trocam 500 por 400 e
   acrescentam uma recusa no cadastro de insumo.
2. Reversão: voltar o código. Não há mudança de banco.
