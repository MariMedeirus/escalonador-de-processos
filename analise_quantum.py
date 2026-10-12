import re
import subprocess
import sys
from pathlib import Path

# Valores de quantum escolhidos para teste (pelo menos 10 valores)

quantums_teste = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]

raiz = Path(__file__).resolve().parent
diretorio_programas = raiz / "programas"
caminho_quantum = diretorio_programas / "quantum.txt"

def executar_testes():
    medias_trocas = []
    medias_instrucoes = []
    quantum_original = caminho_quantum.read_text(encoding="utf-8")

    try:
        for quantum in quantums_teste:
            caminho_quantum.write_text(f"{quantum}\n", encoding="utf-8")

            print(f"Executando o escalonador com quantum = {quantum}")

            resultado = subprocess.run(
                [sys.executable, str(raiz / "Escalonador.py"), str(diretorio_programas)],
                capture_output=True,
                text=True,
                cwd=raiz,
            )
            if resultado.returncode != 0:
                raise RuntimeError(resultado.stderr or resultado.stdout)

            caminho_log = diretorio_programas / f"log{quantum:02d}.txt"
            conteudo = caminho_log.read_text(encoding="utf-8")

            match_trocas = re.search(r"MEDIA DE TROCAS:\s*([\d.]+)", conteudo, re.IGNORECASE)
            match_instrucoes = re.search(
                r"MEDIA DE INSTRU[CÇ][OÕ]ES:\s*([\d.]+)", conteudo, re.IGNORECASE
            )
            if not match_trocas or not match_instrucoes:
                raise ValueError(f"Estatísticas não encontradas em {caminho_log}")

            medias_trocas.append(float(match_trocas.group(1)))
            medias_instrucoes.append(float(match_instrucoes.group(1)))
    finally:
        caminho_quantum.write_text(quantum_original, encoding="utf-8")

    return quantums_teste, medias_trocas, medias_instrucoes


if __name__ == "__main__":
    quantums, trocas, instrucoes = executar_testes()
    print("Quantum | Média de trocas | Média de instruções")
    for quantum, media_trocas, media_instrucoes in zip(quantums, trocas, instrucoes):
        print(f"{quantum:7} | {media_trocas:15g} | {media_instrucoes:19g}")