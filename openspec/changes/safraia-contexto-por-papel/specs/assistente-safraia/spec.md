# Spec Delta

## Purpose

Assistente de IA do SafraViva (SafraIA) que responde, em linguagem natural, a
perguntas sobre a fazenda com dados da empresa do usuário logado, adaptando o
contexto, as sugestões e as consultas permitidas ao papel do login.

## ADDED Requirements

### Requirement: Consulta autenticada e limitada

O sistema SHALL expor `POST /api/safra-ia/consultar` apenas para usuários
autenticados, recebendo `pergunta` (1 a 1000 caracteres após remover espaços
das pontas) e limitando a quantidade de perguntas por usuário por minuto.

#### Scenario: Sem login

- **WHEN** um `POST /api/safra-ia/consultar` é feito sem token válido
- **THEN** a resposta é HTTP 401

#### Scenario: Pergunta vazia

- **WHEN** um usuário autenticado envia `pergunta` só com espaços
- **THEN** a resposta é HTTP 422 com mensagem pedindo uma pergunta de até 1000
  caracteres

#### Scenario: Limite por minuto excedido

- **WHEN** um usuário passa do limite de perguntas configurado dentro de 60
  segundos
- **THEN** a resposta é HTTP 429 pedindo para aguardar um minuto

### Requirement: Papel definido pelo login

O assistente SHALL identificar o papel do usuário exclusivamente pelo perfil
do usuário autenticado. Nenhum campo da requisição SHALL alterar o papel, as
consultas permitidas ou o contexto usado na resposta.

#### Scenario: Administrador reconhecido

- **WHEN** um usuário com perfil `administrador` faz uma pergunta
- **THEN** o assistente responde tratando-o como administrador da fazenda e a
  resposta traz `papel` igual a `administrador`

#### Scenario: Tentativa de trocar de papel pela requisição

- **WHEN** um usuário com perfil `estoquista` envia a pergunta com um campo
  extra `persona` ou `papel` igual a `administrador`
- **THEN** o campo extra é ignorado, a resposta traz `papel` igual a
  `estoquista` e só consultas do estoquista ficam disponíveis

### Requirement: Contexto da conversa por papel

Para cada papel (`administrador`, `proprietario`, `gerente-agricola`,
`agronomo`, `supervisor-campo`, `financeiro`, `estoquista`, `operador`) o
assistente SHALL usar um nome de exibição, um foco de atuação e um tom
próprios, e SHALL orientar a resposta às responsabilidades daquele papel na
fazenda.

#### Scenario: Mesma pergunta, papéis diferentes

- **WHEN** um `supervisor-campo` e um `financeiro` perguntam "como está a
  fazenda?"
- **THEN** a resposta do supervisor prioriza atividades, talhões e insumos, e
  a do financeiro prioriza resultado, custos e fluxo de caixa

### Requirement: Módulos visualizados por papel

O assistente SHALL considerar, para cada papel, os módulos que o perfil
padrão dele pode visualizar em Configurações › Perfis:

| Papel | Módulos visualizados |
|---|---|
| administrador | todos |
| proprietario | Propriedades, Talhões, Funcionários, Atividades, Financeiro, Insumos |
| gerente-agricola | Propriedades, Talhões, Funcionários, Atividades, Financeiro, Insumos |
| agronomo | Propriedades, Talhões, Atividades, Insumos |
| supervisor-campo | Talhões, Atividades, Insumos |
| financeiro | Financeiro |
| estoquista | Atividades, Insumos |
| operador | Atividades |

#### Scenario: Perfil do gerente agrícola

- **WHEN** um `gerente-agricola` consulta o perfil do assistente
- **THEN** as consultas liberadas incluem as de Propriedades, Talhões,
  Funcionários, Atividades, Financeiro e Insumos

### Requirement: Consultas permitidas por papel

O assistente SHALL usar apenas as consultas liberadas ao papel. Uma consulta
é liberada se o papel visualiza ao menos um dos módulos exigidos por ela:

| Consulta | Módulos exigidos (qualquer um) |
|---|---|
| resumo de propriedades | Propriedades |
| área disponível (talhões) | Talhões |
| safras | Talhões, Atividades ou Financeiro |
| atividades, uso de máquinas | Atividades |
| consumo de insumos | Atividades ou Insumos |
| ranking de funcionários, equipe | Funcionários |
| estoque, lotes a vencer, movimentações, fornecedores | Insumos |
| custos, lucro, fluxo mensal, centro de custo, custo/ha | Financeiro |

#### Scenario: Agrônomo pergunta sobre lucro

- **WHEN** um `agronomo` pergunta qual o lucro por safra
- **THEN** nenhuma consulta financeira é executada e o texto explica que essa
  informação é de papéis com acesso ao Financeiro

