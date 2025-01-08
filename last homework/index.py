import requests, json, os, sqlite3, time
from bs4 import BeautifulSoup
from tqdm import tqdm

city_codes = {
	"千代田区": 13101,
	"中央区": 13102,
	"港区": 13103,
	"新宿区": 13104,
	"文京区": 13105,
	"渋谷区": 13113,
	"台東区": 13106,
	"墨田区": 13107,
	"江東区": 13108,
	"荒川区": 13118,
	"足立区": 13121,
	"葛飾区": 13122,
	"江戸川区": 13123,
	"品川区": 13109,
	"目黒区": 13110,
	"大田区": 13111,
	"世田谷区": 13112,
	"中野区": 13114,
	"杉並区": 13115,
	"練馬区": 13120,
	"豊島区": 13116,
	"北区": 13117,
	"板橋区": 13119,
}

conn = sqlite3.connect('./rent_prices.db')
cur = conn.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS rent_prices(city TEXT, rent_price INTEGER)')

conn.commit()
conn.close()

for city in tqdm(city_codes):
	url = f"https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&ta=13&sc={city_codes[city]}&cb=0.0&ct=9999999&mb=0&mt=9999999&et=9999999&cn=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&sngz=&po1=25&pc=50"
	res = requests.get(url)
	res.encoding = res.apparent_encoding
	soup = BeautifulSoup(res.text, 'html.parser')

	pages = int(soup.find('ol', {'class': 'pagination-parts'}).find_all('li')[-1].text)
	for page in tqdm(range(1, 3)):
		res = requests.get(url + f"&page={page}")
		res.encoding = res.apparent_encoding
		soup = BeautifulSoup(res.text, 'html.parser')
		bukken_list = soup.find('div', {'id': 'js-bukkenList'})
		for bukken_blocks in tqdm(bukken_list.find_all('ul', {'class': 'l-cassetteitem'})):
			for bukken in bukken_blocks.find_all('li'):
				try:
					for cassetteitem in bukken.find('table', {'class': 'cassetteitem_other'}).find_all('tbody'):
						conn = sqlite3.connect('./rent_prices.db')
						cur = conn.cursor()
						rent_price = int(cassetteitem.find('span', {'class': 'cassetteitem_other-emphasis ui-text--bold'}).text[:-2])
						tqdm.write(f'{city} / {rent_price}')
						cur.execute(f'INSERT INTO rent_prices ("city", "rent_prices") VALUES ({city}, {rent_price});')
						conn.commit()
						conn.close()
				except:
					continue
	time.sleep(0.1)