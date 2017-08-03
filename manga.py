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
scraper = cfscrape.create_scraper()
#ensures the chapter directory exists, if not it creates a new one
def ensure_dir(filepath):
	directory = os.path.dirname(filepath)
	if not os.path.exists(directory):
		os.makedirs(directory)
#downloads the pages
def download(url_link,filepath):
	try:
		with open(filepath,'wb') as output:
			output.write(urllib2.urlopen(url_link).read())
	except :
		#whenever there is a disconnection
		time.sleep(5)
		download(url_link,filepath)
#searches for the manga
def search(search_term):
	linksearchobj =[]
	searchurl = 'http://kissmanga.com/Search/SearchSuggest'
	data = {
		'type':'manga',
		'keyword': search_term
	}
	html = connection(searchurl,True,data)
	soup = BeautifulSoup(html)
	print 'Mangas found: '
	for i in soup.findAll('a'):
		linksearchobj.append(i['href'])
		print str(len(linksearchobj)) + ': ' + i.text
	if len(linksearchobj) > 1:
		choice = input('Enter your choice: ')
		links(linksearchobj[choice-1])
	else:
		links(linksearchobj[0])

def chapters(manga_name):
	for i in chapter_links:
		chapter = i[i.rfind('/')+1:i.rfind('?id')]
		filepath = manga_name +'\\'+chapter + '\\'
		url = 'http://kissmanga.com'+i
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

def connection(url,Post = False,data=None,seconds = 5):
	try:
		if Post is False:
			soup = scraper.get(url).content
			return soup
		else:
			soup =  scraper.post(url,data).content
			return soup
	except:
		print 'No connection, retrying in '+str(seconds)+' seconds'
		time.sleep(seconds)
		connection(url,seconds)
#provides the link to the manga pages
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
#gets the links to the manga chapters
def links(thisurl):
	soup = BeautifulSoup(connection(thisurl))
	print thisurl
	manga_name = soup.find('link', {'rel': 'alternate'})['title'][:-6]
	_manga_name = thisurl[27:]
	print manga_name
	for i in soup.findAll('a',href=re.compile('/Manga/'+_manga_name)):
		if '?' in i['href']:
			chapter_links.append(i['href'])
	chapters(manga_name)

searchterm = raw_input('Manga name: ')
search(searchterm)
