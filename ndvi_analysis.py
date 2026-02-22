import ee
import pandas as pd
import matplotlib.pyplot as plt

# Inicializa a API do Google Earth Engine
ee.Initialize()

# 1. Define a Área de Interesse (AOI) - Exemplo: Pelotas, RS
# Coordenadas de um ponto central em Pelotas, RS
# Latitude: -31.7668, Longitude: -52.3448
# Buffer de 5000 metros para criar uma área circular
aoi = ee.Geometry.Point(-52.3448, -31.7668).buffer(5000)

# 2. Define o Período de Tempo
start_date = '2020-01-01'
end_date = '2023-12-31'

# 3. Carrega a Coleção de Imagens Sentinel-2
# Filtrar por data, limites da AOI e cobertura de nuvens
collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
    .filterDate(start_date, end_date) \
    .filterBounds(aoi) \
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10))

# Função para calcular o NDVI
def calculate_ndvi(image):
    # Renomear bandas para facilitar o cálculo
    red = image.select('B4')
    nir = image.select('B8')
    ndvi = nir.subtract(red).divide(nir.add(red)).rename('NDVI')
    return image.addBands(ndvi).copyProperties(image, ['system:time_start'])

# faz mapeamento da função NDVI sobre a coleção de imagens
ndvi_collection = collection.map(calculate_ndvi)

# 4. Extrai os valores médios de NDVI para a AOI
def reduce_region_mean(image):
    mean_dict = image.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=aoi,
        scale=10 # Resolução de 10 metros para Sentinel-2
    )
    return ee.Feature(None, {'NDVI': mean_dict.get('NDVI'), 'date': image.get('system:time_start')})

# Aplica a função de redução e converter para uma lista de features
ndvi_features = ndvi_collection.map(reduce_region_mean).getInfo()

# Processa os resultados para um DataFrame pandas
dates = []
ndvi_values = []

for f in ndvi_features:
    properties = f['properties']
    if properties['NDVI'] is not None:
        dates.append(pd.to_datetime(properties['date'], unit='ms'))
        ndvi_values.append(properties['NDVI'])

df = pd.DataFrame({"Date": dates, "NDVI": ndvi_values})
df = df.sort_values(by='Date').reset_index(drop=True)

# 5. Visualização da Série Temporal de NDVI
plt.figure(figsize=(12, 6))
plt.plot(df['Date'], df['NDVI'], marker='o', linestyle='-')
plt.title('Série Temporal de NDVI para a Área de Interesse (Pelotas, RS)')
plt.xlabel('Data')
plt.ylabel('NDVI')
plt.grid(True)
plt.tight_layout()
plt.savefig('ndvi_time_series.png')
plt.show()

print("Análise de NDVI concluída e gráfico salvo como 'ndvi_time_series.png'")
