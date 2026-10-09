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

DIRETORIO_PADRAO = Path(__file__).resolve().parent / "programas"

def executar_motor(tabela, prontos, quantum):
    """
    Loop principal de execucao do processador.
    Eh aqui que a simulacao do sistema operacional ganha vida e faz o time sharing.
    """
    
    # Fila temporaria para os processos que pediram entrada e saida.
    # Serve apenas para o codigo nao quebrar agora, a Mikelly fara a oficial.
    bloqueados = [] 

    # Laco principal do sistema operacional. 
    # Enquanto houver processos vivos na tabela, o nosso processador continua trabalhando.
    while len(tabela) > 0:
        
        # Se a fila de prontos esta vazia, o processador fica ocioso.
        if prontos.vazia():
            # Aqui, no futuro, o tempo vai passar ate um processo bloqueado ser liberado.
            # Usamos o break temporario so para evitar um loop infinito nos testes de agora.
            break 
            
        # Troca de contexto.
        # Tiramos o primeiro processo da fila de prontos, pois ele eh o que tem mais creditos.
        processo = prontos.remover_primeiro()
        
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
            bloqueados.append(processo)
            
        else:
            # Se chegou aqui, o quantum acabou normalmente por limite de tempo.
            # O status volta a ser pronto e ele entra de volta na fila. 
            # O metodo ja coloca ele na posicao correta de acordo com os creditos que sobraram.
            prontos.inserir(processo) 

        # Regra de redistribuicao de creditos.
        # Soma todos os creditos que restam nos processos prontos e bloqueados.
        total_creditos = sum(p.creditos for p in prontos) + sum(p.creditos for p in bloqueados)
        
        # A redistribuicao so acontece se todo mundo zerou os creditos e ainda existe gente viva.
        if total_creditos == 0 and len(tabela) > 0:
            # Varre todos os processos ativos e devolve o credito baseando-se na prioridade do arquivo original.
            for p in tabela:
                p.creditos = p.prioridade
                
            # Como a quantidade de creditos de todo mundo mudou agora, precisamos avisar a fila de prontos.
            # Ela vai se reorganizar do maior para o menor credito.
            prontos.reordenar()


def main(argv: list[str]) -> int:
    diretorio = Path(argv[1]) if len(argv) > 1 else DIRETORIO_PADRAO

    quantum = ler_quantum(diretorio)
    processos = carregar_processos(diretorio)
    tabela, prontos = inicializar(processos)
    
    print(f"Iniciando simulacao com quantum: {quantum}")
    print("-" * 40)
    
    # Chama o motor principal passando as estruturas.
    executar_motor(tabela, prontos, quantum)
    
    print("-" * 40)
    print("Simulacao concluida. Todos os processos realizaram saida.")
    
    # Encerra o script com sucesso.
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))