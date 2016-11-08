#!/usr/bin/env python
import sys
from isbntools.app import *

class IsbnLookup:
	def __init(self):
		pass

	def find(self, isbn):
		return meta(isbn)


if __name__ == "__main__":
    isbn_arg = sys.argv[1]
    print("The ISBN of the most `spoken-about` book with this title is %s" % isbn_arg)
    print("")
    print("... and the book is:")
    print("")
    isbnFinder = IsbnLookup()
    print(isbnFinder.find(isbn_arg))