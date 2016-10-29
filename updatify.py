#!/usr/bin/env python3
import os
import urllib
import urllib.parse
import urllib.request
import sys
import hashlib

#Filetree

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

def parseTree(content):
	tree = []
	lines = content.splitlines()
	for line in lines:
		filedata = line.split(":", 1)
		if len(filedata) == 2:
			file = TreeFile(filedata[0].strip(), filedata[1].strip())
			tree.append(file)
	return tree
	
def downloadTree(url):
	url = "http://" + urllib.parse.quote(url)
	with urllib.request.urlopen(url) as www:
		content = www.read().decode('utf-8')
	return parseTree(content)

def readTree(filename):
	if not os.path.isfile(filename):
		return []
	file = open(filename, "r")
	content = file.read()
	return parseTree(content)

def writeTree(tree, filename):
	out = open(filename, "w")
	for file in tree:
		out.write(file.filename + ":" + file.hash + "\n")
		
def treeContainsFile(tree, filename):
	for file in tree:
		if file.filename == filename:
			return True
	return False
	
def treeContainsHash(tree, hash):
	for file in tree:
		if file.hash == hash:
			return True
	return False

def treeGetFileHash(tree, filename):
	for file in tree:
		if file.filename == filename:
			return file.hash
	return ""

#Treegen

def treegen(rootdir):
	if rootdir == "":
		print("please specify a root directory")
		sys.exit(2)

	os.chdir(rootdir)
	tree = generateTree(".")
	writeTree(tree, "tree.txt")

#Updater

def downloadFile(url, filename):
	print("downloading " + filename + " from " + url)
	if os.path.dirname(filename) != "":
		os.makedirs(os.path.dirname(filename), exist_ok=True)
	url = "http://" + urllib.parse.quote(url)
	with urllib.request.urlopen(url) as www:
		content = www.read()
	file = open(filename, "wb")
	file.write(content)

def removeFile(filename):
	print("removing " + filename)
	os.remove(filename)
	dir = os.path.dirname(filename)
	dirEmpty = False
	try:
		os.rmdir(dir)
		dirEmpty = True
	except OSError as ex:
		dirEmpty = False
	if dirEmpty:
		print("removing " + dir)

def update(rootdir, game, arch, version):
	remoteRootdir = "update.jancc.de/" + game + "/" + version + "/" + arch + "/";
	
	if rootdir == "":
		rootdir = game;
	
	if not os.path.isdir(rootdir):
		os.makedirs(rootdir)
	
	os.chdir(rootdir)
	
	redownload = []
	remove = []
	tree = downloadTree(remoteRootdir + "tree.txt")
	localTree = readTree("tree.txt")
	
	for file in tree:
		if not os.path.isfile(file.filename):
			redownload.append(file.filename)
			continue
		
		hash = hashFile(file.filename)
		if hash != file.hash:
			redownload.append(file.filename)
	
	for file in localTree:
		# any file that still has it's original hash, but is not part of the remote tree will be deleted
		if os.path.isfile(file.filename) and hashFile(file.filename) == treeGetFileHash(localTree, file.filename) and not treeContainsFile(tree, file.filename):
			remove.append(file.filename)
			continue
			
	if len(redownload) == 0:
		print("no updates needed")
	
	for file in redownload:
		downloadFile(remoteRootdir + file, file)
		
	for file in remove:
		removeFile(file)
		
	writeTree(tree, "tree.txt")

# CLI

def updatify(argv):
	command = "";
	rootdir = ""
	arch = ""
	game = ""
	version = "latest"
	
	for i, arg in enumerate(argv):
		if i < len(argv) - 1:
			if arg == "-r" or arg == "--root":
				rootdir = argv[i + 1]
			elif arg == "-g" or arg == "--game":
				game = argv[i + 1]
			elif arg == "-a" or arg == "--arch":
				arch = argv[i + 1]
			elif arg == "-v" or arg == "--version":
				version = argv[i + 1]
			elif arg == "-c" or arg == "--command":
				command = argv[i + 1]
	
	if command == "":
		print("please specify a command (update or treegen)")
		sys.exit(2)
	elif arch == "":
		print("please specify your architecture")
		sys.exit(2)
	elif game == "":
		print("please specify a game")
		sys.exit(2)
	elif command == "update":
		update(rootdir, game, arch, version)
	elif command == "treegen":
		treegen(rootdir)
	
	
updatify(sys.argv)
