# Tasks

## 1. Modelos e banco

- [x] 1.1 Criar `models/funcionario.py` com `Funcionario` (`id_funcionario`
      String(36) PK com default `str(uuid.uuid4())`, `nome_completo`
      String(150) not null, `cpf` String(11) unique not null, `rg` String(20),
      `data_nascimento` Date, `telefone` String(20), `email` String(100),
      `cargo` String(100) not null, `data_admissao` Date not null,
      `data_desligamento` Date, `status` Boolean default True, `observacoes`
      String(500), `data_cadastro` DateTime server_default now). Verificar que
      o modelo importa sem erro (`python -c "import models.funcionario"`).
- [x] 1.2 Criar `models/funcionario_propriedade.py` com
      `FuncionarioPropriedade` (`id_funcionario_propriedade` String(36) PK
      default `str(uuid.uuid4())`, `id_funcionario` FK not null para
      `funcionario`, `id_propriedade` FK not null para `propriedade`,
      `data_vinculacao` DateTime server_default now). Verificar import sem erro.
- [x] 1.3 Registrar os dois modelos em `models/__init__.py` e verificar que o
      app sobe sem erro de mapeamento (`flask shell` ou import de `app`).
- [x] 1.4 Gerar a migration Alembic (tabela `funcionario` antes de
      `funcionario_propriedade`), revisar o script e aplicar com
      `flask db upgrade`; verificar que as duas tabelas existem no banco.

## 2. Schemas Pydantic

- [x] 2.1 Criar `schemas/funcionario_schema.py` com `FuncionarioCreate`:
      `nome_completo: str` (obrigatório, trim), `cpf: str` normalizado para 11
      dígitos (validador que remove não-dígitos e exige len==11),
      `cargo: str` (obrigatório), `data_admissao: date` (obrigatório), demais
      campos opcionais. Verificar com teste unitário que CPF `123.456.789-00`
      vira `12345678900` e que CPF com menos de 11 dígitos levanta erro.
- [x] 2.2 Criar `FuncionarioUpdate` (campos opcionais) e
      `VinculoPropriedadeCreate` (`id_propriedade: int`). Verificar validação
      de payload inválido levanta `ValidationError`.

## 3. Serviços

- [x] 3.1 Criar `services/funcionario_service.py` com `criar_funcionario`
      (valida CPF único consultando antes e retornando `ValueError` amigável) e
      `buscar_por_id` (404 → `ValueError`). Verificar criação e erro de CPF
      duplicado.
- [x] 3.2 Implementar `listar` com filtros opcionais `nome`, `cpf`, `cargo`,
      `id_propriedade` (join `distinct` com `funcionario_propriedade`) e
      `status`. Verificar cada filtro retornando o subconjunto correto.
- [x] 3.3 Implementar `atualizar_funcionario` (preserva unicidade de CPF,
      grava `data_desligamento`) e `inativar_funcionario` (soft delete via
      `status=False`). Verificar atualização e inativação sem remover o registro.
- [x] 3.4 Implementar `vincular_propriedade` (valida existência de funcionário
      e propriedade, grava `data_vinculacao`) e `listar_propriedades` do
      funcionário. Verificar vínculo criado e listagem.
- [x] 3.5 Implementar `indicadores` retornando total, ativos, inativos e
      contagem por propriedade. Verificar os números contra dados de teste.

## 4. API

- [x] 4.1 Criar `controllers/funcionario_controller.py` com
      `GET/POST /funcionarios` (POST valida com `FuncionarioCreate`,
      ValidationError/ValueError → 400, sucesso → 201) e `GET` com os filtros
      via query params. Verificar respostas 201/400/200.
- [x] 4.2 Implementar `GET/PUT/DELETE /funcionarios/<id>` (404 quando
      inexistente, 200 em sucesso, DELETE faz soft delete). Verificar os
      códigos de status.
- [x] 4.3 Implementar `POST /funcionarios/<id>/propriedades` (201; 400 para
      funcionário/propriedade inexistente) e
      `GET /funcionarios/<id>/propriedades` (200). Verificar os fluxos.
- [x] 4.4 Implementar `GET /funcionarios/indicadores` (200 com os cards).
      Verificar o payload dos indicadores.
- [x] 4.5 Registrar `funcionario_bp` em `app.py` com `url_prefix='/api'`.
      Verificar que as rotas respondem sob `/api/funcionarios`.

## 5. Validação de integração

- [x] 5.1 Testar o fluxo completo via Insomnia/HTTP: cadastro → consulta com
      filtros → atualização → vínculo de propriedade → inativação →
      indicadores, conferindo os códigos de status e os efeitos no banco.
- [x] 5.2 Adicionar as requisições de Funcionário e vínculo ao
      `insomnia_safraviva.json` e remover dados de teste do banco.
