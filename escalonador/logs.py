"""Registro dos eventos da execução do escalonador."""

from pathlib import Path


class LogEscalonador:
    def __init__(self, quantum: int, diretorio: str | Path = ".") -> None:
        self.caminho = Path(diretorio) / f"log{quantum:02d}.txt"
        self.caminho.write_text("", encoding="utf-8")

    def registrar(self, evento: str) -> None:
        with self.caminho.open("a", encoding="utf-8") as arquivo:
            arquivo.write(evento + "\n")

    def troca_contexto(self, saiu: str | None, entrou: str) -> None:
        origem = saiu if saiu is not None else "CPU ociosa"
        self.registrar(f"Troca de contexto: saiu {origem}; entrou {entrou}")

    def interrupcao(self, processo: str, motivo: str) -> None:
        self.registrar(f"Interrupção: processo {processo}; motivo: {motivo}")

    def termino(self, processo: str) -> None:
        self.registrar(f"Término: processo {processo}; instrução: SAIDA")