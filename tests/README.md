# Diretório de testes e automação

Esta pasta guarda os scripts auxiliares que vão validar o nosso escalonador em massa.

## Objetivo dos scripts

A rotina de testes segue um fluxo de trabalho bem simples:
* **Execução em lote:** o script de automação chama o arquivo principal do escalonador passando diversos tamanhos de quantum (de forma distribuída e uniforme).
* **Coleta de dados:** em seguida, o código entra em ação para ler todos os arquivos de log (`logXX.txt`) que foram gerados pelo simulador.
* **Análise e visualização:** usando bibliotecas de análise de dados como Pandas e Matplotlib, o script extrai as médias de trocas de processos e de instruções executadas por quantum, plotando os gráficos de desempenho automaticamente.