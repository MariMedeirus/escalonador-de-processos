"""Ponto de entrada do escalonador de processos."""

import sys
from pathlib import Path

from escalonador import FilaBloqueados, carregar_processos, inicializar, ler_quantum
from escalonador.bcp import Estado
from escalonador.logs import LogEscalonador

DIRETORIO_PADRAO = Path(__file__).resolve().parent / "programas"


def executar_motor(tabela, prontos, quantum, diretorio=None, log=None):
    """Executa os processos, registrando eventos e métricas da simulação."""
    if isinstance(diretorio, LogEscalonador) and log is None:
        log = diretorio
        diretorio = None

    bloqueados = FilaBloqueados()
    if log is None:
        pasta_log = Path(diretorio) if diretorio is not None else Path(__file__).resolve().parent
        log = LogEscalonador(quantum, pasta_log)

    processo_anterior = None
    total_trocas = 0
    total_instrucoes = 0
    processos_iniciados = len(tabela)
    simulacao_concluida = True

    while len(tabela) > 0:
        if prontos.vazia():
            simulacao_concluida = False
            if processo_anterior is not None:
                log.troca_contexto(processo_anterior.nome, "CPU ociosa")
            break

        processo = prontos.remover_primeiro()
        log.troca_contexto(
            processo_anterior.nome if processo_anterior is not None else None,
            processo.nome,
        )
        processo.estado = Estado.EXECUTANDO
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
            total_instrucoes += 1

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

        if terminou:
            tabela.remover(processo)
        elif not fez_es:
            prontos.inserir(processo)
            log.interrupcao(processo.nome, "Fim de Quantum")

        total_creditos = sum(p.creditos or 0 for p in tabela)
        if total_creditos == 0 and len(tabela) > 0:
            for p in tabela:
                p.creditos = p.prioridade
            prontos.reordenar()

        bloqueados.avancar_ciclo(prontos)
        if fez_es:
            bloqueados.inserir(processo, FilaBloqueados.CICLOS_ESPERA)

        processo_anterior = processo

    if simulacao_concluida and processo_anterior is not None:
        log.troca_contexto(processo_anterior.nome, "CPU ociosa")

    media_trocas = total_trocas / processos_iniciados if processos_iniciados else 0
    media_instrucoes = total_instrucoes / total_trocas if total_trocas else 0
    log.registrar(f"Quantum: {quantum}")
    log.registrar(f"Media de trocas: {media_trocas:.2f}")
    log.registrar(f"Media de instruções: {media_instrucoes:.2f}")
    return simulacao_concluida


def main(argv: list[str]) -> int:
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