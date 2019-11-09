# ExampleLibraryTools
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



import json, os, fnmatch, requests, ExampleLibraryAccess, logging

hdr4xml = { 'accept': 'application/xml'}
hdr4excel = {'accept': 'application/vnd.ms-excel'}


	
def ADaMProducts(baseURL) -> str:
	dapURL = baseURL + "/mdr/products/DataAnalysis"
	return dapURL
	
def SDTMProducts(baseURL) -> str:
	dtabURL = baseURL + "/mdr/product/DataTabulation"
	return dtabURL
	
def CDASHProducts(baseURL) -> str:
	dcURL = baseURL + "/mdr/product/DataCollection"
	return dcURL
	

def g2ADaMDataStructureListing(baseURL, productVersion) -> str:
	g2URL = baseURL + "/mdr/adam/" + productVersion + "/datastructures"
	return g2URL

def g3ADaMDataStructureDetails(baseURL, productVersion, dataStructure) -> str:
	g3URL = baseURL + "/mdr/adam/" + productVersion + "/datastructures/" + dataStructure
	return g3URL

def g4ADaMVariableGroupListing(baseURL, productVersion, dataStructure) -> str:
	g4URL = baseURL + "/mdr/adam/" + productVersion + "/datastructures/" + dataStructure + "/varsets"
	return G4URL
	
def g5ADaMVariableGroupDetails(baseURL, productVersion, dataStructure, varset) -> str:
	g5URL = baseURL + "/mdr/adam/" + productVersion + "/datastructures/" + dataStructure + "/varsets/" + varset
	return g5URL

def g6ADaMVariableListing(baseURL, productVersion, dataStructure) -> str:
	g6URL = baseURL + "mdr/adam/" + productVersion + "/datastructures/" + dataStructure + "/variables"
	return g6URL

def g7ADaMVariableListing(baseURL, productVersion, dataStructure, varName) ->str:
	g7URL = baseURL + "/mdr/adam/" + productVersion + "/datastructures/" + dataStructure + "/variables/" + varName
	return g7URL


	
def adamigVersions(product) -> str:
	versions = ["1-0"]
	if (product == "adamig"):
		versions = versions + ["1-1"]
	
		return versions
	else:
		return versions

def testADaMRequest(reqURL, uname, passwd) -> dict:
	r = requests.get(reqURL, auth=(uname,passwd))
	status = r.status_code
	if (status == 200):
		reqJson = {}
		reqPayload = r.text
		varInfo = json.loads(reqPayload)
		reqJson["status200"] = varInfo
		return reqJson
	elif (status == 404):
		reqJson = {}
		reqJson["Status404"] = reqURL
		logging.info("%s returned %s", reqURL, status)
	else:
		reqJson = {}
		reqJson["status"] = "ErrorCode" + str(status)
		reqJson["href"] = reqURL
		logging.error("%s returned %s (%s %s)", reqURL, status, uname, passwd)
	return reqJson
	
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
		logging.error("%s returned %s (%s %s)", reqURL, status, uname, passwd)
	return reqJson


def ADaMProducts(baseURL) -> str:
	dapURL = baseURL + "/mdr/products/DataAnalysis"
	return dapURL
	
def SDTMProducts(baseURL) -> str:
	dtabURL = baseURL + "/mdr/products/DataTabulation"
	return dtabURL
	
def CDASHProducts(baseURL) -> str:
	dcURL = baseURL + "/mdr/products/DataCollection"
	return dcURL
	
		
def ApiContent() ->str:
	logging.debug("ApiContent called.")
	tokenList = LibraryAccess.getLibraryAuthInfo()
	uname = tokenList[0]
	passwd = tokenList[1]
	baseURL = tokenList[2]
	respType = tokenList[3]
	prodListURL =  g1ADaMProducts(baseURL)
	
	g1resp = testRequest(prodListURL, uname, passwd)
	
	prLinks = g1resp["_links"]
	prodLinkList = prLinks["adam"]
	i = 0
	for prod in prodLinkList:
		i= i + 1
		prodVerHref = prod["href"]
		prodTitle = prod["title"]
		# datastructures
		logging.info("G2 %s href %s listing", prodTitle, prodVerHref)
		g2URL = adamG2URL(baseURL, prodVerHref)
		g2resp = testRequest(g2URL, uname, passwd)
		g2Links = g2resp["_links"]
		prodDataStructures = g2Links["dataStructures"]
		for ds in prodDataStructures:
			i = i + 1
			dsRef = ds["href"]
			dsTitle = ds["title"]
			logging.info("G3 %s href %s Full Details", dsTitle, dsRef)
			g3URL = adamG3URL(baseURL, dsRef)
			g3resp = testRequest(g3URL, uname, passwd)
			logging.info("G4 %s href %s Varset Listing", dsTitle, dsRef)
			g4URL = adamG4URL(baseURL, dsRef)
			g4resp = testRequest(g4URL, uname, passwd)
			logging.info("G5 %s href %s Variable Listing", dsTitle, dsRef)
			g4Links = g4resp["_links"]
			vsets = g4Links["analysisVariableSets"]
			for vs in vsets:
				i = i + 1
				vsRef = vs["href"]
				vsTitle = vs["title"]
				logging.info("Variable Set %s (%s)", vsTitle, vsRef)
				g5URL = adamG5URL(baseURL, vsRef)
				g5resp = testRequest(g5URL, uname, passwd)
			logging.info("Finished %s Varset details.", vsTitle)
			g6URL = adamG6URL(baseURL, dsRef)
			logging.info("G6 %s Variable Details", dsTitle)
			g6resp = testRequest(g6URL, uname, passwd)
			g6Links = g6resp["_links"]
			dsVars = g6Links["analysisVariables"]
			for vars in dsVars:
				i = i + 1
				varRef = vars["href"]
				varTitle = vars["title"]
				logging.info("G7 Variable %s (%s)", varTitle, varRef)
				g7URL = adamG7URL(baseURL, varRef)
				gresp = testRequest(g7URL, uname, passwd)
			logging.info("Finished %s analysis variable details.", varTitle)
		logging.info("Finished %s dataset.", dsTitle)
	logging.info("Finished %s.", prodTitle)
	info = "processed " + str(i) + " API requests"
	return info
	
	
					
					
