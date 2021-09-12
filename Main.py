from User import *
import sys
import os, time
from Analyst import *
from multiprocessing.managers import BaseManager
from multiprocessing import Process
from User import User
from Analyst import analyze_market
from Ticker import get_ticker

process_number = 30


def user_update(user):
	while True:
		user.get_my_wallet()
		time.sleep(5)


if __name__ == '__main__':
	BaseManager.register('user', User)
	manager = BaseManager()
	manager.start()
	
	user = manager.user()
	user.get_my_wallet()
	
	processes = []
	ticker_name = []
	ticker = get_ticker(count=process_number)
	
	for i in range(process_number):
		p = Process(target=analyze_market, args=(ticker[i]['market'], user, process_number))
		processes.append(p)
		ticker_name.append(ticker[i]['market'])
		p.start()
		time.sleep(1)
	
	
	for p in processes:
		p.join()

# TODO 1. 매수/매도시 주문이 밀려서 1분내에 거래가 안되는 상황 -> 가격이 변하면 탈출하는 조건?
# TODO 2. 이득을 보는 금액 제한
# TODO 3. 프로그램 시작 전에 모든 주문 취소하기
