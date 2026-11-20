# Design

## Context

Motivação em `proposal.md`; comportamento em `specs/assistente-safraia/spec.md`.

Estado atual do backend:
- `services/safra_ia/permissoes.py` tem só `PERFIS_FINANCEIROS` e um mapa
  perfil → persona (4 personas). Perfil fora do mapa cai em `gerente`.
- `services/safra_ia/tools.py` declara 8 consultas em `TOOLS`, cada uma com a
  flag `financeiro`; `tools_permitidas` e `executar_tool` filtram por essa
  flag. Todas recebem `id_empresa` e filtram por
  `Propriedade.id_empresa` (ou `LancamentoFinanceiro.id_empresa`).
- `services/safra_ia/agente.py` monta o prompt de sistema (com o perfil bruto e
  uma frase de restrição financeira), declara as tools permitidas ao
  `ClienteGemini` e devolve `persona` e `SUGESTOES[persona]`.
- O cliente Gemini é injetável por `SAFRAIA_CLIENTE_FACTORY`; os testes usam
  `GeminiFalso`, que executa as tools pedidas.

Restrições de dados que moldam as consultas novas:
- `Maquina`, `Fornecedor` e `CentroCusto` não têm `id_empresa`; só podem ser
  alcançados por registros da empresa (`AtividadeMaquina` → atividade,
  `MovimentacaoEstoque` → insumo → propriedade, `LancamentoFinanceiro`).
- `AtividadeAgricola.safra` é texto (a change `safra-unificada` adiciona
  `id_safra`, mas mantém `safra` com o nome).
- `MovimentacaoEstoque.tipo_movimentacao` usa `ENTRADA`/`SAIDA`.
- As permissões de Configurações › Perfis existem só no frontend
  (`frontendweb/src/components/configuracoes/store.ts`, `PERFIS_PADRAO`) e são
  salvas no navegador.

## Goals / Non-Goals

**Goals:**
- Uma única fonte no backend para papel → módulos → consultas, usada pelo
  prompt, pelas declarações ao Gemini, pela execução e pelo `GET /perfil`.
- Negar no servidor, não só no prompt: consulta fora do papel não executa
  mesmo que o modelo a peça.
- Consultas novas no mesmo formato de resultado das atuais (`dados`,
  `destaques`, `tabela`, `alertas`), para a UI não mudar.

**Non-Goals:**
- Ler permissões customizadas do navegador ou criar tabela de permissões.
- Trocar de provedor de LLM ou mudar `gemini_client.py`.
- Alterar a lógica das 8 consultas existentes além do necessário para ocultar
  valores.

## Decisions

### 1. Matriz por módulo, espelhando `PERFIS_PADRAO`
`permissoes.py` passa a ter `MODULOS_POR_PAPEL` (os módulos com "Visualizar"
de cada perfil padrão) e `PAPEIS` com `nome`, `foco`, `tom`, `saudacao` e
`sugestoes` para os 8 papéis e um papel genérico (`colaborador`) para perfil
desconhecido. Cada tool em `TOOLS` troca a flag `financeiro` por
`modulos: {...}` (qualquer um libera). Funções:
`modulos_do_papel(perfil)`, `ve_financeiro(perfil)` (= tem `Financeiro`),
`tools_permitidas(perfil)`.

- *Alternativa*: lista de papéis em cada tool. Rejeitada: espalha a regra e
  diverge de Configurações; com módulos, mudar um perfil padrão é mudar uma
  linha.
- *Alternativa*: guardar permissões no banco. Rejeitada: fora do escopo (a
  tela de Configurações ainda não persiste no backend).

Comentário em `MODULOS_POR_PAPEL` aponta para `PERFIS_PADRAO` do frontend,
que deve ser mantido em sincronia.

### 2. Negação em duas camadas
Só as tools permitidas são declaradas ao Gemini, e `executar_tool(nome, args,
id_empresa, perfil)` volta a checar o módulo e devolve
`{'erro': 'Seu papel não tem acesso a ...'}` sem rodar a consulta. O agente já
ignora resultados com `erro` na montagem de destaques/tabela. O prompt de
sistema lista os módulos que o papel **não** visualiza, para o modelo explicar
a recusa sem tentar chamar nada (cenários de agrônomo/lucro e
financeiro/estoque).

### 3. Ocultar valores por parâmetro, não por pós-filtro
As consultas com custo (`maquinas`, `consumo_insumos`, `fornecedores`)
recebem `ver_valores: bool`, injetado por `executar_tool` a partir de
`ve_financeiro(perfil)` e nunca vindo do modelo. Sem valores, a função não
calcula nem devolve campos/colunas em reais. `estoque` e `lotes_a_vencer`
continuam como hoje.

