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
import re

import matplotlib.pyplot as plt 


sns.set()

st.set_page_config(layout="wide", page_icon="📊")
### Uplod de data 

data_total = pd.read_csv("siniestros_geocod_rosario.csv")
data = data_total[data_total['anio_acci'] != 2011] # filtro el único siniestro de 2011 infiltrado en el csv del 2012

boton_sin_ilesos = st.checkbox("Eliminar siniestros sin heridos ni fallecidos") # botón para filtrar ilesos
data['total_heridos_fallecidos'] = data['heridos_leves'] + data['heridos_graves'] + data['heridos_gravisimos'] + data['fallecidos']

if boton_sin_ilesos:
    data = data.loc[(data['ilesos'] == 0) | (data['total_heridos_fallecidos'] > 0)]

# Data manipulation
data['fecha_date'] = data['fecha'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'))

data['geometry'] = data.apply(lambda row: Point(row['lon'], row['lat']), axis = 1)
gdf = gpd.GeoDataFrame(data, geometry = data.geometry, crs = 'EPSG:4326')

# Page title
st.title('Siniestros registrados en la ciudad de Rosario, Santa Fe, Argentina')

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

# FILA 1 --> SINIESTROS POR AÑO Y POR MES

fig = px.line(x = anios_interes.index, y = anios_interes.siniestros_por_anio, 
                 labels = {'x': 'Año', 'y': 'Cantidad de siniestros'}, title='Siniestros por año',
                 markers=True)

fig.update_layout(title_x=0.35, width=700)

columns[0].plotly_chart(fig)

fig = px.line(x = data.groupby('fecha_date').size().index, y = data.groupby('fecha_date').size(), 
                 labels = {'x': 'Mes', 'y': 'Cantidad de siniestros'}, title='Siniestros por mes')

fig.update_layout(title_x=0.35, width=700)
columns[1].plotly_chart(fig)

# FILA 2 --> TOTAL INVOLUCRADOS POR AÑO E INVOLUCRADOS SEGÚN TIPO DE GRAVEDAD (con botón para filtrar heridos leves)


st.subheader("Involucrados")
columns = st.columns(2)

fig_involucrados = px.bar(anios_interes, x='anio', y='total',
                          labels={'anio': 'Año', 'total': 'Cantidad de involucrados'},
                          title='Involucrados por año', text='total', range_y=[0, 16000])
fig_involucrados.update_layout(title_x=0.35, width=700)
fig_involucrados.update_traces(textposition='outside')
columns[0].text("\n\n")
columns[0].text("\n")

columns[0].plotly_chart(fig_involucrados)

boton_sin_leves = columns[1].checkbox("Quitar heridos leves")

if boton_sin_leves:
    fig_gravedad = px.bar(anios_interes, x='anio', y=['heridos_graves', 'heridos_gravisimos', 'fallecidos'],
                          barmode='group',
                          labels={'anio': 'Año', 'value': 'Cantidad de involucrados'},
                          title='Tipo de gravedad de los involucrados por Año')
    fig_gravedad.update_layout(legend_title='Tipo de gravedad', title_x=0.25)
else:
    fig_gravedad = px.bar(anios_interes, x='anio', y=['heridos_leves', 'heridos_graves', 'heridos_gravisimos', 'fallecidos'],
                          barmode='group',
                          labels={'anio': 'Año', 'value': 'Cantidad de involucrados'},
                          title='Tipo de gravedad de los involucrados por Año')
    fig_gravedad.update_layout(legend_title='Tipo de gravedad', title_x=0.25)

    fig_gravedad.for_each_trace(lambda t: t.update(name='Heridos leves' if t.name == 'heridos_leves' else
                                                    'Heridos graves' if t.name == 'heridos_graves' else
                                                    'Heridos gravísimos' if t.name == 'heridos_gravisimos' else
                                                    'Fallecidos'))

columns[1].plotly_chart(fig_gravedad, use_container_width=True)


# FILA 3 --> SINIESTROS POR DEPARTAMENTO Y AÑO

# st.subheader('Cantidad de siniestros por departamento')
# accid_por_dpto = data_total.groupby(['anio_acci', 'desc_dpto']).size().reset_index(name='count')
# municipios_unicos = accid_por_dpto['desc_dpto'].unique() #lista municipios
# selected_municipios = st.multiselect('Departamentos a visualizar:', municipios_unicos, default=municipios_unicos) #widget selección múltiple
# filtered_accid_por_dpto = accid_por_dpto[accid_por_dpto['desc_dpto'].isin(selected_municipios)] #filtro df según municipios seleccionados
# st.markdown("Aclaración: si desea visualizar uno o más departamentos, comience haciendo doble clic en el primero de ellos y, posteriormente, realice un clic simple en los demás sobre la leyenda, uno a la vez.")

# fig = px.line(filtered_accid_por_dpto, x='anio_acci', y='count', color='desc_dpto', labels={'anio_acci': 'Año', 'count': 'Cantidad de siniestros'}, 
#                category_orders={'Departamento': accid_por_dpto.groupby('desc_dpto')['count'].sum().sort_values(ascending=False).index}, title= 'Siniestros por departamento y año')

# fig.update_layout(
#     legend=dict(orientation="v", yanchor="top", y=1, xanchor="right", x=1.3),
#     margin=dict(b=60),
#     legend_title_text='Departamentos', title_x=0.35)

# st.plotly_chart(fig)


# FILA 3 --> SINIESTROS POR FRECUENCIA HORARIA (turno) Y RANKING DE SINIESTRALIDAD

st.subheader('Cantidad de siniestros por frecuencia horaria')
columns = st.columns(2)

data['hora_aprox'] = np.where(data['hora_aprox'] == '24:00:00', '00:00:00', data['hora_aprox']) # reemplazo '24:00:00' por '00:00:00'
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
turno_counts = data['turno'].value_counts()
fig = px.histogram(data, x='turno', title='Siniestros por turno',
                   labels={'turno': 'Turno', 'count': 'Cantidad de Siniestros'},
                   category_orders={'turno': ['Desconocido', 'Mañana', 'Tarde', 'Noche']})


fig.update_layout(yaxis_title='Cantidad de siniestros', title_x=0.35, width=700) 


for turno, count in turno_counts.items():
    fig.add_annotation(x=turno, y=count, text=str(count), showarrow=False,
                       yshift=13)
columns[0].plotly_chart(fig)

#ranking de mayor siniestralidad
data_turnos = data[data['turno'].isin(['Mañana', 'Tarde', 'Noche'])]

# combino dia - turno
data_turnos['dia_turno'] = data_turnos['desc_dia'] + ' - ' + data_turnos['turno']
ranking = data_turnos.groupby('dia_turno').size().reset_index(name='cantidad_siniestros')
ranking = ranking.sort_values(by='cantidad_siniestros', ascending=False)

ranking_data = ranking.sort_values(by='cantidad_siniestros', ascending=True)

fig = px.bar(ranking_data, x='cantidad_siniestros', y='dia_turno', orientation='h',
             labels={'cantidad_siniestros': 'Cantidad de siniestros', 'dia_turno': 'Día y turno'},
             title='Ranking de siniestralidad',
             color='cantidad_siniestros', color_continuous_scale='blues',
             range_color=[ranking_data['cantidad_siniestros'].min(), ranking_data['cantidad_siniestros'].max()])

valores = ranking_data['cantidad_siniestros'].sort_values(ascending=True)
for i, valor in enumerate(valores):
    fig.add_annotation(
        x=valor,
        y=ranking_data['dia_turno'].iloc[i],
        text=str(valor),
        showarrow=False,
        font=dict(size=12),
        xshift=16
    )
fig.update_layout(showlegend=False, coloraxis_showscale=False, title_x=0.35)

columns[1].plotly_chart(fig, use_container_width=True)

# FILA 4 --> MAPA LOCALIZACIÓN GEOGRÁFICA DE SINIESTROS
municipios_sta_fe = gpd.read_file('municipios_santa_fe.gpkg')
rosario_mapa = municipios_sta_fe[municipios_sta_fe['nam'] == 'Rosario'].copy()

bounds = rosario_mapa.geometry.bounds # límites del mapa
north, south, east, west = bounds['maxy'].max(), bounds['miny'].min(), bounds['maxx'].max(), bounds['minx'].min()
color_dict = {'Mañana': 'green', 'Tarde': 'blue', 'Noche': 'red', 'Desconocido': 'gray'} # diccionario de colores para cada turno

fig = px.scatter(data, x='lon', y='lat', color='turno',
                 color_discrete_map=color_dict,
                 labels={'lon': 'Longitud', 'lat': 'Latitud', 'turno': 'Turno'},
                 title='Localización geográfica de siniestros por turno')

fig.update_traces(marker=dict(size=4))

fig.update_layout(
    xaxis=dict(range=[west, east], title='Longitud'),
    yaxis=dict(range=[south, north], title='Latitud'),
    legend_title='Turno',
    title_x=0.25,
    width=800, height=800
)
st.plotly_chart(fig)


# FILA 5 --> SINIESTROS POR MODO (calculados sobre al menos uno de los modos participantes)

transportes = data['desc_participante'].str.get_dummies(',') # obtengo df de dummies
conteo_transportes = transportes.sum()  # sumo esos dummies
porcentaje_transportes = (conteo_transportes / len(data)) * 100   # calculo porcentaje 

# sumo los porcentajes de los transportes y camiones

suma_transportes = porcentaje_transportes[['Transporte de Pasajeros','Transporte de Pasajeros (H/ 8 asientos)','Transporte de Pasajeros Larga Distancia (> 8 asientos)',
                                                    'Transporte de Pasajeros Larga Distancia (Doble Piso)','Transporte de Pasajeros Larga Distancia (Piso  y  1/2)','Transporte de Pasajeros Urbano (> 8 asientos)']].sum()
suma_camiones = porcentaje_transportes[['Camión','Camión Chasis','Camión c / Acoplado','Camión c / Semirremolque']].sum()

# reemplazo y elimino
porcentaje_transportes['Transporte de Pasajeros'] = suma_transportes
porcentaje_transportes['Camión'] = suma_camiones
porcentaje_transportes.drop(['Transporte de Pasajeros (H/ 8 asientos)','Transporte de Pasajeros Larga Distancia (> 8 asientos)','Transporte de Pasajeros Larga Distancia (Doble Piso)',
                              'Transporte de Pasajeros Larga Distancia (Piso  y  1/2)','Transporte de Pasajeros Urbano (> 8 asientos)','Camión Chasis','Camión c / Acoplado','Camión c / Semirremolque'], inplace=True)

st.subheader('Participación por modo')
st.markdown("Los porcentajes del siguiente gráfico están calculados sobre la totalidad de siniestros y representan la participación de al menos uno de los modos involucrados.")
columns = st.columns(2)

porcentaje_mayor_a_1 = porcentaje_transportes[porcentaje_transportes > 1].sort_values(ascending=True)
# gráfico solo para los porcentajes mayores al 1%
fig = px.bar(porcentaje_mayor_a_1, orientation='h', labels={'y': 'Modo', 'x': 'Porcentaje de siniestros'}, 

             title='Participación modal en la totalidad de siniestros')

fig.update_layout(height=500, yaxis_title='Modo', xaxis_title='Porcentaje de siniestros',  title_x=0.35, showlegend=False) 
for i, percentage in enumerate(porcentaje_mayor_a_1.values):
    fig.add_annotation(
        x=percentage,
        y=porcentaje_mayor_a_1.index[i],
        text=f'{percentage:.2f}%',
        showarrow=False,
        font=dict(size=12),
        xshift=30 
    )

columns[0].plotly_chart(fig, use_container_width=True)

# para los modos que alcanzan menos del 1%, los escribo en formato texto con HTML

porcentaje_menor_a_1 = porcentaje_transportes[porcentaje_transportes <= 1].sort_values(ascending=False)

columns[1].markdown("<h6 style='text-align: left; margin-top: 100px;  margin-left: 200px;'>Modos que no alcanzan el 1%:</h6>", unsafe_allow_html=True)
var_html = ""  # inicializo el texto HTML
for transporte, porcentaje in porcentaje_menor_a_1.items():

    var_html += f"<p style='text-align: left; margin-left: 200px;'>- {transporte}: {porcentaje:.2f}% </p>"  # agrego el texto HTML con margen izquierdo

columns[1].markdown(var_html, unsafe_allow_html=True)




# FILA 6 --> SINIESTROS POR MODO (calculados sobre la totalidad de los modos participantes)

st.markdown("Los porcentajes del siguiente gráfico están calculados sobre la totalidad de los modos involucrados en los accidentes.")
columns = st.columns(2)
transportes = data['desc_participante'].str.split(',', expand=True)
conteo_transportes = transportes.stack().value_counts()  # cuento numero de ocurrencias de cada vehículo
porcentaje_transportes = (conteo_transportes / conteo_transportes.sum() * 100).round(2)   # calculo porcentaje

# sumo los porcentajes de los transportes y camiones
suma_transportes = porcentaje_transportes[['Transporte de Pasajeros','Transporte de Pasajeros (H/ 8 asientos)','Transporte de Pasajeros Larga Distancia (> 8 asientos)',
                                                    'Transporte de Pasajeros Larga Distancia (Doble Piso)','Transporte de Pasajeros Larga Distancia (Piso  y  1/2)','Transporte de Pasajeros Urbano (> 8 asientos)']].sum()
suma_camiones = porcentaje_transportes[['Camión','Camión Chasis','Camión c / Acoplado','Camión c / Semirremolque']].sum()

# reemplazo y elimino
porcentaje_transportes['Transporte de Pasajeros'] = suma_transportes
porcentaje_transportes['Camión'] = suma_camiones
porcentaje_transportes.drop(['Transporte de Pasajeros (H/ 8 asientos)','Transporte de Pasajeros Larga Distancia (> 8 asientos)','Transporte de Pasajeros Larga Distancia (Doble Piso)',
                              'Transporte de Pasajeros Larga Distancia (Piso  y  1/2)','Transporte de Pasajeros Urbano (> 8 asientos)','Camión Chasis','Camión c / Acoplado','Camión c / Semirremolque'], inplace=True)
porcentaje_mayor_a_1 = porcentaje_transportes[porcentaje_transportes > 1].sort_values(ascending=True)

fig = px.pie(names=porcentaje_mayor_a_1.index, values=porcentaje_mayor_a_1.values,
             title='Porcentaje de modos involucrados')
fig.update_layout(title_x=0.35)
columns[0].plotly_chart(fig, use_container_width=True)

# para los modos que no alcanzan el 1%, escribo en formato texto con HTML
porcentaje_menor_a_1 = porcentaje_transportes[porcentaje_transportes <= 1].sort_values(ascending=False)

columns[1].markdown("<h6 style='text-align: left; margin-top: 80px;  margin-left: 220px;'>Modos que no alcanzan el 1%:</h6>", unsafe_allow_html=True)
var_html = ""  # inicializo el texto HTML
for transporte, porcentaje in porcentaje_menor_a_1.items():
    var_html += f"<p style='text-align: left; margin-left: 220px;'>- {transporte}: {porcentaje:.2f}% </p>"  # Agregar el texto HTML con margen izquierdo
columns[1].markdown(var_html, unsafe_allow_html=True)




# FILA 7 --> SINIESTROS SEGUN DIA DE LA SEMANA (gráfico de barras y torta para porcentajes dia semana - fin de semana y barras para toda la semana)


st.subheader('Siniestros según día')
columns = st.columns(2)

conteo_dias = data['desc_dia'].value_counts()
data_dias = pd.DataFrame({
    'Día de la semana': conteo_dias.index,
    'Cantidad de siniestros': conteo_dias.values
})
data_dias['Tipo de día'] = data_dias['Día de la semana'].apply(lambda x: 'Fin de semana' if x in ['Sabado', 'Domingo'] else 'Día de semana')
dias_total = data_dias.groupby('Tipo de día').sum().reset_index()


# GRAFICO BARRAS DIA SEMANA VS FIN DE SEMANA
fig = px.bar(dias_total, x='Tipo de día', y='Cantidad de siniestros',
             labels={'Cantidad de siniestros': 'Cantidad de siniestros', 'Tipo de día': 'Tipo de día'},
             title='Siniestros por tipo de día')
fig.update_layout(title_x=0.35)
for i, valor in enumerate(dias_total['Cantidad de siniestros']):
    fig.add_annotation(
        x=dias_total['Tipo de día'][i],
        y=valor,
        text=str(valor),
        showarrow=False,
        font=dict(size=12),
        yshift=13  
    )

columns[0].plotly_chart(fig, use_container_width=True)


# GRAFICO TORTA DIA SEMANA VS FIN DE SEMANA
fig = px.pie(dias_total, values='Cantidad de siniestros', names='Tipo de día',
             title='Porcentaje de siniestros por tipo de día')
fig.update_layout(title_x=0.35)

columns[1].plotly_chart(fig, use_container_width=True)


# FILA 8 --> GRÁFICO DE BARRAS SINIESTROS POR DÍA

orden_dias = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']
fig = px.bar(x=conteo_dias.index, y=conteo_dias.values,
             labels={'y': 'Cantidad de siniestros', 'x': 'Día'},
             title='Siniestros por día',
             category_orders={"x": orden_dias})

for i, val in enumerate(conteo_dias.values):
    fig.add_annotation(x=conteo_dias.index[i], y=val, text=str(val), showarrow=False,
                       yshift=13)
fig.update_layout(title_x=0.40)

st.plotly_chart(fig)


# FILA 9 --> SINIESTROS POR TIPO DE CALZADA


st.subheader('Segmentación por tipo de calzada')
columns = st.columns(2)

data['desc_tipo_calzada'] = data['desc_tipo_calzada'].apply(lambda x: re.sub(r'\bhormigón\b', 'Hormigón', x, flags=re.IGNORECASE))
calzada_separada = data['desc_tipo_calzada'].str.get_dummies(sep=',')
calzada_counts = calzada_separada.sum().sort_values(ascending=False)


# gráfico de barras

fig = px.bar(x=calzada_counts.index, y=calzada_counts.values,
             labels={'x': 'Tipo de calzada', 'y': 'Cantidad de siniestros'},
             title='Siniestros por tipo de calzada')
for i in range(len(calzada_counts)):
    fig.add_annotation(x=calzada_counts.index[i],
                       y=calzada_counts.values[i],
                       text=str(calzada_counts.values[i]), 
                       showarrow=False, 
                       font=dict(size=10),
                       yshift=13)

fig.update_layout(title_x=0.40)

columns[0].plotly_chart(fig, use_container_width=True)

# grafico de torta con porcentajes

porcentajes = (calzada_counts / calzada_counts.sum()) * 100
fig = px.pie(names=porcentajes.index, values=porcentajes.values,
             title='Porcentaje de siniestros por tipo de calzada')
fig.update_layout(title_x=0.40)

columns[1].plotly_chart(fig, use_container_width=True)



