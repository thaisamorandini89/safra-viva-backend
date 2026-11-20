# SafraIA com contexto pelo papel do usuário

## Why

O chat do SafraIA tem um seletor "Visualizar como" que deixa qualquer usuário
trocar de persona (Produtor, Agrônomo, Administrador, Gerente). Isso confunde,
porque o acesso real é decidido pelo perfil do login no backend, e quatro
personas não representam os oito papéis de Configurações › Perfis
(`administrador`, `proprietario`, `gerente-agricola`, `agronomo`,
`supervisor-campo`, `financeiro`, `estoquista`, `operador`). O acesso do
assistente também não segue as permissões desses papéis: hoje o financeiro
consulta atividades e o estoquista consulta talhões, embora esses módulos não
sejam deles. Além disso, o assistente só responde oito consultas e não sabe
perguntas básicas, como quantas propriedades a fazenda tem.

## What Changes

### Backend
- O assistente passa a se apresentar e responder pelo papel do usuário logado:
  ao entrar como `administrador`, ele sabe que fala com o administrador da
  fazenda e ajusta tom, foco, saudação e sugestões a esse papel. Não há troca
  de papel dentro do chat.
- As consultas de cada papel passam a seguir os módulos que o perfil padrão
  dele pode visualizar em Configurações › Perfis (Propriedades, Talhões,
  Funcionários, Atividades, Financeiro, Insumos). A regra única "pode ou não
  ver financeiro" sai. Papéis amplos ganham muitas consultas novas; papel
  desconhecido não recebe nenhuma consulta de dados.
- **BREAKING** (comportamento): alguns papéis perdem consultas que tinham fora
  dos seus módulos. O `financeiro` deixa de ver talhões, atividades, ranking
  de funcionários, estoque e lotes; o `estoquista` deixa de ver talhões e
  ranking; `agronomo` e `supervisor-campo` deixam de ver o ranking de
  funcionários; perfil fora da lista deixa de ter as consultas operacionais.
- Novas consultas, todas filtradas pela empresa do usuário:
  - `resumo_propriedades`: número de propriedades, áreas (total,
    agricultável, preservação, pastagem) e número de talhões por propriedade.
  - `movimentacoes_estoque`: entradas e saídas por período e produto.
  - `fornecedores`: fornecedores com entradas de estoque na empresa.
  - `maquinas`: uso de máquinas (horas e atividades) nas atividades da empresa.
  - `equipe`: funcionários ativos por propriedade e cargo.
  - `consumo_insumos`: insumos aplicados por safra e talhão.
  - `fluxo_mensal`: receitas, despesas e saldo por mês.
  - `custos_centro_custo`: despesas por centro de custo.
  - `custo_por_hectare`: despesas da safra divididas pela área plantada.
- Custos de atividades (máquinas e insumos aplicados) e valores de compra só
  aparecem para papéis que visualizam o módulo Financeiro, inclusive nas
  consultas operacionais. O valor do estoque e o valor em risco dos lotes continuam
  visíveis a quem consulta estoque, como hoje.
- Novo `GET /api/safra-ia/perfil`: devolve o papel, o nome de exibição, o foco,
  a saudação, as sugestões e as consultas disponíveis ao usuário logado.
- **BREAKING**: a resposta de `POST /api/safra-ia/consultar` troca o campo
  `persona` por `papel` (o perfil real do usuário). O frontend atual não lê
  `persona`.

### Frontend (`frontendweb`)
- Remove o seletor "Visualizar como" e o conceito de persona do chat.
- Cabeçalho, saudação e sugestões vêm de `GET /api/safra-ia/perfil`; no modo
  demonstração (sem backend), usam um mapa local pelo mesmo papel.
- O modo demonstração passa a respeitar o papel do login.

### Fora do escopo
- Respeitar permissões editadas em Configurações › Perfis: essa tela guarda as
  permissões só no navegador, então o backend segue as permissões padrão de
  cada papel.
- Histórico de conversa no servidor.
- Produtividade (sc/ha): o sistema ainda não registra produção colhida.

## Capabilities

### New Capabilities
- `assistente-safraia`: assistente de IA que responde em linguagem natural
  com dados da empresa do usuário, contexto e consultas definidos pelo papel
  do login.

### Modified Capabilities

Nenhuma.

## Impact

- **Depende de**: nada obrigatório. Se `safra-unificada` for aplicada antes, o
  consumo de insumos por safra usa a safra cadastrada da atividade; senão, usa
  o texto da safra gravado na atividade.
- **Backend**: `services/safra_ia/permissoes.py`, `services/safra_ia/agente.py`,
  `services/safra_ia/tools.py`, `controllers/safra_ia_controller.py`,
  `tests/test_safra_ia.py`, `insomnia_safraviva.json` (ganha as rotas do
  SafraIA).
- **Banco**: sem migration.
- **API**: novo `GET /api/safra-ia/perfil`; `POST /api/safra-ia/consultar`
  devolve `papel` no lugar de `persona` e mais consultas por papel.
- **Frontend** (`frontendweb`): `src/components/safraia/SafraIAAssistant.tsx`,
  `src/services/safraIAMock.ts`, `src/types/safraIA.ts`, `src/services/api.ts`
  e testes `safraIAMock.test.ts` / `safraIAApi.test.ts`.
- **LLM**: mais funções declaradas ao Gemini para papéis amplos; o limite de
  chamadas por minuto não muda.
