import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Calidad de datos", page_icon="📈", layout="wide")
st.title("📈 Calidad de datos")
st.set_option('deprecation.showPyplotGlobalUse', False)
pd.set_option('display.width', 0)

data_total = pd.read_csv("data_final.csv")
data = data_total[data_total['desc_loc']=='ROSARIO'].copy()
data = data.iloc[:, 1:]
data = data[data['anio_acci'] != 2011] #filtro el único siniestro del 2011 infiltrado que figura en el csv del 2012.

# primer sección
st.header("Información Básica sobre el Dataset")
st.markdown("El conjunto de datos cuenta con **{}** siniestros ocurridos entre los años 2012 y 2020 en la ciudad de Rosario, Santa Fe, Argentina.".format(len(data)))
num_filas = data.shape[0]
num_columnas = data.shape[1]
nombre_columnas = data.columns.tolist()

info_basica = pd.DataFrame({
    'Descripción': ['Número de observaciones', 'Número de columnas', 'Nombre de las columnas'],
    'Valor': [num_filas, num_columnas, ", ".join(nombre_columnas)]
})

st.markdown(f"""
**- Número de filas:** {num_filas}
\n**- Número de columnas:** {num_columnas}
\n**- Nombre de las columnas:** {', '.join(nombre_columnas)}
""")

st.markdown("**Primeras filas del dataset:**")
st.dataframe(data.head())

st.subheader('Cantidad de valores nulos por año según categoría')
cuadro = pd.DataFrame()
for col in data.columns:
    if col != 'anio_acci': # agrupo cada columna (menos 'anio_acci') por año y cuento valores nulos
        data_agrupada = data.groupby(['anio_acci'])[col].apply(lambda x: x.isnull().sum()).reset_index()
        cuadro = pd.concat([cuadro, data_agrupada.set_index('anio_acci')], axis=1)
st.table(cuadro)

st.subheader('Cantidad de siniestros duplicados')
columnas = data.columns.tolist()
columnas_seleccionadas = st.multiselect("Seleccionar columnas para hallar duplicados:", columnas) # widget de selección de columnas

if columnas_seleccionadas:
    duplicados = data.duplicated(subset=columnas_seleccionadas, keep=False)
    cantidad_duplicados = duplicados.sum() # cantidad de filas duplicadas
    st.write(f"Cantidad de siniestros duplicados: {cantidad_duplicados}")

    if cantidad_duplicados > 0:
        st.write("Siniestros duplicados:")
        st.write(data[duplicados]) # muestro el df de duplicados
    else:
        st.write("No hay siniestros duplicados según las columnas seleccionadas.")
else:
    st.write("Seleccione al menos una columna para hallar duplicados.")


# segunda sección
st.header('Descripción por Columna')
columna_seleccionada = st.selectbox('Seleccionar columna:', data.columns) # widget para seleccionar una columna

