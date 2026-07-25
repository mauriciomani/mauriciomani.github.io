import itertools
import folium
import streamlit as st
from streamlit_folium import st_folium
from geopy.distance import geodesic

st.set_page_config(page_title="Optimizador CDMX Pub Crawl Roma-Condesa", layout="wide")

RAW_PLACES = [
    [19.41437498848583, -99.16264590633796, "Roma Brewing"],
    [19.4121800550748, -99.16031394866505, "Cantaritos de la Roma"],
    [19.412357617195397, -99.1599402670451, "Falling Piano Brewing Co."],
    [19.419516369728, -99.16406866215532, "Pulqueria los insurgentes"],
    [19.412683965245318, -99.17256894495384, "La Santi Condesa"],
    [19.41618721145826, -99.16978317935698, "Drunkendog"],
    [19.41156468012848, -99.17354675844429, "Salon Malafama"],
    [19.416702624188893, -99.16669475844415, "Foro Bizarro"],
    [19.420321894960413, -99.16550637379012, "Cotorritos Cibeles"],
    [19.411718028226076, -99.17344700448238, "Tienda de cerveza Hercules"],
]

ALL_PLACES = [{"name": p[2], "coords": (p[0], p[1])} for p in RAW_PLACES]

def path_distance(path):
    total = 0.0
    for i in range(len(path) - 1):
        total += geodesic(path[i]["coords"], path[i + 1]["coords"]).meters
    return total

def find_best_route(start_place, other_places, k):
    best_dist = float("inf")
    best_path = None
    for subset in itertools.combinations(other_places, k - 1):
        for permutation in itertools.permutations(subset):
            full_path = (start_place,) + permutation
            dist = path_distance(full_path)
            if dist < best_dist:
                best_dist = dist
                best_path = full_path
    return best_dist, best_path

st.title("🍻 Optimizador Pub Crawl CDMX Roma-Condesa")

# Sidebar Controls
st.sidebar.header("Ajustes de ruta")

all_venue_names = [p["name"] for p in ALL_PLACES]

# Multiselect filter to pick candidate places
selected_venue_names = st.sidebar.multiselect(
    "Bares a considerar:",
    options=all_venue_names,
    default=all_venue_names
)

# Validate active selections
if len(selected_venue_names) < 2:
    st.warning("Por favor selecciona al menos dos lugares para generar una ruta.")
else:
    # Filter dataset based on multiselect
    active_places = [p for p in ALL_PLACES if p["name"] in selected_venue_names]
    
    # Starting Venue Selector
    selected_start_name = st.sidebar.selectbox(
        "Starting Venue:",
        options=selected_venue_names
    )
    
    # Total Stops Slider
    max_k = len(active_places)
    k_stops = st.sidebar.slider(
        "Total Stops to Visit:",
        min_value=2,
        max_value=max_k,
        value=min(4, max_k)
    )

    start_place = next(p for p in active_places if p["name"] == selected_start_name)
    remaining_places = [p for p in active_places if p["name"] != selected_start_name]

    # Calculate optimal route
    best_dist, best_path = find_best_route(start_place, remaining_places, k_stops)

    st.write(f"**Ruta optima:** {best_dist:.0f} metros totales en {k_stops} bares.")

    # Map Generation
    avg_lat = sum(p["coords"][0] for p in active_places) / len(active_places)
    avg_lon = sum(p["coords"][1] for p in active_places) / len(active_places)
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=15, tiles="cartodbpositron")

    # Plot candidate circles for selected places
    for p in active_places:
        folium.CircleMarker(
            location=p["coords"],
            radius=5,
            color="#2c3e50",
            fill=True,
            fill_color="#34495e",
            fill_opacity=0.6,
            tooltip=p["name"]
        ).add_to(m)

    # Connecting PolyLine
    route_coords = [p["coords"] for p in best_path]
    folium.PolyLine(
        locations=route_coords,
        color="#e74c3c",
        weight=5,
        opacity=0.85,
        tooltip=f"{best_dist:.0f} meters"
    ).add_to(m)

    # Numbered Badges for Stops
    for idx, p in enumerate(best_path, 1):
        folium.Marker(
            location=p["coords"],
            popup=f"<b>Stop {idx}:</b> {p['name']}",
            icon=folium.DivIcon(
                html=f"""<div style="font-size: 11pt; color: white; background: #e74c3c; 
                        border-radius: 50%; width: 28px; height: 28px; text-align: center; 
                        line-height: 28px; font-weight: bold; border: 2px solid white;
                        box-shadow: 0px 2px 5px rgba(0,0,0,0.3);">{idx}</div>"""
            )
        ).add_to(m)

    st_folium(m, width=900, height=500)
