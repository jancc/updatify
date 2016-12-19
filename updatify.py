#!/usr/bin/env python3
import os
import urllib
import urllib.parse
import urllib.request
import sys
import hashlib
import json

#Filetree

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
	tree = {}
	tree["files"] = {}
	for root, dirs, files in os.walk(treeroot):
		for file in files:
			filename = os.path.join(root, file)
			filename = removePrefix(filename, "." + os.sep)
			filename = filename.replace(os.sep, "/")	
			if not file.startswith(".") and not filename.startswith("."):
				hash = hashFile(filename)
				tree["files"][filename] = hash
	return tree

def downloadTree(url):
	url = "http://" + urllib.parse.quote(url)
	tree = {}
	with urllib.request.urlopen(url) as www:
		tree = json.loads(www.read().decode('utf-8'))
	return tree

def readTree(filename):
	if not os.path.isfile(filename):
		return {}
	file = open(filename, "r")
	return json.load(file)

def writeTree(tree, filename):
	out = open(filename, "w")
	json.dump(tree, out)

def treeContainsFile(tree, filename):
	return filename in tree["files"]

def treeContainsHash(tree, hash):
	return hash in tree["files"].values()

def treeGetFileHash(tree, filename):
	return tree["files"][filename]

#Treegen

def generate(argv):
	arch = argv[2]
	tree = generateTree(".")
	tree["arch"] = arch
	writeTree(tree, "manifest.json")

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

def install(argv):
	prog = ""
	version = "latest"
	arch = "x86_64_linux"
	
	for i, arg in enumerate(argv):
		if i == 2:
			prog = arg
		elif i == 3:
			version = arg
		elif i == 4:
			arch = arg
	
	remoteRootdir = "update.jancc.de/" + prog + "/" + version + "/" + arch + "/";

	if not os.path.isdir(prog):
		os.makedirs(prog)
	
	os.chdir(prog)
	
	redownload = []
	remove = []
	tree = downloadTree(remoteRootdir + "manifest.json")
	localTree = readTree("manifest.json")
	
	for file in tree["files"]:
		if not os.path.isfile(file):
			redownload.append(file)
			continue
		
		hash = hashFile(file)
		if hash != tree["files"][file]:
			redownload.append(file)
	
	for file in localTree:
		# any file that still has it's original hash, but is not part of the remote tree will be deleted
		if os.path.isfile(file) and hashFile(file) == localTree["files"][file] and not file in tree["files"]:
			remove.append(file)
			continue
			
	if len(redownload) == 0:
		print("no updates needed")
	
	for file in redownload:
		downloadFile(remoteRootdir + file, file)
		
	for file in remove:
		removeFile(file)
		
	writeTree(tree, "manifest.json")

# Remove

def remove(argv):
	prog = argv[2]
	os.chdir(prog)
	tree = readTree("manifest.json")
	
	for file in tree["files"]:
		if os.path.isfile(file):
			removeFile(file)

# CLI

def updatify(argv):
	command = argv[1]
	
	if command == "generate":
		generate(argv)
	elif command == "install":
		install(argv)
	elif command == "remove":
		remove(argv)

updatify(sys.argv)