descripciones= {'anio_acci': 'Año en que ocurrió el siniestro.',
                'nro_acci': 'Contador de siniestros.',
                'fecha': 'Fecha exacta en que ocurrió el siniestro.',
                'desc_dia': 'Día de la semana en que ocurrió el siniestro.',
                'fecha_aprox': 'Fecha aproximada en que ocurrió el siniestro. (???)', 
                'hora_aprox': 'Hora aproximada en que ocurrió el siniestro.',
                'desc_ruta': 'Ruta en que ocurrió el siniestro.',
                'km': 'Número de kilómetro en que ocurrió el siniestro.',
                'cant_participantes': 'Cantidad de participantes en el siniestro.',
                'desc_participante': 'Modo/s involucrado/s en el siniestro.',
                'calle_avenida_km': 'Lugar en que ocurrió el siniestro.',
                'total': 'Total de personas participantes en el siniestro.',
                'heridos_leves': 'Cantidad de heridos leves participantes en el siniestro.',
                'heridos_graves': 'Cantidad de heridos graves participantes en el siniestro.',
                'heridos_gravisimos': 'Cantidad de heridos gravísimos participantes en el siniestro.',
                'ilesos': 'Cantidad de ilesos participantes en el siniestro.', 
                'fallecidos': 'Cantidad de fallecidos en el siniestro.',
                'sin_datos':  'Cantidad de personas involucradas en el siniestro que no se pudieron catalogar en las anteriores (ilesos, heridos, fallecidos).', 
                'posicion_XY': 'Coordenadas donde ocurrió el siniestro.',
                'desc_tipo_via': 'Tipo de vía donde ocurrió el siniestro.',
                'desc_ruta_ori': 'Descripción de la ruta de origen.', 
                'desc_loc': 'Municipio en que ocurrió el siniestro.',
                'desc_dpto': 'Departamento en que ocurrió el siniestro.',
                'desc_tipo_calzada': 'Tipo de calzada en que ocurrió el siniestro.',
                'desc_tipo_banquina': 'Tipo de banquina en que ocurrió el siniestro.',
                'desc_unidad_regional': 'Unidad regional en que ocurrió el siniestro.',
                'desc_lugar_calzada': 'Lugar de la calzada en que ocurrió el siniestro.',
                'desc_zona': 'Tipo de zona en que ocurrió el siniestro.', 
                'desc_prioridad': 'Descripción de prioridad, si existiera.', 
                'desc_estado_semaforo': 'Estado del semáforo al momento del siniestro.',
                'desc_lugar_via': 'Lugar de la vía en que ocurrió el siniestro.', 
                'desc_estado_via': 'Estado de la vía al momento del siniestro.', 
                'desc_estado_visibilidad': 'Estado de visibilidad de la vía al momento del siniestro.', 
                'desc_luminosidad': 'Estado de luminosidad al momento del siniestro.', 
                'desc_estado_clima': 'Estado del clima al momento del siniestro.',
                'desc_tipo_colision': 'Tipo de colisión involucrada en el siniestro.', 
                'desc_tipo_atropello': 'Tipo de atropello involucrado en el siniestro.',
                'desc_tipo_hecho': 'Tipo de siniestro.',
                'desc_pres_calzada': 'Estado de la calzada al momento del siniestro.',
                'desc_senializacion': 'Estado de la señalización al momento del siniestro.', 
                'desc_separacion_via': 'Tipo de separación de la vía, si existiera.', 
                'desc_restriccion': 'Descripción de la restricción involucrada en el siniestro, si existiera. Si tiene separadores físicos o no, imposibilidad de movimientos, etc.'} 

