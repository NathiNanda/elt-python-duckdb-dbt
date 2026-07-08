# Pipeline de Dados Local: Ingestão e Modelagem de Cotações de Moedas

Este projeto implementa um pipeline de dados local completo no paradigma **ELT** (*Extract, Load, Transform*). O objetivo é consumir dados históricos de cotação de moedas de uma API pública, armazenar os dados brutos localmente, carregá-los em um banco de dados relacional colunar de alta performance (**DuckDB**) e realizar transformações e testes de qualidade usando o **dbt-core** (*data build tool*).

Este repositório foi construído com fins de portfólio profissional de Engenharia de Dados, aplicando conceitos fundamentais como modelagem em camadas, integridade referencial, e testes automatizados.

---

## 🛠️ Tecnologias Utilizadas

*   **Python 3.12:** Utilizado para a etapa de ingestão (*requests* e *logging*).
*   **DuckDB:** Banco de dados analítico (OLAP) local de alta performance, usado como Query Engine e Data Warehouse serverless do projeto.
*   **dbt-core (v1.11):** Ferramenta líder de mercado para transformações SQL estruturadas (Analytics Engineering).
*   **dbt-duckdb (Adapter):** Integração nativa que permite ao dbt ler e materializar dados diretamente no DuckDB.
*   **uv:** Gerenciador de pacotes e ambientes virtuais Python ultra veloz da Astro.

---

## 📐 Arquitetura e Fluxo de Dados

O pipeline simula o funcionamento de uma arquitetura de dados corporativa (Bronze, Silver, Gold):

<img width="1980" height="920" alt="image" src="https://github.com/user-attachments/assets/5d4ef13b-e9e8-4717-b790-aa65fbbf10b1" />

**Ingestão (Extract & Load):** O script Python consome o histórico de 30 dias das moedas **USD-BRL**, **EUR-BRL** e **BTC-BRL** da **AwesomeAPI**. Os dados brutos são salvos exatamente como retornados (JSON) na pasta `data/raw/` (simulando um Data Lake / Landing Zone / Bronze).

**Transformação (Transform):**
    *   **Camada Staging (Silver):** Lê os arquivos JSON de forma direta usando as capacidades colunares do DuckDB (`read_json_auto`). Limpa, padroniza as colunas e converte strings em tipos numéricos e temporais corretos.
    *   **Camada Marts (Gold):** Calcula a média semanal das cotações agrupando por moeda e início da semana (segunda-feira).
    
**Qualidade de Dados (Data Quality):** Testes automatizados do dbt garantem que a surrogate key gerada seja única e que campos críticos (como taxas de compra e datas) nunca sejam nulos.

---

## 📁 Estrutura do Projeto

```text
elt-python-duckdb-dbt/
├── .gitignore                     # Arquivos locais de dados e banco de dados são mantidos fora do git
├── pyproject.toml                 # Configuração de dependências via uv
├── uv.lock                        # Lockfile de dependências do Python
├── README.md                      # Documentação principal
├── ingest.py                      # Script Python para extração dos dados da API
├── query_db.py                    # Script Python auxiliar para consultas diretas via SQL no DuckDB
│
├── dbt_api_dbt_duckdb/            # Diretório principal do dbt
    ├── dbt_project.yml            # Arquivo de configuração de projeto dbt
    ├── profiles.yml               # Conector do dbt para o DuckDB local
    └── models/
        ├── staging/               # Camada de limpeza e tipagem básica (Silver)
        │   ├── src_raw_data.yml   # Definição dos caminhos das fontes JSON locais
        │   ├── schema_staging.yml # Definição dos testes (unique, not_null) da staging
        │   └── stg_exchange_rates.sql
        │
        └── marts/                 # Camada analítica de consumo (Gold)
            ├── schema_marts.yml   # Definição dos testes da camada de negócios
            └── mart_weekly_avg_rates.sql
```

---

## ⚡ Como Executar o Projeto

### Pré-requisitos
Você precisará do Python (3.12+) e da ferramenta de gerenciamento de dependências `uv` instalada.

1.  **Clonar o Repositório:**
    ```bash
    git clone https://github.com/NathiNanda/elt-python-duckdb-dbt.git
    cd elt-python-duckdb-dbt
    ```

2.  **Criar o Ambiente Virtual e Instalar Dependências:**
    O `uv` identificará e instalará todas as dependências declaradas no `pyproject.toml` (incluindo `dbt-duckdb` e `requests`):
    ```bash
    uv sync
    ```

3.  **Ativar o Ambiente Virtual:**
    *   No Windows (PowerShell):
        ```powershell
        .venv\Scripts\activate
        ```
    *   No Linux/macOS:
        ```bash
        source .venv/bin/activate
        ```

4.  **Executar a Ingestão de Dados (Python):**
    Este script criará o diretório `data/raw/` e fará o download das cotações históricas em formato JSON:
    ```bash
    python ingest.py
    ```

5.  **Executar e Testar os Modelos com o dbt:**
    Navegue até a pasta do dbt e execute o comando `build` para construir e testar todas as tabelas/views de uma vez:
    ```bash
    cd dbt_api_dbt_duckdb
    dbt build --profiles-dir .
    ```

6.  **Visualizar os Resultados Finais:**
    Retorne à raiz do projeto e execute o script Python que consulta o banco `dev.duckdb` gerado:
    ```bash
    cd ..
    python query_db.py
    ```

---

<img width="1913" height="863" alt="image" src="https://github.com/user-attachments/assets/b9389184-04d6-43a2-8ce6-69845fa66aa3" />

<img width="1840" height="802" alt="image" src="https://github.com/user-attachments/assets/9c2aa52f-72b0-4974-bd6d-d5ad3d2c48a9" />

## 🧠 Aprendizados Chave (Tratamento de Dados de Produção)

Durante o desenvolvimento deste projeto, deparou-se com um desafio clássico de APIs em produção: **inconsistência de esquemas históricos**.

*   **O Problema:** A AwesomeAPI retorna metadados completos (como `create_date` e o código da moeda) apenas para a cotação em tempo real (primeiro item do array JSON). Os registros de dias anteriores contêm apenas o valor da cotação e o campo de `timestamp` (Unix Epoch).
*   **O Impacto:** O uso de `create_date` para gerar chaves primárias e colunas de tempo na camada de staging causou falhas de **dados nulos** e **IDs duplicados** nos testes automatizados do dbt.
*   **A Solução:** O modelo de staging foi reestruturado para depender exclusivamente do campo `timestamp` (que está presente em 100% dos registros de histórico). O timestamp Unix foi convertido para data utilizando a função nativa do DuckDB `epoch_ms(cast(timestamp as bigint) * 1000)`. Com isso, a integridade referencial foi garantida e todos os testes passaram com sucesso.
