import requests
import time
import os
import jwt
import uuid
import hashlib
from urllib.parse import urlencode

ave1_std = 10
ave2_std = 60
order_waiting_time = 60


def get_volume(price):
	volume = 5500 / price
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
	
	querystring = {"market": market, "count": ave2_std}
	
	headers = {"Accept": "application/json"}
	
	response = requests.request("GET", url, headers=headers, params=querystring)
	
	return response.json()


def get_average_And_price(market):
	candles = get_market_candle(market)
	ave1 = ave2 = 0
	for i, candle_data in enumerate(candles):
		if i < ave1_std:
			ave1 += candle_data['trade_price']
		ave2 += candle_data['trade_price']
	
	ave1 /= ave1_std
	ave2 /= ave2_std
	
	return ave1, ave2, candles[0]['trade_price']


def wait_order(order_id):
	access_key = os.environ['UPBIT_OPEN_API_ACCESS_KEY']
	secret_key = os.environ['UPBIT_OPEN_API_SECRET_KEY']
	server_url = os.environ['UPBIT_OPEN_API_SERVER_URL']
	
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
	# 주문 확인
	for i in range(order_waiting_time):
		res = requests.get(server_url + "/v1/order", params=query, headers=headers)
		# done wait cancel
		if res.json()['state'] == 'done':
			return 'done'
		time.sleep(1)
	
	# 1분동안 주문이 체결 안되면 주문 취소후 miss 반환
	while True:
		res = requests.delete(server_url + "/v1/order", params=query, headers=headers)
		if res.json()['state'] == 'done':
			return 'miss'
		time.sleep(0.5)


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
	order_id = res.json()['uuid']
	
	return wait_order(order_id)


def analyze_market(market, user):
	coin = market[4:]
	time_sec = 60
	was_under = False
	while True:
		ave1, ave2, price = get_average_And_price(market)
		if user.have_coin(coin):
			if (buy_price - price) * 0.9995 > 0 or (buy_price - price) / buy_price < -0.03:
				# SELL
				state = order_coin(market, 'ask', volume, price, 'limit')
				if state == 'done':
					user.take_out_coin_from_wallet(market, volume)
					earn = (buy_price - price) * 0.9995 * volume
					print('Sell %s %f Earn %f' % (market, volume, earn), end=' ')
					user.plus_total(earn)
					was_under = False
					time_sec = 60
				elif state == 'miss':
					print('miss selling %s' % market)
				else:
					print(market, sys.argv[0], 'sell function is wrong')
		else:
			if ave1 > ave2 and was_under:
				# buy
				price = get_one_bid_price(price)
				volume = get_volume(price)
				state = order_coin(market, 'bid', volume, price, 'limit')
				if state == 'done':
					user.add_coin_to_wallet(market, volume, price)
					buy_price = price
					time_sec = 10
					print('Buy %s Price %f Volume %f' % (market, price, volume))
				elif state == 'miss':
					print('miss buying %s' % market)
				else:
					print(market, sys.argv[0], 'buy function is wrong')
			
			was_under = ave1 < ave2
		print('%s Price %f %d이평선 : %f %d이평선 %f ave1 > ave2 : %s / was_under : %s [Final %s]' % (market, price, ave1_std, ave1, ave2_std, ave2, (ave1 > ave2), was_under, was_under and (ave1 > ave2)))
		time.sleep(time_sec)
