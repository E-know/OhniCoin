import requests
import time
import os, sys
import jwt
import uuid
import hashlib
from urllib.parse import urlencode

ave1_std = 5
ave2_std = 30
ave3_std = 60
order_waiting_time = 60 * 2
want_to_buy_price = 5500
limit_minus = -0.02
limit_plus = want_to_buy_price * 0.01


def get_volume(price):
	volume = want_to_buy_price / price
	return volume


def get_one_bid_price(price):
	if price < 10:
		return price - 0.01
	elif price < 100:
		return price - 0.1
	elif price < 1000:
		return price - 1
	elif price < 10000:
		return price - 5
	elif price < 100000:
		return price - 10
	elif price < 500000:
		return price - 50
	elif price < 1000000:
		return price - 100
	elif price < 2000000:
		return price - 500
	else:
		return price - 1000


def get_market_candle(market):
	url = "https://api.upbit.com/v1/candles/minutes/1"
	
	querystring = {"market": market, "count": ave3_std}
	
	headers = {"Accept": "application/json"}
	
	response = requests.request("GET", url, headers=headers, params=querystring)
	if response.status_code == 200:
		return response.json()
	else:
		print(sys.argv[0], 'in get_market_candle', response.text)
		return 'miss'


def get_average_And_price(market):
	candles = get_market_candle(market)
	if candles == 'miss':
		print('miss Candle')
		return 'miss', 'miss', 'miss', 'miss'
	ave1 = ave2 = ave3 = 0
	for i, candle_data in enumerate(candles):
		if i < ave1_std:
			ave1 += candle_data['trade_price']
		if i < ave2_std:
			ave2 += candle_data['trade_price']
		ave3 += candle_data['trade_price']
	
	ave1 /= ave1_std
	ave2 /= ave2_std
	ave3 /= ave3_std
	
	
	return ave1, ave2, ave3, candles[0]['trade_price']


def cancel_order(order_id):
	access_key = os.environ['UPBIT_OPEN_API_ACCESS_KEY']
	secret_key = os.environ['UPBIT_OPEN_API_SECRET_KEY']
	server_url = os.environ['UPBIT_OPEN_API_SERVER_URL']
	
	query = {
		'uuid': order_id
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
	
	res = requests.delete(server_url + "/v1/order", params=query, headers=headers)


def wait_order(order_id):
	access_key = os.environ['UPBIT_OPEN_API_ACCESS_KEY']
	secret_key = os.environ['UPBIT_OPEN_API_SECRET_KEY']
	server_url = os.environ['UPBIT_OPEN_API_SERVER_URL']
	
	for i in range(order_waiting_time):
		query = {
			'uuid': order_id
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
		# 주문 확인
		res = requests.get(server_url + "/v1/order", params=query, headers=headers)
		if res.status_code == 200:
			if res.json()['state'] == 'done':
				return 'done'
		time.sleep(1)
	
	cancel_order(order_id)
	return 'miss'


def order_coin(market, side, volume, price, ord_type):
	'''
	:param market: 시장
	:param side: bid - 매수 / ask - 매도
	:param volume: 주문량
	:param price: 가격
	:param ord_type: limit-지정가 주문 / price-시장가 매수 / market-시장가 매도
	:return: done - 체결완료 / miss - 주문 실패
	'''
	access_key = os.environ['UPBIT_OPEN_API_ACCESS_KEY']
	secret_key = os.environ['UPBIT_OPEN_API_SECRET_KEY']
	server_url = os.environ['UPBIT_OPEN_API_SERVER_URL']
	
	query = {
		'market': market,
		'side': side,
		'volume': volume,
		'price': price,
		'ord_type': ord_type,
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
	
	res = requests.post(server_url + "/v1/orders", params=query, headers=headers)
	if res.status_code == 201:
		order_id = res.json()['uuid']
		return wait_order(order_id)
	else:
		print('ERROR', market, res.json()['error']['message'])  # 주문 금액이 부족합니다. # 주문가격 단위를 잘못 입력하셨습니다. 확인 후 시도해주세요.
		return 'miss'


def analyze_market(market, user):
	time_sec = 30
	coin = market[4:]
	was_under = False
	while True:
		ave1, ave2, ave3, price = get_average_And_price(market)
		# print('%s] %f %f %f %f || %s %s' % (market, price, ave1, ave2, ave3, ave2 < ave1 < ave3, was_under))
		if price == 'miss':
			print('%s - analyze_market] Missing Price')
			time.sleep(10)
			continue
		if user.have_coin(coin):
			coin_data = user.get_coin_info_from_wallet(coin)
			buy_price = float(coin_data['avg_buy_price'])
			volume = float(coin_data['balance'])
			time_sec = 10
			if (price * 0.9995 - buy_price * 1.0005) * volume > limit_plus or (price - buy_price) / buy_price < limit_minus:
				# SELL
				state = order_coin(market, 'ask', volume, price, 'limit')
				if state == 'done':
					earn = (price * 0.9995 - buy_price * 1.0005) * volume
					print('Sell %s Earn %f' % (market, earn))
					user.plus_total(earn)
					was_under = False
					time_sec = 30
					user.get_my_wallet()
				elif state == 'miss':
					print('miss selling %s' % market)
					user.get_wallet()
		else:
			if ave2 < ave1 < ave3 and was_under:
				# buy
				price = get_one_bid_price(price)
				volume = get_volume(price)
				state = order_coin(market, 'bid', volume, price, 'limit')
				if state == 'done':
					user.get_my_wallet()
					time_sec = 10
					print('Buy %s Price %f Volume %f' % (market, price, volume))
				elif state == 'miss':
					print('miss buying %s' % market)
					was_under = False
					continue
				else:
					print(market, sys.argv[0], 'buy function is wrong')
			
			was_under = ave1 < ave2
		
		time.sleep(time_sec)
