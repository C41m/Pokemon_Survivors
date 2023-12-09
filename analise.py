import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import json
from pandas import json_normalize  


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
    fig = top5_suportes_jogadores[['name', 'Top 5 Suportes']].rename(columns={'name': 'Jogador'})
    
    return fig

def sup_mais_usados_func(stats_df):

    # Contar a ocorrência de cada Pokémon
    suportes_mais_usados = stats_df['pokemon'].value_counts().reset_index(name='count')

    #Remover o heroi -1
    suportes_mais_usados = suportes_mais_usados.query('pokemon != -1').reset_index(drop=True)

    # Adicionar nomes de Pokémon usando a função support_id_nome
    suportes_mais_usados['pokemon'] = suportes_mais_usados['pokemon'].apply(support_id_nome)
    
    suportes_mais_usados = suportes_mais_usados.rename(columns={'pokemon': 'Nome', 'count':'Quant'})

    # Criar o gráfico de barras com o Plotly
    fig = px.bar(suportes_mais_usados, x='Nome', y='Quant')
    fig.update_layout(xaxis=dict(tickangle=45))  # Ajustar a rotação dos rótulos para melhor legibilidade
    
    fig_table = suportes_mais_usados

    return fig, fig_table

def herois_mais_usados_func(info_df):
    # Criar um DataFrame com os dados
    contagem_heroi = info_df

    contagem_heroi['hero_nome'] = contagem_heroi['character'].apply(hero_nome_id)

    # Criar uma tabela com a contagem de cada personagem usando groupby
    contagem_heroi = info_df.groupby(['hero_nome']).size().reset_index(name='quantidade')

    # Criar um gráfico de pizza com Plotly Express
    fig = px.pie(contagem_heroi, values='quantidade', names='hero_nome')
    fig_table = contagem_heroi.rename(columns={'hero_nome': 'Heroi', 'quantidade': 'Quant'})

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

    resultado_final = resultado_final.rename(columns={'name': 'Jogador', 'vitorias':'Vitorias', 'media_tempo': 'Tempo Médio (Min)'})    

    fig_table = resultado_final

    # Gráfico de barras com estrelas
    fig = px.bar(resultado_final, x='Vitorias', y='Jogador', orientation='h')


    
    return fig, fig_table


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
    fig_heroi = dps_media_heroi.rename(columns={'hero_nome': 'Nome', 'dps':'DPS'})
    
    dps_media_suporte = dps_media.query('pokemon != -1')
    fig_sup = dps_media_suporte[['nome', 'dps']].rename(columns={'nome': 'Nome', 'dps':'DPS'})
    return fig_heroi, fig_sup

def jogador_mais_tempo_func(info_df):
    #
    aux_df = info_df

    # Calcular a quantidade total de tempo jogado por 'name' em segundos
    tempo_total_jogo_nome = aux_df.groupby('name')['time'].sum().reset_index(name='tempo_total_segundos')

    # Converter os segundos para horas
    tempo_total_jogo_nome['tempo_total_horas'] = tempo_total_jogo_nome['tempo_total_segundos'] / 3600

    # Converter os segundos para formato de hora
    tempo_total_jogo_nome['tempo_total_horas'] = pd.to_datetime(tempo_total_jogo_nome['tempo_total_segundos'], unit='s').dt.strftime('%H:%M:%S')

    tempo_total_jogo_nome = tempo_total_jogo_nome[['name', 'tempo_total_horas']]

    tempo_total_jogo_nome = tempo_total_jogo_nome.rename(columns={'name': 'Jogador', 'tempo_total_horas':'Horas'})

    fig_table = tempo_total_jogo_nome.sort_values(by='Horas', ascending=False)
    #tempo_total_jogo_nome[['name', 'tempo_total_horas']]

    fig = tempo_total_jogo_nome.sort_values(by='Horas', ascending=False)
    
    # Criar um gráfico de barras interativo com o Plotly
    fig = px.bar(tempo_total_jogo_nome, x='Jogador', y='Horas', labels={'total_time_seconds': 'Tempo Total Jogado (segundos)'})

    # Personalizar layout
    fig.update_layout(
        xaxis_title='Jogador',
        yaxis_title='Tempo Total Jogado',
        xaxis=dict(tickvals=tempo_total_jogo_nome['Jogador'], ticktext=tempo_total_jogo_nome['Jogador'], autorange="reversed")
        )
    

    return fig, fig_table

def heroi_preferido_jogador_func(info_df):
    heroi_preferido_por_jogador = info_df 

    # Calcular a contagem de ocorrências de cada personagem por jogador
    heroi_preferido_por_jogador = heroi_preferido_por_jogador.groupby(['name', 'hero_nome']).size().reset_index(name='quantidade')

    # Encontrar o índice do primeiro valor máximo para cada jogador
    idx = heroi_preferido_por_jogador.groupby('name')['quantidade'].idxmax()
    heroi_preferido_por_jogador = heroi_preferido_por_jogador.loc[idx]

    # Exibir a tabela final
    fig_table = heroi_preferido_por_jogador[['name', 'hero_nome', 'quantidade']].rename(columns={'name': 'Jogador', 'hero_nome': 'Heroi', 'quantidade': 'Quant'})

    return fig_table


