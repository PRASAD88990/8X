import streamlit as st
import requests
import json
import pandas as pd
from math import radians, sin, cos, sqrt, atan2

@st.cache(ttl=3600)  # cache for 1 hour
def download_json_data(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)
    return filename

def load_and_parse_json(filename):
    data = []
    with open(filename, 'r') as f:
        for line in f:
            try:
                data.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"Error parsing line: {e}")  # Log any errors encountered
    return data


def display_hotels(hotels):
    for _, row in hotels.iterrows():
        st.write(f"Name: {row['name']}")
        st.write(f"Address: {row['address']}, {row['city']}, {row['state']}, {row['postal_code']}")
        st.write(f"Rating: {row['stars']} stars")
        st.write(f"Distance: {row['distance_km']:.2f} km")
        st.write("-" * 40)

def display_restaurants(restaurants):
    for _, row in restaurants.iterrows():
        st.write(f"Name: {row['name']}")
        st.write(f"Address: {row['address']}, {row['city']}, {row['state']}, {row['postal_code']}")
        st.write(f"Rating: {row['stars']} stars")
        st.write(f"Distance: {row['distance_km']:.2f} km")
        st.write("-" * 40)

def main():
    url = "https://www.dropbox.com/scl/fi/9lzttqolt0ojmdiian81r/yelp_academic_dataset_business.json?rlkey=0xz2qnm491hudpfspdcfmr4uo&dl=1"
    filename = "yelp_academic_dataset_business.json"
    data = download_json_data(url,filename)
    business_data_list = load_and_parse_json(filename) 
    business_data = pd.DataFrame(business_data_list)

    hotels = business_data[(business_data['categories'].str.contains('Hotels', na=False))]

    def has_r(row):
        try:
            attributes = row['attributes']
            if attributes is not None and isinstance(attributes, dict):
                return 'RestaurantsPriceRange2' in attributes
            else:
                return False
        except (KeyError, TypeError):
            return False

    hotels_w = hotels[hotels.apply(has_r, axis=1)]
    hotels_w = hotels_w[~hotels_w['categories'].str.contains('Transport|Distilleries', na=False, case=False)]

    restaurants = business_data[business_data['categories'].str.contains('Restaurants', na=False)]

    def haversine(lat1, lon1, lat2, lon2):
        R = 6371.0
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c

    if st.button("take Sample location cordinates from here or any coordinates of a location within any cities"):
        st.write("Kenner, LA: 29.9941° N, 90.2417° W New Orleans, LA: 29.9511° N, 90.0715° W Kennett Square, PA: 39.8465° N, 75.7113° W Tucson, AZ: 32.2226° N, 110.9747° W Saint Louis, MO: 38.6270° N, 90.1994° W Philadelphia, PA: 39.9526° N, 75.1652° W Nashville, TN: 36.1627° N, 86.7816° W Madeira Beach, FL: 27.7986° N, 82.7977° W Santa Barbara, CA: 34.4208° N, 119.6982° W Reno, NV: 39.5296° N, 119.8138° W Terra Ceia, FL: 27.5767° N, 82.5667° W  Spring Hill, TN: 35.7512° N, 86.9300° W Eagle, ID: 43.6951° N, 116.3548° W Tampa Bay, FL: 27.9642° N, 82.4526° W Bellmawr, NJ: 39.8676° N, 75.0943° W Indianapolis, IN: 39.7684° N, 86.1581° W  Tampa, FL: 27.9506° N, 82.4572° W Cahokia, IL: 38.5709° N, 90.1882° W Newark, DE: 39.6837° N, 75.7497° W Treasure Island, FL: 27.7697° N, 82.7687° W Lutz, FL: 28.1511° N, 82.4615° W  Berkeley, CA: 37.8715° N, 122.2730° W West Chester, PA: 39.9607° N, 75.6065° W Mount Holly, NJ: 39.9937° N, 74.7874° W Abington, PA: 40.1220° N, 75.1199° W Franklin, TN: 35.9251° N, 86.8689° W  Sparks, NV: 39.5349° N, 119.7527° W Deptford, NJ: 39.8312° N, 75.1199° W Whitestown, IN: 39.9970° N, 86.3450° W Smyrna, TN: 35.9820° N, 86.5186° W Saint Petersburg, FL: 27.7676° N, 82.6403° W  Columbus, OH: 39.9612° N, 82.9988° W")

    st.title("put your coordinates  here")
    st.title("Hotel Suggestions Based on Location")
    lat = st.number_input("Enter Latitude", value=36.1699)
    lon = st.number_input("Enter Longitude", value=115.1398)
    lon= -lon
    radius_km = st.slider("Search Radius (km)", 1, 20, 10)
    st.title("Restaurant Finder by Cuisine")
    st.write("select type like Thai , Italian , Chinese, japanese")
    cuisine_type = st.text_input("Enter Cuisine Type", "Italian")

    if st.button("Search"):
        st.write("Below are the hotels:")
        nearby_hotels = hotels_w[hotels_w.apply(lambda row: haversine(lat, lon, row['latitude'], row['longitude']) <= radius_km, axis=1)]
        nearby_hotels['distance_km'] = nearby_hotels.apply(lambda row: haversine(lat, lon, row['latitude'], row['longitude']), axis=1)
        display_hotels(nearby_hotels.head(50))  # display only 50 hotels
        filtered_restaurants = restaurants[restaurants['categories'].str.contains(cuisine_type, case=False, na=False)]
        filtered_restaurants['distance_km'] = filtered_restaurants.apply(
    lambda row: haversine(lat, lon, row['latitude'], row['longitude']) <= radius_km, axis=1)
        st.write("\n")
        st.write("-" * 50)
        st.write("\n")

        st.write("Below are the restaurants:")
        display_restaurants(nearby_hotels.head(50))

if __name__ == "__main__":
    main()
