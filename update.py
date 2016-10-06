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
	tree = filetree.downloadTree(remoteRootdir + "tree.txt")
	for file in tree:
		if not os.path.isfile(file.filename):
			redownload.append(file.filename)
			continue
		
		hash = filetree.hashFile(file.filename)
		if hash != file.hash:
			redownload.append(file.filename)
			
	if len(redownload) == 0:
		print("no updates needed")
	
	for file in redownload:
		downloadFile(remoteRootdir + file, file)

update(sys.argv)