def hist_partidas_func(info_df):
    info_df_exp = info_df.copy()
    # Normalizar a coluna 'statistics'

    info_df_exp = json_normalize(info_df['statistics'].tolist())

    # Juntar o DataFrame normalizado de volta ao DataFrame original
    info_df_exp = pd.concat([info_df, info_df_exp], axis=1)

    # Descartar a coluna 'statistics' original se desejado
    info_df_exp = info_df_exp.drop('statistics', axis=1)

    #
    info_df_exp0 = info_df_exp[0].apply(pd.Series).rename(columns={'startTime': 'startTime0', 'pokemon': 'pokemon0', 'damage': 'damage0'})
    info_df_exp1 = info_df_exp[1].apply(pd.Series).rename(columns={'startTime': 'startTime1', 'pokemon': 'pokemon1', 'damage': 'damage1'})
    info_df_exp2 = info_df_exp[2].apply(pd.Series).rename(columns={'startTime': 'startTime2', 'pokemon': 'pokemon2', 'damage': 'damage2'})
    info_df_exp3 = info_df_exp[3].apply(pd.Series).rename(columns={'startTime': 'startTime3', 'pokemon': 'pokemon3', 'damage': 'damage3'})
    info_df_exp4 = info_df_exp[4].apply(pd.Series).rename(columns={'startTime': 'startTime4', 'pokemon': 'pokemon4', 'damage': 'damage4'})
    info_df_exp5 = info_df_exp[5].apply(pd.Series).rename(columns={'startTime': 'startTime5', 'pokemon': 'pokemon5', 'damage': 'damage5'})

    # 
    info_df_exp = pd.concat([info_df_exp, info_df_exp0, info_df_exp1, info_df_exp2, info_df_exp3, info_df_exp4, info_df_exp5], axis=1)
    
    # Colocando nnome dos suportes
    coluna_formatar = ['pokemon1', 'pokemon2', 'pokemon3', 'pokemon4', 'pokemon5']
    for coluna in coluna_formatar:
        info_df_exp[coluna] = info_df_exp[coluna].apply(support_id_nome)
    
    # Colocando nnome dos herois
    info_df_exp['pokemon0'] = info_df_exp['character'].apply(hero_nome_id)


    # Limpando dados dda tabela
    info_df_exp = info_df_exp.drop([0, 1, 2, 3, 4, 5, 'nomePc', 'character'], axis=1)
    info_df_exp['Ordem'] = [f'{ordem}°' for ordem in range(1, len(info_df_exp) + 1)]

    info_df_exp = info_df_exp[['Ordem', 'name', 'level','endTime', 'pokemon0', 'damage0', 'pokemon1', 'damage1', 'startTime1', 'pokemon2', 'damage2', 'startTime2', 'pokemon3', 'damage3', 'startTime3',  'pokemon4', 'damage4', 'startTime4', 'pokemon5', 'damage5', 'startTime5']]

    # Formatar datas
    coluna_formatar = ['startTime1', 'startTime2', 'startTime3', 'startTime4', 'startTime5']
    for coluna in coluna_formatar:
        info_df_exp[coluna] = pd.to_numeric(info_df_exp[coluna].str.replace(',', '.'))
        info_df_exp[coluna] = pd.to_datetime(info_df_exp[coluna], unit='s').dt.strftime('%M:%S:%f').str[:-3]

    # Renomear colunas
    info_df_exp = info_df_exp.rename(columns={'name': 'Jogador', 'endTime': 'Tempo', 'pokemon0': 'Heroi', 'damage0': 'Dano Heroi', 'pokemon1': 'Suporte 1', 'damage1': 'Dano Sup 1', 'startTime1': 'Tempo Sup 1', 'pokemon2': 'Suporte 2', 'damage2': 'Dano Sup 2', 'startTime2': 'Tempo Sup 2', 'pokemon3': 'Suporte 3', 'damage3': 'Dano Sup 3', 'startTime3': 'Tempo Sup 3', 'pokemon4': 'Suporte 4', 'damage4': 'Dano Sup 4', 'startTime4': 'Tempo Sup 4', 'pokemon5': 'Suporte 5', 'damage5': 'Dano Sup 5', 'startTime5': 'Tempo Sup 5'})

    fig_table_rank_geral = info_df_exp.sort_index(ascending=True)

    info_df_exp_un = info_df_exp.copy()
    
    min_indices = info_df_exp_un.groupby('Jogador')['Tempo'].idxmin()

    info_df_exp_un = info_df_exp_un.loc[min_indices].sort_values(by='Tempo', ascending=True).reset_index(drop=True)

    info_df_exp_un['Ordem'] = [f'{ordem}°' for ordem in range(1, len(info_df_exp_un) + 1)]

    fig_table_rank_unico = info_df_exp_un

    pri_rank = fig_table_rank_unico['Jogador'].iloc[0]

    seg_rank = fig_table_rank_unico['Jogador'].iloc[1]
    
    ter_rank = fig_table_rank_unico['Jogador'].iloc[2]


    return fig_table_rank_geral, fig_table_rank_unico, pri_rank, seg_rank, ter_rank