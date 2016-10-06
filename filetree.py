import os
import hashlib
import urllib.request

class TreeFile:
	def __init__(self, filename, hash):
		self.filename = filename
		self.hash = hash

def removePrefix(string, prefix):
	if string.startswith(prefix):
		return string[len(prefix):]
	return string

def hashFile(filename):
	file = open(filename, "rb")
	content = file.read()
	hash = hashlib.sha1()
	hash.update(content)
	return hash.hexdigest()
	
def generateTree(treeroot):
	tree = []
	for root, dirs, files in os.walk(treeroot):
		for file in files:
			filename = os.path.join(root, file)
			filename = removePrefix(filename, "." + os.sep)
			filename = filename.replace(os.sep, "/")
			hash = hashFile(filename)
			tree.append(TreeFile(filename, hash))
	return tree
	
def downloadTree(url):
	tree = []
	url = "http://" + urllib.parse.quote(url)
	with urllib.request.urlopen(url) as www:
		content = www.read().decode('utf-8')
	lines = content.splitlines()
	for line in lines:
		filedata = line.split(":", 1)
		if len(filedata) == 2:
			file = TreeFile(filedata[0].strip(), filedata[1].strip())
			tree.append(file)
	return tree
