"""Bloco de Controle de Processo (BCP).

O BCP guarda tudo o que o escalonador precisa para interromper um processo
e, mais tarde, retomá-lo exatamente de onde parou.
"""

from dataclasses import dataclass, field
from enum import Enum

# Tamanho máximo do segmento de texto de um programa (comandos, incluindo SAIDA).
TAMANHO_MAXIMO_PROGRAMA = 21


class Estado(Enum):
    """Estados possíveis de um processo."""

    PRONTO = "Pronto"
    EXECUTANDO = "Executando"
    BLOQUEADO = "Bloqueado"


@dataclass
class BCP:
    """Bloco de Controle de Processo.

    Atributos:
        nome: nome do programa (primeira linha do arquivo).
        prioridade: prioridade lida de ``prioridades.txt`` (maior = mais prioritário).
        segmento_texto: referência à região de memória com o código do programa
            (um comando por posição, no máximo ``TAMANHO_MAXIMO_PROGRAMA``).
        pc: Contador de Programa — índice, em ``segmento_texto``, da próxima
            instrução a ser executada.
        estado: estado atual do processo (Pronto, Executando ou Bloqueado).
        creditos: créditos restantes; começam iguais à prioridade.
        x, y: registradores de uso geral.
    """

    nome: str
    prioridade: int
    segmento_texto: list[str] = field(repr=False)
    pc: int = 0
    estado: Estado = Estado.PRONTO
    creditos: int | None = None
    x: int = 0
    y: int = 0

    def __post_init__(self) -> None:
        if len(self.segmento_texto) > TAMANHO_MAXIMO_PROGRAMA:
            raise ValueError(
                f"Programa '{self.nome}' tem {len(self.segmento_texto)} comandos; "
                f"o máximo é {TAMANHO_MAXIMO_PROGRAMA}"
            )
        if self.prioridade < 0:
            raise ValueError(f"Prioridade de '{self.nome}' não pode ser negativa")
        if self.creditos is None:
            self.creditos = self.prioridade

    @property
    def instrucao_atual(self) -> str:
        """Instrução apontada pelo Contador de Programa."""
        return self.segmento_texto[self.pc]
