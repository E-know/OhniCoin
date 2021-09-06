from Analysis import watch_chart
from INFO import market_Info
import time
from multiprocessing import Process, Value

def main():
	info = market_Info()
	tickers = info.get_sorted_ticker_by_value(count=30)
	
	processes = []
	total = Value('d', 0)
	for ele in tickers:
		p = Process(target=watch_chart, args=(ele.market, total))
		p.start()
		processes.append(p)
		
		print(ele.market)
		time.sleep(1)
		
	

if __name__ == '__main__':
	main()