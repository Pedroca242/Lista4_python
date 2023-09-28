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

class LeituraSerial:
    def __init__(self, baudrate, port, escala_tempo, escala_tensao):
        self.serial = serial.Serial(port=port, baudrate=baudrate, timeout=0.5)
        self.escala_tempo = escala_tempo
        self.escala_tensao = escala_tensao

    def ler_dados(self):
        while True:
            dados = self.serial.read(4)
            if len(dados) != 4:
                break
            tempo, tensao = struct.unpack('hh', dados)
            tempo = tempo * self.escala_tempo
            tensao = tensao * self.escala_tensao
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
    try:
        leitor = LeituraArquivo(config["nome_arquivo"], config["escala_tempo"], config["escala_tensao"])
    except FileNotFoundError:
        print("Arquivo não encontrado")
        exit()
elif modo == "serial":
    try:
        leitor = LeituraSerial(config["baudrate"], config["port"], config["escala_tempo"], config["escala_tensao"])
    except serial.serialutil.SerialException:
        print("Porta serial inexistente")
        exit()
else:
    print("Modo inválido no arquivo de configuração.")
    exit()

dados = list(leitor.ler_dados())

while True:
    if len(dados) == 0:
        print("Nenhum dado lido")
        if modo == 'serial':
            dados = list(leitor.ler_dados())
        else:
            exit()
    elif len(dados) != config["tamanho_sequencia"]:
        print("Tamanho da sequência lida não corresponde ao configurado.")
        if modo == 'serial':
            dados = list(leitor.ler_dados())
        else:
            exit()
    else:
        break

calcular_fft(dados)
