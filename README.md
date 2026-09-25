# escalonador-de-processos

Escalonador de tarefas para Time Sharing em uma máquina fictícia (EP1), em Python 3.10+.

## Estrutura

- `Escalonador.py` — ponto de entrada (`python Escalonador.py [diretorio_programas]`)
- `escalonador/bcp.py` — classe `BCP` (PC, estado, prioridade, créditos, registradores X e Y, segmento de texto)
- `escalonador/carregador.py` — leitura de `programas/NN.txt`, `prioridades.txt` e `quantum.txt`
- `escalonador/estruturas.py` — `TabelaProcessos`, `FilaProntos` e `inicializar()`
- `programas/` — arquivos de entrada (substituir pelos fornecidos em `EP1.zip`)
- `tests/` — testes (`python -m unittest discover -s tests`)
