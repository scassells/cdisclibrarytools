# ExampleTestWriteDefXML
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



from xml.dom import minidom
import sys
import json, datetime, time, logging

# called from ExampleSDTMDomainsListing to generate Define-XML from library content

ODMdoc = minidom.Document()
odmURL = 'http://www.cdisc.org/ns/odm/v1.3'
defnsURI = 'http://www.cdisc.org/ns/def/v2.1'
mdrDefURL = 'http://www.cdisc.org/ns/LIBRARY-Define/v1.0'
mdrURL = 'http://www.cdisc.org/ns/LIBRARY-XML/v1.0'


def writeXML(defInfo: dict, doCodelists: bool): 
	prodVers = defInfo["ProdVersion"]
	varsetInfoLists = defInfo["igVarsets"]
	if (doCodelists):
		codelists = defInfo["codeLists"]
	prodTitle = "CDISC Library Content for " + defInfo["title"]
	ODMdoc = minidom.Document()
	odmStudy = ODMdoc.createElementNS(odmURL, 'ODM')
	odmStudy.setAttribute('xmlns:def', defnsURI)
	odmStudy.setAttribute('xmlns', odmURL)
	odmAttribs = createODMAttribs(prodVers)
	
	for k, v in odmAttribs.items():
		odmStudy.setAttribute(k, v)
		logging.info("ODM attribute %s: %s", k, v)
	
	StudyTop = ODMdoc.createElement("Study")
	GlobalVariables = ODMdoc.createElement("GlobalVariables")
	StudyName = ODMdoc.createElement("StudyName")
	studyNameText = ODMdoc.createTextNode(prodVers)
	StudyName.appendChild(studyNameText)
	StudyDescription = ODMdoc.createElement("StudyDescription")
	studyDescriptionText = ODMdoc.createTextNode("CLIB Example")
	StudyDescription.appendChild(studyDescriptionText)
	ProtocolName = ODMdoc.createElement("ProtocolName")
	protocolName = ODMdoc.createTextNode("CDISC Library Listing")
	ProtocolName.appendChild(protocolName)
	GlobalVariables.appendChild(StudyName)
	GlobalVariables.appendChild(StudyDescription)
	GlobalVariables.appendChild(ProtocolName)
	studyOID = "[CDISC.Library.Example." + prodVers + "]"
	StudyTop.setAttribute("OID", studyOID)
	StudyTop.appendChild(GlobalVariables)
	
	
	
	MDV = ODMdoc.createElement("MetaDataVersion")
	MDV.setAttribute("OID", "MDV01")
	MDV.setAttribute("Name", "CDISC Library MetaData")
	MDV.setAttribute("def:DefineVersion", "2.1.0")
	MDV.setAttribute("xmlns:def", defnsURI)
	
	stdsDeclare = ODMdoc.createElement("def:Standards")
	igstd = ODMdoc.createElement("def:Standard")
	igstdRef = "CDISCLIB." + prodVers
	igstd.setAttribute("OID", igstdRef)
	igstd.setAttribute("Name", defInfo["Standard"])
	igstd.setAttribute("Type", "IG")
	igstd.setAttribute("Status", "Final")
	igstd.setAttribute("Version", defInfo["StdVersion"])
	stdsDeclare.appendChild(igstd)
	MDV.appendChild(stdsDeclare)
	
	igList = []
	idefList = []
	nStructures = len(varsetInfoLists)
	structVarsetList = []
	vsn = 0
	vsList = []
	comments = []
	
	for ds in varsetInfoLists:
		# vsList = varsetInfoLists[ln]
		itemGroup = {}
		itemGroup["Class"] = ds["Class"]
		itemGroup["OID"] = ds["OID"]
		itemGroup["Name"] = ds["Name"]
		itemGroup["Label"] = ds["Label"]
		itemGroup["defStructure"] = ds["defStructure"]
		itemGroup["Purpose"] = ds["Purpose"]
		itemGroup["defStandardOID"] = igstdRef
		vsAVarList = ds["varlist"]
		irefList = []
		for vsAvars in vsAVarList:
			itemDef = {}
			itemRef = {}
			codeListDef = {}
			varName = vsAvars["name"]
			itemOID = "IT." + itemGroup["Name"] + "."  + varName
			itemDef["OID"] = itemOID
			itemRef["ItemOID"] = itemOID
			itemRef["OrderNumber"] = vsAvars["ordinal"]
			itemRef["Role"] = vsAvars["role"]
			itemRef["mdrCore"] = vsAvars["core"]
			itemDef["Name"] = vsAvars["name"]
			itemDef["label"] = vsAvars["label"]
			itemDef["commentOID"] = "COM." + itemOID
			commentobj = {}
			commentobj["OID"] = itemDef["commentOID"]
			commentobj["notes"] = vsAvars["description"]
			comments.append(commentobj)
			itemDef["DataType"] = vsAvars["simpleDatatype"]
			if (doCodelists):
				if ("_links" in vsAvars):
					links = vsAvars["_links"]
					if ("codelist" in links):
						cl = links["codelist"]
						clHref = cl["href"]
						itemDef["CodeListOID"] = "CL." + clHref
				if ("valueList" in vsAvars):
					valueListLinks = links["valuelist"]
					vlHref =  valueListLinks["href"]
					aTuple = vlHref.rpartition('/')
					vlName = aTuple[2]
					itemDef["CodeListOID"] = "CL." + vlName
				elif ("describedValueDomain" in vsAvars):
					itemDef['CodeListOID'] = "CL." + vsAvars["describedValueDomain"]
				elif ("valueDescription" in vsAvars):
					itemDef['CodeListOID'] = "CL." + vsAvars["valueDescription"]
			irefList.append(itemRef)
			idefList.append(itemDef)
		itemGroup["irefs"] =  irefList
		igList.append(itemGroup)
	logging.info("Done %s", str(vsn))
		
	# now start assembling ODM ItemGroupDef and ItemDef elements. Need to add comments.
	nIG = 0
	for ig in igList:
		logging.info("Creating ItemGroup Def for %s", ig["OID"])
		dataStructure = ODMdoc.createElement('ItemGroupDef')
		dataStructure.setAttribute("OID", ig["OID"])
		dataStructure.setAttribute("Name", ig["Name"])
		dataStructure.setAttribute("Purpose", ig["Purpose"])
		dataStructure.setAttribute("def:Structure", ig["defStructure"])
		dataStructure.setAttribute("def:StandardOID", ig["defStandardOID"])
		description = ODMdoc.createElement('Description')
		transText = ODMdoc.createElement("TranslatedText")
		ltext = ODMdoc.createTextNode(ig["Label"])
		transText.appendChild(ltext)
		description.appendChild(transText)
		dataStructure.appendChild(description)
		defClass = ODMdoc.createElementNS(defnsURI, "def:Class")
		defClass.setAttribute("Name", ig["Class"])
		
		irefList = ig["irefs"]
		for iref in irefList:
			itemRef = ODMdoc.createElement('ItemRef')
			itemRef.setAttribute("ItemOID", iref["ItemOID"])
			itemRef.setAttribute("OrderNumber", iref["OrderNumber"])
			libCore = iref["mdrCore"]
			if (libCore == "Req"):
				itemRef.setAttribute("Mandatory", "Y")
			else:
				itemRef.setAttribute("Mandatory", "N")
			itemRef.setAttribute("mdrCore", iref["mdrCore"])
			itemRef.setAttribute("Role", iref["Role"])
			logging.info("ItemRef[%s]", iref["ItemOID"])
			dataStructure.appendChild(itemRef)
		dataStructure.appendChild(defClass)
		MDV.appendChild(dataStructure)
		
		nIG = nIG + 1

	for idef in idefList:
		logging.info("Creating ItemDef[%s]", idef["OID"])
		itemDef = ODMdoc.createElement('ItemDef')
		itemDef.setAttribute("OID", idef["OID"])
		itemDef.setAttribute("Name", idef["Name"])
		if (idef["DataType"] == "Char"):
			itemDef.setAttribute("DataType", "text")
			itemDef.setAttribute("Length", "50")
		elif(idef["DataType"] == "Num"):
			itemDef.setAttribute("DataType", "float")
		itemDef.setAttribute("def:CommentOID", idef["commentOID"])
		itemDef.setAttribute("xmlns:def", defnsURI)
		description = ODMdoc.createElement('Description')
		transText = ODMdoc.createElement("TranslatedText")
		ltext = ODMdoc.createTextNode(idef["label"])
		transText.appendChild(ltext)
		description.appendChild(transText)
		itemDef.appendChild(description)
		if( "CodeListOID" in idef):
			CodeListRef = ODMdoc.createElement('CodeListRef')
			CodeListRef.setAttribute("CodeListOID", idef["CodeListOID"])
			itemDef.appendChild(CodeListRef)
		MDV.appendChild(itemDef)
	
	
	if (doCodelists):
		for clkey, cl in codelists.items():
			clOID = cl["OID"]
			clType = cl["libCLType"]
			clName = cl["Name"]
			clDtype = cl["dtype"]
			CodeListDef = ODMdoc.createElement('CodeList')
			CodeListDef.setAttribute("OID", clOID)
			CodeListDef.setAttribute("Name", clName)
			CodeListDef.setAttribute("DataType", clDtype)
			#clCodes = cl["Codes"]
			#clinfo = clName + ": " + clCodes + "\n"
			# print(clinfo)
			if (clType == "ValueList"):
				if ("Codes" in cl):
					clCodes = cl["Codes"]
					for cli in clCodes:
						EnumeratedItem = ODMdoc.createElement('EnumeratedItem')
						EnumeratedItem.setAttribute("CodedValue", cli)
						CodeListDef.appendChild(EnumeratedItem)
				MDV.appendChild(CodeListDef)
			elif (clType == "describedValueDomain" ):
				ExternalCodeList = ODMdoc.createElement('ExternalCodeList')
				ExternalCodeList.setAttribute("Name", clName)
				ExternalCodeList.setAttribute("Version", "StudySpecific")
				CodeListDef.appendChild(ExternalCodeList)
				MDV.appendChild(CodeListDef)
			elif (clType == "PublishedEnumeratedItemList"):
				#clCodes = cl["Codes"]
				# do not currently have a way to show a codelist is extensible. Add a clib extension?
				# nci:ExtCodeID
				if ("Codes" in cl):
					clCodes = cl["Codes"]
					for cli in clCodes:     # for codelists each item has a CodedValue and a Concept CodeList
						EnumeratedItem = ODMdoc.createElement('EnumeratedItem')
						EnumeratedItem.setAttribute("CodedValue", cli["CodedValue"])
						EIAlias = ODMdoc.createElement('Alias')
						EIAlias.setAttribute("Context", 'nci:ExtCodeID')
						EIAlias.setAttribute("Name", cli["CCode"])
						EnumeratedItem.appendChild(EIAlias)
						CodeListDef.appendChild(EnumeratedItem)
					
				if ("CCode" in cl):
					clCCode = cl["CCode"]
					CLAlias = ODMdoc.createElement('Alias')
					CLAlias.setAttribute("Context", 'nci:ExtCodeID')
					CLAlias.setAttribute("Name", clCCode)
					CodeListDef.appendChild(CLAlias)
				MDV.appendChild(CodeListDef)
			elif (clType == "Unpublished"):
				CLAlias = ODMdoc.createElement('Alias')
				CLAlias.setAttribute("Context", 'nci:ExtCodeID')
				CLAlias.setAttribute("Name", 'No definition available')
				CodeListDef.appendChild(CLAlias)
				MDV.appendChild(CodeListDef)
			
			logging.info("added CodeList %s [OID= %s, Name= %s]  to Define-XML", clkey, clOID, clName) 
	
	

	nc = 0
	for com in comments:
		commentDef = ODMdoc.createElementNS(defnsURI,'def:CommentDef')
		commentDef.setAttribute("xmlns:def", defnsURI)
		commentDef.setAttribute("OID", com["OID"])
		description = ODMdoc.createElement("Description")
		transText = ODMdoc.createElement("TranslatedText")
		ltext = ODMdoc.createTextNode(com["notes"])
		transText.appendChild(ltext)
		description.appendChild(transText)
		commentDef.appendChild(description)
		MDV.appendChild(commentDef)
		nc = nc + 1
	
	
	
	StudyTop.appendChild(MDV)
	odmStudy.appendChild(StudyTop)
	ODMdoc.appendChild(odmStudy)
	fn = "define" + prodVers + ".xml"
	outfile = open(fn, "w")
	ODMdoc.writexml(outfile, addindent= '    ', newl = '\n')
	outfile.close
	print("Look for output in ", fn)
	
def createODMAttribs(prodVers: str) ->dict:
	# build dict with creationDT, FileOID, FileType, Granularity
	
	cdt = datetime.datetime.now()
	creationDT = cdt.isoformat()
	odmRootAttribs = {}
	odmRootAttribs['CreationDateTime'] = creationDT
	odmRootAttribs['FileOID'] = '[CDISC LIBRARY- ' + prodVers + ']'
	odmRootAttribs['FileType'] = 'Snapshot'
	odmRootAttribs['def:Context'] = 'Other'
	
	return odmRootAttribs
	
