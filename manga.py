from BeautifulSoup import BeautifulSoup
import cfscrape
import re
import urllib2
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from base64 import b64decode
import os
import time

chapter_links = []
def ensure_dir(filepath):
	directory = os.path.dirname(filepath)
	if not os.path.exists(directory):
		os.makedirs(directory)
def download(url_link,filepath):
	try:
		with open(filepath,'wb') as output:
			output.write(urllib2.urlopen(url_link).read())
	except :
		#whenever there is a disconnection
		time.sleep(5)
		download(url_link,filepath)

def chapters(base_url,manga_name):
	chapters = len(chapter_links)
	for i in chapter_links:
		chapters = i[i.rfind('/')+1:i.rfind('?id')]
		filepath = manga_name +'\\'+chapters + '\\'
		url = base_url+i
		print url
		html = connection(url)
		soup = BeautifulSoup(html)
		pat = re.compile('lstImages\.push\(wrapKA\("(.+?)"\)\);')
		encrypted_urls = pat.findall(html)
		page_counter = 0
		ensure_dir(filepath)
		for url in encrypted_urls:
			page_counter += 1
			result = new_decoder(url)
			extension = result[-4:]
			if (not os.path.isfile(filepath+str(page_counter)+extension)):
				download(result,filepath+str(page_counter)+extension)

def connection(url,seconds = 5):
	try:
		soup = scraper.get(url).content
		return soup
	except:
		print 'No connection, retrying in '+str(seconds)+' seconds'
		time.sleep(seconds)
		connection(url,seconds)

def new_decoder(url):
	#from https://gist.github.com/nhanb/74542c36d3dcc5dde4e90b34437fb523
	iv = 'a5e8e2e9c2721be0a84ad660c472c1f3'.decode('hex')
	sha = SHA256.new()
	sha.update('034nsdfns72nasdasd')
	key = sha.digest()
	encoded = b64decode(url)
	dec = AES.new(key=key, mode=AES.MODE_CBC, IV=iv)
	result = dec.decrypt(encoded)
	# unpad
	result = result[:-ord(result[-1])]
	return result

base_url = 'http://kissmanga.com'
scraper = cfscrape.create_scraper()
thisurl = raw_input('Enter the manga link: ')

#Feed HTML file into parser
soup = BeautifulSoup(connection(thisurl))
manga_name = soup.find('link', {'rel': 'alternate'})['title'][:-6]
_manga_name = thisurl[27:]
print _manga_name
for item in soup.findAll('a',href=re.compile('/Manga/'+_manga_name)):
	if '?' in item['href']:
		chapter_links.append(item['href'])

chapters(base_url,manga_name)
