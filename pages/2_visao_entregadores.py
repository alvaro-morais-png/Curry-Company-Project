#libraries
from haversine import haversine
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go


#bibliotecas necessárias
#pip install folium usar os comando pip no terminal para instalar
#pip install streamlit-folium  #para instalar o streamlit_folium
import folium
import pandas as pd
import streamlit as st
from PIL import Image #biblioteca para alterar imagem 
from streamlit_folium import folium_static
from folium.plugins import HeatMap

st.set_page_config(page_title='Visão Entregadores', layout='wide')

#==================================================
#FUNÇÕES
#==================================================
def top_delivery(df1, top_asc   ):
    df22 = (df1.loc[:,['Delivery_person_ID','City','Time_taken(min)']]
              .groupby(['City','Delivery_person_ID'])
              .mean()
              .sort_values(['City', 'Time_taken(min)'], ascending=False)
              .reset_index())
    df_aux011 = df22.loc[df22['City'] == 'Metropolitian', :].head(10)
    df_aux022 = df22.loc[df22['City'] == 'Urban', :].head(10)
    df_aux033 = df22.loc[df22['City'] == 'Semi-Urban', :].head(10)
    
    
    df33 = pd.concat([df_aux011, df_aux022, df_aux033]).reset_index( drop=True)
    return df33
  
def clean_code( df1 ):
    """ Esta função tem responsabilidade de limpar o dataframe
        Tipos de limpeza:
        1.Remoção dos dados NaN
        2.Mudança do tipo da coluna de dados
        3.Remoção dos espaços das variáveis de texto
        4.Formatação da coluna de datas
        5.Limpeza da coluna de tempo(remoção do texto da variável numérica)

        Input: Dataframe
        Output: Dataframe
    """
    #limpeza
    linhas_semnan = df1.loc[:,'Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_semnan,:].copy()
    linhas_semnan = df1.loc[:,'City'] != 'NaN '
    df1 = df1.loc[linhas_semnan,:].copy()
    linhas_semnan = df1.loc[:,'Festival'] != 'NaN '
    df1 = df1.loc[linhas_semnan,:].copy()
    linhas_semnan = df.loc[:,'City'] != 'NaN '
    df1 = df1.loc[linhas_semnan,:].copy()
    linhas_semnan = df1.loc[:,'Road_traffic_density'] != 'NaN '
    df1 = df1.loc[linhas_semnan,:].copy()
    
    df1 = df1.reset_index(drop=True)
    
    #TRANSFORMANDO STRING E NUMEROS
    df1['ID'] = df1['ID'].astype(str)
    df1['Delivery_person_ID'] = df1['Delivery_person_ID'].astype(str)
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')
    
    #df1.dtypes
    
    # Removendo linhas vazias
    df1.loc[:,'ID'] = df1.loc[:,'ID'].str.strip()
    df1.loc[:,'Delivery_person_ID'] = df1.loc[:,'Delivery_person_ID'].str.strip()
    df1.loc[:,'Road_traffic_density'] = df1.loc[:,'Road_traffic_density'].str.strip()
    df1.loc[:,'Type_of_order'] = df1.loc[:,'Type_of_order'].str.strip()
    df1.loc[:,'Type_of_vehicle'] = df1.loc[:,'Type_of_vehicle'].str.strip()
    df1.loc[:,'City'] = df1.loc[:,'City'].str.strip()
    df1.loc[:,'Festival'] = df1.loc[:,'Festival'].str.strip()
    
    #LIMPANDO COLUNA DE TIME TAKEN
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1] )
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    return df1

#importe dataset 
df = pd.read_csv('datasets/train.csv')

#limpeza
df1 = clean_code(df)

# ================================================
# Barra lateral STREAMLIT
# ================================================
st.header('Marketplace - Visão Entregadores')

#image_path = r'C:/Users/MAYA NEVES/Documents/alvin/comunidadeds/projetos/currycompany/logo.jpg' ( comentado para levar para o cloud)
image =  Image.open('logo.jpg')
st.sidebar.image(image, width=200)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime(2022, 4, 13),
    min_value=datetime(2022, 2, 11),
    max_value=datetime(2022, 4, 20),
    format='DD-MM-YYYY')

st.header(date_slider)
st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições de trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default = ['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('Powered by Álvaro Morais')

#criando o filtro e abrindo o dataframe
#filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas,:]
st.dataframe(df1)

#filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)#.isin -> esta dizendo que 'Road_traffic_density' está em 'traffic_options' que o usuário que define
df1 = df1.loc[linhas_selecionadas,:]

# ================================================
# layout STREAMLIT
# ================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial','-','-'] )
with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            #maior idade dos entregadores
            maior_idade = df1.loc[:,['Delivery_person_Age']].max()
            col1.metric('Maior idade', maior_idade)
            
        with col2:
            #menor idade dos entregadores
            menor_idade = df1.loc[:,['Delivery_person_Age']].min()
            col2.metric('Menor idade', menor_idade)
            
        with col3:
            #melhor condicao do veiculo
            melhor_condicao = df1.loc[:,['Vehicle_condition']].max()
            col3.metric('Melhor condicao', melhor_condicao)
            
        with col4:
            #pior condicao do veículo
            pior_condicao = df1.loc[:,['Vehicle_condition']].min()
            col4.metric('Pior condicao', pior_condicao)
            
    with st.container():
        st.markdown("""---""")
        st.title('Avaliacoes')

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliacao media por Entregador')
            avaliac = (df1.loc[:,['Delivery_person_ID', 'Delivery_person_Ratings']]
                       .groupby('Delivery_person_ID')
                       .mean()
                       .reset_index())
            st.dataframe(avaliac)
  
        with col2:
            #Avaliacao media por transito(media e desvio padrao)
            st.markdown('##### Avaliacao media por Transito')
            avaliacao_media_desvio = df1.loc[:,['Delivery_person_Ratings', 'Road_traffic_density']].groupby('Road_traffic_density').agg({'Delivery_person_Ratings': ['mean','std']})
            avaliacao_media_desvio.columns = ['delivery_mean','delivery_std']
                #resetando o nome da coluna mean e std
            avaliacao_media_desvio.reset_index() #o reset_index veio para cá para para a tabela ficar melhor vizualmente
            st.dataframe(avaliacao_media_desvio)
            
            st.markdown('##### Avaliacao media por Clima')
            #Avaliacao media por clima(media e desvio padrao)
            avaliacao_media_desvio_weather = (df1.loc[:,['Delivery_person_Ratings', 'Weatherconditions']]
                                                 .groupby('Weatherconditions')
                                                 .agg({'Delivery_person_Ratings': ['mean','std']}))
            avaliacao_media_desvio_weather.columns = ['delivery_mean','delivery_std'] #resetando o nome da coluna mean e std
            avaliacao_media_desvio_weather.reset_index() #o reset_index veio para cá para para a tabela ficar melhor vizualmente
            st.dataframe(avaliacao_media_desvio_weather)
            
    with st.container():
        st.markdown("""---""")
        st.title("Velocidade de Entrega")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('##### Top Entregadores mais rapidos')
            df3 = top_delivery(df1, top_asc=True)
            st.dataframe(df3)
        
        with col2:
            st.markdown('##### Top Entregadores mais lentos')
            df33 = top_delivery(df1, top_asc=False)
            st.dataframe(df33)