#### Scenario: Estoquista pergunta sobre fornecedores

- **WHEN** um `estoquista` pergunta quais fornecedores mais entregaram
- **THEN** a consulta de fornecedores é executada e a resposta traz a tabela
  de fornecedores da empresa

#### Scenario: Financeiro pergunta sobre estoque

- **WHEN** um `financeiro` pergunta quais insumos estão abaixo do mínimo
- **THEN** a consulta de estoque não é executada e o texto explica que essa
  informação é de papéis com acesso a Insumos

#### Scenario: Operador pergunta sobre suas atividades

- **WHEN** um `operador` pergunta quantas atividades estão atrasadas
- **THEN** a consulta de atividades é executada e a resposta traz o total de
  atrasadas

#### Scenario: Consulta não liberada pedida mesmo assim

- **WHEN** o modelo de IA tenta executar uma consulta fora dos módulos do papel
- **THEN** a consulta não roda, nenhum dado dela entra na resposta e o
  assistente informa que o papel não tem acesso

### Requirement: Papel desconhecido

Um usuário cujo perfil não esteja entre os oito papéis SHALL não ter nenhuma
consulta de dados liberada e SHALL receber contexto genérico de colaborador da
fazenda, podendo receber apenas orientações gerais de gestão rural.

#### Scenario: Perfil não mapeado

- **WHEN** um usuário com perfil `visitante` pergunta quantas propriedades a
  fazenda tem
- **THEN** nenhuma consulta roda e o assistente informa que o papel não tem
  acesso a dados da fazenda

### Requirement: Isolamento por empresa

Toda consulta do assistente SHALL considerar somente dados da empresa do
usuário autenticado, inclusive para cadastros que não têm empresa própria
(máquinas, fornecedores e centros de custo), que só aparecem quando usados em
registros da empresa.

#### Scenario: Máquina usada só por outra empresa

- **WHEN** a máquina "Trator X" aparece apenas em atividades de outra empresa
  e um `supervisor-campo` pergunta sobre o uso de máquinas
- **THEN** "Trator X" não aparece na resposta

#### Scenario: Propriedades de outra empresa

- **WHEN** um `administrador` pergunta quantas propriedades a fazenda tem
- **THEN** a contagem considera apenas propriedades da empresa dele

### Requirement: Resumo de propriedades

O assistente SHALL responder quantas propriedades ativas a empresa tem e, por
propriedade, a área total, agricultável, de preservação e de pastagem e o
número de talhões ativos, com os totais da empresa.

#### Scenario: Número de propriedades

- **WHEN** a empresa tem 2 propriedades ativas e 1 inativa e um
  `proprietario` pergunta quantas propriedades tem
- **THEN** a resposta traz o destaque "Propriedades" com valor 2 e uma tabela
  com as duas propriedades ativas e suas áreas

#### Scenario: Empresa sem propriedades

- **WHEN** a empresa não tem propriedades cadastradas
- **THEN** o assistente informa que não há propriedades e sugere cadastrá-las

### Requirement: Movimentações de estoque

O assistente SHALL resumir entradas e saídas de estoque da empresa por produto
em um período (padrão: últimos 30 dias), com filtro opcional por tipo
(entrada ou saída) e por nome de produto.

#### Scenario: Saídas do mês

- **WHEN** um `estoquista` pergunta o que saiu do estoque este mês
- **THEN** a resposta traz, por produto, a quantidade de saídas do período e o
  total de movimentações

### Requirement: Fornecedores

O assistente SHALL listar os fornecedores que têm entradas de estoque na
empresa, com quantidade de entradas e data da última entrada, ordenados pela
quantidade de entradas.

#### Scenario: Ranking de fornecedores

- **WHEN** um usuário com acesso pergunta quais são os principais fornecedores
- **THEN** a resposta traz a tabela de fornecedores com entradas e última
  entrada

### Requirement: Uso de máquinas

O assistente SHALL resumir, por máquina, as horas e o número de atividades da
empresa em que ela foi usada.

#### Scenario: Máquina mais usada

- **WHEN** um `supervisor-campo` pergunta qual máquina foi mais usada
- **THEN** a resposta destaca a máquina com mais horas e traz a tabela de
  horas e atividades por máquina

### Requirement: Equipe por propriedade

O assistente SHALL informar os funcionários ativos vinculados às propriedades
da empresa, agrupados por propriedade e cargo.

#### Scenario: Tamanho da equipe

- **WHEN** um `administrador` pergunta quantos funcionários trabalham em cada
  propriedade
- **THEN** a resposta traz o total de funcionários ativos e a contagem por
  propriedade e cargo

### Requirement: Consumo de insumos

