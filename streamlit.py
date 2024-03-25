import streamlit as st
import pandas as pd
import geopandas as gpd
import datetime
import folium
from folium import plugins
from streamlit_folium import st_folium
from shapely import Point
import plotly.express as px
import seaborn as sns
import numpy as np

sns.set()

st.set_page_config(layout="wide")
### Uplod de data 
#TO-Do: use cleaned data, final data
data_total = pd.read_csv("data_final.csv")
data = data_total[data_total['desc_dpto']=='Rosario'].copy()

# Data manipulation
data['fecha_date'] = data['fecha'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'))
data.loc[data['posicion_XY'].notnull(), 'lat'] = data.loc[data['posicion_XY'].notnull(), 'posicion_XY'].apply(lambda x: float(x.split(',')[0]))
data.loc[data['posicion_XY'].notnull(), 'lon'] = data.loc[data['posicion_XY'].notnull(), 'posicion_XY'].apply(lambda x: float(x.split(',')[1]))
data['geometry'] = data.apply(lambda row: Point(row['lon'], row['lat']), axis = 1)
gdf = gpd.GeoDataFrame(data, geometry = data.geometry, crs = 'EPSG:4326')

# Page title
st.title('Siniestros registrados en la ciudad de Rosario, Santa Fé, Argentina')

time_range = st.slider(
                        "Intervalo de observaciones:",
                        value=(datetime.datetime(2012, 1, 1), datetime.datetime(2020, 12, 31)))

def create_map(gdf, lat, lon, zoom_start, radius): 
    m = folium.Map(location=[lat, lon], zoom_start = zoom_start)
    folium.TileLayer('OpenStreetMap').add_to(m)
    plugins.HeatMap(gdf, radius = radius).add_to(m)
    return m

data_to_plot_map = gdf[(gdf['fecha_date']>= time_range[0]) & (gdf['fecha_date']<= time_range[1])].drop('fecha_date', axis = 1)
m = create_map(data_to_plot_map[data_to_plot_map['posicion_XY'].notnull()][['lat', 'lon']], 
               lat = -32.952601, lon = -60.643213, zoom_start = 12, radius = 10)
st_folium(m, use_container_width= True)


anios_interes = pd.DataFrame(index = list(range(2012, 2021)))
anios_interes['anio'] = list(range(2012, 2021))
anios_interes['siniestros_por_anio'] = data.groupby('anio_acci').size()
for col in ['heridos_leves', 'heridos_graves', 'heridos_gravisimos', 'ilesos', 'fallecidos', 'total']:
    anios_interes[col] = data.groupby('anio_acci')[col].sum()

columns = st.columns(2) #cantidad de columnas

# fila1
fig = px.line(x = anios_interes.index, y = anios_interes.siniestros_por_anio, 
                 labels = {'x': 'Año', 'y': 'Cantidad de siniestros'}, 
                 markers=True)
columns[0].plotly_chart(fig)

fig = px.line(x = data.groupby('fecha_date').size().index, y = data.groupby('fecha_date').size(), 
                 labels = {'x': 'Fecha', 'y': 'Cantidad de siniestros'}, 
                 )
columns[1].plotly_chart(fig)

# ISSUE 5 

st.subheader("Comparación columna 'Total' y suma de Involucrados")
st.markdown("Histograma y scatterplot con el fin de comparar los valores de la columna *total* y la suma de *heridos_leves*, *heridos_graves*, *heridos_gravisimos*, *ilesos* y *fallecidos*.")
columns = st.columns(2)

#histograma
data['diferencias_totales'] = data[['heridos_leves', 'heridos_graves', 'heridos_gravisimos', 'ilesos', 'fallecidos']].sum(axis = 1) - data.total
fig = px.histogram(data, x = 'diferencias_totales', labels = {'diferencias_totales': 'Diferencias'}, title='Histograma de Diferencias')
columns[0].plotly_chart(fig)

#nuevo scatterplot
data['suma_involucrados'] = data[['heridos_leves', 'heridos_graves', 'heridos_gravisimos', 'ilesos', 'fallecidos']].sum(axis = 1)
fig = px.scatter(data, x='total', y='suma_involucrados', labels={'total': 'Total', 'suma_involucrados': 'Suma involucrados'}, title='Scatterplot Total vs Suma de Involucrados')
columns[1].plotly_chart(fig)

#fila3

st.subheader("Involucrados")
columns = st.columns(2)
fig = px.bar(anios_interes, x = 'anio',  y = 'total', 
             labels = {'anio': 'Año', 'total': 'Cantidad de personas involucradas'})
columns[0].plotly_chart(fig)

fig = px.bar(anios_interes, x = 'anio',  y = ['heridos_leves', 'ilesos'], barmode = 'group', 
             labels = {'anio': 'Año', 'value': 'Cantidad de personas con heridas leves o ilesas'})
columns[1].plotly_chart(fig)

#fila4
columns = st.columns(1)
fig = px.bar(anios_interes, x = 'anio',  y = ['heridos_graves', 'heridos_gravisimos', 'fallecidos'], barmode = 'group', 
             labels = {'anio': 'Año', 'value': 'Cantidad de personas con heridas graves, gravísimas o fallecidas'})
columns[0].plotly_chart(fig)


# ISSUE 4

st.subheader('Cantidad de Valores Nulos por año según Categoría')
cuadro = pd.DataFrame()
for col in data.columns:
    if col != 'anio_acci': # agrupo cada columna (menos 'anio_acci') por año y cuento valores nulos
        data_agrupada = data.groupby(['anio_acci'])[col].apply(lambda x: x.isnull().sum()).reset_index()
        cuadro = pd.concat([cuadro, data_agrupada.set_index('anio_acci')], axis=1)

cuadro.drop('Unnamed: 0', axis=1, inplace=True)
st.table(cuadro)


# ISSUE 7 

st.subheader('Cantidad de Siniestros por Departamento')
accid_por_dpto = data_total.groupby(['anio_acci', 'desc_dpto']).size().reset_index(name='count')
municipios_unicos = accid_por_dpto['desc_dpto'].unique() #lista municipios
selected_municipios = st.multiselect('Departamentos a visualizar:', municipios_unicos, default=municipios_unicos) #widget selección múltiple
filtered_accid_por_dpto = accid_por_dpto[accid_por_dpto['desc_dpto'].isin(selected_municipios)] #filtro df según municipios seleccionados
st.markdown("Aclaración: si desea visualizar uno o más departamentos, comience haciendo doble clic en el primero de ellos y, posteriormente, realice un clic simple en los demás sobre la leyenda, uno a la vez.")

# gráfico con los datos filtrados
fig = px.line(filtered_accid_por_dpto, x='anio_acci', y='count', color='desc_dpto', labels={'anio_acci': 'Año', 'count': 'Cantidad de Siniestros'}, 
               category_orders={'Departamento': accid_por_dpto.groupby('desc_dpto')['count'].sum().sort_values(ascending=False).index})

fig.update_layout(
    legend=dict(orientation="v", yanchor="top", y=1, xanchor="right", x=1.3),
    margin=dict(b=60),
    legend_title_text='Departamentos' 
)

st.plotly_chart(fig)

#SINIESTROS POR FRECUENCIA HORARIA (para Rosario) --> issue 16 

st.subheader('Cantidad de Siniestros por Frecuencia Horaria')
columns = st.columns(2)

# reemplazo '24:00:00' por '00:00:00'
data['hora_aprox'] = np.where(data['hora_aprox'] == '24:00:00', '00:00:00', data['hora_aprox'])
data['hora_aprox'] = pd.to_datetime(data['hora_aprox'])

# límites de los turnos
manana_limite = pd.to_datetime('12:00:00').time()
tarde_limite = pd.to_datetime('20:00:00').time()
noche_limite = pd.to_datetime('00:00:00').time()

def asignar_turno(hora):
    if pd.isnull(hora):
        return 'Desconocido'
    elif hora.time() < manana_limite:
        return 'Mañana'
    elif hora.time() < tarde_limite:
        return 'Tarde'
    else:
        return 'Noche'

data['turno'] = data['hora_aprox'].apply(asignar_turno)
fig = px.histogram(data, x='turno', title='Cantidad de Siniestros por Turno',
                   labels={'turno': 'Turno', 'count': 'Cantidad de Siniestros'},
                   category_orders={'turno': ['Desconocido', 'Mañana', 'Tarde', 'Noche']})

fig.update_layout(yaxis_title='Cantidad de Siniestros') 
columns[0].plotly_chart(fig)

#ranking de mayor siniestralidad
data_turnos = data[data['turno'].isin(['Mañana', 'Tarde', 'Noche'])]

# combino dia - turno
data_turnos['dia_turno'] = data_turnos['desc_dia'] + ' - ' + data_turnos['turno']
ranking = data_turnos.groupby('dia_turno').size().reset_index(name='cantidad_siniestros')
ranking = ranking.sort_values(by='cantidad_siniestros', ascending=False)

ranking_data = ranking.sort_values(by='cantidad_siniestros', ascending=True)

fig = px.bar(ranking_data, x='cantidad_siniestros', y='dia_turno', orientation='h',
             labels={'cantidad_siniestros': 'Cantidad de Eventos', 'dia_turno': 'Día y Turno'},
             title='Ranking de Siniestralidad',
             color='cantidad_siniestros', color_continuous_scale='blues',
             range_color=[ranking_data['cantidad_siniestros'].min(), ranking_data['cantidad_siniestros'].max()])

fig.update_layout(showlegend=False, coloraxis_showscale=False)
columns[1].plotly_chart(fig)