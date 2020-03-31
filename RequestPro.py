import re
from time import sleep
from functools import wraps
from requests_html import requests, HTMLSession

TIMEOUT = 30

headers = {
	'User-Agent' : 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
}

class ProxyInit:
	@staticmethod
	def getProxy():
		proxy = None
		while not proxy:
			try:
				proxy = requests.get("http://178.62.80.215:5010/get/", timeout = 5).json()
			except Exception as e:
				# print(e)
				pass
		return proxy

	@staticmethod
	def delProxy(proxy):
		try:
			requests.get(f"http://178.62.80.215:5010/delete/?proxy={proxy}", timeout = 5)
		except Exception:
			pass

	@classmethod
	def checkProxy(cls):
		src = wait_flag = None
		ret = cls.getProxy()
		src = ret.get("src")
		while src == "no proxy":
			if not wait_flag:
				# print("等待代理池刷新...")
				wait_flag = 1
			sleep(5)
			ret = cls.getProxy()
			src = ret.get("src")
		return ret.get('proxy')

def requestDecorate(func):
	@wraps(func)
	def requestPro(*args, **kwargs):
		while True:
			try:
				response = func(*args, **kwargs)
				if response.status_code == 500:
					continue
				return response
			except Exception as err:
				# print(err)
				# raise
				pass
	return requestPro

@requestDecorate
def requestGet(url, headers = headers):
	session = HTMLSession()
	# proxy = ProxyInit.checkProxy()
	# response = session.get(url, headers = headers, proxies = {'http':f'http://{proxy}'}, timeout = TIMEOUT)
	response = session.get(url, headers = headers, timeout = TIMEOUT)
	return response

@requestDecorate
def requestPost(url, data,  headers = headers):
	session = HTMLSession()
	# proxy = ProxyInit.checkProxy()
	# response = session.post(url, data = data, headers = headers, proxies = {'http':f'http://{proxy}'}, timeout = TIMEOUT)
	response = session.post(url, data = data, headers = headers, timeout = TIMEOUT)
	return response

if __name__ == '__main__':
	proxy = ProxyInit.checkProxy()
	print(proxy)
	ret = requestGet('http://baidu.com')
	print(ret)