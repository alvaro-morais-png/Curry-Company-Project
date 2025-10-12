
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

st.set_page_config(page_title='Visão Empresa', layout='wide')

#------------------------------------------------------------------
#FUNÇÕES
#------------------------------------------------------------------
def delivery_density(df1):
    # pegar os pontos individuais (sem groupby)
    locali = df1.loc[:, ['Delivery_location_latitude', 'Delivery_location_longitude']]
    
    # cria o mapa centralizado
    #lat_center = ((locali['Delivery_location_latitude'].max() + locali['Delivery_location_latitude'].min()) / 2)
    #lon_center = ((locali['Delivery_location_longitude'].max() + locali['Delivery_location_longitude'].min()) / 2)
    lat_center = locali.loc[1500, 'Delivery_location_latitude']
    lon_center = locali.loc[1500, 'Delivery_location_longitude']
   # m = folium.Map(location=[lat_center, lon_center], zoom_start=12)
    m = folium.Map(location=[lat_center, lon_center], zoom_start=4)
    
    
    # adiciona o heatmap
    HeatMap(data=locali[['Delivery_location_latitude', 'Delivery_location_longitude']].values).add_to(m)
    
    # se for usar no streamlit
    
    folium_static(m)
    return None

def country_map(df1):
    #plotando o mapa
    locali = (df1.loc[:,['City','Road_traffic_density','Delivery_location_latitude', 'Delivery_location_longitude']]
                 .groupby(['City', 'Road_traffic_density'])
                 .median()
                 .reset_index())
    map = folium.Map()
    for index, location_info in locali.iterrows():
      folium.Marker([location_info['Delivery_location_latitude'],
                     location_info['Delivery_location_longitude']],
                    popup=location_info[['City','Road_traffic_density' ]]).add_to(map)
    
    folium_static(map, width=1024, height = 600)
    return None

def order_share_by_week(df1):
    #gráfico de linha visão tática
    entrega_semana = (df1.loc[:,['ID', 'week_of_year']]
                         .groupby('week_of_year')
                         .count()
                         .reset_index())
    entrega_semana02 = (df1.loc[:,['Delivery_person_ID', 'week_of_year']]
                           .groupby('week_of_year')
                           .nunique()
                           .reset_index())
    entrega_semana03 = pd.merge(entrega_semana, entrega_semana02, how='inner', on='week_of_year')
    entrega_semana03['order_by_delivery'] = entrega_semana03['ID']/entrega_semana03['Delivery_person_ID']
    fig = px.line(entrega_semana03, x='week_of_year', y='order_by_delivery')
    return fig

def week_of_year(df1):
    #gráfico de linhas visão tática
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    df_sem = (df1.loc[:,['ID', 'week_of_year']]
                 .groupby('week_of_year')
                 .count()
                 .reset_index())
    fig = px.line(df_sem, x='week_of_year', y='ID')
    return fig

def traffic_order_city(df1):
    #grafico bolhas
    comparacao_city_road = (df1.loc[:,['ID','City', 'Road_traffic_density']]
                               .groupby(['City', 'Road_traffic_density'])
                               .count()
                               .reset_index())
    fig = px.scatter(comparacao_city_road, x='City', y= 'Road_traffic_density', size='ID', color='City')
    return fig

def traffic_order_share(df1):
    #grafico de pizza
    dist_tipo = (df1.loc[:,['ID', 'Road_traffic_density']]
                    .groupby('Road_traffic_density')
                    .count()
                    .reset_index())
    dist_tipo['entregas_perc'] = dist_tipo['ID']/dist_tipo['ID'].sum()
    fig = px.pie(dist_tipo, values='entregas_perc', names='Road_traffic_density')
    return fig

def order_metric(df1):
    #Order Metric
    #1 quantidade de pedidos por dia
    #colunas
    cols = ['ID','Order_Date']
    #linhas
    qtd_dia = (df1.loc[:, cols]
                  .groupby('Order_Date')
                  .count()
                  .reset_index()) #o order virou o index, precisei resetar o index
    #desenhar o gráfico de barras - plotly
    fig = px.bar(qtd_dia, x='Order_Date', y='ID')
    
    return fig

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

#========================INÍCIO DA ESTRUTURA LÓGICA DO CÓDIGO========================
#========================
# Import dataset
df = pd.read_csv('datasets/train.csv')
#========================
# limpando os dados
df1 = clean_code( df )

# ================================================
# Barra lateral STREAMLIT
# ================================================
st.header('Marketplace - Visão Cliente')

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
tab1, tab2, tab3 = st.tabs(['Visão Gerencial','Visão Tática','Visão Geográfica'])
#dividindo o gráfico com with
with tab1:
    with st.container():
        #Order Metric
        fig = order_metric(df1)
        st.markdown('# Orders by Day')
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            fig = traffic_order_share(df1)
            st.header("Traffic Order Share")
            st.plotly_chart(fig, use_container_width=True)
           
        with col2:
            fig = traffic_order_city(df1)
            st.header("Traffic Order City")
            st.plotly_chart(fig, use_container_width=True)
          
with tab2:
    with st.container():
        fig = week_of_year(df1)
        st.markdown("Order by Week")
        st.plotly_chart(fig, use_container_width=True)
        
    with st.container():
        fig = order_share_by_week(df1)
        st.markdown("Order Share by Week")
        st.plotly_chart(fig, use_container_width = True)

with tab3:
    with st.container():
        st.markdown('# Country Maps')
        country_map(df1)
        
        
#CRIAR MAPA DE CALOR COM TODOS OS PONTOS
    with st.container():
        st.markdown('# Delivery Density')
        delivery_density(df1)
        
