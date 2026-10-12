"""
Ponto de entrada do escalonador.

Uso: python Escalonador.py [diretorio_programas]

Por padrao, le o subdiretorio 'programas' ao lado deste arquivo.
Nesta etapa, o programa carrega os processos, monta a tabela de processos e a
fila de prontos e exibe o estado inicial do sistema.
"""

import sys
from pathlib import Path
from typing import TextIO

from escalonador import carregar_processos, inicializar, ler_quantum
from escalonador.bcp import Estado

DIRETORIO_PADRAO = Path(__file__).resolve().parent / "programas"

def executar_motor(tabela, prontos, quantum, arquivo_log: TextIO) -> tuple[int, int]:
    """
    Loop principal de execucao do processador.
    Eh aqui que a simulacao do sistema operacional ganha vida e faz o time sharing.
    """
    
    fatias_executadas = 0
    instrucoes_executadas = 0
    bloqueados = []

    def registrar(mensagem: str) -> None:
        arquivo_log.write(mensagem + "\n")

    def atualizar_bloqueados(ignorar=None) -> None:
        restantes = []
        for bloqueado, espera in bloqueados:
            if bloqueado is ignorar:
                restantes.append((bloqueado, espera))
                continue
            espera -= 1
            if espera == 0:
                prontos.inserir(bloqueado)
            else:
                restantes.append((bloqueado, espera))
        bloqueados[:] = restantes

    for processo in prontos:
        registrar(f"Carregando {processo.nome}")

    # Laco principal do sistema operacional. 
    # Enquanto houver processos vivos na tabela, o nosso processador continua trabalhando.
    while len(tabela) > 0:
        
        # Se a fila de prontos esta vazia, o processador fica ocioso.
        if prontos.vazia():
            if not bloqueados:
                break
            atualizar_bloqueados()
            continue
            
        # Troca de contexto.
        # Tiramos o primeiro processo da fila de prontos, pois ele eh o que tem mais creditos.
        processo = prontos.remover_primeiro()
        registrar(f"Executando {processo.nome}")
        
        # Mudamos o cracha dele para mostrar que ele eh o dono do processador neste momento.
        processo.estado = Estado.EXECUTANDO
        
        # O aluguel do processador custa um credito. 
        # Se ele ainda tem creditos sobrando, descontamos na hora que ele entra.
        if processo.creditos > 0:
            processo.creditos -= 1

        # Preparacao do quantum.
        # Preparamos os contadores para controlar o tempo que esse processo vai ficar processando.
        comandos_executados = 0
        fez_es = False
        terminou = False

        # O processo so pode executar comandos ate bater no teto do quantum lido no arquivo.
        while comandos_executados < quantum:
            
            # Pega o texto da instrucao exatamente onde o contador de programa esta apontando.
            instrucao = processo.instrucao_atual
            
            # Anda com o contador um passo para frente, senao ele roda a mesma linha para sempre.
            processo.pc += 1
            comandos_executados += 1

            # Interpretador de comandos.
            if instrucao.startswith("X="):
                # Quebra a string no sinal de igual e salva apenas o numero inteiro no registrador.
                processo.x = int(instrucao.split("=")[1])
                
            elif instrucao.startswith("Y="):
                # Faz a mesma coisa que a instrucao anterior, mas salva no outro registrador.
                processo.y = int(instrucao.split("=")[1])
                
            elif instrucao == "COM":
                # Eh uma instrucao generica, nao muda variaveis, apenas gasta o tempo.
                pass 
                
            elif instrucao == "E/S":
                # O programa pediu um dado externo. 
                fez_es = True
                registrar(f"E/S iniciada em {processo.nome}")
                # Corta o laco na hora e perde o resto do tempo disponivel.
                break 
                
            elif instrucao == "SAIDA":
                # A instrucao final do arquivo de texto, o programa acabou.
                terminou = True
                break 

        # Decisao de destino.
        # O tempo acabou e agora o sistema decide para onde mandar o processo.
        if terminou:
            # Se ele leu a saida, a vida util dele acabou e ele eh apagado da tabela principal.
            tabela.remover(processo)
            
        elif fez_es:
            # Se ele fez entrada e saida, ele vai para a espera. 
            # Muda o status para bloqueado e entra na fila temporaria.
            processo.estado = Estado.BLOQUEADO
            bloqueados.append((processo, 2))
            
        else:
            # Se chegou aqui, o quantum acabou normalmente por limite de tempo.
            # O status volta a ser pronto e ele entra de volta na fila. 
            # O metodo ja coloca ele na posicao correta de acordo com os creditos que sobraram.
            prontos.inserir(processo) 

        registrar(f"Interrompendo {processo.nome} após {comandos_executados} instruções")
        fatias_executadas += 1
        instrucoes_executadas += comandos_executados

        if terminou:
            registrar(f"{processo.nome} terminado. X={processo.x}. Y={processo.y}")

        atualizar_bloqueados(ignorar=processo if fez_es else None)

        # Regra de redistribuicao de creditos.
        # Soma todos os creditos que restam nos processos prontos e bloqueados.
        total_creditos = sum(p.creditos for p in prontos) + sum(p.creditos for p, _ in bloqueados)
        
        # A redistribuicao so acontece se todo mundo zerou os creditos e ainda existe gente viva.
        if total_creditos == 0 and len(tabela) > 0:
            # Varre todos os processos ativos e devolve o credito baseando-se na prioridade do arquivo original.
            for p in tabela:
                p.creditos = p.prioridade
                
            # Como a quantidade de creditos de todo mundo mudou agora, precisamos avisar a fila de prontos.
            # Ela vai se reorganizar do maior para o menor credito.
            prontos.reordenar()

    return fatias_executadas, instrucoes_executadas


def main(argv: list[str]) -> int:
    diretorio = Path(argv[1]) if len(argv) > 1 else DIRETORIO_PADRAO

    quantum = ler_quantum(diretorio)
    processos = carregar_processos(diretorio)
    tabela, prontos = inicializar(processos)
    
    print(f"Iniciando simulacao com quantum: {quantum}")
    print("-" * 40)
    
    caminho_log = diretorio / f"log{quantum:02d}.txt"
    with caminho_log.open("w", encoding="utf-8") as arquivo_log:
        fatias, instrucoes = executar_motor(tabela, prontos, quantum, arquivo_log)
        media_trocas = fatias / len(processos)
        media_instrucoes = instrucoes / fatias if fatias else 0
        arquivo_log.write(f"MEDIA DE TROCAS: {media_trocas:g}\n")
        arquivo_log.write(f"MEDIA DE INSTRUCOES: {media_instrucoes:g}\n")
        arquivo_log.write(f"QUANTUM: {quantum}\n")

    print(f"Log gerado: {caminho_log}")
    
    print("-" * 40)
    print("Simulacao concluida. Todos os processos realizaram saida.")
    
    # Encerra o script com sucesso.
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))