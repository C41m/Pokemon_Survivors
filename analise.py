import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import json


def etl(df):
    df['info'] = df['info'].apply(json.loads)
    # Normalizar 'info'
    info_df = pd.json_normalize(df['info'].tolist())

    # Adicionar 'name' em info
    info_df['name'] = df['name']
    info_df['time'] = pd.to_numeric(df['time'])

    # Filtrar registros com pokemon diferente de -1
    stats_df = pd.json_normalize(df['info'].tolist(), 'statistics')
    stats_df['pokemon'] = stats_df['pokemon'].astype(int)

    # Adicionar 'name' em stats
    stats_df['name'] = df['name'].repeat(info_df['statistics'].apply(len).tolist()).reset_index(drop=True)
    
    stats_dfo = stats_df

    stats_df = stats_df.query('pokemon != -1')
    
    return stats_df, info_df, stats_dfo

def qnt_partidas_func(df):
    fig = df.shape[0]
    return fig

def support_id_nome(id):
    support_names = {
        0: "Arcanine",
        1: "Azumarill",
        2: "Flareon",
        3: "Kingler",
        4: "Leafeon",
        5: "Glalie",
        6: "Beedrill",
        7: "Vaporeon",
        8: "Electabuzz",
        9: "Ampharos",
        10: "Muk",
        11: "Jolteon",
        12: "Rhydon",
        13: "MrMime",
        14: "Swampert",
        15: "Glaceon",
        16: "Alakazam",
        17: "Pidgeot",
        18: "Meganium",
        19: "Umbreon",
        20: "Victribell",
        21: "Espeon",
        22: "Magneton"
    }
    return support_names.get(int(id), "Unknown Support")

def hero_nome_id(id):
    hero_names = {
        0: "Bulbasaur",
        1: "Charmander",
        2: "Squirtle",
        3: "Pikachu"
    }
    return hero_names.get(int(id), "Unknown Hero")

def top5_sup_jogadores_func(stats_df, info_df):

    top5_suportes_jogadores = info_df

    stats_df = stats_df.query('pokemon != -1')

    top5_suportes_jogadores = (
        stats_df.groupby(['name', 'pokemon'])
        .size()
        .reset_index(name='count')
        .sort_values(by=['name', 'count'], ascending=[True, False])
        .groupby('name')
        .head(5)
        .groupby('name')['pokemon']
        .agg(lambda x: ','.join(map(str, x)))
        .reset_index(name='Top 5 Suportes')
        
    )

    # Adicionar nomes de Pokémon usando a função support_id_nome
    top5_suportes_jogadores['Top 5 Suportes'] = top5_suportes_jogadores['Top 5 Suportes'].apply(lambda x: ', '.join(map(support_id_nome, x.split(','))))

    # Remover a coluna de índice desnecessária
    top5_suportes_jogadores = top5_suportes_jogadores.reset_index(drop=True)


    # Exibir o DataFrame resultante
    fig = top5_suportes_jogadores[['name', 'Top 5 Suportes']]
    
    return fig

def sup_mais_usados_func(stats_df):

    # Contar a ocorrência de cada Pokémon
    suportes_mais_usados = stats_df['pokemon'].value_counts().reset_index(name='count')

    # Adicionar nomes de Pokémon usando a função support_id_nome
    suportes_mais_usados['pokemon'] = suportes_mais_usados['pokemon'].apply(support_id_nome)

    # Criar o gráfico de barras com o Plotly
    fig = px.bar(suportes_mais_usados, x='pokemon', y='count')
    fig.update_layout(xaxis=dict(tickangle=45))  # Ajustar a rotação dos rótulos para melhor legibilidade

    return fig

def herois_mais_usados_func(info_df):
    # Criar um DataFrame com os dados
    contagem_heroi = info_df

    contagem_heroi['hero_nome'] = contagem_heroi['character'].apply(hero_nome_id)

    # Criar uma tabela com a contagem de cada personagem usando groupby
    contagem_heroi = info_df.groupby(['hero_nome']).size().reset_index(name='quantidade')

    fig_table = contagem_heroi
    # Criar um gráfico de pizza com Plotly Express
    fig = px.pie(contagem_heroi, values='quantidade', names='hero_nome')

    return fig, fig_table

def vitorias_geral_func(info_df):
    # Criar uma tabela com a contagem de cada jogador
    vitorias_jogadores = info_df.groupby('name').size().reset_index(name='vitorias'). sort_values(by='vitorias', ascending=False)
    # Converter a coluna 'time' para numérica
    info_df['time'] = pd.to_numeric(info_df['time'], errors='coerce')

    # Calcular a média de tempo para cada jogador em minutos
    media_tempo = info_df.groupby('name')['time'].mean().reset_index(name='media_tempo')
    media_tempo['media_tempo'] /= 60  # Convertendo para minutos
    media_tempo['media_tempo'] = pd.to_datetime(media_tempo['media_tempo'], unit='m').dt.strftime('%M:%S.%f')

    # Exibir a tabela
    resultado_final = pd.merge(vitorias_jogadores, media_tempo, on='name')
    fig = resultado_final
    return fig


