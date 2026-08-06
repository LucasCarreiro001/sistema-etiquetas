from datetime import datetime, timedelta

def calcular_validade(produto, manipulado_em: datetime) -> datetime:
    if produto.validade_unidade == 'horas':
        delta = timedelta(hours=produto.validade_valor)
    elif produto.validade_unidade == 'dias':
        delta = timedelta(days=produto.validade_valor)
    else:
        raise ValueError(f"Unidade de validade desconhecida: {produto.validade_unidade}")

    validade = manipulado_em + delta

    if produto.validade_referencia == 'fim_do_dia':
        validade= validade.replace(hour=23, minute=59, second=59)

    return validade