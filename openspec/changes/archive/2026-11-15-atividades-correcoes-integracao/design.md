# Design

## Context

Motivação e escopo em `proposal.md`. O que condiciona o desenho:

- **Dois repositórios**: backend Flask (este) e `frontendweb` (React/Vite). As
  regras e o contrato ficam no backend; o frontend só antecipa as validações.
- **Movimentação de estoque**: `movimentacao_estoque.id_atividade` aponta para
  `tipo_atividade`. A tela de saída, porém, lista as **operações** do talhão em
  "Atividade Relacionada".
- **Módulo de Insumos do frontend**: foi escrito por outra pessoa sobre um
  contrato próprio (`Insumo` com `id`/`nome`/`categoria`/`lotes`, movimentação
  com `tipo: "Entrada" | "Saída"`, rota `/api/movimentacoes-estoque`). Hoje
  `getInsumos` devolve o JSON do backend sem traduzir, e a movimentação cai num
  registro local quando o POST falha.
- **Cache compartilhado**: Início, Notificações, Relatórios e SafraIA usam
  `useQuery` com as chaves `["atividades"]`, `["talhoes"]` e `["insumos"]` e as
  mesmas funções de `api.ts`.
- **Fuso**: o container roda em UTC. Verificado na imagem atual:
  `zoneinfo` resolve `America/Sao_Paulo` sem dependência nova, e às 22h locais a
  data UTC já é a do dia seguinte.
- **Sem testes automatizados no backend**; o frontend tem `vitest`.
- **Migrations** são geradas dentro do container e não são versionadas.

## Goals / Non-Goals

**Goals:**
- Regras da operação conferidas no backend, valendo igual para criação e
  atualização.
- Saída de estoque gravada de verdade e ligada à operação, sem reescrever as
  telas de Insumos.
- Nenhuma alteração de comportamento nas telas de outros módulos além de
  passarem a receber insumos e movimentações reais no formato que já esperam.

**Non-Goals:**
- Alinhar o cadastro de insumo (`POST /api/insumos`) e o script
  `seed-insumos.mjs` ao contrato do backend.
- Lotes: insumos reais chegam às telas com `lotes` vazio, então os alertas de
  validade não aparecem para eles.
- Remover os dados de demonstração dos demais módulos.
- Restrição de unicidade no banco e paginação.

## Decisions

### 1. Operação em coluna nova, mantendo o tipo

`movimentacao_estoque` ganha `id_atividade_agricola` (inteiro, opcional, FK para
`atividade_agricola` com `ON DELETE SET NULL`). `id_atividade` continua
apontando para o tipo e é preenchido a partir da operação quando não vier no
payload; se vier divergente, ou se `id_talhao` divergir do talhão da operação, a
movimentação é recusada.

- *Por quê*: preserva os dados e os relatórios por tipo, permite saber o consumo
  de cada operação e mantém o histórico de estoque quando a operação é excluída.
- *Alternativas*: repontar `id_atividade` para a operação (muda o significado de
  uma coluna com dados e quebra a regressão já testada); guardar só o tipo
  (descartada pela decisão de vincular à operação).

### 2. Regras da operação sobre o estado resultante

Criação e atualização passam por uma única validação aplicada ao estado final da
operação (valores atuais sobrepostos pelo payload), antes do commit: tipo
pertence à categoria, `Concluída` exige `data_fim` e não há outra operação com o
mesmo talhão, tipo e data de início (consulta excluindo a própria).

- *Por quê*: o `PUT` é parcial; validar só os campos enviados deixaria passar,
  por exemplo, a troca isolada da categoria.
- *Alternativa*: `UNIQUE (id_talhao, id_tipo_atividade, data_inicio)` no banco.
  É mais forte sob concorrência, mas faria a migration falhar em ambientes que
  já tenham duplicatas e não dá a mensagem amigável; fica para depois.

### 3. Exclusão de catálogo em uso conferida antes de excluir

Os serviços de categoria, tipo e máquina consultam as referências antes do
`delete` e levantam erro de regra com mensagem específica. Nos controllers, o
`DELETE` passa a distinguir "não encontrado" (404) dos demais erros de regra
(400), como os `PUT` já fazem.

- *Alternativa*: capturar o `IntegrityError` do banco. Descartada por não
  permitir dizer o que está usando o registro.

### 4. Data local no código, não na infraestrutura

A data corrente usada em `atrasada` vem de `zoneinfo`, com o fuso lido de
`APP_TIMEZONE` (padrão `America/Sao_Paulo`). No frontend, o `hoje()` de
`types/atividade.ts` passa a montar a data com os componentes locais em vez de
`toISOString()`.

- *Alternativa*: definir `TZ` no `docker-compose`. Descartada porque a correção
  dependeria da configuração de cada ambiente.

### 5. Data da movimentação recebida como data

`data_movimentacao` entra como data (o formulário só tem dia). É gravada
combinada com a hora UTC corrente, que é a convenção já usada pelo valor padrão
da coluna, mantendo a ordenação dentro do dia. O valor inicial do campo no
formulário passa a ser a data local.

