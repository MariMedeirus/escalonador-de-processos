"""Registro dos eventos da execução do escalonador."""

from pathlib import Path


class LogEscalonador:
    """Cria e escreve os eventos da simulacao em ``logXX.txt``."""

    def __init__(self, quantum: int, diretorio: str | Path = ".") -> None:
        """Inicia um arquivo novo, nomeado com o quantum em dois digitos."""
        self.caminho = Path(diretorio) / f"log{quantum:02d}.txt"
        self.caminho.write_text("", encoding="utf-8")

    def registrar(self, evento: str) -> None:
        """Acrescenta uma linha ao arquivo de log."""
        with self.caminho.open("a", encoding="utf-8") as arquivo:
            arquivo.write(evento + "\n")

    def troca_contexto(self, saiu: str | None, entrou: str) -> None:
        """Registra quem deixou a CPU e quem assumiu, inclusive CPU ociosa."""
        origem = saiu if saiu is not None else "CPU ociosa"
        self.registrar(f"Troca de contexto: saiu {origem}; entrou {entrou}")

    def interrupcao(self, processo: str, motivo: str) -> None:
        """Registra uma interrupcao por E/S ou fim de quantum."""
        self.registrar(f"Interrupção: processo {processo}; motivo: {motivo}")

    def termino(self, processo: str) -> None:
        """Registra o termino do processo ao executar SAIDA."""
        self.registrar(f"Término: processo {processo}; instrução: SAIDA")