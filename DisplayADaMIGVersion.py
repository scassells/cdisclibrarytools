# DisplayADaMIGVersion
import ADaMLibraryTools
import json, os, fnmatch, requests, ExampleLibraryAccess, logging, TestWriteDefXML

classLookupDict = {"ADAE": "OCCURENCE DATA STRUCTURE", "ADTTE": "BASIC DATA STRUCTURE", "OCCDS": "OCCURENCE DATA STRUCTURE", "ADAMIG.ADSL" : "SUBJECT LEVEL ANALYSIS DATASET", "ADAMIG.BDS" : "BASIC DATA STRUCTURE"}

def main():
	logging.basicConfig(filename='ADAMLibraryDev.log', format='%(asctime)s %(message)s', level=logging.INFO)
	logging.info('started')
	rv = displayADaMIG()
	logging.info('done')

if __name__ == '__main__':
	main()


def displayADaMIG() -> str:
	logging.info('started')
	tokenList = ExampleLibraryAccess.getLibraryAuthInfo()
	uname = tokenList[0]
	passwd = tokenList[1]
	baseURL = tokenList[2]
	prodListURL =  ADaMLibraryTools.ADaMProducts(baseURL)
	
	g1resp = ADaMLibraryTools.testRequest(prodListURL, uname, passwd)
	
	prLinks = g1resp["_links"]
	prodLinkList = prLinks["adam"]
	adamProdPrompt = "ADAE[AE], OCCDS[O], TTE[T] or IG[IG]: "
	resp = input(adamProdPrompt)
	igvers = "1-0"
	igdict = {}
	if (resp == "AE"):
		igdict["prodName"] = "ADAE"
		igdict["varsetLinks"] = prodLinkList[0]
	elif (resp == "T"):
		igdict["prodName"] = "ADTTE"
		igdict["varsetLinks"] = prodLinkList[1]
	elif (resp == "O"):
		igdict["prodName"] = "OCCDS"
		igdict["varsetLinks"] = prodLinkList[2]
	elif (resp == "IG"):
		igdict["prodName"] = "ADamIG"
		igdict["varsetLinks"] = prodLinkList[4]
		vsLink = igdict["varsetLinks"]
		prompt = "Use latest version (" + vsLink["title"] + ") [y/n] ?"
		useLatest = input(prompt)
		if (useLatest == "y"):
			igvers = "1-1"
		elif (useLatest == "n"):
			igdict["varsetLinks"] = prodLinkList[3]
			vsLink = igdict["varsetLinks"]
		logging.info("Retrieve library metadata for %s", vsLink["title"])
	else:
		print("Could not process response. Please try again")
	igdict["Version"] = igvers

	igVsets = getVarsets(igdict, tokenList)
	nvStr = str(len(igVsets))
	logging.info("%s variable sets", nvStr)
	vsLink = igdict["varsetLinks"]
	
	defInfo = {}
	defInfo["ProdVersion"] = igdict["prodName"] + "-" + igdict["Version"]
	defInfo["Standard"] = igdict["prodName"]
	defInfo["StdVersion"] = igdict["Version"]
	defInfo["title"] = vsLink["title"]
	defInfo["igVarsets"] = igVsets
	defInfo["codeLists"] = getCodeListDetails(igVsets, tokenList)
	doCodelists = True
	TestWriteDefXML.writeXML(defInfo, doCodelists)
	#nvar = getVariables(resp, igdict, tokenList)
	#nvarStr = str(nvar)
	#logging.info("%s variable definitions", nvarStr)
	logging.info("done")

def getVarsets(igStructInfo: dict, tokenList:list) -> list:
	nv = 0
	uname = tokenList[0]
	passwd = tokenList[1]
	baseURL = tokenList[2]
	prodName = igStructInfo["prodName"]
	igdict = igStructInfo["varsetLinks"]
	href = igdict["href"]
	title = igdict["title"]
	igVsets = []
		
	if (igStructInfo["prodName"] == "ADamIG"):
		g4ADSLurl = baseURL + href + "/datastructures/ADSL/varsets"
		g4ADSLresp = ADaMLibraryTools.testRequest(g4ADSLurl, uname, passwd)
		varsetList = getVarsetDetails("ADAMIG.ADSL", g4ADSLresp, tokenList)
		igVsets.append(varsetList)
		# loop through ADSL varsets then add to DefineXML
		g4BDSurl = baseURL + href + "/datastructures/BDS/varsets"
		g4BDSresp	= ADaMLibraryTools.testRequest(g4BDSurl, uname, passwd)
		varsetList = getVarsetDetails("ADAMIG.BDS", g4BDSresp, tokenList)
		igVsets.append(varsetList)
	else:
		g4URL = baseURL + href + "/datastructures/" + prodName + "/varsets"
		g4resp = ADaMLibraryTools.testRequest(g4URL, uname, passwd)
		varsetList = getVarsetDetails(prodName, g4resp, tokenList)
		igVsets.append(varsetList)
			
	return igVsets

