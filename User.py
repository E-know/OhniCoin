import os
import jwt
import uuid
import hashlib
from urllib.parse import urlencode
import requests
import json


class SingletonInstance:
	__instance = None
	
	@classmethod
	def __getInstance(cls):
		return cls.__instance
	
	@classmethod
	def instance(cls, *args, **kargs):
		cls.__instance = cls(*args, **kargs)
		cls.instance = cls.__getInstance
		return cls.__instance


class User(SingletonInstance):
	wallet = {}
	total = 0
	__access_key = os.environ['UPBIT_OPEN_API_ACCESS_KEY']
	__secret_key = os.environ['UPBIT_OPEN_API_SECRET_KEY']
	__server_url = os.environ['UPBIT_OPEN_API_SERVER_URL']
	
	def get_my_wallet(self):
		
		payload = {
			'access_key': self.__access_key,
			'nonce': str(uuid.uuid4()),
		}
		
		jwt_token = jwt.encode(payload, self.__secret_key)
		authorize_token = 'Bearer {}'.format(jwt_token)
		headers = {"Authorization": authorize_token}
		
		res = requests.get(self.__server_url + "/v1/accounts", headers=headers)
		self.wallet.clear()
		if res.status_code == 200:
			res = res.json()
			for json_data in res:
				self.wallet[json_data['currency']] = dict(json_data)
		else:
			print('ERROR]', sys.argv[0] + 'in User get_my_wallet')
			print(res.json()['error']['message'])
	
	def add_coin_to_wallet(self, market, volume, avg_buy_price):
		coin_name = market[4:]
		
		item = {'currency': coin_name,
		        'balance': volume,
		        'avg_buy_price': avg_buy_price
		        }
		
		if coin_name not in self.wallet:
			self.wallet[coin_name] = item
		else:
			print(sys.argv[0], 'User add_coin_to_wallet] Coin is already in wallet')
	
	def take_out_coin_from_wallet(self, market, volume):
		coin = market[4:]
		
		if coin in self.wallet:
			self.wallet.pop(coin)
		else:
			print(sys.argv[0], 'There is no coin in wallet')
	
	def have_coin(self, coin):
		return coin in self.wallet
	
	def plus_total(self, earn):
		self.total += earn
		print('Total %f' % self.total)
		
	def get_coin_info_from_wallet(self, coin):
		return self.wallet[coin]
	
	def get_wallet(self):
		return self.wallet
	
