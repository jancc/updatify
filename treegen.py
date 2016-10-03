import os
import filetree
import sys

def treegen(argv):
	rootdir = ""
	
	for i, arg in enumerate(argv):
		if i < len(argv) - 1:
			if arg == "-r" or arg == "--root":
				rootdir = argv[i + 1]
				
	if rootdir == "":
		print("please specify a root directory using -r")
		sys.exit(2)
	
	os.chdir(rootdir)
	tree = filetree.generateTree(".")
	out = open("tree.txt", "w")
	for file in tree:
		out.write(file.filename + ":" + file.hash + "\n")

treegen(sys.argv)