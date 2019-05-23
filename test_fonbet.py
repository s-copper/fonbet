from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import requests


URL = 'https://www.fonbet.ru/#!/products/addresses'

ALL_CLUBS = []

YM_API_KEY = ''

YM_API_URL = 'https://search-maps.yandex.ru/v1/?text=Фонбет, {city}, {addr}&type=biz&lang=ru_RU&results=1&apikey={api_key}'


def get_all_addresses(city):
    title_city = city.text
    city.click()
    addresses = wait.until(EC.visibility_of_all_elements_located(
            (By.XPATH, './/div[@class="addr__aside"]//div[@class="addrList__wrap"]/div[@class="addrList__item"]/a')
        ))
    for addr in addresses:
        title_addr = addr.text
        url_api = YM_API_URL.format(city=title_city, addr=title_addr, api_key=YM_API_KEY)
        ALL_CLUBS.append(get_response(url_api))


def get_response(url):
    club = {}
    response = requests.Session().get(url)
    features = response.json().get('features')[0]
    club['lonlat'] = features.get('geometry').get('coordinates')
    companymetadata = features.get('properties').get('CompanyMetaData')
    club['addr'] = companymetadata.get('address')
    club['name'] = companymetadata.get('name')
    _phones = companymetadata.get('Phones')
    phones = []
    for phone in _phones:
        phones.append(phone.get('formatted'))
    club['phones'] = phones
    return club


# start = time.time()

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')

driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
driver.get(URL)

wait = WebDriverWait(driver, 10)

element_iframe = wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'products-page-iframe')))

# ymap = wait.until(EC.visibility_of_element_located((By.XPATH, './/ymaps[@class="ymaps-2-1-73-map"]')))

btn_cities = wait.until(EC.element_to_be_clickable((By.XPATH, './/div[@class="addr"]//a[@class="btn _selected"]')))
btn_cities.click()

cities = wait.until(EC.presence_of_all_elements_located((By.XPATH, './/div[@class="cityChoiceList__item"]/a')))

for city in cities:
    get_all_addresses(city)
    wait.until(EC.element_to_be_clickable((By.XPATH, './/div[@class="addr"]//a[@class="btn _selected"]')))
    btn_cities.click()


ALL_CLUBS = json.dumps(ALL_CLUBS)

with open('test_rocketdata.txt', 'w') as t_rock:
    t_rock.write(ALL_CLUBS)

# print(time.time()-start)
