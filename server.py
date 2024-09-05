import struct
from enlace import *

# Configurar a porta serial
serialName = "COM3"  # Altere para a porta correta
com2 = enlace(serialName)

# Configurações do datagrama
HEAD_SIZE = 12
PAYLOAD_SIZE = 50
EOP = b'\xFF\xFF\xFF'

def verify_packet(packet):
    # Verificar se o EOP está correto e extrair o cabeçalho
    if packet[-3:] != EOP:
        return False, None, None, None
    
    head = packet[:HEAD_SIZE]
    payload = packet[HEAD_SIZE:-3]
    
    # Extrair informações do cabeçalho (número do pacote, total de pacotes)
    packet_num, total_packets = struct.unpack('!II', head[:8])
    
    return True, packet_num, total_packets, payload

def main():
    try:
        # Habilitar comunicação
        com2.enable()
        print("Servidor: Aguardando handshake...")
        
        # Esperar o handshake do cliente
        handshake_data, _ = com2.getData(5)
        if handshake_data == b'HELLO':
            com2.sendData(b'ACK')
        else:
            print("Falha no handshake")
            com2.disable()
            return
        
        print("Servidor: Aguardando pacotes...")
        
        packets = []
        last_packet_num = 0
        while True:
            # Receber um pacote
            packet, _ = com2.getData(HEAD_SIZE + PAYLOAD_SIZE + 3)
            valid, packet_num, total_packets, payload = verify_packet(packet)
            
            if not valid or packet_num != last_packet_num + 1:
                com2.sendData(b'NACK')
                print(f"Erro no pacote {packet_num}")
                break
            
            # Armazenar o payload recebido
            packets.append(payload)
            last_packet_num = packet_num
            com2.sendData(b'ACK')
            print(f"Pacote {packet_num}/{total_packets} recebido")
            
            if packet_num == total_packets:
                break
        
        # Reagrupar os pacotes e salvar o arquivo
        file_data = b''.join(packets)
        with open('arquivo_recebido.txt', 'wb') as f:
            f.write(file_data)
        
        print("Arquivo recebido com sucesso.")
        com2.disable()

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        com2.disable()

if __name__ == "__main__":
    main()
