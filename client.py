import struct
import time
from enlace import *

# Configurar a porta serial
serialName = "/dev/tty.usbmodem1101"  # Altere para a porta correta
com1 = enlace(serialName)

# Configurações do datagrama
HEAD_SIZE = 12
PAYLOAD_SIZE = 50
EOP = b'\xFF\xFF\xFF'

def create_packet(packet_num, total_packets, payload):
    # Criar o cabeçalho com o número do pacote e o total de pacotes
    head = struct.pack('!II', packet_num, total_packets) + b'\x00' * (HEAD_SIZE - 8)
    return head + payload + EOP

def handshake():
    # Iniciar o handshake para verificar se o servidor está ativo
    com1.sendData(b'HELLO')
    response, _ = com1.getData(4)
    return response == b'ACK'

def send_file(file_path):
    try:
        # Habilitar comunicação
        com1.enable()
        
        # Realizar o handshake
        if not handshake():
            print("Servidor inativo. Tentar novamente? S/N")
            return
        
        # Abrir o arquivo e preparar para envio
        with open(file_path, 'rb') as f:
            file_data = f.read()
            total_packets = len(file_data) // PAYLOAD_SIZE + (1 if len(file_data) % PAYLOAD_SIZE != 0 else 0)
        
        for i in range(total_packets):
            # Fragmentar o arquivo em pacotes
            start = i * PAYLOAD_SIZE
            end = start + PAYLOAD_SIZE
            payload = file_data[start:end]
            
            # Criar o datagrama
            packet = create_packet(i + 1, total_packets, payload)
            com1.sendData(packet)
            print(f"Pacote {i + 1}/{total_packets} enviado")
            
            # Aguardar a confirmação do servidor
            response, _ = com1.getData(3)  # Receber ACK/NACK
            if response != b'ACK':
                print(f"Erro no pacote {i + 1}. Reenviando...")
                return

        print("Envio concluído.")
        com1.disable()

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        com1.disable()

if __name__ == "__main__":
    send_file('arquivo_a_ser_enviado.txt')
