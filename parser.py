"""drgtdfg."""
from bs4 import BeautifulSoup

import requests

BASE_URL = 'https://dou.ua/'

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/70.0.3538.77 Safari/537.36"}
response = requests.get(BASE_URL, headers=headers)
soup = BeautifulSoup(response.text, 'lxml')

# print(soup)
