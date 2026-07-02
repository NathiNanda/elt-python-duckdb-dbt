with source_usd as (
    select 
        'USD' as codigo_moeda,
        * 
    from {{ source('raw_api_data', 'usd_brl') }}
),

source_eur as (
    select 
        'EUR' as codigo_moeda,
        * 
    from {{ source('raw_api_data', 'eur_brl') }}
),

source_btc as (
    select 
        'BTC' as codigo_moeda,
        * 
    from {{ source('raw_api_data', 'btc_brl') }}
),

union_sources as (
    select * from source_usd
    union all
    select * from source_eur
    union all
    select * from source_btc
)

select
    -- 1. Chave primária (surrogate key composta)
    md5(concat_ws('-', codigo_moeda, cast(timestamp as varchar))) as id_cotacao,
    
    -- 2. Atributos da cotação
    codigo_moeda,
    cast(high as double) as valor_maximo,
    cast(low as double) as valor_minimo,
    cast(varBid as double) as variacao_bid,
    cast(pctChange as double) as porcentagem_variacao,
    cast(bid as double) as valor_compra,
    cast(ask as double) as valor_venda,
    
    -- 3. Datas e Timestamps
    epoch_ms(cast(timestamp as bigint) * 1000) as data_criacao

from union_sources