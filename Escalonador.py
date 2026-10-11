"""Ponto de entrada do escalonador de processos."""

import sys
from pathlib import Path

from escalonador import FilaBloqueados, carregar_processos, inicializar, ler_quantum
from escalonador.bcp import Estado
from escalonador.logs import LogEscalonador

DIRETORIO_PADRAO = Path(__file__).resolve().parent / "programas"


def executar_motor(tabela, prontos, quantum, diretorio=None, log=None):
    """Executa os processos, registrando eventos e métricas da simulação."""
    # Mantem compatibilidade com chamadas que passam um logger como quarto argumento.
    if isinstance(diretorio, LogEscalonador) and log is None:
        log = diretorio
        diretorio = None

    # Guarda os processos em E/S e libera cada um apos dois usos da CPU por outros processos.
    bloqueados = FilaBloqueados()
    if log is None:
        # Salva o log junto dos arquivos de entrada, ou na pasta do escalonador por padrao.
        pasta_log = Path(diretorio) if diretorio is not None else Path(__file__).resolve().parent
        log = LogEscalonador(quantum, pasta_log)

    # Acumula as metricas legadas usadas pelo script de analise de quantum.
    processo_anterior = None
    total_trocas = 0
    total_instrucoes = 0
    processos_iniciados = len(tabela)
    simulacao_concluida = True

    # Cada iteracao representa uma passagem de um processo pela CPU.
    while len(tabela) > 0:
        if prontos.vazia():
            # Sem processo pronto, nao ha outra passagem que possa concluir a espera de E/S.
            simulacao_concluida = False
            if processo_anterior is not None:
                log.troca_contexto(processo_anterior.nome, "CPU ociosa")
            break

        # Seleciona o processo de maior credito e registra a troca de contexto.
        processo = prontos.remover_primeiro()
        log.troca_contexto(
            processo_anterior.nome if processo_anterior is not None else None,
            processo.nome,
        )
        processo.estado = Estado.EXECUTANDO
        total_trocas += 1

        # O processo consome um credito ao entrar na CPU.
        if processo.creditos > 0:
            processo.creditos -= 1

        comandos_executados = 0
        fez_es = False
        terminou = False

        # Executa no maximo o quantum, avancando o PC antes de tratar cada instrucao.
        while comandos_executados < quantum:
            instrucao = processo.instrucao_atual
            processo.pc += 1
            comandos_executados += 1
            total_instrucoes += 1

            # Interpreta atribuicoes, operacao sem efeito e instrucoes de controle.
            if instrucao.startswith("X="):
                processo.x = int(instrucao.split("=")[1])
            elif instrucao.startswith("Y="):
                processo.y = int(instrucao.split("=")[1])
            elif instrucao == "COM":
                pass
            elif instrucao == "E/S":
                fez_es = True
                log.interrupcao(processo.nome, "E/S")
                break
            elif instrucao == "SAIDA":
                terminou = True
                log.termino(processo.nome)
                break

        # Define o destino do processo apos a CPU: removido, bloqueado ou pronto.
        if terminou:
            tabela.remover(processo)
        elif not fez_es:
            prontos.inserir(processo)
            log.interrupcao(processo.nome, "Fim de Quantum")

        # Quando todos esgotam os creditos, redistribui as prioridades iniciais.
        total_creditos = sum(p.creditos or 0 for p in tabela)
        if total_creditos == 0 and len(tabela) > 0:
            for p in tabela:
                p.creditos = p.prioridade
            prontos.reordenar()

        # Avanca somente os bloqueios existentes durante esta passagem pela CPU.
        bloqueados.avancar_ciclo(prontos)
        if fez_es:
            # A E/S atual comeca a esperar depois do decremento dos bloqueios anteriores.
            bloqueados.inserir(processo, FilaBloqueados.CICLOS_ESPERA)

        processo_anterior = processo

    # Registra a liberacao da CPU quando a simulacao termina sem impasse.
    if simulacao_concluida and processo_anterior is not None:
        log.troca_contexto(processo_anterior.nome, "CPU ociosa")

    # Mantem no mesmo arquivo os dados consumidos pelo analise_quantum.py.
    media_trocas = total_trocas / processos_iniciados if processos_iniciados else 0
    media_instrucoes = total_instrucoes / total_trocas if total_trocas else 0
    log.registrar(f"Quantum: {quantum}")
    log.registrar(f"Media de trocas: {media_trocas:.2f}")
    log.registrar(f"Media de instruções: {media_instrucoes:.2f}")
    return simulacao_concluida


def main(argv: list[str]) -> int:
    # Usa o diretorio informado na linha de comando ou a pasta padrao de programas.
    diretorio = Path(argv[1]) if len(argv) > 1 else DIRETORIO_PADRAO

    quantum = ler_quantum(diretorio)
    processos = carregar_processos(diretorio)
    tabela, prontos = inicializar(processos)

    print(f"Iniciando simulação com quantum: {quantum}")
    print("-" * 40)
    simulacao_concluida = executar_motor(tabela, prontos, quantum, diretorio)
    print("-" * 40)

    if simulacao_concluida:
        print("Simulação concluída. Todos os processos realizaram SAIDA.")
        return 0
    print("Simulação encerrada com processos ainda bloqueados.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))