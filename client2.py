import time
from enlace import *

# Configurar a porta serial
serialName = "/dev/tty.usbmodem101"  # Altere para a porta correta
com1 = enlace(serialName)

# Configurações do EOP
EOP = b'\xAA\xBB\xCC'  # 3 bytes

def create_datagram(packet_number, total_packets, payload):
    """Cria um datagrama com cabeçalho, payload e EOP"""
    head = packet_number.to_bytes(2, 'big') + total_packets.to_bytes(2, 'big') + len(payload).to_bytes(2, 'big') + b'\x00'*6
    return head + payload + EOP

def handshake():
    """Realiza o handshake com o servidor"""
    datagram = create_datagram(0, 0, b'')  # Handshake payload vazio
    com1.sendData(datagram)
    response, _ = com1.getData(15)  # Tamanho total do datagrama esperado (HEAD + EOP)
    if response:
        print("Cliente: Handshake bem-sucedido")
        return True
    else:
        return False

def send_file(file_path):
    """Envia um arquivo fragmentado em pacotes"""
    with open(file_path, 'rb') as file:
        content = file.read()
        
    total_packets = (len(content) + 49) // 50  # Calcula o número total de pacotes
    for i in range(total_packets):
        start = i * 50
        end = min((i + 1) * 50, len(content))
        payload = content[start:end]
        
        datagram = create_datagram(i + 1, total_packets, payload)
        com1.sendData(datagram)
        print(f'Cliente: Pacote {i + 1} enviado')
        
        # Aguardar ACK ou NACK
        response, _ = com1.getData(15)  # 15 bytes para o datagrama do ACK
        if response:
            print(f'Cliente: ACK recebido para pacote {i + 1}')
        else:
            print(f'Cliente: Erro no pacote {i + 1}, reenviando...')
            com1.sendData(datagram)

def main():
    try:
        com1.enable()

        if handshake():
            file_path = 'meu_arquivo.txt'  # Altere para o caminho correto do arquivo
            send_file(file_path)
        else:
            print("Servidor inativo. Tentar novamente? S/N")
            # Implementar lógica para tentar novamente se necessário

        com1.disable()

    except Exception as e:
        print("Cliente: Ocorreu um erro:", e)
        com1.disable()

if __name__ == "__main__":
    main()
