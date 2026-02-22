# Análise de Séries Temporais de NDVI

## Monitoramento Automatizado da Vegetação Usando Imagens Sentinel-2 e Python

Este projeto demonstra a aplicação de sensoriamento remoto e programação Python para o monitoramento automatizado da vegetação através da análise de séries temporais do Índice de Vegetação por Diferença Normalizada (NDVI). Utiliza imagens do satélite Sentinel-2, processadas e analisadas com a API do Google Earth Engine (GEE), a biblioteca pandas para manipulação de dados e matplotlib para visualização.

## Objetivos

*   Desenvolver um script Python para acessar e processar imagens Sentinel-2 via Google Earth Engine.
*   Calcular o NDVI para uma área de interesse específica ao longo do tempo.
*   Gerar séries temporais de NDVI para monitorar mudanças na vegetação.
*   Visualizar as tendências do NDVI usando a biblioteca matplotlib.

## Metodologia

1.  **Coleta de Dados**: Utilização da API do Google Earth Engine para acessar coleções de imagens Sentinel-2 (Top of Atmosphere - TOA ou Bottom of Atmosphere - BOA, dependendo da aplicação específica e correção atmosférica necessária).
2.  **Pré-processamento**: Aplicação de filtros para seleção de imagens com baixa cobertura de nuvens e recorte para a área de estudo.
3.  **Cálculo do NDVI**: Implementação da fórmula do NDVI (NIR - RED) / (NIR + RED) para cada imagem na série temporal.
4.  **Extração de Dados**: Extração dos valores médios de NDVI para a área de interesse.
5.  **Análise de Séries Temporais**: Organização dos dados de NDVI em uma série temporal usando a biblioteca pandas.
6.  **Visualização**: Geração de gráficos de linha para exibir a variação do NDVI ao longo do tempo com matplotlib.

## Tecnologias Utilizadas

*   **Python**: Linguagem de programação principal.
*   **Google Earth Engine (GEE) API**: Plataforma de computação em nuvem para análise geoespacial.
*   **pandas**: Biblioteca para manipulação e análise de dados.
*   **matplotlib**: Biblioteca para criação de visualizações estáticas, animadas e interativas em Python.
*   **Sentinel-2**: Dados de satélite de média resolução espacial do programa Copernicus da Agência Espacial Europeia (ESA).

## Como Usar

1.  **Configuração do Ambiente**: Certifique-se de ter o Python instalado e as bibliotecas `earthengine-api`, `pandas` e `matplotlib` instaladas. Você pode instalá-las via pip:
    ```bash
    pip install earthengine-api pandas matplotlib
    ```
2.  **Autenticação no GEE**: Autentique-se na API do Google Earth Engine executando `earthengine authenticate` no seu terminal.
3.  **Execução do Script**: O script principal (`ndvi_analysis.py`) conterá o código para realizar a análise. Você precisará definir sua área de interesse e o período de tempo desejado.

## Exemplo de Código (ndvi_analysis.py)

```python
import ee
import pandas as pd
import matplotlib.pyplot as plt

# Inicializar a API do Google Earth Engine
ee.Initialize()

# 1. Definir a Área de Interesse (AOI) - Exemplo: Pelotas, RS
# Coordenadas de um ponto central em Pelotas, RS
# Latitude: -31.7668, Longitude: -52.3448
# Buffer de 5000 metros para criar uma área circular
aoi = ee.Geometry.Point(-52.3448, -31.7668).buffer(5000)

# 2. Definir o Período de Tempo
start_date = '2020-01-01'
end_date = '2023-12-31'

# 3. Carregar a Coleção de Imagens Sentinel-2
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

# Mapear a função NDVI sobre a coleção de imagens
ndvi_collection = collection.map(calculate_ndvi)

# 4. Extrair os valores médios de NDVI para a AOI
def reduce_region_mean(image):
    mean_dict = image.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=aoi,
        scale=10 # Resolução de 10 metros para Sentinel-2
    )
    return ee.Feature(None, {'NDVI': mean_dict.get('NDVI'), 'date': image.get('system:time_start')})

# Aplicar a função de redução e converter para uma lista de features
ndvi_features = ndvi_collection.map(reduce_region_mean).getInfo()

# Processar os resultados para um DataFrame pandas
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
```

## Contribuições

Sinta-se à vontade para contribuir com melhorias, correções de bugs ou novas funcionalidades. Por favor, abra uma *issue* ou envie um *pull request*.

## Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
