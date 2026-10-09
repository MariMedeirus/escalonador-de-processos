# Escalonador de processos

Escalonador de tarefas para time sharing em uma máquina fictícia, em Python 3.10+.

## Estrutura

- `Escalonador.py`: ponto de entrada (`python Escalonador.py [diretorio_programas]`)
- `escalonador/bcp.py`: classe `BCP` (PC, estado, prioridade, créditos, registradores X e Y, segmento de texto)
- `escalonador/carregador.py`: leitura de `programas/NN.txt`, `prioridades.txt` e `quantum.txt`
- `escalonador/estruturas.py`: `TabelaProcessos`, `FilaProntos` e `inicializar()`
- `programas/`: arquivos de entrada fornecidos (10 programas, `prioridades.txt` e `quantum.txt`)
- `tests/`: testes (`python -m unittest discover -s tests`)
