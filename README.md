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
