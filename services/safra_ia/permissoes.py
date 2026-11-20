PERFIS_FINANCEIROS = {'administrador', 'financeiro', 'proprietario'}

PERSONA_POR_PERFIL = {
    'administrador': 'administrador',
    'proprietario': 'produtor',
    'financeiro': 'administrador',
    'agronomo': 'agronomo',
    'supervisor-campo': 'gerente',
    'estoquista': 'gerente',
}


def pode_ver_financeiro(perfil):
    return (perfil or '').lower() in PERFIS_FINANCEIROS


def persona_do_perfil(perfil):
    return PERSONA_POR_PERFIL.get((perfil or '').lower(), 'gerente')
