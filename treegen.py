#!/usr/bin/env python3
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
	filetree.writeTree(tree, "tree.txt")

treegen(sys.argv)
