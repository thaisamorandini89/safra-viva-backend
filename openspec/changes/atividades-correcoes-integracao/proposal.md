# Correções da integração de Atividades (tela, regras e estoque)

## Why

A tela de Atividades passou a usar a API real, mas a revisão da integração
encontrou falhas em três frentes: comportamentos errados na própria tela, regras
que o backend aceita sem conferir e a ligação com o estoque, que hoje não chega
ao backend (a saída de estoque chama uma rota inexistente e é "salva" só em
memória). Corrigir agora evita que dados inconsistentes entrem no banco assim
que o módulo for usado de verdade.

## What Changes

### A. Tela de Atividades
- Volta a barrar atividade duplicada (mesmo talhão, tipo e data de início). A
  validação existia na tela e foi perdida na integração; passa a valer também
  no backend.
- Os combos de Talhão e Insumo do formulário deixam de mostrar dados de
  demonstração quando o cadastro está vazio ou a API falha.
- Quando a API de atividades falha, a tela mostra o aviso de erro em vez de
  atividades de demonstração.
- A operação passa a devolver o nome da propriedade (hoje o detalhe mostra
  "#4" e o CSV mostra o número).
- Categoria, tipo, máquina, funcionário e insumo inativos deixam de aparecer
  nos combos (o item já selecionado numa edição é preservado).

### B. Atividade e estoque (escopo enxuto)
- A movimentação de estoque passa a aceitar o vínculo com a **operação**
  registrada (`id_atividade_agricola`), em coluna nova e opcional. O tipo de
  atividade continua gravado, preenchido a partir da operação.
- A movimentação passa a aceitar a data informada pelo usuário
  (`data_movimentacao`), que hoje é descartada.
- O histórico de movimentações passa a devolver o código do talhão e o id da
  operação.
- No frontend, uma camada de tradução converte insumos e movimentações entre o
  formato das telas e o do backend, e a tela passa a usar `/api/movimentacoes`.
- O formulário de movimentação passa a usar funcionários e fornecedores reais e
  a enviar a operação escolhida em "Atividade Relacionada".
- Erros devolvidos pelo backend ao registrar a movimentação passam a aparecer
  para o usuário; o registro local de demonstração só vale quando o backend
  está fora do ar.

### C. Regras no backend
- O tipo de atividade precisa pertencer à categoria informada.
- Operação com status `Concluída` exige data de término.
- Excluir categoria, tipo ou máquina em uso devolve HTTP 400 com mensagem
  clara, em vez de erro 500.
- "Atrasada" passa a ser calculada com a data local da operação
  (`America/Sao_Paulo` por padrão), não com a data UTC do servidor. O cálculo
  equivalente no navegador recebe a mesma correção.

### Fora do escopo
- Cadastro de insumo pela tela (continua como está), lotes e alertas de
  validade.
- Telas de cadastro de categorias, tipos, máquinas e funcionários.
- Baixa automática de estoque a partir dos insumos da atividade.
- Versionamento de migrations, seed de catálogos, coleção do Insomnia e testes
  automatizados no backend.
- O script `scripts/seed-insumos.mjs` do frontend, que usa a rota e o formato
  antigos.

## Capabilities

As capacidades abaixo ainda não estão em `openspec/specs/`: foram introduzidas
pelas changes `atividades-agricolas` e `movimentacao-estoque`, concluídas e não
arquivadas. Esta change só **acrescenta** requisitos a elas; o ideal é arquivar
aquelas duas antes desta.

### New Capabilities
- `atividade-agricola`: unicidade da operação, consistência entre tipo e
  categoria, data de término para operação concluída, data de referência do
  atraso e nome da propriedade na resposta.
- `categoria-atividade`: exclusão de categoria em uso.
- `tipo-atividade`: exclusão de tipo em uso.
- `maquina`: exclusão de máquina em uso.
- `movimentacao-estoque`: vínculo da saída com a operação agrícola, data
  informada da movimentação e identificação do talhão e da operação no
  histórico.

### Modified Capabilities

Nenhuma capacidade de `openspec/specs/` tem requisito alterado.

## Impact

- **Backend**: `services/atividade_agricola_service.py`,
  `models/atividade_agricola.py`, `services/categoria_atividade_service.py`,
  `services/tipo_atividade_service.py`, `services/maquina_service.py` e os
  respectivos controllers; `models/movimentacao_estoque.py`,
  `schemas/movimentacao_schema.py`, `services/movimentacao_service.py`.
- **Banco**: uma migration que adiciona `movimentacao_estoque.id_atividade_agricola`
  (FK opcional). Não há alteração em dados existentes.
- **API**: `POST/PUT /api/atividades` passam a recusar casos antes aceitos
  (duplicada, tipo de outra categoria, concluída sem término); `DELETE` dos três
  catálogos passa a responder 400 quando em uso; `POST /api/movimentacoes`
  aceita dois campos novos e opcionais.
- **Frontend** (`frontendweb`): `src/services/api.ts`, novo módulo de tradução
  de insumos e movimentações com testes, `src/types/atividade.ts`,
  `src/types/insumo.ts`, `src/services/insumosMock.ts`,
  `src/components/atividades/AtividadeForm.tsx`,
  `src/components/insumos/MovimentacaoForm.tsx`.
- **Outras pessoas**: os arquivos de insumos do frontend são do módulo da
  Rafaela, que recebeu commits em 13/11; há risco de conflito de merge.
