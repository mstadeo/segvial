import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Calidad de datos", page_icon="📈", layout="wide")
st.title("Calidad de datos")

data_total = pd.read_csv("data_final.csv")
data = data_total[data_total['desc_dpto']=='Rosario'].copy()


st.markdown("El dataset cuenta con **{}** siniestros ocurridos entre los años 2012 y 2020 en la provincia de Santa Fe.".format(len(data_total)))
st.markdown("En total, **{}** de estos siniestros ocurrieron en el departamento de Rosario.".format(len(data)))


# FILA 1 --> HISTOGRAMA Y SCATTERPLOT COMPARACIÓN TOTAL Y SUMA DE INVOLUCRADO
st.subheader("Comparación columna 'Total' y suma de involucrados")
st.markdown("Histograma y scatterplot con el fin de comparar los valores de la columna *total* y la suma de *heridos_leves*, *heridos_graves*, *heridos_gravisimos*, *ilesos* y *fallecidos*.")
columns = st.columns(2)

data['diferencias_totales'] = data[['heridos_leves', 'heridos_graves', 'heridos_gravisimos', 'ilesos', 'fallecidos']].sum(axis = 1) - data.total
fig = px.histogram(data, x = 'diferencias_totales', 
                   labels = {'diferencias_totales': 'Diferencias'}, 
                   title='Histograma de diferencias')
fig.update_yaxes(title_text='Cantidad de siniestros') # etiqueta eje y
fig.update_layout(title_x=0.35, width=600)
columns[0].plotly_chart(fig)

data['suma_involucrados'] = data[['heridos_leves', 'heridos_graves', 'heridos_gravisimos', 'ilesos', 'fallecidos']].sum(axis = 1)
fig = px.scatter(data, x='total', y='suma_involucrados', 
                 labels={'total': 'Total', 'suma_involucrados': 'Suma de Involucrados'}, 
                 title='Total vs Suma de Involucrados')
fig.update_layout(title_x=0.35, width=600)
columns[1].plotly_chart(fig)


# FILA 2 --> CUADRO CON VALORES NULOS SEGÚN CATEGORÍA Y AÑO

st.subheader('Cantidad de valores nulos por año según categoría')
cuadro = pd.DataFrame()
for col in data.columns:
    if col != 'anio_acci': # agrupo cada columna (menos 'anio_acci') por año y cuento valores nulos
        data_agrupada = data.groupby(['anio_acci'])[col].apply(lambda x: x.isnull().sum()).reset_index()
        cuadro = pd.concat([cuadro, data_agrupada.set_index('anio_acci')], axis=1)
cuadro.drop('Unnamed: 0', axis=1, inplace=True)
st.table(cuadro)