def libraryURL() -> str:
	return  'https://library.cdisc.org/api'

def displayAnalysisProducts(prodListJson) -> list:
	prLinks = prodListJson["_links"]
	prodLinkList = prLinks["adam"]
	display = input("Display Product list? ")
	for prod in prodLinkList:
		prodHref = prod["href"]
		prodTitle = prod["title"]
		prodType = prod["type"]
		if (display == "Y"):
			print(prodHref, prodTitle, prodType)
	return prodLinkList
		
	
def adamG2URL(baseURL: str, prodHref: str) -> str:
	return baseURL +  prodHref + '/datastructures'

def adamG3URL(baseURL: str, dsHref: str) -> str:
	return baseURL + dsHref

	
def adamG4URL(baseURL: str, dsHref: str) -> str:
	g4url = baseURL + dsHref + "/varsets"
	return g4url
	
def adamG5URL(baseURL: str, vsHref: str) -> str:
	g5url = baseURL + vsHref
	return g5url
	
def adamG6URL(baseURL: str, dsHref: str) -> str:
	g6url = baseURL + dsHref + "/variables"
	return g6url

def adamG7URL(baseURL: str, varHref: str) -> str:
	g7url = baseURL + varHref
	return g7url

	
def adamG2Get(g2URL: str, tokenList:list) -> list:
	logging.info(g2URL)
	logging.info(g2URL)
	uname = tokenList[0]
	passwd = tokenList[1]
	r = requests.get(g3URL, auth=(uname, passwd))
	status = r.status_code
	if (status == 200):
		reqPayload = r.text
		reqJson = json.loads(reqPayload)
		dataStructures = adamG2dsList(reqJson)
	else:
		logging.info(r.status)
	return dataStructures
		
	
def adamG2dsList(g2out: dict)  -> list:
	name = g2out['name']
	links = g2out['_links']
	logging.debug(links)
	dsList = links['dataStructures']
	olist = []
	for ds in dsList:
		dsName = ds['title']
		dsURL = ds['href'] + '/varsets'
		olistItem = [dsName, dsURL]
		logging.debug(dsURL)
		olist.append(dsURL)
	return olist
	
def adamG3Get(g3URL: str, tokenList: list) -> int:
	logging.info(g3URL)
	uname = tokenList[0]
	passwd = tokenList[1]
	r = requests.get(g3URL, auth=(uname, passwd))
	status = r.status_code
	if (status == 200):
		varsetInfoList = g3VarListInfo(r.text)
		for vs in varsetInfoList:
			varsetInfo = vs;
			varsetName = varsetInfo["name"]
			logging.debug("Varset Name %s", varsetName)
			g4url = varsetInfo["href"]
			logging.debug(g4url)
			r4 = requests.get(g4url, auth=(uname, passwd))
			g4Status = r4.status_code
			logging.info("Get request %s returned %s", g4url, g4Status)
	else:
		logging.warning("Get request %s returned %s", g3URL,status)
		return status
	return status

def g3VarListInfo(g3resp: str) -> list:
	g3Json = json.loads(g3resp)
	dsName = g3Json["name"]
	dsDescrip = g3Json["description"]
	logging.debug("Name %s Description %s", dsName, dsDescrip)
	dsLinks = g3Json["_links"]
	# now get the list of varsets
	dsVarsets  = dsLinks["analysisVariableSets"]	# dsVarsets is a list
	varsetURLs = list()
	for vs in dsVarsets:
		varsetName = vs["title"]
		varsetHref = vs["href"]
		logging.debug("Varset Name %s href %s", varsetName, varsetHref)
		varsetURL = adamG4URL(varsetHref)
		varsetInfo = {"name": varsetName, "href": varsetURL}
		varsetURLs.append(varsetInfo)
		logging.debug("done with %s", varsetName)
	logging.debug("done with %s", dsName)
	return varsetURLs
	
def adamGet(adamURL: str, uname: str, passwd: str) -> dict:
	r = requests.get(adamURL, auth=(uname, passwd))
	if (r.status_code == 200):
		adamResp = json.loads(r.text)
		return adamResp
	resp = {}
	return resp
		

def testRequestAll(reqURL, uname, passwd, rformat) -> dict:
	hdrs = {'accept' : rformat}
	r = requests.get(reqURL, auth=(uname,passwd), headers = hdrs)
	status = r.status_code
	if (status != 200):
		logging.error("%s returned %s (%s %s)", reqURL, status, uname, passwd)
	
	reqPayload = r.text
	reqJson = json.loads(reqPayload)
	logging.info("%s Json %s xml %s", reqURL, status, statusXML)
	return reqJson


	
		
 
