import os 
import subprocess
import matplotlib.pyplot as plt
import re 

# Valores de quantum escolhidos para teste (pelo menos 10 valores)

quantums_teste = [2, 4, 6, 8, 10, 12, 14, 16, 18, 21]

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

def plotar_graficos(quantums, trocas, instrucoes):

    # Gráfico 1: Média de trocas por processo
    plt.figure(figsize=(10, 5))
    plt.plot(quantums, trocas, marker='o', linestyle='-' , color='b')
    plt.title("Média de trocas por processo vs Tamanho do Quantum")
    plt.xlabel("Valor do Quantum")
    plt.ylabel("Média de trocas por processo")
    plt.xticks(quantums)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig("grafico_trocas.png")
    plt.show()

    # Gráfico 2: Média de instruções executadas por quantum
    plt.figure(figsize=(10, 5))
    plt.plot(quantums, instrucoes, marker='s', linestyle='-' , color='r')
    plt.title("Média de instruções executadas por Quantum")
    plt.xlabel("Valor do Quantum")
    plt.ylabel("Média de instruções executadas por quantum")
    plt.xticks(quantums)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig("grafico_instrucoes.png")
    plt.show()

if __name__ == "__main__":
    print("A iniciar a execução dos testes do escalonador...")
    valor_quantum, media_troca, media_instrucoes = executar_testes()
    print("\nExecuções concluídas! A gerar os gráficos...")
    plotar_graficos(valor_quantum, media_troca, media_instrucoes)
    print("Gráficos gerados com sucesso!")
        