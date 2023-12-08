import streamlit as st
import requests
import pandas as pd
from analise import etl, qnt_partidas_func, top5_sup_jogadores_func, sup_mais_usados_func, herois_mais_usados_func, vitorias_geral_func, dps_heroisup_geral_func


url = "https://rootd4.vercel.app/score/all"
response = requests.get(url)
dados = response.json()
# Transformar a resposta JSON em DataFrame
df = pd.DataFrame(response.json()).copy()
stats_df, info_df, stats_dfo = etl(df)

# Configurar a tabela no Streamlit
tab1, tab2, tab3 = st.tabs(['Dados', 'Jogadores', 'Visão Demográfica'])



with tab1:
    with st.container():
        col1, col2, col3= st.columns(3)

        with col1:
            qnt_partidas = qnt_partidas_func(df)
            st.markdown('## Partidas')
            st.markdown(f'# {qnt_partidas}')
            st.markdown('## ---')

        with col2:
            with st.container():
                st.markdown('## DPS Herois')
                dps_heroi_geral, dps_sup_geral = dps_heroisup_geral_func(info_df, stats_dfo, df)
                st.dataframe(dps_heroi_geral, hide_index=True)
            
        with col3:
            with st.container():
                st.markdown('## DPS Suportes')
                dps_heroi_geral, dps_sup_geral = dps_heroisup_geral_func(info_df, stats_dfo, df)
                st.dataframe(dps_sup_geral, hide_index=True)

        

    with st.container():
        st.markdown('# Herois')
        col1, col2 = st.columns(2)
        with col1:
            herois_mais_usados, herois_mais_usados_tab = herois_mais_usados_func(info_df)
            st.plotly_chart(herois_mais_usados, use_container_width=True, config={'displayModeBar': False, 'displaylogo': False, 'modeBarButtonsToAdd': []})
            
        with col2:
            st.markdown('## Herois mais utilizados')
            herois_mais_usados, herois_mais_usados_tab = herois_mais_usados_func(info_df)
            st.data_editor(herois_mais_usados_tab, use_container_width=True)
    
    with st.container():
        st.markdown('## Suportes mais utilizados')
        sup_mais_usados = sup_mais_usados_func(stats_df)
        st.plotly_chart(sup_mais_usados, use_container_width=True, config={'displayModeBar': False, 'displaylogo': False, 'modeBarButtonsToAdd': []})
    


with tab2:
    with st.container():
        st.markdown('## Vitórias')
        vitorias_geral = vitorias_geral_func(df)
        #st.table(vitorias_geral.set_index('name'))
        st.dataframe(vitorias_geral, hide_index=True)

    with st.container():
        st.markdown('## Suportes mais utilizados')
        top5_sup_jogadores = top5_sup_jogadores_func(stats_df, info_df)
        st.dataframe(top5_sup_jogadores, hide_index=True)