"""Escalonador de processos para Time Sharing em uma máquina fictícia."""

from .bcp import BCP, Estado
from .carregador import carregar_processos, ler_prioridades, ler_quantum
from .estruturas import FilaProntos, TabelaProcessos, inicializar

__all__ = [
    "BCP",
    "Estado",
    "FilaProntos",
    "TabelaProcessos",
    "carregar_processos",
    "inicializar",
    "ler_prioridades",
    "ler_quantum",
]
