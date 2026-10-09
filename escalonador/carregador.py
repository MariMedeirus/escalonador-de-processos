"""
Leitura dos arquivos de entrada.
Este modulo cuida de carregar os programas, as prioridades e o quantum para a memoria do escalonador.
Todos os arquivos ficam no diretorio de programas.
Cada programa esta em um arquivo com nome em numeros, como 01.txt ou 02.txt.
A primeira linha eh o nome do programa e as seguintes sao as instrucoes, terminando sempre com a palavra saida.
"""

import re
from pathlib import Path

from .bcp import BCP

ARQUIVO_PRIORIDADES = "prioridades.txt"
ARQUIVO_QUANTUM = "quantum.txt"

# Define a regra para encontrar os nomes dos arquivos de programa.
# Exige que o nome tenha exatamente dois digitos seguidos da extensao txt.
PADRAO_NOME_PROGRAMA = re.compile(r"^\d{2}\.txt$")

# Define as regras das instrucoes que a nossa maquina ficticia aceita ler.
# O padrao de atribuicao verifica se a linha comeca com X ou Y, seguido de igual e um numero que pode ser negativo.
PADRAO_ATRIBUICAO = re.compile(r"^[XY]=-?\d+$")

# Guarda em um conjunto fechado as instrucoes simples que nao precisam de variaveis.
INSTRUCOES_SIMPLES = {"COM", "E/S", "SAIDA"}


def _ler_linhas(caminho: Path) -> list[str]:
    """
    Le um arquivo de texto e devolve as suas linhas limpas e sem espacos vazios nas bordas.
    """
    # Tenta ler o arquivo usando a codificacao padrao para nao termos problemas com os caracteres.
    try:
        conteudo = caminho.read_text(encoding="utf-8-sig")
    # Se der um erro de formato de texto, tenta ler usando um padrao alternativo.
    except UnicodeDecodeError:
        conteudo = caminho.read_text(encoding="latin-1")
        
    # Limpa as pontas de cada linha de texto e ignora as linhas que estiverem totalmente em branco.
    return [linha.strip() for linha in conteudo.splitlines() if linha.strip()]


def _ler_inteiros(caminho: Path) -> list[int]:
    # Usa a funcao que acabamos de criar para ler as linhas de texto do arquivo.
    linhas = _ler_linhas(caminho)
    
    # Tenta converter cada linha de texto limpa em um numero inteiro.
    try:
        return [int(linha) for linha in linhas]
    # Se alguma linha tiver letras misturadas com numeros, o programa interrompe avisando onde esta o erro.
    except ValueError as erro:
        raise ValueError(f"Valor nao inteiro em {caminho}: {erro}") from None


def instrucao_valida(instrucao: str) -> bool:
    """
    Verifica se a instrucao pertence ao grupo que o nosso processador ficticio sabe executar.
    """
    # Devolve verdadeiro se a instrucao for uma daquelas palavras simples ou se encaixar na regra do X e do Y.
    return instrucao in INSTRUCOES_SIMPLES or bool(PADRAO_ATRIBUICAO.match(instrucao))


def ler_quantum(diretorio: Path) -> int:
    """
    Le o numero que define o tamanho do quantum dentro do seu arquivo correspondente.
    """
    # Tenta extrair todos os numeros encontrados dentro do arquivo do quantum.
    valores = _ler_inteiros(diretorio / ARQUIVO_QUANTUM)
    
    # O arquivo deve ter obrigatoriamente um unico numero la dentro, caso contrario avisa do erro.
    if len(valores) != 1:
        raise ValueError(f"{ARQUIVO_QUANTUM} deve conter exatamente um inteiro")
        
    # O valor do quantum tem que ser sempre positivo, ele nao pode ser zero nem negativo.
    if valores[0] <= 0:
        raise ValueError("O quantum deve ser um inteiro positivo")
        
    # Entrega ao escalonador o primeiro e unico numero retirado do arquivo.
    return valores[0]