columns = st.columns(2)
if columna_seleccionada:
    # en la primer columna, descripción de la variable, cuadro de estadísticas y cuadro de valores nulos por año.
    with columns[0]:
        st.write("**Descripción:** ", descripciones[columna_seleccionada])
        
        traducciones = {
            'count': 'Total',
            'mean': 'Media',
            'std': 'Desviación Estándar',
            'min': 'Valor Mínimo',
            'max': 'Valor Máximo',
            'unique': 'Valores únicos',
            'top': 'Moda',
            'freq': 'Frecuencia'
        }

        if columna_seleccionada != 'nro_acci': # filtro nro_acci porque no tiene sentido estadísticas para esta columna
            estadisticas_basicas = data[columna_seleccionada].describe().rename(traducciones)
            if columna_seleccionada in ['anio_acci', 'fecha_aprox', 'km']: # excluir algunas estadísticas para estas columnas porque no tienen sentido
                estadisticas_basicas.drop(['Media', '25%', '50%', '75%', 'Desviación Estándar'], inplace=True)
        
            st.write("**Estadísticas básicas:**")
            st.write(estadisticas_basicas.T) # muestro cuadro de estadísticas
    
        contador_nulos = data.groupby('anio_acci')[columna_seleccionada].apply(lambda x: x.isna().sum()) # cantidad total de nulos
        total_counts = data.groupby('anio_acci').size()  # total de siniestros por año
        
        nulos = pd.DataFrame({
            'Año': contador_nulos.index,
            'Valores Nulos': contador_nulos.values,
            'Total Siniestros': total_counts.values
        })
        
        nulos['Porcentaje'] = (nulos['Valores Nulos'] / nulos['Total Siniestros']) * 100  # calculo porcentajes de nulos
        nulos['Porcentaje'] = nulos['Porcentaje'].round(2).apply(lambda x: f"{x}%")  # redondeo a dos decimales y agrego '%'
        st.write("**Valores nulos por año:**")
        st.write(nulos.set_index('Año').T) # muestro cuadro de nulos

    # en la segunda columna, muestro algún gráfico que represente a la variable
    with columns[1]:
        if columna_seleccionada != 'nro_acci': # filtro nro_acci porque no tiene sentido graficarlo
            if columna_seleccionada == 'anio_acci':
                # para la columna de los años, grafico una línea de tiempo
                df_anio_acci = data['anio_acci'].value_counts().sort_index().reset_index()
                df_anio_acci.columns = ['anio_acci', 'count']
                fig = px.line(df_anio_acci, x='anio_acci', y='count', 
                            title='Cantidad de valores por año')
                fig.update_layout(title_x=0.25, yaxis_title='Cantidad de valores', showlegend=False)
                st.plotly_chart(fig)

            else:
                anios_disponibles = sorted(data['anio_acci'].unique())
                anio_seleccionado = st.select_slider('Seleccionar año: ', options=anios_disponibles) # slider para seleccionar el año
                data_filtrados = data[data['anio_acci'] == anio_seleccionado] # dataset filtrado según el año seleccionado
                
                if columna_seleccionada == 'posicion_XY':
                    # si la columna es posicion_XY muestro un mapa con las coordenadas, si el df contiene información
                    if anio_seleccionado in range(2011, 2021):
                        def extraer_coordenadas(coordenada):
                            '''Recibe coordenadas y extrae la latitud y la longitud'''
                            if isinstance(coordenada, str):
                                latitud, longitud = coordenada.split(',')
                                return float(latitud), float(longitud)
                            else:
                                return None, None
                        
                        data_filtrados['Latitud'], data_filtrados['Longitud'] = zip(*data_filtrados['posicion_XY'].apply(extraer_coordenadas))
                        data_filtrados = data_filtrados.dropna(subset=['Latitud', 'Longitud'])
                        
                        if data_filtrados.empty:
                            st.warning('No se encuentra información sobre la columna "posicion_XY" para el año seleccionado.')
                        else:
                            fig = px.scatter_mapbox(data_filtrados, 
                                                    lat='Latitud', 
                                                    lon='Longitud', 
                                                    title=f'Localización geográfica de siniestros para el año {anio_seleccionado}',
                                                    zoom=10,
                                                    color_discrete_sequence=['red'])
                            fig.update_layout(title_x=0.25, mapbox_style="open-street-map")
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning('No se encuentra información sobre la columna "posicion_XY" para el año seleccionado.')
                
                elif columna_seleccionada in ['desc_participante', 'hora_aprox']:
                    # top 10 valores más comunes para 'desc_participante' o 'hora_aprox'
                    top_10 = data_filtrados[columna_seleccionada].value_counts().nlargest(10).reset_index()
                    top_10.columns = [columna_seleccionada, 'count']
                    fig = px.bar(top_10, x=columna_seleccionada, y='count', 
                                title=f'Top 10 valores más frecuentes de {columna_seleccionada} para el año {anio_seleccionado}', 
                                text='count')
                    fig.update_layout(title_x=0.25, yaxis_title='Cantidad de valores', showlegend=False)
                    fig.update_traces(textposition='outside')
                    st.plotly_chart(fig, use_container_width=True)

                elif columna_seleccionada == 'fecha':
                    # para la columna fecha, línea de tiempo
                    data_filtrados['fecha'] = pd.to_datetime(data_filtrados['fecha'])
                    df_fecha = data_filtrados['fecha'].value_counts().sort_index().reset_index()
                    df_fecha.columns = ['fecha', 'count']
                    
                    fig = px.line(df_fecha, x='fecha', y='count', 
                                title=f'Cantidad de valores únicos para el año {anio_seleccionado}')
                    fig.update_layout(title_x=0.25, yaxis_title='Cantidad de valores', showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
            
                elif columna_seleccionada == 'km':
                    # para la columna km, agrego widget para seleccionar la ruta
                    rutas = data_filtrados['desc_ruta'].unique().tolist()
                    ruta_seleccionada = st.selectbox("Selecciona una ruta para visualizar", rutas)
                    data_filtrada = data_filtrados[data_filtrados['desc_ruta'] == ruta_seleccionada]
                    if not data_filtrada.empty:
                        fig_hist = px.histogram(data_filtrada, x='km', nbins=10, title=f'Distribución de Siniestros por Kilómetro en {ruta_seleccionada}')
                        fig_hist.update_layout(title_x=0.25, xaxis_title='Kilómetro', yaxis_title='Cantidad de Siniestros')
                        st.plotly_chart(fig_hist, use_container_width=True)

                    else:
                        st.write("No hay datos para la ruta seleccionada.")

                elif pd.api.types.is_numeric_dtype(data_filtrados[columna_seleccionada]):
                    # para el resto de las columnas numéricas, un histograma
                    fig = px.histogram(data_filtrados, x=columna_seleccionada, 
                                    title=f'Cantidad de valores únicos para el año {anio_seleccionado}', 
                                    text_auto=True, range_y=[0, max(data_filtrados[columna_seleccionada])+500])
                    fig.update_layout(title_x=0.30, yaxis_title='Cantidad de valores', showlegend=False)
                    fig.update_traces(textposition='outside')
                    fig.update_xaxes(tickmode='linear', dtick=1)
                    st.plotly_chart(fig, use_container_width=True)

                else:
                    # para el resto de las columnas categóricas, un gráfico de barras
                    value_counts = data_filtrados[columna_seleccionada].value_counts().reset_index()
                    value_counts.columns = [columna_seleccionada, 'count']
                    
                    fig = px.bar(value_counts, x=columna_seleccionada, y='count', 
                                title=f'Cantidad de valores únicos para el año {anio_seleccionado}', 
                                text='count', range_y=[0, max(value_counts['count'])+500])
                    fig.update_layout(title_x=0.30, yaxis_title='Cantidad de valores', showlegend=False)
                    fig.update_traces(textposition='outside')
                    st.plotly_chart(fig, use_container_width=True)

# tercera sección
st.header("Comparación columna 'Total' y suma de involucrados")
st.markdown("Histograma y scatterplot con el fin de comparar los valores de la columna *total* y la suma de *heridos_leves*, *heridos_graves*, *heridos_gravisimos*, *ilesos* y *fallecidos*.")
columns = st.columns(2)

data['diferencias_totales'] = data[['heridos_leves', 'heridos_graves', 'heridos_gravisimos', 'ilesos', 'fallecidos']].sum(axis = 1) - data.total
fig = px.histogram(data, x = 'diferencias_totales', 
                   labels = {'diferencias_totales': 'Diferencias'}, 
                   title='Histograma de diferencias')
fig.update_yaxes(title_text='Cantidad de siniestros') # etiqueta eje y
fig.update_layout(title_x=0.35)
columns[0].plotly_chart(fig)

data['suma_involucrados'] = data[['heridos_leves', 'heridos_graves', 'heridos_gravisimos', 'ilesos', 'fallecidos']].sum(axis = 1)
fig = px.scatter(data, x='total', y='suma_involucrados', 
                 labels={'total': 'Total', 'suma_involucrados': 'Suma de Involucrados'}, 
                 title='Total vs Suma de Involucrados')
fig.update_layout(title_x=0.35)
columns[1].plotly_chart(fig)

# cuarta sección
st.header("Siniestros sin localización geográfica")


columns = st.columns(2)
data_final = pd.read_csv("siniestros_geocod_rosario.csv") # cargo el df con las geocodificaciones
data_final = data_final[data_final['anio_acci'] != 2011] # filtro el único siniestro de 2011 infiltrado en el csv del 2012
nulos_por_año = data_final.groupby('anio_acci')['lat'].apply(lambda x: x.isnull().mean() * 100).reset_index()
nulos_por_año.columns = ['Año', 'Porcentaje de siniestros']
nulos_por_año.set_index('Año', inplace=True)
nulos_por_año['Porcentaje de siniestros'] = nulos_por_año['Porcentaje de siniestros'].round(2).astype(str) + '%'
columns[0].text("\n\n\n")
columns[0].markdown("**Porcentaje de siniestros que no pudieron ser localizados geográficamente:**")
columns[0].dataframe(nulos_por_año.T)

categorias_especificas = ['ppal calles no encontradas', 'sec calles no encontradas', 'ambas calles no encontradas', 'chequear', 'error']
data_final['forma_geocod'] = data_final['forma_geocod'].apply(lambda x: x if x in categorias_especificas else 'geocodificado')

forma_geocod_counts = data_final['forma_geocod'].value_counts().reset_index()
forma_geocod_counts.columns = ['Resultados', 'Cantidad de siniestros']
mapeo_categorias = {
    'ppal calles no encontradas': 'Calle principal no encontrada',
    'sec calles no encontradas': 'Calle secundaria no encontrada',
    'ambas calles no encontradas': 'Ambas calles no encontradas',
    'chequear': 'Chequear',
    'error': 'Error',
    'geocodificado': 'Geocodificado'
}
forma_geocod_counts['Resultados'] = forma_geocod_counts['Resultados'].map(mapeo_categorias)
columns[0].markdown("**Cantidad total de siniestros según los resultados de su geocodificación:**")
columns[0].dataframe(forma_geocod_counts)
fig = px.bar(forma_geocod_counts, y='Cantidad de siniestros', x='Resultados',  title='Resultados de la geocodificación de siniestros',   range_y=[0, 35000], text='Cantidad de siniestros')
fig.update_layout(title_x=0.25)
fig.update_traces(textposition='outside')
columns[1].plotly_chart(fig)