### 6. Tradução em módulo próprio no frontend

Um módulo `src/services/insumosAdapter.ts`, só com funções puras e testado com
`vitest`, converte:

| Direção | Conversão |
|---|---|
| insumo do backend -> `Insumo` | `id_insumo`->`id`, `nome_produto`->`nome`, `categoria_nome`->`categoria` (casada com as categorias conhecidas; sem correspondência, usa a regra de `categoriaDoProduto`), `fabricante_nome`, `descricao_marca`, `status` booleano -> `Ativo`/`Inativo`, `lotes` vazio |
| movimentação do backend -> `MovimentacaoEstoque` | `id_movimentacao`->`id`, `ENTRADA`/`SAIDA` -> `Entrada`/`Saída`, `id_funcionario`/`funcionario_nome` -> `id_responsavel`/`responsavel`, `fornecedor_nome`, `numero_nota_fiscal`->`nota_fiscal`, `destino_finalidade`->`destino`, `id_atividade_agricola`->`id_atividade`, `atividade_descricao`->`atividade`, data reduzida a `AAAA-MM-DD` |
| `NovaMovimentacaoPayload` -> backend | o inverso, enviando só os campos do tipo (entrada ou saída) |

`api.ts` chama essas funções em `getInsumos`, `getMovimentacoes` e
`criarMovimentacao`, e passa a usar `/api/movimentacoes`.

- *Por quê*: as telas de Insumos continuam com os tipos que já usam; a diferença
  de contrato fica num único lugar, coberto por teste.
- *Consequência*: `id_responsavel` da movimentação vira `string` (UUID) nos
  tipos e no mock; o payload ganha `id_fornecedor`; o formulário de atividade
  passa a ler `id`/`nome` do insumo já traduzido.

### 7. Erro do backend aparece; demonstração só sem backend

`criarMovimentacao` propaga o erro quando o backend respondeu (com a mensagem do
campo `error`) e mantém o registro local apenas quando não houve resposta. É o
mesmo critério de `excluirLancamento`. O módulo de Insumos já exibe
`erro.message`, então não precisa mudar.

### 8. Leituras "só cadastrados" para os formulários

`getTalhoesCadastrados` e `getInsumosCadastrados` devolvem apenas o que veio do
backend e propagam a falha. Os formulários de atividade e de movimentação usam
essas funções com chaves próprias (`["talhoes","cadastrados"]`,
`["insumos","cadastrados"]`), para não dividir cache com as consultas que caem
em dados de demonstração. `getTalhoes` e `getInsumos` mantêm o comportamento
atual para os outros módulos.

As atividades seguem o mesmo padrão: `getAtividadesCadastradas`, com a chave
`["atividades","cadastradas"]`, é usada pelo módulo de Atividades e por
"Atividade Relacionada"; `getAtividades` mantém o retorno de demonstração para
os outros módulos. A invalidação por `["atividades"]` alcança as duas chaves.

- *Alternativa*: tirar o mock das funções existentes para todos. Descartada por
  mudar telas de outros módulos. Chegou a ser aplicada em `getAtividades`, mas o
  teste com o backend parado deixou a tela Início em "Carregando" por cerca de
  um minuto, e a mudança foi desfeita.

### 9. Inativos filtrados no formulário

Os combos omitem itens com `status` falso (ou `Inativo`), exceto o que já está
selecionado na operação em edição. A checagem de duplicidade na tela usa a lista
carregada, apenas para resposta imediata; quem decide é o backend.

## Risks / Trade-offs

- [Conflito de merge com o módulo de Insumos, que recebeu commits em 13/11] →
  mudanças concentradas no módulo novo, em `api.ts` e em um formulário; trabalho
  em branch própria; avisar a autora antes do merge.
- [Regras novas recusam payloads antes aceitos] → o único consumidor é o
  frontend do projeto, que já valida os mesmos casos na tela.
- [Insumos reais sem lotes nas telas] → alertas de validade ficam vazios para
  eles; registrado como não objetivo.
- [`seed-insumos.mjs` segue incompatível com o backend] → já falha hoje (rota
  inexistente); não muda.
- [Um único fuso por instalação] → `APP_TIMEZONE` cobre propriedades fora do
  horário de Brasília.
- [Data informada combinada com hora UTC] → a ordenação entre movimentações com
  e sem data informada no mesmo dia pode não refletir a ordem real de registro.
- [Migration não versionada] → o passo de geração e a revisão ficam descritos
  nas tasks; versionar migrations continua fora do escopo.

## Migration Plan

1. Gerar a migration no container (`flask db migrate`), revisar que contém
   apenas a coluna `id_atividade_agricola` e sua FK, e aplicar com
   `flask db upgrade`.
2. Publicar o backend antes do frontend: os campos novos são opcionais e as
   rotas não mudam.
3. Reversão: `flask db downgrade` remove a coluna; o código anterior não a usa.

## Open Questions

- Qual contrato o script `seed-insumos.mjs` deve seguir é uma conversa com a
  autora do módulo de Insumos; não altera esta change.
