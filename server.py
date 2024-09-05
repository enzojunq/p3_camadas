import struct
from enlace import *

# Configurar a porta serial
serialName = "COM3"  # Altere para a porta correta
com2 = enlace(serialName)

def main():
    try:
        # Habilitar comunicação
        com2.enable()
        print(f'Esperando primeiro byte.')
        rxBuffer, nRx = com2.getData(1)
        com2.rx.clearBuffer()
        time.sleep(.1)
        print("Servidor: Comunicação habilitada")

        print("Servidor: Aguardando números...")

        numbers = []
        while True:
            # Tenta receber 4 bytes (um float 32 bits)
            rxBuffer, nRx = com2.getData(4)
            print(len(numbers))
            number = struct.unpack('f', rxBuffer)[0]
            print(f'Servidor: Recebido {number}')
            numbers.append(number)
            if len(numbers) > 4:
                break  # Se menos de 4 bytes foram recebidos, a transmissão acabou
        print('saiu do while')

        # Calcular a soma dos números recebidos
        total_sum = sum(numbers)
        print(f'Servidor: Soma calculada: {total_sum}')

        # Converter a soma para formato IEEE-754 e enviar de volta ao cliente
        binary_sum = struct.pack('f', total_sum)
        com2.sendData(binary_sum)
        print(f'Servidor: Soma enviada ao cliente: {total_sum}')

        # Finalizar a comunicação
        com2.disable()
        print("Servidor: Comunicação encerrada")

    except Exception as e:
        print("Servidor: Ocorreu um erro:", e)
        com2.disable()

if __name__ == "__main__":
    main()
