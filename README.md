# Escalonador de processos

Escalonador de tarefas para time sharing em uma máquina fictícia, em Python 3.10+.

## Estrutura

- `Escalonador.py`: ponto de entrada (`python Escalonador.py [diretorio_programas]`)
- `escalonador/bcp.py`: classe `BCP` (PC, estado, prioridade, créditos, registradores X e Y, segmento de texto)
- `escalonador/carregador.py`: leitura de `programas/NN.txt`, `prioridades.txt` e `quantum.txt`
- `escalonador/estruturas.py`: `TabelaProcessos`, `FilaProntos` e `inicializar()`
- `programas/`: arquivos de entrada fornecidos (10 programas, `prioridades.txt` e `quantum.txt`)
- `tests/`: testes (`python -m unittest discover -s tests`)

## Execução e logfiles

Na pasta raiz, execute `python Escalonador.py`. O quantum é lido de `programas/quantum.txt` e o logfile correspondente é gravado na mesma pasta, com o formato `logXX.txt` (por exemplo, quantum 3 gera `programas/log03.txt`). Cada execução substitui apenas o logfile daquele quantum.

Para gerar os logfiles de quantum 2, 4, ..., 20 e exibir as médias calculadas, execute `python analise_quantum.py`. O script restaura o valor original de `programas/quantum.txt` ao terminar.
