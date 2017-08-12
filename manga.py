from BeautifulSoup import BeautifulSoup
import cfscrape
import re
import urllib2
import urllib
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from base64 import b64decode
import os
import time
FTYPES = {
	'/JPEG' : '.jpg',
    '/GIF' : '.gif',
    '/PNG' : '.png',
	}
chapter_links = []
scraper = cfscrape.create_scraper()
#ensures the chapter directory exists and changes the directory, if not it creates a new one
def ensure_dir(directory):
	if not os.path.exists(directory):
		os.makedirs(directory)
	os.chdir(directory)
#checks the number of files in a folder
def queue(filepath):
	num_files = len([f for f in os.listdir(filepath) if os.path.isfile(os.path.join(filepath, f))])
	return num_files
#downloads the pages
def download(url_link,filepath):
	try:
		urllib.urlretrieve(url_link,filepath)
	except :
		#whenever there is a disconnection
		print 'ping'
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
#using the content-type headers, it tries to guess the extension of the page
def extension(url):
	try:
		page = urllib2.urlopen(url)
		content = page.headers.getheader('content-type')
		ext = content[content.rfind('/'):].upper()
		ext = FTYPES[ext]
		return ext
	except:
		#there is a weird bug with some chapter pages where you can't find the content-type
		#if it ever happens the extension will default to .jpg
		return '.jpg'

def chapters(manga_name):
	ensure_dir(manga_name)
	for i in reversed(chapter_links):
		chapter = i[i.rfind('/')+1:i.rfind('?id')]
		ensure_dir(chapter)
		url = 'http://kissmanga.com'+i
		print 'Downloading ' + chapter
		html = connection(url)
		soup = BeautifulSoup(html)
		pat = re.compile('lstImages\.push\(wrapKA\("(.+?)"\)\);')
		encrypted_urls = pat.findall(html)
		page_counter = 0
		#checks if the chapter has been downloaded
		if queue(os.getcwd()) == len(encrypted_urls):
			print chapter + ' has already been downloaded. Skipping it.'
			continue
		else:
			#if it has been downloaded it initiates the download of the chapter
			for url in encrypted_urls:
				page_counter += 1
				result = new_decoder(url)
				ext = extension(result)
				if (not os.path.isfile(str(page_counter)+ext)):
					download(result,str(page_counter)+ext)
			os.chdir('..')

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
