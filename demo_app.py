import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import plotly.express as px
from PIL import Image
from wordcloud import WordCloud
import folium
from streamlit_folium import folium_static

with st.echo(code_location='below'):
    st.title("Airbnb New York")
    st.write("All charts and maps are customizable by price to provide relevant information for your budget."
             " Please use a checkbox and a slider in the sidebar.")

    dt = pd.read_csv('AB_NYC_2019.csv', sep=',', decimal='.')
    dt = dt[dt['price'] > 0]

    agree = st.sidebar.checkbox('Show expensive options $750+')
    if agree:
        data = dt.copy()
    else:
        data = dt[dt['price'] <= 750]

    price_slider = st.sidebar.slider(
        'Select a price range',
        min(data['price']), max(data['price']), (100, 500)
    )

    data_by_price = data[data['price'] >= price_slider[0]]
    data_by_price = data_by_price[data_by_price['price'] <= price_slider[1]]


    st.write("## Room type boroughs map")
    st.write("If you're interested in a specific room type, here you can see how many suitable accommodation options "
             "are available in each borough.")
    st.write('*use a price slider and a select box to customize the chart *')
    room_selectbox = st.selectbox(
        'Choose a room type',
        (data['room_type'].unique())
    )
    room_data = data_by_price[data_by_price['room_type'] == room_selectbox]
    room_data['count'] = 1
    room_data = room_data.groupby("neighbourhood_group").sum()
    room_data.reset_index(level=0, inplace=True)

    st.write("*you can choose different map types for better orientation (upper right map corner)*")
    ny_map = folium.Map(location=[40.730610,-73.935242], min_zoom=10)
    folium.TileLayer('stamenwatercolor').add_to(ny_map)
    folium.TileLayer('Stamen Toner').add_to(ny_map)
    choropleth =folium.Choropleth(geo_data="Borough Boundaries.geojson",
                        fill_opacity=0.7, line_opacity=0.8,  data = room_data,
                        key_on='feature.properties.boro_name',
                        columns = ['neighbourhood_group', 'count'],
                        fill_color = 'RdPu', legend_name='Stay options available',
                        name="choropleth",
                        highlight=True,).add_to(ny_map)
    points = [[[40.86, -73.90], [40.86, -73.83]],
              [[40.66, -73.98], [40.66, -73.89]],
              [[40.72, -74.00], [40.80, -73.94]],
              [[40.72, -73.82], [40.72, -73.74]],
              [[40.59, -74.19], [40.59, -74.07]]]
    labels = ['BRONX', 'BROOKLYN', 'MANHATTAN', 'QUEENS', 'STATEN ISLAND']
    for point, label in zip(points, labels):
        line = folium.PolyLine(point, color='yellow', weight=2.5, opacity=0.1)
        attributes = {'fill': 'black', 'font-weight': 'bold', 'font-size': '11'}
        ny_map.add_child(line)
        folium.plugins.PolyLineTextPath(line, label, repeat=False, offset=0, attributes=attributes).add_to(ny_map)
    folium.LayerControl().add_to(ny_map)
    folium_static(ny_map)


    st.write("## Comparative price charts")
    st.write('Here you can compare the price distribution by room type in NY and its boroughs.'
             ' It can help you to understand whether the chosen borough is relatively cheap or expensive in NY')
    st.write('*use a price slider and a select box to customize the chart*')
    neighbourhood_selectbox = st.selectbox(
        'Choose a neighbourhood',
        (data['neighbourhood_group'].unique())
    )
    current_data = data_by_price[data_by_price['neighbourhood_group'] == neighbourhood_selectbox]
    fig, [x1, x2] = plt.subplots(1, 2, figsize=(15, 5),sharex=True)
    sns.histplot(data_by_price, ax=x1, x='price', hue='room_type',
                 hue_order=['Shared room', 'Private room', 'Entire home/apt'],
                 element="poly",
                 palette=[sns.color_palette("husl", 9)[1], sns.color_palette("husl", 9)[0],
                          sns.color_palette("husl", 9)[5]])\
        .set_title('Price distribution by room type in New York City')
    sns.histplot(current_data, ax=x2, x='price', hue='room_type',
                 hue_order=['Shared room', 'Private room', 'Entire home/apt'],
                 element="poly",
                 palette=[sns.color_palette("husl", 9)[1], sns.color_palette("husl", 9)[0],
                          sns.color_palette("husl", 9)[5]]) \
        .set_title('Price distribution by room type in ' + neighbourhood_selectbox)
    x1.set_xlabel('Price')
    x2.set_xlabel('Price')
    x1.set_ylabel('Number of options')
    x2.set_ylabel('Number of options')
    legend = x1.get_legend()
    handles = legend.legendHandles
    legend.remove()
    x1.legend(handles, ['Shared room', 'Private room', 'Entire home/apt'], title='Room type')
    legend = x2.get_legend()
    handles = legend.legendHandles
    legend.remove()
    x2.legend(handles, ['Shared room', 'Private room', 'Entire home/apt'], title='Room type')
    st.pyplot(fig)

    st.write("##  ")
    st.write('Here you can compare the price distribution in all boroughs to choose the most suitable one for your '
             'accommodation.')
    st.write('*use a price slider to customize the chart*')
    fig, x = plt.subplots()
    sns.violinplot(data=data_by_price, x='neighbourhood_group', y='price', palette=sns.color_palette("pastel"))\
        .set_title("Price distribution by boroughs")
    x.set_xlabel('Borough')
    x.set_ylabel('Price')
    st.pyplot(fig)


    st.write("## Availability and price map")
    st.write("Here you can see all options on the map to navigate better and to find out what locations are more or "
             "less pricey. Also here you can see what options may be available for your stay.")
    st.write('*use a price slider the availability option to customize the map*')
    days = st.number_input('Minimum days available (out of 365)', min_value=0, max_value=365, step=1)
    st.write('*hover to get more information*')
    map_data = data_by_price[data_by_price["availability_365"]>=days]
    fig, ax = plt.subplots()
    fig = px.scatter_mapbox(map_data, lat='latitude', lon='longitude', color="price", hover_name="room_type",
                            hover_data=["price","availability_365"],
                            color_continuous_scale=px.colors.sequential.Turbo, mapbox_style="stamen-terrain",
                            size_max=10, zoom=9)
    st.write(fig)

    st.write("##  Animated bar chart by the budget amount")
    st.write("Here you can see the dynamic of available options in all boroughs as your budget increases.")
    df = pd.DataFrame(columns=['Borough', 'Budget per day', 'number'])
    for neighbourhood in data['neighbourhood_group'].unique():
        for price in range(0, 760, 10):
            d = data[data['neighbourhood_group'] == neighbourhood]
            d = d[d['price'] <= price]
            new_row = {'Borough': neighbourhood, 'Budget per day': price, 'number': d.shape[0]}
            df = df.append(new_row, ignore_index=True)
    fig, ax = plt.subplots()
    fig = px.bar(df, x="Borough", y='number', color="Borough",
                animation_frame="Budget per day", animation_group="Borough", range_y=[0, max(df['number'])+1000],
                color_discrete_sequence=px.colors.qualitative.Plotly[5:10], labels={
                     "number": "Number of options"})

    st.write(fig)


    st.write("## Borough word cloud ")
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.write("To find out more about the place where you're going to live, let's see how Airbnb places are described"
             " in different boroughs.")
    borough_selectbox = st.selectbox(
        'Choose a borough',
        (data['neighbourhood_group'].unique())
    )
    boroughs_data = data[data['neighbourhood_group'] == borough_selectbox]
    fig, ax = plt.subplots()
    text = ''
    for word in boroughs_data['name']:
        text = text + " " + str(word)
    nyc_mask = np.array(Image.open('nyc.png'))
    ### FROM: (https://github.com/amueller/word_cloud/blob/master/examples/parrot.py)
    nyc_mask[nyc_mask.sum(axis=2) == 0] = 255
    ### END FROM
    stop = ['Private Room', 'Apartment', 'Bedroom apartment', 'bedroom', "in", "NYC", "Private", "Room", "bed", "with",
            'and', 'for', 'near', 'close to', 'mins to', 'Apt', 'the', 'a']
    fig = WordCloud(stopwords = stop, width=480, height=480, max_words=500, background_color="black", colormap="Blues",
                    mask=nyc_mask, contour_width=3, contour_color='white').generate(text)
    plt.imshow(fig, interpolation="bilinear")
    plt.axis("off")
    plt.margins(x=0, y=0)
    st.pyplot()









