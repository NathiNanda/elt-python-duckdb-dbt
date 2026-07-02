import duckdb

def query_gold_data():
    # Conecta ao arquivo de banco de dados do DuckDB
    con = duckdb.connect(database="data/dev.duckdb", read_only=True)
    
    # Realiza a consulta na tabela gerada pela camada Mart do dbt
    query = """
        SELECT 
            codigo_moeda,
            inicio_semana,
            media_valor_compra,
            media_valor_venda,
            total_cotacoes_na_semana
        FROM main.mart_weekly_avg_rates
        ORDER BY codigo_moeda, inicio_semana DESC;
    """
    
    print("\n--- Visualizando Médias Semanais (Camada Mart) ---")
    resultados = con.execute(query).fetchall()
    
    # Imprime os resultados formatados
    for linha in resultados:
        moeda, inicio, compra, venda, count = linha
        print(f"Moeda: {moeda} | Semana de: {inicio.strftime('%Y-%m-%d')} | Média Compra: R$ {compra:.4f} | Média Venda: R$ {venda:.4f} | Cotações: {count}")

    con.close()

if __name__ == "__main__":
    query_gold_data()
