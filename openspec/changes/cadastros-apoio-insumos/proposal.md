# Cadastros de apoio dos insumos

## Why

O backend já tem as rotas de fornecedor, fabricante, marca e produto, mas não
existe tela para nenhum deles: só dá para escolhê-los nos combos do "Novo
Insumo". Excluir um fornecedor, fabricante ou marca usado por um produto, ou
repetir um CNPJ de fornecedor ou o nome de um fabricante, termina em erro 500. E
o "Novo Insumo" sempre cria um produto novo, embora o backend aceite um produto
existente: hoje 9 dos 10 produtos cadastrados estão sem insumo.

## What Changes

### Backend
- Fornecedor, fabricante e marca usados por algum produto, e fornecedor usado
  numa entrada de estoque, não podem ser excluídos: a exclusão responde HTTP 400
  com mensagem de que o cadastro está em uso. Fornecedor e fabricante podem ser
  inativados; a marca não tem situação.
- CNPJ de fornecedor repetido, CNPJ de fornecedor ou fabricante sem 14 dígitos e
  nome de fabricante repetido (sem diferenciar maiúsculas de minúsculas) passam
  a responder HTTP 400 em vez de 500.
- Um produto que já tem insumo não pode receber outro: o cadastro de insumo com
  esse `id_produto` responde HTTP 400.

### Frontend
- O módulo Insumos ganha a aba "Cadastros", com as seções Fornecedores,
  Fabricantes e Marcas: lista, cadastro, edição, inativação (fornecedor e
  fabricante) e exclusão, com as recusas do backend na tela.
- O "Novo Insumo" ganha a escolha entre produto existente e produto novo. Com
  produto existente, os dados do produto aparecem preenchidos e travados, e só
  os dados de estoque são informados.
- Depois de salvar ou excluir um cadastro, os combos do formulário de insumo e
  da movimentação são atualizados sem recarregar a página.

### Fora do escopo
- Tela própria de produto e de categoria de insumo.
- Endereço do fornecedor (`id_logradouro`) na tela.
- Vínculo entre marca e fabricante.
- Compra de insumo gerando despesa no Financeiro.

## Capabilities

### New Capabilities
- `fornecedor`: cadastro, consulta, atualização e exclusão protegida de
  fornecedores.
- `fabricante`: cadastro, consulta, atualização e exclusão protegida de
  fabricantes.

### Modified Capabilities
- `marca`: a exclusão é recusada quando a marca está em uso por um produto.
- `insumo`: um produto passa a ter no máximo um insumo.

## Impact

- **Backend**: `services/fornecedor_service.py`, `services/fabricante_service.py`,
  `services/marca_service.py`, `services/insumo_service.py` e os controllers de
  fornecedor, fabricante e marca (status 400 para a recusa de exclusão).
  `insomnia_safraviva.json` ganha as requisições de fornecedor e fabricante.
- **Banco**: sem migration.
- **API**: nenhuma rota nova nem removida. Respostas 500 viram 400 nos casos
  acima; `DELETE` de fornecedor, fabricante e marca em uso passa a responder 400.
- **Frontend** (`frontendweb`): `src/services/api.ts`, novos componentes da aba
  "Cadastros" em `src/components/insumos/`, `InsumosModule.tsx`,
  `InsumoForm.tsx` e `src/services/insumosAdapter.ts` com testes.
