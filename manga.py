from BeautifulSoup import BeautifulSoup
import cfscrape
import re
import wget
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from base64 import b64decode
import binascii
import os

chapter_links = []
def ensure_dir(filepath):
	directory = os.path.dirname(filepath)
	if not os.path.exists(directory):
		os.makedirs(directory)

def chapters(base_url,manga_name):
	chapters = len(chapter_links)
	for i in chapter_links:
		chapters = i[i.rfind('/')+1:i.rfind('?id')]
		filepath = manga_name +'\\'+chapters + '\\'
		ensure_dir(filepath)
		url = base_url+i
		print url
		html = scraper.get(url).content
		soup = BeautifulSoup(html)
		pat = re.compile('lstImages\.push\(wrapKA\("(.+?)"\)\);')
		encrypted_urls = pat.findall(html)
		for url in encrypted_urls:
			result = new_decoder(url)
			if (not os.path.isfile(filepath+result[-7:])):
				wget.download(result,filepath+result[-7:])

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
soup = BeautifulSoup(scraper.get(thisurl).content)
manga_name = soup.find('link', {'rel': 'alternate'})['title'][:-6]
for item in soup.findAll('a',href=re.compile('/Manga/'+manga_name)):
	if '?' in item['href']:
		chapter_links.append(item['href'])

chapters(base_url,manga_name)
