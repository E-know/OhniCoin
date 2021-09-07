import os
import jwt
import uuid
import hashlib
from urllib.parse import urlencode
import os
import jwt
import uuid
from multiprocessing import Process, Pipe
import requests


class order:
	__access_key = os.environ['UPBIT_OPEN_API_ACCESS_KEY']
	__secret_key = os.environ['UPBIT_OPEN_API_SECRET_KEY']
	__server_url = os.environ['UPBIT_OPEN_API_SERVER_URL']
	
	
	def __new__(cls, *args, **kwargs):
		if not hasattr(cls, "_instance"):
			print("order class instance is created")
			cls._instance = super().__new__(cls)
		return cls._instance
	
	def __init__(self):
		print("order class __init__ is called")
	
	'''
	market : 마켓 이름
	side : bid-매수/ ask-매도
	volume 주문량
	price 주문가격
	order_type limit-지정가 주문/ price-시장가 매수 /market - 시장가 매도
	'''
	def order_coin(self, market, side, volume, price, ord_type):
		query = {
			'market': market,
			'side': side,
			'volume': volume,
			'price': price,
			'ord_type': ord_type,  # limit - 지정가 주문 / price - 시장가 매수 / market - 시장가 매도
		}
		
		query_string = urlencode(query).encode()
		
		m = hashlib.sha512()
		m.update(query_string)
		query_hash = m.hexdigest()
		
		payload = {
			'access_key': self.__access_key,
			'nonce': str(uuid.uuid4()),
			'query_hash': query_hash,
			'query_hash_alg': 'SHA512',
		}
		
		jwt_token = jwt.encode(payload, self.__secret_key)
		authorize_token = 'Bearer {}'.format(jwt_token)
		headers = {"Authorization": authorize_token}
		
		response = requests.post(self.__server_url + "/v1/orders", params=query, headers=headers)
		if response.status_code != 201:
			print(market, side, volume, price, ord_type, response.json()['error']['message'])
		return response
