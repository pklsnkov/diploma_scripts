'''
Скрипт для использования инструмента QGIS для нахождения кратчайшего расстояния
'''

import os
import geopandas as gpd
import json
from shapely import wkt, LineString, MultiLineString
from qgis.core import QgsApplication, QgsProcessingFeedback, QgsVectorLayer
from qgis.analysis import QgsNativeAlgorithms

TRAINS_WITH_COORDS_PATH = 'Database\\trains_from_ya_rasp_with_coords.json'
TRAINS_WITH_GEOM_PATH = 'Database\\trains_with_geom.json'
RAILROAD_PATH = '/Geodata/RussiaFinalGeneralizedSplited.gpkg|layername=RussiaFinalGeneralizedSplited'

QgsApplication.setPrefixPath("C:/Program Files/QGIS 3.36.1/apps/qgis", True)
qgs = QgsApplication([], False)
qgs.initQgis()
import processing
from processing.core.Processing import Processing
Processing.initialize()

def get_graph_geom(start_point_info, end_point_info):
    res = processing.run("native:shortestpathpointtopoint", {
        'INPUT': RAILROAD_PATH,
        'STRATEGY': 0,
        'DIRECTION_FIELD': '',
        'VALUE_FORWARD': '',
        'VALUE_BACKWARD': '',
        'VALUE_BOTH': '',
        'DEFAULT_DIRECTION': 2,
        'SPEED_FIELD': '',
        'DEFAULT_SPEED': 50,
        'TOLERANCE': 0,
        'START_POINT': start_point_info,
        'END_POINT': end_point_info,
        'OUTPUT': 'TEMPORARY_OUTPUT'
    })

    output_layer = res['OUTPUT']
    features = list(output_layer.getFeatures())
    if features:
        geom = features[0].geometry()
        wkt = geom.asWkt()
        return wkt
    else:
        print("No features found in the output layer.")
        return None

def do_work():
    with open(TRAINS_WITH_GEOM_PATH, 'r', encoding='utf-8') as file:
        try:
            processed_trains = json.load(file)
            processed_trains_nums = []
            for processed_train in processed_trains:
                num = list(processed_train)[0]
                processed_trains_nums.append(num)
        except:
            processed_trains_nums = []
        
    trains_with_geom = processed_trains
    with open(TRAINS_WITH_COORDS_PATH, 'r', encoding='utf-8') as file:
        trains = json.load(file)
    
    for train_num, train_info in trains.items():
        if train_num in processed_trains_nums:
            print(f'Поезд {train_num} пропущен')
            continue
        stops = train_info['stops']
        geoms = []
        for i, stop in enumerate(stops):
            print(f'{i}/{len(stops)}')
            if i+1 < len(stops):
                try:
                    first_point_coords = stops[i]['coords']
                    second_point_coords = stops[i+1]['coords']
                except:
                    print('Точка пропущена')
                    continue
                
                if second_point_coords[0] == '' or second_point_coords[1] == '' or first_point_coords[0] == '' or first_point_coords[1] == '':
                    print(f'Не удалось обработать станцию')
                    continue
                
                first_point_info = f'{first_point_coords[1]},{first_point_coords[0]} [EPSG:4326]'
                second_point_info = f'{second_point_coords[1]},{second_point_coords[0]} [EPSG:4326]'
                wkt_geom = get_graph_geom(first_point_info, second_point_info)
                
                if wkt_geom:
                    geom = wkt.loads(wkt_geom)
                    geoms.append(geom)
                else:
                    print('')
        train_path = MultiLineString(geoms)
        wkt_path = train_path.wkt
        train_info['geom'] = wkt_path
        trains_with_geom.append({
            train_num: train_info
        })
        print(f'Сделан поезд {train_num}')
        with open(TRAINS_WITH_GEOM_PATH, 'w', encoding='utf-8') as file:
            json.dump(trains_with_geom, file, ensure_ascii=False, indent=5)
        
        # debug
        # gdf = gpd.GeoDataFrame(geometry=[train_path])
        # gdf.set_crs(epsg=4326, inplace=True)
        # gdf.to_file('output.gpkg', layer='multilinestring_layer', driver='GPKG')
        # break

    with open(TRAINS_WITH_GEOM_PATH, 'w', encoding='utf-8') as file:
        # file.write('')
        json.dump(trains_with_geom, file, ensure_ascii=False, indent=5)

do_work()
qgs.exitQgis()

