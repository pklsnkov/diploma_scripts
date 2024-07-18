'''
Алгоритмы для выгрузки железнодорожной сети и поездов через OverPassAPI
'''

import geopandas as gpd
import requests
from shapely.geometry import Point, LineString
import json
import os

def download_railway():
     overpass_api_base_url = "https://overpass-api.de/api/interpreter?data="
     data_url = '''
          [out:json][timeout:20000];
          area[name="Россия"]->.searchArea;
          way["railway"="rail"]["usage"="main"](area.searchArea);
          out geom;
     '''
     overpass_response = requests.get(f"{overpass_api_base_url}{data_url}")
     if overpass_response.status_code == 200:
          response_json = overpass_response.json()
          geoms_json = response_json['elements']
          lines = []
          for geom_json in geoms_json:
               geometry = geom_json['geometry']
               points = [Point(data['lon'], data['lat']) for data in geometry]
               line = LineString(points)
               lines.append(line)
          gdf = gpd.GeoDataFrame(geometry=lines)
          gdf.to_file('railway.geojson', driver='GeoJSON')

def download_trains_from_osm():
     overpass_api_base_url = "https://overpass-api.de/api/interpreter?data="
     data_url = '''
          [out:json][timeout:20000];
          area[name="Россия"]->.searchArea;
          relation["route"="train"](area.searchArea);
          out geom;
     '''
     overpass_response = requests.get(f"{overpass_api_base_url}{data_url}")
     if overpass_response.status_code == 200:
          trains = []
          response_json = overpass_response.json()
          trains_json = response_json['elements']
          for train_json in trains_json:
               tags = train_json['tags']
               members = train_json['members']
               stops_info = []
               try:
                    service = tags['service']
                    if service == 'regional':
                         continue
               except:
                    pass
               for member in members:
                    if member['type'] == 'node':
                         stops_info.append(member)
               trains.append({
                    'info': tags,
                    'stops_info': stops_info
               })
          json_trains = json.dumps(trains, indent=5, ensure_ascii=False)
          with open(os.path.join("D:\\4 курс\\diploma_code\\Database","trains.json"), "w", encoding="UTF-8") as json_file:
               json_file.write(json_trains)