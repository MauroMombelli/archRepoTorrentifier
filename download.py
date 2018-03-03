from bs4 import BeautifulSoup
import requests

import urllib.request

import pickle, os, subprocess, random, bisect, traceback, time

urlCore = 'https://arch.mirror.square-r00t.net/core/os/x86_64/'
ext = 'xz'

def listFiles(url, ext=''):
	page = requests.get(url).text
	soup = BeautifulSoup(page, 'html.parser')
	return [ node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]

def download(url, file):
	urllib.request.urlretrieve (url+'/'+file, file)
	return file

def torrentify(mirrors, repo, file):
	command = '/usr/bin/mktorrent'
	
	#add WEBSEED (10 random mirror)
	command += ' -w '

	randomMirror = random.choices(mirrors, k = 10)
	for mirrors in randomMirror:
		command += mirrors + repo + '/os/x86_64/' + file + ','
	command = command[:-1] #remove last comma
	
	#add TRAKER (to find)
	command += ' -a udp://tracker.open-internet.nl:6969/announce,udp://tracker.opentrackr.org:1337/announce,https://open.kickasstracker.com:443/announce,http://mgtracker.org:6969/announce'
	
	#torrent name
	outputFile = 'torrent/' + repo + '/' + file + '.torrent'
	command += ' -o ' + outputFile + ' ' + file
	
	print("----------- creating torrent -------")
	
	popen = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
	for stdout_line in iter(popen.stdout.readline, ""):
		print( stdout_line )
	popen.stdout.close()
	print("+++++++++++++++++++++++++++++++++++++")
	return_code = popen.wait()
	if return_code:
		raise subprocess.CalledProcessError(return_code, command)
	
	return outputFile

def publish(torrent):
	print("here we publish the torrent")
	
def loadMirror(mirrors, filename):
	with open(filename) as f:
		content = f.readlines()

	#remove whitespace characters like `\n` at the end of each line
	mirrors += [x.strip() for x in content if not x.startswith('#')]

def downloadRepo(mirrors, repoName):
	print("downloading repo " + repoName)

	try:
		os.makedirs("torrent/" + repoName)
	except FileExistsError:
		pass
	except Exception as e: 
		print('Exception on making folders')
		traceback.print_exc()
	
	fileList = os.listdir("torrent/" + repoName)
	fileList.sort()
	
	url = random.choice(mirrors) + repoName + '/os/x86_64/'
	try:
		fileInRepo = listFiles(url, ext)
	except Exception as e: 
		print('Exception on downloading mirror')
		traceback.print_exc()
		raise
	
	for file in fileInRepo:
		try:

			url = random.choice(mirrors) + repoName + '/os/x86_64/'
			
			print (file)
			
			for letter in file:
				if (letter < 'a' or letter > 'z') and (letter < 'A' or letter > 'Z') and (letter < '0' or letter > '9') and (not letter in "+-._%:"):
					raise ValueError('invalid filename, has bad simbols '+str(file))
			
			packagename = file.split('-')
			if len(packagename) < 3:
				raise ValueError('invalid filename, does not have - '+str(packagename))
			
			i = bisect.bisect_left(fileList, file + '.torrent')
			if i != len(fileList) and fileList[i] == file + '.torrent':
				#we already have the torrent
				continue
			
			#delete old torrent
			if i != len(fileList):
				diskPackagename = fileList[i].split('-')
				if diskPackagename == packagename:
					print("found an old torrent, delting " + str(fileList[i]))
					os.remove(fileList[i])
			
			downloaded = download(url, file)
			
			torrent = torrentify(mirrors, repoName, downloaded)
			
			os.remove(downloaded)
			
			publish(torrent)
			
			print("file %s torrentified" % (str(packagename[0])))
		except Exception as e: 
			print('Exception on file ' + str(file))
			traceback.print_exc()

mirrors = []

loadMirror(mirrors, 'mirrors.txt')

while True:
	try:
		downloadRepo(mirrors, 'core')
		downloadRepo(mirrors, 'extra')
		downloadRepo(mirrors, 'community')
	except Exception as e: 
		print('Exception on download repo')
		traceback.print_exc()
	
	print('waiting for next itereation')
	time.sleep(60*10) #every 10 minutes
	



'''
def loadPacketDB(database:dict, fileName:str):
	with open (fileName, 'rb') as fp:
		database = pickle.load(fp)
	

def savePacketDB(database:dict, fileName:str):
	try:
		with open(fileName + '.tmp', 'wb') as fp:
			pickle.dump(database, fp)
		
		os.rename(fileName + '.tmp', fileName)
		print("database saved "+ str(fileName))
	except Exception as e: 
		print('Exception on saving database file ' + str(fileName) + " " + str(e))
'''
