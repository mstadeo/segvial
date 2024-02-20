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
sns.set()

st.set_page_config(layout="wide")
### Uplod de data
#TO-Do: use cleaned data, final data
data = pd.read_csv('data_final.csv')
data = data[data['desc_dpto']=='Rosario'].copy()

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

columns = st.columns(2)
fig = px.line(x = anios_interes.index, y = anios_interes.siniestros_por_anio,
                 labels = {'x': 'Año', 'y': 'Cantidad de siniestros'},
                 markers=True)
columns[0].plotly_chart(fig)

fig = px.line(x = data.groupby('fecha_date').size().index, y = data.groupby('fecha_date').size(),
                 labels = {'x': 'Fecha', 'y': 'Cantidad de siniestros'},
                 )
columns[1].plotly_chart(fig)

columns = st.columns(2)
data['diferencias_totales'] = data[['heridos_leves', 'heridos_graves', 'heridos_gravisimos', 'ilesos', 'fallecidos']].sum(axis = 1) - data.total
fig = px.histogram(data, x = 'diferencias_totales', labels = {'diferencias_totales': 'Diferencias'})
columns[0].plotly_chart(fig)

fig = px.bar(anios_interes, x = 'anio',  y = 'total',
             labels = {'anio': 'Año', 'total': 'Cantidad de personas involucradas'})
columns[1].plotly_chart(fig)

columns = st.columns(2)
fig = px.bar(anios_interes, x = 'anio',  y = ['heridos_leves', 'ilesos'], barmode = 'group',
             labels = {'anio': 'Año', 'value': 'Cantidad de personas con heridas leves o ilesas'})
columns[0].plotly_chart(fig)

fig = px.bar(anios_interes, x = 'anio',  y = ['heridos_graves', 'heridos_gravisimos', 'fallecidos'], barmode = 'group',
             labels = {'anio': 'Año', 'value': 'Cantidad de personas con heridas graves, gravísimas o fallecidas'})
columns[1].plotly_chart(fig)


# fig = px.line(anios_interes, x = 'anio', y = ['heridos_leves', 'heridos_graves', 'heridos_gravisimos', 'ilesos', 'fallecidos'])

# st.plotly_chart(fig)
