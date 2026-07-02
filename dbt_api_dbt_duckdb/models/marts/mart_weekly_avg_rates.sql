with staging_data as (
    select * from {{ ref('stg_exchange_rates') }}
),

calc_weekly as (
    select
        codigo_moeda,
        -- Extrai o ano e o número da semana da data de criação
        date_trunc('week', data_criacao) as inicio_semana,
        round(avg(valor_compra), 4) as media_valor_compra,
        round(avg(valor_venda), 4) as media_valor_venda,
        count(*) as total_cotacoes_na_semana
    from staging_data
    group by 1, 2
)

select
    -- Criação de um ID único para a semana + moeda
    md5(concat_ws('-', codigo_moeda, cast(inicio_semana as varchar))) as id_semana,
    codigo_moeda,
    inicio_semana,
    media_valor_compra,
    media_valor_venda,
    total_cotacoes_na_semana
from calc_weekly
order by codigo_moeda, inicio_semana desc
