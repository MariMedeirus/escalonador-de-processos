"""
Estruturas do escalonador.
Aqui definimos as classes que organizam a tabela de processos e a fila de prontos.
"""

from collections.abc import Iterator

from .bcp import BCP, Estado


class TabelaProcessos:
    """
    Tabela de processos.
    Cada entrada guarda uma referencia para um bloco de controle de processo.
    Ela serve como um grande fichario que contem todos os processos presentes no sistema, nao importa o estado atual deles.
    """

    def __init__(self) -> None:
        # Inicia a tabela como uma lista vazia pronta para receber os processos.
        self._entradas: list[BCP] = []

    def adicionar(self, bcp: BCP) -> None:
        # Coloca um processo novo no final da lista da tabela.
        self._entradas.append(bcp)

    def remover(self, bcp: BCP) -> None:
        # Tira o processo especifico da lista.
        # Isso acontece quando o processo executa o comando de saida e termina de vez.
        self._entradas.remove(bcp)

    def __len__(self) -> int:
        # Devolve a quantidade total de processos guardados na tabela no momento.
        return len(self._entradas)

    def __iter__(self) -> Iterator[BCP]:
        # Permite que a gente use um laco for para passar por todos os processos da tabela.
        return iter(self._entradas)

    def __contains__(self, bcp: BCP) -> bool:
        # Permite perguntar se um processo especifico ainda esta guardado dentro da tabela.
        return bcp in self._entradas


class FilaProntos:
    """
    Fila de processos prontos.
    Ela organiza os processos que estao esperando para usar o processador.
    A fila eh sempre ordenada pela quantidade de creditos, do maior para o menor.
    Se dois processos tem o mesmo numero de creditos, o que chegou antes fica na frente.
    """

    def __init__(self) -> None:
        # Inicia a fila como uma lista vazia.
        self._fila: list[BCP] = []

    def inserir(self, bcp: BCP) -> None:
        """
        Insere o processo na posicao certa da fila de acordo com os creditos dele.
        """
        # Muda o estado do processo para pronto assim que ele entra nesta fila.
        bcp.estado = Estado.PRONTO
        
        # Assume inicialmente que o processo vai entrar no final da fila.
        posicao = len(self._fila)
        
        # Percorre a fila inteira para descobrir a posicao correta.
        for indice, outro in enumerate(self._fila):
            # Se encontrar um processo que tem menos creditos que o nosso processo novo, 
            # encontramos o lugar certo para furar a fila.
            if outro.creditos < bcp.creditos:
                posicao = indice
                # Corta o laco de busca pois ja achamos o lugar.
                break
                
        # Insere o processo exatamente na posicao encontrada.
        self._fila.insert(posicao, bcp)

    def remover_primeiro(self) -> BCP:
        """
        Remove e devolve o processo de maior numero de creditos que esta no topo da fila.
        """
        # Verifica se a fila esta vazia antes de tentar tirar alguem de la.
        if not self._fila:
            raise IndexError("Fila de prontos vazia")
            
        # Tira o primeiro item da lista e entrega ele para quem chamou a funcao.
        return self._fila.pop(0)

    def primeiro(self) -> BCP | None:
        # Apenas olha quem eh o primeiro da fila sem tirar ele de la, ou devolve nada se estiver vazia.
        return self._fila[0] if self._fila else None

    def vazia(self) -> bool:
        # Verifica se a fila esta vazia e devolve verdadeiro ou falso.
        return not self._fila
    
    def reordenar(self) -> None:
        """
        Arruma a fila inteira baseando-se nos creditos atuais, do maior para o menor.
        Isso eh necessario quando a gente devolve os creditos de todo mundo na redistribuicao.
        A ordem de chegada para empates eh mantida automaticamente pelo python.
        """
        # Usa a funcao de ordenacao nativa para organizar a lista olhando so para o atributo creditos.
        self._fila.sort(key=lambda bcp: bcp.creditos, reverse=True)

    def __len__(self) -> int:
        # Devolve quantos processos estao esperando na fila no momento.
        return len(self._fila)

    def __iter__(self) -> Iterator[BCP]:
        # Permite usar um laco for para passar por todos os processos que estao na fila.
        return iter(self._fila)


def inicializar(processos: list[BCP]) -> tuple[TabelaProcessos, FilaProntos]:
    """
    Monta a tabela e a fila de prontos pegando a lista de processos que acabou de ser lida.
    Os processos chegam na ordem alfabetica dos arquivos originais.
    """
    # Cria as estruturas vazias.
    tabela = TabelaProcessos()
    prontos = FilaProntos()
    
    # Passa por todos os processos da lista um por um.
    for bcp in processos:
        # Guarda o processo no fichario geral.
        tabela.adicionar(bcp)
        # Coloca o processo na fila de prontos para ele comecar a disputar o processador.
        prontos.inserir(bcp)
        
    # Entrega a tabela e a fila montadas e preenchidas.
    return tabela, prontos