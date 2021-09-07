from Analysis import watch_chart
from INFO import market_Info
import time
from multiprocessing import Process, Value, Manager
from multiprocessing.managers import BaseManager
from Account import user_Info


def main():
	BaseManager.register('Account', user_Info) # TODO
	manager = BaseManager()
	manager.start()
	
	user_info = manager.Account()
	
	
	
	market_info = market_Info()
	tickers = market_info.get_sorted_ticker_by_value(count=20, minimum=1000)


	processes = []
	# TODO total 삭제하기
	total = Value('d', 0)
	for ele in tickers:
		p = Process(target=watch_chart, args=(user_info, ele.market, total,))
		p.start()
		processes.append(p)

		print(ele.market)
		time.sleep(1)
		
	

if __name__ == '__main__':
	main()