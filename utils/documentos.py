def cnpj_digitos(valor):
    """CNPJ só com os dígitos, ou None quando vazio; recusa o que não tem 14 dígitos."""
    digitos = "".join(filter(str.isdigit, str(valor or "")))
    if not digitos:
        return None
    if len(digitos) != 14:
        raise ValueError("O CNPJ deve ter 14 dígitos.")
    return digitos
