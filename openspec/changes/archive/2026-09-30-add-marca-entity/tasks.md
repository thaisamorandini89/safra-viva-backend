# Tasks

## 1. Modelo e banco

- [x] 1.1 Criar `models/marca.py` com a classe `Marca` (`__tablename__ = 'marca'`,
      `id_marca` Integer PK, `descricao_marca` String(500) not null unique, `__repr__`).
- [x] 1.2 Gerar a migration Alembic (`flask db migrate -m "criando tabela marca"`)
      a partir da head atual e revisar o arquivo gerado em `migrations/versions/`.
- [x] 1.3 Aplicar a migration (`flask db upgrade`) e confirmar a tabela no banco.

## 2. Serviço

- [x] 2.1 Criar `services/marca_service.py` com `MarcaService.listar_todos()`
      ordenando por `descricao_marca`.
- [x] 2.2 Implementar `MarcaService.criar_marca(dados)` validando obrigatoriedade,
      aplicando `strip()` e bloqueando descrição duplicada com `ValueError`.
- [x] 2.3 Implementar `MarcaService.atualizar_marca(id_marca, dados)` buscando a
      marca (erro quando inexistente), validando a nova descrição e impedindo
      duplicidade com outra marca.
- [x] 2.4 Implementar `MarcaService.excluir_marca(id_marca)` removendo o registro
      e sinalizando erro quando a marca não existir.
- [x] 2.5 Tratar falha de commit com `rollback` e `RuntimeError` em todas as operações.

## 3. API

- [x] 3.1 Criar `controllers/marca_controller.py` com `marca_bp` e
      `GET /marcas` retornando `id_marca` e `descricao_marca`.
- [x] 3.2 Implementar `POST /marcas` retornando 201 em sucesso, 400 para
      payload inválido/duplicado e 500 para erro inesperado.
- [x] 3.3 Implementar `PUT /marcas/<int:id_marca>` retornando 200 com a marca
      atualizada, 400 para payload inválido/duplicado, 404 quando não existir
      e 500 para erro inesperado.
- [x] 3.4 Implementar `DELETE /marcas/<int:id_marca>` retornando 200 com mensagem
      de sucesso, 404 quando não existir e 500 para erro inesperado.
- [x] 3.5 Registrar `marca_bp` em `app.py` com `url_prefix='/api'`.

## 4. Validação

- [x] 4.1 Testar manualmente `GET`/`POST`/`PUT`/`DELETE` em `/api/marcas`
      (incluindo duplicidade e id inexistente).
- [x] 4.2 Adicionar as requisições de Marca ao `insomnia_safraviva.json`.
