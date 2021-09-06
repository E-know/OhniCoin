from pykson import JsonObject, IntegerField, StringField, ObjectListField, FloatField, Pykson
import requests
import time


class market_Info(object):
	tickers_dict = {}
	
	def __new__(cls, *args, **kwargs):
		if not hasattr(cls, "_instance"):  # Foo 클래스 객체에 _instance 속성이 없다면
			print("__new__ is called\n")
			cls._instance = super().__new__(cls)  # Foo 클래스의 객체를 생성하고 Foo._instance로 바인딩
		return cls._instance  # Foo._instance를 리턴
	
	def __init__(self):
		print("__init__ is called\n")
	
	def __called_ticker_value__(self):
		url = "https://api.upbit.com/v1/market/all"
		
		querystring = {"isDetails": "false"}
		
		headers = {"Accept": "application/json"}
		
		response = requests.request("GET", url, headers=headers, params=querystring)
		
		for ele in response.json():
			if ele['market'][:3] == 'KRW':
				self.tickers_dict.update({ele['market']: Pykson().from_json(ele, Ticker)})
	
	def __set_tickers_info__(self):
		if len(self.tickers_dict) == 0:
			print('ticker info is not called')
			self.__called_ticker_value__()
		
		print('Downloading Tickers Info', end='')
		
		url = "https://api.upbit.com/v1/candles/days"
		querystring = {"count": "1", 'market': ''}
		headers = {"Accept": "application/json"}
		ticker_list = []
		
		for i, key in enumerate(self.tickers_dict):
			querystring['market'] = self.tickers_dict[key].market
			response = requests.request("GET", url, headers=headers, params=querystring)
			# print(response.text)
			data = response.json()[0]
			
			self.tickers_dict[data['market']].change_rate = data['change_rate']
			self.tickers_dict[data['market']].candle_acc_trade_price = data['candle_acc_trade_price']
			self.tickers_dict[data['market']].trade_price = data['trade_price']
			
			if i % 7 == 0:
				print('.', end='')
				time.sleep(1.5)
		print()
	
	def get_sorted_ticker_by_value(self, count=None, minimum=None):
		self.__set_tickers_info__()
		
		ticker_list = []
		for key in self.tickers_dict:
			if minimum is None:
				ticker_list.append(self.tickers_dict[key])
			elif self.tickers_dict[key].trade_price >= minimum:
				ticker_list.append(self.tickers_dict[key])
		
		ticker_list.sort(key=lambda it: -it.change_rate)
		
		return ticker_list if count is None else ticker_list[:count]
	
	def print_tickers(self):
		for key in self.tickers_dict.keys():
			print(self.tickers_dict[key].market, self.tickers_dict[key].korean_name, self.tickers_dict[key].change_rate)


class Ticker(JsonObject):
	market = StringField()
	korean_name = StringField()
	english_name = StringField()
	change_rate = FloatField()
	candle_acc_trade_price = FloatField()
	trade_price = FloatField()
