"""
Escalonador de processos para time sharing em uma maquina ficticia.
Este arquivo transforma a pasta escalonador em um modulo python.
Ele tambem define quais ferramentas ficam visiveis para quem importar esta pasta no arquivo principal.
"""

# Puxa a ficha do processo e os estados possiveis.
from .bcp import BCP, Estado

# Importa as funcoes de leitura do nosso arquivo carregador.
from .carregador import carregar_processos, ler_prioridades, ler_quantum

# Traz as estruturas de dados principais que gerenciam a tabela e a fila de prontos.
from .estruturas import FilaProntos, TabelaProcessos, inicializar

# A lista abaixo define o que sera exportado quando alguem importar a pasta inteira.
# Funciona como uma vitrine mostrando apenas as pecas que os outros arquivos podem usar.
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