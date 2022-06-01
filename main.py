import re
import requests
from bs4 import BeautifulSoup
import argparse
import random
from pprint import pprint
import json
import os
from anpr import DataTrafficOCR


def get_marca_model(placa):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
    proxies = get_free_proxies()
    endpoints = ['https://www.ipvabr.com.br/placa/', 'https://placafipe.com/placa/', 'https://www.tabelafipebrasil.com/placa/', 'https://placaipva.com.br/placa/']

    #page = requests.get(endpoints[endpoint_idx]+'%s' % placa, headers=headers)

    while True:
        try:
            proxy_idx = random.randint(0, len(proxies) - 1)
            endpoint_idx = random.randint(0, len(endpoints) - 1)
            
            proxy = {"http": proxies[proxy_idx], "https": proxies[proxy_idx]}
            page = requests.get(endpoints[endpoint_idx]+'%s' % placa, headers=headers, proxies=proxy,timeout=5)

            print(endpoints[endpoint_idx]+'%s' % placa)
            print(page.status_code, endpoints[endpoint_idx])
            print(f"Proxy currently being used: {proxy['https']}")

            if page.status_code == 200:
                break

        except:
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


def get_free_proxies():
    url = "https://free-proxy-list.net/"
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--placa", help="Placa do veiculo", type=str, required=False)
    parser.add_argument("--dir", help="Pasta de imagens", type=str, required=False)
    args = parser.parse_args()

    LIB_PATH = 'lib'
    ocr = DataTrafficOCR('generated', LIB_PATH, mask='???/????', on_weights=False)

    for root, _, files in os.walk(args.dir):
        for file in files:
            img_path = os.path.join(root+file)
            
            val = ocr.ocr(img_path)
            
            result = json.loads(val)

            if len(result['result']) > 1:
                json_result = get_marca_model(str(result['result']))
                pprint(json_result)
