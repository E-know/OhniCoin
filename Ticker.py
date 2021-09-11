import requests
import sys
import time

minutes = 240
day = 1


def get_ticker(count=None):
	import requests
	
	url = "https://api.upbit.com/v1/market/all"
	
	querystring = {"isDetails": "false"}
	
	headers = {"Accept": "application/json"}
	
	response = requests.request("GET", url, headers=headers, params=querystring)
	'''
	https://docs.upbit.com/reference#%EC%9D%BCday-%EC%BA%94%EB%93%A4-1
	'''
	ticker = []
	print('Get Ticker from UPbit', end='')
	for i, json_data in enumerate(response.json()):
		if json_data['market'][:3] == 'KRW':
			candle = get_market_candle(json_data['market'])
			node = dict(candle[0])
			ticker.append(node)
		if i % 10 == 0:
			time.sleep(1.1)
			print('.', end='')
	
	print('DONE!')
	ticker.sort(key=lambda it: -it['change_rate'])
	
	return ticker if count is None else ticker[:count]


def get_market_candle(market):
	url = "https://api.upbit.com/v1/candles/days"
	
	querystring = {"count": "1", 'market': market}
	
	headers = {"Accept": "application/json"}
	
	response = requests.request("GET", url, headers=headers, params=querystring)
	
	return response.json()


