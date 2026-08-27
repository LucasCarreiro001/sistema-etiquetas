from datetime import datetime
from impressora import gerar_zpl

zpl = gerar_zpl(
    produto_nome="Molho de tomate",
    manipulado_por="Lucas",
    manipulado_em=datetime.now(),
    validade=datetime(2026, 8, 20),
    armazenamento="refrigerado",
    porcao="1kg"
)

print(zpl)