import sys
import requests
import json
import data_type
from time import time

import get_dtp




VIN = 'X89195230B0CK6158' # VIN, который можно менять
id = {'history': ['vehicle', 'ownershipPeriods'],
      'dtp': 'Accidents',
      'wanted': 'records',
      'restrict': 'records',
      'diagnostic': 'diagnosticCards'}
car = {}

# проверка на длину
if len(VIN) != 17:
    print('Неправильно введёный VIN номер.')
    sys.exit()

def get_data(url, key):
    headers = {
        'Accept': 'application / json, text / javascript, * / *; q = 0.01',
        'Accept - Encoding': 'gzip, deflate, br',
        'Accept - Language': 'ru,en;q=0.9,ko;q=0.8',
        'Connection': 'keep - alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 YaBrowser/21.11.1.932 Yowser/2.5 Safari/537.36'
    }
    params = {
        'vin': VIN,
        'checkType': key
    }

    req = requests.post(url=url, headers=headers, params=params)

    while req.json().get('RequestResult') == None:
        req = requests.post(url=url, headers=headers, params=params)

# проверка на правильность номера
#     if req.json().get('RequestResult') == None:
#         print('Такого VIN номера не существует.')
#         sys.exit()

# запрос по регистрации
    if key == 'history':
        d_register = req.json()["RequestResult"][id[key][0]]
        p_register = req.json()["RequestResult"][id[key][1]]['ownershipPeriod']

        if d_register.get('engineNumber') == None:
            d_register['engineNumber'] = '-'
            d_register['engineVolume'] = '-'

        car['registr'] = {
            'model': d_register['model'],
            'year': d_register['year'],
            'color': d_register['color'],
            'VIN': VIN,
            'numberEngine': d_register['engineNumber'],
            'workingVol': d_register['engineVolume'],
            'power': d_register['powerHp'],
            'type_car': data_type.auto_types[d_register['type']]
        }
        car['period'] = []
        for num in p_register:
            if num.get('to') == None:
                num['to'] = 'настоящее время'

            car['period'].append({
                'date_from': num['from'],
                'date_to': num['to'],
                'typePerson': data_type.type_owner[num['simplePersonType']],
                'last_oper': data_type.typeOperation[num['lastOperation']]
            })

# запрос по дтп
    elif key == 'dtp':
        d_dtp = req.json()["RequestResult"][id[key]]
        car['dtp'] = []
        for num in d_dtp:
            car['dtp'].append({
                'number_dtp': num['AccidentNumber'],
                'time_dtp': num['AccidentDateTime'],
                'type_dtp': num['AccidentType'],
                'place_dtp': num['AccidentPlace'],
                'model_dtp': num['VehicleMark'],
                'dmp_dtp': num['DamagePoints'],
                'way_image': get_dtp.svgtopng(num['DamagePoints']),
            })
        if len(car['dtp']) == 0 :
            car['dtp'].append('По указанному VIN номеру не найдено данных')

# запрос по розыску
    elif key == 'wanted':
        d_wanted = req.json()["RequestResult"][id[key]]
        car['wanted'] = []
        for num in d_wanted:
            car['wanted'].append({
                'model_w': num['w_model'],
                'year_w': num['w_god_vyp'],
                'data_w': num['w_data_pu'],
                'region_w': num['w_reg_inic']
            })
        if len(car['wanted']) == 0:
            car['wanted'].append('По указанному VIN номеру не найдено данных')

# запрос по ограничениям
    elif key == 'restrict':
        d_limit = req.json()["RequestResult"][id[key]]
        car['limit'] = []
        for num in d_limit:
            car['limit'].append({
                'date_l': num['dateogr'],
                'region_l': num['regname'],
                'organ_l': data_type.organs[num['divtype']],
                'type_l': data_type.ogr[num['ogrkod']],
                'osnov_l': num['osnOgr'],
                'phone_l': num['phone'],
                'KeyGID_l': num['gid']
            })
        if len(car['limit']) == 0:
            car['limit'].append('По указанному VIN номеру не найдено данных')

# запрос по диагностике
    elif key == 'diagnostic':
        d_diagnostic = req.json()["RequestResult"][id[key]]
        car['diagnostic'] = []
        for num in d_diagnostic:
            car['diagnostic'].append({
                'number_dc': num['dcNumber'],
                'date_dc': num['dcDate'],
                'date_end_dc': num['dcExpirationDate'],
                'addres_dc': num['pointAddress'],
                'brand_dc': num['brand'],
                'model_dc': num['model'],
                'odometr_dc': num['odometerValue']
            })
        if len(car['diagnostic']) == 0:
            car['diagnostic'].append('По указанному VIN номеру не найдено данных')

# сохраняет полученные данные в json
        with open("data.json", "w") as file:
            json.dump(car, file, indent=4, ensure_ascii=False)
# тест вывода в консоль (можно убрать)
        #print(car)

# время обработки всего запроса (можно убрать)
    print(f"[INFO] Обработал страницу {key}")


def main():
    for key in id.keys():
        get_data("https://xn--b1afk4ade.xn--90adear.xn--p1ai/proxy/check/auto/{0}".format(key), key)


if __name__ == '__main__':
    t0 = time()
    main()
    print(time() - t0)