- *Alternativa*: remover chaves monetárias do resultado depois. Rejeitada:
  frágil (texto de destaque e células de tabela também carregam valores).

### 4. Escopo por empresa nas consultas novas
- `resumo_propriedades`: `Propriedade` da empresa com `status` verdadeiro;
  talhões ativos por propriedade.
- `maquinas`: `AtividadeMaquina` join `AtividadeAgricola` filtrada por
  `id_propriedade` da empresa (mesmo padrão das tools atuais); agrupa por
  `id_maquina` (ou `nome` quando sem id).
- `fornecedores`: `MovimentacaoEstoque` `ENTRADA` com `id_fornecedor`, join
  `Insumo` nas propriedades da empresa.
- `movimentacoes_estoque`: `MovimentacaoEstoque` join `Insumo`/`Produto` nas
  propriedades da empresa, período padrão 30 dias.
- `equipe`: `FuncionarioPropriedade` nas propriedades da empresa, funcionário
  com `status` ativo e sem `data_desligamento`.
- `consumo_insumos`: `AtividadeInsumo` join `AtividadeAgricola` da empresa;
  filtro de safra compara o texto `AtividadeAgricola.safra` (sem diferenciar
  maiúsculas) e de talhão por código ou nome.
- `fluxo_mensal`, `custos_centro_custo`, `custo_por_hectare`:
  `LancamentoFinanceiro.id_empresa`; centro de custo resolvido por
  `id_centro_custo`; custo/ha usa `Safra.area_plantada` das safras das
  propriedades da empresa.

Todas limitam linhas com `LIMITE_LINHAS` e usam `_moeda`/`_area` existentes.

### 5. Contexto do prompt por papel
`_sistema(usuario, papel)` inclui nome do usuário, nome de exibição do papel,
foco, tom ("você está falando com o administrador da fazenda...") e os módulos
fora do papel. O texto do pedido nunca altera o papel: o controller continua
aceitando só `pergunta` no schema Pydantic (campos extras já são ignorados).

### 6. `GET /api/safra-ia/perfil`
Rota no mesmo blueprint, `@requer_auth`, sem contar no limite por minuto (não
chama o LLM). Resposta montada de `PAPEIS` + `tools_permitidas`:
`{papel, nome_papel, foco, saudacao, sugestoes, consultas: [{nome, descricao}]}`.
`papel` é o perfil em minúsculas (ou `colaborador` se desconhecido).

### 7. Frontend
- `types/safraIA.ts`: remove `SafraIAPersonaId`/`SafraIAPersona`; adiciona
  `SafraIAPerfil` (formato do `GET /perfil`) e `papel` em `SafraIAResposta`;
  `SafraIAConsultaPayload.persona` vira `papel: string`.
- `safraIAMock.ts`: `PERSONAS` vira `PAPEIS_DEMO` com os 8 papéis + genérico
  e `verFinanceiro` derivado dos mesmos módulos; `resolverPersona` é removido;
  `saudacaoInicial`/`responderSafraIA` recebem o papel.
- `api.ts`: `getPerfilSafraIA()` com fallback para `PAPEIS_DEMO` quando não há
  token ou o backend não responde (mesmo padrão de `consultarSafraIA`).
- `SafraIAAssistant.tsx`: remove `personaOverride`, `trocarPersona` e o bloco
  "Visualizar como"; cabeçalho e sugestões iniciais vêm do perfil.

## Risks / Trade-offs

- [Perfis editados em Configurações não valem no SafraIA] → documentado como
  fora do escopo; matriz espelha os perfis padrão, com comentário de
  sincronia.
- [Perda de acesso para financeiro, estoquista, agrônomo, supervisor e perfis
  desconhecidos] → marcada como BREAKING na proposta; a recusa explica qual
  módulo dá acesso.
- [Mais funções declaradas (até 17) podem confundir o modelo leve] →
  descrições curtas e distintas; `MAX_RODADAS` continua 4; testes cobrem
  seleção via `GeminiFalso` e não dependem do modelo real.
- [Consumo por safra depende do texto da safra na atividade] → comparação
  sem diferenciar maiúsculas; com `safra-unificada` o campo passa a trazer o
  nome da safra cadastrada, sem mudança aqui.
- [Desvio entre mapa do backend e `PAPEIS_DEMO` do frontend] → o chat usa o
  `GET /perfil` sempre que há backend; o mapa local só vale no modo
  demonstração.

## Migration Plan

Sem migration de banco. Publicar backend e frontend juntos: o frontend novo
funciona com o backend antigo pelo fallback local de perfil, e o backend novo
não quebra o frontend antigo (que não lê `persona`). Rollback: reverter os
commits; nenhum dado é alterado.
