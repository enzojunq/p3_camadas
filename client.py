import struct
import time
from enlace import *

# Configurar a porta serial
serialName = "/dev/tty.usbmodem1101"  # Altere para a porta correta
com1 = enlace(serialName)

def main():
    try:
        # Habilitar comunicação
        com1.enable()
        
        time.sleep(.2)
        print('Cliente: Enviando byte de sacrifício')
        com1.sendData(b'00')
        print('Cliente: Byte de sacrifício enviado')
        time.sleep(1)
        
        
        print("Cliente: Comunicação habilitada")

        # Números a serem enviados (exemplo com números hard coded)
        numbers = [45.450000, -1.435670, 1.23e2, -3.14, 0.000123, 100, 100]
        
        
        # numbers = [1,2,3,4,5]
        print("Cliente: Números a serem enviados:", numbers)

        # Enviar cada número em formato IEEE-754
        for number in numbers:
            binary_representation = struct.pack('f', number)
            com1.sendData(binary_representation)
            print(f'Cliente: Enviado {number}')
            time.sleep(.1)

        # Aguardar a resposta do servidor
        timeout = 5
        start_time = time.time()
        response_received = False

        while (time.time() - start_time) < timeout:
            response, _ = com1.getData(4)  # Espera por 4 bytes (soma em ponto flutuante)
            if response:
                sum_result = struct.unpack('f', response)[0]
                print(f'Cliente: Soma recebida do servidor: {sum_result}')
                response_received = True
                break

        if not response_received:
            print("Cliente: Time out - Nenhuma resposta do servidor")

        # Finalizar a comunicação
        com1.disable()
        print("Cliente: Comunicação encerrada")

    except Exception as e:
        print("Cliente: Ocorreu um erro:", e)
        com1.disable()

if __name__ == "__main__":
    main()
