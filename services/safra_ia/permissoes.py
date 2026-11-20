MODULOS_POR_PAPEL = {
    # Keep these defaults synchronized with PERFIS_PADRAO in frontendweb.
    'administrador': {'Propriedades', 'Talhões', 'Funcionários', 'Atividades', 'Financeiro', 'Insumos'},
    'proprietario': {'Propriedades', 'Talhões', 'Funcionários', 'Atividades', 'Financeiro', 'Insumos'},
    'gerente-agricola': {'Propriedades', 'Talhões', 'Funcionários', 'Atividades', 'Financeiro', 'Insumos'},
    'agronomo': {'Propriedades', 'Talhões', 'Atividades', 'Insumos'},
    'supervisor-campo': {'Talhões', 'Atividades', 'Insumos'},
    'financeiro': {'Financeiro'},
    'estoquista': {'Atividades', 'Insumos'},
    'operador': {'Atividades'},
}

PAPEIS = {
    'administrador': {
        'nome': 'Administrador',
        'foco': 'Visão completa e gestão da fazenda',
        'tom': 'estratégico e objetivo',
        'saudacao': 'Olá! Sou o SafraIA. Posso ajudar você a acompanhar toda a fazenda, das propriedades aos resultados financeiros. O que deseja saber?',
        'sugestoes': [
            'Quantas propriedades e hectares temos?',
            'Qual o resultado financeiro por safra?',
            'Como está o estoque de insumos?',
            'Quais atividades estão atrasadas?',
        ],
    },
    'proprietario': {
        'nome': 'Proprietário',
        'foco': 'Visão gerencial e resultados da fazenda',
        'tom': 'estratégico e claro',
        'saudacao': 'Olá! Sou o SafraIA. Posso trazer um panorama das propriedades, operações e resultados da sua fazenda. Como posso ajudar?',
        'sugestoes': [
            'Quantas propriedades e hectares temos?',
            'Qual o custo por hectare das safras?',
            'Como está o fluxo financeiro?',
            'Quais insumos precisam de reposição?',
        ],
    },
    'gerente-agricola': {
        'nome': 'Gerente Agrícola',
        'foco': 'Gestão operacional, equipes e custos',
        'tom': 'prático e orientado à ação',
        'saudacao': 'Olá! Sou o SafraIA. Posso ajudar a acompanhar propriedades, equipes, atividades, insumos e custos da operação. O que precisa analisar?',
        'sugestoes': [
            'Quais atividades estão atrasadas?',
            'Qual máquina foi mais usada?',
            'Quais insumos foram aplicados nesta safra?',
            'Qual foi o custo por hectare?',
        ],
    },
    'agronomo': {
        'nome': 'Agrônomo',
        'foco': 'Talhões, safras, atividades e manejo de insumos',
        'tom': 'técnico e objetivo',
        'saudacao': 'Olá! Sou o SafraIA. Posso ajudar com áreas, safras, atividades e consumo de insumos. O que deseja analisar?',
        'sugestoes': [
            'Quais áreas estão disponíveis para plantio?',
            'Quanto de insumo foi aplicado nesta safra?',
            'Quais atividades estão atrasadas?',
            'Quais insumos estão abaixo do mínimo?',
        ],
    },
    'supervisor-campo': {
        'nome': 'Supervisor de Campo',
        'foco': 'Atividades, máquinas e insumos no campo',
        'tom': 'prático e direto',
        'saudacao': 'Olá! Sou o SafraIA. Posso ajudar a acompanhar as atividades, máquinas e insumos usados no campo. O que precisa verificar?',
        'sugestoes': [
            'Quais atividades estão atrasadas?',
            'Qual máquina foi mais usada?',
            'Quais insumos foram aplicados por talhão?',
            'Quais insumos precisam de reposição?',
        ],
    },
    'financeiro': {
        'nome': 'Financeiro',
        'foco': 'Receitas, despesas e resultados financeiros',
        'tom': 'preciso e analítico',
        'saudacao': 'Olá! Sou o SafraIA. Posso analisar o fluxo de caixa, despesas, custos por centro de custo e resultados por safra. O que deseja consultar?',
        'sugestoes': [
            'Como foi o fluxo financeiro nos últimos 12 meses?',
            'Qual safra teve maior lucro?',
            'Onde estão concentradas as despesas?',
            'Qual o custo por hectare de cada safra?',
        ],
    },
    'estoquista': {
        'nome': 'Estoquista',
        'foco': 'Estoque, movimentações e fornecedores',
        'tom': 'operacional e direto',
        'saudacao': 'Olá! Sou o SafraIA. Posso ajudar com o estoque, as movimentações de insumos e os fornecedores. O que precisa conferir?',
        'sugestoes': [
            'Quais insumos estão abaixo do mínimo?',
            'O que saiu do estoque este mês?',
            'Quais lotes vencem em breve?',
            'Quais fornecedores mais entregaram?',
        ],
    },
    'operador': {
        'nome': 'Operador',
        'foco': 'Atividades agrícolas da operação',
        'tom': 'simples e direto',
        'saudacao': 'Olá! Sou o SafraIA. Posso ajudar a consultar as atividades agrícolas. O que deseja saber?',
        'sugestoes': [
            'Quais atividades estão atrasadas?',
            'Quantas atividades estão em andamento?',
            'Quais atividades foram concluídas?',
            'Como estão as atividades da fazenda?',
        ],
    },
    'colaborador': {
        'nome': 'Colaborador',
        'foco': 'Orientações gerais de gestão rural',
        'tom': 'neutro e objetivo',
        'saudacao': 'Olá! Sou o SafraIA. Posso ajudar com orientações gerais de gestão rural. Como posso ajudar?',
        'sugestoes': [
            'Como planejar uma rotação de culturas?',
            'Quais cuidados ajudam a conservar o solo?',
            'Como organizar as atividades da fazenda?',
            'Como armazenar insumos agrícolas com segurança?',
        ],
    },
}


def papel_do_perfil(perfil):
    papel = (perfil or '').strip().lower()
    return papel if papel in MODULOS_POR_PAPEL else 'colaborador'


def modulos_do_papel(perfil):
    return MODULOS_POR_PAPEL.get(papel_do_perfil(perfil), set())


def ve_financeiro(perfil):
    return 'Financeiro' in modulos_do_papel(perfil)
