import re
import requests
from bs4 import BeautifulSoup
import argparse
import random
from pprint import pprint
import json
import os
import shutil
from anpr import DataTrafficOCR

def get_free_proxies():
    url = "https://www.sslproxies.org/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
    soup = BeautifulSoup(requests.get(url, headers=headers).content, "html.parser")
    proxies = []
    for row in soup.find("table").find_all("tr")[1:]:
        tds = row.find_all("td")
        try:
            ip = tds[0].text.strip()
            port = tds[1].text.strip()
            host = f"{ip}:{port}"
            proxies.append(host)
        except IndexError:
            continue

    return proxies

def get_marca_model(placa, proxies):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
    
    print(proxies)
    endpoints = ['https://www.ipvabr.com.br/placa/', 'https://placafipe.com/placa/', 'https://www.tabelafipebrasil.com/placa/', 'https://placaipva.com.br/placa/']

    #page = requests.get(endpoints[endpoint_idx]+'%s' % placa, headers=headers)
    contador = 0
    while True:
        try:
            proxy_idx = random.randint(0, len(proxies) - 1)
            endpoint_idx = random.randint(0, len(endpoints) - 1)
            
            proxy = {"http": proxies[proxy_idx], "https": proxies[proxy_idx]}
            page = requests.get(endpoints[endpoint_idx]+'%s' % placa, headers=headers, proxies=proxy, timeout=1)

            print(endpoints[endpoint_idx]+'%s' % placa)
            print(page.status_code, endpoints[endpoint_idx])
            print(f"Proxy currently being used: {proxy['https']}")

            if page.status_code == 200:
                break

        except:
            proxies.pop(proxy_idx)
            print("Error, looking for another proxy")

    soup = BeautifulSoup(page.text, 'html.parser')

    car_details = dict()

    try:

        for row in soup.find("table").find_all("tr"):
            tds = row.find_all("td")

            try:
                key = tds[0].text.strip()
                value = tds[1].text.strip()
                car_details[key] = value
            except IndexError:
                continue
    except:
        print("Placa invalída!")

    return car_details


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--placa", help="Placa do veiculo", type=str, required=False)
    parser.add_argument("--dir", help="Pasta de imagens", type=str, required=False)
    args = parser.parse_args()

    LIB_PATH = 'lib'

    proxies = get_free_proxies()

    ocr = DataTrafficOCR('generated', LIB_PATH, mask='???/????', on_weights=False)

    for root, _, files in os.walk(args.dir):
        for file in files:
            img_path = os.path.join(root+file)
            
            val = ocr.ocr(img_path)
            
            result = json.loads(val)

            print(len(proxies))

            if len(proxies) == 1:
                proxies = get_free_proxies()

            if len(result['result']) > 1:
                #print(get_free_proxies())
                json_result = get_marca_model(str(result['result']), proxies)
                pprint(json_result)
                try:
                    marca = json_result["Marca:"].replace(" ", "_")
                    modelo = json_result["Modelo:"].replace(" ", "_")
                    new_dir = "/home/willian/Pictures/marca_modelo/"+marca+"_"+modelo+"/"
                    os.makedirs(new_dir, exist_ok=True)
                    shutil.move(img_path, new_dir)
                    print(marca, modelo)
                except:
                    continue