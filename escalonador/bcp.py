"""
Bloco de controle de processo.
Esta ficha guarda tudo o que o escalonador precisa para interromper um processo e retoma-lo exatamente de onde parou.
"""

from dataclasses import dataclass, field
from enum import Enum

# Tamanho maximo do segmento de texto de um programa.
TAMANHO_MAXIMO_PROGRAMA = 21


class Estado(Enum):
    """
    Estados possiveis de um processo.
    Funciona como um conjunto de etiquetas fixas para sabermos a condicao atual do processo no sistema.
    """

    PRONTO = "Pronto"
    EXECUTANDO = "Executando"
    BLOQUEADO = "Bloqueado"


@dataclass
class BCP:
    """
    Ficha do bloco de controle de processo.
    """

    # Nome do programa que vem da primeira linha do arquivo lido.
    nome: str
    
    # Prioridade lida do ficheiro de texto, onde um valor maior significa mais importancia.
    prioridade: int
    
    # Referencia a regiao de memoria com o codigo do programa.
    # Eh apenas uma lista contendo os textos de cada comando que o processo vai executar.
    segmento_texto: list[str] = field(repr=False)
    
    # Contador de programa. 
    # Ele funciona como um dedo apontando para o indice da proxima instrucao que o processador deve ler.
    pc: int = 0
    
    # Estado atual do processo, que por padrao sempre comeca como pronto ao ser carregado.
    estado: Estado = Estado.PRONTO
    
    # Creditos restantes que o processo tem para gastar. 
    # Inicia vazio pois o valor sera calculado logo apos a criacao da ficha.
    creditos: int | None = None
    
    # Registradores de uso geral que servem como espaco de rascunho para numeros inteiros.
    x: int = 0
    y: int = 0

    def __post_init__(self) -> None:
        # Esta funcao roda automaticamente logo apos a ficha do processo ser instanciada na memoria.
        # Ela serve para validar se os dados que o programa recebeu estao dentro das regras.
        
        # Verifica se a quantidade de linhas de comando ultrapassa o limite permitido pela maquina ficticia.
        if len(self.segmento_texto) > TAMANHO_MAXIMO_PROGRAMA:
            # Lanca um erro interrompendo tudo se o programa for grande demais.
            raise ValueError(
                f"Programa '{self.nome}' tem {len(self.segmento_texto)} comandos; "
                f"o maximo eh {TAMANHO_MAXIMO_PROGRAMA}"
            )
            
        # Confere se a prioridade informada tem um valor negativo.
        if self.prioridade < 0:
            # Lanca um erro pois a regra estabelece que a prioridade nao pode ser menor que zero.
            raise ValueError(f"Prioridade de '{self.nome}' nao pode ser negativa")
            
        # Se os creditos ainda nao foram definidos, configuramos o valor inicial.
        if self.creditos is None:
            # A carga inicial de creditos eh sempre exatamente igual a prioridade do processo.
            self.creditos = self.prioridade

    @property
    def instrucao_atual(self) -> str:
        """
        Devolve a instrucao exata que esta sendo apontada pelo contador de programa no momento.
        """
        # Acessa a lista de comandos do processo usando o valor do contador como indice de busca.
        return self.segmento_texto[self.pc]