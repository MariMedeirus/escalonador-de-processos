"""Ponto de entrada do escalonador.

Uso: ``python Escalonador.py [diretorio_programas]``

Por padrão, lê o subdiretório ``programas`` ao lado deste arquivo.
Nesta etapa, o programa carrega os processos, monta a Tabela de Processos e a
Fila de Prontos e exibe o estado inicial do sistema.
"""

import sys
from pathlib import Path

from escalonador import carregar_processos, inicializar, ler_quantum

DIRETORIO_PADRAO = Path(__file__).resolve().parent / "programas"


def main(argv: list[str]) -> int:
    diretorio = Path(argv[1]) if len(argv) > 1 else DIRETORIO_PADRAO

    quantum = ler_quantum(diretorio)
    processos = carregar_processos(diretorio)
    tabela, prontos = inicializar(processos)

    print(f"Quantum: {quantum}")
    print(f"Tabela de Processos ({len(tabela)} processos):")
    for bcp in tabela:
        print(
            f"  {bcp.nome}: prioridade={bcp.prioridade} creditos={bcp.creditos} "
            f"pc={bcp.pc} estado={bcp.estado.value} X={bcp.x} Y={bcp.y} "
            f"instrucoes={len(bcp.segmento_texto)}"
        )
    print("Fila de Prontos (ordem de execução):")
    for bcp in prontos:
        print(f"  Carregando {bcp.nome}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
