import requests
import time
from multiprocessing import Pipe
import os
import jwt
import uuid
import hashlib
from urllib.parse import urlencode

LIMIT_MONEY = 5500


def get_average(response):
	ave_5 = 0
	ave_60 = 0
	for i, ele in enumerate(response.json()):
		if i < 5:
			ave_5 += ele['trade_price']
		ave_60 += ele['trade_price']
	
	ave_5 /= 5
	ave_60 /= 60
	
	return ave_5, ave_60


def number_count(price):
	count = round(LIMIT_MONEY / price, 2)
	if LIMIT_MONEY <= count * price <= LIMIT_MONEY * 1.2:
		return count
	else:
		return count + 0.009  # TODO 더 정확하게 계산하기


def check_order(order_id):
	access_key = os.environ['UPBIT_OPEN_API_ACCESS_KEY']
	secret_key = os.environ['UPBIT_OPEN_API_SECRET_KEY']
	server_url = os.environ['UPBIT_OPEN_API_SERVER_URL']
	count = 0
	while True:
		query = {
			'uuid': order_id,
		}
		query_string = urlencode(query).encode()
		
		m = hashlib.sha512()
		m.update(query_string)
		query_hash = m.hexdigest()
		
		payload = {
			'access_key': access_key,
			'nonce': str(uuid.uuid4()),
			'query_hash': query_hash,
			'query_hash_alg': 'SHA512',
		}
		
		jwt_token = jwt.encode(payload, secret_key)
		authorize_token = 'Bearer {}'.format(jwt_token)
		headers = {"Authorization": authorize_token}
		
		response = requests.get(server_url + "/v1/order", params=query, headers=headers)
		
		if response.status_code == 200:
			response = response.json()
			if response['state'] == 'done':
				return response['state']
		elif response.status_code >= 400:
			print(response.json()['error']['message'])
		count += 1
		if count == 60:
			res = requests.delete(server_url + "/v1/order", params=query, headers=headers)
			# TODO 삭제 요청후 삭제 완료 되었는지 확인후에 함수 탈출하기
			return 'miss'
		time.sleep(1)


def watch_chart(user_info, market, total):
	url = "https://api.upbit.com/v1/candles/minutes/1"
	ORDER = user_info.get_order()
	
	querystring = {"market": market,
	               "count": 60}
	
	headers = {"Accept": "application/json"}
	
	have_coin = False
	buy_price = 0
	was_under = False
	timer_sec = 60
	while True:
		response = requests.request("GET", url, headers=headers, params=querystring)
		price = response.json()[0]['trade_price']
		
		ave_5, ave_60 = get_average(response)
		
		if have_coin:
			print(market, ']HAVE : Price %f buy_price %f volume %f earn %f percent %f' % (price, buy_price, volume, ((price - buy_price) - buy_price * 0.0005 - price * 0.0005) * volume, round((price - buy_price) / buy_price, 2)))
			if ((price - buy_price) - buy_price * 0.0005 - price * 0.0005) * volume > 0 or (price - buy_price) / buy_price <= -0.015:
				status = ORDER.order_coin(market, 'ask', volume, price, 'limit')
				if status.status_code == 201:
					if check_order(status.json()['uuid']) == 'done':
						earn = ((price - buy_price) - buy_price * 0.0005 - price * 0.0005) * volume
						total.value += earn
						have_coin = False
						was_under = False
						print(response.json()[0]['candle_date_time_kst'], market, ']SELL earn : %f total : %f' % (earn, total.value))
					elif check_order(status.json()['uuid']) == 'miss':
						print('Cancel sell order', market)
				else:
					print(response.json()[0]['candle_date_time_kst'], market, ']SELL ', status.json()['error']['message'])
		elif not have_coin:
			if was_under and ave_5 > ave_60:
				volume = number_count(price)
				status = ORDER.order_coin(market, 'bid', volume, price, 'limit')
				if status.status_code == 201:
					if check_order(status.json()['uuid']) == 'done':
						buy_price = price
						have_coin = True
						print(response.json()[0]['candle_date_time_kst'], market, 'BUYING ORDER COMPLETE', buy_price)
					elif check_order(status.json()['uuid']) == 'miss':
						print('Cancel buy order', market)
				else:
					print(response.json()[0]['candle_date_time_kst'], market, ']BUY ', status.json()['error']['message'])
			was_under = ave_5 < ave_60
		print(response.json()[0]['candle_date_time_kst'], market, ']현재가 : %d  60이평선: %f  5이평선: %f' % (price, ave_60, ave_5))
		time.sleep(timer_sec)

# TODO 내 자산목록에 코인이 있는지 없는지 확인후 판매
