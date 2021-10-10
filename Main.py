from multiprocessing import Process
from multiprocessing.managers import BaseManager

from Analyst import *
from Analyst import analyze_market, order_coin
from Ticker import get_ticker
from User import User

import sys

process_number = 30

if __name__ == '__main__':
	BaseManager.register('user', User)
	manager = BaseManager()
	manager.start()
	
	user = manager.user()
	user.get_my_wallet()
	
	processes = []
	ticker_name = []
	ticker = get_ticker(count=process_number)
	
	while True:
		C = input()
		print('''
		E = END
		A = Analyze
		S = Sell in Wallet 적정가에 코인 판매
		B = blank Wallet 시장가로 모든 코인 판매
		''', flush=True)
		print('', flush=True)
		C = input()
		
		for p in processes:
			p.terminate()
		processes = []
		
		if C == 'E':
			break
		elif C == 'A':
			for i in range(process_number):
				p = Process(target=analyze_market, args=(ticker[i]['market'], user,))
				processes.append(p)
				ticker_name.append(ticker[i]['market'])
				p.start()
				time.sleep(1)
			
			for coin in user.get_wallet():
				if coin == 'KRW':
					continue
				if coin not in ticker_name:
					p = Process(target=analyze_market, args=('KRW-' + coin, user,))
					processes.append(p)
					p.start()
					time.sleep(1)
		elif C == 'S':
			for coin in user.get_wallet():
				if coin == 'KRW':
					continue
				if coin not in ticker_name:
					p = Process(target=analyze_market, args=('KRW-' + coin, user,))
					processes.append(p)
					p.start()
					time.sleep(1)
		elif C == 'B':
			wallet = user.get_my_wallet()
			for coin in wallet:
				if coin == 'KRW':
					continue
				order_coin(
					market='KRW-' + coin,
					side='ask',
					volume=wallet[coin]['balance'],
					price=None,
					ord_type='market'
				)
				time.sleep(0.5)
	
	for p in processes:
		p.terminate()

# TODO 1. 매수/매도시 주문이 밀려서 1분내에 거래가 안되는 상황 -> 가격이 변하면 탈출하는 조건?
# TODO 2. 이득을 보는 금액 제한
# TODO 3. 프로그램 시작 전에 모든 주문 취소하기
# TODO 4. 모든 코인 팔아버리는 함수 가동 (시작 할때 만들기)
# TODO 5. 티커 재 선정및 재 가동 함수 구현
