import json
import struct
import serial
import numpy as np
import matplotlib.pyplot as plt

class LeituraArquivo:
    def __init__(self, arquivo, escala_tempo, escala_tensao):
        self.arquivo = arquivo
        self.escala_tempo = escala_tempo
        self.escala_tensao = escala_tensao

    def ler_dados(self):
        with open(self.arquivo, 'rb') as file:
            while True:
                dados = file.read(4)
                if len(dados) != 4:
                    break
                tempo, tensao = struct.unpack('hh', dados)
                tempo = tempo * self.escala_tempo
                tensao = tensao * self.escala_tensao
                yield tempo, tensao

class LeituraSerial: #avr
    def __init__(self, baudrate, port, escala_tempo, escala_tensao):
        self.serial = serial.Serial(port=port, baudrate=baudrate, timeout=0.5)
        self.escala_tempo = escala_tempo
        self.escala_tensao = escala_tensao

    def ler_dados(self):
        with self.serial as ser:
            n = 0
            while True:
                dados = ser.read(4)
                print(dados)
                if len(dados) != 4 or n == 200:
                    break
                tempo, tensao = struct.unpack('hh', dados)
                tempo = tempo * self.escala_tempo
                tensao = tensao * self.escala_tensao
                n += 1
                yield tempo, tensao


def calcular_fft(dados):
    tempo = [item[0] for item in dados]
    tensao = [item[1] for item in dados]

    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.plot(tempo, tensao, c='black')
    plt.title('Sequência no Tempo')
    plt.xlabel('Tempo (s)')
    plt.ylabel('Tensão (V)')

    plt.subplot(1, 2, 2)
    fft_result = np.fft.fft(tensao)
    freq = np.fft.fftfreq(len(tensao))
    plt.plot(freq, abs(fft_result), c='black')
    plt.title('FFT')
    plt.xlabel('Frequência (Hz)')
    plt.ylabel('Amplitude')

    plt.tight_layout()
    plt.show()

with open('config.json', 'r') as arquivo_config:
    config = json.load(arquivo_config)

modo = config["modo"]
if modo == "arquivo":
    leitor = LeituraArquivo("4a_lista_dados.bin", config["escala_tempo"], config["escala_tensao"])
    dados = list(leitor.ler_dados())
elif modo == "serial":
    leitor = LeituraSerial(config["baudrate"], config["port"], config["escala_tempo"], config["escala_tensao"])
    dados = list(leitor.ler_dados())
    while True:
        if len(dados) == 0:
            print("Nenhum dado lido")
            dados = list(leitor.ler_dados())
        else:
            break
else:
    print("Modo inválido no arquivo de configuração.")
    exit()



if not dados:
    print("Nenhum dado lido.")
elif len(dados) != config["tamanho_sequencia"]:
    print("Tamanho da sequência lida não corresponde ao configurado.")
else:
    calcular_fft(dados)
