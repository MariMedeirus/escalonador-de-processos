# Simulador de escalonador de processos

Este projeto implementa um simulador de escalonamento de processos em Python 3.10+, projetado para replicar o comportamento de um Sistema Operativo baseado em *Time Sharing* com gestão de prioridades por créditos.

O sistema carrega instruções a partir de arquivos de texto, simula o consumo de ciclos de CPU (baseado no *quantum* configurado), gere trocas de contexto e aplica castigos de espera para operações de E/S.

## Estrutura do projeto

O projeto foi modularizado para separar a lógica de gestão da CPU, o armazenamento e a automação de testes. *Para detalhes profundos, consulte os ficheiros README internos de cada diretório.*

* `Escalonador.py`: O motor principal do sistema. Gere o ciclo de vida dos processos e a distribuição da CPU.
* `analise_quantum.py`: Script de automação. Executa o simulador em lote variando o *quantum* e gera gráficos de desempenho (Matplotlib) para análise do *trade-off* (Custo vs. Benefício).
* **`/escalonador/`**: Núcleo lógico do Sistema Operativo.
* `bcp.py`: Definição do Bloco de Controlo de Processo e dos estados (PRONTO, EXECUTANDO, BLOQUEADO).
* `carregador.py`: Módulo de leitura, validação e carregamento dos ficheiros da máquina fictícia para a memória.
* `estruturas.py`: Implementação da `TabelaProcessos`, `FilaProntos` (ordenada por créditos) e `FilaBloqueados` (temporizador de E/S).
* `logs.py`: Gestor responsável por espelhar os eventos no terminal e formatar as métricas de saída.


* **`/programas/`**: Diretório de armazenamento (memória secundária) contendo os 10 programas de teste (`XX.txt`), o ficheiro de `prioridades.txt` e o `quantum.txt`.
* **`/programas/saidas/`**: Diretório gerado automaticamente onde são guardados os relatórios `logXX.txt` e os gráficos de desempenho (`.png`).
* **`/tests/`**: Suite de testes unitários que garantem a integridade da leitura e das filas de processamento.

## Como executar

Certifique-se de ter o Python 3.10 ou superior instalado na sua máquina. Não são necessárias bibliotecas externas para correr o motor principal.

**1. Para correr a simulação normal:**
Na raiz do repositório, abra o terminal e execute:
```bash
python Escalonador.py
```
*(O sistema irá procurar automaticamente os dados na pasta `/programas` e gerar o log na pasta `/programas/saidas/`)*.

**2. Para correr a automação e gerar os gráficos de análise:**
*(Requer a instalação prévia do Matplotlib e do Pandas)*
```bash
pip install matplotlib pandas
python analise_quantum.py
```

## Como executar os testes unitários

Para garantir que o código cumpre os requisitos estruturais, corra o explorador de testes do Python:
```bash
python -m unittest discover -s tests
```