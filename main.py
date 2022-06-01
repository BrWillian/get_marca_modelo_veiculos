import requests
from bs4 import BeautifulSoup
import re
import random


def get_marca_model(placa):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
    proxies = get_free_proxies()

    page = requests.get('https://placafipe.com/placa/%s' % placa, headers=headers)

    while page.status_code != 200:
        try:
            proxy_idx = random.randint(0, len(proxies) - 1)
            proxy = {"http": proxies[proxy_idx], "https": proxies[proxy_idx]}
            page = requests.get('https://placafipe.com/placa/%s' % placa, headers=headers, proxies=proxy, timeout=1)
            print(f"Proxy currently being used: {proxy['https']}")
            break
        except:
            print("Error, looking for another proxy")

    soup = BeautifulSoup(page.text, 'html.parser')

    tokens = soup.select('tr td')

    marca = re.compile('Marca:')

    modelo = re.compile('Modelo:')
    marca_str = None
    modelo_str = None

    for idx, token in enumerate(tokens):
        result = marca.match(token.get_text())

        if result:
            marca_str = tokens[idx + 1].get_text()
            break

    for idx, token in enumerate(tokens):
        result = modelo.match(token.get_text())

        if result:
            modelo_str = tokens[idx + 1].get_text()
            break

    marca_str = re.sub("[^A-Za-z0-9]+", "_", marca_str)

    modelo_str_crop = modelo_str.split(' ')[:2]
    modelo_str = '_'.join(modelo_str_crop)

    return marca_str + '_' + modelo_str


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
    result = get_marca_model('jhw6773')
    print(result)
