"""Ponto de entrada do escalonador.

Uso: ``python Escalonador.py [diretorio_programas]``

Por padrão, lê o subdiretório ``programas`` ao lado deste arquivo.
Nesta etapa, o programa carrega os processos, monta a Tabela de Processos e a
Fila de Prontos e exibe o estado inicial do sistema.
"""

import sys
from pathlib import Path

from escalonador import carregar_processos, inicializar, ler_quantum
from escalonador.bcp import Estado

DIRETORIO_PADRAO = Path(__file__).resolve().parent / "programas"

def executar_motor(tabela, prontos, quantum):
    """Loop principal de execução do processador."""
    
    bloqueados = [] # Fila temporária para que o código não quebre.

    # O sistema roda enquanto houver processos na tabela de processos
    while len(tabela) > 0:
        
        if prontos.vazia():
            # Se não há prontos, mas há bloqueados, o tempo passa
            break # Usando break temporário apenas para evitar loop infinito nos seus testes iniciais
            
        # Puxa o primeiro da fila
        processo = prontos.remover_primeiro()
        processo.estado = Estado.EXECUTANDO
        
        # O processo perde 1 crédito ao entrar no processador
        if processo.creditos > 0:
            processo.creditos -= 1

        # Inicia o quantum
        comandos_executados = 0
        fez_es = False
        terminou = False

        while comandos_executados < quantum:
            # Lê a instrução atual e avança o program counter (PC)
            instrucao = processo.instrucao_atual
            processo.pc += 1
            comandos_executados += 1

            # Interpretador de comandos
            if instrucao.startswith("X="):
                processo.x = int(instrucao.split("=")[1])
            elif instrucao.startswith("Y="):
                processo.y = int(instrucao.split("=")[1])
            elif instrucao == "COM":
                pass # Apenas gasta 1 tempo do quantum
            elif instrucao == "E/S":
                fez_es = True
                break # Sai do processador antes do quantum terminar
            elif instrucao == "SAIDA":
                terminou = True
                break # Processo chegou ao fim

        # Decide para onde o processo vai
        if terminou:
            tabela.remover(processo)
        elif fez_es:
            processo.estado = Estado.BLOQUEADO
            bloqueados.append(processo)
        else:
            # Fim de quantum normal: volta para a fila de prontos
            prontos.inserir(processo) # O método inserir já o coloca na posição correta

        # Regra de redistribuição de créditos
        total_creditos = sum(p.creditos for p in prontos) + sum(p.creditos for p in bloqueados)
        
        if total_creditos == 0 and len(tabela) > 0:
            for p in tabela:
                p.creditos = p.prioridade
            prontos.reordenar()


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
