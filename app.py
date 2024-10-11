def calcular_aqi(pm25):
    if pm25 <= 12:
        aqi = (50/12) * pm25
    elif pm25 <= 35.4:
        aqi = ((100 - 51)/(35.4 - 12.1)) * (pm25 - 12.1) + 51
    elif pm25 <= 55.4:
        aqi = ((150 - 101)/(55.4 - 35.5)) * (pm25 - 35.5) + 101
    elif pm25 <= 150.4:
        aqi = ((200 - 151)/(150.4 - 55.5)) * (pm25 - 55.5) + 151
    elif pm25 <= 250.4:
        aqi = ((300 - 201)/(250.4 - 150.5)) * (pm25 - 150.5) + 201
    elif pm25 <= 350.4:
        aqi = ((400 - 301)/(350.4 - 250.5)) * (pm25 - 250.5) + 301
    elif pm25 <= 500.4:
        aqi = ((500 - 401)/(500.4 - 350.5)) * (pm25 - 350.5) + 401
    else:
        aqi = None
    return round(aqi, 2) if aqi is not None else None

def obtener_recomendacion(aqi):
    if aqi <= 50:
        return 'Bueno - No hay riesgo.'
    elif aqi <= 100:
        return 'Moderado - Grupos sensibles deben considerar limitar esfuerzos prolongados al aire libre.'
    elif aqi <= 150:
        return 'Insalubre para grupos sensibles - Evitar esfuerzos al aire libre.'
    elif aqi <= 200:
        return 'Insalubre - Todos deben limitar esfuerzos al aire libre.'
    elif aqi <= 300:
        return 'Muy insalubre - Evitar actividades al aire libre.'
    elif aqi <= 500:
        return 'Peligroso - Emergencia sanitaria.'
    else:
        return 'Datos no disponibles.'

def color_aqi(aqi):
    if aqi <= 50:
        return 'green'
    elif aqi <= 100:
        return 'yellow'
    elif aqi <= 150:
        return 'orange'
    elif aqi <= 200:
        return 'red'
    elif aqi <= 300:
        return 'purple'
    elif aqi <= 500:
        return 'maroon'
    else:
        return 'gray'

try:
    url = "https://siata.gov.co/EntregaData1/Datos_SIATA_Aire_AQ_pm25_Last.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        df = pd.json_normalize(data['measurements'])
    else:
        print(f"Error al descargar el archivo: {response.status_code}")

    df = df[['coordinates.latitude', 'coordinates.longitude', 'value', 'date.local']]

    df['date.local'] = pd.to_datetime(df['date.local'])

    # Fecha del filtrado
    fecha = "2024-09-04"
    hora = "17:00:00"

    # Filtrar por la fecha y la hora
    df_filtrado = df[(df['date.local'].dt.date == pd.to_datetime(fecha).date()) &
                     (df['date.local'].dt.time == pd.to_datetime(hora).time())]

    #buscamos valores correctos
    df_filtrado = df_filtrado[df_filtrado['value'].between(0, 500)]

    #AQI
    df_filtrado['AQI'] = df_filtrado['value'].apply(calcular_aqi)
    df_filtrado['color'] = df_filtrado['AQI'].apply(color_aqi)
    df_filtrado['reomendacion']= df_filtrado['AQI'].apply(obtener_recomendacion)
    

    #Obtenemos los valores de latitud y longitud
    coordenadas = df_filtrado[['coordinates.latitude', 'coordinates.longitude']].values
    valor_aqi = df_filtrado['AQI'].values


    # Crear malla e interpolación
    grid_x, grid_y = np.mgrid[
        df_filtrado['coordinates.latitude'].min():df_filtrado['coordinates.latitude'].max():100j,
        df_filtrado['coordinates.longitude'].min():df_filtrado['coordinates.longitude'].max():100j
    ]

    grid_z0 = griddata(coordenadas, valor_aqi, (grid_x, grid_y), method='cubic')

    # Rangos AQI
    aqi_categories = [
      (0, 50, 'green'),
      (51, 100, 'yellow'),
      (101, 150, 'orange'),
      (151, 200, 'red'),
      (201, 300, 'red'),
      (301, 500, 'maroon')
    ]

    # Calcular los valores normalizados
    aqi_colorscale = []
    for aqi_min, aqi_max, color in aqi_categories:
      norm_min = (aqi_min - 0) / 500
      norm_max = (aqi_max - 0) / 500
      aqi_colorscale.append([norm_min, color])
      aqi_colorscale.append([norm_max, color])

    # Eliminar duplicados y ordenar
    aqi_colorscale = sorted(list(set(tuple(item) for item in aqi_colorscale)))
    
    # Obtener recomendaciones para los valores interpolados
    recomendaciones = [obtener_recomendacion(aqi) for aqi in grid_z0.flatten()]

    # Interpolacion en el mapa de calor
    fig = go.Figure()
    
    fig.add_trace(go.Densitymapbox(
        lat=grid_x.flatten(),
        lon=grid_y.flatten(),
        z=grid_z0.flatten(),
        radius=10,
        opacity=0.5,
        zmin=0,
        zmax=500,
        colorscale=aqi_colorscale,
        hoverinfo="lon+lat+z+text",
        text=recomendaciones
    ))

    #Puntos reales de los sensores al gráfico de Mapbox 
    fig.add_trace(go.Scattermapbox(
        lat=coordenadas[:, 0],
        lon=coordenadas[:, 1],
        mode='markers',
        marker=dict(
            size=8,
            color=valor_aqi,
            colorscale=aqi_colorscale,
            cmin=0,
            cmax=500,
        ),
       text=df_filtrado['reomendacion'],
       hoverinfo='text'
    ))

    # Estilo del mapa
    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_center_lat=df_filtrado['coordinates.latitude'].mean(),
        mapbox_center_lon=df_filtrado['coordinates.longitude'].mean(),
        mapbox_zoom=8,
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )

    server = flask.Flask(__name__)

    app = dash.Dash(server=server, routes_pathname_prefix="/")

    app.layout = html.Div([
        html.H1("Calidad del Aire en Medellín"),
        dcc.Graph(figure=fig, id="Mapa_interpolacion"),
    ])

    if __name__ == '__main__':
        app.run_server(debug=True, use_reloader=False, host='0.0.0.0', port=80)

except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
