from datetime import datetime
from calculo_validade import calcular_validade


class ProdutoFake:
    def __init__(self, validade_valor, validade_unidade, validade_referencia):
        self.validade_valor = validade_valor
        self.validade_unidade = validade_unidade
        self.validade_referencia = validade_referencia


# Caso 1: regra padrão, em dias
produto1 = ProdutoFake(3, "dias", "padrao")
manipulado_em = datetime(2026, 7, 24, 15, 0)
print("Caso 1 (padrao, dias):", calcular_validade(produto1, manipulado_em))
# Esperado: 2026-07-27 15:00:00

# Caso 2: regra fim do dia
produto2 = ProdutoFake(1, "dias", "fim_do_dia")
print("Caso 2 (fim do dia):", calcular_validade(produto2, manipulado_em))
# Esperado: 2026-07-25 23:59:59

# Caso 3: em horas
produto3 = ProdutoFake(8, "horas", "padrao")
print("Caso 3 (horas):", calcular_validade(produto3, manipulado_em))
# Esperado: 2026-07-24 23:00:00