def ler_prioridades(diretorio: Path) -> list[int]:
    """
    Le o arquivo de prioridades e devolve uma lista de numeros baseada na ordem do arquivo original.
    """
    # Apenas chama a funcao de ler inteiros informando o caminho exato do arquivo de prioridades.
    return _ler_inteiros(diretorio / ARQUIVO_PRIORIDADES)


def ler_programa(caminho: Path) -> tuple[str, list[str]]:
    """
    Le um arquivo de programa e separa o nome dele das instrucoes que ele vai processar.
    """
    # Le todas as linhas de texto do arquivo e limpa os espacos marginais.
    linhas = _ler_linhas(caminho)
    
    # Um programa precisa ter pelo menos um nome e uma instrucao para ser considerado valido.
    if len(linhas) < 2:
        raise ValueError(f"{caminho.name}: programa precisa de nome e ao menos uma instrucao")

    # Corta a primeira linha e guarda como nome, o resto vai para a lista de instrucoes.
    nome, instrucoes = linhas[0], linhas[1:]
    
    # Varre cada instrucao da lista para ver se tem alguma palavra estranha nao aceita pelo processador.
    for numero, instrucao in enumerate(instrucoes, start=1):
        if not instrucao_valida(instrucao):
            raise ValueError(f"{caminho.name}: instrucao invalida na posicao {numero}: '{instrucao}'")
            
    # A ultima instrucao carregada daquele arquivo tem obrigatoriamente de ser a palavra saida.
    if instrucoes[-1] != "SAIDA":
        raise ValueError(f"{caminho.name}: programa deve terminar com SAIDA")
        
    # Devolve tudo empacotado, o nome do processo e a sua lista de comandos ja devidamente verificados.
    return nome, instrucoes


def listar_arquivos_programas(diretorio: Path) -> list[Path]:
    """
    Procura todos os arquivos de programas contidos na pasta e os organiza por ordem alfabetica.
    """
    # Procura na pasta os arquivos cujo nome encaixe na nossa regra numerica e devolve ordenado.
    return sorted(p for p in diretorio.iterdir() if PADRAO_NOME_PROGRAMA.match(p.name))


def carregar_processos(diretorio: Path) -> list[BCP]:
    """
    Pega todos os arquivos da pasta de programas e transforma cada um em um bloco de controle de processo vivo.
    """
    diretorio = Path(diretorio)
    
    # Recolhe a lista limpa e ordenada de todos os arquivos de programas presentes.
    arquivos = listar_arquivos_programas(diretorio)
    
    # Se a pasta estiver completamente vazia, o sistema nao vai ter o que gerenciar e tem que dar erro.
    if not arquivos:
        raise FileNotFoundError(f"Nenhum programa encontrado em {diretorio}")

    # Le a lista completa das prioridades a partir do seu arquivo especifico.
    prioridades = ler_prioridades(diretorio)
    
    # Confere se a quantidade de prioridades bate de forma exata com a quantidade de programas encontrados.
    if len(prioridades) != len(arquivos):
        raise ValueError(
            f"{ARQUIVO_PRIORIDADES} tem {len(prioridades)} linhas, "
            f"mas ha {len(arquivos)} programas"
        )

    # Cria a lista vazia onde colocaremos os processos definitivos para enviar ao escalonador.
    processos = []
    
    # Junta os nomes dos arquivos e as prioridades formando pares, e avanca um par de cada vez.
    for arquivo, prioridade in zip(arquivos, prioridades):
        # Le o nome e o segmento de texto lendo o conteudo de dentro do arquivo do programa.
        nome, segmento_texto = ler_programa(arquivo)
        
        # Junta todas as informacoes, instancia a ficha do processo e insere na lista final.
        processos.append(BCP(nome=nome, prioridade=prioridade, segmento_texto=segmento_texto))
        
    # Devolve a caixa cheia de processos criados e prontos para entrarem nas filas de estado.
    return processos