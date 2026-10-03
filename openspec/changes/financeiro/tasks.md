# Tasks

## 1. Modelos e banco

- [ ] 1.1 Criar `models/safra.py` com `Safra` (`id_safra` PK inteira, `nome`
      String not null, `cultura` String not null, `id_propriedade` FK not null,
      `data_inicio` Date not null, `data_fim` Date opcional, `area_plantada`
      Numeric(12,2) opcional, `status` Boolean default True, `data_cadastro`
      server_default now) e verificar que a classe importa sem erro.
- [ ] 1.2 Criar `models/centro_custo.py` com `CentroCusto` (`id_centro_custo` PK
      inteira, `nome` String not null, `tipo` String(20) not null, `descricao`
      String opcional, `status` Boolean default True, `data_cadastro`
      server_default now).
- [ ] 1.3 Criar `models/lancamento_financeiro.py` com `LancamentoFinanceiro`
      (`id_lancamento` String(36) PK com default `str(uuid.uuid4())`, `tipo`
      String(10) not null, `categoria` String not null, `descricao` opcional,
      `valor` Numeric(14,2) not null, `data_lancamento` Date not null,
      `forma_pagamento` String(20) opcional, `status` String(10) default
      'PENDENTE', `conciliado` Boolean default False, `observacao` opcional,
      `data_cadastro` server_default now, FKs opcionais `id_empresa`,
      `id_propriedade`, `id_talhao`, `id_safra`, `id_centro_custo`).
- [ ] 1.4 Criar `models/rateio_lancamento.py` com `RateioLancamento`
      (`id_rateio` PK inteira, `id_lancamento` FK not null, `id_talhao` FK not
      null, `percentual` Numeric(5,2) not null).
- [ ] 1.5 Registrar os quatro modelos em `models/__init__.py` na ordem de
      dependência e verificar que `flask db migrate` enxerga as classes.
- [ ] 1.6 Gerar a migration Alembic criando `safra` e `centro_custo` antes de
      `lancamento_financeiro`, e `rateio_lancamento` por último; revisar e
      aplicar com `flask db upgrade`, verificando que as tabelas existem.

## 2. Schemas Pydantic

- [ ] 2.1 Criar `schemas/safra_schema.py` com `SafraCreate` (`nome`, `cultura`,
      `id_propriedade`, `data_inicio` obrigatórios; `data_fim`, `area_plantada`
      opcionais) e `SafraOut`; verificar rejeição de payload sem campo
      obrigatório.
- [ ] 2.2 Criar `schemas/centro_custo_schema.py` com `CentroCustoCreate`
      (`nome` obrigatório, `tipo: Literal['OPERACIONAL','ADMINISTRATIVO']`) e
      `CentroCustoOut`; verificar rejeição de `tipo` inválido.
- [ ] 2.3 Criar `schemas/lancamento_schema.py` com `RateioItem`
      (`id_talhao: int`, `percentual: Decimal gt=0`), `LancamentoCreate`
      (`tipo: Literal['RECEITA','DESPESA']`, `categoria`, `data_lancamento`,
      `valor: Decimal gt=0` obrigatórios; `forma_pagamento`/`status` Literal;
      FKs e `rateio: list[RateioItem]` opcionais) e `LancamentoOut`; verificar
      rejeição de `valor<=0` e `tipo` inválido.

## 3. Serviços

- [ ] 3.1 Criar `services/safra_service.py` com `criar` (validar existência da
      propriedade) e `listar(id_propriedade=None)`; verificar erro quando a
      propriedade não existe.
- [ ] 3.2 Criar `services/centro_custo_service.py` com `criar` e `listar`;
      verificar criação e listagem.
- [ ] 3.3 Criar `services/lancamento_service.py` com `criar(dados)` validando a
      existência de cada vínculo informado (empresa/propriedade/talhão/safra/
      centro de custo) e persistindo lançamento + rateio na mesma transação com
      rollback em falha; verificar criação com e sem vínculos.
- [ ] 3.4 Implementar no `lancamento_service` a validação de rateio: talhões
      existentes e soma de percentuais igual a 100%, senão `ValueError`;
      verificar rejeição quando a soma difere de 100%.
- [ ] 3.5 Implementar `atualizar(id, dados)` (mesmas validações; 404 se
      inexistente) e `excluir(id)` bloqueando exclusão quando `conciliado` é
      verdadeiro (RN003); verificar os dois caminhos.
- [ ] 3.6 Implementar `listar(filtros)` com filtros por período, tipo, safra,
      propriedade e talhão, ordenado por `data_lancamento` desc; verificar cada
      filtro.

## 4. Serviço de relatórios

- [ ] 4.1 Criar `services/financeiro_service.py` com `saldo(filtros)` retornando
      `receita_total`, `despesa_total` e `saldo`; verificar o cálculo com dados
      de receita e despesa.
- [ ] 4.2 Implementar `fluxo_caixa(data_inicio, data_fim)` com itens (data,
      descrição, entrada, saída, saldo acumulado) em ordem crescente de data;
      verificar que o saldo acumulado está correto.
- [ ] 4.3 Implementar `indicadores(agrupar_por)` para {safra, talhao, cultura}
      com receita/despesa totais, lucro líquido, margem líquida e ROI, e
      custo/receita/lucro por hectare (nulos quando a área for nula/zero);
      verificar agregação por safra e por cultura e o tratamento de área
      ausente.

## 5. API (controllers e blueprints)

- [ ] 5.1 Criar `controllers/safra_controller.py` com `POST`/`GET /safras`
      (201/400/500; filtro `id_propriedade`); verificar via requisição.
- [ ] 5.2 Criar `controllers/centro_custo_controller.py` com
      `POST`/`GET /centros-custo`; verificar via requisição.
- [ ] 5.3 Criar `controllers/lancamento_controller.py` com `POST`, `GET`,
      `PUT /lancamentos/<id>` e `DELETE /lancamentos/<id>`, validando o payload
      com os schemas (ValidationError → 400) e mapeando erros do service
      (vínculo/rateio inválido → 400, inexistente → 404, conciliado → 400);
      verificar cada rota.
- [ ] 5.4 Criar `controllers/financeiro_controller.py` com
      `GET /financeiro/saldo`, `GET /financeiro/fluxo-caixa` e
      `GET /financeiro/indicadores` (agrupar_por inválido → 400); verificar cada
      rota.
- [ ] 5.5 Registrar os quatro blueprints em `app.py` com `url_prefix='/api'` e
      verificar que a aplicação sobe sem erro de import.

## 6. Validação de integração

- [ ] 6.1 Exercitar o fluxo completo (criar safra → centro de custo → lançamento
      de receita e de despesa com rateio) e conferir saldo, fluxo de caixa e
      indicadores por safra/cultura via HTTP.
- [ ] 6.2 Validar as regras: valor <= 0 (400), campo obrigatório ausente (400),
      vínculo inexistente (400), rateio ≠ 100% (400) e exclusão de lançamento
      conciliado (400).
- [ ] 6.3 Adicionar as requisições de Safra, Centro de Custo, Lançamento e
      Financeiro ao `insomnia_safraviva.json` e remover dados de teste.
