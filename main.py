import streamlit as st
import requests
import pandas as pd
from analise import etl, qnt_partidas_func, top5_sup_jogadores_func, sup_mais_usados_func, herois_mais_usados_func, vitorias_geral_func, dps_heroisup_geral_func, jogador_mais_tempo_func, heroi_preferido_jogador_func, hist_partidas_func
from time import time

url = "https://rootd4.vercel.app/score/all"
response = requests.get(url)
dados = response.json()
# Transformar a resposta JSON em DataFrame
df = pd.DataFrame(response.json()).copy()
stats_df, info_df, stats_dfo = etl(df)

st.set_page_config(page_title='Pokemon Survivors', page_icon='logo.png')

with open("styles.css") as f:
    css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

with st.container():
    col1, col2, col3 = st.columns(3)
    with col2:
        st.image('logo.png', width=150, use_column_width=True)

# Configurar a tabs no Streamlit
tab1, tab2, tab3 = st.tabs(['Dados', 'Jogadores', 'Suporte'])


with tab1:
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            rank_geral, rank_unico, pri_rank, seg_rank, ter_rank = hist_partidas_func(info_df) 
            st.markdown(f"<h1 style='text-align: center; color: white;'>{pri_rank}</h1>", unsafe_allow_html=True)
            st.markdown("<h1 style='text-align: center; color: white;'>🥇</h1>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<h1 style='text-align: center; color: white;'>{seg_rank}</h1>", unsafe_allow_html=True)
            st.markdown("<h1 style='text-align: center; color: white;'>🥈</h1>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<h1 style='text-align: center; color: white;'>{ter_rank}</h1>", unsafe_allow_html=True)
            st.markdown("<h1 style='text-align: center; color: white;'>🥉</h1>", unsafe_allow_html=True)

        st.write('---')
        st.markdown('# Ranking Geral')
        st.dataframe(rank_geral, hide_index=True, use_container_width=True)

    with st.container():
        st.markdown('# Ranking Unitário')
        st.dataframe(rank_unico, hide_index=True, use_container_width=True )
        col1, col2, col3= st.columns(3)

        with col1:
            qnt_partidas = qnt_partidas_func(df)
            st.markdown('## Partidas')
            st.markdown(f'# {qnt_partidas}')

        with col1:
            st.markdown('# asd')

        with col2:
            with st.container():
                st.markdown('## DPS Herois')
                dps_heroi_geral, dps_sup_geral = dps_heroisup_geral_func(info_df, stats_dfo, df)
                st.dataframe(dps_heroi_geral, hide_index=True, use_container_width=True)
            
        with col3:
            with st.container():
                st.markdown('## DPS Suportes')
                dps_heroi_geral, dps_sup_geral = dps_heroisup_geral_func(info_df, stats_dfo, df)
                st.dataframe(dps_sup_geral, hide_index=True, use_container_width=True)
        st.write('---')

        

    with st.container():
        st.markdown('# Herois')
        col1, col2= st.columns(2)
        with col1:
            herois_mais_usados, herois_mais_usados_tab = herois_mais_usados_func(info_df)
            st.data_editor(herois_mais_usados_tab, hide_index=True, use_container_width=True)
            
        with col2:
            herois_mais_usados, herois_mais_usados_tab = herois_mais_usados_func(info_df)
            st.plotly_chart(herois_mais_usados, use_container_width=True, config={'displayModeBar': False, 'displaylogo': False, 'modeBarButtonsToAdd': []})
        
        st.write('---')

    with st.container():
        col1, col2, col3 = st.columns(3)
        with col2:
            st.markdown('# Suportes')
            sup_mais_usados, sup_mais_usados_table = sup_mais_usados_func(stats_df)
            st.dataframe(sup_mais_usados_table, use_container_width=True, hide_index=True)

    with st.container():
        sup_mais_usados, sup_mais_usados_table = sup_mais_usados_func(stats_df)
        st.plotly_chart(sup_mais_usados, use_container_width=True, config={'displayModeBar': False, 'displaylogo': False, 'modeBarButtonsToAdd': []})
    


with tab2:
    with st.container():
        col1, col2= st.columns(2)
        with col1:
            st.markdown('# Vitórias')
            with st.container():
                vitorias_geral, vitorias_geral_tabela = vitorias_geral_func(df)
                #st.table(vitorias_geral.set_index('name'))
                st.dataframe(vitorias_geral_tabela, use_container_width=True, hide_index=True, column_config={"Vitorias": st.column_config.NumberColumn(format="%d ⭐")})
                # Adicionar estilos CSS para centralizar o DataFrame
            
        with col2:
            with st.container():
                vitorias_geral, vitorias_geral_tabela = vitorias_geral_func(df)
                #st.table(vitorias_geral.set_index('name'))
                st.plotly_chart(vitorias_geral, use_container_width=True)
                # Adicionar estilos CSS para centralizar o DataFrame
                
                # st.write('---')
    
    with st.container():
        col1, col2= st.columns(2)
        with col1:
            with st.container():
                st.markdown('## Tempo total de jogo')
                jogador_mais_tempo, jogador_mais_tempo_tabela  = jogador_mais_tempo_func(info_df)
                st.dataframe(jogador_mais_tempo_tabela, use_container_width=True, hide_index=True)

        with col2:
            with st.container():
                st.markdown('## Tempo total de jogo')
                jogador_mais_tempo, jogador_mais_tempo_tabela  = jogador_mais_tempo_func(info_df)
                st.plotly_chart(jogador_mais_tempo, use_container_width=True)
        
        
    with st.container():
        col1, col2= st.columns(2)
        with col1:
            st.markdown('### Herois mais utilizados')
            heroi_preferido_jogador = heroi_preferido_jogador_func(info_df)
            st.dataframe(heroi_preferido_jogador, hide_index=True, use_container_width=True) 

        with col2:            
            st.markdown('### Suportes mais utilizados')
            top5_sup_jogadores = top5_sup_jogadores_func(stats_df, info_df)
            st.dataframe(top5_sup_jogadores, hide_index=True, use_container_width=True)
with tab3:
    st.write("# Cheats! >>>>>>>>>>> [link](https://rb.gy/d6lzey) OMFG")
    st.image('https://steamuserimages-a.akamaihd.net/ugc/93849814307728107/05C64279F092F4F09F8423C0FC0951055922702D/?imw=5000&imh=5000&ima=fit&impolicy=Letterbox&imcolor=%23000000&letterbox=false')