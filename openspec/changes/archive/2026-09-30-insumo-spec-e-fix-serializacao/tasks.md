# Tasks

## 1. Correção da serialização

- [x] 1.1 Em `services/insumo_service.py`, importar `Fabricante` e `Marca`.
- [x] 1.2 Em `listar_todos`, resolver o nome do fabricante via
      `produto.id_fabricante` → `Fabricante.nome_fabricante`.
- [x] 1.3 Resolver a descrição da marca via `produto.id_marca` →
      `Marca.descricao_marca`.
- [x] 1.4 Substituir as chaves `fabricante` e `marca` por `id_fabricante`,
      `fabricante_nome`, `id_marca` e `descricao_marca`.
- [x] 1.5 Garantir que insumos cujo produto não tenha fabricante/marca retornem
      ids nulos e nomes vazios, sem lançar exceção.

## 2. Validação

- [x] 2.1 Cadastrar um insumo e confirmar que `GET /api/insumos` retorna 200
      com os campos de fabricante e marca preenchidos.
- [x] 2.2 Confirmar que `GET /api/insumos/{id}` retorna 200 no mesmo formato.
- [x] 2.3 Testar com produto sem fabricante e sem marca (deve retornar 200).
- [x] 2.4 Remover os dados de teste utilizados.

## 3. Documentação da capability

- [x] 3.1 Revisar o delta em `specs/insumo/spec.md` conferindo cada requisito
      contra o comportamento real do código.
- [ ] 3.2 Arquivar a change para consolidar `openspec/specs/insumo/`.
