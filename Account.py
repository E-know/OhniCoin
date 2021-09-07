from pykson import JsonObject, IntegerField, StringField, ObjectField, FloatField, Pykson
import os
import jwt
import uuid
import hashlib
from urllib.parse import urlencode
import requests
from Order import order

class user_Info:
	coins = {}
	ORDER = order()
	t = 0
	
	def __new__(cls, *args, **kwargs):
		if not hasattr(cls, "_instance"):  # Foo 클래스 객체에 _instance 속성이 없다면
			print("User Info Instance is Create")
			cls._instance = super().__new__(cls)  # Foo 클래스의 객체를 생성하고 Foo._instance로 바인딩
		
		return cls._instance  # Foo._instance를 리턴
	
	def __init__(self):
		print("unser_Info Class __init__")
		
		self.set_user_info()
		self.__print_user_info()
	
	def set_user_info(self):
		access_key = os.environ['UPBIT_OPEN_API_ACCESS_KEY']
		secret_key = os.environ['UPBIT_OPEN_API_SECRET_KEY']
		server_url = os.environ['UPBIT_OPEN_API_SERVER_URL']
		
		payload = {
			'access_key': access_key,
			'nonce': str(uuid.uuid4()),
		}
		
		jwt_token = jwt.encode(payload, secret_key)
		authorize_token = 'Bearer {}'.format(jwt_token)
		headers = {"Authorization": authorize_token}
		
		response = requests.get(server_url + "/v1/accounts", headers=headers)
		
		for ele in response.json():
			item = coin(ele)
			self.coins.update({ele['currency']: coin(ele)})
	
	def __print_user_info(self):
		if len(self.coins) <= 0:
			print('ACCOUNT-user_Info-print_user_info] USER INFO IS EMPTY')
			return
		print('===========================계좌 현황===========================')
		krw = self.coins['KRW']
		print('KRW] %f 원' % krw.balance)
		
		for key in self.coins:
			if key != 'KRW':
				print('%s] %f %s' % (key, self.coins[key].balance, key))
		print('===============================================================')
		
	def get_order(self):
		return self.ORDER

class coin(JsonObject):
	def __init__(self, item):
		self.currency = item['currency']
		self.balance = float(item['balance'])
		self.avg_buy_price = item['avg_buy_price']
