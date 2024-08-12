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

    st.title("Hotel Suggestions Based on Location")
    lat = st.number_input("Enter Latitude", value=36.1699)
    lon = st.number_input("Enter Longitude", value=-115.1398)
    radius_km = st.slider("Search Radius (km)", 1, 20, 10)
    st.title("Restaurant Finder by Cuisine")
    cuisine_type = st.text_input("Enter Cuisine Type", "Italian")

    if st.button("Search"):
        st.write("Below are the hotels:")
        nearby_hotels = hotels_w[hotels_w.apply(lambda row: haversine(lat, lon, row['latitude'], row['longitude']) <= radius_km, axis=1)]
        nearby_hotels['distance_km'] = nearby_hotels.apply(lambda row: haversine(lat, lon, row['latitude'], row['longitude']), axis=1)
        display_hotels(nearby_hotels.head(50))  # display only 50 hotels

        st.write("\n")
        st.write("-" * 50)
        st.write("\n")

        st.write("Below are the restaurants:")
        for i in range(50):
            st.write(f"Restaurant {i+1}")

if __name__ == "__main__":
    main()