def getCodeListDetails(igVsets: list, tokenList: list) -> dict:
	uname = tokenList[0]
	passwd = tokenList[1]
	baseURL = tokenList[2]
	codeListDefs = []
	nStructures = len(igVsets)
	structVarsetList = []
	logging.info("getCodeListDetails - %s data structures ", str(nStructures))
	vsn = 0
	vsList = []
	comments = []
	codelists = {}
	
	for ln in range(0, nStructures):
		vsList = igVsets[ln]
		for vs in vsList:
			vsn = vsn + 1
			logging.info("VsList Loop %s", str(vsn))
			vsAVarList = vs["aVars"]
			for vsAvars in vsAVarList:
				logging.info("Looking for valuelist and codelist references for  %s ",  vsAvars["name"])
				codeListDef = {}
				links = vsAvars["_links"]
				if ("valueList" in vsAvars):
					vl = vsAvars["valueList"]
					valueListLinks = links["valuelist"]
					vlHref =  valueListLinks["href"]
					aTuple = vlHref.rpartition('/')
					vlName = aTuple[2]
					# itemDef["CodeListRef"] = vlURI 
					if (not(vlName in codelists )):
						codeListDef["libCLType"] = 'ValueList'
						codeListDef["OID"] = "CL." + vlName
						codeListDef["Name"] = vlName + " - values"
						if (vlName.find('Numer')):
							codeListDef["dtype"] = "integer"
						else:
							codeListDef["dtype"] = "text"
						codes = []
						for v in vl:
							codes.append(v)
						codeListDef["Codes"] = codes
						logging.info("Adding ValueList %s", vlHref)
						codelists[vlName] = codeListDef
				elif ("codelist" in links):
					cl = links["codelist"]
					clHref = cl["href"]
					if (not(clHref in codelists)):
						clType = cl["type"]
						if (clType == "Root Value Domain"):
							clURL =  baseURL + clHref
							clresp = ADaMLibraryTools.testRequest(clURL, uname, passwd)
							clverLinks = clresp["_links"]
							clVersions = clverLinks["versions"]
							# get the last one
							nvers = len(clVersions)
							useVersion = clVersions[nvers-1]
							hrefCL = useVersion["href"]
							cliURL = baseURL + useVersion["href"]
							cliResp = ADaMLibraryTools.testRequest(cliURL, uname, passwd)
							logging.info("adding codelist %s [%s]",clHref, cliResp["submissionValue"])
							codeListDef["libCLType"] = 'EnumeratedItemList'
							codeListDef["OID"] = "CL." + clHref
							codeListDef["Name"] = cliResp["submissionValue"]
							codeListDef["CCode"] = cliResp["conceptId"]
							if( "extensible" in cliResp):
								codeListDef["Extensible"] = cliResp["extensible"]
							codeListDef["dtype"] = "text"
							codes = []
							termList = cliResp["terms"]
							for termDef in termList:
								clitem = {}
								clitem["CodedValue"] = termDef["submissionValue"]
								clitem["CCode"] = termDef["conceptId"]
								logging.info("Adding code %s [%s]", termDef["submissionValue"], termDef["conceptId"])
								codes.append(clitem)
							codeListDef["Codes"] = codes
							codelists[clHref] = codeListDef
					else:
						logging.info("Codelist %s already defined", clHref)
				elif ("describedValueDomain" in vsAvars):
					v1Name = None
					v1Name = vsAvars["describedValueDomain"] + "(external)"
					if (not(v1Name in codelists )):
						codeListDef["libCLType"] = 'describedValueDomain'
						codeListDef["OID"] = "CL." + vsAvars["describedValueDomain"]
						codeListDef["Name"] = vsAvars["describedValueDomain"] + "(external)"
						codeListDef["dtype"] = "external"
						codeListDef["Codes"] = "none"
						codeListDef["ExternalCL"] = vsAvars["describedValueDomain"]
						logging.info("Adding describedValueDomain:%s", vsAvars["describedValueDomain"])
						codelists[v1Name] = codeListDef
	return codelists
				
					
						
							
	
def getVarsetDetails(pref:str, g4resp:dict, tokenList:list) -> list:
	uname = tokenList[0]
	passwd = tokenList[1]
	baseURL = tokenList[2]
	g4Links = g4resp["_links"]
	vsets = g4Links["analysisVariableSets"]
	vsetList = []
	
	for vs in vsets:
		vsetInfo = {}
		vsRef = vs["href"]
		vsTitle = vs["title"]
		logging.info("Variable Set %s (%s)", vsTitle, vsRef)
		g5URL = ADaMLibraryTools.adamG5URL(baseURL, vsRef)
		g5resp = ADaMLibraryTools.testRequest(g5URL, uname, passwd)
		vsetInfo["Class"] = getVSClass(pref)
		vsetInfo["VSREF"] = vsRef
		vsetInfo["OID"] =  pref + "." + str(g5resp["ordinal"])
		vsetInfo["Name"] = g5resp["name"]
		vsetInfo["Label"] = g5resp["label"]
		vsetInfo["OrderNumber"] = g5resp["ordinal"]
		vsetInfo["Purpose"] = "LibraryVariableGroup"
		#aVarsLinks = g5resp["_links"]
		vsetInfo["aVars"] = g5resp["analysisVariables"]
		
		logging.info("Finished %s Varset details.", vsTitle)
		vsetList.append(vsetInfo)
	return vsetList
	
def getVSClass(prodOrStruct: str) -> str:
	classCT = classLookupDict[prodOrStruct]
	return classCT
	