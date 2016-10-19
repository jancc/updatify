#!/usr/bin/env python3
import filetree
import os
import urllib
import sys

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

def update(argv):
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
				
	if rootdir == "" or arch == "" or game == "":
		print("please specify a root directory using -r")
		sys.exit(2)

	remoteRootdir = "update.jancc.de/" + game + "/" + version + "/" + arch + "/";
	
	if not os.path.isdir(rootdir):
		os.makedirs(rootdir)
	
	os.chdir(rootdir)
	
	redownload = []
	remove = []
	tree = filetree.downloadTree(remoteRootdir + "tree.txt")
	localTree = filetree.readTree("tree.txt")
	
	for file in tree:
		if not os.path.isfile(file.filename):
			redownload.append(file.filename)
			continue
		
		hash = filetree.hashFile(file.filename)
		if hash != file.hash:
			redownload.append(file.filename)
	
	for file in localTree:
		# any file that still has it's original hash, but is not part of the remote tree will be deleted
		if filetree.hashFile(file.filename) == filetree.treeGetFileHash(localTree, file.filename) and not filetree.treeContainsFile(tree, file.filename):
			remove.append(file.filename)
			continue
			
	if len(redownload) == 0:
		print("no updates needed")
	
	for file in redownload:
		downloadFile(remoteRootdir + file, file)
		
	for file in remove:
		removeFile(file)
		
	filetree.writeTree(tree, "tree.txt")

update(sys.argv)
