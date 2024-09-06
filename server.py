import struct
from enlace import *

# Configurar a porta serial
serialName = "COM3"  # Altere para a porta correta
com2 = enlace(serialName)

# Configurações do datagrama
HEAD_SIZE = 12
EOP = b'\xFF\xFF\xFF'

def verify_packet(packet):
    # Verificar se o EOP está correto e extrair o cabeçalho
    if packet[-3:] != EOP:
        return False, None, None, None
    
    head = packet[:HEAD_SIZE]
    payload = packet[HEAD_SIZE:-3]
    
    # Extrair informações do cabeçalho (número do pacote, total de pacotes e tamanho do payload)
    packet_num, total_packets, expected_payload_size = struct.unpack('!III', head)
    
    # Verificar o tamanho do payload recebido
    if len(payload) != expected_payload_size:
        print(f"Erro: Tamanho do payload incorreto no pacote {packet_num}. Esperado: {expected_payload_size}, Recebido: {len(payload)}")
        return False, packet_num, total_packets, None

    return True, packet_num, total_packets, payload

def main():
    try:
        # Habilitar comunicação
        com2.enable()

        # Receber byte de sacrifício e limpar buffer
        print("Servidor: esperando 1 byte de sacrifício")
        rxBuffer, nRx = com2.getData(1)
        com2.rx.clearBuffer()
        time.sleep(0.1)
        
        print("Servidor: Aguardando handshake...")
        
        # Esperar o handshake do cliente
        handshake_data, _ = com2.getData(5)
        print(f"Servidor: Dados recebidos no handshake: {handshake_data}")
        
        if handshake_data == b'HELLO':
            print("Servidor: Respondendo ao handshake com ACK")
            com2.sendData(b'ACK')  # Enviar confirmação ao cliente
        else:
            print("Servidor: Falha no handshake")
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
                if not valid:
                    print("Erro no pacote - não valido")
                    com2.sendData(b'NACK')
                    # break
                if packet_num != last_packet_num + 1:
                    print(f"Número do pacote incorreto - esperado {last_packet_num + 1}, recebido {packet_num}")
                    com2.sendData(b'NACK')
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