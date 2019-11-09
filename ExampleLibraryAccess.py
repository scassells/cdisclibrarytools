# ExampleLibraryAccess
# The MIT License (MIT) 
# 
#   Copyright (c) 2019 CDISC
#  
#   Permission is hereby granted, free of charge, to any person obtaining a copy of this software and 
#   associated documentation files (the "Software"), to deal in the Software without restriction, 
#   including without limitation the rights to use, copy, modify, merge, publish, distribute, 
#   sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is 
#   furnished to do so, subject to the following conditions:
#   The above copyright notice and this permission notice shall be included in all copies or 
#   substantial portions of the Software.
# 
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT 
#   NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND 
#   NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
#   DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT 
#   OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import getpass, logging, requests

cdisc_prod_LibraryURL = "https://library.cdisc.org/api"

acceptDict = {'j' : 'application/json', 'x' : 'application/xml', 'e': 'application/vnd.ms-excel', 'c':'text/csv'}

def getLibraryAuthInfo() -> list:
	logging.debug("getLibraryAuthInfo")
	alist = []
	uname = input("Username: ")
	passwd = getpass.getpass()
	useURL = cdisc_prod_LibraryURL
	alist.append(uname)
	alist.append(passwd)
	alist.append(useURL)
	return alist
	logging.info("askUntilOk")
	counter = askCount
	clist = []
	while (counter > 0):
		clist = getLibraryAuthInfo()
		askPrompt = clist[0] + '/' + clist[1] + ' ok? [y/n] '
		keepIt = input(askPrompt)
		if (keepIt == 'y'):
			return clist
		counter = counter - 1
	return clist
	
		
