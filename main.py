import requests
from bs4 import BeautifulSoup
import re


def get_marca_model(placa):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
    page = requests.get('https://placafipe.com/placa/%s' % placa, headers=headers)
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

    return marca_str+'_'+modelo_str


if __name__ == "__main__":
    result = get_marca_model('pjj9889')
    print(result)
