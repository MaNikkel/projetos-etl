# ETL Meteorológico — Comparação Java vs Haskell

Projeto de dissertação de mestrado que compara implementações orientada a objetos (Java) e funcional (Haskell) do mesmo pipeline ETL para dados meteorológicos.

## Pré-requisitos

- Docker e Docker Compose
- Java 21 + Maven
- GHC + Stack (Haskell)
- Python 3.12+

## Configuração

Todas as configurações são gerenciadas por variáveis de ambiente. Copie o arquivo de exemplo e ajuste conforme necessário:

```bash
cp .env.example .env
```

| Variável | Padrão | Descrição |
|---|---|---|
| `DB_HOST` | `localhost` | Host do PostgreSQL |
| `DB_PORT` | `5432` | Porta do PostgreSQL |
| `DB_NAME` | `meteorological` | Nome do banco de dados |
| `DB_USER` | `meteo` | Usuário do banco de dados |
| `DB_PASSWORD` | `meteo123` | Senha do banco de dados |
| `CSV_PATH` | `test.csv` | Caminho do CSV de origem (relativo à raiz do projeto) |

O arquivo `.env` é carregado automaticamente pelo Makefile e pelo docker-compose. Cada implementação ETL também lê essas variáveis em tempo de execução (com fallback para os padrões acima).

## Início Rápido

```bash
# 1. Configurar (ou usar os padrões)
cp .env.example .env

# 2. Iniciar o PostgreSQL
make up

# 3. Configurar o ambiente de testes em Python
make venv

# 4. Rodar ambos os ETLs e os testes
make all
```

## Comandos Individuais

```bash
make up          # Inicia o container PostgreSQL
make wait-pg     # Aguarda o PostgreSQL ficar pronto
make java        # Compila e executa o ETL em Java
make haskell     # Compila e executa o ETL em Haskell
make test        # Executa a suíte de verificação com pytest
make down        # Para e remove containers + volumes
make clean       # Limpeza completa (containers, artefatos de build, venv)
```
## Estratégia de Testes

Os testes usam **pytest** com **psycopg3** para consultar o banco após cada execução ETL:

- **Contagem de linhas**: exatamente 15 linhas carregadas
- **Esquema**: todas as 33 colunas presentes com tipos corretos
- **Equivalência de valores**: cada valor corresponde ao dado esperado calculado em Python (`pytest.approx` para floats)
- **Tratamento de nulos**: campos vazios do CSV são persistidos como `NULL` em SQL
- **Equivalência entre implementações**: saídas de Java e Haskell são idênticas linha a linha


Contectar

ssh -i ~/.ssh/etl-aws ssm-user@3.83.11.14  - Java
ssh -i ~/.ssh/etl-aws ssm-user@3.93.40.45 - Haskell


export JAVA_HOME=/usr/lib/jvm/java-21-amazon-corretto && export PATH="$JAVA_HOME/bin:$PATH" && hash -r

COPIAR ARQUIVOS

JAVA: scp -i ~/.ssh/etl-aws /Users/mathiasnikkel/Documents/UTFPR/dissertacao/projetos-etl/file.csv ssm-user@3.83.11.14:/home/ssm-user/projetos-etl/java-etl/test.csv

HASKELL: scp -i ~/.ssh/etl-aws /Users/mathiasnikkel/Documents/UTFPR/dissertacao/projetos-etl/file.csv  ssm-user@3.93.40.45:/home/ssm-user/projetos-etl/haskell-etl/test.csv

# Gerar CSV e carregar

./generate-and-upload-csv.sh <num>

# Coletar métricas

Ajustar os horários em UTC em get-metrics.sh e rodar:

./get-metrics.sh | ./format-cloudwatch-metrics.py 

# Coletar energia gasta

A coleta de energia neste projeto é uma estimativa baseada nas métricas do CloudWatch durante a janela de execução do ETL. Como as instâncias EC2 não expõem medição direta de joules por processo, o script calcula a potência média estimada a partir do uso de CPU e integra esse valor ao longo do intervalo informado.

Por padrão, o script usa:

- `region`: `us-east-1`
- `namespace`: `mestrado-etl`
- instância Java: `i-07d9247870bc7b12e`
- instância Haskell: `i-0c54cef44d7ac9941`
- `period`: `60` segundos
- potência ociosa estimada: `8 W`
- potência máxima estimada: `20 W`

Exemplo de uso:

```bash
./estimate-etl-energy.py \
  --region us-east-1 \
  --start-time "2026-04-23T14:12:00Z" \
  --end-time "2026-04-23T14:16:00Z"
```

O resultado inclui, para Java e Haskell:

- pico de memória
- pico da média de memória
- pico da média de CPU
- pico da média de `NetworkIn`
- pico da média de `NetworkOut`
- potência média estimada em watts
- energia estimada em joules

Para ajustar o modelo de potência:

```bash
./estimate-etl-energy.py \
  --region us-east-1 \
  --start-time "2026-04-23T14:12:00Z" \
  --end-time "2026-04-23T14:16:00Z" \
  --idle-watts 7 \
  --max-watts 18
```