def dps_geral_func(info_df, stats_dfo, df):
    dps_geral = stats_dfo.copy()

    dps_geral['nome'] = dps_geral['pokemon'].apply(support_id_nome)

    # Adicionar colunas 'name' e 'time' de volta
    dps_geral['time'] = df['time'].repeat(info_df['statistics'].apply(len).tolist()).reset_index(drop=True)

    # Converter colunas para float
    dps_geral['startTime'] = dps_geral['startTime'].str.replace(',', '.').astype(float)
    dps_geral['time'] = dps_geral['time'].str.replace(',', '.').astype(float)
    dps_geral['damage'] = dps_geral['damage'].str.replace(',', '.').astype(int)

    # Calcular DPS
    dps_geral['dps'] = dps_geral['damage'] / (dps_geral['time'] - dps_geral['startTime'])

    # Calcular média do DPS para cada pokemon
    dps_media = dps_geral.groupby(['nome', 'pokemon'])['dps'].mean().reset_index()
    return dps_media, dps_geral

def dps_heroisup_geral_func(info_df, stats_dfo, df):
    dps_media, dps_geral = dps_geral_func(info_df, stats_dfo, df)

    stats_df = dps_geral.copy()

    dps_media_heroi = stats_df.query('pokemon == -1').reset_index(drop=True)

    # Adicionar coluna 'hero' com os IDs dos heróis repetidos
    dps_media_heroi['hero'] = info_df['character'].repeat(info_df['statistics'].apply(len).tolist()).reset_index(drop=True)

    # Adicionar coluna 'hero_nome' com os nomes correspondentes aos heróis
    dps_media_heroi['hero_nome'] = info_df['character'].apply(hero_nome_id)

    # Calcular a média do DPS para cada herói
    dps_media_heroi = dps_media_heroi.groupby('hero_nome')['dps'].mean().reset_index()

    # Renomear a coluna do índice para 'hero_nome'
    dps_media_heroi = dps_media_heroi.rename(columns={'hero_nome': 'hero_nome'})

    # Exibir o DataFrame resultante
    fig_heroi = dps_media_heroi

    dps_media_suporte = dps_media.query('pokemon != -1')
    fig_sup = dps_media_suporte
    return fig_heroi, fig_sup

# def herois_mais_usados_func(df):
#     # Criar um DataFrame com os dados
#     df_info_normalized = pd.json_normalize(df['info'].tolist())
#     df_info_normalized['name'] = df['name']
#     df_info_normalized['hero_nome'] = df_info_normalized['character'].apply(hero_nome_id)

#     # Criar uma tabela com a contagem de cada personagem usando groupby
#     tabela_contagem_personagens = df_info_normalized.groupby(['character', 'hero_nome']).size().reset_index(name='quantidade')
    
#     # Mapear as cores para cada herói
#     cores_herois = {
#         'Bulbasaur': '83ba36',
#         'Charmander': '#e53800',
#         'Pikachu': '#f4dc26',
#         'Squirtle': '#93c8d0'
#     }

#     # Criar o gráfico de pizza com cores personalizadas
#     fig = go.Figure()

#     fig.add_trace(go.Pie(
#         labels=tabela_contagem_personagens['hero_nome'],
#         values=tabela_contagem_personagens['quantidade'],
#         marker=dict(colors=[cores_herois[heroi] for heroi in tabela_contagem_personagens['hero_nome']]),
#         textinfo='percent+label',  # Exibir percentagem e rótulo
#         textposition='inside',  # Colocar o texto dentro da fatia
#     ))

#     return fig

# def dps_media_func(df):
#     # Normalizar 'info'
#     info_df = pd.json_normalize(df['info'].tolist())

#     # Abrir statistics
#     stats_df = pd.DataFrame(info_df['statistics'].explode().tolist())

#     # Adicionar colunas 'name' e 'time' de volta
#     stats_df['name'] = df['name'].repeat(info_df['statistics'].apply(len).tolist()).reset_index(drop=True)
#     stats_df['time'] = df['time'].repeat(info_df['statistics'].apply(len).tolist()).reset_index(drop=True)

#     # Converter colunas para float
#     stats_df['startTime'] = stats_df['startTime'].str.replace(',', '.').astype(float)
#     stats_df['time'] = stats_df['time'].str.replace(',', '.').astype(float)
#     stats_df['damage'] = stats_df['damage'].str.replace(',', '.').astype(int)

#     # Calcular DPS
#     stats_df['dps'] = stats_df['damage'] / (stats_df['time'] - stats_df['startTime'])

#     # Calcular média do DPS para cada pokemon
#     average_dps = stats_df.groupby('pokemon')['dps'].mean().reset_index()

#     return average_dps