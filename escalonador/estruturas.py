"""Estruturas do escalonador: Tabela de Processos e Fila de Prontos."""

from collections.abc import Iterator

from .bcp import BCP, Estado


class TabelaProcessos:
    """Tabela de Processos: cada entrada é uma referência a um BCP.

    Contém todos os processos presentes no sistema, independentemente do estado.
    """

    def __init__(self) -> None:
        self._entradas: list[BCP] = []

    def adicionar(self, bcp: BCP) -> None:
        self._entradas.append(bcp)

    def remover(self, bcp: BCP) -> None:
        self._entradas.remove(bcp)

    def __len__(self) -> int:
        return len(self._entradas)

    def __iter__(self) -> Iterator[BCP]:
        return iter(self._entradas)

    def __contains__(self, bcp: BCP) -> bool:
        return bcp in self._entradas


class FilaProntos:
    """Fila de processos prontos, ordenada por créditos (do maior para o menor).

    Empates são resolvidos por ordem de chegada: um processo inserido com o
    mesmo número de créditos de outro já na fila fica atrás dele.
    """

    def __init__(self) -> None:
        self._fila: list[BCP] = []

    def inserir(self, bcp: BCP) -> None:
        """Insere o BCP na posição correspondente aos seus créditos atuais."""
        bcp.estado = Estado.PRONTO
        posicao = len(self._fila)
        for indice, outro in enumerate(self._fila):
            if outro.creditos < bcp.creditos:
                posicao = indice
                break
        self._fila.insert(posicao, bcp)

    def remover_primeiro(self) -> BCP:
        """Remove e devolve o processo de maior número de créditos."""
        if not self._fila:
            raise IndexError("Fila de prontos vazia")
        return self._fila.pop(0)

    def primeiro(self) -> BCP | None:
        return self._fila[0] if self._fila else None

    def vazia(self) -> bool:
        return not self._fila

    def __len__(self) -> int:
        return len(self._fila)

    def __iter__(self) -> Iterator[BCP]:
        return iter(self._fila)


def inicializar(processos: list[BCP]) -> tuple[TabelaProcessos, FilaProntos]:
    """Monta a Tabela de Processos e a Fila de Prontos a partir dos BCPs carregados.

    Os processos devem vir na ordem alfabética dos arquivos; a fila de prontos
    resultante fica ordenada por créditos (iguais à prioridade nesse momento).
    """
    tabela = TabelaProcessos()
    prontos = FilaProntos()
    for bcp in processos:
        tabela.adicionar(bcp)
        prontos.inserir(bcp)
    return tabela, prontos
