import socket

def gerar_zpl(produto_nome: str, manipulado_por: str, manipulado_em, validade, armazenamento: str, porcao: str = None) -> str:
    linhas = [
        "^XA",
        "^CF0,30",
        f"^FO50,30^FD{produto_nome}^FS",
        "^CF0,20",
        f"^FO50,80^FDManipulado por: {manipulado_por}^FS",
        f"^FO50,110^FDManipulacao: {manipulado_em.strftime('%d/%m/%Y %H:%M')}^FS",
        f"^FO50,140^FDValidade: {validade.strftime('%d/%m/%Y %H:%M')}^FS",
        f"^FO50,170^FDArmazenamento: {armazenamento.upper()}^FS",
    ]

    if porcao:
        linhas.append(f"^FO50,200^FDPorcao: {porcao}^FS")

    linhas.append("^XZ")

    return "\n".join(linhas)


IMPRESSORA_IP = "192.168.0.XX"  # substitui pelo IP real quando descobrir
IMPRESSORA_PORTA = 9100  # porta padrão pra impressão crua (raw) via rede

def enviar_para_impressora(zpl: str):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(5)
            sock.connect((IMPRESSORA_IP, IMPRESSORA_PORTA))
            sock.sendall(zpl.encode("utf-8"))
        print("Comando enviado para a impressora com sucesso.")
    except (socket.timeout, ConnectionRefusedError, OSError) as e:
        print(f"Erro ao conectar na impressora: {e}")