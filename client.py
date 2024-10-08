import struct
import time
from enlace import *

# Configurar a porta serial
serialName = "/dev/tty.usbmodem101"  # Altere para a porta correta
com1 = enlace(serialName)

# Configurações do datagrama

PAYLOAD_SIZE = 50
EOP = b'\xFF\xFF\xFF'

def create_packet(packet_num, total_packets, payload):
    # Criar o cabeçalho com o número do pacote, o total de pacotes e o tamanho do payload
    payload_size = len(payload)  # Tamanho real do payload
    head = struct.pack('!III', packet_num, total_packets, payload_size)  # Adicionando o tamanho do payload no head
    return head + payload + EOP

def handshake():
    # Enviar byte de sacrifício para eliminar "lixo"
    time.sleep(0.2)
    com1.sendData(b'00')  # Byte de sacrifício
    time.sleep(1)

    # Iniciar o handshake para verificar se o servidor está ativo
    print("Cliente: Iniciando handshake")
    com1.sendData(b'HELLO')  # Envia mensagem de handshake
    
    # Esperar resposta do servidor
    response, _ = com1.getData(4)
    
    if response == b'ACK':  # Espera confirmação de ACK do servidor
        print("Cliente: Handshake bem-sucedido!")
        return True
    else:
        print(f"Cliente: Falha no handshake. Resposta recebida: {response}")
        return False

def send_file(file_path):
    try:
        # Habilitar comunicação
        com1.enable()
        
        # Loop para tentar o handshake até o sucesso ou decisão do usuário de parar
        while True:
            # Realizar o handshake
            if handshake():
                break  # Handshake bem-sucedido, podemos sair do loop
            else:
                print("Servidor inativo. Tentar novamente? S/N")
                if input().lower() != 's':
                    com1.disable()  # Desabilitar comunicação antes de sair
                    return
                else:
                    print("Tentando novamente o handshake...")
                    time.sleep(1)  # Espera antes de tentar novamente

        # Se chegarmos aqui, o handshake foi bem-sucedido
        print("Handshake bem-sucedido. Iniciando envio de arquivo.")
            
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

def send_file_with_incorrect_payload(file_path):
    try:
        # Habilitar comunicação
        com1.enable()
        
        # Loop para tentar o handshake até o sucesso ou decisão do usuário de parar
        while True:
            if handshake():
                break
            else:
                print("Servidor inativo. Tentar novamente? S/N")
                if input().lower() != 's':
                    com1.disable()
                    return
                else:
                    print("Tentando novamente o handshake...")
                    time.sleep(1)

        # Se chegarmos aqui, o handshake foi bem-sucedido
        print("Handshake bem-sucedido. Iniciando envio de arquivo.")

        # Abrir o arquivo e preparar para envio
        with open(file_path, 'rb') as f:
            file_data = f.read()
            total_packets = len(file_data) // PAYLOAD_SIZE + (1 if len(file_data) % PAYLOAD_SIZE != 0 else 0)

        for i in range(total_packets):
            start = i * PAYLOAD_SIZE
            end = start + PAYLOAD_SIZE
            payload = file_data[start:end]

            if i == 0:  # Simular erro no primeiro pacote
                print(f"Simulando erro no pacote {i+1}")
                payload = payload[:4]  # Diminuir o tamanho do payload intencionalmente para simular erro

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
    # Enviar arquivo normal
    # send_file('arquivo.txt')

    # Enviar arquivo com simulação de erro no payload
    send_file_with_incorrect_payload('arquivo.txt')
