from User import *
import sys
import os, time
from Analyst import *
from multiprocessing.managers import BaseManager
from multiprocessing import Process
from User import User
from Analyst import analyze_market
from Ticker import get_ticker

number = 50

if __name__ == '__main__':
	BaseManager.register('user', User)
	manager = BaseManager()
	manager.start()
	
	user = manager.user()
	
	processes = []
	
	ticker = get_ticker(count=number)
	
	for i in range(number):
		p = Process(target=analyze_market, args=(ticker[i]['market'], user,))
		processes.append(p)
		p.start()
		time.sleep(1)
		
	for p in processes:
		p.join()