O assistente SHALL somar os insumos aplicados nas atividades da empresa por
produto, com filtro opcional por safra e por talhão.

#### Scenario: Consumo por safra

- **WHEN** um `agronomo` pergunta quanto de NPK foi aplicado na safra
  "2025/2026"
- **THEN** a resposta traz a quantidade aplicada por produto nas atividades
  daquela safra, com a unidade

### Requirement: Fluxo mensal

O assistente SHALL apresentar receitas, despesas e saldo por mês a partir dos
lançamentos da empresa, no período pedido (padrão: últimos 12 meses).

#### Scenario: Mês com prejuízo

- **WHEN** um `financeiro` pergunta como foi o fluxo de caixa no ano
- **THEN** a resposta traz uma linha por mês com receitas, despesas e saldo e
  um alerta para os meses com saldo negativo

### Requirement: Custos por centro de custo

O assistente SHALL somar as despesas da empresa por centro de custo no período
pedido, agrupando as sem centro de custo como "Sem centro de custo".

#### Scenario: Maior centro de custo

- **WHEN** um `proprietario` pergunta onde está gastando mais
- **THEN** a resposta traz as despesas por centro de custo, da maior para a
  menor

### Requirement: Custo por hectare

O assistente SHALL calcular, por safra da empresa, as despesas vinculadas à
safra divididas pela área plantada. Safra sem área plantada SHALL aparecer sem
custo por hectare, com a indicação de área não informada.

#### Scenario: Custo por hectare da safra

- **WHEN** a safra "Soja 25/26" tem R$ 50.000,00 de despesas e 100 ha
  plantados
- **THEN** a resposta mostra R$ 500,00/ha para essa safra

#### Scenario: Safra sem área

- **WHEN** uma safra tem despesas mas não tem área plantada
- **THEN** ela aparece com "área não informada" no lugar do custo por hectare

### Requirement: Valores monetários restritos

Somente papéis que visualizam o módulo Financeiro SHALL receber valores de
custo de atividades, de máquinas, de insumos aplicados e de compras. Para os
demais papéis, as consultas operacionais SHALL responder apenas quantidades.
O valor do estoque e o valor em risco de lotes continuam visíveis a quem
consulta estoque.

#### Scenario: Consumo sem custo para o agrônomo

- **WHEN** um `agronomo` consulta o consumo de insumos
- **THEN** a resposta traz quantidades e não traz nenhum valor em reais

#### Scenario: Consumo com custo para o administrador

- **WHEN** um `administrador` consulta o consumo de insumos
- **THEN** a resposta traz quantidades e o custo por produto

### Requirement: Perfil do assistente

O sistema SHALL expor `GET /api/safra-ia/perfil` para o usuário autenticado,
retornando `papel`, `nome_papel`, `foco`, `saudacao`, `sugestoes` e
`consultas` (nome e descrição de cada consulta liberada ao papel).

#### Scenario: Perfil do estoquista

- **WHEN** um `estoquista` faz `GET /api/safra-ia/perfil`
- **THEN** a resposta é HTTP 200 com `papel` igual a `estoquista`, sugestões
  de estoque e somente as consultas liberadas ao estoquista

#### Scenario: Perfil sem login

- **WHEN** `GET /api/safra-ia/perfil` é feito sem token válido
- **THEN** a resposta é HTTP 401

### Requirement: Resposta da consulta

A resposta de `POST /api/safra-ia/consultar` SHALL trazer `intent`, `texto`,
`sugestoes` do papel, `origem` igual a `backend` e `papel`, e, quando houver,
`destaques`, `alertas` e `tabela` vindos das consultas executadas. A resposta
SHALL deixar de trazer o campo `persona`.

#### Scenario: Resposta com dados

- **WHEN** um `administrador` pergunta quantas propriedades tem
- **THEN** a resposta é HTTP 200 com `papel` igual a `administrador`,
  `intent` contendo `resumo_propriedades`, destaques e tabela, e sem o campo
  `persona`

### Requirement: Chat sem seleção de papel

O chat do SafraIA SHALL mostrar o papel do usuário logado no cabeçalho, com a
saudação e as sugestões desse papel, e SHALL NOT oferecer seleção ou troca de
papel ou persona. No modo demonstração (sem backend), o chat SHALL usar o
mesmo papel do login.

#### Scenario: Administrador abre o chat

- **WHEN** um `administrador` abre o chat
- **THEN** o cabeçalho mostra "Administrador", a saudação é a do
  administrador e não existe seletor "Visualizar como"

#### Scenario: Modo demonstração respeita o login

- **WHEN** o backend do SafraIA está indisponível e um `agronomo` pergunta
  sobre lucro
- **THEN** a resposta de demonstração informa que o papel não tem acesso a
  dados financeiros
