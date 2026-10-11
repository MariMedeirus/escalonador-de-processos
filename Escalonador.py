"""
Ponto de entrada do escalonador.

Uso: python Escalonador.py [diretorio_programas]

Por padrao, le o subdiretorio 'programas' ao lado deste arquivo.
Nesta etapa, o programa carrega os processos, monta a tabela de processos e a
fila de prontos e exibe o estado inicial do sistema.
"""

import sys
from pathlib import Path

from escalonador import carregar_processos, inicializar, ler_quantum
from escalonador.bcp import Estado
from escalonador.estruturas import FilaBloqueados

DIRETORIO_PADRAO = Path(__file__).resolve().parent / "programas"

def executar_motor(tabela, prontos, quantum, diretorio):
    """
    Loop principal de execucao do processador.
    Eh aqui que a simulacao do sistema operacional ganha vida e faz o time sharing.
    """
    
    # Fila que gerencia o tempo de espera de entrada e saida.
    bloqueados = FilaBloqueados() 

    # Variaveis para acumular os dados que vao para o relatorio.
    total_trocas = 0
    total_instrucoes = 0
    processos_iniciados = len(tabela)

    # Laco principal do sistema operacional. 
    while len(tabela) > 0:
        
        # Se a fila de prontos esta vazia, o processador fica ocioso.
        if prontos.vazia():
            # Trava de seguranca.
            if bloqueados.vazia():
                break 
            
            # O processador nao faz nada, mas o tempo passa para quem esta bloqueado.
            liberados = bloqueados.passar_tempo()
            for p in liberados:
                prontos.inserir(p)
            continue 
            
        # Troca de contexto.
        processo = prontos.remover_primeiro()
        processo.estado = Estado.EXECUTANDO
        
        # Toda vez que um processo entra na cpu, contabilizamos uma troca.
        total_trocas += 1
        
        if processo.creditos > 0:
            processo.creditos -= 1

        comandos_executados = 0
        fez_es = False
        terminou = False

        while comandos_executados < quantum:
            
            instrucao = processo.instrucao_atual
            processo.pc += 1
            comandos_executados += 1
            
            # Conta o total global de instrucoes para fazer a media depois.
            total_instrucoes += 1

            if instrucao.startswith("X="):
                processo.x = int(instrucao.split("=")[1])
            elif instrucao.startswith("Y="):
                processo.y = int(instrucao.split("=")[1])
            elif instrucao == "COM":
                pass 
            elif instrucao == "E/S":
                fez_es = True
                break 
            elif instrucao == "SAIDA":
                terminou = True
                break 

        # O quantum acabou, entao passamos o tempo para quem estava bloqueado.
        liberados = bloqueados.passar_tempo()

        # Decisao de destino do processo atual.
        if terminou:
            tabela.remover(processo)
        elif fez_es:
            # Vai para a fila de bloqueados passar por 2 ciclos.
            bloqueados.inserir(processo, 2)
        else:
            prontos.inserir(processo) 

        # Os processos que terminaram a E/S voltam para a fila de prontos.
        for p in liberados:
            prontos.inserir(p)

        # Regra de redistribuicao de creditos.
        total_creditos = sum(p.creditos for p in prontos) + sum(p.creditos for p in bloqueados)
        if total_creditos == 0 and len(tabela) > 0:
            for p in tabela:
                p.creditos = p.prioridade
            prontos.reordenar()

    # Fim da simulacao. Calcula as medias para o grafico.
    media_trocas = total_trocas / processos_iniciados if processos_iniciados > 0 else 0
    media_instrucoes = total_instrucoes / total_trocas if total_trocas > 0 else 0

    # Gera o arquivo de log no mesmo diretorio de programas.
    caminho_log = diretorio / f"log{quantum:02d}.txt"
    with open(caminho_log, "w", encoding="utf-8") as f:
        f.write(f"Quantum: {quantum}\n")
        f.write(f"Media de trocas: {media_trocas:.2f}\n")
        f.write(f"Media de instrucoes: {media_instrucoes:.2f}\n")

def main(argv: list[str]) -> int:
    diretorio = Path(argv[1]) if len(argv) > 1 else DIRETORIO_PADRAO

    quantum = ler_quantum(diretorio)
    processos = carregar_processos(diretorio)
    tabela, prontos = inicializar(processos)
    
    print(f"Iniciando simulacao com quantum: {quantum}")
    print("-" * 40)
    
    # Passamos o diretorio para ele saber onde salvar o txt.
    executar_motor(tabela, prontos, quantum, diretorio)
    
    print("-" * 40)
    print("Simulacao concluida. Log gerado com sucesso.")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))