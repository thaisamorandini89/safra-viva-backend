# Financeiro real de ponta a ponta

## Why

O backend e as telas do Financeiro já existem, mas não funcionam juntos. Sem
safras nem centros de custo no banco, o formulário mostra dados de demonstração;
ao salvar com eles o backend recusa, a tela engole o erro e "salva" só na
memória, e o lançamento some ao recarregar. Não há tela para cadastrar safra ou
centro de custo, nada marca um lançamento como conciliado, e a change
`financeiro` que criou o backend nunca foi verificada (0 de 26 tasks marcadas).

## What Changes

### Verificação do que já existe
- Os 35 cenários das specs da change `financeiro` são conferidos pela API; os
  desvios encontrados no código são corrigidos e as tasks dela são marcadas.
- As requisições do Financeiro entram no `insomnia_safraviva.json`, que hoje não
  tem nenhuma.

### Backend
- Safra passa a ter edição e exclusão. A exclusão é recusada quando a safra tem
  lançamentos; a alternativa é inativar.
- Safra passa a recusar término anterior ao início e nome repetido dentro da
  mesma propriedade.
- Centro de custo passa a ter edição e exclusão, com a mesma regra de uso.
- Passa a existir a conciliação de lançamento: só lançamento pago pode ser
  conciliado, o conciliado não pode ser editado nem excluído, e a conciliação
  pode ser desfeita.

### Frontend
- Quando o backend responde, as telas mostram só o que está cadastrado, mesmo
  vazio. Os dados de demonstração ficam apenas para quando o backend não
  responde.
- Recusas do backend ao salvar lançamento, safra ou centro de custo aparecem na
  tela, em vez de virar um salvamento em memória.
- O módulo Financeiro ganha as abas "Safras" e "Centros de Custo", com lista,
  cadastro, edição, inativação e exclusão.
- O formulário de lançamento lista só safras e centros ativos e orienta o
  cadastro quando não há nenhum.
- A lista de lançamentos ganha as ações de conciliar e de desfazer a
  conciliação, e trava a edição e a exclusão do conciliado.

### Fora do escopo
- Ligar a safra cadastrada a atividades e movimentações (change
  `safra-unificada`).
- Gerar despesa a partir da entrada de estoque e levar o custo das atividades
  aos indicadores.
- Mudar as regras de cálculo de saldo, fluxo de caixa e indicadores.
- Tirar os dados de demonstração de outros módulos (talhões, insumos,
  atividades).

## Capabilities

`safra`, `centro-custo` e `lancamento-financeiro` ainda não estão em
`openspec/specs/`: vêm da change `financeiro`, concluída no código e não
arquivada. Esta change só acrescenta requisitos a elas.

### New Capabilities
- `safra`: edição, exclusão protegida, período válido e nome único por
  propriedade.
- `centro-custo`: edição e exclusão protegida.
- `lancamento-financeiro`: conciliação e proteção do lançamento conciliado
  contra alteração.

### Modified Capabilities

Nenhuma capacidade de `openspec/specs/` tem requisito alterado.

## Impact

- **Depende de**: nada para implementar. Para arquivar, a change `financeiro`
  precisa ser arquivada antes (`/opsx-archive financeiro`), para as specs
  principais nascerem na ordem certa.
- **Backend**: `services/safra_service.py`, `services/centro_custo_service.py`,
  `services/lancamento_service.py`, os schemas e controllers correspondentes e
  `insomnia_safraviva.json`. Correções pontuais nos arquivos do Financeiro se a
  verificação apontar desvios.
- **Banco**: sem migration.
- **API**: novos `PUT` e `DELETE` em `/api/safras/{id}` e
  `/api/centros-custo/{id}`, novo `PUT /api/lancamentos/{id}/conciliacao`;
  `POST /api/safras` passa a recusar período inválido e nome repetido;
  `PUT /api/lancamentos/{id}` passa a recusar lançamento conciliado.
- **Frontend** (`frontendweb`): `src/services/api.ts`, `src/types/financeiro.ts`,
  `src/components/financeiro/` (módulo, formulário e lista de lançamentos, e as
  duas telas novas) e testes.
- **Outros módulos**: Início, Notificações, Mapa, Relatórios e SafraIA leem as
  safras pela mesma consulta e passam a ver as cadastradas, em vez das de
  demonstração.
- **Change `financeiro`**: o `tasks.md` dela é atualizado com o resultado da
  verificação.
