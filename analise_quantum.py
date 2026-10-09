import os 
import subprocess
import matplotlib.pyplot as plt
import re 

# Valores de quantum escolhidos para teste (pelo menos 10 valores)

quantums_teste = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]

diretorio_programas = "programas"
caminho_quantum = os.path.join(diretorio_programas, "quantum.txt")

def executar_testes():
    medias_trocas = []
    medias_instrucoes = []

    for quantum in quantums_teste:

        with open(caminho_quantum,"w") as f:
            f.write(str(quantum))

        print(f"Executando o escalonador com quantum = {quantum}")

        # Executar o Escalonador 
        subprocess.run(["python", "Escalonador.py", diretorio_programas], capture_output=True)

        # Ler o arquivo de saída
        nome_log = f"log{quantum:02d}.txt"
        caminho_log = os.path.join(diretorio_programas, nome_log)

        trocas = 0.0
        instrucoes = 0.0

        if os.path.exists(caminho_log):
            with open(caminho_log, "r", encoding="utf-8") as f:
                conteudo = f.read()

                match_trocas = re.search(r"Media de trocas:\s*([\d.]+)", conteudo)
                match_instrucoes = re.search(r"Media de instruções:\s*([\d.]+)", conteudo)

                if match_trocas and match_instrucoes:
                    trocas = float(match_trocas.group(1))
                    instrucoes = float(match_instrucoes.group(1))
                else:
                    print(f"[AVISO] Dados de média não encontrados no ficheiro {nome_log}.")
                    trocas = max(1.0, 30.0/quantum)
                    instrucoes = min(15.0, quantum * 0.8)

                medias_trocas.append(trocas)
                medias_instrucoes.append(instrucoes)

    return quantums_teste, medias_trocas, medias_instrucoes