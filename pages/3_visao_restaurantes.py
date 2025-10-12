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
import numpy as np
from PIL import Image #biblioteca para alterar imagem 
from streamlit_folium import folium_static
from folium.plugins import HeatMap

st.set_page_config(page_title='Visão Restaurantes', layout='wide')

#==================================================
#FUNÇÕES
#==================================================
def avg_std_time_on_traffic(df1):
    #grafico de pizza 2
    entrega_cidade_pedido = (df1.loc[:,['City', 'Time_taken(min)','Road_traffic_density']]
                                .groupby(['City','Road_traffic_density'])
                                .agg({'Time_taken(min)':['mean','std']}))
    entrega_cidade_pedido.columns = ['avg_time','std_time']
    entrega_cidade_pedido = entrega_cidade_pedido.reset_index()
    
    fig = px.sunburst(entrega_cidade_pedido, path=['City', 'Road_traffic_density'], values = 'avg_time', color='std_time', color_continuous_scale='RdBu', color_continuous_midpoint=np.average(entrega_cidade_pedido['std_time']))
    return fig

def grafico_pizza_distance(df1):
    #grafico de pizza1
    col = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df1['distance'] = df1.loc[:, col].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis =1)
    avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
    fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0,0.1,0])])
    return fig

def avg_std_time_graph(df1):
    entrega_cidade = (df1.loc[:,['City', 'Time_taken(min)']].groupby('City').agg({'Time_taken(min)':['mean','std']}))
    entrega_cidade.columns = ['avg_time','std_time']
    entrega_cidade = entrega_cidade.reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control', x=entrega_cidade['City'], y=entrega_cidade['avg_time'], error_y=dict(type='data', array=entrega_cidade['std_time'])))
    fig.update_layout(barmode='group')
    
    return fig

def avg_std_time_delivery(df1, festival, op):
    """
        Esta função calcula o tempo médio e o desvio padrão do tempo de entrega.
        Parâmetros:
            Input:
                -df: Dataframe com os dados necessários para o cálculo
                -op: Tipo de operação que precisa ser calculado
                    'avg_time':Calcula o tempo médio 
                    'std_time': Calcula o desvio padrão do tempo.
            Output:
                -df : Dataframe com 2 colunas e 1 linha
    """
            
    entrega_cidade_festival = (df1.loc[:,['Time_taken(min)','Festival']]
                              .groupby('Festival')
                              .agg({'Time_taken(min)':['mean','std']}))
    entrega_cidade_festival.columns = ['avg_time','std_time']
    entrega_cidade_festival = entrega_cidade_festival.reset_index()
    entrega_cidade_festival = np.round(entrega_cidade_festival.loc[entrega_cidade_festival['Festival'] == festival, op],2)
    return entrega_cidade_festival

def distance(df1):
    col = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df1['distance'] = (df1.loc[:, col].apply(lambda x: haversine(
                        (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                        (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis =1))
    avg_distance = np.round(df1['distance'].mean(),2)
    return avg_distance

def top_delivery(df1, top_asc   ):
    df22 = (df1.loc[:,['Delivery_person_ID','City','Time_taken(min)']]
              .groupby(['City','Delivery_person_ID'])
              .mean()
              .sort_values(['City', 'Time_taken(min)'], ascending=top_asc)
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
st.header('Marketplace - Visão Restaurantes')

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
tab1, tab2, tab3 = st.tabs(['Visão Restaurantes','-','-'])
with tab1:
    with st.container():
        st.title('Overal Metrics')
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            #Quantidade de entregadores únicos
            qtd = len(df1.loc[:,'Delivery_person_ID'].unique())
            col1.metric('Entregadores', qtd)
      
        with col2:
            #Distância média dos restaurantes e dos locais de entrega
            avg_distance = distance(df1)
            col2.metric('A distancia media',avg_distance)
      
        with col3:
            entrega_cidade_festival = avg_std_time_delivery(df1,'Yes', 'avg_time') 
            col3.metric('Tempo médio de entrega', entrega_cidade_festival)

        with col4:
            entrega_cidade_festival = avg_std_time_delivery(df1,'Yes', 'std_time') 
            col4.metric('Desvio padrão', entrega_cidade_festival)
       
        with col5:
            entrega_cidade_festival = avg_std_time_delivery(df1,'No', 'avg_time')
            col5.metric('Tempo médio de entrega s/ Festival', entrega_cidade_festival)
        
        with col6: 
            entrega_cidade_festival = avg_std_time_delivery(df1,'No', 'std_time')
            col6.metric('Desvio padrão de entrega', entrega_cidade_festival)
            
    with st.container():
        st.markdown("""---""")
        col1, col2 = st.columns(2) 

        with col1:
            st.title("Tempo médio de entrega por cidade")
            fig = avg_std_time_graph(df1)
            st.plotly_chart(fig)
        with col2:
            st.title('Tempo médio por cidade e tipo de pedido')
            entrega_cidade_pedido = df1.loc[:,['City', 'Time_taken(min)','Type_of_order']].groupby(['City','Type_of_order']).agg({'Time_taken(min)':['mean','std']})
            entrega_cidade_pedido.columns = ['avg_time','std_time']
            entrega_cidade_pedido = entrega_cidade_pedido.reset_index()
            st.dataframe(entrega_cidade_pedido)
    with st.container():
        st.markdown("""---""")
        st.title('Distribuição do tempo')

        col1, col2 = st.columns(2)
        with col1:
            #grafico de pizza 01
            fig = grafico_pizza_distance(df1)
            st.plotly_chart(fig)
            
        with col2:
            fig = avg_std_time_on_traffic(df1)
            st.plotly_chart(fig)

        










    