import re
import json
import threading
from time import sleep
from RequestPro import *
from requests_html import HTMLSession, requests

headers = {
	'User-Agent' : 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
	'Host' : 'm.bilibili.com'
}
link_list = []
# main_title = None

def getId(txt):
	id_pattern = r'(av(\d)+$|BV([\w\d]+))'
	url_pattern = r'https?://(m|(www))\.bilibili\.com/video/(av(\d)+$|BV([\w\d]+)).*'
	ret = re.match(id_pattern, txt)
	if ret:
		return f'http://m.bilibili.com/video/{ret.group(0)}'
	ret = re.match(url_pattern, txt)
	if ret:
		return txt.replace('https', 'http')

def getShortLink(raw_url):
	api_url = 'http://v1.alapi.cn/api/url'
	data = {'url':f'http://{raw_url}', 'type':'1'}
	response = requestPost(api_url, data = data).json()
	return response['data']['short_url']

def getMainLink(url):
	response = requestGet(url, headers = headers)
	# main_title = response.html.xpath('//*[@id="vTitle"]/span/text()')
	try:
		# download_link = re.findall(r"video_url:\s?'/{0,2}(.+mid=\d+)'", response.text)[0]
		download_link = re.findall(r"video_url:\s?'(https?:)?//(.+\w=\w+)'", response.text)[0][1]
		# hongkong
		# download_link = re.findall(r"video_url:\s?'(https?:)?//cn-hk-eq-bcache-\d+(.+\w=\w+)'", response.text)[0][1]
		# download_link = 'upos-sz-mirrorhw' + download_link
	except IndexError:
		return False
	download_link = getShortLink(download_link)
	link_list.append(f'[P1]\n{download_link}')
	#
	p = response.html.xpath('//*[@id="page"]/div/div[6]/div[1]/div[1]/div/div[*]')
	p_num = len(p)
	if p_num:
		return p_num

def getSubLink(url, i):
	url = f'{url}?p={i}'
	response = requestGet(url, headers = headers)
	try:
		download_link = re.findall(r"video_url:\s?'(https?:)?//(.+\w=\w+)'", response.text)[0][1]
		# hongkong
		# download_link = re.findall(r"video_url:\s?'(https?:)?//cn-hk-eq-bcache-\d+(.+\w=\w+)'", response.text)[0][1]
		# download_link = 'upos-sz-mirrorhw' + download_link
	except IndexError:
		return 'Something is wrong...'
	download_link = getShortLink(download_link)
	link_list.append(f'[P{i}]\n{download_link}')

def bili(txt):
	info = ''
	url = getId(txt)
	if not url:
		return
	p_num = getMainLink(url)
	if p_num:
		threads = [threading.Thread(target = getSubLink, args = (url, i,)) for i in range(2, p_num+1)]
		for t in threads:
			t.start()
		for t in threads:
			t.join()
	link_list.sort()
	for link in link_list:
		info += f'{link}\n'
	link_list.clear()
	return info[:-1]

def main():
	# info = getId('av1234')
	# info = getId('https://m.bilibili.com/video/BV1VV411o7n1')
	info = bili('http://m.bilibili.com/video/BV1e7411y77a')
	# info = bili('av92712214')
	# info = getShortLink('mooc.uue.me/icourse163/BIT-1001870002.html')
	print(info)

if __name__ == '__main__':
	main()