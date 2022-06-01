import requests
from bs4 import BeautifulSoup
import argparse
import random
from pprint import pprint


def get_marca_model(placa):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
    proxies = get_free_proxies()

    endpoints = ['https://www.ipvabr.com.br/placa/', 'https://placafipe.com/placa/', 'https://www.tabelafipebrasil.com/placa/', 'https://placaipva.com.br/placa/']

    endpoint_idx = random.randint(0, len(endpoints) - 1)

    page = requests.get(endpoints[endpoint_idx]+'%s' % placa, headers=headers)

    while page.status_code != 200:
        try:
            proxy_idx = random.randint(0, len(proxies) - 1)
            
            proxy = {"http": proxies[proxy_idx], "https": proxies[proxy_idx]}
            page = requests.get(endpoints[endpoint_idx]+'%s' % placa, headers=headers, proxies=proxy, timeout=1)
            print(f"Proxy currently being used: {proxy['https']}")
            break
        except:
            print("Error, looking for another proxy")

    soup = BeautifulSoup(page.text, 'html.parser')

    car_details = dict()

    for row in soup.find("table").find_all("tr"):
        tds = row.find_all("td")

        try:
            key = tds[0].text.strip()
            value = tds[1].text.strip()
            car_details[key] = value
        except IndexError:
            continue

    return car_details


def get_free_proxies():
    url = "https://free-proxy-list.net/"
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
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
    parser.add_argument("--placa", help="Placa do veiculo", type=str, required=True)
    args = parser.parse_args()

    json = get_marca_model(args.placa)
    pprint(json)
