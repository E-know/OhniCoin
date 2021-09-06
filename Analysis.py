import requests
import time


def get_average(response):
	ave_5 = 0
	ave_120 = 0
	for i, ele in enumerate(response.json()):
		if i < 5:
			ave_5 += ele['trade_price']
		ave_120 += ele['trade_price']
	
	ave_5 /= 5
	ave_120 /= 120
	
	return ave_5, ave_120


def watch_chart(market, total):
	url = "https://api.upbit.com/v1/candles/minutes/1"
	
	querystring = {"market": market,
	               "count": 120}
	
	headers = {"Accept": "application/json"}
	
	have_coin = False
	buy_price = 0
	was_under = False
	timer_sec = 60
	while True:
		response = requests.request("GET", url, headers=headers, params=querystring)
		price = response.json()[0]['trade_price']
		
		ave_5, ave_120 = get_average(response)
		
		if have_coin:
			if (price - buy_price) - buy_price * 0.0005 - price * 0.0005 > 0:
				earn = (price - buy_price) - buy_price * 0.0005 - price * 0.0005
				total.value += earn
				print('BUY PERMISSION : ', buy_price * 0.0005)
				print('SELL PERMISSION : ', price * 0.0005)
				print('EARN EXCEPT PERMISSION : ', price - buy_price)
				print(response.json()[0]['candle_date_time_kst'], market, '[<P>]SELL : %d  EARN : %f TOTAL : %f GET_PERCENT : %f' % (price, earn, total.value, earn / buy_price * 100))
				have_coin = False
				timer_sec = 60
			elif (buy_price - price) / buy_price <= -0.1:
				total.value += (price - buy_price) * 0.9995 - buy_price * 0.0005
				print(response.json()[0]['candle_date_time_kst'], market, '[<M>]SELL : %d  EARN : %f TOTAL : %f GET_PERCENT : %f' % (price, earn, total.value, earn / buy_price * 100))
				have_coin = False
				timer_sec = 60
		elif not have_coin:
			if was_under and ave_5 > ave_120:
				print(response.json()[0]['candle_date_time_kst'], market, 'BUY', price)
				have_coin = True
				buy_price = price
				timer_sec = 60
			was_under = ave_5 < ave_120
		
		# print(response.json()[0]['candle_date_time_kst'], market, ']현재가 : %d  120이평선: %f  5이평선: %f' % (price, ave_120, ave_5))
		time.sleep(timer_sec)
