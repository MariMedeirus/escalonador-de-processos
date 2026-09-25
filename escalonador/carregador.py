"""Leitura dos arquivos de entrada: programas, ``prioridades.txt`` e ``quantum.txt``.

Todos os arquivos ficam no diretório ``programas``. Cada programa está em um
arquivo ``NN.txt`` (``01.txt``, ``02.txt``, ...): a primeira linha é o nome do
programa e as seguintes são as instruções, terminando em ``SAIDA``.
"""

import re
from pathlib import Path

from .bcp import BCP

ARQUIVO_PRIORIDADES = "prioridades.txt"
ARQUIVO_QUANTUM = "quantum.txt"

# Nome de arquivo de programa: inteiro sequencial de dois dígitos.
PADRAO_NOME_PROGRAMA = re.compile(r"^\d{2}\.txt$")

# Instruções aceitas pela máquina fictícia.
PADRAO_ATRIBUICAO = re.compile(r"^[XY]=-?\d+$")
INSTRUCOES_SIMPLES = {"COM", "E/S", "SAIDA"}


def _ler_linhas(caminho: Path) -> list[str]:
    """Lê um arquivo-texto e devolve suas linhas não vazias, sem espaços nas bordas."""
    try:
        conteudo = caminho.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        conteudo = caminho.read_text(encoding="latin-1")
    return [linha.strip() for linha in conteudo.splitlines() if linha.strip()]


def _ler_inteiros(caminho: Path) -> list[int]:
    linhas = _ler_linhas(caminho)
    try:
        return [int(linha) for linha in linhas]
    except ValueError as erro:
        raise ValueError(f"Valor não inteiro em {caminho}: {erro}") from None


def instrucao_valida(instrucao: str) -> bool:
    """Verifica se a instrução pertence ao conjunto aceito pelo processador."""
    return instrucao in INSTRUCOES_SIMPLES or bool(PADRAO_ATRIBUICAO.match(instrucao))


def ler_quantum(diretorio: Path) -> int:
    """Lê o inteiro único de ``quantum.txt``."""
    valores = _ler_inteiros(diretorio / ARQUIVO_QUANTUM)
    if len(valores) != 1:
        raise ValueError(f"{ARQUIVO_QUANTUM} deve conter exatamente um inteiro")
    if valores[0] <= 0:
        raise ValueError("O quantum deve ser um inteiro positivo")
    return valores[0]


def ler_prioridades(diretorio: Path) -> list[int]:
    """Lê ``prioridades.txt``: uma prioridade por linha, na ordem alfabética dos programas."""
    return _ler_inteiros(diretorio / ARQUIVO_PRIORIDADES)


def ler_programa(caminho: Path) -> tuple[str, list[str]]:
    """Lê um arquivo de programa e devolve ``(nome, segmento_texto)``."""
    linhas = _ler_linhas(caminho)
    if len(linhas) < 2:
        raise ValueError(f"{caminho.name}: programa precisa de nome e ao menos uma instrução")

    nome, instrucoes = linhas[0], linhas[1:]
    for numero, instrucao in enumerate(instrucoes, start=1):
        if not instrucao_valida(instrucao):
            raise ValueError(f"{caminho.name}: instrução inválida na posição {numero}: '{instrucao}'")
    if instrucoes[-1] != "SAIDA":
        raise ValueError(f"{caminho.name}: programa deve terminar com SAIDA")
    return nome, instrucoes


def listar_arquivos_programas(diretorio: Path) -> list[Path]:
    """Arquivos ``NN.txt`` do diretório, em ordem alfabética."""
    return sorted(p for p in diretorio.iterdir() if PADRAO_NOME_PROGRAMA.match(p.name))


def carregar_processos(diretorio: Path) -> list[BCP]:
    """Carrega os programas do diretório em BCPs, na ordem alfabética dos arquivos.

    A prioridade da linha ``i`` de ``prioridades.txt`` é associada ao ``i``-ésimo
    programa; os créditos iniciais de cada BCP são iguais à sua prioridade.
    """
    diretorio = Path(diretorio)
    arquivos = listar_arquivos_programas(diretorio)
    if not arquivos:
        raise FileNotFoundError(f"Nenhum programa NN.txt encontrado em {diretorio}")

    prioridades = ler_prioridades(diretorio)
    if len(prioridades) != len(arquivos):
        raise ValueError(
            f"{ARQUIVO_PRIORIDADES} tem {len(prioridades)} linhas, "
            f"mas há {len(arquivos)} programas"
        )

    processos = []
    for arquivo, prioridade in zip(arquivos, prioridades):
        nome, segmento_texto = ler_programa(arquivo)
        processos.append(BCP(nome=nome, prioridade=prioridade, segmento_texto=segmento_texto))
    return processos
