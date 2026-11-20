# Tasks

## 1. Matriz de papéis (backend)

- [x] 1.1 Em `services/safra_ia/permissoes.py`, trocar `PERFIS_FINANCEIROS` e
      `PERSONA_POR_PERFIL` por `MODULOS_POR_PAPEL` (8 papéis, espelhando os
      módulos com "Visualizar" de `PERFIS_PADRAO` do frontend, com comentário
      de sincronia), `PAPEIS` (nome, foco, tom, saudação e 4 sugestões por
      papel + `colaborador` genérico) e as funções `papel_do_perfil`,
      `modulos_do_papel` e `ve_financeiro`; verificar com teste que perfil
      desconhecido resolve para `colaborador` sem módulos e que `financeiro`
      só tem `Financeiro`.
- [x] 1.2 Em `services/safra_ia/tools.py`, trocar a flag `financeiro` de cada
      tool por `modulos` conforme a tabela "Consultas permitidas por papel" e
      reescrever `tools_permitidas(perfil)` e `executar_tool(nome, args,
      id_empresa, perfil)` para checar módulos e injetar `ver_valores`;
      atualizar os testes existentes de `tests/test_safra_ia.py` e verificar
      com `python -m pytest tests/test_safra_ia.py` os cenários "Agrônomo
      pergunta sobre lucro", "Financeiro pergunta sobre estoque", "Operador
      pergunta sobre suas atividades" e "Consulta não liberada pedida mesmo
      assim" (tool pedida fora do papel devolve `erro` e não entra na
      resposta).

## 2. Contexto por papel e endpoints (backend)

- [x] 2.1 Em `services/safra_ia/agente.py`, montar o prompt de sistema com
      nome, papel, foco, tom e módulos fora do papel, devolver `papel` (sem
      `persona`) e as sugestões de `PAPEIS`; verificar com teste que o prompt
      do `administrador` o trata como administrador da fazenda, que a resposta
      não tem `persona` e que um campo extra `persona: administrador` enviado
      por um `estoquista` é ignorado.
- [x] 2.2 Criar `GET /api/safra-ia/perfil` em
      `controllers/safra_ia_controller.py` (autenticado, fora do limite por
      minuto); verificar com teste os cenários "Perfil do estoquista", "Perfil
      do gerente agrícola" e "Perfil sem login".
- [x] 2.3 Adicionar ao `insomnia_safraviva.json` as requisições
      `POST /api/safra-ia/consultar` e `GET /api/safra-ia/perfil` com o
      header `Authorization`; verificar que o JSON é válido
      (`python -c "import json; json.load(open('insomnia_safraviva.json', encoding='utf-8'))"`).

## 3. Consultas operacionais novas (backend)

- [x] 3.1 Implementar `resumo_propriedades` (propriedades ativas, áreas e
      talhões ativos por propriedade); verificar com teste "Número de
      propriedades" (2 ativas + 1 inativa → 2), "Empresa sem propriedades" e
      "Propriedades de outra empresa".
- [x] 3.2 Implementar `equipe` (funcionários ativos e não desligados por
      propriedade e cargo); verificar com teste "Tamanho da equipe" e que
      funcionário desligado ou de outra empresa não conta.
- [x] 3.3 Implementar `maquinas` (horas e atividades por máquina, custo só com
      `ver_valores`); verificar com teste "Máquina mais usada", "Máquina usada
      só por outra empresa" e que o `supervisor-campo` não recebe valores em
      reais.
- [x] 3.4 Implementar `consumo_insumos` (quantidade por produto, filtros de
      safra e talhão, custo só com `ver_valores`); verificar com teste
      "Consumo por safra", "Consumo sem custo para o agrônomo" e "Consumo com
      custo para o administrador".
- [x] 3.5 Implementar `movimentacoes_estoque` (entradas/saídas por produto,
      padrão 30 dias, filtros de tipo e produto); verificar com teste "Saídas
      do mês" e que movimentações de outra empresa ou fora do período não
      entram.
- [x] 3.6 Implementar `fornecedores` (entradas e última entrada por
      fornecedor, valor comprado só com `ver_valores`); verificar com teste
      "Estoquista pergunta sobre fornecedores" e que fornecedor com entradas
      só em outra empresa não aparece.

## 4. Consultas financeiras novas (backend)

- [x] 4.1 Implementar `fluxo_mensal` (receitas, despesas e saldo por mês,
      padrão 12 meses, alerta para saldo negativo); verificar com teste "Mês
      com prejuízo".
- [x] 4.2 Implementar `custos_centro_custo` (despesas por centro de custo,
      "Sem centro de custo" para vazios, ordem decrescente); verificar com
      teste "Maior centro de custo".
- [x] 4.3 Implementar `custo_por_hectare` (despesas da safra / área
      plantada); verificar com teste "Custo por hectare da safra"
      (R$ 50.000,00 / 100 ha → R$ 500,00/ha) e "Safra sem área".
- [x] 4.4 Rodar `python -m pytest` completo e verificar que toda a suíte do
      backend passa, incluindo `tests/test_auth.py`.

## 5. Chat sem seleção de papel (frontend `frontendweb`)

- [x] 5.1 Em `src/types/safraIA.ts` e `src/services/safraIAMock.ts`, trocar
      personas por `PAPEIS_DEMO` (8 papéis + genérico, financeiro derivado dos
      módulos) e remover `resolverPersona`; atualizar
      `safraIAMock.test.ts` e verificar com `npm test` o cenário "Modo
      demonstração respeita o login" (agrônomo sem lucro) e que o
      `gerente-agricola` vê financeiro.
- [x] 5.2 Em `src/services/api.ts`, criar `getPerfilSafraIA()` com fallback
      para `PAPEIS_DEMO` sem token ou sem backend, e enviar o papel do login ao
      mock; atualizar `safraIAApi.test.ts` e verificar com `npm test`.
- [x] 5.3 Em `src/components/safraia/SafraIAAssistant.tsx`, remover
      `personaOverride`, `trocarPersona` e o bloco "Visualizar como", e usar o
      perfil do assistente no cabeçalho, saudação e sugestões; verificar com
      `npm run lint`, `npx tsc --noEmit` sem erros novos e no navegador o
      cenário "Administrador abre o chat".

## 6. Verificação integrada

- [ ] 6.1 Com backend e frontend no ar, entrar como `administrador`,
      `agronomo`, `financeiro` e `estoquista` e verificar no chat que o
      cabeçalho mostra o papel, que "quantas propriedades eu tenho?" responde
      para quem visualiza Propriedades e é recusada com explicação para
      financeiro e estoquista, e que não há seletor de papel. Verificar também
      `openspec validate safraia-contexto-por-papel --strict`.
