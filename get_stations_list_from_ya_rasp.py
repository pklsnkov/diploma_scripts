'''
Скрипт для загрузки списка всех доступных ж/д станций в Яндекс Расписаниях
'''

import requests
import json

from config import YANDEX_SHEDULE_API_KEY as API_KEY

link = f'https://api.rasp.yandex.net/v3.0/stations_list/?apikey={API_KEY}&lang=ru_RU&format=json'
r = requests.get(link)
ya_rasp_stations = json.loads(r.text)

stations_data = []
for country in ya_rasp_stations['countries']:
     if country['title'] == 'Россия':
          for region in country['regions']:
               current_region = region['title']
               stations_in_region = []
               for settlement in region['settlements']:
                    for station in settlement['stations']:
                         if station['transport_type'] == 'train':
                              stations_in_region.append(station)
               stations_data.append({
                    'region': current_region,
                    'stations': stations_in_region
               })
          
with open('Database\\stations_from_ya_rasp.json', 'w', encoding='utf-8') as file:
     json.dump(stations_data, file, ensure_ascii=False, indent=5)
print('Дамп сделан')