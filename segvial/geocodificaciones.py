import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
import time

pd.set_option('display.max_columns', None)

data = pd.read_csv("data_final.csv")
data = data[data['desc_dpto']=='Rosario'].copy()

data['forma_geocod'] = np.nan # Columna nueva con todos nulos
data['geo_incorrecta'] = np.nan # Columna nueva con todos nulos

# Si la direccion ya estaba geocodificada (años 2019 y 2020) --> defino forma_geocod como existente y guardo lat y lon en una nueva columna
data.loc[data['posicion_XY'].notnull(), 'forma_geocod'] = 'existente'
data.loc[data['posicion_XY'].notnull(), 'lat'] = data.loc[data['posicion_XY'].notnull(), 'posicion_XY'].apply(lambda x: float(x.split(',')[0]))
data.loc[data['posicion_XY'].notnull(), 'lon'] = data.loc[data['posicion_XY'].notnull(), 'posicion_XY'].apply(lambda x: float(x.split(',')[1]))

# Separo los accidentes en ruta y los accidentes en ciudad
accidentes_ruta = data[data['desc_ruta'].notna() | data['calle_avenida_km'].str.contains('ruta|km|kilometro|autopista|autovia', case=False, na=False)].copy()
accidentes_ciudad = data[~data.index.isin(accidentes_ruta.index)].copy()

# De los accidentes en ciudad --> filtro aquellas direcciones con intersecciones
filtro_interseccion = accidentes_ciudad['calle_avenida_km'].str.contains(' y | entre | e | casi ', case=False, na=False)
intersecciones = accidentes_ciudad[filtro_interseccion].copy()
data2geocode = accidentes_ciudad[~filtro_interseccion].copy()
assert (len(intersecciones) + len(data2geocode)) == len(accidentes_ciudad)

# Elijo un año para trabajar y lo filtro del dataset.
anio = 2012
data_2012 = data2geocode[data2geocode['anio_acci'] == anio].copy()

# Geocodificar
geolocator = Nominatim(user_agent="mi-aplicacion")
data_subset_2012 = data_2012.head(50)

for index, row in data_subset_2012.iterrows():
    if pd.isna(row['forma_geocod']):

        direccion = f"{row['calle_avenida_km']}, {row['desc_loc']}, {row['desc_dpto']} Santa Fe, Argentina"

        # Si algun dato es nulo
        if pd.isna(row['calle_avenida_km']) or pd.isna(row['desc_loc']) or pd.isna(row['desc_dpto']):
            data_subset_2012.loc[index, 'sin_info_geo'] = direccion
            continue

        try:
            location = geolocator.geocode(direccion)
            if location:
                latitud = location.latitude
                longitud = location.longitude
                data_subset_2012.loc[index, 'lat'] = latitud
                data_subset_2012.loc[index, 'lon'] = longitud
                data_subset_2012.loc[index, 'forma_geocod'] = 'nominatim'
            else:
                data_subset_2012.loc[index, 'geo_incorrecta'] = direccion

        except Exception as e:
            print(f"Error en la geolocalización para la fila {index}: {e}")
            data_subset_2012.loc[index, 'errores'] = direccion
    else:
        # Si 'forma_geocod' no es nulo, pasa al siguiente registro del DataFrame
        continue

    time.sleep(1)

data_subset_2012.to_csv('test_geocode.csv')
