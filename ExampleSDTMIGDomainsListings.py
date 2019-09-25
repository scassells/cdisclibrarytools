# ExampleSDTMDIGDomainListings
#
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

import json, os, fnmatch, requests, getpass
import pandas as pd
import ExampleLibraryTools as lt
import ExampleLibraryAccess as la
import ExampleTestWriteDefXML as TestWriteODMXML

# From Python command line import as sl then call as sl.displaySDTMDomainMetaData('standard','version') 
# Note: does not handle controlled terminology


baseURL = "https://library.cdisc.org/api"

# Modify this list to change the set of domains included in the response
domainList = ["DM", "DS", "EX", "AE", "CM", "EG", "LB", "SU", "VS"]

def DefineMetaData(standard, version, tokenList) ->list:
	uname = tokenList[0]
	passwd = tokenList[1]
	stdVersURL =  baseURL + '/mdr/' + standard + '/' + version + '/datasets/'
	dsURL = lambda dsURL, dsName: dsURL + dsName
	varLists = []
	# assemble list of dataset definitions
	for d in domainList:
		dURL = dsURL(stdVersURL, d)
		varListCLIB = testRequest(dURL, uname, passwd)
		varList = varListCLIB["datasetVariables"]   # this is a list
		dmlistdict = {}
		dmlistdict["OID"] = "CLIB.IG." + d
		dmlistdict["Name"] = d
		dmlistdict["Label"] = varListCLIB["label"]
		dsLinx = varListCLIB["_links"]
		x = dsLinx["parentClass"]
		y = x["title"]
		dmlistdict["Class"] = y
		dmlistdict["Purpose"] = "SDTM Specification"
		dmlistdict["defStructure"] = varListCLIB["datasetStructure"]
		dmlistdict["varlist"] = varList
		varLists.append(dmlistdict)

	return varLists

def displaySDTMDomainMetaData(stdName, version) -> str:
	tokenList = getLibraryAuthInfo()
	varLists = DefineMetaData(stdName, version, tokenList)
	
	goon = input("convert to Define-XML? [y/n]")
	if (goon != "y"):
		return varLists
		
	uname = tokenList[0]
	passwd = tokenList[1]

	defInfo = {}
	defInfo["ProdVersion"] = stdName + "-" + version
	defInfo["Standard"] = stdName
	defInfo["StdVersion"] = version
	defInfo["title"] = "this is the title"
	igVsets = varLists
	defInfo["igVarsets"] = igVsets
	doCodeLists = False
	TestWriteODMXML.writeXML(defInfo, doCodeLists)
	print("done")

# gets library authorization info from the user
def getLibraryAuthInfo() -> list:
	alist = []
	uname = input("Username: ")
	passwd = getpass.getpass()
	alist.append(uname)
	alist.append(passwd)
	return alist
	
def testRequest(reqURL, uname, passwd, rformat='json') -> dict:
	r = requests.get(reqURL, auth=(uname,passwd))
	status = r.status_code
	if (status == 200):
		reqPayload = r.text
		reqJson = json.loads(reqPayload)
		return reqJson
	elif (status == 404):
		reqJson = {}
		reqJson["Status404"] = reqURL
		logging.info("%s returned %s", reqURL, status)
	else:
		reqJson = {}
		reqJson["status"] = "ErrorCode" + str(status)
		reqJson["href"] = reqURL
		errmsg = reqURL + ' returned ' + str(status) + ' (' + uname + ',' + passwd + ')'
		print(errmsg)
	return reqJson	
 
