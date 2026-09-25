"""Testes da Fase 1: BCP, leitura de arquivos e inicialização das estruturas."""

import tempfile
import unittest
from pathlib import Path

from escalonador import BCP, Estado, carregar_processos, inicializar, ler_prioridades, ler_quantum
from escalonador.bcp import TAMANHO_MAXIMO_PROGRAMA
from escalonador.carregador import ler_programa
from escalonador.estruturas import FilaProntos

PROGRAMAS_EXEMPLO = Path(__file__).resolve().parent.parent / "programas"


def escrever(diretorio: Path, nome: str, linhas: list[str]) -> Path:
    caminho = diretorio / nome
    caminho.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return caminho


class TestBCP(unittest.TestCase):
    def test_valores_iniciais(self):
        bcp = BCP(nome="TESTE-1", prioridade=3, segmento_texto=["COM", "SAIDA"])
        self.assertEqual(bcp.pc, 0)
        self.assertEqual(bcp.estado, Estado.PRONTO)
        self.assertEqual(bcp.creditos, 3)
        self.assertEqual((bcp.x, bcp.y), (0, 0))
        self.assertEqual(bcp.instrucao_atual, "COM")

    def test_programa_grande_demais(self):
        codigo = ["COM"] * TAMANHO_MAXIMO_PROGRAMA + ["SAIDA"]
        with self.assertRaises(ValueError):
            BCP(nome="GRANDE", prioridade=1, segmento_texto=codigo)


class TestCarregador(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_ler_quantum(self):
        escrever(self.dir, "quantum.txt", ["4"])
        self.assertEqual(ler_quantum(self.dir), 4)

    def test_quantum_invalido(self):
        escrever(self.dir, "quantum.txt", ["0"])
        with self.assertRaises(ValueError):
            ler_quantum(self.dir)

    def test_ler_prioridades(self):
        escrever(self.dir, "prioridades.txt", ["1", "3", "4"])
        self.assertEqual(ler_prioridades(self.dir), [1, 3, 4])

    def test_ler_programa(self):
        caminho = escrever(self.dir, "01.txt", ["TESTE-1", "X=8", "COM", "E/S", "Y=-10", "SAIDA"])
        nome, codigo = ler_programa(caminho)
        self.assertEqual(nome, "TESTE-1")
        self.assertEqual(codigo, ["X=8", "COM", "E/S", "Y=-10", "SAIDA"])

    def test_instrucao_invalida(self):
        caminho = escrever(self.dir, "01.txt", ["TESTE-1", "X = 8", "SAIDA"])
        with self.assertRaises(ValueError):
            ler_programa(caminho)

    def test_programa_sem_saida(self):
        caminho = escrever(self.dir, "01.txt", ["TESTE-1", "COM"])
        with self.assertRaises(ValueError):
            ler_programa(caminho)

    def test_carregar_processos_em_ordem_alfabetica(self):
        escrever(self.dir, "02.txt", ["B", "SAIDA"])
        escrever(self.dir, "01.txt", ["A", "SAIDA"])
        escrever(self.dir, "10.txt", ["C", "SAIDA"])
        escrever(self.dir, "prioridades.txt", ["1", "5", "3"])
        escrever(self.dir, "quantum.txt", ["2"])
        processos = carregar_processos(self.dir)
        self.assertEqual([p.nome for p in processos], ["A", "B", "C"])
        self.assertEqual([p.prioridade for p in processos], [1, 5, 3])
        self.assertEqual([p.creditos for p in processos], [1, 5, 3])

    def test_prioridades_incompativeis(self):
        escrever(self.dir, "01.txt", ["A", "SAIDA"])
        escrever(self.dir, "prioridades.txt", ["1", "2"])
        with self.assertRaises(ValueError):
            carregar_processos(self.dir)

    def test_diretorio_exemplo(self):
        processos = carregar_processos(PROGRAMAS_EXEMPLO)
        self.assertEqual(len(processos), 10)
        self.assertEqual(ler_quantum(PROGRAMAS_EXEMPLO), 3)
        self.assertEqual(sum(p.creditos for p in processos), 58)


class TestEstruturas(unittest.TestCase):
    def test_fila_ordenada_por_creditos_com_empate_por_chegada(self):
        a = BCP(nome="A", prioridade=1, segmento_texto=["SAIDA"])
        b = BCP(nome="B", prioridade=5, segmento_texto=["SAIDA"])
        c = BCP(nome="C", prioridade=3, segmento_texto=["SAIDA"])
        d = BCP(nome="D", prioridade=5, segmento_texto=["SAIDA"])
        fila = FilaProntos()
        for bcp in (a, b, c, d):
            fila.inserir(bcp)
        self.assertEqual([p.nome for p in fila], ["B", "D", "C", "A"])
        self.assertIs(fila.remover_primeiro(), b)
        self.assertEqual(len(fila), 3)

    def test_inicializar(self):
        processos = carregar_processos(PROGRAMAS_EXEMPLO)
        tabela, prontos = inicializar(processos)
        self.assertEqual(len(tabela), 10)
        self.assertEqual(len(prontos), 10)
        self.assertTrue(all(p.estado == Estado.PRONTO for p in prontos))
        creditos = [p.creditos for p in prontos]
        self.assertEqual(creditos, sorted(creditos, reverse=True))
        self.assertEqual(
            [p.nome for p in prontos],
            ["TESTE-7", "TESTE-4", "TESTE-8", "TESTE-9", "TESTE-6",
             "TESTE-5", "TESTE-10", "TESTE-2", "TESTE-3", "TESTE-1"],
        )


if __name__ == "__main__":
    unittest.main()
